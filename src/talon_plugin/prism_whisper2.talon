os: windows
-

# Prism_whisper2 - Talon Voice Integration
# Hotkey: Win+Alt+V pour transcription vocale

# Global hotkey pour démarrer transcription
key(win-alt-v): user.prism_transcribe()

# Actions utilisateur
user.prism_transcribe():
    # Signaler début transcription
    user.prism_signal_start()
    # TODO: Attendre fin transcription + insertion automatique

user.prism_signal_start():
    # Méthode 1: Créer fichier signal pour bridge Python
    user.prism_create_signal_file()

user.prism_create_signal_file():
    # Créer fichier trigger pour communication avec Python
    # Le bridge Python surveille ce fichier
    user.system_command("echo transcribe > C:\\Dev\\Superwhisper2\\talon_trigger.txt") 