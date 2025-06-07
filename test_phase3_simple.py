#!/usr/bin/env python3
"""
Test Phase 3 Simplifié - SuperWhisper2 Engine V5
Test infrastructure Phase 3 sans dépendances audio complexes
Focus: INT8 Quantification + GPU RTX 3090 + Infrastructure V5
"""

import os
import sys
import time
import logging
from datetime import datetime

# Forcer utilisation RTX 3090 24GB (GPU 1)
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Test imports Phase 3
try:
    import torch
    import torch.cuda
    from faster_whisper import WhisperModel
    import transformers
    import accelerate
    import optimum
    
    PHASE3_DEPS_OK = True
    print("✅ Dépendances Phase 3 installées:")
    print(f"   - torch: {torch.__version__}")
    print(f"   - transformers: {transformers.__version__}")
    print(f"   - CUDA disponible: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"   - GPU: {gpu_name} ({gpu_memory:.1f}GB)")
    
except ImportError as e:
    PHASE3_DEPS_OK = False
    print(f"❌ Dépendances Phase 3 manquantes: {e}")


class SimpleModelOptimizer:
    """
    Version simplifiée de ModelOptimizer pour test infrastructure
    """
    
    def __init__(self, logger):
        self.logger = logger
        self.int8_model = None
        self.fp16_model = None
        self.quantization_enabled = False
        
    def test_int8_quantification(self):
        """
        Test simplifié INT8 quantification
        """
        try:
            self.logger.info("🔧 Test quantification INT8...")
            
            if not torch.cuda.is_available():
                self.logger.error("❌ CUDA non disponible")
                return False
            
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            self.logger.info(f"🎮 GPU VRAM: {gpu_memory:.1f}GB")
            
            # Test création modèle Whisper
            self.logger.info("📦 Chargement modèle Whisper medium...")
            
            # Modèle FP16 d'abord
            start_time = time.time()
            self.fp16_model = WhisperModel(
                "medium",
                device="cuda", 
                compute_type="float16"
            )
            fp16_load_time = time.time() - start_time
            self.logger.info(f"✅ Modèle FP16 chargé en {fp16_load_time:.1f}s")
            
            # Test INT8 si GPU suffisant
            if gpu_memory >= 8:  # Minimum 8GB pour INT8
                start_time = time.time()
                self.int8_model = WhisperModel(
                    "medium",
                    device="cuda",
                    compute_type="int8"
                )
                int8_load_time = time.time() - start_time
                self.logger.info(f"✅ Modèle INT8 chargé en {int8_load_time:.1f}s")
                
                self.quantization_enabled = True
                return True
            else:
                self.logger.warning(f"⚠️ GPU {gpu_memory:.1f}GB insuffisant pour INT8")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur test INT8: {e}")
            return False


class SimplePhase3Engine:
    """
    Version simplifiée de SuperWhisper2EngineV5 pour test infrastructure
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.model_optimizer = None
        self.phase3_optimizations = {
            'int8_quantization': False,
            'gpu_memory_available': False,
            'cuda_streams': False,
            'vram_cache': False
        }
        
    def _setup_logging(self):
        """Setup logging"""
        logger = logging.getLogger('SimplePhase3Engine')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - ENGINE - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def test_phase3_infrastructure(self):
        """
        Test infrastructure Phase 3 complète
        """
        self.logger.info("🚀 DÉBUT TEST INFRASTRUCTURE PHASE 3")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_success': False
        }
        
        # Test 1: GPU et CUDA
        gpu_test = self._test_gpu_infrastructure()
        results['tests']['gpu_infrastructure'] = gpu_test
        self.phase3_optimizations['gpu_memory_available'] = gpu_test['success']
        
        # Test 2: Model Optimizer
        if gpu_test['success']:
            model_test = self._test_model_optimizer()
            results['tests']['model_optimizer'] = model_test
            self.phase3_optimizations['int8_quantization'] = model_test['success']
        
        # Test 3: CUDA Streams
        if gpu_test['success']:
            streams_test = self._test_cuda_streams()
            results['tests']['cuda_streams'] = streams_test
            self.phase3_optimizations['cuda_streams'] = streams_test['success']
        
        # Test 4: VRAM Cache simulation
        if gpu_test['success']:
            cache_test = self._test_vram_cache()
            results['tests']['vram_cache'] = cache_test
            self.phase3_optimizations['vram_cache'] = cache_test['success']
        
        # Évaluation globale
        successful_tests = sum(1 for test in results['tests'].values() if test['success'])
        total_tests = len(results['tests'])
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        results['overall_success'] = success_rate >= 0.75  # 75% tests réussis
        results['success_rate'] = success_rate
        results['optimizations'] = self.phase3_optimizations
        
        # Log résumé
        status_emoji = "✅" if results['overall_success'] else "❌"
        self.logger.info(f"{status_emoji} INFRASTRUCTURE PHASE 3: {successful_tests}/{total_tests} tests réussis ({success_rate:.1%})")
        
        return results
    
    def _test_gpu_infrastructure(self):
        """Test infrastructure GPU RTX 3090"""
        test = {
            'name': 'GPU Infrastructure',
            'success': False,
            'details': {}
        }
        
        try:
            self.logger.info("🎮 Test infrastructure GPU...")
            
            if not torch.cuda.is_available():
                test['details']['error'] = "CUDA non disponible"
                return test
            
            # Infos GPU
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            
            test['details'].update({
                'gpu_name': gpu_name,
                'gpu_memory_gb': gpu_memory,
                'cuda_version': torch.version.cuda
            })
            
            # Vérifications
            is_rtx_3090 = "RTX 3090" in gpu_name or gpu_memory >= 20  # RTX 3090 24GB
            has_sufficient_memory = gpu_memory >= 8  # Minimum 8GB
            
            if has_sufficient_memory:
                test['success'] = True
                if is_rtx_3090 or gpu_memory >= 20:
                    self.logger.info(f"🏆 RTX 3090 24GB détecté: {gpu_name} ({gpu_memory:.1f}GB)")
                    self.logger.info("💎 GPU optimal pour Phase 3 - Tous avantages RTX 3090 activés")
                else:
                    self.logger.info(f"✅ GPU compatible: {gpu_name} ({gpu_memory:.1f}GB)")
            else:
                test['details']['error'] = f"GPU {gpu_memory:.1f}GB insuffisant (minimum 8GB)"
                
        except Exception as e:
            test['details']['error'] = str(e)
            self.logger.error(f"❌ Test GPU error: {e}")
        
        return test
    
    def _test_model_optimizer(self):
        """Test ModelOptimizer et INT8"""
        test = {
            'name': 'Model Optimizer INT8',
            'success': False,
            'details': {}
        }
        
        try:
            self.logger.info("⚡ Test Model Optimizer...")
            
            self.model_optimizer = SimpleModelOptimizer(self.logger)
            success = self.model_optimizer.test_int8_quantification()
            
            test['success'] = success
            test['details'] = {
                'int8_enabled': self.model_optimizer.quantization_enabled,
                'fp16_model_loaded': self.model_optimizer.fp16_model is not None,
                'int8_model_loaded': self.model_optimizer.int8_model is not None
            }
            
        except Exception as e:
            test['details']['error'] = str(e)
            self.logger.error(f"❌ Test Model Optimizer error: {e}")
        
        return test
    
    def _test_cuda_streams(self):
        """Test création CUDA streams"""
        test = {
            'name': 'CUDA Streams',
            'success': False,
            'details': {}
        }
        
        try:
            self.logger.info("🌊 Test CUDA Streams...")
            
            # Créer 4 streams test
            streams = []
            for i in range(4):
                stream = torch.cuda.Stream(device=0)
                streams.append(stream)
            
            test['success'] = len(streams) == 4
            test['details'] = {
                'streams_created': len(streams),
                'target_streams': 4
            }
            
            self.logger.info(f"✅ {len(streams)} CUDA streams créés")
            
        except Exception as e:
            test['details']['error'] = str(e)
            self.logger.error(f"❌ Test CUDA Streams error: {e}")
        
        return test
    
    def _test_vram_cache(self):
        """Test allocation cache VRAM"""
        test = {
            'name': 'VRAM Cache 24GB',
            'success': False,
            'details': {}
        }
        
        try:
            self.logger.info("💾 Test VRAM Cache...")
            
            # Nettoyer cache
            torch.cuda.empty_cache()
            initial_memory = torch.cuda.memory_allocated(0) / 1024**3
            
            # Allouer cache test (1GB)
            cache_tensors = []
            cache_size_gb = 4.0 if gpu_memory >= 20 else 1.0  # 4GB cache si RTX 3090 24GB
            tensor_size = int((cache_size_gb * 1024**3) / (4 * 10))  # 10 tensors float32
            
            for i in range(10):
                tensor = torch.zeros(tensor_size // 4, dtype=torch.float32, device='cuda')
                cache_tensors.append(tensor)
            
            final_memory = torch.cuda.memory_allocated(0) / 1024**3
            allocated_gb = final_memory - initial_memory
            
            test['success'] = allocated_gb >= (2.0 if cache_size_gb >= 4.0 else 0.5)  # Critère adaptatif RTX 3090
            test['details'] = {
                'initial_memory_gb': initial_memory,
                'final_memory_gb': final_memory,
                'allocated_gb': allocated_gb,
                'cache_tensors': len(cache_tensors)
            }
            
            self.logger.info(f"✅ Cache VRAM: {allocated_gb:.1f}GB alloué")
            
            # Cleanup
            del cache_tensors
            torch.cuda.empty_cache()
            
        except Exception as e:
            test['details']['error'] = str(e)
            self.logger.error(f"❌ Test VRAM Cache error: {e}")
        
        return test


def main():
    """
    Test principal infrastructure Phase 3
    """
    print("🚀 SuperWhisper2 Phase 3 - Test Infrastructure Simplifié")
    print("🎯 Validation: INT8 + GPU RTX 3090 + CUDA Streams + VRAM Cache")
    print()
    
    if not PHASE3_DEPS_OK:
        print("❌ Dépendances Phase 3 manquantes")
        return
    
    # Créer engine test
    engine = SimplePhase3Engine()
    
    # Test infrastructure complète
    results = engine.test_phase3_infrastructure()
    
    # Afficher résultats
    print("\n📊 RÉSULTATS TESTS PHASE 3:")
    print(f"   Succès global: {'✅' if results['overall_success'] else '❌'}")
    print(f"   Taux réussite: {results['success_rate']:.1%}")
    print()
    
    for test_name, test_result in results['tests'].items():
        status = "✅" if test_result['success'] else "❌"
        print(f"   {status} {test_result['name']}")
        
        if 'error' in test_result['details']:
            print(f"      ❌ Erreur: {test_result['details']['error']}")
    
    print("\n🎯 OPTIMISATIONS PHASE 3:")
    for opt_name, enabled in results['optimizations'].items():
        status = "✅" if enabled else "❌"
        print(f"   {status} {opt_name}")
    
    # Recommandation
    if results['overall_success']:
        print("\n🚀 RECOMMANDATION: Phase 3 peut continuer")
        print("   Infrastructure Phase 3 validée ✅")
        print("   Prêt pour implémentation optimisations avancées")
    else:
        print("\n⚠️ RECOMMANDATION: Corriger infrastructure")
        print("   Résoudre erreurs avant optimisations avancées")


if __name__ == "__main__":
    main() 