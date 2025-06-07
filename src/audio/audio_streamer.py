#!/usr/bin/env python3
"""
Audio Streamer Asynchrone pour Prism_whisper2
Parallélisation capture audio + transcription pour -1s latence
Architecture: Buffer circulaire + VAD + Pipeline async
"""

import numpy as np
import sounddevice as sd
import threading
import queue
import time
import logging
from typing import Optional, Callable, List, Tuple
from collections import deque
import wave
import tempfile


class AudioStreamer:
    """
    Streaming audio asynchrone avec pipeline parallèle
    Optimisation: Capture pendant transcription = -1s latence
    """
    
    def __init__(self, sample_rate=16000, chunk_duration=1.0, buffer_size=5):
        # Configuration audio
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration  # 1s chunks
        self.chunk_frames = int(sample_rate * chunk_duration)
        self.channels = 1
        
        # Buffers circulaires
        self.buffer_size = buffer_size  # 5 chunks max
        self.audio_buffer = deque(maxlen=buffer_size)
        self.processing_queue = queue.Queue(maxsize=buffer_size)
        
        # State management
        self.streaming = False
        self.stream = None
        self.capture_thread = None
        self.processing_thread = None
        
        # Callbacks
        self.transcription_callback = None
        self.audio_ready_callback = None
        
        # VAD (Voice Activity Detection) simple
        self.vad_threshold = 0.01  # Seuil volume
        self.silence_timeout = 2.0  # 2s silence = fin
        self.last_voice_time = 0
        
        # Metrics
        self.chunks_captured = 0
        self.chunks_processed = 0
        
        # Setup logging
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging pour audio streamer"""
        logger = logging.getLogger('AudioStreamer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - AUDIO - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def set_transcription_callback(self, callback: Callable[[np.ndarray], None]):
        """Définir callback pour transcription audio"""
        self.transcription_callback = callback
    
    def start_streaming(self) -> bool:
        """Démarrer le streaming audio asynchrone"""
        try:
            self.logger.info("🎤 Démarrage streaming audio asynchrone...")
            
            # Reset state
            self.streaming = True
            self.chunks_captured = 0
            self.chunks_processed = 0
            self.last_voice_time = time.time()
            
            # Démarrer stream audio
            self.stream = sd.InputStream(
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._audio_callback,
                blocksize=self.chunk_frames,
                dtype=np.float32
            )
            
            # Démarrer threads
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            
            self.stream.start()
            self.capture_thread.start()
            self.processing_thread.start()
            
            self.logger.info("✅ Streaming audio démarré")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage streaming: {e}")
            return False
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback audio temps réel (non-bloquant)"""
        if status:
            self.logger.warning(f"⚠️ Audio status: {status}")
        
        # Copier données audio
        audio_chunk = indata.copy()[:, 0]  # Mono
        
        # VAD simple (Voice Activity Detection)
        volume = np.sqrt(np.mean(audio_chunk ** 2))
        has_voice = volume > self.vad_threshold
        
        if has_voice:
            self.last_voice_time = time.time()
        
        # Ajouter au buffer (non-bloquant)
        try:
            self.processing_queue.put_nowait({
                'audio': audio_chunk,
                'timestamp': time.time(),
                'volume': volume,
                'has_voice': has_voice
            })
            self.chunks_captured += 1
        except queue.Full:
            # Buffer plein, ignorer chunk (pas critique)
            pass
    
    def _capture_loop(self):
        """Boucle capture (accumulation chunks pour transcription)"""
        accumulated_audio = []
        accumulation_duration = 3.0  # 3s d'audio pour transcription
        target_chunks = int(accumulation_duration / self.chunk_duration)
        
        while self.streaming:
            try:
                # Accumuler chunks jusqu'à durée cible
                while len(accumulated_audio) < target_chunks and self.streaming:
                    try:
                        chunk_data = self.processing_queue.get(timeout=0.5)
                        
                        # Ajouter seulement si voix détectée
                        if chunk_data['has_voice']:
                            accumulated_audio.append(chunk_data['audio'])
                        
                        # Check timeout silence
                        if time.time() - self.last_voice_time > self.silence_timeout:
                            if accumulated_audio:
                                self.logger.info("🔇 Silence détecté, traitement audio accumulé")
                                break
                        
                    except queue.Empty:
                        continue
                
                # Traiter audio accumulé si suffisant
                if accumulated_audio:
                    combined_audio = np.concatenate(accumulated_audio)
                    self.logger.info(f"🎵 Audio prêt: {len(combined_audio)/self.sample_rate:.1f}s")
                    
                    # Déclencher transcription (parallèle)
                    if self.transcription_callback:
                        # Thread séparé pour non-blocage
                        transcription_thread = threading.Thread(
                            target=self.transcription_callback,
                            args=(combined_audio,),
                            daemon=True
                        )
                        transcription_thread.start()
                    
                    # Reset accumulation
                    accumulated_audio = []
                    self.chunks_processed += 1
                
            except Exception as e:
                self.logger.error(f"❌ Erreur capture loop: {e}")
                time.sleep(0.1)
    
    def _processing_loop(self):
        """Boucle processing (gestion VAD et buffers)"""
        while self.streaming:
            try:
                # Monitoring et nettoyage buffers
                if self.processing_queue.qsize() > self.buffer_size * 0.8:
                    self.logger.warning("⚠️ Buffer audio presque plein")
                
                # Stats périodiques
                if self.chunks_captured % 50 == 0 and self.chunks_captured > 0:
                    self.logger.info(f"📊 Chunks: {self.chunks_captured} capturés, {self.chunks_processed} traités")
                
                time.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur processing loop: {e}")
                time.sleep(1.0)
    
    def stop_streaming(self):
        """Arrêter le streaming proprement"""
        self.logger.info("🛑 Arrêt streaming audio...")
        
        self.streaming = False
        
        # Arrêter stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        # Attendre threads
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2)
        
        self.logger.info("✅ Streaming arrêté")
    
    def get_stats(self) -> dict:
        """Statistiques streaming"""
        return {
            'streaming': self.streaming,
            'chunks_captured': self.chunks_captured,
            'chunks_processed': self.chunks_processed,
            'queue_size': self.processing_queue.qsize(),
            'last_voice_age': time.time() - self.last_voice_time if self.last_voice_time else 0,
            'sample_rate': self.sample_rate,
            'chunk_duration': self.chunk_duration
        }
    
    def capture_single_shot(self, duration=3.0) -> Optional[np.ndarray]:
        """
        Capture audio simple (backward compatibility)
        """
        try:
            self.logger.info(f"🎤 Capture single shot {duration}s...")
            
            audio_data = sd.rec(
                frames=int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            sd.wait()
            
            return audio_data.flatten()
            
        except Exception as e:
            self.logger.error(f"❌ Erreur capture single: {e}")
            return None


class AudioStreamingManager:
    """
    Manager pour intégration streaming avec Whisper Engine
    Orchestration complète du pipeline audio asynchrone
    """
    
    def __init__(self, whisper_engine):
        self.whisper_engine = whisper_engine
        self.audio_streamer = AudioStreamer()
        self.active = False
        
        # Setup callback transcription
        self.audio_streamer.set_transcription_callback(self._handle_transcription)
        
        # Results queue
        self.results_queue = queue.Queue()
        
        self.logger = logging.getLogger('AudioStreamingManager')
    
    def _handle_transcription(self, audio_data: np.ndarray):
        """Handler pour transcription audio (appelé asynchrone)"""
        try:
            start_time = time.time()
            
            # Transcription via engine pre-loaded
            segments, info = self.whisper_engine.model.transcribe(
                audio_data,
                language="fr",
                condition_on_previous_text=False
            )
            
            # Collecter résultats
            text_parts = []
            for segment in segments:
                text = segment.text.strip()
                if text:
                    text_parts.append(text)
            
            if text_parts:
                result = " ".join(text_parts)
                elapsed = time.time() - start_time
                
                self.logger.info(f"✅ Transcription streaming: {result[:50]}... ({elapsed:.1f}s)")
                
                # Ajouter aux résultats
                self.results_queue.put({
                    'success': True,
                    'text': result,
                    'duration': elapsed,
                    'timestamp': time.time()
                })
            
        except Exception as e:
            self.logger.error(f"❌ Erreur transcription streaming: {e}")
            self.results_queue.put({
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            })
    
    def start_continuous_mode(self) -> bool:
        """Démarrer mode streaming continu"""
        if not self.whisper_engine.model_loaded:
            self.logger.error("❌ Engine Whisper pas prêt")
            return False
        
        self.logger.info("🌊 Démarrage mode streaming continu...")
        self.active = True
        return self.audio_streamer.start_streaming()
    
    def get_latest_result(self, timeout=1.0) -> Optional[dict]:
        """Récupérer dernier résultat transcription"""
        try:
            return self.results_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop_continuous_mode(self):
        """Arrêter mode streaming"""
        self.logger.info("⏹️ Arrêt mode streaming continu...")
        self.active = False
        self.audio_streamer.stop_streaming()
    
    def get_stats(self) -> dict:
        """Stats complètes streaming"""
        stats = self.audio_streamer.get_stats()
        stats.update({
            'manager_active': self.active,
            'results_pending': self.results_queue.qsize(),
            'whisper_ready': self.whisper_engine.model_loaded
        })
        return stats


if __name__ == "__main__":
    # Test standalone streaming
    import sys
    sys.path.append('..')
    
    print("🧪 Test Audio Streaming Asynchrone...")
    
    def dummy_transcription(audio_data):
        print(f"📝 Transcription simulée: {len(audio_data)} samples")
        time.sleep(1)  # Simuler processing
        print("✅ Transcription terminée")
    
    streamer = AudioStreamer()
    streamer.set_transcription_callback(dummy_transcription)
    
    if streamer.start_streaming():
        print("✅ Streaming démarré, test 10s...")
        time.sleep(10)
        
        stats = streamer.get_stats()
        print(f"📊 Stats: {stats}")
        
        streamer.stop_streaming()
    else:
        print("❌ Échec streaming") 