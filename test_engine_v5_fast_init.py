#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Engine V5 - INITIALISATION RAPIDE
Version optimisée pour démarrage en <30 secondes
"""

import sys
import os
from pathlib import Path
import time
import numpy as np
import sounddevice as sd
import json
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
import difflib
from typing import List, Dict, Any
import threading

# Configuration pour initialisation rapide
FAST_INIT_CONFIG = {
    "skip_int8_quantization": True,      # Skip INT8 (économise ~40s)
    "skip_small_model": True,            # Skip modèle small (économise ~15s)  
    "reduced_vram_cache": 1,             # Cache réduit 1GB au lieu de 5GB
    "skip_warmup": True,                 # Skip warm-up passes
    "minimal_cuda_streams": 1,           # 1 stream au lieu de 4
}

class FastEngineV5Tester:
    """Test Engine V5 avec initialisation rapide"""
    
    def __init__(self):
        self.setup_paths()
        self.engine = None
        self.callbacks_received = 0
        self.transcription_segments = []
        self.test_active = False
        self.rode_device_id = None
        
        # Interface
        self.root = None
        self.setup_gui()
        
        # Référence pour validation
        self.reference_text = """Bonjour, ceci est un test de validation pour SuperWhisper2. Je vais maintenant énoncer plusieurs phrases de complexité croissante pour évaluer la précision de transcription.
