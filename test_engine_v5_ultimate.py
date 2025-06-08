#!/usr/bin/env python3
"""
Test Engine V5 SuperWhisper2 + Microphone Rode NT-USB
Script de test ultime avec détection automatique Rode et métriques complètes
RTX 3090 24GB + Engine V5 Phase 3 + Rode NT-USB
"""

import os
import sys
import time
import threading
import queue
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
import re
import difflib
from collections import Counter
import sounddevice as sd
import numpy as np
import json

# Configuration RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # RTX 3090 24GB
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajouter src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Texte de validation de référence
TEXTE_REFERENCE = """Bonjour, ceci est un test de validation pour SuperWhisper2. Je vais maintenant énoncer plusieurs phrases de complexité croissante pour évaluer la précision de transcription.
Premièrement, des mots simples : chat, chien, maison, voiture, ordinateur, téléphone.
Deuxièmement, des phrases courtes : Il fait beau aujourd'hui. Le café est délicieux. J'aime la musique classique.
Troisièmement, des phrases plus complexes : L'intelligence artificielle transforme notre manière de travailler et de communiquer dans le monde moderne.
Quatrièmement, des termes techniques : algorithme, machine learning, GPU RTX 3090, faster-whisper, quantification INT8, latence de transcription.
Cinquièmement, des nombres et dates : vingt-trois, quarante-sept, mille neuf cent quatre-vingt-quinze, le quinze janvier deux mille vingt-quatre.
Sixièmement, des mots difficiles : chrysanthème, anticonstitutionnellement, prestidigitateur, kakémono, yaourt.
Septièmement, une phrase longue et complexe : L'optimisation des performances de transcription vocale nécessite une approche méthodique combinant la sélection appropriée des modèles, l'ajustement des paramètres de traitement, et l'implémentation d'algorithmes de post-traitement pour améliorer la qualité du résultat final.
Fin du test de validation."""


