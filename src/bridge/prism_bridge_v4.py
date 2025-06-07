#!/usr/bin/env python3
"""
Prism_whisper2 Bridge V4 - Ultra Performance
Bridge avec Engine V4 : Pre-loading + Streaming + GPU Memory Pinning
Architecture: Talon → Bridge V4 → Engine V4 (optimisé) → Clipboard → Auto-paste
Test au micro avec latence ultra-réduite
"""

import os
import time
import logging
import sys
from pathlib import Path
from typing import Optional
import threading
import subprocess

# Import du service Engine V4 optimisé
sys.path.append(str(Path(__file__).parent.parent))
from core.whisper_engine_v4 import get_engine_v4, start_service_v4


class PrismBridgeV4:
    """Bridge V4 avec Engine ultra-optimisé pour test micro"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.trigger_file = self.project_root / "talon_trigger.txt"
        self.log_file = self.project_root / "logs" / "prism_bridge_v4.log"
        
        # Assurer que le répertoire logs existe
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Engine V4 optimisé
        self.engine = None
        self.running = False
        
        # Métriques V4
        self.total_transcriptions = 0
        self.total_time = 0.0
        self.gpu_optimizations = 0
        
    def _setup_logging(self):
        """Setup logging pour Bridge V4"""
        logger = logging.getLogger('PrismBridgeV4')
        logger.setLevel(logging.INFO)
        
        # Éviter doublons de handlers
        if logger.handlers:
            logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - INFO - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def start_bridge(self):
        """Démarrer Bridge V4 avec Engine optimisé"""
        try:
            print("🎙️ Prism_whisper2 Bridge V4 - Ultra Performance")
            print("Architecture: Talon → Bridge V4 → Engine V4 (Pre-loading + Streaming + GPU) → Clipboard")
            print("Test au micro avec optimisations maximales")
            print("-" * 70)
            
            self.logger.info("🚀 Prism Bridge V4 (Ultra Performance) initializing...")
            
            # Démarrer Engine V4 optimisé
            self.logger.info("🚀 Démarrage Engine V4 avec toutes optimisations...")
            if start_service_v4():
                self.engine = get_engine_v4()
                self.logger.info("✅ Engine V4 prêt (Pre-loaded + Streaming + GPU)")
                
                # Afficher status Engine
                status = self.engine.get_status()
                self.logger.info(f"📊 Engine Status V4: version={status.get('version')}, gpu_enabled={status.get('gpu_enabled')}")
                
                # Démarrer surveillance trigger
                self.logger.info("👁️ Démarrage surveillance trigger...")
                self.running = True
                self._monitor_trigger()
                
            else:
                self.logger.error("❌ Échec démarrage Engine V4")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage Bridge V4: {e}")
            return False
    
    def _monitor_trigger(self):
        """Surveillance du trigger avec Engine V4"""
        self.logger.info(f"👁️ Surveillance trigger: {self.trigger_file}")
        
        while self.running:
            try:
                if self.trigger_file.exists():
                    trigger_content = self.trigger_file.read_text().strip()
                    
                    if trigger_content == "transcribe":
                        self.logger.info("🎯 Trigger détecté: transcription demandée")
                        self._handle_transcription_v4()
                        
                        # Supprimer trigger
                        try:
                            self.trigger_file.unlink()
                        except:
                            pass
                
                time.sleep(0.1)  # Check rapide
                
            except FileNotFoundError:
                # Trigger supprimé, continuer surveillance
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"❌ Erreur surveillance trigger: {e}")
                time.sleep(1)
    
    def _handle_transcription_v4(self):
        """Handler transcription avec Engine V4 optimisé"""
        start_time = time.time()
        
        try:
            self.logger.info("⚡ Début transcription ultra-optimisée V4...")
            
            # Transcription via Engine V4 (GPU optimisé)
            success, result = self.engine.transcribe_now(timeout=15)
            
            if success and result:
                elapsed_time = time.time() - start_time
                
                # Stats
                self.total_transcriptions += 1
                self.total_time += elapsed_time
                if hasattr(self.engine, 'gpu_optimizations'):
                    self.gpu_optimizations = self.engine.gpu_optimizations
                
                self.logger.info(f"✅ Transcription V4 réussie en {elapsed_time:.2f}s: {result}")
                
                # Copier dans clipboard
                self._copy_to_clipboard(result)
                
                # Auto-paste
                self._auto_paste()
                
                self.logger.info("🎉 Transcription V4 terminée")
                
                # Stats périodiques
                if self.total_transcriptions % 5 == 0:
                    avg_time = self.total_time / self.total_transcriptions
                    self.logger.info(f"📊 Stats V4: {self.total_transcriptions} transcriptions, moyenne {avg_time:.2f}s, GPU optimizations: {self.gpu_optimizations}")
                
            else:
                self.logger.error(f"❌ Échec transcription V4: {result}")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur transcription V4: {e}")
    
    def _copy_to_clipboard(self, text: str):
        """Copier texte dans clipboard"""
        try:
            import subprocess
            
            # PowerShell pour clipboard Windows
            ps_command = f'Set-Clipboard -Value "{text}"'
            subprocess.run(['powershell', '-Command', ps_command], 
                         check=True, capture_output=True)
            
            self.logger.info("📋 Texte copié dans clipboard")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur clipboard: {e}")
    
    def _auto_paste(self):
        """Auto-paste universel via PowerShell SendKeys"""
        try:
            time.sleep(0.2)  # Délai pour stabilité
            
            # PowerShell SendKeys pour paste universel
            ps_command = '''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("^v")
            '''
            
            subprocess.run(['powershell', '-Command', ps_command], 
                         check=True, capture_output=True)
            
            self.logger.info("⌨️ Auto-paste V4 exécuté")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur auto-paste: {e}")
    
    def get_bridge_stats(self) -> dict:
        """Stats complètes Bridge V4"""
        stats = {
            'version': 'v4_ultra_performance',
            'total_transcriptions': self.total_transcriptions,
            'average_time': self.total_time / max(self.total_transcriptions, 1),
            'gpu_optimizations': self.gpu_optimizations,
            'running': self.running
        }
        
        # Stats Engine V4 si disponible
        if self.engine:
            engine_stats = self.engine.get_status()
            stats['engine_stats'] = engine_stats
        
        return stats
    
    def stop_bridge(self):
        """Arrêter Bridge V4 proprement"""
        self.logger.info("🛑 Arrêt Prism Bridge V4...")
        
        self.running = False
        
        if self.engine:
            self.engine.stop_engine()
        
        # Stats finales
        final_stats = self.get_bridge_stats()
        self.logger.info(f"📊 Stats finales V4: {final_stats}")
        
        self.logger.info("✅ Bridge V4 arrêté")


def test_bridge_v4():
    """Test interactif Bridge V4"""
    print("🧪 Test interactif Prism Bridge V4...")
    
    bridge = PrismBridgeV4()
    
    try:
        if bridge.start_bridge():
            print("\n✅ Bridge V4 démarré avec succès!")
            print("\n🎤 PRÊT POUR TEST MICRO:")
            print("- Utilisez Win+Alt+V dans Talon pour déclencher")
            print("- Ou créez manuellement: echo 'transcribe' > talon_trigger.txt")
            print("- Ctrl+C pour arrêter")
            
            # Boucle interactive
            while True:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Arrêt demandé...")
                    break
        else:
            print("❌ Échec démarrage Bridge V4")
            
    except Exception as e:
        print(f"❌ Erreur test Bridge V4: {e}")
    finally:
        bridge.stop_bridge()


if __name__ == "__main__":
    test_bridge_v4() 