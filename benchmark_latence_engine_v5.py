"""
Benchmark Latence Engine V5 - Objectif <1.2s
Selon recommandations développeur C pour 30 segments
"""
import time
import statistics
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# Simuler imports Engine V5
# from src.core.whisper_engine_v5 import SuperWhisper2EngineV5

class LatencyBenchmarkV5:
    """
    Benchmark automatisé latence Engine V5
    Objectif développeur C: <1.2s par segment
    """
    
    def __init__(self, engine_v5):
        self.engine = engine_v5
        self.results = []
        self.target_latency = 1.2  # Objectif développeur C
        
    def generate_test_audio(self, duration_s: float, sample_rate: int = 16000) -> np.ndarray:
        """Génère audio test synthétique pour benchmark"""
        samples = int(duration_s * sample_rate)
        
        # Audio synthétique simulant parole (fréquences vocales)
        t = np.linspace(0, duration_s, samples)
        
        # Composantes fréquentielles vocales
        audio = (
            0.3 * np.sin(2 * np.pi * 440 * t) +    # A4 (parole)
            0.2 * np.sin(2 * np.pi * 880 * t) +    # A5 (harmoniques)
            0.1 * np.sin(2 * np.pi * 1320 * t) +   # E6 (consonnes)
            0.05 * np.random.randn(samples)        # Bruit naturel
        )
        
        # Normaliser
        audio = audio / np.max(np.abs(audio)) * 0.7
        
        return audio.astype(np.float32)
    
    def benchmark_single_segment(self, duration_s: float) -> dict:
        """
        Benchmark un segment audio unique
        """
        # Générer audio test
        audio = self.generate_test_audio(duration_s)
        
        # Mesurer latence transcription
        start_time = time.perf_counter()
        
        try:
            # Appel Engine V5 - à adapter selon API réelle
            result = self.engine.transcribe_sync(audio)
            
            end_time = time.perf_counter()
            latency = end_time - start_time
            
            return {
                'duration_s': duration_s,
                'latency_s': latency,
                'ratio': latency / duration_s,
                'text': result.get('text', ''),
                'success': True,
                'real_time_factor': duration_s / latency
            }
            
        except Exception as e:
            end_time = time.perf_counter()
            latency = end_time - start_time
            
            return {
                'duration_s': duration_s,
                'latency_s': latency,
                'ratio': latency / duration_s,
                'text': '',
                'success': False,
                'error': str(e),
                'real_time_factor': 0
            }
    
    def benchmark_30_segments(self) -> dict:
        """
        Benchmark complet 30 segments selon développeur C
        Durées variées pour stress test
        """
        print("🚀 Démarrage benchmark 30 segments...")
        print(f"🎯 Objectif latence: <{self.target_latency}s")
        
        # Durées de test (3 réplications de 10 durées)
        test_durations = [
            # Segments courts
            1.0, 1.5, 2.0, 2.5, 3.0,
            # Segments moyens  
            3.5, 4.0, 4.5, 5.0, 5.5,
        ] * 3  # 30 segments total
        
        results = []
        latencies = []
        
        for i, duration in enumerate(test_durations, 1):
            print(f"📊 Segment {i}/30 ({duration}s)...", end=' ')
            
            result = self.benchmark_single_segment(duration)
            results.append(result)
            
            if result['success']:
                latencies.append(result['latency_s'])
                status = f"✅ {result['latency_s']:.3f}s"
                if result['latency_s'] <= self.target_latency:
                    status += " 🎯"
                else:
                    status += " ⚠️"
            else:
                status = f"❌ {result.get('error', 'Erreur')}"
                
            print(status)
            
            # Petite pause pour éviter overload
            time.sleep(0.1)
        
        # Analyse statistique
        if latencies:
            stats = {
                'total_segments': len(results),
                'successful_segments': len(latencies),
                'failed_segments': len(results) - len(latencies),
                'mean_latency': statistics.mean(latencies),
                'median_latency': statistics.median(latencies),
                'min_latency': min(latencies),
                'max_latency': max(latencies),
                'std_latency': statistics.stdev(latencies) if len(latencies) > 1 else 0,
                'segments_under_target': sum(1 for l in latencies if l <= self.target_latency),
                'success_rate': (len(latencies) / len(results)) * 100,
                'target_achievement_rate': (sum(1 for l in latencies if l <= self.target_latency) / len(latencies)) * 100 if latencies else 0
            }
        else:
            stats = {
                'total_segments': len(results),
                'successful_segments': 0,
                'failed_segments': len(results),
                'mean_latency': 0,
                'success_rate': 0,
                'target_achievement_rate': 0
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'target_latency': self.target_latency,
            'results': results,
            'statistics': stats
        }
    
    def save_results(self, benchmark_data: dict, filename: str = None):
        """Sauvegarder résultats benchmark"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_latence_v5_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(benchmark_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvés: {filename}")
    
    def print_summary(self, benchmark_data: dict):
        """Affiche résumé des résultats"""
        stats = benchmark_data['statistics']
        
        print(f"\n🏆 RÉSUMÉ BENCHMARK LATENCE ENGINE V5")
        print(f"=" * 50)
        print(f"🎯 Objectif: <{self.target_latency}s")
        print(f"📊 Segments testés: {stats['total_segments']}")
        print(f"✅ Segments réussis: {stats['successful_segments']}")
        print(f"💯 Taux de succès: {stats['success_rate']:.1f}%")
        
        if stats['successful_segments'] > 0:
            print(f"\n⏱️ LATENCES:")
            print(f"   Moyenne: {stats['mean_latency']:.3f}s")
            print(f"   Médiane: {stats['median_latency']:.3f}s")
            print(f"   Min: {stats['min_latency']:.3f}s")
            print(f"   Max: {stats['max_latency']:.3f}s")
            print(f"   Écart-type: {stats['std_latency']:.3f}s")
            
            print(f"\n🎯 OBJECTIF <{self.target_latency}s:")
            print(f"   Segments conformes: {stats['segments_under_target']}/{stats['successful_segments']}")
            print(f"   Taux conformité: {stats['target_achievement_rate']:.1f}%")
            
            # Recommandations
            if stats['target_achievement_rate'] >= 90:
                print(f"\n🏆 EXCELLENT! Objectif largement atteint")
            elif stats['target_achievement_rate'] >= 70:
                print(f"\n✅ BON! Objectif majoritairement atteint")
            elif stats['target_achievement_rate'] >= 50:
                print(f"\n⚠️ MOYEN. Optimisations recommandées")
            else:
                print(f"\n❌ INSUFFISANT. Optimisations critiques requises")


def main():
    """Point d'entrée benchmark"""
    print("🔥 BENCHMARK LATENCE ENGINE V5")
    print("Objectif développeur C: <1.2s par segment")
    print("=" * 50)
    
    # TODO: Initialiser Engine V5 réel
    # engine_v5 = SuperWhisper2EngineV5()
    
    # Simuler pour développement
    class MockEngine:
        def transcribe_sync(self, audio):
            # Simuler processing time variable
            processing_time = len(audio) / 16000 * 0.3 + np.random.normal(0.2, 0.1)
            time.sleep(max(0.1, processing_time))
            return {'text': 'Test transcription simulée'}
    
    mock_engine = MockEngine()
    
    # Lancer benchmark
    benchmark = LatencyBenchmarkV5(mock_engine)
    results = benchmark.benchmark_30_segments()
    
    # Afficher et sauver
    benchmark.print_summary(results)
    benchmark.save_results(results)
    
    return results


if __name__ == "__main__":
    main() 