#!/usr/bin/env python3
"""
SuperWhisper2 Overlays - Phase 2.2
Affichage transcription temps réel + waveform audio
"""

import os
import sys
import time
import threading
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Tuple, List
import tkinter as tk
from tkinter import ttk
import win32gui
import win32con


class OverlaySettings:
    """Gestionnaire des paramètres overlays persistants"""
    
    def __init__(self, config_file: str = "overlay_settings.json"):
        self.project_root = Path(__file__).parent.parent.parent
        self.config_file = self.project_root / "config" / config_file
        
        # Assurer que le répertoire config existe
        self.config_file.parent.mkdir(exist_ok=True)
        
        # Settings par défaut
        self.default_settings = {
            "transcription_overlay": {
                "enabled": True,
                "position": {"x": 50, "y": 50},
                "size": {"width": 600, "height": 150},
                "transparency": 0.85,
                "font_size": 16,
                "font_family": "Segoe UI",
                "background_color": "#2C3E50",
                "text_color": "#ECF0F1",
                "fade_duration": 5.0
            },
            "status_overlay": {
                "enabled": True,
                "position": {"x": 50, "y": 220},
                "size": {"width": 300, "height": 60},
                "transparency": 0.75,
                "background_color": "#27AE60",
                "text_color": "#FFFFFF"
            },
            "general": {
                "monitor_index": 0,
                "hotkey_toggle": "F12",
                "auto_hide_delay": 8.0,
                "animations_enabled": True
            }
        }
        
        self.settings = self.load_settings()
    
    def load_settings(self) -> dict:
        """Charger settings depuis fichier JSON"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                return {**self.default_settings, **loaded}
            else:
                return self.default_settings.copy()
        except Exception:
            return self.default_settings.copy()
    
    def save_settings(self):
        """Sauvegarder settings dans fichier JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur sauvegarde settings: {e}")
    
    def get(self, overlay_type: str, key: str, default=None):
        """Obtenir setting spécifique"""
        return self.settings.get(overlay_type, {}).get(key, default)
    
    def set(self, overlay_type: str, key: str, value):
        """Définir setting spécifique"""
        if overlay_type not in self.settings:
            self.settings[overlay_type] = {}
        self.settings[overlay_type][key] = value
        self.save_settings()


class BaseOverlay:
    """Classe de base pour tous les overlays"""
    
    def __init__(self, name: str, settings: OverlaySettings):
        self.name = name
        self.settings = settings
        self.root = None
        self.visible = False
        
        # Configuration overlay
        self.position = self.settings.get(name, "position", {"x": 100, "y": 100})
        self.size = self.settings.get(name, "size", {"width": 400, "height": 100})
        self.transparency = self.settings.get(name, "transparency", 0.8)
        
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging pour overlay"""
        logger = logging.getLogger(f'Overlay_{self.name}')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def create_window(self):
        """Créer fenêtre overlay de base"""
        self.root = tk.Toplevel()
        self.root.title(f"SuperWhisper2 - {self.name}")
        
        # Configuration fenêtre overlay
        self.root.overrideredirect(True)  # Pas de barre de titre
        self.root.wm_attributes("-topmost", True)  # Toujours au-dessus
        self.root.wm_attributes("-alpha", self.transparency)  # Transparence
        
        # Position et taille
        x, y = self.position["x"], self.position["y"]
        w, h = self.size["width"], self.size["height"]
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
        # Rendre non-cliquable (pass-through events)
        self._make_clickthrough()
        
        self.logger.info(f"✨ Overlay {self.name} créé à ({x},{y}) taille {w}x{h}")
    
    def _make_clickthrough(self):
        """Rendre l'overlay non-cliquable (pass-through)"""
        # TEMPORAIREMENT DÉSACTIVÉ - causait des blocages
        # Les overlays restent cliquables pour le moment
        self.logger.info("⚠️ Clickthrough désactivé temporairement")
        
        # TODO: Réimplémenter sans blocage
        # try:
        #     # Utiliser Win32 API pour rendre transparent aux clics
        #     hwnd = self.root.winfo_id()
        #     
        #     # Get extended window style
        #     extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        #     
        #     # Add WS_EX_TRANSPARENT style
        #     extended_style |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
        #     
        #     # Set the new extended style
        #     win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style)
        #     
        # except Exception as e:
        #     self.logger.warning(f"⚠️ Clickthrough non disponible: {e}")
    
    def show(self):
        """Afficher overlay"""
        if not self.root:
            self.create_window()
        
        if not self.visible:
            self.visible = True
            self.root.deiconify()
            self.logger.info(f"👁️ Overlay {self.name} affiché")
    
    def hide(self):
        """Masquer overlay"""
        if self.visible and self.root:
            self.visible = False
            self.root.withdraw()
            self.logger.info(f"🙈 Overlay {self.name} masqué")
    
    def destroy(self):
        """Détruire overlay"""
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
            self.root = None
        self.visible = False


