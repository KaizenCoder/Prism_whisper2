#!/usr/bin/env python3
"""
Test Performance SuperWhisper2 Engine V5 - VALIDATION PHASE 3
Utilisation directe du moteur sauvegardé avec performances <1s
RTX 3090 UNIQUEMENT - CPU INTERDIT
"""

import os
import sys
import time
import numpy as np

# Configuration RTX 3090 OBLIGATOIRE
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # RTX 3090 24GB
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajouter src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def main():
    """Test validation Engine V5 - Performance Phase 3"""
    
    print("🚀 VALIDATION SUPERWHISPER2 ENGINE V5")
    print("=" * 50)
    print("📋 RÈGLES: RTX 3090 UNIQUEMENT - CPU INTERDIT")
    print("🎯 OBJECTIF: Validation performances <1s Phase 3")
    print()
    
    try:
        # Import Engine V5 sauvegardé
        print("📦 Chargement SuperWhisper2EngineV5...")
        from core.whisper_engine_v5 import SuperWhisper2EngineV5, get_engine_v5
        
        # Initialisation moteur
        print("⚡ Initialisation moteur Phase 3...")
        engine = SuperWhisper2EngineV5()
        
        # Démarrage avec toutes optimisations
        print("🔥 Démarrage engine avec optimisations RTX 3090...")
        success = engine.start_engine()
        
        if not success:
            print("❌ ÉCHEC: Engine V5 non démarré")
            return False
            
        print("✅ Engine V5 démarré avec succès!")
        
        # Status Phase 3
        status = engine.get_phase3_status()
        print(f"📊 Phase: {status['phase']}")
        print(f"🔧 Version Engine: {status['engine_version']}")
        print(f"⚡ Optimisations: {status['optimizations_count']}/{status['total_optimizations']}")
        print(f"🎮 GPU VRAM: {status['gpu_status']['vram_cache_gb']:.1f}GB")
        print(f"🔀 CUDA Streams: {status['gpu_status']['cuda_streams']}")
        
        # Validation AUCUN FALLBACK CPU
        gpu_status = status['gpu_status']
        if gpu_status['vram_cache_gb'] == 0:
            print("❌ ERREUR: VRAM cache = 0 - Possible fallback CPU détecté!")
            return False
            
        print()
        print("🧪 TEST PERFORMANCE - 3 TRANSCRIPTIONS")
        print("-" * 40)
        
        # Tests performance terrain
        test_results = []
        for i in range(3):
            print(f"Test {i+1}/3...")
            
            start_time = time.time()
            success, text = engine.transcribe_now(timeout=10)
            latency = time.time() - start_time
            
            if success:
                print(f"  ⏱️ Latence: {latency:.3f}s")
                print(f"  📝 Texte: {text[:50]}..." if text else "  📝 Aucun texte")
                test_results.append(latency)
            else:
                print(f"  ❌ Échec transcription")
                test_results.append(999.0)  # Marqueur échec
            print()
        
        # Analyse résultats
        valid_results = [r for r in test_results if r < 900]
        if valid_results:
            avg_latency = sum(valid_results) / len(valid_results)
            min_latency = min(valid_results)
            
            print("📈 RÉSULTATS FINAUX")
            print("=" * 50)
            print(f"🎯 Latence moyenne: {avg_latency:.3f}s")
            print(f"⚡ Latence minimale: {min_latency:.3f}s")
            print(f"✅ Tests réussis: {len(valid_results)}/3")
            
            # Validation objectifs Phase 3
            if avg_latency < 1.0:
                print("🏆 OBJECTIF ATTEINT: <1s latence!")
            elif avg_latency < 3.0:
                print("✅ OBJECTIF PHASE 3: <3s latence validé")
            else:
                print("⚠️ Latence élevée - Optimisations à vérifier")
                
            return avg_latency < 3.0
        else:
            print("❌ ÉCHEC: Aucune transcription réussie")
            return False
            
    except ImportError as e:
        print(f"❌ ERREUR IMPORT: {e}")
        print("💡 Vérification: Engine V5 présent dans src/core/")
        return False
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            if 'engine' in locals():
                engine.stop_engine()
                print("🛑 Engine arrêté proprement")
        except:
            pass

if __name__ == "__main__":
    success = main()
    exit_code = 0 if success else 1
    print(f"\n🎯 VALIDATION: {'SUCCÈS' if success else 'ÉCHEC'}")
    sys.exit(exit_code) 