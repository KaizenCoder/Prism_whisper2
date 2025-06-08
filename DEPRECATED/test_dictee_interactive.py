#!/usr/bin/env python3
"""
Test de dictée interactive pour SuperWhisper2
Interface simple avec affichage en temps réel
"""

import os
import sys
import time
import threading
import tkinter as tk
from pathlib import Path

# Configuration GPU RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # RTX 3090 sur GPU 1
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajout des modules au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from ui.overlays_simple import SimpleOverlayManager
    from core.whisper_engine_v5 import SuperWhisper2EngineV5
    from core.streaming_manager import AudioStreamingManager
except ImportError as e:
    print(f"❌ Erreur import: {e}")
    print("Modules requis manquants. Utilisation d'une version simplifiée...")
    sys.exit(1)


class DicteeInteractive:
    """Interface de dictée interactive avec affichage temps réel"""
    
    def __init__(self):
        self.running = False
        self.engine = None
        self.streaming_manager = None
        self.overlay_manager = None
        self.root = None
        
    def setup_interface(self):
        """Configuration interface graphique"""
        self.root = tk.Tk()
        self.root.title("SuperWhisper2 - Dictée Interactive")
        self.root.geometry("400x200")
        
        # Interface simple
        tk.Label(self.root, text="SuperWhisper2 - Dictée Interactive", 
                font=("Arial", 16, "bold")).pack(pady=20)
        
        self.status_label = tk.Label(self.root, text="Initialisation...", 
                                   font=("Arial", 12))
        self.status_label.pack(pady=10)
        
        # Boutons
        self.start_btn = tk.Button(self.root, text="Démarrer Dictée", 
                                 command=self.start_dictee, 
                                 bg="#27AE60", fg="white", 
                                 font=("Arial", 12, "bold"))
        self.start_btn.pack(pady=5)
        
        self.stop_btn = tk.Button(self.root, text="Arrêter", 
                                command=self.stop_dictee,
                                bg="#E74C3C", fg="white",
                                font=("Arial", 12, "bold"),
                                state="disabled")
        self.stop_btn.pack(pady=5)
        
        # Bouton quitter
        tk.Button(self.root, text="Quitter", 
                 command=self.quit_app,
                 font=("Arial", 10)).pack(pady=10)
    
    def setup_engine(self):
        """Configuration moteur Whisper"""
        try:
            self.status_label.config(text="Chargement moteur Whisper...")
            self.root.update()
            
            # Configuration engine (CPU pour éviter problème CUDA)
            self.engine = SuperWhisper2EngineV5(device='cpu')
            
            # Callback pour affichage transcription
            self.engine.transcription_callback = self.on_transcription
            
            if self.engine.start_engine():
                self.status_label.config(text="✅ Moteur prêt")
                return True
            else:
                self.status_label.config(text="❌ Erreur moteur")
                return False
                
        except Exception as e:
            self.status_label.config(text=f"❌ Erreur: {e}")
            return False
    
    def setup_overlay(self):
        """Configuration overlay"""
        try:
            self.overlay_manager = SimpleOverlayManager()
            return True
        except Exception as e:
            print(f"❌ Erreur overlay: {e}")
            return False
    
    def on_transcription(self, text):
        """Callback transcription - affichage temps réel"""
        if self.overlay_manager:
            self.overlay_manager.update_transcription(text, is_final=True)
        
        print(f"📝 Transcription: {text}")
    
    def start_dictee(self):
        """Démarrer mode dictée"""
        if not self.running:
            self.running = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="🎤 Dictée active - Parlez!")
            
            # Afficher overlays
            if self.overlay_manager:
                self.overlay_manager.show_all()
                self.overlay_manager.start_recording()
            
            # Démarrer streaming
            if hasattr(self.engine, 'start_streaming_mode'):
                self.engine.start_streaming_mode()
            
            print("🎤 Mode dictée démarré - Parlez maintenant!")
    
    def stop_dictee(self):
        """Arrêter mode dictée"""
        if self.running:
            self.running = False
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.status_label.config(text="🟢 Prêt")
            
            # Arrêter streaming
            if hasattr(self.engine, 'stop_streaming_mode'):
                self.engine.stop_streaming_mode()
            
            # Masquer overlays
            if self.overlay_manager:
                self.overlay_manager.stop_recording()
                self.overlay_manager.hide_all()
            
            print("⏹️ Mode dictée arrêté")
    
    def quit_app(self):
        """Quitter application"""
        self.stop_dictee()
        
        if self.overlay_manager:
            self.overlay_manager.destroy_all()
        
        if self.engine:
            self.engine.stop_engine()
        
        self.root.quit()
    
    def run(self):
        """Lancer application"""
        print("🚀 SuperWhisper2 - Dictée Interactive")
        print("=" * 50)
        
        # Setup interface
        self.setup_interface()
        
        # Setup overlay
        if not self.setup_overlay():
            print("⚠️ Overlay non disponible, mode console seulement")
        
        # Setup engine
        if not self.setup_engine():
            print("❌ Impossible de démarrer le moteur")
            return
        
        print("✅ Interface prête!")
        print("💡 Cliquez sur 'Démarrer Dictée' puis parlez")
        
        # Démarrer interface
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 Application fermée")
        finally:
            self.quit_app()


def main():
    """Point d'entrée principal"""
    app = DicteeInteractive()
    app.run()


if __name__ == "__main__":
    main() 