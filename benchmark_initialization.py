#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark d'initialisation Engine V5 - Modèle Medium FP16
Test précis du temps de chargement sur RTX 3090
"""

import time
import sys
import os
from pathlib import Path

def benchmark_engine_v5_initialization():
    """Mesure précise du temps d'initialisation Engine V5"""
    
    print(f"🚀 BENCHMARK INITIALISATION ENGINE V5")
    print(f"=" * 60)
    print(f"GPU: RTX 3090 24GB")
    print(f"Modèle: Whisper Medium FP16")
    print(f"Quantification: INT8")
    print(f"=" * 60)
    
    # Phase 1: Import SuperWhisper2
    print(f"\n⏱️  PHASE 1: Import SuperWhisper2...")
    start_import = time.time()
    
    try:
        sys.path.append(str(Path(__file__).parent / "src"))
        from core.whisper_engine_v5 import SuperWhisper2EngineV5
        
        import_time = time.time() - start_import
        print(f"✅ Import terminé: {import_time:.2f}s")
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return None
    
    # Phase 2: Création instance Engine
    print(f"\n⏱️  PHASE 2: Création instance Engine V5...")
    start_instance = time.time()
    
    try:
        engine = SuperWhisper2EngineV5()
        instance_time = time.time() - start_instance
        print(f"✅ Instance créée: {instance_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Erreur création instance: {e}")
        return None
    
    # Phase 3: Initialisation Phase 3 (chargement modèle)
    print(f"\n⏱️  PHASE 3: Initialisation Phase 3 (Modèle Medium FP16)...")
    start_init = time.time()
    
    try:
        result = engine.start_engine()
        
        init_time = time.time() - start_init
        print(f"✅ Phase 3 initialisée: {init_time:.2f}s")
        print(f"📊 Résultat: {result}")
        
    except Exception as e:
        print(f"❌ Erreur initialisation Phase 3: {e}")
        return None
    
    # Calcul temps total
    total_time = import_time + instance_time + init_time
    
    print(f"\n" + "=" * 60)
    print(f"📊 RÉSULTATS BENCHMARK")
    print(f"=" * 60)
    print(f"⏱️  Import SuperWhisper2:     {import_time:.2f}s")
    print(f"⏱️  Création instance:       {instance_time:.2f}s")
    print(f"⏱️  Chargement Medium FP16:  {init_time:.2f}s")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"⏱️  TEMPS TOTAL:             {total_time:.2f}s")
    print(f"=" * 60)
    
    # Benchmarks de référence
    print(f"\n📈 BENCHMARKS DE RÉFÉRENCE")
    print(f"─────────────────────────────────────")
    if init_time < 10:
        perf = "🚀 EXCELLENT"
    elif init_time < 20:
        perf = "✅ BON"
    elif init_time < 30:
        perf = "⚠️  ACCEPTABLE"
    else:
        perf = "❌ LENT"
    
    print(f"Performance: {perf}")
    print(f"Référence RTX 3090: ~15-25s attendu")
    
    # Nettoyage
    try:
        if hasattr(engine, 'stop_engine'):
            engine.stop_engine()
        print(f"\n🧹 Nettoyage terminé")
    except:
        pass
    
    return {
        'import_time': import_time,
        'instance_time': instance_time,
        'init_time': init_time,
        'total_time': total_time,
        'performance': perf
    }

if __name__ == "__main__":
    print(f"🎯 Benchmark Initialisation Engine V5 - Medium FP16")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        results = benchmark_engine_v5_initialization()
        if results:
            print(f"\n✅ Benchmark terminé avec succès!")
        else:
            print(f"\n❌ Benchmark échoué")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Benchmark interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur benchmark: {e}") 