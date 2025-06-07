#!/usr/bin/env python3
"""
SuperWhisper2 Engine V3 avec Audio Streaming
Service background + Model pre-loading + Audio streaming asynchrone
Optimisation: -4s pre-loading + -1s streaming = -5s total
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

# Import audio streaming (fix relative import)
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from audio.audio_streamer import AudioStreamingManager


class SuperWhisper2EngineV3:
    """
    Service background Whisper V3 avec streaming audio
    Performance: Model pre-loaded + Audio streaming parallèle
    """
    
    def __init__(self):
        # Hériter des capacités V2
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
        
        # Nouveau: Audio streaming manager
        self.streaming_manager = None
        self.streaming_mode = False
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Thread worker
        self.worker_thread = None
        
    def _setup_logging(self):
        """Setup logging V3"""
        logger = logging.getLogger('SuperWhisper2EngineV3')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - ENGINE_V3 - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def start_engine(self):
        """Démarrer le service V3 avec streaming"""
        try:
            self.logger.info("🚀 Démarrage SuperWhisper2 Engine V3...")
            
            # 1. Pre-load modèle (hérité V2)
            self._preload_whisper_model()
            
            # 2. Initialiser streaming manager
            self.streaming_manager = AudioStreamingManager(self)
            
            # 3. Démarrer worker thread
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
            self.logger.info("✅ SuperWhisper2 Engine V3 prêt (pre-loaded + streaming)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Échec démarrage engine V3: {e}")
            return False
    
    def _preload_whisper_model(self):
        """Pre-loading du modèle Whisper (identique V2)"""
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
        """Boucle worker V3 (gestion requests + streaming)"""
        self.logger.info("🔄 Worker loop V3 démarré")
        
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
                
            except Exception as e:
                self.logger.error(f"❌ Erreur worker V3: {e}")
    
    def _handle_request(self, request):
        """Handler pour requests (V2 compatible)"""
        try:
            if request['action'] == 'transcribe':
                result = self._transcribe_internal()
                self.result_queue.put({
                    'success': True,
                    'result': result,
                    'request_id': request.get('id')
                })
            elif request['action'] == 'start_streaming':
                self.start_streaming_mode()
            elif request['action'] == 'stop_streaming':
                self.stop_streaming_mode()
                
        except Exception as e:
            self.logger.error(f"❌ Erreur handle request: {e}")
            self.result_queue.put({
                'success': False,
                'error': str(e),
                'request_id': request.get('id', 'unknown')
            })
    
    def transcribe_now(self, timeout=15) -> Tuple[bool, Optional[str]]:
        """
        Transcription synchrone V3 (backward compatible)
        """
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
        """
        NOUVEAU: Démarrer mode streaming continu
        Optimisation: Capture pendant transcription = -1s latence
        """
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
        """Récupérer résultat streaming (non-bloquant)"""
        if not self.streaming_mode:
            return None
        
        return self.streaming_manager.get_latest_result(timeout)
    
    def _transcribe_internal(self) -> Optional[str]:
        """Transcription interne (héritée V2)"""
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
    
    def get_status(self) -> dict:
        """Status V3 complet"""
        status = {
            'version': 'v3_streaming',
            'running': self.running,
            'model_loaded': self.model_loaded,
            'queue_size': self.request_queue.qsize(),
            'streaming_mode': self.streaming_mode,
            'memory_info': self._get_gpu_memory() if self.model_loaded else None
        }
        
        # Stats streaming si actif
        if self.streaming_mode and self.streaming_manager:
            streaming_stats = self.streaming_manager.get_stats()
            status['streaming_stats'] = streaming_stats
        
        return status
    
    def _get_gpu_memory(self) -> dict:
        """Info mémoire GPU (hérité V2)"""
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
        """Arrêter le service V3 proprement"""
        self.logger.info("🛑 Arrêt SuperWhisper2 Engine V3...")
        
        # Arrêter streaming si actif
        if self.streaming_mode:
            self.stop_streaming_mode()
        
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
        
        self.logger.info("✅ Engine V3 arrêté")


# Instance globale V3
_engine_v3_instance = None

def get_engine_v3() -> SuperWhisper2EngineV3:
    """Obtenir l'instance globale du service V3"""
    global _engine_v3_instance
    if _engine_v3_instance is None:
        _engine_v3_instance = SuperWhisper2EngineV3()
    return _engine_v3_instance


def start_service_v3():
    """Démarrer le service V3"""
    engine = get_engine_v3()
    return engine.start_engine()


if __name__ == "__main__":
    # Test standalone V3
    print("🧪 Test SuperWhisper2 Engine V3 (Streaming)...")
    
    engine = SuperWhisper2EngineV3()
    if engine.start_engine():
        print("✅ Service V3 démarré")
        
        # Test transcription classique
        print("🔄 Test transcription classique...")
        success, result = engine.transcribe_now()
        if success:
            print(f"✅ Transcription classique: {result}")
        
        # Test mode streaming
        print("🌊 Test mode streaming...")
        if engine.start_streaming_mode():
            print("✅ Streaming démarré, attente 10s...")
            
            # Écouter résultats streaming
            for i in range(10):
                result = engine.get_streaming_result(timeout=1.0)
                if result and result['success']:
                    print(f"🎵 Streaming résultat: {result['text']}")
                time.sleep(1)
            
            engine.stop_streaming_mode()
        
        print(f"📊 Status final: {engine.get_status()}")
        engine.stop_engine()
    else:
        print("❌ Échec démarrage V3") 