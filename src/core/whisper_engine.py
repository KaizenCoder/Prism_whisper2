#!/usr/bin/env python3
"""
SuperWhisper2 Engine avec Pre-loading
Service background qui maintient le modèle Whisper en mémoire RTX 3090
Optimisation: -4s latence par élimination du model loading
"""

import os
import sys
import time
import threading
import queue
import traceback
from typing import Optional, Tuple
import logging

# Force utilisation GPU RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

try:
    import sounddevice as sd
    import numpy as np
    from faster_whisper import WhisperModel
except ImportError as e:
    print(f"ERROR: Modules requis manquants: {e}")
    sys.exit(1)


class SuperWhisper2Engine:
    """
    Service background Whisper avec model pre-loading
    Performance: Model chargé 1 fois au démarrage vs chaque transcription
    """
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.running = False
        
        # Queue pour requests async
        self.request_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # Configuration audio
        self.sample_rate = 16000
        self.channels = 1
        self.duration = 3.0  # 3 secondes d'enregistrement
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Thread worker
        self.worker_thread = None
        
    def _setup_logging(self):
        """Setup logging interne"""
        logger = logging.getLogger('SuperWhisper2Engine')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - ENGINE - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def start_engine(self):
        """Démarrer le service avec pre-loading"""
        try:
            self.logger.info("🚀 Démarrage SuperWhisper2 Engine...")
            
            # 1. Pre-load modèle (4s une seule fois vs chaque call)
            self._preload_whisper_model()
            
            # 2. Démarrer worker thread
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
            self.logger.info("✅ SuperWhisper2 Engine prêt (modèle pre-loaded)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Échec démarrage engine: {e}")
            return False
    
    def _preload_whisper_model(self):
        """Pre-loading du modèle Whisper (4s sauvés)"""
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
    
    def _worker_loop(self):
        """Boucle worker pour traitement async"""
        self.logger.info("🔄 Worker loop démarré")
        
        while self.running:
            try:
                # Attendre request (timeout 1s)
                try:
                    request = self.request_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Traiter request
                if request['action'] == 'transcribe':
                    result = self._transcribe_internal()
                    self.result_queue.put({
                        'success': True,
                        'result': result,
                        'request_id': request.get('id')
                    })
                
                self.request_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"❌ Erreur worker: {e}")
                self.result_queue.put({
                    'success': False,
                    'error': str(e),
                    'request_id': request.get('id', 'unknown')
                })
    
    def transcribe_now(self, timeout=15) -> Tuple[bool, Optional[str]]:
        """
        Transcription synchrone optimisée
        Returns: (success, text)
        """
        if not self.model_loaded:
            return False, "Modèle non chargé"
        
        try:
            # Request async
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
    
    def _transcribe_internal(self) -> Optional[str]:
        """Transcription interne optimisée (modèle déjà chargé)"""
        try:
            # 1. Enregistrement audio (3s)
            self.logger.info("🎤 Enregistrement audio...")
            audio_data = sd.rec(
                frames=int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            sd.wait()
            
            # 2. Transcription (modèle déjà en mémoire = ultra-rapide)
            self.logger.info("🧠 Transcription...")
            audio_flat = audio_data.flatten().astype(np.float32)
            
            segments, info = self.model.transcribe(
                audio_flat,
                language="fr",
                condition_on_previous_text=False
            )
            
            # 3. Collecte résultats
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
            traceback.print_exc()
            return None
    
    def get_status(self) -> dict:
        """Status du service"""
        return {
            'running': self.running,
            'model_loaded': self.model_loaded,
            'queue_size': self.request_queue.qsize(),
            'memory_info': self._get_gpu_memory() if self.model_loaded else None
        }
    
    def _get_gpu_memory(self) -> dict:
        """Info mémoire GPU RTX 3090"""
        try:
            import torch
            if torch.cuda.is_available():
                return {
                    'allocated': f"{torch.cuda.memory_allocated(0) / 1024**3:.1f}GB",
                    'reserved': f"{torch.cuda.memory_reserved(0) / 1024**3:.1f}GB"
                }
        except:
            pass
        return {'status': 'unavailable'}
    
    def stop_engine(self):
        """Arrêter le service proprement"""
        self.logger.info("🛑 Arrêt SuperWhisper2 Engine...")
        self.running = False
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        
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
        
        self.logger.info("✅ Engine arrêté")


# Instance globale (singleton pattern)
_engine_instance = None

def get_engine() -> SuperWhisper2Engine:
    """Obtenir l'instance globale du service"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SuperWhisper2Engine()
    return _engine_instance


def start_service():
    """Démarrer le service background"""
    engine = get_engine()
    return engine.start_engine()


def transcribe() -> Tuple[bool, Optional[str]]:
    """Interface simple pour transcription"""
    engine = get_engine()
    return engine.transcribe_now()


if __name__ == "__main__":
    # Test standalone
    print("🧪 Test SuperWhisper2 Engine...")
    
    engine = SuperWhisper2Engine()
    if engine.start_engine():
        print("✅ Service démarré, test transcription...")
        success, result = engine.transcribe_now()
        if success:
            print(f"✅ Transcription: {result}")
        else:
            print(f"❌ Échec: {result}")
        
        print(f"📊 Status: {engine.get_status()}")
        engine.stop_engine()
    else:
        print("❌ Échec démarrage service") 