class TranscriptionOverlay(BaseOverlay):
    """Overlay affichage transcription temps réel"""
    
    def __init__(self, settings: OverlaySettings):
        super().__init__("transcription_overlay", settings)
        self.current_text = ""
        self.text_label = None
        self.auto_hide_timer = None
        
        # Style configuration
        self.font_size = self.settings.get(self.name, "font_size", 16)
        self.font_family = self.settings.get(self.name, "font_family", "Segoe UI")
        self.bg_color = self.settings.get(self.name, "background_color", "#2C3E50")
        self.text_color = self.settings.get(self.name, "text_color", "#ECF0F1")
        self.fade_duration = self.settings.get(self.name, "fade_duration", 5.0)
    
    def create_window(self):
        """Créer fenêtre transcription avec style moderne"""
        super().create_window()
        
        # Frame principal avec style moderne
        main_frame = tk.Frame(
            self.root,
            bg=self.bg_color,
            relief="flat",
            bd=0
        )
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Label pour le texte transcription
        self.text_label = tk.Label(
            main_frame,
            text="",
            font=(self.font_family, self.font_size, "normal"),
            bg=self.bg_color,
            fg=self.text_color,
            wraplength=self.size["width"] - 20,
            justify="left",
            anchor="nw"
        )
        self.text_label.pack(fill="both", expand=True, padx=10, pady=10)
    
    def update_text(self, text: str, is_final: bool = False):
        """Mettre à jour texte transcription"""
        if not self.text_label:
            return
        
        self.current_text = text
        
        # Style différent selon si c'est final ou en cours
        if is_final:
            # Texte final - couleur normale
            self.text_label.config(
                text=f"🎤 {text}",
                fg=self.text_color
            )
            
            # Programmer auto-hide après délai
            self._schedule_auto_hide()
        else:
            # Transcription en cours - couleur plus claire
            lighter_color = "#BDC3C7"  # Plus clair pour indiquer temporaire
            self.text_label.config(
                text=f"🎙️ {text}...",
                fg=lighter_color
            )
        
        # Afficher si pas déjà visible
        if not self.visible:
            self.show()
        
        self.logger.info(f"📝 Transcription: {text[:50]}...")
    
    def _schedule_auto_hide(self):
        """Programmer masquage automatique"""
        # Annuler timer précédent
        if self.auto_hide_timer:
            self.auto_hide_timer.cancel()
        
        # Nouveau timer
        self.auto_hide_timer = threading.Timer(
            self.fade_duration,
            self.hide
        )
        self.auto_hide_timer.start()


