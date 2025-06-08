# Configuration de l'Environnement - Phase 4 : Projet Prometheus

Ce document décrit la configuration nécessaire pour faire fonctionner l'intégration entre **SuperWhisper V5** et **Talon Voice**.

## 1. Vue d'ensemble de l'Architecture

L'architecture repose sur deux applications distinctes qui communiquent via un pont simple basé sur le système de fichiers :

- **SuperWhisper V5 :** Capture l'audio, le transcrit en texte ultra-rapidement.
- **Talon Voice :** Reçoit le texte transcrit et l'exécute comme une commande via son puissant écosystème.
- **PrismBridge (le pont) :** Un script Talon (`prism_bridge_poc.py`) surveille un fichier (`command.json`) pour recevoir des instructions de SuperWhisper.

## 2. Prérequis Logiciels

### 2.1. Talon Voice

1.  **Installation :** Téléchargez et installez Talon depuis le [site officiel](https://talonvoice.com/).
2.  **Lancement initial :** Lancez Talon au moins une fois pour qu'il crée son répertoire de configuration (`%APPDATA%/Talon` sur Windows).
3.  **Commandes communautaires (knausj) :** Il est fortement recommandé d'installer le jeu de commandes de la communauté, car il fournit des actions de base essentielles (`actions.insert`, `actions.key`, etc.).
    - Ouvrez un terminal Git et exécutez la commande suivante :
      ```bash
      git clone https://github.com/knausj/knausj_talon.git "%APPDATA%/Talon/user/knausj_talon"
      ```
    - Relancez Talon. Il chargera automatiquement ce nouvel ensemble de scripts.

### 2.2. SuperWhisper2

1.  **Dépôt Git :** Assurez-vous d'avoir cloné le dépôt SuperWhisper2 et d'être sur la branche principale.
2.  **Dépendances Python :** Installez les dépendances nécessaires à l'aide de `pip` et du fichier `pyproject.toml` (ou `requirements.txt` si généré).
    ```bash
    pip install -e .
    ```

## 3. Configuration du Pont (PrismBridge)

Le pont est un simple script Python qui doit être placé dans le répertoire utilisateur de Talon pour être chargé au démarrage.

1.  **Copier le script du pont :**
    Le script de preuve de concept, `prism_bridge_poc.py`, qui gère la communication, se trouve dans `src/proof_of_concepts/`. Il doit être copié (ou un lien symbolique doit être créé) dans le dossier utilisateur de Talon.

    - **Source :** `[Chemin de votre projet Superwhisper2]/src/proof_of_concepts/prism_bridge_poc.py`
    - **Destination :** `%APPDATA%/Talon/user/prism_bridge.py` (renommé pour la clarté).

2.  **Comprendre le mécanisme de communication :**
    - SuperWhisper écrit des commandes dans un fichier JSON situé ici :
      `%LOCALAPPDATA%/Temp/superwhisper_talon_bridge/command.json`.
    - Le script `prism_bridge.py` dans Talon détecte les modifications de ce fichier, lit la commande et l'exécute.
    - Ce mécanisme ne nécessite aucune configuration réseau et est intrinsèquement simple et robuste.

## 4. Procédure de Lancement et de Vérification

Pour que le système fonctionne correctement, suivez cet ordre :

1.  **Lancez Talon Voice.**
2.  **Vérifiez les logs de Talon :**
    - Accédez au menu de Talon dans la barre système (System Tray).
    - Cliquez sur `Scripting -> View Log`.
    - Vous devriez voir des lignes confirmant le chargement des scripts, y compris une ligne indiquant la surveillance du fichier de commandes :
      `[PrismBridge] Watching for commands in: C:\Users\[VotreNom]\AppData\Local\Temp\superwhisper_talon_bridge\command.json`
3.  **Lancez SuperWhisper V5** (ou un script de test comme `talon_rpc_poc.py`).
4.  **Testez la connexion :**
    - Exécutez le script `talon_rpc_poc.py` depuis le projet SuperWhisper :
      ```bash
      python src/proof_of_concepts/talon_rpc_poc.py
      ```
    - Suivez les instructions et vérifiez que le texte est bien inséré dans l'application active et que les notifications apparaissent. Si c'est le cas, le pont est fonctionnel. 