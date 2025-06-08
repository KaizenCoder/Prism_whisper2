#!/usr/bin/env python3
"""
Test de debug pour identifier le problème d'arrêt automatique
SuperWhisper2 Engine V5 - Test minimal sans GUI
"""

import sys
import os
import time
import threading
import queue

# Ajouter le répertoire src au chemin
src_dir = os.path.join(os.path.dirname(__file__), "src")
if os.path.exists(src_dir):
    sys.path.insert(0, src_dir)

def test_engine_stability():
    """Test de stabilité de l'engine V5"""
    print("[INIT] Test de stabilité Engine V5...")
    
    try:
        from core.whisper_engine_v5 import SuperWhisper2EngineV5
        print("[OK] Import Engine V5 réussi")
        
        # Initialisation engine
        engine = SuperWhisper2EngineV5()
        print("[OK] Engine créé")
        
        # Variables de test
        transcriptions_received = []
        test_active = True
        
        # Callback de test
        def on_transcription_callback(text: str):
            print(f"[CALLBACK] Reçu: '{text}' (len: {len(text) if text else 0})")
            if text and text.strip():
                transcriptions_received.append({
                    'timestamp': time.time(),
                    'text': text.strip()
                })
                print(f"[STAT] Total transcriptions: {len(transcriptions_received)}")
        
        # Configuration callback
        engine.set_transcription_callback(on_transcription_callback)
        print("[OK] Callback configuré")
        
        # Démarrage engine
        print("[FAST] Démarrage engine avec optimisations RTX 3090...")
        success = engine.start_engine()
        
        if not success:
            print("[ERR] Échec démarrage engine")
            return False
            
        # Status engine
        status = engine.get_phase3_status()
        print(f"[OK] Engine démarré avec succès!")
        print(f"[GPU] RTX 3090: {status['gpu_status']['vram_cache_gb']:.1f}GB VRAM")
        print(f"[FAST] {status['optimizations_count']}/{status['total_optimizations']} optimisations actives")
        
        # Configuration microphone par défaut
        try:
            import sounddevice as sd
            default_input = sd.query_devices(kind='input')
            print(f"[MIC] Device par défaut: {default_input['name']}")
            print(f"[MIC] Channels: {default_input['max_input_channels']}")
        except Exception as e:
            print(f"[WARN] Erreur config audio: {e}")
        
        # Test de stabilité - attendre et voir si l'engine reste actif
        print("[TEST] Début du test de stabilité (30 secondes)...")
        print("[TEST] L'engine doit rester actif et capturer l'audio automatiquement")
        print("=" * 60)
        
        start_time = time.time()
        for i in range(30):  # Test de 30 secondes
            elapsed = time.time() - start_time
            
            # Vérifier status engine
            if hasattr(engine, 'streaming_manager') and engine.streaming_manager:
                streaming_active = "ACTIF"
            else:
                streaming_active = "INACTIF"
                
            print(f"[TIME] {elapsed:.1f}s - Streaming: {streaming_active} - Transcriptions: {len(transcriptions_received)}")
            
            # Vérifier les transcriptions récentes
            recent = [t for t in transcriptions_received if time.time() - t['timestamp'] < 5]
            if recent:
                print(f"[ACTIVITY] {len(recent)} transcriptions dans les 5 dernières secondes")
            
            time.sleep(1)
        
        print("=" * 60)
        print(f"[FINAL] Test terminé - Total transcriptions: {len(transcriptions_received)}")
        
        # Afficher les transcriptions
        if transcriptions_received:
            print("[RESULTS] Transcriptions reçues:")
            for i, trans in enumerate(transcriptions_received):
                print(f"  {i+1}. [{trans['timestamp']:.1f}] {trans['text'][:50]}...")
        else:
            print("[WARN] Aucune transcription reçue")
            
        return True
        
    except Exception as e:
        print(f"[ERR] Erreur test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Point d'entrée"""
    print("=" * 60)
    print("SUPERWHISPER2 ENGINE V5 - TEST DE STABILITÉ")
    print("=" * 60)
    
    success = test_engine_stability()
    
    if success:
        print("[OK] Test de stabilité terminé avec succès")
    else:
        print("[ERR] Échec du test de stabilité")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 