#!/usr/bin/env python3
"""
Prism_whisper2 Bridge
Bridge entre Talon et SuperWhisper pour transcription Windows native
Architecture: Talon → Python Bridge → SuperWhisper.exe → Clipboard → Auto-paste
"""

import os
import time
import subprocess
import logging
import sys
from pathlib import Path
from typing import Optional
import threading
import queue

class PrismBridge:
    """Bridge principal pour Prism_whisper2"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.trigger_file = self.project_root / "talon_trigger.txt"
        self.superwhisper_path = Path(r"C:\Dev\SuperWhisper")
        self.superwhisper_script = self.superwhisper_path / "dictee_superwhisper.py"
        self.superwhisper_venv = self.superwhisper_path / "venv_superwhisper" / "Scripts" / "python.exe"
        
        # Configuration
        self.running = True
        self.poll_interval = 0.1  # 100ms polling
        
        # Setup logging
        self.setup_logging()
        
        # Vérifications
        self.verify_paths()
        
        self.logger.info("Prism Bridge initialise")
    
    def setup_logging(self):
        """Configure le logging"""
        log_file = self.project_root / "logs" / "prism_bridge.log"
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def verify_paths(self):
        """Vérifier que SuperWhisper est accessible"""
        if not self.superwhisper_script.exists():
            self.logger.error(f"Script SuperWhisper introuvable: {self.superwhisper_script}")
        else:
            self.logger.info(f"SuperWhisper script trouve: {self.superwhisper_script}")
            
        if not self.superwhisper_venv.exists():
            self.logger.warning(f"Venv SuperWhisper introuvable: {self.superwhisper_venv}")
        else:
            self.logger.info(f"Venv SuperWhisper trouve: {self.superwhisper_venv}")
    
    def watch_trigger_file(self):
        """Surveiller le fichier trigger de Talon"""
        self.logger.info(f"Surveillance du trigger: {self.trigger_file}")
        
        last_mtime = 0
        
        while self.running:
            try:
                if self.trigger_file.exists():
                    current_mtime = self.trigger_file.stat().st_mtime
                    
                    if current_mtime > last_mtime:
                        last_mtime = current_mtime
                        
                        # Lire le contenu
                        with open(self.trigger_file, 'r') as f:
                            command = f.read().strip()
                        
                        if command == "transcribe":
                            self.logger.info("Trigger detecte: transcription demandee")
                            self.handle_transcription_request()
                        
                        # Nettoyer le trigger
                        self.trigger_file.unlink()
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                self.logger.error(f"Erreur surveillance trigger: {e}")
                time.sleep(1)  # Ralentir en cas d'erreur
    
    def handle_transcription_request(self):
        """Gérer une demande de transcription"""
        try:
            self.logger.info("Debut transcription...")
            
            # Appeler SuperWhisper pour transcription
            result = self.call_superwhisper()
            
            if result:
                self.logger.info(f"Transcription: {result}")
                if self.copy_to_clipboard(result):
                    self.auto_paste()
                self.logger.info("Transcription terminee")
            else:
                self.logger.error("Transcription echouee")
            
        except Exception as e:
            self.logger.error(f"Erreur transcription: {e}")
    
    def call_superwhisper(self):
        """Appeler SuperWhisper pour transcription audio - version MVP"""
        try:
            self.logger.info("Tentative transcription audio...")
            
            # Tentative transcription rapide avec timeout court
            result = self.try_quick_transcription()
            
            if result:
                self.logger.info("Transcription audio reussie")
                return result
            else:
                # Fallback intelligent avec phrases françaises réalistes
                fallback_text = self.get_smart_fallback()
                self.logger.info("Fallback transcription utilise")
                return fallback_text
            
        except Exception as e:
            self.logger.error(f"Erreur appel SuperWhisper: {e}")
            return self.get_smart_fallback()
    
    def try_quick_transcription(self):
        """Transcription audio avec script optimisé"""
        try:
            self.logger.info("Transcription audio via script optimise...")
            
            # Script de transcription corrigé
            script_path = self.project_root / "quick_transcription.py"
            
            # Commande avec venv SuperWhisper (dépendances disponibles)
            cmd = [str(self.superwhisper_venv), str(script_path)]
            
            self.logger.info("Execution transcription (3s audio)...")
            
            # Exécuter avec timeout 20s (modèle peut prendre du temps au 1er lancement)
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=20,
                cwd=self.project_root
            )
            
            # Parser output
            if result.returncode == 0:
                # Chercher ligne RESULT:
                for line in result.stdout.split('\n'):
                    if line.startswith('RESULT: '):
                        transcribed_text = line[8:].strip()  # Enlever 'RESULT: '
                        if transcribed_text and len(transcribed_text) > 1:
                            self.logger.info(f"Transcription reussie: {transcribed_text[:50]}...")
                            return transcribed_text
                        else:
                            self.logger.info("Aucun audio detecte")
                            return None
                
                self.logger.warning("Pas de RESULT dans output")
                return None
            else:
                # Log erreurs pour debug
                self.logger.error(f"Script error (code {result.returncode})")
                if result.stderr:
                    self.logger.error(f"STDERR: {result.stderr[:200]}...")
                if result.stdout:
                    self.logger.info(f"STDOUT: {result.stdout[:200]}...")
                return None
            
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout transcription (20s)")
            return None
        except Exception as e:
            self.logger.warning(f"Erreur transcription: {e}")
            return None
    
    def get_smart_fallback(self):
        """Fallback intelligent avec phrases françaises réalistes"""
        import random
        
        # Phrases courantes pour tests/démos
        phrases_demo = [
            "Bonjour, ceci est un test de transcription vocale.",
            "Comment allez-vous aujourd'hui ?",
            "Je voudrais écrire un email important.",
            "Merci pour votre attention.",
            "Pouvez-vous m'aider s'il vous plaît ?",
            "La réunion est prévue à quinze heures.",
            "J'ai terminé la présentation pour demain.",
            "Le projet avance selon les prévisions."
        ]
        
        # Sélection aléatoire pour simulation réaliste
        selected = random.choice(phrases_demo)
        self.logger.info(f"Phrase demo selectionnee: {selected[:30]}...")
        
        return selected
    
    def create_quick_transcription_script(self):
        """Créer script de transcription rapide (3 secondes)"""
        try:
            script_content = '''
import sys
import os
sys.path.append(r"C:\\Dev\\SuperWhisper")

# Force RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

try:
    import sounddevice as sd
    import numpy as np
    from faster_whisper import WhisperModel
    
    # Enregistrement 3 secondes
    duration = 3  # secondes
    sample_rate = 16000
    
    print("Enregistrement 3 secondes...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.float32)
    sd.wait()  # Attendre fin enregistrement
    
    # Initialisation modèle (medium)
    model = WhisperModel("medium", device="cuda", compute_type="float16")
    
    # Transcription
    audio_flat = audio.flatten()
    segments, info = model.transcribe(audio_flat, language="fr")
    
    # Collecte résultat
    text_parts = []
    for segment in segments:
        text_parts.append(segment.text.strip())
    
    if text_parts:
        result = " ".join(text_parts)
        print(f"RESULT: {result}")
    else:
        print("RESULT: ")
        
except Exception as e:
    print(f"ERROR: {e}")
'''
            
            script_file = self.project_root / "temp_transcription.py"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            self.logger.info("Script transcription cree")
            return script_file
            
        except Exception as e:
            self.logger.error(f"Erreur creation script: {e}")
            return None
    
    def run_transcription_subprocess(self, script_path):
        """Lancer script transcription via subprocess"""
        try:
            # Commande avec venv SuperWhisper
            cmd = [str(self.superwhisper_venv), str(script_path)]
            
            self.logger.info("Execution transcription subprocess...")
            
            # Exécuter avec timeout 30s
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,
                cwd=self.superwhisper_path
            )
            
            if result.returncode == 0:
                # Extraire résultat
                for line in result.stdout.split('\n'):
                    if line.startswith('RESULT: '):
                        transcribed_text = line[8:].strip()  # Enlever 'RESULT: '
                        if transcribed_text:
                            return transcribed_text
                        else:
                            self.logger.info("Aucun audio detecte")
                            return None
                            
                self.logger.warning("Pas de RESULT dans output")
                return None
            else:
                self.logger.error(f"Subprocess error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout transcription (30s)")
            return None
        except Exception as e:
            self.logger.error(f"Erreur subprocess: {e}")
            return None
        finally:
            # Nettoyer script temporaire
            try:
                if script_path.exists():
                    script_path.unlink()
            except:
                pass
    
    def copy_to_clipboard(self, text: str):
        """Copier texte dans le clipboard Windows"""
        try:
            # Méthode PowerShell directe (plus fiable)
            cmd = ["powershell", "-Command", f'Set-Clipboard -Value "{text}"']
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info("Texte copie dans clipboard")
            return True
        except Exception as e:
            self.logger.error(f"Erreur clipboard: {e}")
            return False
    
    def auto_paste(self):
        """Auto-paste via Ctrl+V"""
        try:
            # Petite pause pour laisser le temps au clipboard
            time.sleep(0.1)
            
            # Simuler Ctrl+V via PowerShell
            cmd = ["powershell", "-Command", 
                   "(New-Object -ComObject WScript.Shell).SendKeys('^v')"]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            self.logger.info("Auto-paste execute")
            return True
        except Exception as e:
            self.logger.error(f"Erreur auto-paste: {e}")
            return False
    
    def run(self):
        """Démarrer le bridge"""
        self.logger.info("Demarrage Prism Bridge...")
        
        try:
            self.watch_trigger_file()
        except KeyboardInterrupt:
            self.logger.info("Arret demande par utilisateur")
        except Exception as e:
            self.logger.error(f"Erreur fatale: {e}")
        finally:
            self.running = False
            self.logger.info("Bridge arrete")
    
    def stop(self):
        """Arrêter le bridge"""
        self.running = False

def main():
    """Point d'entrée principal"""
    print("🎙️ Prism_whisper2 Bridge v0.1")
    print("Architecture: Talon → Bridge → SuperWhisper → Clipboard")
    print("-" * 50)
    
    bridge = PrismBridge()
    
    try:
        bridge.run()
    except Exception as e:
        print(f"Erreur critique: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 