class UltimateEngineV5Test:
    def __init__(self):
        self.engine = None
        self.listening = False
        self.transcription_complete = ""
        self.transcription_segments = []
        self.start_time = None
        self.rode_device_id = None
        self.callback_count = 0
        self.audio_queue = queue.Queue()
        self.bypass_mode = False
        
        # Interface GitHub-style
        self.root = tk.Tk()
        self.root.title("Test Engine V5 Ultimate - Rode NT-USB")
        self.root.geometry("1400x850")
        self.root.configure(bg="#0d1117")
        
        # Style colors
        self.colors = {
            'bg': '#0d1117',
            'bg_secondary': '#161b22',
            'border': '#30363d',
            'text': '#c9d1d9',
            'text_secondary': '#8b949e',
            'accent': '#58a6ff',
            'success': '#3fb950',
            'warning': '#d29922',
            'error': '#f85149'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Interface utilisateur GitHub-style"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="🎤 Test Engine V5 Ultimate - SuperWhisper2",
                              font=("Segoe UI", 24, "bold"),
                              bg=self.colors['bg'], 
                              fg=self.colors['text'])
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(header_frame,
                                 text="RTX 3090 • Phase 3 INT8 • Rode NT-USB • Transcription temps réel",
                                 font=("Segoe UI", 12),
                                 bg=self.colors['bg'], 
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack()
        
        # Control buttons
        btn_frame = tk.Frame(self.root, bg=self.colors['bg'])
        btn_frame.pack(pady=10)
        
        self.init_btn = tk.Button(btn_frame,
                                 text="🔧 INIT ENGINE + RODE",
                                 command=self.init_engine_rode,
                                 bg=self.colors['accent'], 
                                 fg="white",
                                 font=("Segoe UI", 11, "bold"),
                                 width=20, height=2,
                                 relief="flat",
                                 cursor="hand2")
        self.init_btn.pack(side="left", padx=5)
        
        self.start_btn = tk.Button(btn_frame,
                                  text="▶️ START TEST",
                                  command=self.start_test,
                                  bg=self.colors['success'], 
                                  fg="white",
                                  font=("Segoe UI", 11, "bold"),
                                  width=20, height=2,
                                  state="disabled",
                                  relief="flat",
                                  cursor="hand2")
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(btn_frame,
                                 text="⏹️ STOP TEST", 
                                 command=self.stop_test,
                                 bg=self.colors['error'], 
                                 fg="white",
                                 font=("Segoe UI", 11, "bold"),
                                 width=20, height=2,
                                 state="disabled",
                                 relief="flat",
                                 cursor="hand2")
        self.stop_btn.pack(side="left", padx=5)
        
        self.analyze_btn = tk.Button(btn_frame,
                                    text="📊 ANALYZE RESULTS",
                                    command=self.analyze_results,
                                    bg=self.colors['warning'], 
                                    fg="white",
                                    font=("Segoe UI", 11, "bold"),
                                    width=20, height=2,
                                    state="disabled",
                                    relief="flat",
                                    cursor="hand2")
        self.analyze_btn.pack(side="left", padx=5)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=40)
        status_frame.pack(fill="x", pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame,
                                    text="🔴 Status: Not initialized",
                                    font=("Segoe UI", 12, "bold"),
                                    bg=self.colors['bg_secondary'], 
                                    fg=self.colors['error'])
        self.status_label.pack(side="left", padx=20, pady=8)
        
        self.callback_label = tk.Label(status_frame,
                                      text="Callbacks: 0",
                                      font=("Segoe UI", 10),
                                      bg=self.colors['bg_secondary'], 
                                      fg=self.colors['text_secondary'])
        self.callback_label.pack(side="right", padx=20, pady=8)
        
        # Main content area
        content_frame = tk.Frame(self.root, bg=self.colors['bg'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel - Transcription
        left_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        trans_label = tk.Label(left_frame,
                              text="📝 TRANSCRIPTION TEMPS RÉEL",
                              font=("Segoe UI", 11, "bold"),
                              bg=self.colors['bg'], 
                              fg=self.colors['accent'])
        trans_label.pack(anchor="w", pady=(0, 5))
        
        trans_frame = tk.Frame(left_frame, 
                              bg=self.colors['border'], 
                              highlightthickness=1,
                              highlightbackground=self.colors['border'])
        trans_frame.pack(fill="both", expand=True)
        
        self.transcription_text = scrolledtext.ScrolledText(trans_frame,
                                                          font=("Consolas", 11),
                                                          bg=self.colors['bg_secondary'], 
                                                          fg=self.colors['text'],
                                                          wrap=tk.WORD,
                                                          insertbackground=self.colors['accent'],
                                                          selectbackground=self.colors['accent'],
                                                          selectforeground="white",
                                                          relief="flat",
                                                          padx=10, pady=10)
        self.transcription_text.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Right panel - Stats
        right_frame = tk.Frame(content_frame, bg=self.colors['bg'], width=400)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)
        
        stats_label = tk.Label(right_frame,
                              text="📊 STATISTIQUES LIVE",
                              font=("Segoe UI", 11, "bold"),
                              bg=self.colors['bg'], 
                              fg=self.colors['accent'])
        stats_label.pack(anchor="w", pady=(0, 5))
        
        stats_frame = tk.Frame(right_frame, 
                              bg=self.colors['border'], 
                              highlightthickness=1,
                              highlightbackground=self.colors['border'])
        stats_frame.pack(fill="both", expand=True)
        
        self.stats_text = tk.Text(stats_frame,
                                 font=("Consolas", 10),
                                 bg=self.colors['bg_secondary'], 
                                 fg=self.colors['text'],
                                 height=25,
                                 relief="flat",
                                 padx=10, pady=10)
        self.stats_text.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Initial content
        self.show_instructions()
        
    def show_instructions(self):
        """Affiche les instructions initiales"""
        instructions = f"""=== INSTRUCTIONS TEST ENGINE V5 ULTIMATE ===

1. 🔧 INIT ENGINE + RODE
   → Détecte automatiquement le Rode NT-USB
   → Initialise Engine V5 Phase 3
   → Configure les optimisations RTX 3090

2. ▶️ START TEST
   → Active la transcription temps réel
   → Affiche les callbacks reçus
   → Mode bypass disponible si nécessaire

3. 📖 LISEZ LE TEXTE DE VALIDATION
   → Parlez clairement dans le microphone
   → Attendez les transcriptions

4. ⏹️ STOP TEST
   → Arrête l'enregistrement
   → Prépare l'analyse

5. 📊 ANALYZE RESULTS
   → Calcule WER et similarité
   → Analyse par complexité
   → Sauvegarde les résultats

=== TEXTE DE VALIDATION ===
{TEXTE_REFERENCE}

=== DEBUGGING ===
Si aucune transcription n'apparaît :
- Vérifiez le niveau audio du Rode
- Le mode bypass sera proposé automatiquement
- Les logs détaillés aideront au diagnostic
"""
        self.log_message(instructions)
        
    def log_message(self, message, color=None):
        """Affiche message avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        full_message = f"[{timestamp}] {message}"
        
        # Console
        print(full_message)
        
        # UI
        self.transcription_text.insert(tk.END, full_message + "\n")
        self.transcription_text.see(tk.END)
        self.root.update()
        
    def update_stats(self):
        """Met à jour les statistiques en temps réel"""
        stats = []
        
        # Device info
        stats.append("=== DEVICE INFO ===")
        stats.append(f"Rode Device ID: {self.rode_device_id}")
        stats.append(f"Bypass Mode: {'ON' if self.bypass_mode else 'OFF'}")
        stats.append("")
        
        # Transcription stats
        stats.append("=== TRANSCRIPTION ===")
        stats.append(f"Segments: {len(self.transcription_segments)}")
        stats.append(f"Total chars: {len(self.transcription_complete)}")
        stats.append(f"Callbacks: {self.callback_count}")
        
        if self.start_time:
            elapsed = time.time() - self.start_time
            stats.append(f"Elapsed: {elapsed:.1f}s")
            if len(self.transcription_complete) > 0:
                chars_per_sec = len(self.transcription_complete) / elapsed
                stats.append(f"Speed: {chars_per_sec:.1f} chars/s")
        
        stats.append("")
        
        # Engine status
        if self.engine:
            stats.append("=== ENGINE V5 ===")
            try:
                status = self.engine.get_phase3_status()
                stats.append(f"Optimizations: {status['optimizations_count']}/{status['total_optimizations']}")
                stats.append(f"VRAM Cache: {status['gpu_status']['vram_cache_gb']:.1f}GB")
                stats.append(f"CUDA Streams: {status['gpu_status']['cuda_streams']}")
                
                # Optimizations details
                stats.append("\nOptimizations:")
                for opt_name, enabled in status['optimizations'].items():
                    icon = "✅" if enabled else "❌"
                    stats.append(f"{icon} {opt_name}")
            except:
                stats.append("Status unavailable")
        
        # Update UI
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "\n".join(stats))
        
    def detect_rode_microphone(self):
        """Détecte automatiquement le microphone Rode"""
        try:
            self.log_message("🔍 Scanning for Rode microphone...")
            
            devices = sd.query_devices()
            self.log_message(f"Found {len(devices)} audio devices")
            
            # Keywords for Rode detection
            rode_keywords = ['rode', 'nt-usb', 'nt usb', 'procaster', 'podmic', 'podcaster']
            
            # First pass: exact Rode match
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    device_name = device['name'].lower()
                    
                    for keyword in rode_keywords:
                        if keyword in device_name:
                            self.rode_device_id = i
                            self.log_message(f"✅ RODE DETECTED: {device['name']}")
                            self.log_message(f"   Device ID: {i}")
                            self.log_message(f"   Sample Rate: {device['default_samplerate']} Hz")
                            self.log_message(f"   Channels: {device['max_input_channels']}")
                            return True
            
            # Second pass: USB microphones
            self.log_message("⚠️ No Rode found, looking for USB microphones...")
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    device_name = device['name'].lower()
                    if 'usb' in device_name or 'microphone' in device_name:
                        self.rode_device_id = i
                        self.log_message(f"📎 Using USB device: {device['name']} (ID: {i})")
                        return True
            
            self.log_message("❌ No suitable microphone found")
            return False
            
        except Exception as e:
            self.log_message(f"❌ Error detecting microphone: {str(e)}", self.colors['error'])
            return False
    
    def test_rode_audio_level(self):
        """Test the audio level of the Rode microphone"""
        if self.rode_device_id is None:
            return False
            
        try:
            self.log_message("🎤 Testing Rode audio level (3 seconds)...")
            
            # Get device info to check sample rate
            device_info = sd.query_devices(self.rode_device_id)
            native_samplerate = int(device_info['default_samplerate'])
            self.log_message(f"📊 Device native sample rate: {native_samplerate} Hz")
            
            # Record with native sample rate first
            duration = 3.0
            
            audio_data = sd.rec(int(duration * native_samplerate),
                               samplerate=native_samplerate,
                               channels=1,  # Use mono for consistency
                               device=self.rode_device_id,
                               dtype=np.float32)
            sd.wait()
            
            # Resample to 16kHz if needed
            if native_samplerate != 16000:
                self.log_message(f"🔄 Resampling from {native_samplerate}Hz to 16kHz...")
                # Simple resampling
                resample_ratio = 16000 / native_samplerate
                new_length = int(len(audio_data) * resample_ratio)
                audio_data = np.interp(
                    np.linspace(0, len(audio_data), new_length),
                    np.arange(len(audio_data)),
                    audio_data.flatten()
                ).reshape(-1, 1)
            
            # Calculate levels
            rms_level = np.sqrt(np.mean(audio_data ** 2))
            max_level = np.max(np.abs(audio_data))
            
            self.log_message(f"📊 Audio levels:")
            self.log_message(f"   RMS: {rms_level:.6f}")
            self.log_message(f"   Max: {max_level:.6f}")
            self.log_message(f"   Final sample rate: 16000 Hz")
            
            if rms_level > 0.0001:
                self.log_message("✅ Audio level OK - Microphone is working")
                return True
            else:
                self.log_message("⚠️ Low audio level - Check microphone gain")
                return True  # Continue anyway
                
        except Exception as e:
            self.log_message(f"❌ Audio test error: {str(e)}", self.colors['error'])
            return False
    
    def init_engine_rode(self):
        """Initialize Engine V5 with Rode microphone"""
        self.log_message("="*80)
        self.log_message("🚀 INITIALIZING ENGINE V5 + RODE NT-USB")
        self.log_message("="*80)
        
        self.status_label.config(text="🟡 Status: Initializing...", fg=self.colors['warning'])
        self.init_btn.config(state="disabled")
        
        def init_thread():
            try:
                # Step 1: Detect Rode
                if not self.detect_rode_microphone():
                    raise Exception("Failed to detect Rode microphone")
                
                # Step 2: Test audio
                if not self.test_rode_audio_level():
                    self.log_message("⚠️ Audio test failed but continuing...")
                
                # Step 3: Configure sounddevice
                self.log_message("🔧 Configuring sounddevice for Rode...")
                sd.default.device[0] = self.rode_device_id
                sd.default.samplerate = 16000
                sd.default.channels = 1
                self.log_message(f"✅ Sounddevice configured for device {self.rode_device_id}")
                
                # Step 4: Import and initialize Engine V5
                self.log_message("📦 Importing SuperWhisper2 Engine V5...")
                from src.core.whisper_engine_v5 import SuperWhisper2EngineV5
                
                self.log_message("⚙️ Creating Engine V5 instance...")
                self.engine = SuperWhisper2EngineV5()
                
                # Step 5: Start Engine V5
                self.log_message("🎮 Starting Engine V5 Phase 3...")
                success = self.engine.start_engine()
                
                if success:
                    self.log_message("✅ ENGINE V5 INITIALIZED SUCCESSFULLY!")
                    
                    # Get status
                    status = self.engine.get_phase3_status()
                    self.log_message(f"📊 Optimizations: {status['optimizations_count']}/{status['total_optimizations']}")
                    self.log_message(f"💾 VRAM Cache: {status['gpu_status']['vram_cache_gb']:.1f}GB")
                    self.log_message(f"🔥 CUDA Streams: {status['gpu_status']['cuda_streams']}")
                    
                    # Diagnostic complet des méthodes Engine V5
                    self.log_message("🔍 Engine V5 Methods Diagnostic:")
                    methods_to_check = [
                        'start_listening', 'begin_recording', 'stop_listening', 'stop_recording',
                        'is_listening', 'is_recording', 'get_audio_config', 'set_audio_device',
                        'audio_streamer', 'streaming_manager', 'force_listening', 'restart_audio',
                        'enable_continuous_listening', 'start_streaming', 'activate_microphone'
                    ]
                    
                    available_methods = []
                    for method in methods_to_check:
                        if hasattr(self.engine, method):
                            available_methods.append(method)
                            try:
                                attr = getattr(self.engine, method)
                                if callable(attr):
                                    self.log_message(f"   ✅ {method}() - METHOD")
                                else:
                                    self.log_message(f"   📦 {method} - ATTRIBUTE: {type(attr).__name__}")
                            except Exception as e:
                                self.log_message(f"   ❌ {method} - ERROR: {e}")
                    
                    self.log_message(f"📋 Total Engine V5 methods/attributes found: {len(available_methods)}")
                    
                    # Diagnostic de l'état audio
                    self.log_message("🎤 Audio State Diagnostic:")
                    try:
                        if hasattr(self.engine, 'audio_streamer') and self.engine.audio_streamer:
                            streamer = self.engine.audio_streamer
                            self.log_message(f"   → AudioStreamer type: {type(streamer).__name__}")
                            
                            # Check AudioStreamer methods
                            streamer_methods = ['start', 'stop', 'is_active', 'get_device', 'set_device']
                            for method in streamer_methods:
                                if hasattr(streamer, method):
                                    self.log_message(f"   ✅ AudioStreamer.{method}()")
                        
                        if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
                            manager = self.engine.streaming_manager
                            self.log_message(f"   → StreamingManager type: {type(manager).__name__}")
                            
                            # Check ALL StreamingManager methods and attributes
                            self.log_message("   🔍 StreamingManager full diagnostic:")
                            manager_attrs = dir(manager)
                            public_attrs = [attr for attr in manager_attrs if not attr.startswith('_')]
                            
                            for attr in public_attrs:
                                try:
                                    obj = getattr(manager, attr)
                                    if callable(obj):
                                        self.log_message(f"     ✅ {attr}() - METHOD")
                                    else:
                                        self.log_message(f"     📦 {attr} - ATTRIBUTE: {type(obj).__name__}")
                                except Exception as e:
                                    self.log_message(f"     ❌ {attr} - ERROR: {e}")
                            
                            # Test specific StreamingManager methods
                            test_methods = [
                                'start_streaming', 'stop_streaming', 'is_streaming', 'force_restart',
                                'start', 'begin', 'activate', 'enable', 'listen', 'record', 'capture'
                            ]
                            
                            self.log_message("   🧪 Testing StreamingManager methods:")
                            for method in test_methods:
                                if hasattr(manager, method):
                                    self.log_message(f"     🎯 Found: {method}()")
                                    try:
                                        # Test the method
                                        func = getattr(manager, method)
                                        if callable(func):
                                            # Try to get method signature info
                                            import inspect
                                            sig = inspect.signature(func)
                                            self.log_message(f"       → Signature: {method}{sig}")
                                    except Exception as e:
                                        self.log_message(f"       → Signature error: {e}")
                    except Exception as diag_e:
                        self.log_message(f"⚠️ Audio diagnostic error: {diag_e}")
                    
                    self.status_label.config(text="🟢 Status: Engine V5 Ready", fg=self.colors['success'])
                    self.start_btn.config(state="normal")
                    self.update_stats()
                else:
                    raise Exception("Engine V5 start_engine() failed")
                
            except Exception as e:
                error_msg = f"❌ INIT ERROR: {str(e)}"
                self.log_message(error_msg, self.colors['error'])
                self.status_label.config(text="🔴 Status: Init failed", fg=self.colors['error'])
                self.init_btn.config(state="normal")
                messagebox.showerror("Initialization Error", error_msg)
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def start_test(self):
        """Start transcription test"""
        if not self.engine:
            messagebox.showerror("Error", "Engine V5 not initialized!")
            return
            
        self.log_message("="*80)
        self.log_message("▶️ STARTING TRANSCRIPTION TEST")
        self.log_message("="*80)
        
        # Reset state
        self.transcription_complete = ""
        self.transcription_segments = []
        self.start_time = time.time()
        self.listening = True
        self.callback_count = 0
        self.bypass_mode = False  # Reset bypass mode
        
        # Configure callback
        def on_transcription_callback(text: str):
            """Callback for Engine V5 transcriptions"""
            self.callback_count += 1
            self.callback_label.config(text=f"Callbacks: {self.callback_count}")
            
            self.log_message(f"🔄 Engine V5 Callback #{self.callback_count}: '{text}'")
            
            if not self.listening:
                return
                
            if text and text.strip():
                timestamp = time.time() - self.start_time
                self.transcription_segments.append({
                    'text': text.strip(),
                    'timestamp': timestamp,
                    'source': 'engine_v5'  # Marquer la source
                })
                
                self.transcription_complete += text.strip() + " "
                
                # Display with color
                self.log_message(f"🎯 [ENGINE V5 {timestamp:.1f}s] {text.strip()}", self.colors['success'])
                self.update_stats()
        
        try:
            # Set callback with debug
            self.log_message("🔧 Setting transcription callback...")
            self.engine.set_transcription_callback(on_transcription_callback)
            self.log_message("✅ Callback configured")
            
            # Force start audio streaming avec toutes les méthodes disponibles
            self.log_message("🔍 Activating Engine V5 audio streaming...")
            
            # Essayer toutes les méthodes de démarrage possibles
            streaming_started = False
            
            if hasattr(self.engine, 'start_listening'):
                try:
                    result = self.engine.start_listening()
                    self.log_message(f"✅ start_listening() → {result}")
                    streaming_started = True
                except Exception as e:
                    self.log_message(f"⚠️ start_listening() error: {e}")
            
            if hasattr(self.engine, 'begin_recording'):
                try:
                    result = self.engine.begin_recording()
                    self.log_message(f"✅ begin_recording() → {result}")
                    streaming_started = True
                except Exception as e:
                    self.log_message(f"⚠️ begin_recording() error: {e}")
            
            # Essayer via AudioStreamer
            if hasattr(self.engine, 'audio_streamer') and self.engine.audio_streamer:
                streamer = self.engine.audio_streamer
                if hasattr(streamer, 'start'):
                    try:
                        result = streamer.start()
                        self.log_message(f"✅ AudioStreamer.start() → {result}")
                        streaming_started = True
                    except Exception as e:
                        self.log_message(f"⚠️ AudioStreamer.start() error: {e}")
                
                # Forcer le device sur l'AudioStreamer
                if hasattr(streamer, 'set_device'):
                    try:
                        streamer.set_device(self.rode_device_id)
                        self.log_message(f"✅ AudioStreamer device set to {self.rode_device_id}")
                    except Exception as e:
                        self.log_message(f"⚠️ AudioStreamer.set_device() error: {e}")
            
            # Essayer via StreamingManager
            if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
                manager = self.engine.streaming_manager
                self.log_message("🎧 Attempting StreamingManager activation...")
                
                # Try all possible streaming activation methods
                activation_methods = [
                    'start_streaming', 'start', 'begin', 'activate', 'enable',
                    'listen', 'record', 'capture', 'force_restart'
                ]
                
                for method_name in activation_methods:
                    if hasattr(manager, method_name):
                        try:
                            method = getattr(manager, method_name)
                            if callable(method):
                                self.log_message(f"🎯 Trying StreamingManager.{method_name}()...")
                                result = method()
                                self.log_message(f"✅ StreamingManager.{method_name}() → {result}")
                                streaming_started = True
                                break  # Success, stop trying other methods
                        except Exception as e:
                            self.log_message(f"⚠️ StreamingManager.{method_name}() error: {e}")
                
                # Diagnostic post-activation du StreamingManager
                self.log_message("🔍 Post-activation StreamingManager diagnostic:")
                try:
                    # Check running state
                    if hasattr(manager, 'running'):
                        running_state = manager.running
                        self.log_message(f"   📊 running = {running_state}")
                    
                    # Check stream counter
                    if hasattr(manager, 'stream_counter'):
                        counter = manager.stream_counter
                        self.log_message(f"   📊 stream_counter = {counter}")
                    
                    # Check audio_streamer
                    if hasattr(manager, 'audio_streamer') and manager.audio_streamer:
                        streamer = manager.audio_streamer
                        self.log_message(f"   🎵 audio_streamer found: {type(streamer).__name__}")
                        
                        # Inspect AudioStreamer state
                        streamer_attrs = ['device_id', 'sample_rate', 'chunk_size', 'is_recording', 'active', 'running']
                        for attr in streamer_attrs:
                            if hasattr(streamer, attr):
                                try:
                                    value = getattr(streamer, attr)
                                    self.log_message(f"     → {attr} = {value}")
                                except Exception as e:
                                    self.log_message(f"     → {attr} error: {e}")
                        
                        # Try to force AudioStreamer device
                        if hasattr(streamer, 'set_device_id'):
                            try:
                                streamer.set_device_id(self.rode_device_id)
                                self.log_message(f"     ✅ AudioStreamer device set to {self.rode_device_id}")
                            except Exception as e:
                                self.log_message(f"     ⚠️ AudioStreamer.set_device_id() error: {e}")
                        
                        # Try to start AudioStreamer
                        streamer_start_methods = ['start', 'begin_recording', 'activate', 'enable']
                        for method_name in streamer_start_methods:
                            if hasattr(streamer, method_name):
                                try:
                                    method = getattr(streamer, method_name)
                                    if callable(method):
                                        result = method()
                                        self.log_message(f"     ✅ AudioStreamer.{method_name}() → {result}")
                                        break
                                except Exception as e:
                                    self.log_message(f"     ⚠️ AudioStreamer.{method_name}() error: {e}")
                        
                        # 🎯 CRITICAL: Test direct de l'AudioStreamer
                        self.log_message("🎯 TESTING AUDIOSTREAMER DIRECT CONNECTION:")
                        
                        # Force device configuration on AudioStreamer
                        if hasattr(streamer, 'device_id'):
                            current_device = getattr(streamer, 'device_id', 'N/A')
                            self.log_message(f"     📊 Current AudioStreamer device: {current_device}")
                            
                            if current_device != self.rode_device_id:
                                self.log_message(f"     ⚠️ Device mismatch! AudioStreamer={current_device}, Rode={self.rode_device_id}")
                                
                                # Try to force correct device
                                device_set_methods = ['set_device_id', 'set_device', 'configure_device']
                                for method_name in device_set_methods:
                                    if hasattr(streamer, method_name):
                                        try:
                                            method = getattr(streamer, method_name)
                                            if callable(method):
                                                result = method(self.rode_device_id)
                                                self.log_message(f"     ✅ AudioStreamer.{method_name}({self.rode_device_id}) → {result}")
                                                
                                                # Verify device change
                                                new_device = getattr(streamer, 'device_id', 'N/A')
                                                self.log_message(f"     📊 New AudioStreamer device: {new_device}")
                                                break
                                        except Exception as e:
                                            self.log_message(f"     ⚠️ AudioStreamer.{method_name}() error: {e}")
                            else:
                                self.log_message(f"     ✅ AudioStreamer device correctly set to Rode {self.rode_device_id}")
                        
                        # Test if AudioStreamer is actually capturing
                        self.log_message("🔬 Testing AudioStreamer capture state:")
                        capture_states = ['is_recording', 'is_active', 'is_capturing', 'active']
                        for state_name in capture_states:
                            if hasattr(streamer, state_name):
                                try:
                                    state = getattr(streamer, state_name)
                                    if callable(state):
                                        state_value = state()
                                        self.log_message(f"     📊 {state_name}() → {state_value}")
                                    else:
                                        self.log_message(f"     📊 {state_name} = {state}")
                                except Exception as e:
                                    self.log_message(f"     ⚠️ {state_name} error: {e}")
                        
                        # Manual audio chunk simulation test
                        self.log_message("🧪 Testing manual on_audio_ready() trigger:")
                        try:
                            import numpy as np
                            
                            # Create test audio chunk (3 seconds of silence)
                            test_chunk = np.zeros(16000 * 3, dtype=np.float32)  # 3s at 16kHz
                            self.log_message(f"     📦 Created test chunk: shape={test_chunk.shape}, dtype={test_chunk.dtype}")
                            
                            # Try to manually trigger on_audio_ready
                            if hasattr(manager, 'on_audio_ready'):
                                try:
                                    result = manager.on_audio_ready(test_chunk)
                                    self.log_message(f"     ✅ Manual on_audio_ready() → {result}")
                                    self.log_message(f"     📊 Stream counter after manual trigger: {manager.stream_counter}")
                                except Exception as e:
                                    self.log_message(f"     ⚠️ Manual on_audio_ready() error: {e}")
                            
                        except Exception as sim_e:
                            self.log_message(f"     ⚠️ Audio simulation error: {sim_e}")
                        
                        # Check if there's a start_stream or similar method
                        stream_methods = ['start_stream', 'begin_stream', 'start_capture', 'activate_stream']
                        self.log_message("🌊 Testing streaming methods:")
                        for method_name in stream_methods:
                            if hasattr(streamer, method_name):
                                try:
                                    method = getattr(streamer, method_name)
                                    if callable(method):
                                        # Check signature first
                                        import inspect
                                        sig = inspect.signature(method)
                                        self.log_message(f"     📝 {method_name}{sig}")
                                        
                                        # Try to call with device if needed
                                        if len(sig.parameters) == 0:
                                            result = method()
                                            self.log_message(f"     ✅ {method_name}() → {result}")
                                        elif 'device' in str(sig) or 'device_id' in str(sig):
                                            result = method(self.rode_device_id)
                                            self.log_message(f"     ✅ {method_name}({self.rode_device_id}) → {result}")
                                        else:
                                            self.log_message(f"     📋 {method_name} requires: {list(sig.parameters.keys())}")
                                except Exception as e:
                                    self.log_message(f"     ⚠️ {method_name} error: {e}")
                    else:
                        self.log_message("   ❌ No audio_streamer found in StreamingManager")
                    
                    # Test callback mechanism directly
                    self.log_message("🔗 Testing callback mechanism:")
                    if hasattr(manager, 'transcriber_callback'):
                        self.log_message("   📞 transcriber_callback method found")
                    if hasattr(manager, 'on_audio_ready'):
                        self.log_message("   🎤 on_audio_ready method found")
                        
                        # Try to manually trigger on_audio_ready (if safe)
                        try:
                            import inspect
                            sig = inspect.signature(manager.on_audio_ready)
                            self.log_message(f"   → on_audio_ready signature: {sig}")
                        except Exception as e:
                            self.log_message(f"   → signature error: {e}")
                    
                except Exception as diag_e:
                    self.log_message(f"⚠️ Post-activation diagnostic error: {diag_e}")
                
                # Try to force device configuration on StreamingManager
                device_methods = ['set_device', 'set_audio_device', 'configure_device']
                for method_name in device_methods:
                    if hasattr(manager, method_name):
                        try:
                            method = getattr(manager, method_name)
                            if callable(method):
                                result = method(self.rode_device_id)
                                self.log_message(f"✅ StreamingManager.{method_name}({self.rode_device_id}) → {result}")
                        except Exception as e:
                            self.log_message(f"⚠️ StreamingManager.{method_name}() error: {e}")
                
                # Check streaming state
                state_methods = ['is_streaming', 'is_active', 'is_listening', 'get_status']
                for method_name in state_methods:
                    if hasattr(manager, method_name):
                        try:
                            method = getattr(manager, method_name)
                            if callable(method):
                                state = method()
                                self.log_message(f"📊 StreamingManager.{method_name}() → {state}")
                        except Exception as e:
                            self.log_message(f"⚠️ StreamingManager.{method_name}() error: {e}")
            
            # Configuration du device si méthode disponible
            if hasattr(self.engine, 'set_audio_device'):
                try:
                    result = self.engine.set_audio_device(self.rode_device_id)
                    self.log_message(f"✅ Engine V5 audio device set to {self.rode_device_id} → {result}")
                except Exception as e:
                    self.log_message(f"⚠️ set_audio_device() error: {e}")
            
            if not streaming_started:
                self.log_message("⚠️ No streaming start method succeeded, relying on callback only")
            else:
                self.log_message("✅ Engine V5 streaming activation attempted")
            
            # Update UI
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="🔴 Status: Recording...", fg=self.colors['error'])
            
            self.log_message(f"🎤 Listening on Rode device {self.rode_device_id}")
            self.log_message("📖 READ THE VALIDATION TEXT NOW!")
            
            # Start monitoring thread with shorter interval
            self.start_monitoring()
            
        except Exception as e:
            error_msg = f"❌ START ERROR: {str(e)}"
            self.log_message(error_msg, self.colors['error'])
            messagebox.showerror("Start Error", error_msg)
    
    def start_monitoring(self):
        """Monitor for transcriptions and implement bypass if needed"""
        def monitor_thread():
            # Wait 7 seconds for first transcription (réduit de 10s)
            time.sleep(7)
            
            if self.listening and len(self.transcription_segments) == 0:
                self.log_message("⚠️ No transcriptions received after 7 seconds", self.colors['warning'])
                self.log_message("🔧 Checking audio stream...", self.colors['warning'])
                
                # Offer bypass mode
                self.root.after(0, self.offer_bypass_mode)
            elif self.listening and self.callback_count > 0:
                # Engine V5 a envoyé au moins 1 callback, continuer à monitorer
                self.log_message("✅ Engine V5 callback detected, continuing monitoring...")
                
                # Monitoring continu pour détecter l'arrêt du streaming
                def continuous_monitor():
                    last_callback_count = self.callback_count
                    time.sleep(15)  # Attendre 15s
                    
                    if self.listening and self.callback_count == last_callback_count:
                        self.log_message("⚠️ Engine V5 streaming stopped, activating bypass...", self.colors['warning'])
                        if not self.bypass_mode:  # Si pas déjà en bypass
                            self.root.after(0, self.enable_bypass_mode)
                
                threading.Thread(target=continuous_monitor, daemon=True).start()
        
        threading.Thread(target=monitor_thread, daemon=True).start()
    
    def offer_bypass_mode(self):
        """Offer to use bypass mode with direct audio capture"""
        if not self.listening:
            return
            
        result = messagebox.askyesno(
            "No Transcriptions", 
            "No transcriptions received from Engine V5.\n\n"
            "Would you like to try BYPASS MODE?\n"
            "(Direct audio capture + transcription)"
        )
        
        if result:
            self.enable_bypass_mode()
    
    def enable_bypass_mode(self):
        """Enable bypass mode with direct audio capture"""
        self.bypass_mode = True
        self.log_message("🔧 ENABLING BYPASS MODE", self.colors['warning'])
        self.log_message("📡 Starting direct audio capture...", self.colors['warning'])
        
        # Start direct audio capture thread
        def capture_thread():
            try:
                # Import faster-whisper for bypass
                from faster_whisper import WhisperModel
                
                # Use 'small' model instead of 'tiny' for better French performance
                self.log_message("🧠 Loading bypass model (small for better French)...")
                model = WhisperModel("small", device="cuda", compute_type="int8")
                
                # Longer capture for better context
                capture_duration = 5  # 5 seconds instead of 3
                silence_threshold = 0.001
                
                while self.listening and self.bypass_mode:
                    # Capture audio with proper sample rate
                    audio_data = sd.rec(int(capture_duration * 16000),
                                       samplerate=16000,
                                       channels=1,
                                       device=self.rode_device_id,
                                       dtype=np.float32)
                    sd.wait()
                    
                    if not self.listening:
                        break
                    
                    # Check if there's speech
                    rms = np.sqrt(np.mean(audio_data ** 2))
                    self.log_message(f"🔊 Audio level: {rms:.6f}")
                    
                    if rms > silence_threshold:
                        # Transcribe with better parameters
                        self.log_message("🎯 Processing audio segment...")
                        segments, info = model.transcribe(
                            audio_data.flatten(), 
                            language="fr",
                            beam_size=5,
                            best_of=5,
                            temperature=0.0,
                            condition_on_previous_text=False
                        )
                        
                        for segment in segments:
                            text = segment.text.strip()
                            if text and len(text) > 2:  # Filter very short segments
                                # Simulate callback
                                timestamp = time.time() - self.start_time
                                self.transcription_segments.append({
                                    'text': text,
                                    'timestamp': timestamp,
                                    'source': 'bypass'  # Marquer la source bypass
                                })
                                self.transcription_complete += text + " "
                                self.log_message(f"🔄 [BYPASS {timestamp:.1f}s] {text}", self.colors['warning'])
                                self.update_stats()
                    else:
                        self.log_message(f"🔇 Silence detected (RMS: {rms:.6f})")
                                
            except Exception as e:
                self.log_message(f"❌ Bypass error: {str(e)}", self.colors['error'])
        
        threading.Thread(target=capture_thread, daemon=True).start()
    
    def stop_test(self):
        """Stop transcription test"""
        if not self.listening:
            return
            
        self.listening = False
        self.bypass_mode = False
        
        self.log_message("="*80)
        self.log_message("⏹️ STOPPING TEST")
        self.log_message("="*80)
        
        # Update UI
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.analyze_btn.config(state="normal")
        self.status_label.config(text="🟢 Status: Test completed", fg=self.colors['success'])
        
        # Summary
        total_time = time.time() - self.start_time if self.start_time else 0
        self.log_message(f"📊 Test duration: {total_time:.1f}s")
        self.log_message(f"📊 Segments: {len(self.transcription_segments)}")
        self.log_message(f"📊 Total callbacks: {self.callback_count}")
        self.log_message(f"📊 Characters: {len(self.transcription_complete)}")
        
        if len(self.transcription_segments) > 0:
            self.log_message("✅ Transcriptions received successfully!")
        else:
            self.log_message("⚠️ No transcriptions received")
        
        self.update_stats()
    
    def analyze_results(self):
        """Analyze transcription results"""
        if not self.transcription_complete.strip():
            messagebox.showwarning("No Data", "No transcription data to analyze!")
            return
            
        self.log_message("="*80)
        self.log_message("📊 ANALYZING RESULTS")
        self.log_message("="*80)
        
        # Séparer les segments par source
        engine_v5_segments = [s for s in self.transcription_segments if s.get('source') == 'engine_v5']
        bypass_segments = [s for s in self.transcription_segments if s.get('source') == 'bypass']
        
        # Statistiques par source
        self.log_message("=== SOURCE ANALYSIS ===")
        self.log_message(f"📊 Engine V5 segments: {len(engine_v5_segments)}")
        self.log_message(f"📊 Bypass segments: {len(bypass_segments)}")
        self.log_message(f"📊 Engine V5 callbacks: {self.callback_count}")
        
        # Déterminer si bypass a été vraiment utilisé
        bypass_was_used = len(bypass_segments) > 0
        
        # Clean texts for comparison
        ref_clean = self.clean_text(TEXTE_REFERENCE)
        trans_clean = self.clean_text(self.transcription_complete)
        
        # Calculate metrics
        similarity = difflib.SequenceMatcher(None, ref_clean, trans_clean).ratio()
        
        ref_words = ref_clean.split()
        trans_words = trans_clean.split()
        
        # WER calculation
        wer_errors = self.calculate_wer(ref_words, trans_words)
        wer = (wer_errors / len(ref_words) * 100) if ref_words else 0
        word_accuracy = 100 - wer
        
        # Display results
        self.log_message("=== OVERALL METRICS ===")
        self.log_message(f"📊 Similarity: {similarity*100:.1f}%")
        self.log_message(f"📊 Word Accuracy: {word_accuracy:.1f}% (WER: {wer:.1f}%)")
        self.log_message(f"📊 Reference words: {len(ref_words)}")
        self.log_message(f"📊 Transcribed words: {len(trans_words)}")
        self.log_message(f"📊 Word errors: {wer_errors}")
        
        # Complexity analysis
        self.analyze_by_complexity(trans_clean)
        
        # Error analysis
        self.analyze_errors(ref_words, trans_words)
        
        # Performance metrics
        total_time = self.transcription_segments[-1]['timestamp'] if self.transcription_segments else 0
        self.log_message("\n=== PERFORMANCE ===")
        self.log_message(f"⏱️ Total time: {total_time:.1f}s")
        self.log_message(f"📦 Total segments: {len(self.transcription_segments)}")
        self.log_message(f"🎤 Device: Rode ID {self.rode_device_id}")
        self.log_message(f"🔧 Bypass mode used: {'Yes' if bypass_was_used else 'No'}")
        
        # Engine V5 diagnostic détaillé
        self.log_message("\n=== ENGINE V5 DIAGNOSTIC ===")
        self.log_message(f"🎯 Engine V5 callbacks: {self.callback_count}")
        self.log_message(f"🎯 Engine V5 segments: {len(engine_v5_segments)}")
        
        if len(engine_v5_segments) > 0:
            engine_chars = sum(len(s['text']) for s in engine_v5_segments)
            self.log_message(f"✅ Engine V5 contributed {engine_chars} characters")
            self.log_message("✅ Engine V5 is partially functional")
        
        if self.callback_count == 0:
            self.log_message("❌ CRITICAL: Engine V5 sent zero callbacks")
            self.log_message("   → Audio streaming not reaching Engine V5")
            self.log_message("   → Check AudioStreamer initialization")
            self.log_message("   → Verify microphone device configuration")
        elif self.callback_count < len(self.transcription_segments) / 2:
            self.log_message("⚠️ WARNING: Engine V5 sent few callbacks")
            self.log_message("   → Streaming is intermittent")
            self.log_message("   → Audio pipeline may need restart mechanism")
            self.log_message("   → Consider continuous listening activation")
        else:
            self.log_message("✅ Engine V5 is working well")
        
        # Bypass diagnostic
        if bypass_was_used:
            bypass_chars = sum(len(s['text']) for s in bypass_segments)
            self.log_message(f"\n=== BYPASS DIAGNOSTIC ===")
            self.log_message(f"🔄 Bypass contributed {bypass_chars} characters")
            self.log_message(f"🔄 Bypass segments: {len(bypass_segments)}")
            self.log_message(f"🔄 Bypass coverage: {len(bypass_segments)/len(self.transcription_segments)*100:.1f}%")
        
        # Save results
        self.save_results(similarity, word_accuracy, wer, total_time)
        
        self.log_message("="*80)
        self.log_message("✅ ANALYSIS COMPLETE")
        self.log_message("="*80)
    
    def clean_text(self, text):
        """Clean text for comparison"""
        # Remove punctuation and convert to lowercase
        cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Normalize French accents
        replacements = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'ù': 'u', 'û': 'u', 'ü': 'u',
            'î': 'i', 'ï': 'i',
            'ô': 'o', 'ö': 'o',
            'ç': 'c'
        }
        
        for accented, plain in replacements.items():
            cleaned = cleaned.replace(accented, plain)
            
        return cleaned
    
    def calculate_wer(self, ref_words, hyp_words):
        """Calculate Word Error Rate using Levenshtein distance"""
        m, n = len(ref_words), len(hyp_words)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if ref_words[i-1] == hyp_words[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],    # Deletion
                        dp[i][j-1],    # Insertion
                        dp[i-1][j-1]   # Substitution
                    )
        
        return dp[m][n]
    
    def analyze_by_complexity(self, transcription):
        """Analyze transcription by complexity segments"""
        self.log_message("\n=== COMPLEXITY ANALYSIS ===")
        
        segments = [
            ("Simple words", ["chat", "chien", "maison", "voiture", "ordinateur", "telephone"]),
            ("Technical terms", ["algorithme", "machine learning", "gpu", "rtx", "faster whisper", "quantification", "int8"]),
            ("Numbers/Dates", ["vingt trois", "quarante sept", "mille neuf cent", "quinze janvier", "deux mille"]),
            ("Difficult words", ["chrysantheme", "anticonstitutionnellement", "prestidigitateur", "kakemono", "yaourt"])
        ]
        
        for segment_name, keywords in segments:
            found = sum(1 for keyword in keywords if keyword in transcription.lower())
            total = len(keywords)
            percentage = (found / total * 100) if total > 0 else 0
            
            status = "✅" if percentage >= 70 else "⚠️" if percentage >= 50 else "❌"
            self.log_message(f"{status} {segment_name}: {found}/{total} ({percentage:.1f}%)")
    
    def analyze_errors(self, ref_words, trans_words):
        """Analyze common errors"""
        self.log_message("\n=== ERROR ANALYSIS ===")
        
        # Convert to Counter for frequency analysis
        ref_counter = Counter(ref_words)
        trans_counter = Counter(trans_words)
        
        # Missing words
        missing_words = []
        for word, count in ref_counter.items():
            if trans_counter[word] < count:
                missing_words.append(word)
        
        if missing_words:
            self.log_message(f"❌ Missing words ({len(missing_words)}): {', '.join(missing_words[:10])}")
            if len(missing_words) > 10:
                self.log_message(f"   ... and {len(missing_words) - 10} more")
        
        # Added words (potential hallucinations)
        added_words = []
        for word, count in trans_counter.items():
            if word not in ref_counter:
                added_words.append(word)
        
        if added_words:
            self.log_message(f"➕ Added words ({len(added_words)}): {', '.join(added_words[:10])}")
            if len(added_words) > 10:
                self.log_message(f"   ... and {len(added_words) - 10} more")
    
    def save_results(self, similarity, word_accuracy, wer, total_time):
        """Save detailed results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_engine_v5_ultimate_{timestamp}.json"
        
        results = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "duration": total_time,
                "device_id": self.rode_device_id,
                "bypass_mode": self.bypass_mode,
                "engine": "SuperWhisper2 Engine V5 Phase 3",
                "gpu": "RTX 3090 24GB"
            },
            "metrics": {
                "similarity": similarity * 100,
                "word_accuracy": word_accuracy,
                "wer": wer,
                "segments": len(self.transcription_segments),
                "total_chars": len(self.transcription_complete),
                "callbacks": self.callback_count
            },
            "reference_text": TEXTE_REFERENCE,
            "transcription": self.transcription_complete,
            "segments": self.transcription_segments
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            self.log_message(f"💾 Results saved to: {filename}", self.colors['success'])
            
            # Also save text version
            txt_filename = filename.replace('.json', '.txt')
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write("TEST ENGINE V5 ULTIMATE - RESULTS\n")
                f.write("="*60 + "\n\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Device: Rode ID {self.rode_device_id}\n")
                f.write(f"Bypass Mode: {'Yes' if self.bypass_mode else 'No'}\n\n")
                
                f.write("METRICS\n")
                f.write("-"*30 + "\n")
                f.write(f"Similarity: {similarity*100:.1f}%\n")
                f.write(f"Word Accuracy: {word_accuracy:.1f}%\n")
                f.write(f"WER: {wer:.1f}%\n")
                f.write(f"Duration: {total_time:.1f}s\n")
                f.write(f"Segments: {len(self.transcription_segments)}\n\n")
                
                f.write("REFERENCE TEXT\n")
                f.write("-"*30 + "\n")
                f.write(TEXTE_REFERENCE + "\n\n")
                
                f.write("TRANSCRIPTION\n")
                f.write("-"*30 + "\n")
                f.write(self.transcription_complete + "\n\n")
                
                f.write("SEGMENTS\n")
                f.write("-"*30 + "\n")
                for i, seg in enumerate(self.transcription_segments):
                    f.write(f"[{i+1}] {seg['timestamp']:.1f}s: {seg['text']}\n")
            
            self.log_message(f"💾 Text results saved to: {txt_filename}", self.colors['success'])
            
        except Exception as e:
            self.log_message(f"❌ Save error: {str(e)}", self.colors['error'])
    
    def start_engine_v5_streaming(self):
        """Démarre le streaming Engine V5 avec fallbacks robustes"""
        try:
            self.log_message("🔧 Setting transcription callback...")
            self.engine.set_transcription_callback(self.on_transcription_received)
            self.log_message("✅ Callback configured")
            
            # === NIVEAU 1: ACTIVATION STANDARD ===
            self.log_message("🔍 Checking Engine V5 audio readiness...")
            if hasattr(self.engine, 'start_listening'):
                self.engine.start_listening()
                self.log_message("✅ Engine V5 start_listening() activated")
            else:
                self.log_message("⚠️ No explicit start method found, using advanced activation")
            
            # === NIVEAU 2: CONFIGURATION FORCÉE RODE ===
            success_level_2 = self._force_configure_rode_streaming()
            
            # === NIVEAU 3: MONITORING THREAD ACTIF ===
            if success_level_2:
                self._start_streaming_monitor()
                self.log_message("✅ Multi-level streaming activation complete")
            else:
                self.log_message("⚠️ Fallback to bypass mode recommended")
            
            self.log_message(f"🎤 Listening on Rode device {self.rode_device_id}")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Engine V5 streaming failed: {e}")
            return False
    
    def _force_configure_rode_streaming(self):
        """NIVEAU 2: Configuration forcée du Rode sur AudioStreamer"""
        try:
            self.log_message("🔧 NIVEAU 2: Force-configuring Rode on AudioStreamer...")
            
            # Accéder au StreamingManager
            if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
                manager = self.engine.streaming_manager
                
                # Configurer l'AudioStreamer avec le device Rode
                if hasattr(manager, 'audio_streamer') and manager.audio_streamer:
                    streamer = manager.audio_streamer
                    
                    # Configuration explicite du device
                    device_config_methods = ['set_device', 'configure_device', 'set_input_device']
                    for method_name in device_config_methods:
                        if hasattr(streamer, method_name):
                            try:
                                method = getattr(streamer, method_name)
                                result = method(self.rode_device_id)
                                self.log_message(f"✅ AudioStreamer.{method_name}({self.rode_device_id}) → {result}")
                                break
                            except Exception as e:
                                self.log_message(f"⚠️ {method_name} failed: {e}")
                    
                    # Configuration du sample rate
                    if hasattr(streamer, 'sample_rate'):
                        streamer.sample_rate = 16000
                        self.log_message("✅ AudioStreamer sample_rate = 16000")
                    
                    # Force restart du streaming
                    restart_methods = ['restart', 'force_restart', 'reset_and_start']
                    for method_name in restart_methods:
                        if hasattr(streamer, method_name):
                            try:
                                method = getattr(streamer, method_name)
                                result = method()
                                self.log_message(f"✅ AudioStreamer.{method_name}() → {result}")
                                break
                            except Exception as e:
                                continue
                
                # Redémarrer le StreamingManager
                if hasattr(manager, 'restart'):
                    try:
                        manager.restart()
                        self.log_message("✅ StreamingManager.restart() executed")
                    except Exception as e:
                        self.log_message(f"⚠️ StreamingManager restart failed: {e}")
                
                return True
                
        except Exception as e:
            self.log_message(f"❌ Level 2 configuration failed: {e}")
            
        return False
    
    def _start_streaming_monitor(self):
        """NIVEAU 3: Thread de monitoring pour maintenir le streaming actif"""
        try:
            self.log_message("🔧 NIVEAU 3: Starting streaming monitor thread...")
            
            def streaming_monitor():
                import time
                import numpy as np
                
                monitor_count = 0
                last_callback_count = self.callback_count
                inactive_cycles = 0
                
                while self.listening and monitor_count < 30:  # Max 2.5 minutes
                    time.sleep(5)  # Check every 5 seconds
                    monitor_count += 1
                    
                    # Vérifier si des callbacks ont été reçus
                    current_callbacks = self.callback_count
                    if current_callbacks > last_callback_count:
                        last_callback_count = current_callbacks
                        inactive_cycles = 0
                        self.log_message(f"✅ Engine V5 active: {current_callbacks} callbacks")
                        continue
                    
                    inactive_cycles += 1
                    self.log_message(f"⚠️ No Engine V5 activity for {inactive_cycles * 5}s")
                    
                    # Si pas d'activité depuis 10s, forcer un trigger
                    if inactive_cycles >= 2:
                        self._trigger_manual_audio_processing()
                        
                    # Si pas d'activité depuis 20s, tenter une relance
                    if inactive_cycles >= 4:
                        self.log_message("🔧 Attempting streaming restart...")
                        self._restart_engine_streaming()
                        inactive_cycles = 0  # Reset counter after restart attempt
            
            # Lancer le thread de monitoring
            threading.Thread(target=streaming_monitor, daemon=True).start()
            self.log_message("✅ Streaming monitor thread started")
            
        except Exception as e:
            self.log_message(f"❌ Monitor thread failed: {e}")
    
    def _trigger_manual_audio_processing(self):
        """Force un traitement audio manuel si le streaming est inactif"""
        try:
            if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
                manager = self.engine.streaming_manager
                
                # Capturer de l'audio depuis le Rode
                import sounddevice as sd
                import numpy as np
                
                # Capture 3 secondes d'audio
                duration = 3.0
                sample_rate = 16000
                audio_data = sd.rec(int(duration * sample_rate), 
                                  samplerate=sample_rate, 
                                  channels=1, 
                                  device=self.rode_device_id)
                sd.wait()
                
                # Convertir en format attendu
                audio_chunk = audio_data.flatten().astype(np.float32)
                
                # Déclencher on_audio_ready manuellement
                if hasattr(manager, 'on_audio_ready'):
                    manager.on_audio_ready(audio_chunk)
                    self.log_message(f"🔧 Manual audio trigger: {len(audio_chunk)} samples")
                
        except Exception as e:
            self.log_message(f"⚠️ Manual audio processing failed: {e}")
    
    def _restart_engine_streaming(self):
        """Redémarre complètement le streaming Engine V5"""
        try:
            if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
                manager = self.engine.streaming_manager
                
                # Arrêter proprement
                if hasattr(manager, 'stop'):
                    manager.stop()
                
                # Attendre un peu
                import time
                time.sleep(1)
                
                # Redémarrer
                if hasattr(manager, 'start'):
                    manager.start()
                    self.log_message("🔄 Engine V5 streaming restarted")
                
                # Reconfigurer le device
                self._force_configure_rode_streaming()
                
        except Exception as e:
            self.log_message(f"❌ Streaming restart failed: {e}")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    print("🚀 Starting Test Engine V5 Ultimate...")
    
    try:
        app = UltimateEngineV5Test()
        app.run()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
