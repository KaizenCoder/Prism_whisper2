#!/usr/bin/env python3
"""
Test Engine V5 SuperWhisper2 - FOCUS 100% ENGINE V5
Script laser-focalisé sur l'Engine V5 pour diagnostiquer et corriger le problème des callbacks
RTX 3090 24GB + Engine V5 Phase 3 + Rode NT-USB
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
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


class EngineV5FocusTest:
    def __init__(self):
        self.engine = None
        self.listening = False
        self.callback_count = 0
        self.start_time = None
        self.rode_device_id = None
        self.engine_state = {}
        
        # Interface minimaliste focalisée
        self.root = tk.Tk()
        self.root.title("Engine V5 Focus Test - Diagnostic Callbacks")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0d1117")
        
        # Style colors
        self.colors = {
            'bg': '#0d1117',
            'bg_secondary': '#161b22',
            'text': '#c9d1d9',
            'accent': '#58a6ff',
            'success': '#3fb950',
            'warning': '#d29922',
            'error': '#f85149'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Interface ultra-focalisée sur Engine V5"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=60)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="🎯 ENGINE V5 FOCUS TEST - Diagnostic Callbacks",
                              font=("Segoe UI", 20, "bold"),
                              bg=self.colors['bg'], 
                              fg=self.colors['accent'])
        title_label.pack(pady=15)
        
        # Control buttons
        btn_frame = tk.Frame(self.root, bg=self.colors['bg'])
        btn_frame.pack(pady=10)
        
        self.init_btn = tk.Button(btn_frame,
                                 text="🚀 INIT ENGINE V5",
                                 command=self.init_engine,
                                 bg=self.colors['accent'], 
                                 fg="white",
                                 font=("Segoe UI", 12, "bold"),
                                 width=18, height=2)
        self.init_btn.pack(side="left", padx=10)
        
        self.test_btn = tk.Button(btn_frame,
                                 text="🔍 TEST CALLBACKS",
                                 command=self.test_callbacks,
                                 bg=self.colors['success'], 
                                 fg="white",
                                 font=("Segoe UI", 12, "bold"),
                                 width=18, height=2,
                                 state="disabled")
        self.test_btn.pack(side="left", padx=10)
        
        self.fix_btn = tk.Button(btn_frame,
                                text="🔧 FIX ENGINE V5",
                                command=self.fix_engine_v5,
                                bg=self.colors['warning'], 
                                fg="white",
                                font=("Segoe UI", 12, "bold"),
                                width=18, height=2,
                                state="disabled")
        self.fix_btn.pack(side="left", padx=10)
        
        # Status
        status_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'])
        status_frame.pack(fill="x", pady=10)
        
        self.status_label = tk.Label(status_frame,
                                    text="🔴 Status: Engine V5 non initialisé",
                                    font=("Segoe UI", 12, "bold"),
                                    bg=self.colors['bg_secondary'], 
                                    fg=self.colors['error'])
        self.status_label.pack(side="left", padx=20, pady=8)
        
        self.callback_label = tk.Label(status_frame,
                                      text="Callbacks: 0/0",
                                      font=("Segoe UI", 12, "bold"),
                                      bg=self.colors['bg_secondary'], 
                                      fg=self.colors['text'])
        self.callback_label.pack(side="right", padx=20, pady=8)
        
        # Log area
        log_label = tk.Label(self.root,
                            text="📋 DIAGNOSTIC LOG ENGINE V5",
                            font=("Segoe UI", 12, "bold"),
                            bg=self.colors['bg'], 
                            fg=self.colors['accent'])
        log_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        log_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'])
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                 font=("Consolas", 10),
                                                 bg=self.colors['bg_secondary'], 
                                                 fg=self.colors['text'],
                                                 wrap=tk.WORD,
                                                 insertbackground=self.colors['accent'],
                                                 selectbackground=self.colors['accent'],
                                                 selectforeground="white",
                                                 padx=10, pady=10)
        self.log_text.pack(fill="both", expand=True, padx=2, pady=2)
        
    def log_message(self, message, color=None):
        """Log avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        full_msg = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, full_msg)
        if color:
            # Add color highlighting if needed
            pass
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def detect_rode_microphone(self):
        """Détection automatique Rode NT-USB"""
        self.log_message("🔍 Recherche microphone Rode NT-USB...")
        
        try:
            devices = sd.query_devices()
            rode_keywords = ['rode', 'nt-usb', 'usb microphone', 'microphone usb']
            
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                if any(keyword in device_name for keyword in rode_keywords):
                    if device['max_input_channels'] > 0:
                        self.rode_device_id = i
                        self.log_message(f"✅ Rode trouvé: Device {i} - {device['name']}")
                        self.log_message(f"   📊 Sample Rate: {device['default_samplerate']}Hz")
                        self.log_message(f"   🎵 Channels: {device['max_input_channels']}")
                        return True
            
            self.log_message("❌ Rode NT-USB non trouvé!")
            return False
            
        except Exception as e:
            self.log_message(f"❌ Erreur détection: {e}")
            return False
    
    def init_engine(self):
        """Initialisation Engine V5 uniquement"""
        self.log_message("="*80)
        self.log_message("🚀 INITIALISATION ENGINE V5 PHASE 3")
        self.log_message("="*80)
        
        self.status_label.config(text="🟡 Status: Initialisation...", fg=self.colors['warning'])
        self.init_btn.config(state="disabled")
        
        def init_thread():
            try:
                # Step 1: Rode detection
                if not self.detect_rode_microphone():
                    raise Exception("Rode NT-USB non détecté")
                
                # Step 2: Configure sounddevice globalement
                self.log_message("🔧 Configuration sounddevice...")
                sd.default.device[0] = self.rode_device_id
                sd.default.samplerate = 16000
                sd.default.channels = 1
                self.log_message(f"✅ Sounddevice → Device {self.rode_device_id}, 16kHz, Mono")
                
                # Step 3: Import Engine V5
                self.log_message("📦 Import SuperWhisper2 Engine V5...")
                from src.core.whisper_engine_v5 import SuperWhisper2EngineV5
                
                # Step 4: Create Engine V5
                self.log_message("⚙️ Création instance Engine V5...")
                self.engine = SuperWhisper2EngineV5()
                
                # Step 5: Start Engine V5
                self.log_message("🎮 Démarrage Engine V5...")
                success = self.engine.start_engine()
                
                if not success:
                    raise Exception("Engine V5 start_engine() failed")
                    
                self.log_message("✅ ENGINE V5 INITIALISÉ AVEC SUCCÈS!")
                
                # Get status
                status = self.engine.get_phase3_status()
                self.log_message(f"📊 Optimizations: {status['optimizations_count']}/{status['total_optimizations']}")
                self.log_message(f"💾 VRAM Cache: {status['gpu_status']['vram_cache_gb']:.1f}GB")
                self.log_message(f"🔥 CUDA Streams: {status['gpu_status']['cuda_streams']}")
                
                # Diagnostic complet Architecture Engine V5
                self.log_message("🏗️ ARCHITECTURE ENGINE V5:")
                self.analyze_engine_architecture()
                
                self.status_label.config(text="🟢 Status: Engine V5 Ready", fg=self.colors['success'])
                self.test_btn.config(state="normal")
                self.fix_btn.config(state="normal")
                
            except Exception as e:
                error_msg = f"❌ ERREUR INIT: {str(e)}"
                self.log_message(error_msg)
                self.status_label.config(text="🔴 Status: Échec init", fg=self.colors['error'])
                self.init_btn.config(state="normal")
                messagebox.showerror("Erreur", error_msg)
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def analyze_engine_architecture(self):
        """Analyse complète de l'architecture Engine V5"""
        # 1. Top-level components
        self.log_message("🔍 Composants principaux:")
        main_components = [
            'audio_streamer', 'streaming_manager', 'model_selector', 
            'transcriber', 'optimizer', 'gpu_manager'
        ]
        
        for comp in main_components:
            if hasattr(self.engine, comp):
                obj = getattr(self.engine, comp)
                if obj:
                    self.log_message(f"   ✅ {comp}: {type(obj).__name__}")
                    self.engine_state[comp] = obj
                else:
                    self.log_message(f"   ⚪ {comp}: None")
            else:
                self.log_message(f"   ❌ {comp}: Missing")
        
        # 2. StreamingManager deep dive
        if 'streaming_manager' in self.engine_state:
            self.log_message("🎧 STREAMING MANAGER ANALYSIS:")
            manager = self.engine_state['streaming_manager']
            self.analyze_streaming_manager(manager)
        
        # 3. AudioStreamer deep dive
        if 'audio_streamer' in self.engine_state:
            self.log_message("🎵 AUDIO STREAMER ANALYSIS:")
            streamer = self.engine_state['audio_streamer']
            self.analyze_audio_streamer(streamer)
    
    def analyze_streaming_manager(self, manager):
        """Analyse détaillée du StreamingManager"""
        # Get all methods and attributes
        attrs = [attr for attr in dir(manager) if not attr.startswith('_')]
        methods = []
        properties = []
        
        for attr in attrs:
            try:
                obj = getattr(manager, attr)
                if callable(obj):
                    methods.append(attr)
                else:
                    properties.append((attr, obj))
            except:
                pass
        
        self.log_message(f"   📋 Methods disponibles: {len(methods)}")
        for method in methods:
            self.log_message(f"     • {method}()")
        
        self.log_message(f"   📊 Propriétés: {len(properties)}")
        for prop, value in properties:
            self.log_message(f"     • {prop} = {value}")
        
        # Test critical states
        critical_states = ['running', 'active', 'is_streaming', 'stream_counter']
        self.log_message("   🎯 États critiques:")
        for state in critical_states:
            if hasattr(manager, state):
                try:
                    value = getattr(manager, state)
                    if callable(value):
                        value = value()
                    self.log_message(f"     ✅ {state} = {value}")
                except Exception as e:
                    self.log_message(f"     ❌ {state} error: {e}")
    
    def analyze_audio_streamer(self, streamer):
        """Analyse détaillée de l'AudioStreamer"""
        # Get configuration
        config_attrs = ['device_id', 'sample_rate', 'chunk_size', 'format', 'channels']
        self.log_message("   ⚙️ Configuration:")
        for attr in config_attrs:
            if hasattr(streamer, attr):
                try:
                    value = getattr(streamer, attr)
                    self.log_message(f"     • {attr} = {value}")
                except:
                    pass
        
        # Get state
        state_attrs = ['is_recording', 'is_active', 'running', 'active']
        self.log_message("   📊 État:")
        for attr in state_attrs:
            if hasattr(streamer, attr):
                try:
                    value = getattr(streamer, attr)
                    if callable(value):
                        value = value()
                    self.log_message(f"     • {attr} = {value}")
                except:
                    pass
    
    def test_callbacks(self):
        """Test des callbacks Engine V5"""
        if not self.engine:
            messagebox.showerror("Erreur", "Engine V5 non initialisé!")
            return
            
        self.log_message("="*80)
        self.log_message("🔍 TEST CALLBACKS ENGINE V5")
        self.log_message("="*80)
        
        self.listening = True
        self.callback_count = 0
        self.start_time = time.time()
        
        # Configure callback avec diagnostic
        def engine_callback(text: str):
            """Callback principal Engine V5"""
            self.callback_count += 1
            elapsed = time.time() - self.start_time
            
            self.callback_label.config(text=f"Callbacks: {self.callback_count}/∞")
            self.log_message(f"🎯 CALLBACK #{self.callback_count} [{elapsed:.1f}s]: '{text}'")
            
            # Debug callback source
            import inspect
            frame = inspect.currentframe()
            caller_info = inspect.getframeinfo(frame.f_back)
            self.log_message(f"   📍 Called from: {caller_info.filename}:{caller_info.lineno}")
        
        try:
            # Set callback
            self.log_message("🔧 Configuration callback...")
            self.engine.set_transcription_callback(engine_callback)
            self.log_message("✅ Callback configuré")
            
            # 🎯 ACTIVATION FORCÉE ENGINE V5
            self.log_message("🚀 ACTIVATION FORCÉE ENGINE V5...")
            self.force_activate_engine_v5()
            
            # Start monitoring
            self.log_message("👁️ Démarrage surveillance callbacks...")
            self.start_callback_monitoring()
            
            self.status_label.config(text="🟢 Status: Test en cours", fg=self.colors['success'])
            
        except Exception as e:
            self.log_message(f"❌ Erreur test callbacks: {e}")
    
    def force_activate_engine_v5(self):
        """Activation forcée de tous les composants Engine V5"""
        # 1. StreamingManager activation
        if 'streaming_manager' in self.engine_state:
            manager = self.engine_state['streaming_manager']
            self.log_message("🎧 Activation StreamingManager...")
            
            # Try all activation methods
            activation_methods = [
                'start', 'start_streaming', 'begin', 'activate', 'enable',
                'listen', 'record', 'capture'
            ]
            
            for method_name in activation_methods:
                if hasattr(manager, method_name):
                    try:
                        method = getattr(manager, method_name)
                        if callable(method):
                            result = method()
                            self.log_message(f"   ✅ {method_name}() → {result}")
                            break
                    except Exception as e:
                        self.log_message(f"   ⚠️ {method_name}() error: {e}")
        
        # 2. AudioStreamer activation
        if 'audio_streamer' in self.engine_state:
            streamer = self.engine_state['audio_streamer']
            self.log_message("🎵 Activation AudioStreamer...")
            
            # Force device configuration
            device_methods = ['set_device', 'set_device_id', 'configure_device']
            for method_name in device_methods:
                if hasattr(streamer, method_name):
                    try:
                        method = getattr(streamer, method_name)
                        if callable(method):
                            result = method(self.rode_device_id)
                            self.log_message(f"   ✅ {method_name}({self.rode_device_id}) → {result}")
                            break
                    except Exception as e:
                        self.log_message(f"   ⚠️ {method_name}() error: {e}")
            
            # Start streaming
            start_methods = ['start', 'begin_recording', 'start_capture', 'activate']
            for method_name in start_methods:
                if hasattr(streamer, method_name):
                    try:
                        method = getattr(streamer, method_name)
                        if callable(method):
                            result = method()
                            self.log_message(f"   ✅ {method_name}() → {result}")
                            break
                    except Exception as e:
                        self.log_message(f"   ⚠️ {method_name}() error: {e}")
        
        # 3. Engine-level activation
        engine_methods = [
            'start_listening', 'begin_recording', 'activate_audio', 
            'enable_streaming', 'force_start'
        ]
        
        self.log_message("🎮 Activation Engine V5 global...")
        for method_name in engine_methods:
            if hasattr(self.engine, method_name):
                try:
                    method = getattr(self.engine, method_name)
                    if callable(method):
                        result = method()
                        self.log_message(f"   ✅ {method_name}() → {result}")
                except Exception as e:
                    self.log_message(f"   ⚠️ {method_name}() error: {e}")
    
    def start_callback_monitoring(self):
        """Surveillance continue des callbacks"""
        def monitor_thread():
            self.log_message("👁️ Surveillance callbacks démarrée...")
            
            # Wait for callbacks
            for i in range(30):  # 30 seconds
                time.sleep(1)
                
                if not self.listening:
                    break
                
                elapsed = time.time() - self.start_time
                self.log_message(f"⏱️ [{elapsed:.0f}s] Callbacks reçus: {self.callback_count}")
                
                # Check engine state every 5 seconds
                if i % 5 == 0:
                    self.check_engine_state()
                
                # If no callbacks after 10s, try manual trigger
                if i == 10 and self.callback_count == 0:
                    self.log_message("🔧 Pas de callbacks → Test manuel...")
                    self.trigger_manual_callback()
            
            self.log_message(f"📊 Test terminé: {self.callback_count} callbacks en 30s")
            
        threading.Thread(target=monitor_thread, daemon=True).start()
    
    def check_engine_state(self):
        """Vérification état Engine V5"""
        if 'streaming_manager' in self.engine_state:
            manager = self.engine_state['streaming_manager']
            
            # Check if still running
            if hasattr(manager, 'running'):
                running = getattr(manager, 'running')
                self.log_message(f"   📊 StreamingManager.running = {running}")
            
            # Check stream counter
            if hasattr(manager, 'stream_counter'):
                counter = getattr(manager, 'stream_counter')
                self.log_message(f"   📊 StreamingManager.stream_counter = {counter}")
    
    def trigger_manual_callback(self):
        """Déclenchement manuel d'un callback test"""
        try:
            # Create test audio chunk
            test_audio = np.zeros(16000 * 2, dtype=np.float32)  # 2 seconds silence
            
            # Try to trigger manually via StreamingManager
            if 'streaming_manager' in self.engine_state:
                manager = self.engine_state['streaming_manager']
                
                if hasattr(manager, 'on_audio_ready'):
                    self.log_message("🧪 Test manuel on_audio_ready()...")
                    result = manager.on_audio_ready(test_audio)
                    self.log_message(f"   → Résultat: {result}")
                
                # Try transcriber callback directly
                if hasattr(manager, 'transcriber_callback'):
                    self.log_message("🧪 Test manuel transcriber_callback()...")
                    result = manager.transcriber_callback("Test manuel Engine V5")
                    self.log_message(f"   → Résultat: {result}")
                    
        except Exception as e:
            self.log_message(f"⚠️ Erreur test manuel: {e}")
    
    def fix_engine_v5(self):
        """Correction AGRESSIVE Engine V5 - Focus callbacks"""
        self.log_message("="*80)
        self.log_message("🔧 CORRECTION AGRESSIVE ENGINE V5")
        self.log_message("="*80)
        
        # 1. Diagnostic chain audio→callbacks
        self.log_message("🔍 DIAGNOSTIC CHAÎNE AUDIO→CALLBACKS:")
        self.diagnose_audio_callback_chain()
        
        # 2. Force audio pipeline reconnection
        self.log_message("🔗 Reconnexion pipeline audio...")
        self.reconnect_audio_pipeline()
        
        # 3. Force streaming with direct audio injection
        self.log_message("💉 Injection audio directe...")
        self.inject_direct_audio()
        
        # 4. Bypass internal audio and use external feed
        self.log_message("🚀 Contournement audio interne...")
        self.bypass_internal_audio()
        
        # 5. Test immediate callback
        self.log_message("🧪 Test callback immédiat...")
        self.trigger_manual_callback()
        
        self.log_message("✅ Correction agressive terminée")
    
    def diagnose_audio_callback_chain(self):
        """Diagnostic complet de la chaîne audio→callbacks"""
        # 1. Verify callback is properly set
        self.log_message("🔗 Vérification callback:")
        if hasattr(self.engine, '_transcription_callback'):
            callback = getattr(self.engine, '_transcription_callback')
            self.log_message(f"   ✅ Callback engine: {callback}")
        else:
            self.log_message("   ❌ Pas de callback engine")
        
        # 2. Verify StreamingManager has callback
        if 'streaming_manager' in self.engine_state:
            manager = self.engine_state['streaming_manager']
            callback_attrs = ['transcriber_callback', 'callback', '_callback', 'on_transcription']
            
            for attr in callback_attrs:
                if hasattr(manager, attr):
                    callback = getattr(manager, attr)
                    self.log_message(f"   ✅ StreamingManager.{attr}: {callback}")
        
        # 3. Verify audio flow
        self.log_message("🎵 Vérification flux audio:")
        
        # Test direct audio capture
        try:
            # Capture 1 second of audio from Rode
            self.log_message("   🎤 Test capture audio Rode...")
            audio_data = sd.rec(int(1 * 16000), samplerate=16000, channels=1, device=self.rode_device_id)
            sd.wait()
            
            # Check audio level
            rms_level = np.sqrt(np.mean(audio_data**2))
            max_level = np.max(np.abs(audio_data))
            
            self.log_message(f"   📊 RMS: {rms_level:.6f}, Max: {max_level:.6f}")
            
            if max_level > 0.001:  # Audio detected
                self.log_message("   ✅ Audio Rode OK - Signal détecté")
                
                # Try to inject this audio into Engine V5
                self.inject_audio_to_engine(audio_data)
            else:
                self.log_message("   ⚠️ Pas de signal audio détecté")
                
        except Exception as e:
            self.log_message(f"   ❌ Erreur test audio: {e}")
    
    def inject_audio_to_engine(self, audio_data):
        """Injection audio directe dans Engine V5"""
        self.log_message("💉 Injection audio dans Engine V5...")
        
        # Ensure correct format
        if audio_data.ndim > 1:
            audio_data = audio_data.flatten()
        
        audio_data = audio_data.astype(np.float32)
        
        # Try multiple injection points
        injection_points = []
        
        # 1. StreamingManager.on_audio_ready
        if 'streaming_manager' in self.engine_state:
            manager = self.engine_state['streaming_manager']
            if hasattr(manager, 'on_audio_ready'):
                injection_points.append(('StreamingManager.on_audio_ready', manager.on_audio_ready))
        
        # 2. AudioStreamer methods
        if 'audio_streamer' in self.engine_state:
            streamer = self.engine_state['audio_streamer']
            audio_methods = ['process_audio', 'on_audio', 'handle_audio', 'feed_audio']
            for method_name in audio_methods:
                if hasattr(streamer, method_name):
                    method = getattr(streamer, method_name)
                    if callable(method):
                        injection_points.append((f'AudioStreamer.{method_name}', method))
        
        # 3. Engine-level injection
        engine_methods = ['process_audio', 'feed_audio', 'on_audio_data']
        for method_name in engine_methods:
            if hasattr(self.engine, method_name):
                method = getattr(self.engine, method_name)
                if callable(method):
                    injection_points.append((f'Engine.{method_name}', method))
        
        # Test each injection point
        for name, method in injection_points:
            try:
                self.log_message(f"   🎯 Test {name}...")
                result = method(audio_data)
                self.log_message(f"   ✅ {name} → {result}")
                
                # Wait a bit to see if callback triggers
                time.sleep(0.5)
                
            except Exception as e:
                self.log_message(f"   ❌ {name} error: {e}")
    
    def inject_direct_audio(self):
        """Injection audio en temps réel dans Engine V5"""
        self.log_message("🔄 Démarrage injection audio temps réel...")
        
        def audio_injection_thread():
            try:
                # Stream audio directly to Engine V5
                chunk_size = 1024
                sample_rate = 16000
                
                def audio_callback(indata, frames, time, status):
                    if status:
                        self.log_message(f"⚠️ Audio callback status: {status}")
                    
                    # Convert to correct format
                    audio_chunk = indata[:, 0].astype(np.float32)  # Mono
                    
                    # Inject into Engine V5
                    if 'streaming_manager' in self.engine_state:
                        manager = self.engine_state['streaming_manager']
                        if hasattr(manager, 'on_audio_ready'):
                            try:
                                manager.on_audio_ready(audio_chunk)
                            except Exception as e:
                                pass  # Silent fail for real-time
                
                # Start audio stream
                self.log_message("🎵 Démarrage stream audio direct...")
                with sd.InputStream(callback=audio_callback,
                                   device=self.rode_device_id,
                                   channels=1,
                                   samplerate=sample_rate,
                                   blocksize=chunk_size):
                    
                    self.log_message("✅ Stream audio direct actif")
                    
                    # Run for 10 seconds
                    for i in range(100):
                        time.sleep(0.1)
                        if not self.listening:
                            break
                
                self.log_message("⏹️ Stream audio direct arrêté")
                
            except Exception as e:
                self.log_message(f"❌ Erreur injection audio: {e}")
        
        threading.Thread(target=audio_injection_thread, daemon=True).start()
    
    def bypass_internal_audio(self):
        """Contournement complet du système audio interne"""
        self.log_message("🚀 CONTOURNEMENT SYSTÈME AUDIO INTERNE")
        
        # Create external audio→transcription pipeline
        def external_pipeline():
            try:
                self.log_message("🔧 Pipeline externe audio→transcription...")
                
                # 1. Capture audio chunks
                chunk_duration = 3.0  # seconds
                sample_rate = 16000
                
                for i in range(10):  # 10 chunks = 30 seconds
                    if not self.listening:
                        break
                    
                    self.log_message(f"📦 Capture chunk {i+1}/10...")
                    
                    # Capture audio
                    audio_chunk = sd.rec(int(chunk_duration * sample_rate), 
                                       samplerate=sample_rate, 
                                       channels=1, 
                                       device=self.rode_device_id)
                    sd.wait()
                    
                    # Check audio level
                    rms_level = np.sqrt(np.mean(audio_chunk**2))
                    
                    if rms_level > 0.001:  # Audio detected
                        self.log_message(f"   📊 Audio détecté (RMS: {rms_level:.6f})")
                        
                        # Force transcription via Engine V5
                        self.force_transcription_engine_v5(audio_chunk.flatten())
                    else:
                        self.log_message(f"   ⚪ Silence (RMS: {rms_level:.6f})")
                
                self.log_message("✅ Pipeline externe terminé")
                
            except Exception as e:
                self.log_message(f"❌ Erreur pipeline externe: {e}")
        
        threading.Thread(target=external_pipeline, daemon=True).start()
    
    def force_transcription_engine_v5(self, audio_data):
        """Force transcription via Engine V5 en bypassing audio stream"""
        try:
            # Try to access transcription engine directly
            if hasattr(self.engine, 'transcriber'):
                transcriber = self.engine.transcriber
                self.log_message("   🎯 Accès transcriber direct...")
                
                # Try transcribe method
                if hasattr(transcriber, 'transcribe'):
                    result = transcriber.transcribe(audio_data)
                    self.log_message(f"   📝 Transcription: {result}")
                    
                    # Trigger callback manually
                    if hasattr(self.engine, '_transcription_callback'):
                        callback = self.engine._transcription_callback
                        if callback:
                            callback(str(result))
                            self.log_message("   ✅ Callback déclenché manuellement")
            
            # Try model_selector transcription
            if hasattr(self.engine, 'model_selector'):
                model_selector = self.engine.model_selector
                if hasattr(model_selector, 'transcribe'):
                    result = model_selector.transcribe(audio_data)
                    self.log_message(f"   📝 ModelSelector transcription: {result}")
                    
                    # Trigger callback
                    if hasattr(self.engine, '_transcription_callback'):
                        callback = self.engine._transcription_callback
                        if callback:
                            callback(str(result))
            
        except Exception as e:
            self.log_message(f"   ❌ Force transcription error: {e}")
    
    def reconnect_audio_pipeline(self):
        """Reconnexion du pipeline audio"""
        try:
            # Re-configure global sounddevice
            sd.default.device[0] = self.rode_device_id
            sd.default.samplerate = 16000
            sd.default.channels = 1
            
            # Force device on all components
            if 'audio_streamer' in self.engine_state:
                streamer = self.engine_state['audio_streamer']
                
                # Set device on streamer
                if hasattr(streamer, 'set_device_id'):
                    streamer.set_device_id(self.rode_device_id)
                    self.log_message(f"   ✅ AudioStreamer device → {self.rode_device_id}")
                
                # Restart streamer
                if hasattr(streamer, 'restart'):
                    streamer.restart()
                    self.log_message("   ✅ AudioStreamer restarted")
            
            self.log_message("✅ Pipeline audio reconnecté")
            
        except Exception as e:
            self.log_message(f"⚠️ Erreur reconnexion: {e}")
    
    def run(self):
        """Lancement de l'interface"""
        self.log_message("🎯 ENGINE V5 FOCUS TEST - Diagnostic des callbacks")
        self.log_message("Objectif: Faire fonctionner les callbacks Engine V5 à 100%")
        self.log_message("-" * 60)
        
        self.root.mainloop()


def main():
    """Point d'entrée principal"""
    try:
        app = EngineV5FocusTest()
        app.run()
    except Exception as e:
        print(f"Erreur fatale: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 