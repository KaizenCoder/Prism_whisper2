# SuperWhisper2 - Proposition d'Implémentation 🛠️

**Pour** : Peer Review et Validation Technique  
**Date** : Janvier 2025  
**Version** : Draft 1.0  

---

## 🏗️ Architecture Globale

### Vue d'Ensemble
```
┌─────────────────────────────────────────────────────────────┐
│                    SUPERWHISPER2                            │
├─────────────────────────────────────────────────────────────┤
│  System Tray UI  │  Configuration  │   Error Handling       │
├─────────────────────────────────────────────────────────────┤
│                   CORE ENGINE                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │   Talon     │  │    Audio     │  │     Whisper RTX     │ │
│  │ Interface   │  │   Capture    │  │      Engine         │ │
│  │             │  │              │  │                     │ │
│  │ Win+Shift+V │──│ Microphone   │──│ GPU Transcription   │ │
│  │ Text Insert │  │ VAD          │  │ faster-whisper      │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Communication Flow
```
1. User presses Win+Shift+V
   ↓
2. Talon detects hotkey → Calls Python callback
   ↓
3. Core Engine → Starts audio capture
   ↓
4. Audio Capture → Records until silence detected
   ↓
5. Whisper RTX → Transcribes audio to text
   ↓
6. Core Engine → Sends text back to Talon
   ↓
7. Talon → Inserts text into active application
```

## 📦 Structure de Code Proposée

### Project Structure
```
SuperWhisper2/
├── pyproject.toml                 # Dependencies & packaging
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py              # Main orchestrator
│   │   ├── config.py              # Configuration management
│   │   └── events.py              # Event handling system
│   ├── whisper_engine/
│   │   ├── __init__.py
│   │   ├── rtx_engine.py          # RTX 3090 optimized Whisper
│   │   ├── model_manager.py       # Model loading & caching
│   │   └── performance_monitor.py # GPU monitoring
│   ├── talon_plugin/
│   │   ├── __init__.py
│   │   ├── interface.py           # Python-Talon communication
│   │   ├── superwhisper2.talon    # Talon script
│   │   └── superwhisper2.py       # Talon Python module
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── capture.py             # Audio recording
│   │   ├── vad.py                 # Voice Activity Detection
│   │   └── preprocessing.py       # Audio preprocessing
│   └── ui/
│       ├── __init__.py
│       ├── system_tray.py         # System tray interface
│       ├── overlay.py             # Transcription overlay
│       └── config_dialog.py       # Settings dialog
├── config/
│   ├── default.yaml               # Default configuration
│   └── models.yaml                # Model specifications
├── scripts/
│   ├── install.py                 # Installation script
│   ├── setup_talon.py             # Talon configuration
│   └── benchmark.py               # Performance testing
└── tests/
    ├── test_engine.py
    ├── test_whisper_rtx.py
    ├── test_talon_integration.py
    └── test_performance.py
```

## 🔧 Implémentation Détaillée

### 1. Core Engine (`src/core/engine.py`)

```python
"""
SuperWhisper2 Core Engine
Orchestrateur principal gérant tous les composants
"""

import asyncio
import logging
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

from ..whisper_engine import WhisperRTXEngine
from ..talon_plugin import TalonInterface
from ..audio import AudioCapture, VoiceActivityDetector
from ..ui import SystemTray, TranscriptionOverlay
from .config import Config
from .events import EventBus, Event

class EngineState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    INSERTING = "inserting"
    ERROR = "error"

@dataclass
class TranscriptionResult:
    text: str
    language: str
    confidence: float
    duration: float

