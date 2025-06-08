from src.audio.audio_streamer import AudioStreamer
import threading
from typing import Callable
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import queue

class AudioStreamingManager:
    """
    Orchestre le pipeline de streaming audio.
    Récupère les chunks audio de AudioStreamer et les envoie au moteur de transcription.
    """
    def __init__(self, transcriber_callback: Callable, logger: any, model_selector: Callable):
        """
        Initialise le gestionnaire de streaming.

        Args:
            transcriber_callback: La fonction à appeler pour traiter un chunk audio (ex: engine.process_audio_chunk).
            logger: L'instance du logger.
            model_selector: La fonction qui retourne le modèle whisper à utiliser selon la durée de l'audio.
        """
        self.transcriber_callback = transcriber_callback
        self.logger = logger
        self.model_selector = model_selector

        # Note: on passe `self.on_audio_ready` comme callback à l'AudioStreamer.
        self.audio_streamer = AudioStreamer(callback=self.on_audio_ready, logger=self.logger)
        
        self.running = False
        self.stream_counter = 0

        # Remplacement threads daemon par ThreadPoolExecutor selon développeur C
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.results_queue = queue.Queue()

    def start(self):
        """Démarre le streaming audio."""
        self.running = True
        self.audio_streamer.start()
        self.logger.info("AudioStreamingManager a démarré et écoute AudioStreamer.")

    def stop(self):
        """Arrête le streaming audio."""
        self.running = False
        self.audio_streamer.stop()
        self.logger.info("AudioStreamingManager arrêté.")

    def on_audio_ready(self, audio_chunk: np.ndarray):
        """Audio callback utilisant ThreadPoolExecutor selon développeur C"""
        # Soumission au pool au lieu de créer threads manuels
        future = self.thread_pool.submit(
            self._safe_transcriber_callback, 
            audio_chunk, 
            self.model_selector(len(audio_chunk) / 16000), 
            self.stream_counter
        )
        self.stream_counter += 1
    
    def _safe_transcriber_callback(self, audio_chunk: np.ndarray, model: any, stream_id: int):
        """Wrapper sécurisé pour callbacks avec ThreadPoolExecutor"""
        try:
            # Traitement transcription dans pool de threads
            result = self.transcriber_callback(audio_chunk, model, stream_id)
            self.results_queue.put(result)
        except Exception as e:
            self.logger.error(f"Erreur ThreadPool callback: {e}")
            # Continuer le streaming même en cas d'erreur 