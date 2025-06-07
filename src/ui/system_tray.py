#!/usr/bin/env python3
"""
SuperWhisper2 System Tray - Phase 2.1
Interface utilisateur moderne avec intégration Bridge V4
Features: Icône animée, menu contextuel, notifications, contrôle service
"""

import os
import sys
import time
import threading
import logging
from pathlib import Path
from typing import Optional
import pystray
from PIL import Image, ImageDraw
import win32gui
import win32con
from plyer import notification

# Import Bridge V4 et Overlays
sys.path.append(str(Path(__file__).parent.parent))
from bridge.prism_bridge_v4 import PrismBridgeV4
from ui.overlays_simple import SimpleOverlayManager


class SuperWhisperSystemTray:
    """System Tray professionnel pour SuperWhisper2"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.log_file = self.project_root / "logs" / "system_tray.log"
        
        # Assurer que le répertoire logs existe
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Bridge V4
        self.bridge = None
        self.bridge_thread = None
        self.is_running = False
        self.is_recording = False
        self.is_processing = False
        
        # Overlays Manager
        self.overlay_manager = None
        self.overlays_enabled = True
        
        # System Tray
        self.tray_icon = None
        self.menu = None
        
        # Icons
        self.icon_idle = self._create_icon_idle()
        self.icon_recording = self._create_icon_recording()
        self.icon_processing = self._create_icon_processing()
        self.icon_error = self._create_icon_error()
        
        self.logger.info("🎯 SuperWhisper2 System Tray initialisé")
    
    def _setup_logging(self):
        """Setup logging pour System Tray"""
        logger = logging.getLogger('SystemTray')
        logger.setLevel(logging.INFO)
        
        if logger.handlers:
            logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - TRAY - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _create_icon_idle(self) -> Image.Image:
        """Créer icône idle (bleu)"""
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Microphone idle (bleu)
        draw.ellipse([16, 16, 48, 48], fill=(52, 152, 219, 255), outline=(41, 128, 185, 255), width=2)
        draw.rectangle([28, 24, 36, 40], fill=(255, 255, 255, 255))
        draw.ellipse([30, 42, 34, 46], fill=(255, 255, 255, 255))
        draw.line([32, 46, 32, 52], fill=(255, 255, 255, 255), width=2)
        draw.line([28, 52, 36, 52], fill=(255, 255, 255, 255), width=2)
        
        return image
    
    def _create_icon_recording(self) -> Image.Image:
        """Créer icône recording (rouge animé)"""
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Microphone recording (rouge)
        draw.ellipse([16, 16, 48, 48], fill=(231, 76, 60, 255), outline=(192, 57, 43, 255), width=2)
        draw.rectangle([28, 24, 36, 40], fill=(255, 255, 255, 255))
        draw.ellipse([30, 42, 34, 46], fill=(255, 255, 255, 255))
        draw.line([32, 46, 32, 52], fill=(255, 255, 255, 255), width=2)
        draw.line([28, 52, 36, 52], fill=(255, 255, 255, 255), width=2)
        
        # Indicateur recording
        draw.ellipse([50, 10, 60, 20], fill=(231, 76, 60, 255))
        
        return image
    
    def _create_icon_processing(self) -> Image.Image:
        """Créer icône processing (orange)"""
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Microphone processing (orange)
        draw.ellipse([16, 16, 48, 48], fill=(243, 156, 18, 255), outline=(230, 126, 34, 255), width=2)
        draw.rectangle([28, 24, 36, 40], fill=(255, 255, 255, 255))
        draw.ellipse([30, 42, 34, 46], fill=(255, 255, 255, 255))
        draw.line([32, 46, 32, 52], fill=(255, 255, 255, 255), width=2)
        draw.line([28, 52, 36, 52], fill=(255, 255, 255, 255), width=2)
        
        # Indicateur processing (gear)
        draw.ellipse([48, 8, 58, 18], fill=(243, 156, 18, 255))
        
        return image
    
    def _create_icon_error(self) -> Image.Image:
        """Créer icône error (rouge)"""
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Microphone error (rouge foncé)
        draw.ellipse([16, 16, 48, 48], fill=(192, 57, 43, 255), outline=(128, 38, 29, 255), width=2)
        draw.rectangle([28, 24, 36, 40], fill=(255, 255, 255, 255))
        draw.ellipse([30, 42, 34, 46], fill=(255, 255, 255, 255))
        draw.line([32, 46, 32, 52], fill=(255, 255, 255, 255), width=2)
        draw.line([28, 52, 36, 52], fill=(255, 255, 255, 255), width=2)
        
        # X error
        draw.line([48, 8, 58, 18], fill=(192, 57, 43, 255), width=3)
        draw.line([58, 8, 48, 18], fill=(192, 57, 43, 255), width=3)
        
        return image
    
    def _create_menu(self):
        """Créer menu contextuel système tray"""
        menu_items = [
            pystray.MenuItem(
                "🎙️ SuperWhisper2",
                lambda: None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "▶️ Démarrer Service" if not self.is_running else "⏸️ Arrêter Service",
                self._toggle_service
            ),
            pystray.MenuItem(
                "📊 Statistiques",
                self._show_stats
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "👁️ Overlays" if self.overlays_enabled else "🙈 Overlays",
                self._toggle_overlays
            ),
            pystray.MenuItem(
                "⚙️ Configuration",
                self._open_settings
            ),
            pystray.MenuItem(
                "📋 Test Transcription",
                self._test_transcription
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "ℹ️ À propos",
                self._show_about
            ),
            pystray.MenuItem(
                "❌ Quitter",
                self._quit_application
            )
        ]
        
        return pystray.Menu(*menu_items)
    
    def _toggle_service(self, icon=None, item=None):
        """Démarrer/Arrêter le service SuperWhisper2"""
        if not self.is_running:
            self._start_service()
        else:
            self._stop_service()
    
    def _start_service(self):
        """Démarrer service Bridge V4"""
        try:
            self.logger.info("🚀 Démarrage service SuperWhisper2...")
            
            # Notification
            self._show_notification(
                "SuperWhisper2",
                "Démarrage du service de transcription...",
                "info"
            )
            
            # Démarrer Bridge V4 dans thread séparé
            self.bridge = PrismBridgeV4()
            self.bridge_thread = threading.Thread(
                target=self._run_bridge_service,
                daemon=True
            )
            self.bridge_thread.start()
            
            self.is_running = True
            self._update_icon(self.icon_idle)
            self._update_menu()
            
            self.logger.info("✅ Service SuperWhisper2 démarré")
            
            # Notification succès
            self._show_notification(
                "SuperWhisper2",
                "Service démarré! Utilisez Win+Alt+V pour transcrire",
                "success"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage service: {e}")
            self._show_notification(
                "SuperWhisper2 - Erreur",
                f"Échec démarrage: {str(e)[:50]}...",
                "error"
            )
            self._update_icon(self.icon_error)
    
    def _stop_service(self):
        """Arrêter service Bridge V4"""
        try:
            self.logger.info("⏸️ Arrêt service SuperWhisper2...")
            
            self.is_running = False
            
            if self.bridge:
                self.bridge.stop_bridge()
                self.bridge = None
            
            self._update_icon(self.icon_idle)
            self._update_menu()
            
            self.logger.info("✅ Service SuperWhisper2 arrêté")
            
            # Notification
            self._show_notification(
                "SuperWhisper2",
                "Service arrêté",
                "info"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur arrêt service: {e}")
    
    def _run_bridge_service(self):
        """Exécuter Bridge V4 dans thread séparé"""
        try:
            self.bridge.start_bridge()
        except Exception as e:
            self.logger.error(f"❌ Erreur Bridge V4: {e}")
            self.is_running = False
            self._update_icon(self.icon_error)
    
    def _show_stats(self, icon=None, item=None):
        """Afficher statistiques service"""
        try:
            if self.bridge:
                stats = self.bridge.get_bridge_stats()
                
                stats_text = f"""📊 Statistiques SuperWhisper2
                