Premièrement, des mots simples : chat, chien, maison, voiture, ordinateur, téléphone.
Deuxièmement, des phrases courtes : Il fait beau aujourd'hui. Le café est délicieux. J'aime la musique classique.
Troisièmement, des phrases plus complexes : L'intelligence artificielle transforme notre manière de travailler et de communiquer dans le monde moderne.
Quatrièmement, des termes techniques : algorithme, machine learning, GPU RTX 3090, faster-whisper, quantification INT8, latence de transcription.
Cinquièmement, des nombres et dates : vingt-trois, quarante-sept, mille neuf cent quatre-vingt-quinze, le quinze janvier deux mille vingt-quatre.
Sixièmement, des mots difficiles : chrysanthème, anticonstitutionnellement, prestidigitateur, kakémono, yaourt.
Septièmement, une phrase longue et complexe : L'optimisation des performances de transcription vocale nécessite une approche méthodique combinant la sélection appropriée des modèles, l'ajustement des paramètres de traitement, et l'implémentation d'algorithmes de post-traitement pour améliorer la qualité du résultat final.
Fin du test de validation."""

    def setup_paths(self):
        """Configuration des chemins d'import"""
        project_root = Path(__file__).parent
        src_path = project_root / "src"
        sys.path.insert(0, str(src_path))
        
    def setup_gui(self):
        """Interface utilisateur simplifiée"""
        self.root = tk.Tk()
        self.root.title("🚀 Engine V5 Fast Init Test")
        self.root.geometry("900x600")
        self.root.configure(bg='#0d1117')
        
        # Style GitHub
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header
        header_frame = tk.Frame(self.root, bg='#161b22', height=60)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = tk.Label(header_frame, 
                              text="🚀 ENGINE V5 - INITIALISATION RAPIDE",
                              font=('Consolas', 16, 'bold'),
                              bg='#161b22', fg='#58a6ff')
        title_label.pack(pady=10)
        
        # Boutons
        button_frame = tk.Frame(self.root, bg='#0d1117')
        button_frame.pack(fill='x', padx=10, pady=5)
        
        self.init_btn = tk.Button(button_frame, text="🔧 INIT RAPIDE", 
                                 command=self.fast_init, bg='#238636', fg='white',
                                 font=('Consolas', 10, 'bold'), width=15)
        self.init_btn.pack(side='left', padx=5)
        
        self.start_btn = tk.Button(button_frame, text="▶️ START TEST", 
                                  command=self.start_test, bg='#1f6feb', fg='white',
                                  font=('Consolas', 10, 'bold'), width=15)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="⏹️ STOP", 
                                 command=self.stop_test, bg='#da3633', fg='white',
                                 font=('Consolas', 10, 'bold'), width=15)
        self.stop_btn.pack(side='left', padx=5)
        
        # Logs
        self.log_text = scrolledtext.ScrolledText(self.root, height=30, 
                                                 bg='#0d1117', fg='#c9d1d9',
                                                 font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Status
        self.status_label = tk.Label(self.root, text="Status: Prêt pour initialisation rapide",
                                   bg='#0d1117', fg='#7c3aed', font=('Consolas', 10))
        self.status_label.pack(pady=5)

    def log(self, message: str, color: str = None):
        """Log avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_msg)
        if color:
            # Coloration simple pour les messages importants
            if "✅" in message:
                self.log_text.tag_add("success", f"end-{len(log_msg)}c", "end-1c")
                self.log_text.tag_config("success", foreground="#28a745")
            elif "❌" in message:
                self.log_text.tag_add("error", f"end-{len(log_msg)}c", "end-1c") 
                self.log_text.tag_config("error", foreground="#dc3545")
                
        self.log_text.see(tk.END)
        self.root.update()

    def detect_rode(self):
        """Détection du Rode NT-USB"""
        self.log("🔍 Scan rapide Rode NT-USB...")
        
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if 'RODE' in device['name'].upper() and device['max_input_channels'] > 0:
                self.rode_device_id = i
                self.log(f"✅ RODE DÉTECTÉ: {device['name']} (ID: {i})")
                return True
                
        self.log("❌ Rode NT-USB non détecté")
        return False

    def fast_init(self):
        """Initialisation rapide Engine V5"""
        def init_thread():
            try:
                self.status_label.config(text="Status: Initialisation rapide en cours...")
                start_time = time.time()
                
                self.log("=" * 60)
                self.log("🚀 INITIALISATION RAPIDE ENGINE V5")
                self.log("=" * 60)
                self.log("⚡ Optimisations rapides activées:")
                for key, value in FAST_INIT_CONFIG.items():
                    if value:
                        self.log(f"   ✅ {key}")
                
                # 1. Détection Rode
                if not self.detect_rode():
                    self.log("❌ Arrêt: Rode requis")
                    return
                    
                # 2. Import Engine
                self.log("📦 Import Engine V5...")
                from core.whisper_engine_v5 import SuperWhisper2EngineV5
                self.log("✅ Import terminé")
                
                # 3. Création instance
                self.log("⚙️ Création instance...")
                self.engine = SuperWhisper2EngineV5()
                self.engine.set_transcription_callback(self.on_transcription)
                
                # 4. Configuration rapide
                self.log("⚡ Configuration optimisations rapides...")
                self.configure_fast_mode()
                
                # 5. Démarrage
                self.log("🚀 Démarrage Engine V5 mode rapide...")
                success = self.engine.start_engine()
                
                init_time = time.time() - start_time
                
                if success:
                    self.log(f"✅ ENGINE V5 READY en {init_time:.1f}s !")
                    self.status_label.config(text=f"Status: Engine V5 Ready ({init_time:.1f}s)")
                    self.init_btn.config(state='disabled')
                    self.start_btn.config(state='normal')
                else:
                    self.log("❌ Échec initialisation")
                    self.status_label.config(text="Status: Échec initialisation")
                    
            except Exception as e:
                self.log(f"❌ Erreur init: {e}")
                self.status_label.config(text="Status: Erreur initialisation")
                
        # Lancer dans un thread pour ne pas bloquer l'UI
        threading.Thread(target=init_thread, daemon=True).start()

    def configure_fast_mode(self):
        """Configure le mode rapide sur l'engine"""
        if hasattr(self.engine, 'model_optimizer') and self.engine.model_optimizer:
            # Désactiver optimisations coûteuses
            self.log("⚡ Désactivation quantification INT8...")
            self.engine.quantization_active = False
            
        if hasattr(self.engine, 'vram_cache_gb'):
            # Cache VRAM réduit
            self.log("💾 Cache VRAM réduit: 1GB")
            self.engine.vram_cache_gb = 1
            
        # Configuration audio simple
        if hasattr(self.engine, 'streaming_manager'):
            self.log("🎤 Configuration audio simple")

    def on_transcription(self, text: str):
        """Callback transcription"""
        self.callbacks_received += 1
        timestamp = time.time()
        
        self.transcription_segments.append({
            'text': text,
            'timestamp': timestamp,
            'source': 'engine_v5'
        })
        
        self.log(f"📝 [{self.callbacks_received}] {text}")

    def start_test(self):
        """Démarrer le test"""
        if not self.engine:
            self.log("❌ Engine non initialisé")
            return
            
        self.test_active = True
        self.callbacks_received = 0
        self.transcription_segments = []
        
        self.log("=" * 50)
        self.log("▶️ DÉBUT DU TEST")
        self.log("=" * 50)
        self.log("📖 LISEZ LE TEXTE DE VALIDATION:")
        self.log("─" * 50)
        
        # Afficher le texte par chunks
        words = self.reference_text.split()
        for i in range(0, len(words), 20):
            chunk = " ".join(words[i:i+20])
            self.log(chunk)
            
        self.log("─" * 50)
        self.status_label.config(text="Status: Test en cours - Parlez maintenant!")
        
        # Monitoring
        self.monitor_test()

    def monitor_test(self):
        """Surveillance du test"""
        def monitor():
            start_time = time.time()
            while self.test_active:
                elapsed = time.time() - start_time
                if elapsed > 5 and self.callbacks_received == 0:
                    self.log("⚠️ Aucun callback après 5s")
                    
                time.sleep(1)
                
        threading.Thread(target=monitor, daemon=True).start()

    def stop_test(self):
        """Arrêter le test"""
        self.test_active = False
        self.log("⏹️ ARRÊT DU TEST")
        self.analyze_results()

    def analyze_results(self):
        """Analyse des résultats"""
        if not self.transcription_segments:
            self.log("❌ Aucune transcription reçue")
            return
            
        self.log("=" * 50)
        self.log("📊 ANALYSE DES RÉSULTATS")
        self.log("=" * 50)
        
        # Concaténer transcription
        full_transcription = " ".join([seg['text'] for seg in self.transcription_segments])
        
        # Calcul WER simple
        ref_words = self.reference_text.lower().split()
        trans_words = full_transcription.lower().split()
        
        similarity = difflib.SequenceMatcher(None, self.reference_text.lower(), 
                                           full_transcription.lower()).ratio()
        
        self.log(f"📊 Segments reçus: {len(self.transcription_segments)}")
        self.log(f"📊 Callbacks: {self.callbacks_received}")
        self.log(f"📊 Similarité: {similarity*100:.1f}%")
        
        # Sauvegarder
        self.save_results(full_transcription, similarity)

    def save_results(self, transcription: str, similarity: float):
        """Sauvegarde des résultats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fast_init_test_{timestamp}"
        
        # JSON
        results = {
            'timestamp': datetime.now().isoformat(),
            'fast_init_config': FAST_INIT_CONFIG,
            'callbacks': self.callbacks_received,
            'segments': len(self.transcription_segments),
            'similarity': similarity * 100,
            'reference_text': self.reference_text,
            'transcription': transcription,
            'segments_data': self.transcription_segments
        }
        
        with open(f"{filename}.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        self.log(f"💾 Résultats sauvés: {filename}.json")

    def run(self):
        """Lancer l'application"""
        self.log("🚀 Engine V5 Fast Init Tester Ready!")
        self.log("💡 Cliquez 'INIT RAPIDE' pour commencer")
        self.root.mainloop()

if __name__ == "__main__":
    app = FastEngineV5Tester()
    app.run() 