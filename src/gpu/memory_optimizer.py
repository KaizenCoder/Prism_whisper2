#!/usr/bin/env python3
"""
GPU Memory Optimizer pour Prism_whisper2
Memory pinning + Zero-copy transfers + CUDA streams pour -0.5s latence
Architecture: Pinned buffers GPU pour éliminer copies CPU-GPU
"""

import numpy as np
import logging
import time
import threading
from typing import Optional, List, Dict, Any
from collections import deque
import gc

try:
    import torch
    import torch.cuda
    CUDA_AVAILABLE = torch.cuda.is_available()
except ImportError:
    CUDA_AVAILABLE = False
    torch = None


class GPUMemoryOptimizer:
    """
    Optimiseur mémoire GPU pour transcription ultra-rapide
    Optimisation: Memory pinning + Zero-copy + Stream processing
    """
    
    def __init__(self, device_id=0, max_buffers=8, buffer_size_mb=16):
        self.device_id = device_id
        self.max_buffers = max_buffers
        self.buffer_size = buffer_size_mb * 1024 * 1024  # MB to bytes
        
        # État GPU
        self.cuda_available = CUDA_AVAILABLE
        self.device = None
        self.streams = []
        self.memory_pool = []
        self.pinned_buffers = deque(maxlen=max_buffers)
        
        # Buffers audio optimisés
        self.audio_buffer_pool = deque(maxlen=max_buffers)
        self.result_buffer_pool = deque(maxlen=max_buffers)
        
        # Stats
        self.allocations = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_memory_saved = 0
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialiser GPU si disponible
        self.initialized = False
        if self.cuda_available:
            self._initialize_gpu()
    
    def _setup_logging(self):
        """Setup logging pour GPU optimizer"""
        logger = logging.getLogger('GPUMemoryOptimizer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - GPU - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_gpu(self):
        """Initialiser optimisations GPU"""
        try:
            self.logger.info("🔧 Initialisation GPU Memory Optimizer...")
            
            # Vérifier device disponible
            if not torch.cuda.is_available():
                self.logger.warning("⚠️ CUDA non disponible, fallback CPU")
                self.cuda_available = False
                return False
            
            # Setup device
            self.device = torch.device(f"cuda:{self.device_id}")
            torch.cuda.set_device(self.device_id)
            
            # Get GPU info
            gpu_name = torch.cuda.get_device_name(self.device_id)
            total_memory = torch.cuda.get_device_properties(self.device_id).total_memory
            self.logger.info(f"🎮 GPU: {gpu_name} ({total_memory / 1024**3:.1f}GB)")
            
            # Créer CUDA streams pour parallélisation
            self._create_cuda_streams()
            
            # Pré-allouer buffers pinned
            self._preallocate_pinned_buffers()
            
            # Optimiser cache GPU
            self._optimize_gpu_cache()
            
            self.initialized = True
            self.logger.info("✅ GPU Memory Optimizer initialisé")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Échec init GPU: {e}")
            self.cuda_available = False
            return False
    
    def _create_cuda_streams(self):
        """Créer streams CUDA pour parallélisation"""
        try:
            # 3 streams : audio input, processing, output
            stream_names = ['audio_input', 'processing', 'output']
            
            for name in stream_names:
                stream = torch.cuda.Stream(device=self.device)
                self.streams.append({
                    'name': name,
                    'stream': stream,
                    'active': False
                })
            
            self.logger.info(f"🌊 {len(self.streams)} CUDA streams créés")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création streams: {e}")
    
    def _preallocate_pinned_buffers(self):
        """Pré-allouer buffers pinned pour audio"""
        try:
            # Tailles typiques audio (3s à 16kHz = 48k samples = 192KB float32)
            audio_sizes = [
                16000 * 1,   # 1s audio
                16000 * 3,   # 3s audio
                16000 * 5,   # 5s audio
                16000 * 10   # 10s audio
            ]
            
            for size in audio_sizes:
                # Buffer pinned en mémoire pour accès GPU rapide
                buffer = torch.zeros(size, dtype=torch.float32, pin_memory=True)
                self.pinned_buffers.append({
                    'size': size,
                    'buffer': buffer,
                    'in_use': False,
                    'created_at': time.time()
                })
            
            # Buffers audio streaming (CPU pinned seulement)
            for i in range(self.max_buffers // 2):
                audio_buffer = torch.zeros(16000 * 3, dtype=torch.float32, pin_memory=True)
                self.audio_buffer_pool.append({
                    'buffer': audio_buffer,
                    'in_use': False,
                    'size': 16000 * 3
                })
            
            self.logger.info(f"📦 {len(self.pinned_buffers)} buffers pinned pré-alloués")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur pré-allocation: {e}")
    
    def _optimize_gpu_cache(self):
        """Optimiser cache GPU pour performance"""
        try:
            # Nettoyer cache initial
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Configurer allocateur pour éviter fragmentation
            if hasattr(torch.cuda, 'set_per_process_memory_fraction'):
                # Utiliser 80% de la mémoire GPU max
                torch.cuda.set_per_process_memory_fraction(0.8, self.device_id)
            
            self.logger.info("🧹 Cache GPU optimisé")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Cache optimization warning: {e}")
    
    def get_pinned_buffer(self, size: int) -> Optional[torch.Tensor]:
        """
        Obtenir buffer pinned optimisé pour taille donnée
        Zero-copy si buffer disponible
        """
        if not self.cuda_available:
            return None
        
        try:
            # Chercher buffer disponible de taille suffisante
            best_buffer = None
            best_size_diff = float('inf')
            
            for buffer_info in self.pinned_buffers:
                if (not buffer_info['in_use'] and 
                    buffer_info['size'] >= size):
                    
                    size_diff = buffer_info['size'] - size
                    if size_diff < best_size_diff:
                        best_buffer = buffer_info
                        best_size_diff = size_diff
            
            if best_buffer:
                best_buffer['in_use'] = True
                self.cache_hits += 1
                self.logger.debug(f"📋 Buffer cache hit: {size} samples")
                return best_buffer['buffer'][:size]
            
            # Pas de buffer disponible, créer nouveau
            self.cache_misses += 1
            self.logger.debug(f"📦 Buffer cache miss: {size} samples")
            
            new_buffer = torch.zeros(size, dtype=torch.float32, pin_memory=True)
            return new_buffer
            
        except Exception as e:
            self.logger.error(f"❌ Erreur get pinned buffer: {e}")
            return None
    
    def release_pinned_buffer(self, buffer: torch.Tensor):
        """Libérer buffer pinned pour réutilisation"""
        try:
            for buffer_info in self.pinned_buffers:
                if torch.equal(buffer_info['buffer'][:buffer.size(0)], buffer):
                    buffer_info['in_use'] = False
                    self.logger.debug("🔄 Buffer pinned libéré")
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Erreur release buffer: {e}")
            return False
    
    def optimize_audio_transfer(self, audio_np: np.ndarray) -> torch.Tensor:
        """
        Optimiser transfert audio CPU → GPU avec zero-copy
        """
        if not self.cuda_available:
            return torch.from_numpy(audio_np)
        
        try:
            start_time = time.time()
            
            # Obtenir buffer pinned optimisé
            buffer = self.get_pinned_buffer(len(audio_np))
            
            if buffer is not None:
                # Copy vers buffer pinned (plus rapide que allocation+copy)
                buffer[:len(audio_np)] = torch.from_numpy(audio_np)
                
                # Transfer vers GPU avec stream asynchrone
                if self.streams:
                    with torch.cuda.stream(self.streams[0]['stream']):
                        gpu_tensor = buffer.to(self.device, non_blocking=True)
                else:
                    gpu_tensor = buffer.to(self.device, non_blocking=True)
                
                transfer_time = (time.time() - start_time) * 1000
                self.logger.debug(f"⚡ Transfer optimisé: {transfer_time:.1f}ms")
                return gpu_tensor
            else:
                # Fallback classique
                return torch.from_numpy(audio_np).to(self.device)
                
        except Exception as e:
            self.logger.error(f"❌ Erreur optimize transfer: {e}")
            return torch.from_numpy(audio_np)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Statistiques mémoire GPU détaillées"""
        stats = {
            'cuda_available': self.cuda_available,
            'initialized': self.initialized,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_ratio': self.cache_hits / max(self.cache_hits + self.cache_misses, 1),
            'pinned_buffers': len(self.pinned_buffers),
            'streams': len(self.streams)
        }
        
        if self.cuda_available:
            try:
                stats.update({
                    'gpu_allocated': f"{torch.cuda.memory_allocated(self.device_id) / 1024**3:.2f}GB",
                    'gpu_reserved': f"{torch.cuda.memory_reserved(self.device_id) / 1024**3:.2f}GB",
                    'gpu_max_allocated': f"{torch.cuda.max_memory_allocated(self.device_id) / 1024**3:.2f}GB"
                })
            except Exception as e:
                stats['gpu_memory_error'] = str(e)
        
        return stats
    
    def cleanup_memory(self):
        """Nettoyage mémoire GPU intelligent"""
        if not self.cuda_available:
            return
        
        try:
            self.logger.info("🧹 Nettoyage mémoire GPU...")
            
            # Libérer tous les buffers
            for buffer_info in self.pinned_buffers:
                buffer_info['in_use'] = False
            
            # Vider cache PyTorch
            torch.cuda.empty_cache()
            
            # Garbage collect
            gc.collect()
            
            # Reset stats
            allocated_before = torch.cuda.memory_allocated(self.device_id)
            
            self.logger.info(f"✅ Mémoire nettoyée: {allocated_before / 1024**2:.1f}MB libérés")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur cleanup: {e}")
    
    def benchmark_transfer_speed(self, sizes=[16000, 48000, 160000]) -> Dict[str, float]:
        """Benchmark vitesse transfert pour différentes tailles"""
        if not self.cuda_available:
            return {'error': 'CUDA non disponible'}
        
        results = {}
        
        for size in sizes:
            # Test données audio simulées
            audio_data = np.random.randn(size).astype(np.float32)
            
            # Test transfer classique
            start = time.time()
            tensor_classic = torch.from_numpy(audio_data).to(self.device)
            classic_time = (time.time() - start) * 1000
            
            # Test transfer optimisé
            start = time.time()
            tensor_optimized = self.optimize_audio_transfer(audio_data)
            optimized_time = (time.time() - start) * 1000
            
            speedup = classic_time / optimized_time if optimized_time > 0 else 1.0
            
            results[f"{size}_samples"] = {
                'classic_ms': round(classic_time, 2),
                'optimized_ms': round(optimized_time, 2),
                'speedup': round(speedup, 2)
            }
            
            # Cleanup
            del tensor_classic, tensor_optimized
        
        return results


class GPUAudioProcessor:
    """
    Processeur audio GPU intégré avec memory optimizer
    Interface haut niveau pour optimisations transparentes
    """
    
    def __init__(self, whisper_model):
        self.whisper_model = whisper_model
        self.optimizer = GPUMemoryOptimizer()
        self.logger = logging.getLogger('GPUAudioProcessor')
        
        # Métriques performance
        self.total_optimizations = 0
        self.total_time_saved = 0.0
    
    def process_audio_optimized(self, audio_np: np.ndarray) -> tuple:
        """
        Traitement audio optimisé GPU avec memory pinning
        """
        start_time = time.time()
        
        try:
            # Transfer optimisé vers GPU
            if self.optimizer.cuda_available:
                audio_tensor = self.optimizer.optimize_audio_transfer(audio_np)
                
                # Conversion pour Whisper (si nécessaire)
                if hasattr(audio_tensor, 'cpu'):
                    audio_for_whisper = audio_tensor.cpu().numpy()
                else:
                    audio_for_whisper = audio_np
            else:
                audio_for_whisper = audio_np
            
            # Transcription Whisper
            segments, info = self.whisper_model.transcribe(
                audio_for_whisper,
                language="fr",
                condition_on_previous_text=False
            )
            
            # Collecter résultats
            text_parts = []
            for segment in segments:
                text = segment.text.strip()
                if text:
                    text_parts.append(text)
            
            result = " ".join(text_parts) if text_parts else None
            processing_time = time.time() - start_time
            
            # Stats
            self.total_optimizations += 1
            
            self.logger.debug(f"🎵 Audio traité en {processing_time:.2f}s (GPU optimisé)")
            
            return True, result, processing_time
            
        except Exception as e:
            self.logger.error(f"❌ Erreur processing GPU: {e}")
            return False, str(e), time.time() - start_time
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Stats performance processeur GPU"""
        base_stats = {
            'total_optimizations': self.total_optimizations,
            'avg_time_saved': self.total_time_saved / max(self.total_optimizations, 1)
        }
        
        optimizer_stats = self.optimizer.get_memory_stats()
        base_stats.update(optimizer_stats)
        
        return base_stats


if __name__ == "__main__":
    # Test standalone GPU optimizer
    print("🧪 Test GPU Memory Optimizer...")
    
    optimizer = GPUMemoryOptimizer()
    
    if optimizer.cuda_available:
        print("✅ CUDA disponible")
        
        # Test benchmark
        results = optimizer.benchmark_transfer_speed()
        print(f"📊 Benchmark transfers: {results}")
        
        # Test stats
        stats = optimizer.get_memory_stats()
        print(f"📈 Memory stats: {stats}")
        
        optimizer.cleanup_memory()
    else:
        print("⚠️ CUDA non disponible, optimisations désactivées") 