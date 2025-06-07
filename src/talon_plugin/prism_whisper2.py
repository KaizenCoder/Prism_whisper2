"""
Prism_whisper2 - Talon Python Module
Actions pour integration Talon ↔ Python Bridge
"""

import os
import subprocess
from talon import Module, actions

# Module Talon pour nos actions personnalisées
mod = Module()

@mod.action_class
class Actions:
    def prism_transcribe():
        """Déclencher une transcription Prism_whisper2"""
        # Créer signal file pour bridge
        trigger_file = r"C:\Dev\Superwhisper2\talon_trigger.txt"
        try:
            with open(trigger_file, 'w') as f:
                f.write("transcribe\n")
            print(f"✅ Signal créé: {trigger_file}")
        except Exception as e:
            print(f"❌ Erreur signal: {e}")
    
    def prism_signal_start():
        """Signaler début de transcription"""
        actions.user.prism_create_signal_file()
    
    def prism_create_signal_file():
        """Créer fichier signal pour bridge Python"""
        actions.user.prism_transcribe()
    
    def system_command(command: str):
        """Exécuter commande système"""
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"✅ Commande exécutée: {command}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur commande: {e}")

print("🎙️ Prism_whisper2 Talon module loaded !") 