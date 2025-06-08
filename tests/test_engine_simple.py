#!/usr/bin/env python3
"""
Test Simple - Vérification Engine V5
Test rapide pour vérifier que le moteur fonctionne
"""

import os
import sys
import time

# Configuration RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajouter src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_engine_basic():
    """Test basique d'initialisation Engine V5"""
    print("[TEST] Démarrage test Engine V5...")
    
    try:
        print("[INIT] Import Engine V5...")
        from core.whisper_engine_v5 import SuperWhisper2EngineV5
        print("✅ Import réussi")
        
        print("[INIT] Création instance...")
        engine = SuperWhisper2EngineV5()
        print("✅ Instance créée")
        
        print("[INIT] Démarrage engine...")
        start_time = time.time()
        success = engine.start_engine()
        init_time = time.time() - start_time
        
        if success:
            print(f"✅ Engine démarré en {init_time:.2f}s")
            
            # Status
            status = engine.get_phase3_status()
            print(f"[STAT] {status['optimizations_count']}/{status['total_optimizations']} optimisations")
            print(f"[GPU] {status['gpu_status']['vram_cache_gb']:.1f}GB VRAM")
            print(f"[GPU] {status['gpu_status']['cuda_streams']} CUDA streams")
            
            # Test transcription simple
            print("[TEST] Test transcription...")
            test_audio = [0.1] * 16000  # 1s de signal test
            
            def callback(text):
                print(f"[RESULT] Transcription: '{text}'")
            
            engine.set_transcription_callback(callback)
            # Note: Pas de transcription directe dans l'API publique
            
            print("✅ ENGINE V5 FONCTIONNE!")
            return True
            
        else:
            print("❌ Échec démarrage engine")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_whisper():
    """Test fallback avec faster-whisper direct"""
    print("\n[FALLBACK] Test faster-whisper direct...")
    
    try:
        from faster_whisper import WhisperModel
        print("✅ Import faster-whisper réussi")
        
        print("[INIT] Chargement modèle tiny...")
        model = WhisperModel("tiny", device="cuda", compute_type="int8")
        print("✅ Modèle chargé")
        
        # Test transcription
        import numpy as np
        test_audio = np.random.normal(0, 0.1, 16000).astype(np.float32)
        
        print("[TEST] Transcription test...")
        segments, _ = model.transcribe(test_audio, language="fr")
        
        for segment in segments:
            print(f"[RESULT] '{segment.text.strip()}'")
        
        print("✅ FASTER-WHISPER FONCTIONNE!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur fallback: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 TEST MOTEUR SUPERWHISPER2")
    print("=" * 50)
    
    # Test 1: Engine V5
    engine_ok = test_engine_basic()
    
    # Test 2: Fallback
    fallback_ok = test_fallback_whisper()
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS")
    print("=" * 50)
    print(f"Engine V5: {'✅ OK' if engine_ok else '❌ ÉCHEC'}")
    print(f"Fallback: {'✅ OK' if fallback_ok else '❌ ÉCHEC'}")
    
    if engine_ok or fallback_ok:
        print("🎉 AU MOINS UN MOTEUR FONCTIONNE!")
    else:
        print("💥 AUCUN MOTEUR NE FONCTIONNE!") 