#!/usr/bin/env python3
"""
Prism_whisper2 Bridge V2 - Optimisé Performance
Bridge avec service SuperWhisper2 pre-loaded pour latence ultra-réduite
Architecture: Talon → Bridge V2 → Engine Service (pre-loaded) → Clipboard → Auto-paste
Optimisation: -4s latence via model pre-loading
"""

import os
import time
import logging
import sys
from pathlib import Path
from typing import Optional
import threading

# Import du service optimisé
sys.path.append(str(Path(__file__).parent.parent))
from core.whisper_engine import get_engine, start_service


class PrismBridgeV2:
    """Bridge V2 avec service SuperWhisper2 optimisé"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.trigger_file = self.project_root / "talon_trigger.txt"
        
        # Configuration
        self.running = True
        self.poll_interval = 0.1  # 100ms polling
        
        # Setup logging
        self.setup_logging()
        
        # Référence au service engine
        self.engine = None
        self.engine_ready = False
        
        self.logger.info("🚀 Prism Bridge V2 (Performance Optimized) initializing...")
    
    def setup_logging(self):
        """Configure le logging"""
        log_file = self.project_root / "logs" / "prism_bridge_v2.log"
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
    
    def start_services(self):
        """Démarrer tous les services (avec pre-loading)"""
        try:
            self.logger.info("🔥 Démarrage services avec pre-loading...")
            
            # 1. Démarrer service Whisper (pre-loading 4s une seule fois)
            if start_service():
                self.engine = get_engine()
                self.engine_ready = True
                self.logger.info("✅ Service SuperWhisper2 pre-loaded et prêt")
                
                # Afficher status
                status = self.engine.get_status()
                self.logger.info(f"📊 Engine Status: {status}")
                
                return True
            else:
                self.logger.error("❌ Échec démarrage service Whisper")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage services: {e}")
            return False
    
    def watch_trigger_file(self):
        """Surveiller le fichier trigger de Talon (optimisé)"""
        self.logger.info(f"👁️ Surveillance trigger: {self.trigger_file}")
        
        last_mtime = 0
        
        while self.running:
            try:
                if self.trigger_file.exists():
                    current_mtime = self.trigger_file.stat().st_mtime
                    
                    if current_mtime > last_mtime:
                        last_mtime = current_mtime
                        
                        # Lire commande
                        with open(self.trigger_file, 'r') as f:
                            command = f.read().strip()
                        
                        if command == "transcribe":
                            self.logger.info("🎯 Trigger détecté: transcription demandée")
                            self.handle_transcription_request_v2()
                        
                        # Nettoyer trigger
                        self.trigger_file.unlink()
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur surveillance trigger: {e}")
                time.sleep(1)
    
    def handle_transcription_request_v2(self):
        """Gérer transcription avec service optimisé"""
        if not self.engine_ready:
            self.logger.error("❌ Service engine pas prêt")
            self._fallback_transcription()
            return
        
        try:
            start_time = time.time()
            self.logger.info("⚡ Début transcription optimisée...")
            
            # Transcription via service pre-loaded (ultra-rapide)
            success, result = self.engine.transcribe_now(timeout=10)
            
            elapsed = time.time() - start_time
            
            if success and result:
                self.logger.info(f"✅ Transcription réussie en {elapsed:.1f}s: {result}")
                if self.copy_to_clipboard(result):
                    self.auto_paste()
                self.logger.info("🎉 Transcription terminée")
            else:
                self.logger.warning(f"⚠️ Transcription vide ou échec: {result}")
                # Utiliser fallback intelligent
                self._fallback_transcription()
            
        except Exception as e:
            self.logger.error(f"❌ Erreur transcription V2: {e}")
            self._fallback_transcription()
    
    def _fallback_transcription(self):
        """Fallback intelligent en cas de problème"""
        import random
        
        phrases_demo = [
            "Transcription en cours d'optimisation...",
            "Service temporairement indisponible.",
            "Test de fallback intelligent.",
            "Système en mode dégradé."
        ]
        
        fallback_text = random.choice(phrases_demo)
        self.logger.info(f"🔄 Fallback utilisé: {fallback_text}")
        
        if self.copy_to_clipboard(fallback_text):
            self.auto_paste()
    
    def copy_to_clipboard(self, text: str) -> bool:
        """Copier texte dans clipboard Windows"""
        try:
            import subprocess
            
            # PowerShell command pour clipboard
            cmd = ['powershell', '-command', f'Set-Clipboard -Value "{text}"']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                self.logger.info("📋 Texte copié dans clipboard")
                return True
            else:
                self.logger.error(f"❌ Erreur clipboard: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur copy_to_clipboard: {e}")
            return False
    
    def auto_paste(self):
        """Auto-paste universel optimisé"""
        try:
            import subprocess
            
            # PowerShell SendKeys pour paste universel
            cmd = [
                'powershell', '-command',
                'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("^v")'
            ]
            
            # Petit délai pour stabilité
            time.sleep(0.1)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                self.logger.info("⌨️ Auto-paste exécuté")
            else:
                self.logger.warning(f"⚠️ Auto-paste warning: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur auto_paste: {e}")
    
    def get_performance_stats(self) -> dict:
        """Statistiques performance"""
        stats = {
            'bridge_version': 'v2_optimized',
            'engine_ready': self.engine_ready,
            'running': self.running
        }
        
        if self.engine_ready:
            engine_status = self.engine.get_status()
            stats.update(engine_status)
        
        return stats
    
    def run(self):
        """Lancer le bridge optimisé"""
        try:
            self.logger.info("🚀 Démarrage Prism Bridge V2...")
            
            # 1. Démarrer services avec pre-loading
            if not self.start_services():
                self.logger.error("❌ Échec démarrage services")
                return
            
            # 2. Démarrer surveillance
            self.logger.info("👁️ Démarrage surveillance trigger...")
            self.watch_trigger_file()
            
        except KeyboardInterrupt:
            self.logger.info("⚡ Interruption clavier détectée")
        except Exception as e:
            self.logger.error(f"❌ Erreur bridge: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Arrêter le bridge proprement"""
        self.logger.info("🛑 Arrêt Prism Bridge V2...")
        self.running = False
        
        if self.engine_ready and self.engine:
            self.engine.stop_engine()
        
        self.logger.info("✅ Bridge V2 arrêté")


def main():
    """Point d'entrée principal"""
    print("🎙️ Prism_whisper2 Bridge V2 - Performance Optimized")
    print("Architecture: Talon → Bridge V2 → Engine Service (pre-loaded) → Clipboard")
    print("Optimisation: -4s latence via model pre-loading")
    print("--" * 25)
    
    bridge = PrismBridgeV2()
    
    try:
        bridge.run()
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 