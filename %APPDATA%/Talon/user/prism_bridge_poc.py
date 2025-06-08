from talon import Module, actions, fs, app
import json
import os
import time

# --- Notification de chargement du module ---
def notify_load():
    app.notify("PrismBridge", "Le module de pont est en cours de chargement...")
# Lancer la notification au moment où le module est interprété par Python
notify_load()

# --- Définition du chemin de communication ---
TEMP_DIR = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp', 'superwhisper_talon_bridge')
COMMAND_FILE_PATH = os.path.join(TEMP_DIR, 'command.json')

os.makedirs(TEMP_DIR, exist_ok=True)

mod = Module()

@mod.action_class
class Actions:
    def prism_poc_insert_text(text: str):
        """Inserts text. Notifies on execution."""
        app.notify("PrismBridge", f"Action: Insertion de '{text}'")
        actions.insert(text)

    def prism_poc_execute_command(command: str, data: str = ""):
        """Executes a command. Notifies on execution."""
        app.notify("PrismBridge", f"Action: Exécution de '{command}'")
        # Ici, vous pourriez ajouter une logique pour mapper les commandes à des actions Talon réelles
        print(f"[PrismBridge POC] Commande générique reçue: {command} avec data: {data}")

# --- Logique de surveillance de fichier ---
def on_command_file_change(path, flags):
    """Callback exécuté lorsque le fichier de commande est modifié."""
    try:
        app.notify("PrismBridge", f"Détection de changement sur {os.path.basename(path)}!")
        
        if not os.path.exists(COMMAND_FILE_PATH):
            print("[PrismBridge] Fichier de commande non trouvé après changement.")
            return

        with open(COMMAND_FILE_PATH, 'r') as f:
            content = f.read()
        
        if not content.strip():
            print("[PrismBridge] Fichier de commande est vide.")
            return

        app.notify("PrismBridge", "Lecture du contenu du fichier...")
        command_data = json.loads(content)
        command = command_data.get("command")
        data = command_data.get("data", "")

        app.notify("PrismBridge", f"Commande reçue: {command}")

        if command == "insert_text":
            actions.user.prism_poc_insert_text(data)
        elif command == "execute":
            actions.user.prism_poc_execute_command(data)
        else:
            app.notify("PrismBridge", f"Commande inconnue: {command}")
        
        # Effacer le fichier après traitement pour éviter les exécutions multiples
        # Ceci est critique pour la stabilité
        with open(COMMAND_FILE_PATH, 'w') as f:
            f.write('')
        print(f"[PrismBridge] Fichier de commande '{os.path.basename(path)}' traité et vidé.")

    except json.JSONDecodeError:
        app.notify("PrismBridge ERROR", "Erreur de décodage JSON.")
        print(f"[PrismBridge] Erreur de décodage JSON depuis {COMMAND_FILE_PATH}")
    except Exception as e:
        app.notify("PrismBridge ERROR", f"Erreur: {e}")
        print(f"[PrismBridge] Erreur lors du traitement du fichier de commande: {e}")

def start_watching():
    """Initialise la surveillance du fichier."""
    # S'assurer que le fichier existe avant de le surveiller
    if not os.path.exists(COMMAND_FILE_PATH):
        open(COMMAND_FILE_PATH, 'w').close()
    
    fs.watch(COMMAND_FILE_PATH, on_command_file_change)
    msg = f"Surveillance démarrée pour {COMMAND_FILE_PATH}"
    print(f"[PrismBridge] {msg}")
    app.notify("PrismBridge", msg)

# Enregistrer la fonction pour qu'elle s'exécute quand Talon est prêt
app.register("ready", start_watching) 