import json
import os
import time

# --- Configuration du chemin de communication ---
# Doit correspondre exactement au chemin dans le script Talon
TEMP_DIR = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp', 'superwhisper_talon_bridge')
COMMAND_FILE_PATH = os.path.join(TEMP_DIR, 'command.json')

def send_command_to_talon(command: str, data: str):
    """Écrit une commande dans le fichier partagé pour que Talon la lise."""
    # S'assurer que le répertoire existe, au cas où Talon n'aurait pas encore été lancé
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    command_payload = {
        "command": command,
        "data": data,
        "timestamp": time.time()  # Pour garantir que le fichier est bien modifié
    }
    
    try:
        with open(COMMAND_FILE_PATH, 'w') as f:
            json.dump(command_payload, f)
        print(f"-> Sent command '{command}' with data '{data}' to Talon.")
    except Exception as e:
        print(f"Error sending command to Talon: {e}")

if __name__ == "__main__":
    print("--- Talon RPC Proof of Concept ---")
    print(f"Ce script va envoyer une commande à Talon via le fichier :")
    print(f"{COMMAND_FILE_PATH}\n")
    
    print("Assurez-vous que Talon est en cours d'exécution et que le script 'prism_bridge_poc.py' est actif.")
    print("Ouvrez un éditeur de texte (ex: Notepad) pour voir le résultat de la commande 'insert_text'.\n")
    
    # Test 1: Envoyer une commande pour insérer du texte
    input("Appuyez sur Entrée pour envoyer la commande 'Hello from SuperWhisper!'...")
    send_command_to_talon("insert_text", "Hello from SuperWhisper!")
    
    print("\nLa commande a été envoyée. Vérifiez votre éditeur de texte.")
    print("Une notification devrait aussi apparaître.")

    # Test 2: Envoyer une commande "générique"
    input("\nAppuyez sur Entrée pour envoyer la commande 'play_sound'...")
    send_command_to_talon("execute", "play_sound")
    print("\nLa commande a été envoyée. Vérifiez les notifications système.")

    print("\n--- Test Terminé ---") 