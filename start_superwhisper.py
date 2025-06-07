#!/usr/bin/env python3
"""
SuperWhisper2 - Lanceur principal
Script de démarrage rapide pour l'interface System Tray Phase 2.1
"""

import os
import sys
from pathlib import Path

def main():
    """Démarrer SuperWhisper2 avec interface System Tray"""
    
    print("🚀 SuperWhisper2 - Démarrage...")
    print("=" * 50)
    print("Phase 2.1: Interface System Tray")
    print("Features: Icône animée, menu contextuel, notifications")
    print("=" * 50)
    
    # Vérifier environnement
    project_root = Path(__file__).parent
    ui_module = project_root / "src" / "ui" / "system_tray.py"
    
    if not ui_module.exists():
        print("❌ Module System Tray introuvable!")
        input("Appuyez sur Entrée pour fermer...")
        return
    
    # Ajouter src au path
    sys.path.insert(0, str(project_root / "src"))
    
    try:
        # Importer et lancer System Tray
        from ui.system_tray import SuperWhisperSystemTray
        
        print("🎯 Lancement interface System Tray...")
        print("💡 Cherchez l'icône SuperWhisper2 dans la barre des tâches")
        print("🖱️ Clic droit sur l'icône pour accéder au menu")
        print("⌨️ Utilisez Win+Alt+V pour transcrire une fois le service démarré")
        print("-" * 50)
        
        # Créer et démarrer
        tray = SuperWhisperSystemTray()
        tray.start_tray()
        
    except KeyboardInterrupt:
        print("\n👋 Application fermée par utilisateur")
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        print("💡 Vérifiez que les dépendances sont installées:")
        print("   pip install pystray plyer pywin32")
        input("Appuyez sur Entrée pour fermer...")
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        input("Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main() 