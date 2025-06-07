#!/usr/bin/env python3
"""
SuperWhisper2 Overlays Simple - Test Phase 2.2
Version simplifiée pour diagnostiquer les problèmes
"""

import os
import sys
import time
import threading
import logging
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk


class SimpleOverlaySettings:
    """Settings simplifiés pour test"""
    
    def __init__(self):
        self.settings = {
            "transcription_overlay": {
                "enabled": True,
                "position": {"x": 50, "y": 50},
                "size": {"width": 600, "height": 150},
                "transparency": 0.85,
                "font_size": 16,
                "background_color": "#2C3E50",
                "text_color": "#ECF0F1"
            },
            "status_overlay": {
                "enabled": True,
                "position": {"x": 50, "y": 220},
                "size": {"width": 300, "height": 60},
                "transparency": 0.75,
                "background_color": "#27AE60",
                "text_color": "#FFFFFF"
            }
        }
    
    def get(self, overlay_type: str, key: str, default=None):
        return self.settings.get(overlay_type, {}).get(key, default)


class SimpleOverlay:
    """Overlay simplifié sans Win32"""
    
    def __init__(self, name: str, settings: SimpleOverlaySettings):
        self.name = name
        self.settings = settings
        self.root = None
        self.visible = False
        
        self.position = self.settings.get(name, "position", {"x": 100, "y": 100})
        self.size = self.settings.get(name, "size", {"width": 400, "height": 100})
        self.transparency = self.settings.get(name, "transparency", 0.8)
        
        print(f"✨ SimpleOverlay {name} initialisé")
    
    def create_window(self):
        """Créer fenêtre overlay simple"""
        self.root = tk.Toplevel()
        self.root.title(f"SuperWhisper2 - {self.name}")
        
        # Configuration basique sans Win32
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", self.transparency)
        
        # Position et taille
        x, y = self.position["x"], self.position["y"]
        w, h = self.size["width"], self.size["height"]
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
        print(f"✨ Fenêtre {self.name} créée à ({x},{y}) taille {w}x{h}")
    
    def show(self):
        """Afficher overlay"""
        if not self.root:
            self.create_window()
        
        if not self.visible:
            self.visible = True
            self.root.deiconify()
            print(f"👁️ Overlay {self.name} affiché")
    
    def hide(self):
        """Masquer overlay"""
        if self.visible and self.root:
            self.visible = False
            self.root.withdraw()
            print(f"🙈 Overlay {self.name} masqué")
    
    def destroy(self):
        """Détruire overlay"""
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
            self.root = None
        self.visible = False


class SimpleTranscriptionOverlay(SimpleOverlay):
    """Overlay transcription simplifié"""
    
    def __init__(self, settings: SimpleOverlaySettings):
        super().__init__("transcription_overlay", settings)
        self.text_label = None
        
        self.font_size = self.settings.get(self.name, "font_size", 16)
        self.bg_color = self.settings.get(self.name, "background_color", "#2C3E50")
        self.text_color = self.settings.get(self.name, "text_color", "#ECF0F1")
    
    def create_window(self):
        """Créer fenêtre transcription"""
        super().create_window()
        
        # Frame principal
        main_frame = tk.Frame(
            self.root,
            bg=self.bg_color,
            relief="flat",
            bd=2
        )
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Label texte
        self.text_label = tk.Label(
            main_frame,
            text="🎤 SuperWhisper2 Ready",
            font=("Segoe UI", self.font_size, "normal"),
            bg=self.bg_color,
            fg=self.text_color,
            wraplength=self.size["width"] - 20,
            justify="left",
            anchor="nw"
        )
        self.text_label.pack(fill="both", expand=True, padx=10, pady=10)
    
    def update_text(self, text: str, is_final: bool = False):
        """Mettre à jour texte"""
        if not self.text_label:
            return
        
        if is_final:
            self.text_label.config(text=f"🎤 {text}", fg=self.text_color)
        else:
            self.text_label.config(text=f"🎙️ {text}...", fg="#BDC3C7")
        
        if not self.visible:
            self.show()
        
        print(f"📝 Transcription: {text[:50]}...")


