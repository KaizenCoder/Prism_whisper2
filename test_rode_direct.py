#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST RODE DIRECT - Bypass Engine V5
Solution simple et fonctionnelle qui marche
"""

import sounddevice as sd
import numpy as np
import time
import threading
import queue
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import json
import difflib

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    print("❌ faster-whisper non disponible")

class RodeDirectTester:
    """Test direct Rode -> faster-whisper"""
    
    def __init__(self):
        self.rode_device_id = None
        self.recording = False
        self.audio_queue = queue.Queue()
        self.transcription_results = []
        
        # Configuration audio
        self.sample_rate = 16000
        self.chunk_duration = 3.0  # 3 secondes par chunk
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # Modèle Whisper
        self.model = None
        
        # Interface
        self.setup_gui()
        
        # Texte de référence
        self.reference_text = """Bonjour, ceci est un test de validation pour SuperWhisper2. Je vais maintenant énoncer plusieurs phrases de complexité croissante pour évaluer la précision de transcription.
Premièrement, des mots simples : chat, chien, maison, voiture, ordinateur, téléphone.
Deuxièmement, des phrases courtes : Il fait beau aujourd'hui. Le café est délicieux. J'aime la musique classique.
Troisièmement, des phrases plus complexes : L'intelligence artificielle transforme notre manière de travailler et de communiquer dans le monde moderne.
Quatrièmement, des termes techniques : algorithme, machine learning, GPU RTX 3090, faster-whisper, quantification INT8, latence de transcription.
Cinquièmement, des nombres et dates : vingt-trois, quarante-sept, mille neuf cent quatre-vingt-quinze, le quinze janvier deux mille vingt-quatre.
Sixièmement, des mots difficiles : chrysanthème, anticonstitutionnellement, prestidigitateur, kakémono, yaourt.
Septièmement, une phrase longue et complexe : L'optimisation des performances de transcription vocale nécessite une approche méthodique combinant la sélection appropriée des modèles, l'ajustement des paramètres de traitement, et l'implémentation d'algorithmes de post-traitement pour améliorer la qualité du résultat final.
Fin du test de validation."""

    def setup_gui(self):
        """Interface simple et efficace"""
        self.root = tk.Tk()
        self.root.title("🎤 Rode Direct Test - SOLUTION SIMPLE")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Header
        header = tk.Label(self.root, text="🎤 RODE DIRECT → FASTER-WHISPER",
                         font=('Consolas', 16, 'bold'), 
                         bg='#1a1a1a', fg='#00ff00')
        header.pack(pady=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="Status: Prêt",
                                   font=('Consolas', 12), 
                                   bg='#1a1a1a', fg='#ffff00')
        self.status_label.pack(pady=5)
        
        # Boutons
        button_frame = tk.Frame(self.root, bg='#1a1a1a')
        button_frame.pack(pady=10)
        
        self.detect_btn = tk.Button(button_frame, text="🔍 DETECT RODE", 
                                   command=self.detect_rode, bg='#333', fg='white',
                                   font=('Consolas', 10, 'bold'), width=15)
        self.detect_btn.pack(side='left', padx=5)
        
        self.init_btn = tk.Button(button_frame, text="⚡ INIT MODEL", 
                                 command=self.init_model, bg='#006600', fg='white',
                                 font=('Consolas', 10, 'bold'), width=15)
        self.init_btn.pack(side='left', padx=5)
        
        self.start_btn = tk.Button(button_frame, text="🎤 START", 
                                  command=self.start_recording, bg='#0066cc', fg='white',
                                  font=('Consolas', 10, 'bold'), width=15)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="⏹️ STOP", 
                                 command=self.stop_recording, bg='#cc0000', fg='white',
                                 font=('Consolas', 10, 'bold'), width=15)
        self.stop_btn.pack(side='left', padx=5)
        
        # Logs
        self.log_text = scrolledtext.ScrolledText(self.root, height=25,
                                                 bg='#000000', fg='#00ff00',
                                                 font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def log(self, message: str):
        """Log simple"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_msg)
        self.log_text.see(tk.END)
        self.root.update()
        
    def detect_rode(self):
        """Détection simple du Rode"""
        self.log("🔍 Détection Rode NT-USB...")
        
        devices = sd.query_devices()
        self.log(f"📋 {len(devices)} devices détectés")
        
        for i, device in enumerate(devices):
            if 'RODE' in device['name'].upper() and device['max_input_channels'] > 0:
                self.rode_device_id = i
                self.log(f"✅ RODE TROUVÉ: {device['name']}")
                self.log(f"   Device ID: {i}")
                self.log(f"   Sample Rate: {device['default_samplerate']} Hz")
                self.log(f"   Channels: {device['max_input_channels']}")
                self.status_label.config(text=f"Status: Rode détecté (ID: {i})")
                return
                
        self.log("❌ Rode NT-USB non trouvé")
        self.status_label.config(text="Status: Rode non détecté")
        
    def init_model(self):
        """Initialisation faster-whisper"""
        def init_thread():
            try:
                if not FASTER_WHISPER_AVAILABLE:
                    self.log("❌ faster-whisper non disponible")
                    return
                    
                self.log("⚡ Initialisation faster-whisper...")
                self.log("📦 Chargement modèle 'small'...")
                start_time = time.time()
                
                # Modèle small pour rapidité
                self.model = WhisperModel("small", device="cuda", compute_type="int8")
                
                init_time = time.time() - start_time
                self.log(f"✅ Modèle prêt en {init_time:.1f}s")
                self.status_label.config(text=f"Status: Modèle prêt ({init_time:.1f}s)")
                
            except Exception as e:
                self.log(f"❌ Erreur init modèle: {e}")
                self.status_label.config(text="Status: Erreur modèle")
                
        threading.Thread(target=init_thread, daemon=True).start()
        
    def audio_callback(self, indata, frames, time, status):
        """Callback direct audio"""
        if status:
            self.log(f"⚠️ Audio status: {status}")
            
        if self.recording:
            # Conversion mono
            audio_data = indata[:, 0] if indata.shape[1] > 1 else indata.flatten()
            
            # Vérification niveau audio
            rms = np.sqrt(np.mean(audio_data**2))
            if rms > 0.001:  # Seuil minimal de bruit
                self.audio_queue.put(audio_data.copy())
                
    def start_recording(self):
        """Démarrer l'enregistrement direct"""
        if not self.rode_device_id:
            self.log("❌ Rode non détecté")
            return
            
        if not self.model:
            self.log("❌ Modèle non initialisé")
            return
            
        self.recording = True
        self.transcription_results = []
        
        self.log("=" * 50)
        self.log("🎤 DÉMARRAGE ENREGISTREMENT DIRECT")
        self.log("=" * 50)
        self.log("📖 Lisez le texte de validation:")
        self.log("─" * 30)
        
        # Afficher le texte
        words = self.reference_text.split()
        for i in range(0, len(words), 15):
            chunk = " ".join(words[i:i+15])
            self.log(chunk)
            
        self.log("─" * 30)
        self.status_label.config(text="Status: 🎤 ENREGISTREMENT EN COURS")
        
        # Démarrer capture audio
        try:
            self.stream = sd.InputStream(
                device=self.rode_device_id,
                channels=1,
                samplerate=self.sample_rate,
                callback=self.audio_callback,
                blocksize=1024
            )
            self.stream.start()
            self.log("✅ Capture audio démarrée")
            
            # Démarrer traitement
            self.start_processing()
            
        except Exception as e:
            self.log(f"❌ Erreur capture: {e}")
            
    def start_processing(self):
        """Traitement audio en temps réel"""
        def process_audio():
            audio_buffer = []
            
            while self.recording:
                try:
                    # Récupérer audio
                    audio_chunk = self.audio_queue.get(timeout=0.1)
                    audio_buffer.extend(audio_chunk)
                    
                    # Transcription par chunks de 3s
                    if len(audio_buffer) >= self.chunk_size:
                        chunk_to_process = np.array(audio_buffer[:self.chunk_size])
                        audio_buffer = audio_buffer[self.chunk_size:]
                        
                        # Transcription
                        self.transcribe_chunk(chunk_to_process)
                        
                except queue.Empty:
                    continue
                except Exception as e:
                    self.log(f"❌ Erreur traitement: {e}")
                    
        threading.Thread(target=process_audio, daemon=True).start()
        
    def transcribe_chunk(self, audio_chunk: np.ndarray):
        """Transcription d'un chunk audio"""
        try:
            # Transcription faster-whisper
            segments, info = self.model.transcribe(audio_chunk, language="fr")
            
            for segment in segments:
                text = segment.text.strip()
                if text:
                    timestamp = time.time()
                    self.transcription_results.append({
                        'text': text,
                        'timestamp': timestamp,
                        'confidence': getattr(segment, 'avg_logprob', 0.0)
                    })
                    
                    self.log(f"📝 [{len(self.transcription_results)}] {text}")
                    
        except Exception as e:
            self.log(f"❌ Erreur transcription: {e}")
            
    def stop_recording(self):
        """Arrêter l'enregistrement"""
        self.recording = False
        
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
            
        self.log("⏹️ ARRÊT ENREGISTREMENT")
        self.status_label.config(text="Status: Arrêté")
        
        # Analyse des résultats
        self.analyze_results()
        
    def analyze_results(self):
        """Analyse simple des résultats"""
        if not self.transcription_results:
            self.log("❌ Aucune transcription")
            return
            
        self.log("=" * 50)
        self.log("📊 ANALYSE RÉSULTATS")
        self.log("=" * 50)
        
        # Concaténer
        full_transcription = " ".join([r['text'] for r in self.transcription_results])
        
        # Similarité
        similarity = difflib.SequenceMatcher(
            None, 
            self.reference_text.lower(), 
            full_transcription.lower()
        ).ratio()
        
        self.log(f"📊 Segments: {len(self.transcription_results)}")
        self.log(f"📊 Similarité: {similarity*100:.1f}%")
        self.log(f"📝 Transcription: {full_transcription}")
        
        # Sauvegarde
        self.save_results(full_transcription, similarity)
        
    def save_results(self, transcription: str, similarity: float):
        """Sauvegarde"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rode_direct_test_{timestamp}.json"
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'method': 'rode_direct_faster_whisper',
            'segments': len(self.transcription_results),
            'similarity': similarity * 100,
            'reference_text': self.reference_text,
            'transcription': transcription,
            'results': self.transcription_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        self.log(f"💾 Sauvé: {filename}")
        
    def run(self):
        """Lancer l'app"""
        self.log("🎤 Rode Direct Tester - SOLUTION SIMPLE QUI MARCHE!")
        self.log("💡 1. Detect Rode  2. Init Model  3. Start")
        self.root.mainloop()

if __name__ == "__main__":
    app = RodeDirectTester()
    app.run() 