Transcriptions: {stats.get('total_transcriptions', 0)}
Temps moyen: {stats.get('average_time', 0):.2f}s
GPU optimisations: {stats.get('gpu_optimizations', 0)}
Service actif: {'✅ Oui' if self.is_running else '❌ Non'}"""
                
                self._show_notification(
                    "SuperWhisper2 - Statistiques",
                    stats_text.replace('\n', ' | '),
                    "info"
                )
            else:
                self._show_notification(
                    "SuperWhisper2 - Statistiques",
                    "Service non démarré",
                    "info"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Erreur stats: {e}")
    
    def _test_transcription(self, icon=None, item=None):
        """Test transcription manuelle"""
        try:
            if not self.is_running:
                self._show_notification(
                    "SuperWhisper2 - Test",
                    "Démarrez d'abord le service",
                    "warning"
                )
                return
            
            # Test avec overlays si disponibles
            if self.overlay_manager and self.overlays_enabled:
                self._test_with_overlays()
            else:
                # Test classique
                trigger_file = self.project_root / "talon_trigger.txt"
                trigger_file.write_text("transcribe")
            
            self._show_notification(
                "SuperWhisper2 - Test",
                "Test de transcription lancé...",
                "info"
            )
            
            self.logger.info("🧪 Test transcription manuel lancé")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur test: {e}")
    
    def _test_with_overlays(self):
        """Test transcription avec démonstration overlays"""
        try:
            # Démarrer recording
            self.overlay_manager.start_recording()
            self._update_icon(self.icon_recording)
            
            # Transcription progressive (simulée pour démo)
            texts = [
                "Test overlays",
                "Test overlays en cours",
                "Test overlays en cours de transcription",
                "Test overlays en cours de transcription temps réel"
            ]
            
            for i, text in enumerate(texts):
                threading.Timer(
                    1.0 + i * 0.8,
                    lambda t=text: self.overlay_manager.update_transcription(t, False)
                ).start()
            
            # Finaliser transcription et lancer vraie transcription
            def finalize():
                self.overlay_manager.transcription_complete(
                    "Test overlays: démonstration terminée",
                    3.2
                )
                self._update_icon(self.icon_idle)
                
                # Maintenant lancer vraie transcription
                trigger_file = self.project_root / "talon_trigger.txt"
                trigger_file.write_text("transcribe")
            
            threading.Timer(4.5, finalize).start()
            
            self.logger.info("🎬 Test overlays + transcription lancé")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur test overlays: {e}")
    
    def _toggle_overlays(self, icon=None, item=None):
        """Toggle affichage overlays"""
        try:
            if not self.overlay_manager:
                # Initialiser overlays au premier usage
                self.overlay_manager = SimpleOverlayManager()
                self.logger.info("✨ Overlay Manager initialisé")
            
            self.overlays_enabled = not self.overlays_enabled
            
            if self.overlays_enabled:
                self.overlay_manager.show_all()
                self._show_notification(
                    "SuperWhisper2 - Overlays",
                    "Overlays activés",
                    "success"
                )
                self.logger.info("👁️ Overlays activés")
            else:
                self.overlay_manager.hide_all()
                self._show_notification(
                    "SuperWhisper2 - Overlays",
                    "Overlays masqués",
                    "info"
                )
                self.logger.info("🙈 Overlays masqués")
            
            # Mettre à jour menu
            self._update_menu()
            
        except Exception as e:
            self.logger.error(f"❌ Erreur toggle overlays: {e}")
            self._show_notification(
                "SuperWhisper2 - Erreur",
                f"Erreur overlays: {str(e)[:50]}...",
                "error"
            )
    
    def _open_settings(self, icon=None, item=None):
        """Ouvrir configuration (Phase 2.3)"""
        self._show_notification(
            "SuperWhisper2 - Configuration",
            "Interface de configuration en développement (Phase 2.3)",
            "info"
        )
    
    def _show_about(self, icon=None, item=None):
        """Afficher informations application"""
        about_text = """SuperWhisper2 v2.0