class SimpleStatusOverlay(SimpleOverlay):
    """Overlay statut simplifié"""
    
    def __init__(self, settings: SimpleOverlaySettings):
        super().__init__("status_overlay", settings)
        self.status_label = None
        
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
            bd=2
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
            self.status_label.config(text=status, bg=color)
            
            if not self.visible:
                self.show()


class SimpleOverlayManager:
    """Gestionnaire overlays simplifié"""
    
    def __init__(self):
        self.settings = SimpleOverlaySettings()
        self.overlays = {}
        
        # Créer overlays
        self._create_overlays()
        print("🎯 SimpleOverlayManager initialisé")
    
    def _create_overlays(self):
        """Créer overlays simples"""
        self.overlays["transcription"] = SimpleTranscriptionOverlay(self.settings)
        self.overlays["status"] = SimpleStatusOverlay(self.settings)
        print(f"✨ {len(self.overlays)} overlays simples créés")
    
    def show_all(self):
        """Afficher tous les overlays"""
        for overlay in self.overlays.values():
            overlay.show()
        print("👁️ Tous les overlays affichés")
    
    def hide_all(self):
        """Masquer tous les overlays"""
        for overlay in self.overlays.values():
            overlay.hide()
        print("🙈 Tous les overlays masqués")
    
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
            self.overlays["status"].update_status(f"✅ Complete ({duration:.1f}s)", "#27AE60")
    
    def destroy_all(self):
        """Détruire tous les overlays"""
        for overlay in self.overlays.values():
            overlay.destroy()
        self.overlays.clear()
        print("🗑️ Tous les overlays détruits")


def main():
    """Test overlays simples"""
    try:
        print("🎯 SuperWhisper2 Overlays Simple - Test Phase 2.2")
        print("=" * 60)
        
        # Root tkinter
        root = tk.Tk()
        root.withdraw()
        
        print("🔧 Création manager overlays...")
        manager = SimpleOverlayManager()
        
        print("🔧 Test séquence complète...")
        
        # Étape 1: Afficher overlays
        print("\n📍 Étape 1: Affichage overlays")
        manager.show_all()
        root.update()
        
        # Attendre un peu
        print("⏱️ Attente 2s...")
        time.sleep(2)
        root.update()
        
        # Étape 2: Simulation recording
        print("\n📍 Étape 2: Simulation recording")
        manager.start_recording()
        root.update()
        
        # Attendre un peu
        print("⏱️ Attente 1s...")
        time.sleep(1)
        root.update()
        
        # Étape 3: Transcription progressive
        print("\n📍 Étape 3: Transcription progressive")
        
        manager.update_transcription("Bonjour", False)
        root.update()
        time.sleep(0.5)
        
        manager.update_transcription("Bonjour, ceci est", False)
        root.update()
        time.sleep(0.5)
        
        manager.update_transcription("Bonjour, ceci est un test", False)
        root.update()
        time.sleep(0.5)
        
        # Étape 4: Fin transcription
        print("\n📍 Étape 4: Fin transcription")
        manager.stop_recording()
        root.update()
        
        time.sleep(1)
        
        manager.transcription_complete("Bonjour, ceci est un test de transcription", 3.2)
        root.update()
        
        print("\n✅ Test terminé avec succès!")
        print("💡 Overlays visibles? (o/n)")
        print("⏸️ Appuyez sur Ctrl+C pour fermer")
        
        # Garder ouvert 10 secondes pour observation
        for i in range(10):
            root.update()
            time.sleep(1)
        
        print("\n🔧 Nettoyage...")
        manager.destroy_all()
        
    except KeyboardInterrupt:
        print("\n👋 Test interrompu par utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            manager.destroy_all()
            root.quit()
        except:
            pass


if __name__ == "__main__":
    main() 