class StatusOverlay(BaseOverlay):
    """Overlay statut service et progression"""
    
    def __init__(self, settings: OverlaySettings):
        super().__init__("status_overlay", settings)
        self.status_label = None
        
        # Style
        self.bg_color = self.settings.get(self.name, "background_color", "#27AE60")
        self.text_color = self.settings.get(self.name, "text_color", "#FFFFFF")
    
    def create_window(self):
        """Créer fenêtre statut"""
        super().create_window()
        
        # Frame principal
        main_frame = tk.Frame(
            self.root,
            bg=self.bg_color,
            relief="flat",
            bd=0
        )
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Label statut
        self.status_label = tk.Label(
            main_frame,
            text="🟢 SuperWhisper2 Ready",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        self.status_label.pack(pady=10)
    
    def update_status(self, status: str, color: str = "#27AE60"):
        """Mettre à jour statut"""
        if self.status_label:
            self.status_label.config(text=status)
            
            # Mettre à jour couleur de fond
            self.status_label.config(bg=color)
            
            # Afficher si pas visible
            if not self.visible:
                self.show()


class OverlayManager:
    """Gestionnaire principal des overlays"""
    
    def __init__(self):
        self.settings = OverlaySettings()
        self.overlays = {}
        self.logger = self._setup_logging()
        
        # Créer overlays
        self._create_overlays()
        
        # État global
        self.overlays_enabled = True
        
        self.logger.info("🎯 OverlayManager initialisé")
    
    def _setup_logging(self):
        """Setup logging"""
        logger = logging.getLogger('OverlayManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - OVERLAY - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _create_overlays(self):
        """Créer tous les overlays"""
        # Overlay transcription
        if self.settings.get("transcription_overlay", "enabled", True):
            self.overlays["transcription"] = TranscriptionOverlay(self.settings)
        
        # Overlay statut
        if self.settings.get("status_overlay", "enabled", True):
            self.overlays["status"] = StatusOverlay(self.settings)
        
        self.logger.info(f"✨ {len(self.overlays)} overlays créés")
    
    def show_all(self):
        """Afficher tous les overlays activés"""
        if not self.overlays_enabled:
            return
        
        for overlay in self.overlays.values():
            overlay.show()
        
        self.logger.info("👁️ Tous les overlays affichés")
    
    def hide_all(self):
        """Masquer tous les overlays"""
        for overlay in self.overlays.values():
            overlay.hide()
        
        self.logger.info("🙈 Tous les overlays masqués")
    
    def toggle_overlays(self):
        """Toggle affichage overlays"""
        self.overlays_enabled = not self.overlays_enabled
        
        if self.overlays_enabled:
            self.show_all()
        else:
            self.hide_all()
        
        self.logger.info(f"🔄 Overlays {'activés' if self.overlays_enabled else 'désactivés'}")
    
    def update_transcription(self, text: str, is_final: bool = False):
        """Mettre à jour transcription"""
        if "transcription" in self.overlays:
            self.overlays["transcription"].update_text(text, is_final)
    
    def start_recording(self):
        """Démarrer enregistrement"""
        if "status" in self.overlays:
            self.overlays["status"].update_status("🔴 Recording...", "#E74C3C")
    
    def stop_recording(self):
        """Arrêter enregistrement"""
        if "status" in self.overlays:
            self.overlays["status"].update_status("🟠 Processing...", "#F39C12")
    
    def transcription_complete(self, text: str, duration: float):
        """Transcription terminée"""
        if "transcription" in self.overlays:
            self.overlays["transcription"].update_text(text, is_final=True)
        
        if "status" in self.overlays:
            self.overlays["status"].update_status(
                f"✅ Complete ({duration:.1f}s)",
                "#27AE60"
            )
            
            # Retour à ready après délai
            threading.Timer(3.0, lambda: self.overlays["status"].update_status(
                "🟢 SuperWhisper2 Ready",
                "#27AE60"
            )).start()
    
    def destroy_all(self):
        """Détruire tous les overlays"""
        for overlay in self.overlays.values():
            overlay.destroy()
        
        self.overlays.clear()
        self.logger.info("🗑️ Tous les overlays détruits")


def main():
    """Test des overlays"""
    try:
        print("🎯 SuperWhisper2 Overlays - Phase 2.2")
        print("Test des overlays transcription temps réel")
        print("-" * 50)
        
        # Créer root tkinter invisible
        root = tk.Tk()
        root.withdraw()  # Masquer fenêtre principale
        
        # Créer manager overlays
        manager = OverlayManager()
        
        print("✨ Overlays créés")
        print("🔧 Test séquence complète...")
        
        # Test séquence
        manager.show_all()
        time.sleep(2)
        
        manager.start_recording()
        time.sleep(3)
        
        # Simulation transcription progressive
        manager.update_transcription("Bonjour", False)
        time.sleep(1)
        manager.update_transcription("Bonjour, ceci est", False)
        time.sleep(1)
        manager.update_transcription("Bonjour, ceci est un test", False)
        time.sleep(1)
        
        manager.stop_recording()
        
        # Transcription finale
        manager.transcription_complete("Bonjour, ceci est un test de transcription temps réel", 5.2)
        
        print("✅ Test terminé - Overlays fonctionnels")
        print("💡 Appuyez sur Ctrl+C pour fermer")
        
        # Boucle événements
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n👋 Overlays fermés")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        try:
            manager.destroy_all()
        except:
            pass


if __name__ == "__main__":
    main() 