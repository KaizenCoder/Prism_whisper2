#!/usr/bin/env python3
"""
FIX Engine V5 Callbacks V2 - SuperWhisper2
Version corrigée avec signature callback flexible
RTX 3090 24GB + Engine V5 Phase 3 + Correction callbacks
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import sounddevice as sd
import numpy as np

# Configuration RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # RTX 3090 24GB
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajouter src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)


class EngineV5CallbackFixV2:
    def __init__(self):
        self.engine = None
        self.callback_count = 0
        self.test_running = False
        self.rode_device_id = None
        
        # Interface simple
        self.root = tk.Tk()
        self.root.title("FIX Engine V5 Callbacks V2")
        self.root.geometry("1000x600")
        self.root.configure(bg="#0d1117")
        
        self.colors = {
            'bg': '#0d1117',
            'bg_secondary': '#161b22',
            'text': '#c9d1d9',
            'accent': '#58a6ff',
            'success': '#3fb950',
            'error': '#f85149'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Interface de correction"""
        # Title
        title_label = tk.Label(self.root, 
                              text="🔧 FIX ENGINE V5 CALLBACKS V2",
                              font=("Segoe UI", 18, "bold"),
                              bg=self.colors['bg'], 
                              fg=self.colors['accent'])
        title_label.pack(pady=20)
        
        # Buttons
        btn_frame = tk.Frame(self.root, bg=self.colors['bg'])
        btn_frame.pack(pady=10)
        
        self.init_btn = tk.Button(btn_frame,
                                 text="🚀 INIT & FIX",
                                 command=self.init_and_fix,
                                 bg=self.colors['accent'], 
                                 fg="white",
                                 font=("Segoe UI", 12, "bold"),
                                 width=15, height=2)
        self.init_btn.pack(side="left", padx=10)
        
        self.test_btn = tk.Button(btn_frame,
                                 text="🧪 TEST CALLBACKS",
                                 command=self.test_callbacks,
                                 bg=self.colors['success'], 
                                 fg="white",
                                 font=("Segoe UI", 12, "bold"),
                                 width=15, height=2,
                                 state="disabled")
        self.test_btn.pack(side="left", padx=10)
        
        # Status
        self.status_label = tk.Label(self.root,
                                    text="Status: Non initialisé",
                                    font=("Segoe UI", 12, "bold"),
                                    bg=self.colors['bg'], 
                                    fg=self.colors['text'])
        self.status_label.pack(pady=10)
        
        self.callback_label = tk.Label(self.root,
                                      text="Callbacks: 0",
                                      font=("Segoe UI", 12, "bold"),
                                      bg=self.colors['bg'], 
                                      fg=self.colors['text'])
        self.callback_label.pack()
        
        # Log
        self.log_text = scrolledtext.ScrolledText(self.root,
                                                 font=("Consolas", 10),
                                                 bg=self.colors['bg_secondary'], 
                                                 fg=self.colors['text'],
                                                 wrap=tk.WORD,
                                                 height=20)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=20)
        
    def log(self, message):
        """Logging avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        full_msg = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, full_msg)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def detect_rode(self):
        """Détection Rode rapide"""
        try:
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if 'rode' in device['name'].lower() and device['max_input_channels'] > 0:
                    self.rode_device_id = i
                    self.log(f"✅ Rode détecté: Device {i}")
                    return True
            return False
        except:
            return False
    
    def init_and_fix(self):
        """Initialisation et correction Engine V5"""
        self.log("="*60)
        self.log("🔧 CORRECTION CALLBACKS ENGINE V5 V2")
        self.log("="*60)
        
        self.status_label.config(text="Status: Initialisation...", fg=self.colors['accent'])
        self.init_btn.config(state="disabled")
        
        def init_thread():
            try:
                # Step 1: Rode detection
                if not self.detect_rode():
                    raise Exception("Rode non détecté")
                
                # Step 2: Init Engine V5
                self.log("📦 Import Engine V5...")
                from src.core.whisper_engine_v5 import SuperWhisper2EngineV5
                
                self.log("⚙️ Création Engine V5...")
                self.engine = SuperWhisper2EngineV5()
                
                self.log("🚀 Démarrage Engine V5...")
                success = self.engine.start_engine()
                
                if not success:
                    raise Exception("Engine V5 start failed")
                
                self.log("✅ Engine V5 initialisé")
                
                # Step 3: DIAGNOSTIC RAPIDE
                self.log("🔍 Diagnostic rapide...")
                
                # Check streaming_manager
                if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
                    manager = self.engine.streaming_manager
                    self.log(f"✅ StreamingManager trouvé: {type(manager).__name__}")
                    
                    # Check methods
                    if hasattr(manager, 'on_audio_ready'):
                        self.log("✅ on_audio_ready() trouvée")
                    if hasattr(manager, 'transcriber_callback'):
                        self.log("✅ transcriber_callback() trouvée")
                else:
                    raise Exception("StreamingManager manquant")
                
                # Check current callback state
                callback_current = getattr(self.engine, 'transcription_callback', 'NOT_FOUND')
                self.log(f"📊 transcription_callback actuel: {callback_current}")
                
                # Step 4: CORRECTION CALLBACKS
                self.log("🔧 CORRECTION CHAÎNE CALLBACKS V2...")
                self.fix_callback_chain_v2()
                
                self.status_label.config(text="Status: Engine V5 corrigé ✅", fg=self.colors['success'])
                self.test_btn.config(state="normal")
                
            except Exception as e:
                error_msg = f"❌ Erreur: {e}"
                self.log(error_msg)
                self.status_label.config(text="Status: Échec", fg=self.colors['error'])
                self.init_btn.config(state="normal")
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def fix_callback_chain_v2(self):
        """CORRECTION V2 des callbacks avec signature flexible"""
        self.log("🔧 Correction chaîne callbacks V2...")
        
        # 1. Créer callback principal
        def main_callback(text: str):
            """Callback principal corrigé"""
            if text and text.strip():
                self.callback_count += 1
                self.callback_label.config(text=f"Callbacks: {self.callback_count}")
                self.log(f"🎯 CALLBACK REÇU #{self.callback_count}: '{text.strip()}'")
        
        # 2. Configurer callback sur l'engine
        self.log("🔗 Configuration callback engine...")
        try:
            # Method 1: set_transcription_callback
            if hasattr(self.engine, 'set_transcription_callback'):
                self.engine.set_transcription_callback(main_callback)
                self.log("✅ set_transcription_callback() configuré")
            
            # Method 2: Direct attribute
            self.engine.transcription_callback = main_callback
            self.log("✅ transcription_callback attribut configuré")
            
            # Method 3: _transcription_callback (private)
            self.engine._transcription_callback = main_callback
            self.log("✅ _transcription_callback configuré")
            
        except Exception as e:
            self.log(f"⚠️ Erreur config engine callback: {e}")
        
        # 3. Configurer callback sur StreamingManager avec signature flexible
        if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
            manager = self.engine.streaming_manager
            self.log("🔗 Configuration callback StreamingManager V2...")
            
            try:
                # Store original callback if exists
                original_callback = None
                if hasattr(manager, 'transcriber_callback'):
                    original_callback = getattr(manager, 'transcriber_callback')
                    self.log(f"📋 Original callback trouvé: {type(original_callback)}")
                
                # Create flexible signature callback
                def flexible_callback(*args, **kwargs):
                    """Callback avec signature flexible pour Engine V5"""
                    try:
                        # Extract text from various possible argument patterns
                        text = ""
                        
                        if args:
                            # Try first argument as text
                            if len(args) >= 1 and isinstance(args[0], str):
                                text = args[0]
                            # Try second argument if first is not string
                            elif len(args) >= 2 and isinstance(args[1], str):
                                text = args[1]
                            # Try third argument
                            elif len(args) >= 3 and isinstance(args[2], str):
                                text = args[2]
                        
                        # Try kwargs
                        if not text and kwargs:
                            text = kwargs.get('text', '') or kwargs.get('transcript', '') or kwargs.get('result', '')
                        
                        # Log debug info
                        if args or kwargs:
                            self.log(f"🔍 Callback appelé avec: args={len(args)}, kwargs={list(kwargs.keys())}")
                        
                        # Call main callback if text found
                        if text and text.strip():
                            main_callback(text)
                        
                        # Call original callback if exists
                        if callable(original_callback):
                            try:
                                if args or kwargs:
                                    original_callback(*args, **kwargs)
                                else:
                                    original_callback(text)
                            except Exception as e:
                                self.log(f"⚠️ Original callback error: {e}")
                                
                    except Exception as e:
                        self.log(f"⚠️ Flexible callback error: {e}")
                
                # Replace transcriber_callback
                manager.transcriber_callback = flexible_callback
                self.log("✅ StreamingManager.transcriber_callback V2 patché")
                
                # Add additional callback attributes
                manager.callback = flexible_callback
                manager._callback = flexible_callback
                manager.on_transcription = flexible_callback
                self.log("✅ Callbacks multiples ajoutés au StreamingManager")
                
            except Exception as e:
                self.log(f"⚠️ Erreur config StreamingManager: {e}")
        
        # 4. Forcer connexion AudioStreamer→StreamingManager
        self.log("🔗 Force connexion AudioStreamer→StreamingManager...")
        self.force_audio_connection()
        
        self.log("✅ Correction callbacks V2 terminée")
    
    def force_audio_connection(self):
        """Force la connexion audio"""
        try:
            # Configure sounddevice global
            sd.default.device[0] = self.rode_device_id
            sd.default.samplerate = 16000
            sd.default.channels = 1
            self.log("✅ Sounddevice configuré")
            
            # Start streaming manager if needed
            if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
                manager = self.engine.streaming_manager
                
                # Try to start/restart
                if hasattr(manager, 'start'):
                    try:
                        result = manager.start()
                        self.log(f"✅ StreamingManager.start() → {result}")
                    except Exception as e:
                        self.log(f"⚠️ StreamingManager.start() error: {e}")
                
                # Check if there's an audio_streamer
                if hasattr(manager, 'audio_streamer') and manager.audio_streamer:
                    streamer = manager.audio_streamer
                    self.log("🎵 AudioStreamer trouvé")
                    
                    # Force device configuration
                    if hasattr(streamer, 'device_id'):
                        current_device = getattr(streamer, 'device_id', 'N/A')
                        self.log(f"📊 AudioStreamer device: {current_device}")
                        
                        if current_device != self.rode_device_id:
                            # Try to set device
                            for method_name in ['set_device_id', 'set_device']:
                                if hasattr(streamer, method_name):
                                    try:
                                        method = getattr(streamer, method_name)
                                        method(self.rode_device_id)
                                        self.log(f"✅ {method_name}({self.rode_device_id})")
                                        break
                                    except Exception as e:
                                        self.log(f"⚠️ {method_name} error: {e}")
                    
                    # Start AudioStreamer
                    for method_name in ['start', 'begin_recording']:
                        if hasattr(streamer, method_name):
                            try:
                                method = getattr(streamer, method_name)
                                result = method()
                                self.log(f"✅ AudioStreamer.{method_name}() → {result}")
                                break
                            except Exception as e:
                                self.log(f"⚠️ AudioStreamer.{method_name} error: {e}")
            
        except Exception as e:
            self.log(f"⚠️ Erreur connexion audio: {e}")
    
    def test_callbacks(self):
        """Test des callbacks corrigés V2"""
        if not self.engine:
            self.log("❌ Engine non initialisé")
            return
        
        self.log("="*60)
        self.log("🧪 TEST CALLBACKS CORRIGÉS V2")
        self.log("="*60)
        
        self.test_running = True
        self.callback_count = 0
        self.callback_label.config(text="Callbacks: 0")
        
        # Test 1: Manual callback trigger
        self.log("🧪 Test 1: Trigger callback manuel...")
        try:
            callback = getattr(self.engine, 'transcription_callback', None)
            if callback and callable(callback):
                callback("Test callback manuel Engine V5 V2")
                self.log("✅ Callback manuel déclenché")
            else:
                self.log("❌ Pas de callback callable trouvé")
        except Exception as e:
            self.log(f"❌ Erreur callback manuel: {e}")
        
        # Test 2: StreamingManager callback avec multiples signatures
        if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
            manager = self.engine.streaming_manager
            self.log("🧪 Test 2: StreamingManager callback...")
            
            try:
                if hasattr(manager, 'transcriber_callback'):
                    # Test différentes signatures
                    manager.transcriber_callback("Test StreamingManager V2")
                    manager.transcriber_callback("Test avec args", "arg2", "arg3")
                    manager.transcriber_callback(text="Test avec kwargs")
                    self.log("✅ StreamingManager callbacks déclenchés")
            except Exception as e:
                self.log(f"❌ Erreur StreamingManager callback: {e}")
        
        # Test 3: Audio injection amélioré
        self.log("🧪 Test 3: Injection audio améliorée...")
        self.test_audio_injection()
        
        # Test 4: Real audio streaming
        self.log("🧪 Test 4: Streaming audio réel (15s)...")
        self.test_real_streaming()
    
    def test_audio_injection(self):
        """Test injection audio avec seuil abaissé"""
        try:
            # Capture 2 seconds of audio for better detection
            self.log("🎤 Capture 2s audio...")
            audio_data = sd.rec(int(2 * 16000), samplerate=16000, channels=1, device=self.rode_device_id)
            sd.wait()
            
            audio_flat = audio_data.flatten().astype(np.float32)
            rms = np.sqrt(np.mean(audio_flat**2))
            max_level = np.max(np.abs(audio_flat))
            self.log(f"📊 Audio: RMS={rms:.6f}, Max={max_level:.6f}")
            
            if rms > 0.0003 or max_level > 0.001:  # Seuil très abaissé
                self.log("✅ Audio détecté → Injection...")
                
                # Try to inject via StreamingManager
                if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
                    manager = self.engine.streaming_manager
                    if hasattr(manager, 'on_audio_ready'):
                        try:
                            result = manager.on_audio_ready(audio_flat)
                            self.log(f"✅ Injection audio → {result}")
                        except Exception as e:
                            self.log(f"❌ Erreur injection: {e}")
            else:
                self.log("⚪ Audio trop faible → Injection forcée...")
                
                # Force injection even with silence
                if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
                    manager = self.engine.streaming_manager
                    if hasattr(manager, 'on_audio_ready'):
                        try:
                            # Create synthetic test audio
                            test_audio = np.random.normal(0, 0.01, 16000 * 2).astype(np.float32)
                            result = manager.on_audio_ready(test_audio)
                            self.log(f"✅ Injection audio forcée → {result}")
                        except Exception as e:
                            self.log(f"❌ Erreur injection forcée: {e}")
                
        except Exception as e:
            self.log(f"❌ Erreur test audio: {e}")
    
    def test_real_streaming(self):
        """Test streaming audio réel prolongé"""
        def streaming_thread():
            try:
                self.log("🎵 Démarrage streaming audio réel V2...")
                
                chunk_count = 0
                
                def audio_callback(indata, frames, time, status):
                    nonlocal chunk_count
                    if self.test_running:
                        chunk_count += 1
                        audio_chunk = indata[:, 0].astype(np.float32)
                        
                        # Log every 50 chunks
                        if chunk_count % 50 == 0:
                            rms = np.sqrt(np.mean(audio_chunk**2))
                            self.log(f"📊 Chunk #{chunk_count}: RMS={rms:.6f}")
                        
                        # Inject into Engine V5
                        if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
                            manager = self.engine.streaming_manager
                            if hasattr(manager, 'on_audio_ready'):
                                try:
                                    manager.on_audio_ready(audio_chunk)
                                except:
                                    pass  # Silent fail
                
                with sd.InputStream(callback=audio_callback,
                                   device=self.rode_device_id,
                                   channels=1,
                                   samplerate=16000,
                                   blocksize=1024):
                    
                    for i in range(150):  # 15 seconds
                        if not self.test_running:
                            break
                        time.sleep(0.1)
                
                self.log(f"⏹️ Streaming arrêté après {chunk_count} chunks")
                
            except Exception as e:
                self.log(f"❌ Erreur streaming: {e}")
        
        threading.Thread(target=streaming_thread, daemon=True).start()
        
        # Stop after 15 seconds
        def stop_test():
            time.sleep(15)
            self.test_running = False
            self.log(f"📊 Test terminé: {self.callback_count} callbacks reçus au total")
        
        threading.Thread(target=stop_test, daemon=True).start()
    
    def run(self):
        """Lancement interface"""
        self.log("🔧 FIX ENGINE V5 CALLBACKS V2")
        self.log("Objectif: Réparer définitivement la chaîne audio→callbacks")
        self.log("Améliorations: Signature flexible + seuil audio abaissé")
        self.log("-" * 60)
        
        self.root.mainloop()


def main():
    try:
        app = EngineV5CallbackFixV2()
        app.run()
    except Exception as e:
        print(f"Erreur: {e}")


if __name__ == "__main__":
    main() 