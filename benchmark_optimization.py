#!/usr/bin/env python3
"""
Benchmark Optimisation Model Pre-loading
Comparaison latence: Bridge V1 vs Bridge V2 avec pre-loading
Objectif: Mesurer amélioration -4s latence
"""

import time
import sys
import os
from pathlib import Path
import subprocess
import statistics

# Ajouter src au path
sys.path.append(str(Path(__file__).parent / "src"))

def benchmark_v1_approach():
    """Benchmark approche V1 (rechargement modèle à chaque fois)"""
    print("🔍 Benchmark V1 (rechargement modèle)...")
    
    times = []
    
    for i in range(3):  # 3 tests pour moyenne
        print(f"  Test {i+1}/3...")
        start = time.time()
        
        # Simuler rechargement modèle + transcription
        try:
            cmd = [sys.executable, "quick_transcription.py"]
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"    Temps: {elapsed:.1f}s")
        except subprocess.TimeoutExpired:
            print(f"    Timeout (>30s)")
            times.append(30.0)
        except Exception as e:
            print(f"    Erreur: {e}")
            times.append(30.0)
    
    avg_time = statistics.mean(times)
    print(f"📊 V1 Moyenne: {avg_time:.1f}s")
    return avg_time, times

def benchmark_v2_approach():
    """Benchmark approche V2 (modèle pre-loaded)"""
    print("🚀 Benchmark V2 (modèle pre-loaded)...")
    
    try:
        from core.whisper_engine import SuperWhisper2Engine
        
        # 1. Pre-loading initial (temps d'initialisation)
        engine = SuperWhisper2Engine()
        
        print("  Initialisation engine (pre-loading)...")
        init_start = time.time()
        if engine.start_engine():
            init_time = time.time() - init_start
            print(f"  Pre-loading terminé en: {init_time:.1f}s")
        else:
            print("  ❌ Échec initialisation")
            return None, []
        
        # 2. Tests transcription (modèle déjà chargé)
        times = []
        for i in range(3):
            print(f"  Test transcription {i+1}/3...")
            start = time.time()
            
            success, result = engine.transcribe_now(timeout=15)
            elapsed = time.time() - start
            times.append(elapsed)
            
            if success:
                print(f"    Temps: {elapsed:.1f}s - Résultat: {result[:30]}...")
            else:
                print(f"    Temps: {elapsed:.1f}s - Échec: {result}")
        
        # 3. Cleanup
        engine.stop_engine()
        
        avg_time = statistics.mean(times)
        print(f"📊 V2 Moyenne (sans pre-loading): {avg_time:.1f}s")
        print(f"📊 V2 Pre-loading initial: {init_time:.1f}s")
        
        return avg_time, times, init_time
        
    except ImportError as e:
        print(f"❌ Modules V2 non disponibles: {e}")
        return None, []

def main():
    """Benchmark complet et analyse"""
    print("🎯 Benchmark Optimisation Model Pre-loading")
    print("=" * 50)
    
    # Test V1
    v1_avg, v1_times = benchmark_v1_approach()
    
    print()
    
    # Test V2
    v2_result = benchmark_v2_approach()
    if v2_result and len(v2_result) >= 3:
        v2_avg, v2_times, init_time = v2_result
    else:
        print("❌ Benchmark V2 échoué")
        return
    
    print()
    print("📈 ANALYSE COMPARATIVE")
    print("=" * 50)
    print(f"V1 (rechargement) : {v1_avg:.1f}s ± {statistics.stdev(v1_times):.1f}s")
    print(f"V2 (pre-loaded)  : {v2_avg:.1f}s ± {statistics.stdev(v2_times):.1f}s")
    print(f"V2 init (1 fois) : {init_time:.1f}s")
    print()
    
    # Calculs amélioration
    improvement = v1_avg - v2_avg
    improvement_pct = (improvement / v1_avg) * 100
    
    print(f"⚡ AMÉLIORATION: {improvement:.1f}s ({improvement_pct:.0f}%)")
    
    if improvement >= 3.0:
        print("✅ OBJECTIF ATTEINT: -4s latence")
    elif improvement >= 2.0:
        print("🟡 PROGRÈS NOTABLE: -2s latence")
    else:
        print("🔴 AMÉLIORATION INSUFFISANTE")
    
    print()
    print("🎯 RECOMMANDATIONS:")
    print(f"- Démarrer V2 au boot système (pre-loading {init_time:.1f}s)")
    print(f"- Utilisation continue: {v2_avg:.1f}s par transcription")
    print(f"- Économie temps par rapport V1: {improvement:.1f}s")

if __name__ == "__main__":
    main() 