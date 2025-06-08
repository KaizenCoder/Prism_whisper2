#!/usr/bin/env python3
"""
Test Simplifié Correction Artefacts SuperWhisper2
Validation VAD + Anti-Hallucination (sans émojis Unicode)
Phase 3 - RTX 3090 Performance + Correction Artefacts
"""

import os
import sys
import time
import logging
from datetime import datetime

# Configuration RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # RTX 3090 24GB
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajouter src au path  
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from core.whisper_engine_v5 import SuperWhisper2EngineV5

class SimpleArtifactTest:
    """Test simplifié de validation des corrections artefacts"""
    
    def __init__(self):
        self.engine = None
        self.transcriptions_received = 0
        self.setup_logging()
        
    def setup_logging(self):
        """Configuration logging simple"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f'artifact_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            ]
        )
        self.logger = logging.getLogger('ArtifactTest')
        
    def test_hallucination_detection(self):
        """Test détection patterns hallucination"""
        self.logger.info("=== TEST DETECTION HALLUCINATIONS ===")
        
        # Créer engine temporaire pour test
        test_engine = SuperWhisper2EngineV5()
        
        # Patterns hallucination identifiés
        hallucination_tests = [
            "Sous-titres réalisés par la communauté d'Amara.org",
            "Merci d'avoir regardé cette vidéo!",
            "N'hésitez pas à vous abonner",
            "Like et abonne-toi",
            "À bientôt pour une nouvelle vidéo"
        ]
        
        # Textes valides
        valid_texts = [
            "Bonjour, ceci est un test de validation.",
            "L'intelligence artificielle transforme notre monde.",
            "SuperWhisper2 fonctionne parfaitement avec RTX 3090.",
            "Je vais maintenant tester la transcription vocale."
        ]
        
        detected_hallucinations = 0
        total_hallucinations = len(hallucination_tests)
        
        self.logger.info(f"Test {total_hallucinations} patterns d'hallucination...")
        for i, pattern in enumerate(hallucination_tests, 1):
            is_hallucination = test_engine._is_hallucination(pattern)
            status = "DETECTE" if is_hallucination else "MANQUE"
            self.logger.info(f"  {i}. {status}: '{pattern[:40]}...'")
            if is_hallucination:
                detected_hallucinations += 1
        
        valid_passed = 0
        total_valid = len(valid_texts)
        
        self.logger.info(f"Test {total_valid} textes valides...")
        for i, text in enumerate(valid_texts, 1):
            is_hallucination = test_engine._is_hallucination(text)
            status = "ACCEPTE" if not is_hallucination else "REJETE"
            self.logger.info(f"  {i}. {status}: '{text[:40]}...'")
            if not is_hallucination:
                valid_passed += 1
        
        # Résultats
        hallucination_rate = (detected_hallucinations / total_hallucinations) * 100
        valid_rate = (valid_passed / total_valid) * 100
        
        self.logger.info("=== RESULTATS DETECTION ===")
        self.logger.info(f"Hallucinations détectées: {detected_hallucinations}/{total_hallucinations} ({hallucination_rate:.1f}%)")
        self.logger.info(f"Textes valides acceptés: {valid_passed}/{total_valid} ({valid_rate:.1f}%)")
        
        success = hallucination_rate >= 80 and valid_rate >= 95
        self.logger.info(f"STATUS FINAL: {'SUCCES' if success else 'ECHEC'}")
        
        return success
    
    def test_vad_integration(self):
        """Test intégration VAD"""
        self.logger.info("=== TEST INTEGRATION VAD ===")
        
        try:
            self.logger.info("Initialisation Engine V5 avec VAD...")
            
            self.engine = SuperWhisper2EngineV5()
            
            # Callback simple pour compter transcriptions
            def on_transcription(text):
                self.transcriptions_received += 1
                self.logger.info(f"Transcription #{self.transcriptions_received}: '{text[:50]}...'")
            
            self.engine.set_transcription_callback(on_transcription)
            
            # Tenter démarrage
            success = self.engine.start_engine()
            
            if success:
                self.logger.info("ENGINE V5 DEMARRE AVEC SUCCES!")
                
                # Vérifier status VAD
                status = self.engine.get_phase3_status()
                opt_count = status['optimizations_count']
                total_opt = status['total_optimizations']
                
                self.logger.info(f"Optimisations actives: {opt_count}/{total_opt}")
                self.logger.info(f"VRAM cache: {status['gpu_status']['vram_cache_gb']:.1f}GB")
                self.logger.info(f"CUDA streams: {status['gpu_status']['cuda_streams']}")
                
                # Test court
                self.logger.info("Test capture audio 10 secondes...")
                self.logger.info("PARLEZ MAINTENANT ou restez silencieux pour tester VAD")
                
                start_time = time.time()
                initial_count = self.transcriptions_received
                
                while time.time() - start_time < 10:
                    time.sleep(1)
                    elapsed = int(time.time() - start_time)
                    if elapsed % 3 == 0:
                        current_count = self.transcriptions_received
                        new_transcriptions = current_count - initial_count
                        self.logger.info(f"[{elapsed}s] Transcriptions reçues: {new_transcriptions}")
                
                final_count = self.transcriptions_received - initial_count
                self.logger.info(f"Total transcriptions en 10s: {final_count}")
                
                self.engine.stop_engine()
                return True
                
            else:
                self.logger.error("ECHEC DEMARRAGE ENGINE V5")
                return False
                
        except Exception as e:
            self.logger.error(f"ERREUR VAD TEST: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_full_test(self):
        """Exécution test complet"""
        self.logger.info("DEBUT TEST CORRECTION ARTEFACTS SUPERWHISPER2")
        self.logger.info("Phase 3 - RTX 3090 + VAD + Anti-Hallucination")
        self.logger.info("=" * 60)
        
        results = {}
        
        try:
            # Test 1: Détection hallucinations
            results['hallucination_detection'] = self.test_hallucination_detection()
            
            print("\n" + "="*50)
            print("ETAPE 1/2 TERMINEE - Appuyez sur ENTREE pour continuer...")
            input()
            
            # Test 2: Intégration VAD
            results['vad_integration'] = self.test_vad_integration()
            
            # Rapport final
            self.logger.info("\n" + "=" * 60)
            self.logger.info("RAPPORT FINAL CORRECTION ARTEFACTS")
            self.logger.info("=" * 60)
            
            all_passed = all(results.values())
            
            for test_name, passed in results.items():
                status = "SUCCES" if passed else "ECHEC"
                self.logger.info(f"{test_name}: {status}")
            
            final_status = "SUCCES COMPLET" if all_passed else "ECHECS DETECTES"
            self.logger.info(f"\nSTATUS FINAL: {final_status}")
            
            if all_passed:
                self.logger.info("RECOMMANDATION: Système anti-artefact OPERATIONNEL")
                self.logger.info("VALIDATION: Prêt déploiement production")
            else:
                self.logger.info("RECOMMANDATION: Ajustements requis avant production")
                
        except KeyboardInterrupt:
            self.logger.info("Test interrompu par utilisateur")
        
        except Exception as e:
            self.logger.error(f"ERREUR GENERALE: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            if self.engine:
                try:
                    self.engine.stop_engine()
                except:
                    pass
            self.logger.info("TEST TERMINE")


def main():
    """Point d'entrée principal"""
    print("Test Correction Artefacts SuperWhisper2")
    print("Phase 3 - RTX 3090 + VAD + Anti-Hallucination")
    print("=" * 50)
    
    test = SimpleArtifactTest()
    test.run_full_test()


if __name__ == "__main__":
    main() 