class SuperWhisper2Engine:
    """
    Moteur principal de SuperWhisper2
    Gère l'orchestration de tous les composants
    """
    
    def __init__(self, config_path: Optional[str] = None):
        # Configuration
        self.config = Config(config_path)
        
        # Logging
        self._setup_logging()
        
        # Event system
        self.event_bus = EventBus()
        
        # State management
        self._state = EngineState.IDLE
        self._transcription_active = False
        
        # Components (lazy loading)
        self._whisper_engine: Optional[WhisperRTXEngine] = None
        self._talon_interface: Optional[TalonInterface] = None
        self._audio_capture: Optional[AudioCapture] = None
        self._vad: Optional[VoiceActivityDetector] = None
        self._system_tray: Optional[SystemTray] = None
        self._overlay: Optional[TranscriptionOverlay] = None
        
        # Performance monitoring
        self._stats = {
            'total_transcriptions': 0,
            'average_latency': 0.0,
            'error_count': 0
        }
    
    async def initialize(self):
        """Initialisation asynchrone de tous les composants"""
        try:
            self.logger.info("Initializing SuperWhisper2 Engine...")
            
            # Initialize Whisper engine (preload model)
            self._whisper_engine = WhisperRTXEngine(self.config.whisper)
            await self._whisper_engine.initialize()
            
            # Initialize audio components
            self._audio_capture = AudioCapture(self.config.audio)
            self._vad = VoiceActivityDetector(self.config.vad)
            
            # Initialize Talon interface
            self._talon_interface = TalonInterface(self.config.talon)
            await self._talon_interface.setup_hotkeys(self._on_hotkey_pressed)
            
            # Initialize UI components
            self._system_tray = SystemTray(self._on_tray_action)
            self._overlay = TranscriptionOverlay()
            
            # Setup event handlers
            self._setup_event_handlers()
            
            self._set_state(EngineState.IDLE)
            self.logger.info("SuperWhisper2 Engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize engine: {e}")
            await self._handle_error(e)
            raise
    
    async def start(self):
        """Démarre le service SuperWhisper2"""
        if self._state == EngineState.IDLE:
            self.logger.info("Starting SuperWhisper2 service...")
            
            # Start system tray
            await self._system_tray.show()
            
            # Start background tasks
            asyncio.create_task(self._monitor_performance())
            
            self.logger.info("SuperWhisper2 service started")
        else:
            self.logger.warning(f"Cannot start: engine in state {self._state}")
    
    async def stop(self):
        """Arrête le service SuperWhisper2"""
        self.logger.info("Stopping SuperWhisper2 service...")
        
        # Cancel any active transcription
        if self._transcription_active:
            await self._cancel_transcription()
        
        # Cleanup components
        if self._system_tray:
            await self._system_tray.hide()
        
        if self._talon_interface:
            await self._talon_interface.cleanup()
        
        if self._whisper_engine:
            await self._whisper_engine.cleanup()
        
        self._set_state(EngineState.IDLE)
        self.logger.info("SuperWhisper2 service stopped")
    
    # ========================================
    # Hotkey Handling
    # ========================================
    
    async def _on_hotkey_pressed(self, hotkey: str):
        """Callback appelé par Talon lors d'un hotkey"""
        self.logger.debug(f"Hotkey pressed: {hotkey}")
        
        if hotkey == "win-shift-v":
            await self._start_transcription()
        elif hotkey == "win-shift-s":
            await self._stop_transcription()
        elif hotkey == "win-shift-c":
            await self._show_config()
    
    async def _start_transcription(self):
        """Démarre une session de transcription"""
        if self._state != EngineState.IDLE:
            self.logger.warning(f"Cannot start transcription: engine in state {self._state}")
            return
        
        try:
            self._set_state(EngineState.LISTENING)
            self._transcription_active = True
            
            # Show overlay
            await self._overlay.show("Listening...")
            
            # Start audio capture
            audio_data = await self._capture_audio_until_silence()
            
            if audio_data is None:
                await self._cancel_transcription()
                return
            
            # Process transcription
            self._set_state(EngineState.PROCESSING)
            await self._overlay.update("Processing...")
            
            result = await self._transcribe_audio(audio_data)
            
            if result:
                # Insert text
                self._set_state(EngineState.INSERTING)
                await self._overlay.update(f"Inserting: {result.text[:50]}...")
                
                await self._insert_text(result.text)
                
                # Update stats
                self._update_stats(result)
                
                self.logger.info(f"Transcription completed: '{result.text[:100]}'")
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            await self._handle_error(e)
        
        finally:
            await self._cleanup_transcription()
    
    async def _capture_audio_until_silence(self) -> Optional[bytes]:
        """Capture audio jusqu'à détection de silence"""
        try:
            return await self._audio_capture.record_until_silence(
                vad=self._vad,
                max_duration=self.config.audio.max_duration,
                silence_threshold=self.config.vad.silence_threshold
            )
        except Exception as e:
            self.logger.error(f"Audio capture failed: {e}")
            return None
    
    async def _transcribe_audio(self, audio_data: bytes) -> Optional[TranscriptionResult]:
        """Transcrit l'audio en texte via Whisper RTX"""
        try:
            import time
            start_time = time.time()
            
            result = await self._whisper_engine.transcribe(
                audio_data,
                language=self.config.whisper.default_language
            )
            
            duration = time.time() - start_time
            
            return TranscriptionResult(
                text=result.text.strip(),
                language=result.language,
                confidence=result.confidence,
                duration=duration
            )
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return None
    
    async def _insert_text(self, text: str):
        """Insère le texte dans l'application active via Talon"""
        try:
            await self._talon_interface.insert_text(text)
        except Exception as e:
            self.logger.error(f"Text insertion failed: {e}")
            raise
    
    # ========================================
    # State Management
    # ========================================
    
    def _set_state(self, new_state: EngineState):
        """Change l'état du moteur"""
        old_state = self._state
        self._state = new_state
        
        self.logger.debug(f"State changed: {old_state} → {new_state}")
        
        # Emit event
        self.event_bus.emit(Event("state_changed", {
            "old_state": old_state,
            "new_state": new_state
        }))
        
        # Update system tray
        if self._system_tray:
            asyncio.create_task(self._system_tray.update_status(new_state))
    
    async def _cleanup_transcription(self):
        """Nettoie après une transcription"""
        self._transcription_active = False
        self._set_state(EngineState.IDLE)
        
        if self._overlay:
            await self._overlay.hide()
    
    async def _cancel_transcription(self):
        """Annule la transcription en cours"""
        self.logger.info("Cancelling transcription")
        
        if self._audio_capture:
            await self._audio_capture.stop()
        
        await self._cleanup_transcription()
    
    # ========================================
    # Error Handling & Recovery
    # ========================================
    
    async def _handle_error(self, error: Exception):
        """Gestion centralisée des erreurs"""
        self._stats['error_count'] += 1
        self._set_state(EngineState.ERROR)
        
        error_msg = f"Error: {str(error)}"
        self.logger.error(error_msg)
        
        # Show error in overlay
        if self._overlay:
            await self._overlay.show_error(error_msg)
        
        # Attempt recovery
        await self._attempt_recovery()
    
    async def _attempt_recovery(self):
        """Tentative de récupération automatique"""
        try:
            self.logger.info("Attempting automatic recovery...")
            
            # Reset components
            await self._cleanup_transcription()
            
            # Test Whisper engine
            if self._whisper_engine:
                await self._whisper_engine.health_check()
            
            # Test Talon interface
            if self._talon_interface:
                await self._talon_interface.health_check()
            
            self._set_state(EngineState.IDLE)
            self.logger.info("Recovery successful")
            
        except Exception as e:
            self.logger.error(f"Recovery failed: {e}")
            # Could trigger notification to user
    
    # ========================================
    # Monitoring & Performance
    # ========================================
    
    def _update_stats(self, result: TranscriptionResult):
        """Met à jour les statistiques de performance"""
        self._stats['total_transcriptions'] += 1
        
        # Update average latency (exponential moving average)
        alpha = 0.1
        self._stats['average_latency'] = (
            alpha * result.duration + 
            (1 - alpha) * self._stats['average_latency']
        )
    
    async def _monitor_performance(self):
        """Monitoring continu des performances"""
        while True:
            try:
                # Check GPU memory
                if self._whisper_engine:
                    gpu_memory = await self._whisper_engine.get_gpu_memory_usage()
                    
                    if gpu_memory > self.config.performance.max_vram_gb:
                        self.logger.warning(f"High GPU memory usage: {gpu_memory:.1f}GB")
                
                # Check average latency
                if (self._stats['average_latency'] > self.config.performance.max_latency_ms / 1000):
                    self.logger.warning(f"High latency: {self._stats['average_latency']:.3f}s")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute
    
    # ========================================
    # Configuration & Setup
    # ========================================
    
    def _setup_logging(self):
        """Configure le système de logging"""
        self.logger = logging.getLogger('superwhisper2')
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(self.config.logging.level)
    
    def _setup_event_handlers(self):
        """Configure les gestionnaires d'événements"""
        self.event_bus.subscribe("whisper_model_loaded", self._on_model_loaded)
        self.event_bus.subscribe("transcription_completed", self._on_transcription_completed)
        self.event_bus.subscribe("error", self._on_error_event)
    
    # Event handlers
    async def _on_model_loaded(self, event):
        self.logger.info(f"Whisper model loaded: {event.data['model_name']}")
    
    async def _on_transcription_completed(self, event):
        result = event.data['result']
        self.logger.debug(f"Transcription: {result.text} ({result.confidence:.2f})")
    
    async def _on_error_event(self, event):
        await self._handle_error(event.data['error'])
    
    # UI callbacks
    async def _on_tray_action(self, action: str):
        if action == "start":
            await self.start()
        elif action == "stop":
            await self.stop()
        elif action == "config":
            await self._show_config()
        elif action == "exit":
            await self.stop()
            exit(0)
    
    async def _show_config(self):
        """Affiche la fenêtre de configuration"""
        # To be implemented
        pass
    
    # ========================================
    # Public API
    # ========================================
    
    @property
    def state(self) -> EngineState:
        return self._state
    
    @property
    def stats(self) -> dict:
        return self._stats.copy()
    
    def is_ready(self) -> bool:
        return (
            self._state == EngineState.IDLE and
            self._whisper_engine is not None and
            self._talon_interface is not None
        )


