from src.audio.audio_streamer import AudioStreamer
import threading
from typing import Callable
import numpy as np

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
        """
        Callback appelé par AudioStreamer chaque fois qu'un segment audio est prêt.
        """
        if not self.running:
            return

        duration_s = len(audio_chunk) / 16000
        model = self.model_selector(duration_s)
        stream_id = self.stream_counter
        self.stream_counter += 1

        # Lance la transcription dans un thread séparé pour ne pas bloquer la boucle de capture audio.
        # C'est une décision d'architecture clé pour la réactivité.
        threading.Thread(target=self.transcriber_callback, args=(audio_chunk, model, stream_id)).start() 