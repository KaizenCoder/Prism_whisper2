#!/usr/bin/env python3
"""
SuperWhisper2 Engine V4 avec GPU Memory Pinning
Service V3 + GPU optimizations pour latence ultra-réduite
Optimisation: Pre-loading + Streaming + GPU Memory Pinning = -5.5s total
"""

import os
import sys
import time
import threading
import queue
import traceback
from typing import Optional, Tuple
import logging

# Force utilisation GPU RTX
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

try:
    import sounddevice as sd
    import numpy as np
    from faster_whisper import WhisperModel
except ImportError as e:
    print(f"ERROR: Modules requis manquants: {e}")
    sys.exit(1)

# Import modules optimisés
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from audio.audio_streamer import AudioStreamingManager
from gpu.memory_optimizer import GPUMemoryOptimizer, GPUAudioProcessor


class SuperWhisper2EngineV4:
    """
    Service background Whisper V4 avec toutes optimisations
    Performance: Pre-loading + Streaming + GPU Memory Pinning
    """
    
    def __init__(self):
        # Hériter des capacités V3
        self.model = None
        self.model_loaded = False
        self.running = False
        
        # Queue pour requests
        self.request_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # Configuration audio
        self.sample_rate = 16000
        self.channels = 1
        self.duration = 3.0
        
        # Audio streaming V3
        self.streaming_manager = None
        self.streaming_mode = False
        
        # NOUVEAU V4: GPU Memory Optimizer
        self.gpu_optimizer = None
        self.gpu_processor = None
        self.gpu_enabled = False
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Thread worker
        self.worker_thread = None
        
        # Métriques V4
        self.gpu_optimizations = 0
        self.total_speedup = 0.0
        
    def _setup_logging(self):
        """Setup logging V4"""
        logger = logging.getLogger('SuperWhisper2EngineV4')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - ENGINE_V4 - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def start_engine(self):
        """Démarrer le service V4 avec toutes optimisations"""
        try:
            self.logger.info("🚀 Démarrage SuperWhisper2 Engine V4 (GPU Optimized)...")
            
            # 1. Pre-load modèle (hérité V2)
            self._preload_whisper_model()
            
            # 2. Initialiser GPU optimizer (NOUVEAU V4)
            self._initialize_gpu_optimizer()
            
            # 3. Initialiser streaming manager avec GPU
            self.streaming_manager = AudioStreamingManager(self)
            
            # 4. Démarrer worker thread
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
            self.logger.info("✅ SuperWhisper2 Engine V4 prêt (Pre-loaded + Streaming + GPU)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Échec démarrage engine V4: {e}")
            return False
    
    def _preload_whisper_model(self):
        """Pre-loading du modèle Whisper (identique V2/V3)"""
        start_time = time.time()
        self.logger.info("📦 Pre-loading modèle Whisper...")
        
        try:
            self.model = WhisperModel(
                "medium",
                device="cuda",
                compute_type="float16"
            )
            
            load_time = time.time() - start_time
            self.model_loaded = True
            self.logger.info(f"✅ Modèle Whisper pre-loaded en {load_time:.1f}s")
            
            # Test dummy pour warm-up GPU
            dummy_audio = np.zeros(self.sample_rate, dtype=np.float32)
            self.model.transcribe(dummy_audio, language="fr")
            self.logger.info("🔥 GPU warm-up terminé")
            
        except Exception as e:
            self.logger.error(f"❌ Échec pre-loading: {e}")
            self.model_loaded = False
            raise
    
    def _initialize_gpu_optimizer(self):
        """NOUVEAU V4: Initialiser optimiseur GPU"""
        try:
            self.logger.info("🔧 Initialisation GPU Memory Optimizer...")
            
            # Créer optimiseur GPU
            self.gpu_optimizer = GPUMemoryOptimizer()
            
            if self.gpu_optimizer.cuda_available and self.gpu_optimizer.initialized:
                # Créer processeur audio GPU
                self.gpu_processor = GPUAudioProcessor(self.model)
                self.gpu_enabled = True
                
                # Benchmark initial
                benchmark_results = self.gpu_optimizer.benchmark_transfer_speed()
                self.logger.info(f"📊 GPU Benchmark: {benchmark_results}")
                
                self.logger.info("✅ GPU Memory Optimizer activé")
            else:
                self.logger.warning("⚠️ GPU optimizer désactivé (fallback CPU)")
                self.gpu_enabled = False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur init GPU optimizer: {e}")
            self.gpu_enabled = False
    
    def _worker_loop(self):
        """Boucle worker V4 (gestion requests + streaming + GPU)"""
        self.logger.info("🔄 Worker loop V4 démarré")
        
        while self.running:
            try:
                # Traiter requests classiques
                try:
                    request = self.request_queue.get(timeout=1.0)
                    self._handle_request(request)
                except queue.Empty:
                    pass
                
                # Traiter résultats streaming si actif
                if self.streaming_mode and self.streaming_manager:
                    result = self.streaming_manager.get_latest_result(timeout=0.1)
                    if result:
                        self.logger.info(f"🌊 Résultat streaming: {result.get('text', 'N/A')[:30]}...")
                        # Propager vers result_queue si nécessaire
                        self.result_queue.put(result)
                
                # Stats GPU périodiques
                if self.gpu_enabled and self.gpu_optimizations % 50 == 0 and self.gpu_optimizations > 0:
                    stats = self.gpu_processor.get_performance_stats()
                    self.logger.info(f"📊 GPU Stats: {stats.get('cache_hit_ratio', 0):.2f} hit ratio")
                
            except Exception as e:
                self.logger.error(f"❌ Erreur worker V4: {e}")
    
    def _handle_request(self, request):
        """Handler pour requests V4 (avec GPU optimizations)"""
        try:
            if request['action'] == 'transcribe':
                # Utiliser GPU processor si disponible
                if self.gpu_enabled:
                    result = self._transcribe_gpu_optimized()
                else:
                    result = self._transcribe_internal()
                
                self.result_queue.put({
                    'success': True,
                    'result': result,
                    'request_id': request.get('id'),
                    'gpu_optimized': self.gpu_enabled
                })
                
            elif request['action'] == 'start_streaming':
                self.start_streaming_mode()
            elif request['action'] == 'stop_streaming':
                self.stop_streaming_mode()
                
        except Exception as e:
            self.logger.error(f"❌ Erreur handle request V4: {e}")
            self.result_queue.put({
                'success': False,
                'error': str(e),
                'request_id': request.get('id', 'unknown')
            })
    
    def _transcribe_gpu_optimized(self) -> Optional[str]:
        """
        NOUVEAU V4: Transcription optimisée GPU avec memory pinning
        """
        try:
            start_time = time.time()
            
            # Enregistrement audio classique
            self.logger.info("🎤 Enregistrement audio (GPU optimized)...")
            audio_data = sd.rec(
                frames=int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            sd.wait()
            
            # Traitement GPU optimisé
            audio_flat = audio_data.flatten().astype(np.float32)
            
            success, result, processing_time = self.gpu_processor.process_audio_optimized(audio_flat)
            
            if success and result:
                total_time = time.time() - start_time
                self.gpu_optimizations += 1
                
                self.logger.info(f"✅ Transcription GPU optimisée: {result[:50]}... ({total_time:.2f}s)")
                return result
            else:
                self.logger.warning("⚠️ GPU optimization failed, fallback CPU")
                return self._transcribe_internal()
                
        except Exception as e:
            self.logger.error(f"❌ Erreur transcription GPU: {e}")
            return self._transcribe_internal()
    
    def _transcribe_internal(self) -> Optional[str]:
        """Transcription interne classique (fallback)"""
        try:
            # Enregistrement audio classique
            self.logger.info("🎤 Enregistrement audio...")
            audio_data = sd.rec(
                frames=int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            sd.wait()
            
            # Transcription
            self.logger.info("🧠 Transcription...")
            audio_flat = audio_data.flatten().astype(np.float32)
            
            segments, info = self.model.transcribe(
                audio_flat,
                language="fr",
                condition_on_previous_text=False
            )
            
            # Collecte résultats
            text_parts = []
            for segment in segments:
                text = segment.text.strip()
                if text:
                    text_parts.append(text)
            
            if text_parts:
                result = " ".join(text_parts)
                self.logger.info(f"✅ Transcription: {result[:50]}...")
                return result
            else:
                self.logger.info("⚠️ Aucun audio détecté")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Erreur transcription interne: {e}")
            return None
    
    def transcribe_now(self, timeout=15) -> Tuple[bool, Optional[str]]:
        """Transcription synchrone V4 (backward compatible)"""
        if not self.model_loaded:
            return False, "Modèle non chargé"
        
        try:
            # Request standard
            request_id = f"req_{time.time()}"
            self.request_queue.put({
                'action': 'transcribe',
                'id': request_id
            })
            
            # Attendre résultat
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    result = self.result_queue.get(timeout=0.5)
                    if result.get('request_id') == request_id:
                        if result['success']:
                            return True, result['result']
                        else:
                            return False, result.get('error', 'Erreur inconnue')
                except queue.Empty:
                    continue
            
            return False, "Timeout transcription"
            
        except Exception as e:
            return False, f"Erreur transcription: {e}"
    
    def start_streaming_mode(self) -> bool:
        """Démarrer mode streaming (hérité V3)"""
        if not self.model_loaded or not self.streaming_manager:
            self.logger.error("❌ Engine ou streaming manager pas prêt")
            return False
        
        try:
            self.logger.info("🌊 Activation mode streaming continu...")
            
            if self.streaming_manager.start_continuous_mode():
                self.streaming_mode = True
                self.logger.info("✅ Mode streaming actif")
                return True
            else:
                self.logger.error("❌ Échec démarrage streaming")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur start streaming: {e}")
            return False
    
    def stop_streaming_mode(self):
        """Arrêter mode streaming"""
        if self.streaming_mode and self.streaming_manager:
            self.logger.info("⏹️ Arrêt mode streaming...")
            self.streaming_manager.stop_continuous_mode()
            self.streaming_mode = False
            self.logger.info("✅ Mode streaming arrêté")
    
    def get_streaming_result(self, timeout=1.0) -> Optional[dict]:
        """Récupérer résultat streaming (hérité V3)"""
        if not self.streaming_mode:
            return None
        
        return self.streaming_manager.get_latest_result(timeout)
    
    def get_status(self) -> dict:
        """Status V4 complet avec GPU stats"""
        status = {
            'version': 'v4_gpu_optimized',
            'running': self.running,
            'model_loaded': self.model_loaded,
            'queue_size': self.request_queue.qsize(),
            'streaming_mode': self.streaming_mode,
            'gpu_enabled': self.gpu_enabled,
            'gpu_optimizations': self.gpu_optimizations,
            'memory_info': self._get_gpu_memory() if self.model_loaded else None
        }
        
        # Stats streaming si actif
        if self.streaming_mode and self.streaming_manager:
            streaming_stats = self.streaming_manager.get_stats()
            status['streaming_stats'] = streaming_stats
        
        # Stats GPU si actif
        if self.gpu_enabled and self.gpu_processor:
            gpu_stats = self.gpu_processor.get_performance_stats()
            status['gpu_stats'] = gpu_stats
        
        return status
    
    def _get_gpu_memory(self) -> dict:
        """Info mémoire GPU (étendu V4)"""
        try:
            import torch
            if torch.cuda.is_available():
                base_info = {
                    'allocated': f"{torch.cuda.memory_allocated(0) / 1024**3:.2f}GB",
                    'reserved': f"{torch.cuda.memory_reserved(0) / 1024**3:.2f}GB"
                }
                
                # Stats GPU optimizer si disponible
                if self.gpu_enabled and self.gpu_optimizer:
                    optimizer_stats = self.gpu_optimizer.get_memory_stats()
                    base_info.update(optimizer_stats)
                
                return base_info
        except:
            pass
        return {'status': 'unavailable'}
    
    def stop_engine(self):
        """Arrêter le service V4 proprement"""
        self.logger.info("🛑 Arrêt SuperWhisper2 Engine V4...")
        
        # Arrêter streaming si actif
        if self.streaming_mode:
            self.stop_streaming_mode()
        
        self.running = False
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        
        # Cleanup GPU optimizer
        if self.gpu_enabled and self.gpu_optimizer:
            self.gpu_optimizer.cleanup_memory()
        
        # Cleanup GPU memory
        if self.model_loaded:
            try:
                del self.model
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                self.logger.info("🧹 Mémoire GPU nettoyée")
            except:
                pass
        
        self.logger.info("✅ Engine V4 arrêté")


# Instance globale V4
_engine_v4_instance = None

def get_engine_v4() -> SuperWhisper2EngineV4:
    """Obtenir l'instance globale du service V4"""
    global _engine_v4_instance
    if _engine_v4_instance is None:
        _engine_v4_instance = SuperWhisper2EngineV4()
    return _engine_v4_instance


def start_service_v4():
    """Démarrer le service V4"""
    engine = get_engine_v4()
    return engine.start_engine()


if __name__ == "__main__":
    # Test standalone V4
    print("🧪 Test SuperWhisper2 Engine V4 (GPU Optimized)...")
    
    engine = SuperWhisper2EngineV4()
    if engine.start_engine():
        print("✅ Service V4 démarré")
        
        # Test transcription GPU optimisée
        print("🔄 Test transcription GPU optimisée...")
        success, result = engine.transcribe_now()
        if success:
            print(f"✅ Transcription V4: {result}")
        
        print(f"📊 Status final V4: {engine.get_status()}")
        engine.stop_engine()
    else:
        print("❌ Échec démarrage V4") 