# Entry point
async def main():
    """Point d'entrée principal"""
    engine = SuperWhisper2Engine()
    
    try:
        await engine.initialize()
        await engine.start()
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down SuperWhisper2...")
        await engine.stop()
    except Exception as e:
        print(f"Fatal error: {e}")
        await engine.stop()
        raise

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Whisper RTX Engine (`src/whisper_engine/rtx_engine.py`)

```python
"""
Whisper RTX 3090 Optimized Engine
Gestion optimisée de Whisper sur RTX 3090
"""

import os
import asyncio
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
import torch
import numpy as np
from faster_whisper import WhisperModel

# Configure environment for RTX 3090
os.environ["HF_HOME"] = "D:/modeles_ia"
os.environ["HF_CACHE_DIR"] = "D:/modeles_ia/huggingface/hub"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # RTX 3090 priority

@dataclass
class WhisperConfig:
    model_size: str = "medium"
    device: str = "cuda"
    compute_type: str = "float16"
    language: str = "fr"
    beam_size: int = 5
    best_of: int = 5
    patience: float = 1.0
    length_penalty: float = 1.0
    repetition_penalty: float = 1.1
    no_repeat_ngram_size: int = 0
    temperature: float = 0.0
    compression_ratio_threshold: float = 2.4
    log_prob_threshold: float = -1.0
    no_speech_threshold: float = 0.6

@dataclass
class TranscriptionResult:
    text: str
    language: str
    confidence: float
    segments: list
    duration: float

class WhisperRTXEngine:
    """
    Moteur Whisper optimisé pour RTX 3090
    """
    
    def __init__(self, config: WhisperConfig):
        self.config = config
        self.logger = logging.getLogger('whisper_rtx')
        
        # Model state
        self._model: Optional[WhisperModel] = None
        self._model_loaded = False
        self._loading_lock = asyncio.Lock()
        
        # Performance monitoring
        self._stats = {
            'total_transcriptions': 0,
            'average_duration': 0.0,
            'model_load_time': 0.0,
            'gpu_memory_peak': 0.0
        }
        
        # CUDA setup
        self._setup_cuda()
    
    def _setup_cuda(self):
        """Configuration CUDA pour RTX 3090"""
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA not available - RTX 3090 required")
        
        # Get RTX 3090 info
        device_count = torch.cuda.device_count()
        current_device = torch.cuda.current_device()
        device_name = torch.cuda.get_device_name(current_device)
        
        self.logger.info(f"CUDA Devices: {device_count}")
        self.logger.info(f"Current Device: {current_device} - {device_name}")
        
        if "RTX 3090" not in device_name and "RTX" not in device_name:
            self.logger.warning(f"Expected RTX 3090, got: {device_name}")
        
        # Optimize CUDA settings
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        
        # Memory management
        torch.cuda.empty_cache()
        
        total_memory = torch.cuda.get_device_properties(current_device).total_memory
        self.logger.info(f"GPU Memory: {total_memory / 1024**3:.1f} GB")
    
    async def initialize(self):
        """Initialisation et pré-chargement du modèle"""
        async with self._loading_lock:
            if self._model_loaded:
                return
            
            try:
                self.logger.info(f"Loading Whisper model: {self.config.model_size}")
                start_time = time.time()
                
                # Load model with optimizations
                self._model = WhisperModel(
                    self.config.model_size,
                    device=self.config.device,
                    compute_type=self.config.compute_type,
                    download_root="D:/modeles_ia/whisper",
                    local_files_only=False  # Allow download if needed
                )
                
                # Warm up model with dummy audio
                await self._warm_up_model()
                
                load_time = time.time() - start_time
                self._stats['model_load_time'] = load_time
                
                self._model_loaded = True
                self.logger.info(f"Model loaded in {load_time:.2f}s")
                
                # Check GPU memory usage
                memory_used = self._get_gpu_memory_usage()
                self._stats['gpu_memory_peak'] = memory_used
                self.logger.info(f"GPU Memory Usage: {memory_used:.1f} GB")
                
            except Exception as e:
                self.logger.error(f"Failed to load Whisper model: {e}")
                raise
    
    async def _warm_up_model(self):
        """Réchauffe le modèle avec un audio de test"""
        try:
            # Generate dummy audio (1 second of silence)
            dummy_audio = np.zeros(16000, dtype=np.float32)
            
            # Run dummy transcription
            segments, info = self._model.transcribe(
                dummy_audio,
                language=self.config.language,
                beam_size=1,  # Faster for warmup
                best_of=1
            )
            
            # Consume generator to ensure model is fully loaded
            list(segments)
            
            self.logger.debug("Model warm-up completed")
            
        except Exception as e:
            self.logger.warning(f"Model warm-up failed: {e}")
    
    async def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> TranscriptionResult:
        """
        Transcrit l'audio en texte
        
        Args:
            audio_data: Audio bytes (WAV format)
            language: Langue cible (None pour auto-détection)
        
        Returns:
            TranscriptionResult avec le texte transcrit
        """
        if not self._model_loaded:
            await self.initialize()
        
        try:
            start_time = time.time()
            
            # Convert audio bytes to numpy array
            audio_array = self._process_audio(audio_data)
            
            # Transcription parameters
            transcribe_params = {
                'language': language or self.config.language,
                'beam_size': self.config.beam_size,
                'best_of': self.config.best_of,
                'patience': self.config.patience,
                'length_penalty': self.config.length_penalty,
                'repetition_penalty': self.config.repetition_penalty,
                'no_repeat_ngram_size': self.config.no_repeat_ngram_size,
                'temperature': self.config.temperature,
                'compression_ratio_threshold': self.config.compression_ratio_threshold,
                'log_prob_threshold': self.config.log_prob_threshold,
                'no_speech_threshold': self.config.no_speech_threshold,
                'word_timestamps': True,
                'prepend_punctuations': "\"'"¿([{-",
                'append_punctuations': "\"'.。,，!！?？:：")]}、"
            }
            
            # Run transcription on GPU
            segments, info = self._model.transcribe(audio_array, **transcribe_params)
            
            # Process results
            segments_list = list(segments)
            full_text = ' '.join(segment.text.strip() for segment in segments_list)
            
            # Calculate confidence (average of segments)
            confidence = np.mean([segment.avg_logprob for segment in segments_list]) if segments_list else 0.0
            confidence = np.exp(confidence)  # Convert log prob to probability
            
            duration = time.time() - start_time
            
            # Update stats
            self._update_stats(duration)
            
            result = TranscriptionResult(
                text=full_text,
                language=info.language,
                confidence=confidence,
                segments=[{
                    'start': seg.start,
                    'end': seg.end,
                    'text': seg.text,
                    'confidence': np.exp(seg.avg_logprob)
                } for seg in segments_list],
                duration=duration
            )
            
            self.logger.debug(f"Transcription completed in {duration:.3f}s: '{full_text[:100]}'")
            return result
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            raise
    
    def _process_audio(self, audio_data: bytes) -> np.ndarray:
        """
        Traite les données audio pour Whisper
        
        Args:
            audio_data: Audio bytes (format WAV)
            
        Returns:
            numpy array float32 à 16kHz
        """
        try:
            import wave
            import io
            
            # Open WAV data
            with wave.open(io.BytesIO(audio_data), 'rb') as wav_file:
                # Get audio parameters
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                
                # Read raw audio data
                raw_audio = wav_file.readframes(frames)
            
            # Convert to numpy array
            if sample_width == 1:
                dtype = np.uint8
            elif sample_width == 2:
                dtype = np.int16
            elif sample_width == 4:
                dtype = np.int32
            else:
                raise ValueError(f"Unsupported sample width: {sample_width}")
            
            audio_array = np.frombuffer(raw_audio, dtype=dtype)
            
            # Handle stereo
            if channels == 2:
                audio_array = audio_array.reshape(-1, 2).mean(axis=1)
            
            # Convert to float32 [-1, 1]
            if dtype == np.uint8:
                audio_array = (audio_array.astype(np.float32) - 128) / 128
            elif dtype == np.int16:
                audio_array = audio_array.astype(np.float32) / 32768
            elif dtype == np.int32:
                audio_array = audio_array.astype(np.float32) / 2147483648
            
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                audio_array = self._resample_audio(audio_array, sample_rate, 16000)
            
            return audio_array
            
        except Exception as e:
            self.logger.error(f"Audio processing failed: {e}")
            raise
    
    def _resample_audio(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        try:
            import librosa
            return librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)
        except ImportError:
            # Fallback: simple decimation/interpolation (not ideal but works)
            if orig_sr == target_sr:
                return audio
            
            ratio = target_sr / orig_sr
            new_length = int(len(audio) * ratio)
            
            # Simple linear interpolation
            indices = np.linspace(0, len(audio) - 1, new_length)
            return np.interp(indices, np.arange(len(audio)), audio)
    
    def _update_stats(self, duration: float):
        """Met à jour les statistiques de performance"""
        self._stats['total_transcriptions'] += 1
        
        # Exponential moving average
        alpha = 0.1
        self._stats['average_duration'] = (
            alpha * duration + 
            (1 - alpha) * self._stats['average_duration']
        )
    
    def _get_gpu_memory_usage(self) -> float:
        """Retourne l'utilisation mémoire GPU en GB"""
        if torch.cuda.is_available():
            memory_used = torch.cuda.memory_allocated() / 1024**3
            return memory_used
        return 0.0
    
    async def get_gpu_memory_usage(self) -> float:
        """Version async de get_gpu_memory_usage"""
        return self._get_gpu_memory_usage()
    
    async def health_check(self) -> bool:
        """Vérifie que le moteur fonctionne correctement"""
        try:
            if not self._model_loaded:
                return False
            
            # Test with minimal audio
            dummy_audio = np.zeros(1600, dtype=np.float32)  # 0.1 second
            
            # Convert to WAV bytes for consistency
            import wave
            import io
            
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes((dummy_audio * 32767).astype(np.int16).tobytes())
            
            wav_data = wav_buffer.getvalue()
            
            # Test transcription
            result = await self.transcribe(wav_data)
            
            return result is not None
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Nettoie les ressources"""
        if self._model:
            del self._model
            self._model = None
            self._model_loaded = False
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.logger.info("Whisper RTX engine cleaned up")
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de performance"""
        return {
            **self._stats,
            'gpu_memory_current': self._get_gpu_memory_usage(),
            'model_loaded': self._model_loaded,
            'realtime_factor': self._calculate_realtime_factor()
        }
    
    def _calculate_realtime_factor(self) -> float:
        """Calcule le facteur temps réel (doit être > 1.0)"""
        if self._stats['average_duration'] > 0:
            # Assume average audio length of 3 seconds
            estimated_audio_length = 3.0
            return estimated_audio_length / self._stats['average_duration']
        return 0.0


# Utility functions
def check_rtx3090_available() -> bool:
    """Vérifie si RTX 3090 est disponible"""
    if not torch.cuda.is_available():
        return False
    
    device_name = torch.cuda.get_device_name()
    return "RTX 3090" in device_name or "RTX" in device_name

def benchmark_performance() -> Dict[str, float]:
    """Benchmark rapide des performances"""
    # Implementation for performance testing
    pass
```

