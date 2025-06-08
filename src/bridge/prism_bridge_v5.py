import json
import os
import time
from typing import Dict, Any

class PrismBridgeV5:
    """
    PrismBridgeV5 est responsable de la communication unidirectionnelle
    de SuperWhisper vers Talon Voice.

    Il envoie des commandes en écrivant dans un fichier JSON partagé, qui est
    surveillé par un script compagnon côté Talon.
    """
    def __init__(self):
        self.is_connected: bool = False
        self._temp_dir: str = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp', 'superwhisper_talon_bridge')
        self.command_file_path: str = os.path.join(self._temp_dir, 'command.json')
        self._last_command_time: float = 0

    def connect(self):
        """
        Active le pont. Prépare l'environnement de communication.
        """
        print("[PrismBridgeV5] Activation du pont...")
        try:
            os.makedirs(self._temp_dir, exist_ok=True)
            # Effacer tout ancien fichier de commande au démarrage
            if os.path.exists(self.command_file_path):
                os.remove(self.command_file_path)
            self.is_connected = True
            print(f"[PrismBridgeV5] Pont activé. Fichier de commande : {self.command_file_path}")
        except Exception as e:
            print(f"[PrismBridgeV5] Erreur lors de l'activation du pont : {e}")
            self.is_connected = False

    def disconnect(self):
        """
        Désactive le pont.
        """
        print("[PrismBridgeV5] Désactivation du pont.")
        self.is_connected = False

    def send_command(self, command: str, data: Any) -> bool:
        """
        Méthode principale pour envoyer une commande à Talon.

        Args:
            command (str): Le nom de la commande à exécuter (ex: "insert_text").
            data (Any): La charge utile de la commande.

        Returns:
            bool: True si la commande a été envoyée, False sinon.
        """
        if not self.is_connected:
            print("[PrismBridgeV5] Avertissement : Tentative d'envoi de commande alors que le pont est déconnecté.")
            return False

        payload: Dict[str, Any] = {
            "command": command,
            "data": data,
            "timestamp": time.time()
        }

        try:
            with open(self.command_file_path, 'w') as f:
                json.dump(payload, f)
            self._last_command_time = payload["timestamp"]
            return True
        except Exception as e:
            print(f"[PrismBridgeV5] Erreur lors de l'envoi de la commande '{command}': {e}")
            return False

    def send_text(self, text: str) -> bool:
        """
        Raccourci pour envoyer du texte à insérer par Talon.
        Ceci sera l'une des commandes les plus utilisées.
        """
        print(f"[PrismBridgeV5] Envoi du texte : '{text}'")
        return self.send_command("insert_text", text)

    def run_talon_action(self, action_name: str, data: Any = None) -> bool:
        """
        Raccourci pour exécuter une action générique définie dans Talon.
        """
        print(f"[PrismBridgeV5] Demande d'exécution de l'action Talon : '{action_name}'")
        command_data = {"action": action_name, "data": data}
        return self.send_command("run_action", command_data)

if __name__ == '__main__':
    # --- Section de test pour le squelette de la classe ---
    print("--- Test du squelette PrismBridgeV5 ---")

    bridge = PrismBridgeV5()
    
    # Test de connexion
    bridge.connect()
    assert bridge.is_connected

    # Test d'envoi de texte
    print("\nTest 1: Envoi de texte. Vérifiez votre éditeur.")
    input("Appuyez sur Entrée pour continuer...")
    success = bridge.send_text("Le squelette de PrismBridgeV5 est fonctionnel.")
    assert success

    time.sleep(1) # Laisser le temps à Talon de réagir

    # Test d'action générique
    print("\nTest 2: Exécution d'une action générique (notification).")
    input("Appuyez sur Entrée pour continuer...")
    success = bridge.run_talon_action("app.notify", data={"body": "Test depuis PrismBridgeV5", "title": "Test d'Action"})
    assert success

    # Test de déconnexion
    bridge.disconnect()
    assert not bridge.is_connected

    print("\n--- Tests terminés avec succès ---") 