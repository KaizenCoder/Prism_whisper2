#!/usr/bin/env python3
"""
Test détection GPU RTX 3090 - Configuration double GPU
Vérifier si CUDA_VISIBLE_DEVICES='1' fonctionne correctement
"""

import os
import sys

# Configuration RTX 3090 (comme dans tous les autres scripts)
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # RTX 3090 24GB
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

def test_gpu_detection():
    """Test détection GPU avec configuration RTX 3090"""
    print("🔍 TEST DÉTECTION GPU RTX 3090")
    print("=" * 40)
    
    # Test PyTorch
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ CUDA disponible: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            compute_cap = torch.cuda.get_device_capability(0)
            
            print(f"🎮 GPU détecté: {gpu_name}")
            print(f"💾 VRAM: {gpu_memory:.1f}GB")
            print(f"🔧 Compute Capability: {compute_cap}")
            
            # Vérifier si c'est RTX 3090
            is_rtx_3090 = "RTX 3090" in gpu_name or gpu_memory >= 20
            print(f"🏆 RTX 3090 détecté: {'✅ OUI' if is_rtx_3090 else '❌ NON'}")
            
            return is_rtx_3090
        else:
            print("❌ CUDA non disponible")
            return False
            
    except ImportError as e:
        print(f"❌ PyTorch non installé: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur PyTorch: {e}")
        return False

def test_faster_whisper():
    """Test faster-whisper avec RTX 3090"""
    print("\n🎤 TEST FASTER-WHISPER RTX 3090")
    print("=" * 40)
    
    try:
        from faster_whisper import WhisperModel
        print("✅ faster-whisper importé")
        
        # Test initialisation GPU
        print("🔄 Test initialisation GPU...")
        model = WhisperModel("tiny", device="cuda", compute_type="int8")
        print("✅ Modèle Whisper GPU initialisé")
        
        # Test transcription rapide
        import numpy as np
        dummy_audio = np.zeros(16000, dtype=np.float32)
        segments, info = model.transcribe(dummy_audio)
        list(segments)  # Force exécution
        
        print("✅ Test transcription réussi")
        print(f"📊 Langue détectée: {info.language}")
        return True
        
    except ImportError as e:
        print(f"❌ faster-whisper non installé: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur faster-whisper: {e}")
        print(f"   Détail: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC COMPLET RTX 3090")
    print("Configuration: CUDA_VISIBLE_DEVICES='1'")
    print()
    
    # Test 1: Détection GPU
    gpu_ok = test_gpu_detection()
    
    # Test 2: faster-whisper si GPU OK
    whisper_ok = False
    if gpu_ok:
        whisper_ok = test_faster_whisper()
    
    # Résumé
    print("\n📋 RÉSUMÉ DIAGNOSTIC")
    print("=" * 40)
    print(f"🎮 GPU RTX 3090: {'✅ OK' if gpu_ok else '❌ ÉCHEC'}")
    print(f"🎤 faster-whisper: {'✅ OK' if whisper_ok else '❌ ÉCHEC'}")
    
    if gpu_ok and whisper_ok:
        print("\n🎉 CONFIGURATION RTX 3090 OPÉRATIONNELLE")
        print("   Interface peut maintenant fonctionner")
    else:
        print("\n🚨 PROBLÈME CONFIGURATION")
        if not gpu_ok:
            print("   - Vérifier installation CUDA/PyTorch")
        if gpu_ok and not whisper_ok:
            print("   - Problème faster-whisper ou CUDA libraries") 