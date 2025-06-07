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
    Capture l'audio du microphone en continu et le transmet via un callback.
    """
    def __init__(self, callback: Callable[[np.ndarray], None], logger: any, sample_rate=16000, chunk_duration=3.0):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_frames = int(sample_rate * chunk_duration)
        self.channels = 1
        
        self.callback = callback
        self.logger = logger
        
        self.running = False
        self.stream = None
        self.thread = None

    def start(self):
        """Démarre la capture audio."""
        if self.running:
            return
        self.logger.info("🎤 Démarrage de la capture audio...")
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.start()

    def _capture_loop(self):
        """Boucle de capture qui lit depuis le microphone."""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.float32,
            blocksize=self.chunk_frames,
            callback=self._audio_callback
        )
        with self.stream:
            while self.running:
                time.sleep(0.1) # La boucle est principalement pilotée par le callback

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback de sounddevice, appelé avec de nouvelles données audio."""
        if status:
            self.logger.warning(f"AudioStreamer status: {status}")
        if self.running and self.callback:
            try:
                # Le callback est appelé directement avec le chunk audio
                self.callback(indata[:, 0])
            except Exception as e:
                self.logger.error(f"Erreur dans le callback de l'AudioStreamer: {e}")

    def stop(self):
        """Arrête la capture audio."""
        if not self.running:
            return
        self.logger.info("🛑 Arrêt de la capture audio...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.stream:
            self.stream.close()
        self.logger.info("✅ Capture audio arrêtée.")

    def add_to_buffer(self, audio_data: np.ndarray):
        """
        Méthode pour ajouter manuellement des données audio au flux.
        Utile pour les tests. Simule une capture micro.
        """
        if self.running and self.callback:
            self.logger.info(f"Injecting {len(audio_data)/self.sample_rate:.2f}s of audio for testing.")
            self.callback(audio_data)


class AudioStreamingManager:
    """
    Chef d'orchestre pour le streaming audio continu et la transcription
    """
    def __init__(self, whisper_engine):
        self.engine = whisper_engine
        self.logger = self.engine.logger
        self.streamer = AudioStreamer(
            sample_rate=self.engine.sample_rate,
            chunk_duration=1.0, # Traiter l'audio par chunks de 1s
            callback=self.engine.process_audio_chunk
        )
        self.continuous_mode = False
        self.last_result = None

    def _handle_transcription(self, audio_data: np.ndarray):
        """
        Gère la logique de transcription d'un chunk audio.
        Cette méthode est maintenant directement dans l'engine (process_audio_chunk)
        pour un couplage plus propre.
        """
        # obsolète
        pass

    def start_continuous_mode(self) -> bool:
        """Démarrer mode streaming continu"""
        if not self.engine.model_loaded:
            self.logger.error("❌ Engine Whisper pas prêt")
            return False
        
        self.logger.info("🌊 Démarrage mode streaming continu...")
        self.continuous_mode = True
        return self.streamer.start()
    
    def get_latest_result(self, timeout=1.0) -> Optional[dict]:
        """Récupérer dernier résultat transcription"""
        try:
            return self.results_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop_continuous_mode(self):
        """Arrêter mode streaming"""
        self.logger.info("⏹️ Arrêt mode streaming continu...")
        self.continuous_mode = False
        self.streamer.stop()
    
    def get_stats(self) -> dict:
        """Stats complètes streaming"""
        stats = {
            'manager_active': self.continuous_mode,
            'results_pending': self.results_queue.qsize(),
            'whisper_ready': self.engine.model_loaded
        }
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
    
    streamer = AudioStreamer(dummy_transcription, logging.getLogger('AudioStreamer'))
    
    if streamer.start():
        print("✅ Streaming démarré, test 10s...")
        time.sleep(10)
        
        stats = streamer.get_stats()
        print(f"📊 Stats: {stats}")
        
        streamer.stop()
    else:
        print("❌ Échec streaming") 