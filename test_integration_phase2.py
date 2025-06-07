#!/usr/bin/env python3
"""
SuperWhisper2 - Test d'Intégration Phase 2.1 + 2.2
System Tray + Overlays + Bridge V4 Integration
"""

import time
import sys
import threading
import subprocess
from pathlib import Path

def test_integration_phase2():
    """Test complet intégration Phase 2"""
    print("🎯 SuperWhisper2 - Test Intégration Phase 2")
    print("=" * 60)
    print("📋 Tests prévus :")
    print("  ✅ System Tray + Service démarrage")
    print("  ✅ Overlays intégration") 
    print("  ✅ Menu contextuel avec overlays toggle")
    print("  ✅ Test transcription avec overlays")
    print("  ✅ Performance et stabilité")
    print()
    
    print("💡 Instructions :")
    print("  1. Le System Tray va se lancer avec icône dans barre des tâches")
    print("  2. Clic droit sur l'icône pour accéder au menu")
    print("  3. Cliquez sur '👁️ Overlays' pour les activer")
    print("  4. Cliquez sur '📋 Test Transcription' pour voir démo")
    print("  5. Observez les overlays pendant la transcription")
    print("  6. Fermez en cliquant '❌ Quitter'")
    print()
    
    print("🚀 Démarrage System Tray intégré...")
    print("⏱️ Attendre 5 secondes pour initialisation complète")
    print()
    
    # Le System Tray est déjà lancé en background
    # Attendre pour laisser le temps de tester
    
    input("📍 Appuyez sur Entrée quand vous avez terminé les tests...")
    
    print()
    print("✅ Test d'intégration Phase 2 terminé !")
    print("📝 Résultats attendus :")
    print("  - System Tray visible et fonctionnel")
    print("  - Menu avec option Overlays")
    print("  - Overlays s'affichent/masquent via menu")
    print("  - Test transcription montre overlays en action")
    print("  - Service Bridge V4 intégré et stable")


def test_manual_overlays():
    """Test manuel overlays séparés"""
    print("\n🔧 Test Overlays Manuel (backup)")
    print("-" * 40)
    
    try:
        # Import et test direct
        sys.path.append(str(Path(__file__).parent / "src"))
        from ui.overlays_simple import SimpleOverlayManager
        
        print("✨ Création Overlay Manager...")
        manager = SimpleOverlayManager()
        
        print("👁️ Affichage overlays...")
        manager.show_all()
        
        print("⏱️ Test 5 secondes...")
        time.sleep(2)
        
        print("📝 Test transcription...")
        manager.start_recording()
        time.sleep(1)
        
        manager.update_transcription("Test manuel", False)
        time.sleep(1)
        
        manager.transcription_complete("Test manuel terminé", 2.0)
        time.sleep(2)
        
        print("🧹 Nettoyage...")
        manager.destroy_all()
        
        print("✅ Test manuel réussi !")
        
    except Exception as e:
        print(f"❌ Erreur test manuel: {e}")


if __name__ == "__main__":
    test_integration_phase2()
    
    # Test backup si nécessaire
    response = input("\n💡 Voulez-vous tester les overlays manuellement? (o/n): ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        test_manual_overlays() 