## 📋 Points de Review Requis

### 1. Architecture
- [ ] **Modularité** : Chaque composant est-il suffisamment découplé ?
- [ ] **Scalabilité** : L'architecture peut-elle évoluer facilement ?
- [ ] **Error Handling** : La gestion d'erreur est-elle robuste ?
- [ ] **Performance** : L'architecture introduit-elle des goulots d'étranglement ?

### 2. Code Quality
- [ ] **Lisibilité** : Le code est-il clair et bien documenté ?
- [ ] **Type Safety** : Les type hints sont-ils corrects et complets ?
- [ ] **Testing** : Les composants sont-ils testables unitairement ?
- [ ] **Logging** : Le système de logs est-il approprié ?

### 3. Performance
- [ ] **Latence** : L'objectif <500ms est-il réaliste ?
- [ ] **Memory Usage** : La gestion mémoire GPU est-elle optimale ?
- [ ] **Async Design** : L'architecture async est-elle bien conçue ?
- [ ] **Resource Management** : Les ressources sont-elles bien gérées ?

### 4. Integration
- [ ] **Talon Interface** : L'intégration Talon est-elle viable ?
- [ ] **Windows Native** : Le comportement Windows est-il natif ?
- [ ] **Hardware Specific** : L'optimisation RTX 3090 est-elle correcte ?
- [ ] **Configuration** : Le système de config est-il flexible ?

## 🚀 Prochaines Étapes

### Phase 1 : Validation Technique
1. **Review de l'architecture** par peers
2. **Proof of concept** des composants critiques
3. **Benchmarks** performance RTX 3090
4. **Tests** intégration Talon

### Phase 2 : Implémentation MVP
1. **Core Engine** : Version minimale fonctionnelle
2. **Whisper RTX** : Optimisations performance
3. **Audio Pipeline** : Capture et VAD
4. **Talon Plugin** : Hotkeys et insertion

### Phase 3 : Polish & Testing
1. **UI Components** : System tray et overlay
2. **Error Recovery** : Robustesse et reliability
3. **Installation** : Package et déploiement
4. **Documentation** : Guide utilisateur complet

---

**Cette proposition d'implémentation vise à créer un SuperWhisper2 robuste, performant et natif Windows. Vos retours et suggestions sont essentiels pour affiner l'architecture avant l'implémentation ! 🎯** 