Transcription vocale ultra-rapide
Phase 2: Interface & UX moderne
GPU RTX 3090 optimisé"""
        
        self._show_notification(
            "SuperWhisper2 - À propos",
            about_text.replace('\n', ' | '),
            "info"
        )
    
    def _quit_application(self, icon=None, item=None):
        """Quitter application"""
        self.logger.info("👋 Fermeture SuperWhisper2...")
        
        # Arrêter service
        if self.is_running:
            self._stop_service()
        
        # Notification
        self._show_notification(
            "SuperWhisper2",
            "Application fermée",
            "info"
        )
        
        # Quitter tray
        if self.tray_icon:
            self.tray_icon.stop()
    
    def _update_icon(self, new_icon: Image.Image):
        """Mettre à jour icône système tray"""
        if self.tray_icon:
            self.tray_icon.icon = new_icon
    
    def _update_menu(self):
        """Mettre à jour menu contextuel"""
        if self.tray_icon:
            self.tray_icon.menu = self._create_menu()
    
    def _show_notification(self, title: str, message: str, notification_type: str = "info"):
        """Afficher notification Windows"""
        try:
            # Icône selon type
            icon_path = None
            if notification_type == "success":
                timeout = 3
            elif notification_type == "error":
                timeout = 5
            elif notification_type == "warning":
                timeout = 4
            else:
                timeout = 3
            
            notification.notify(
                title=title,
                message=message,
                timeout=timeout,
                toast=True
            )
            
            self.logger.info(f"📢 Notification: {title} - {message}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur notification: {e}")
    
    def start_tray(self):
        """Démarrer système tray"""
        try:
            self.logger.info("🎯 Démarrage System Tray SuperWhisper2...")
            
            # Créer menu
            self.menu = self._create_menu()
            
            # Créer icône tray
            self.tray_icon = pystray.Icon(
                "SuperWhisper2",
                self.icon_idle,
                "SuperWhisper2 - Transcription vocale",
                self.menu
            )
            
            # Notification de démarrage
            self._show_notification(
                "SuperWhisper2",
                "Interface système démarrée. Clic droit pour le menu.",
                "success"
            )
            
            # Démarrer automatiquement le service
            threading.Timer(2.0, self._start_service).start()
            
            # Lancer tray (bloquant)
            self.tray_icon.run()
            
        except Exception as e:
            self.logger.error(f"❌ Erreur système tray: {e}")
            raise


def main():
    """Point d'entrée principal"""
    try:
        print("🎙️ SuperWhisper2 System Tray - Phase 2.1")
        print("Interface utilisateur moderne avec Bridge V4")
        print("-" * 50)
        
        # Créer et lancer système tray
        tray = SuperWhisperSystemTray()
        tray.start_tray()
        
    except KeyboardInterrupt:
        print("\n👋 Application fermée par utilisateur")
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        input("Appuyez sur Entrée pour fermer...")


if __name__ == "__main__":
    main() 