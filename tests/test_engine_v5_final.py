#!/usr/bin/env python3
"""
Test Final Engine V5 SuperWhisper2 - MICROPHONE RODE
Version avec sélection automatique microphone Rode
RTX 3090 + Engine V5 + Rode ProcasterCD/PodMic
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
import re
import difflib
from collections import Counter
import sounddevice as sd
import numpy as np

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

class FinalEngineV5Test:
    def __init__(self):
        self.engine = None
        self.listening = False
        self.transcription_complete = ""
        self.transcription_segments = []
        self.start_time = None
        self.rode_device_id = None
        
        # Interface simplifiée
        self.root = tk.Tk()
        self.root.title("🎤 Test Final Engine V5 - Microphone Rode")
        self.root.geometry("1400x800")
        self.root.configure(bg="#0d1117")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Interface utilisateur optimisée"""
        # Header
        header = tk.Frame(self.root, bg="#0d1117")
        header.pack(fill="x", pady=20)
        
        title = tk.Label(header, 
                        text="🎤 TEST ENGINE V5 - MICROPHONE RODE",
                        font=("Segoe UI", 20, "bold"),
                        bg="#0d1117", fg="#f0f6fc")
        title.pack()
        
        subtitle = tk.Label(header,
                           text="SuperWhisper2 Phase 3 • RTX 3090 • INT8 Quantification • Rode ProcasterCD/PodMic",
                           font=("Segoe UI", 12),
                           bg="#0d1117", fg="#7c3aed")
        subtitle.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self.root, bg="#0d1117")
        btn_frame.pack(pady=20)
        
        self.init_btn = tk.Button(btn_frame,
                                 text="🔧 INITIALISER + RODE",
                                 command=self.init_engine_with_rode,
                                 bg="#238636", fg="white",
                                 font=("Segoe UI", 12, "bold"),
                                 width=25, height=2,
                                 relief="flat")
        self.init_btn.pack(side="left", padx=10)
        
        self.start_btn = tk.Button(btn_frame,
                                  text="🎙️ DEMARRER TEST",
                                  command=self.start_test,
                                  bg="#1f6feb", fg="white",
                                  font=("Segoe UI", 12, "bold"),
                                  width=25, height=2,
                                  state="disabled", relief="flat")
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = tk.Button(btn_frame,
                                 text="⏹️ ARRETER TEST", 
                                 command=self.stop_test,
                                 bg="#da3633", fg="white",
                                 font=("Segoe UI", 12, "bold"),
                                 width=25, height=2,
                                 state="disabled", relief="flat")
        self.stop_btn.pack(side="left", padx=10)
        
        self.analyze_btn = tk.Button(btn_frame,
                                    text="📊 ANALYSER",
                                    command=self.analyze_results,
                                    bg="#fb8500", fg="white",
                                    font=("Segoe UI", 12, "bold"),
                                    width=25, height=2,
                                    state="disabled", relief="flat")
        self.analyze_btn.pack(side="left", padx=10)
        
        # Status
        self.status_label = tk.Label(self.root,
                                    text="🔴 Status: Prêt pour initialisation",
                                    font=("Segoe UI", 14, "bold"),
                                    bg="#0d1117", fg="#f85149")
        self.status_label.pack(pady=15)
        
        # Output area
        output_frame = tk.Frame(self.root, bg="#0d1117")
        output_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Transcription
        trans_frame = tk.LabelFrame(output_frame,
                                   text="🎯 TRANSCRIPTION TEMPS RÉEL",
                                   font=("Segoe UI", 12, "bold"),
                                   bg="#0d1117", fg="#58a6ff",
                                   labelanchor="n")
        trans_frame.pack(fill="both", expand=True, pady=5)
        
        self.transcription_text = scrolledtext.ScrolledText(trans_frame,
                                                          font=("Consolas", 11),
                                                          bg="#161b22", fg="#e6edf3",
                                                          wrap=tk.WORD,
                                                          height=20,
                                                          insertbackground="#f0f6fc")
        self.transcription_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Stats
        stats_frame = tk.LabelFrame(output_frame,
                                   text="📈 STATISTIQUES",
                                   font=("Segoe UI", 11, "bold"),
                                   bg="#0d1117", fg="#58a6ff")
        stats_frame.pack(fill="x", pady=5)
        
        self.stats_text = tk.Text(stats_frame,
                                 font=("Consolas", 10),
                                 bg="#161b22", fg="#e6edf3",
                                 height=4,
                                 insertbackground="#f0f6fc")
        self.stats_text.pack(fill="x", padx=10, pady=5)
        
        # Instructions
        self.show_instructions()
        
    def show_instructions(self):
        """Affiche les instructions initiales"""
        instructions = """=== INSTRUCTIONS TEST ENGINE V5 ===

🔧 1. INITIALISER + RODE → Configure Engine V5 + détecte microphone Rode
🎙️ 2. DEMARRER TEST → Active la transcription temps réel
📖 3. LISEZ LE TEXTE DE VALIDATION → Parlez clairement dans le microphone
⏹️ 4. ARRETER TEST → Termine l'enregistrement
📊 5. ANALYSER → Affiche les statistiques de précision détaillées

=== TEXTE DE VALIDATION À LIRE ===
""" + TEXTE_REFERENCE + "\n\n" + "="*80
        
        self.transcription_text.insert(tk.END, instructions)
        
    def log_message(self, message, color="#e6edf3"):
        """Affiche message avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        full_message = f"[{timestamp}] {message}"
        
        print(full_message)
        
        self.transcription_text.insert(tk.END, full_message + "\n")
        self.transcription_text.see(tk.END)
        self.root.update()
        
    def detect_rode_microphone(self):
        """Détecte automatiquement le microphone Rode"""
        try:
            self.log_message("🔍 Détection microphone Rode...")
            
            devices = sd.query_devices()
            self.log_message(f"📊 {len(devices)} périphériques audio détectés")
            
            # Recherche prioritaire Rode
            rode_keywords = ['rode', 'procaster', 'podmic', 'podcaster', 'procastercd']
            
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                
                # Log tous les devices d'entrée pour debug
                if device['max_input_channels'] > 0:
                    self.log_message(f"  [{i}] {device['name']} ({device['max_input_channels']} canaux)")
                
                # Vérifier si c'est un Rode
                for keyword in rode_keywords:
                    if keyword in device_name and device['max_input_channels'] > 0:
                        self.rode_device_id = i
                        self.log_message(f"✅ RODE DÉTECTÉ: {device['name']}")
                        self.log_message(f"📊 Device ID: {i}")
                        self.log_message(f"📊 Sample Rate: {device['default_samplerate']} Hz")
                        return True
            
            # Fallback: recherche plus large
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    device_name = device['name'].lower()
                    if 'usb' in device_name or 'microphone' in device_name:
                        self.rode_device_id = i
                        self.log_message(f"⚠️ FALLBACK USB/Micro: {device['name']}")
                        return True
            
            self.log_message("❌ Aucun microphone Rode détecté")
            return False
            
        except Exception as e:
            self.log_message(f"❌ Erreur détection microphone: {str(e)}")
            return False
    
    def test_rode_microphone(self):
        """Test du microphone Rode détecté"""
        if self.rode_device_id is None:
            return False
            
        try:
            self.log_message("🎤 Test microphone Rode (3 secondes)...")
            self.status_label.config(text="🟡 Test microphone en cours...", fg="#f1c40f")
            
            # Test enregistrement
            duration = 3.0
            sample_rate = 16000
            
            audio_data = sd.rec(int(duration * sample_rate),
                               samplerate=sample_rate,
                               channels=1,
                               device=self.rode_device_id,
                               dtype=np.float32)
            sd.wait()
            
            # Analyse niveau audio
            rms_level = np.sqrt(np.mean(audio_data ** 2))
            max_level = np.max(np.abs(audio_data))
            
            self.log_message(f"📊 Niveau RMS: {rms_level:.6f}")
            self.log_message(f"📊 Niveau Max: {max_level:.6f}")
            
            if rms_level > 0.0001:
                self.log_message("✅ Microphone Rode fonctionnel!")
                return True
            else:
                self.log_message("⚠️ Niveau audio faible - Vérifiez le gain")
                return True  # Continuer quand même
                
        except Exception as e:
            self.log_message(f"❌ Erreur test microphone: {str(e)}")
            return False
    
    def configure_sounddevice_for_rode(self):
        """Configure sounddevice pour utiliser le microphone Rode"""
        try:
            if self.rode_device_id is not None:
                # Configurer device par défaut
                sd.default.device[0] = self.rode_device_id
                sd.default.samplerate = 16000
                sd.default.channels = 1
                
                self.log_message(f"🎤 Sounddevice configuré pour device {self.rode_device_id}")
                return True
            return False
            
        except Exception as e:
            self.log_message(f"❌ Erreur configuration sounddevice: {str(e)}")
            return False
    
    def init_engine_with_rode(self):
        """Initialise Engine V5 avec microphone Rode"""
        self.log_message("🚀 INITIALISATION ENGINE V5 + RODE...")
        self.status_label.config(text="🟡 Initialisation en cours...", fg="#f1c40f")
        self.init_btn.config(state="disabled")
        
        def init_thread():
            try:
                # 1. Détecter microphone Rode
                if not self.detect_rode_microphone():
                    raise Exception("Microphone Rode non détecté")
                
                # 2. Tester microphone
                if not self.test_rode_microphone():
                    raise Exception("Test microphone Rode échoué")
                
                # 3. Configurer sounddevice
                if not self.configure_sounddevice_for_rode():
                    raise Exception("Configuration sounddevice échouée")
                
                # 4. Import et init Engine V5
                self.log_message("📦 Import SuperWhisper2 Engine V5...")
                from src.core.whisper_engine_v5 import SuperWhisper2EngineV5
                
                self.log_message("⚙️ Création instance Engine V5...")
                self.engine = SuperWhisper2EngineV5()
                
                # 5. Démarrer Engine V5
                self.log_message("🎮 Démarrage Engine V5 Phase 3...")
                success = self.engine.start_engine()
                
                if success:
                    self.log_message("✅ ENGINE V5 + RODE PRÊT!", "#2ecc71")
                    self.status_label.config(text="🟢 Engine V5 + Rode initialisé", fg="#2ecc71")
                    self.start_btn.config(state="normal")
                else:
                    raise Exception("Échec start_engine()")
                
            except Exception as e:
                error_msg = f"❌ ERREUR: {str(e)}"
                self.log_message(error_msg, "#e74c3c")
                self.status_label.config(text="🔴 Erreur initialisation", fg="#e74c3c")
                self.init_btn.config(state="normal")
                messagebox.showerror("Erreur", error_msg)
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def start_test(self):
        """Démarre le test avec microphone Rode"""
        if not self.engine or self.rode_device_id is None:
            messagebox.showerror("Erreur", "Engine V5 ou microphone Rode non configuré!")
            return
            
        self.log_message("="*80)
        self.log_message("🎙️ DÉBUT TEST AVEC MICROPHONE RODE")
        self.log_message("="*80)
        
        # Reset données
        self.transcription_complete = ""
        self.transcription_segments = []
        self.start_time = time.time()
        self.listening = True
        
        # Callback pour transcription
        def on_transcription_callback(text: str):
            if not self.listening:
                return
                
            timestamp = time.time() - self.start_time
            self.transcription_segments.append({
                'text': text,
                'timestamp': timestamp
            })
            
            self.transcription_complete += text + " "
            self.log_message(f"🎯 {text}", "#58a6ff")
            self.update_live_stats()
        
        try:
            # Configurer callback
            self.engine.set_transcription_callback(on_transcription_callback)
            
            # UI
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="🔴 ENREGISTREMENT ACTIF - PARLEZ!", fg="#e74c3c")
            
            self.log_message("✅ Engine V5 en écoute avec microphone Rode")
            self.log_message("📖 LISEZ LE TEXTE DE VALIDATION MAINTENANT!")
            
        except Exception as e:
            error_msg = f"❌ ERREUR DÉMARRAGE: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Erreur", error_msg)
    
    def stop_test(self):
        """Arrête le test"""
        if not self.listening:
            return
            
        self.listening = False
        self.log_message("="*80)
        self.log_message("⏹️ ARRÊT TEST")
        self.log_message("="*80)
        
        # UI
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.analyze_btn.config(state="normal")
        self.status_label.config(text="🟢 Test terminé", fg="#2ecc71")
        
        total_time = time.time() - self.start_time if self.start_time else 0
        self.log_message(f"📊 Durée: {total_time:.1f}s | Segments: {len(self.transcription_segments)}")
        self.log_message("📊 Cliquez 'ANALYSER' pour statistiques détaillées")
    
    def update_live_stats(self):
        """Stats temps réel"""
        if not self.transcription_segments:
            return
            
        nb_segments = len(self.transcription_segments)
        total_chars = len(self.transcription_complete)
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        stats = f"Segments: {nb_segments} | Caractères: {total_chars} | Temps: {elapsed:.1f}s"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)
    
    def analyze_results(self):
        """Analyse complète des résultats"""
        if not self.transcription_complete.strip():
            messagebox.showwarning("Attention", "Aucune transcription à analyser!")
            return
            
        self.log_message("="*80)
        self.log_message("📊 ANALYSE DÉTAILLÉE")
        self.log_message("="*80)
        
        # Nettoyage pour comparaison
        ref_clean = self.clean_text(TEXTE_REFERENCE)
        trans_clean = self.clean_text(self.transcription_complete)
        
        # Métriques principales
        similarity = difflib.SequenceMatcher(None, ref_clean, trans_clean).ratio()
        
        ref_words = ref_clean.split()
        trans_words = trans_clean.split()
        word_errors = self.calculate_wer(ref_words, trans_words)
        wer = (word_errors / len(ref_words) * 100) if ref_words else 0
        word_accuracy = 100 - wer
        
        total_time = time.time() - self.start_time if self.start_time else 1
        
        # Résultats
        self.log_message("--- 📈 RÉSULTATS ---")
        self.log_message(f"🎯 Similarité globale: {similarity*100:.1f}%")
        self.log_message(f"📊 Précision mots: {word_accuracy:.1f}% (WER: {wer:.1f}%)")
        self.log_message(f"⏱️ Durée totale: {total_time:.1f}s")
        self.log_message(f"📦 Segments: {len(self.transcription_segments)}")
        self.log_message(f"🎤 Microphone: Rode (Device {self.rode_device_id})")
        
        # Analyse par complexité
        self.analyze_complexity(trans_clean)
        
        # Sauvegarde
        self.save_results(similarity, word_accuracy, total_time)
        
        self.log_message("="*80)
        self.log_message("✅ ANALYSE TERMINÉE")
        self.log_message("="*80)
    
    def clean_text(self, text):
        """Nettoyage pour comparaison"""
        cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Normalisation accents
        replacements = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'ù': 'u', 'û': 'u', 'ü': 'u',
            'î': 'i', 'ï': 'i', 'ô': 'o', 'ö': 'o', 'ç': 'c'
        }
        
        for accented, plain in replacements.items():
            cleaned = cleaned.replace(accented, plain)
            
        return cleaned
    
    def calculate_wer(self, ref_words, hyp_words):
        """Word Error Rate"""
        m, n = len(ref_words), len(hyp_words)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
            
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if ref_words[i-1].lower() == hyp_words[j-1].lower():
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        
        return dp[m][n]
    
    def analyze_complexity(self, transcription):
        """Analyse par complexité"""
        self.log_message("--- 🧩 ANALYSE COMPLEXITÉ ---")
        
        segments = [
            ("Mots simples", ["chat", "chien", "maison", "voiture", "ordinateur", "telephone"]),
            ("Termes techniques", ["algorithme", "machine learning", "gpu", "rtx", "faster whisper", "quantification", "int8"]),
            ("Nombres", ["vingt trois", "quarante sept", "mille neuf cent", "quinze janvier", "deux mille"]),
            ("Mots difficiles", ["chrysantheme", "anticonstitutionnellement", "prestidigitateur", "kakemono", "yaourt"])
        ]
        
        for segment_name, keywords in segments:
            found = sum(1 for keyword in keywords if keyword in transcription.lower())
            total = len(keywords)
            percentage = (found / total * 100) if total > 0 else 0
            status = "✅" if percentage >= 70 else "⚠️" if percentage >= 50 else "❌"
            self.log_message(f"{status} {segment_name}: {found}/{total} ({percentage:.1f}%)")
    
    def save_results(self, similarity, word_accuracy, total_time):
        """Sauvegarde résultats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_engine_v5_rode_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("RÉSULTATS TEST ENGINE V5 + MICROPHONE RODE\n")
                f.write("="*80 + "\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"GPU: RTX 3090 24GB\n")
                f.write(f"Microphone: Rode (Device ID {self.rode_device_id})\n")
                f.write(f"Phase: 3 (INT8 Quantification)\n\n")
                
                f.write("MÉTRIQUES\n")
                f.write("-"*40 + "\n")
                f.write(f"Similarité: {similarity*100:.1f}%\n")
                f.write(f"Précision mots: {word_accuracy:.1f}%\n")
                f.write(f"Durée: {total_time:.1f}s\n")
                f.write(f"Segments: {len(self.transcription_segments)}\n\n")
                
                f.write("RÉFÉRENCE\n")
                f.write("-"*40 + "\n")
                f.write(TEXTE_REFERENCE + "\n\n")
                
                f.write("TRANSCRIPTION\n")
                f.write("-"*40 + "\n")
                f.write(self.transcription_complete + "\n\n")
                
                f.write("DÉTAILS\n")
                f.write("-"*40 + "\n")
                for i, segment in enumerate(self.transcription_segments):
                    f.write(f"[{i+1}] {segment['timestamp']:.1f}s: {segment['text']}\n")
            
            self.log_message(f"💾 Sauvegardé: {filename}")
            
        except Exception as e:
            self.log_message(f"❌ Erreur sauvegarde: {str(e)}")
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

def main():
    """Point d'entrée"""
    print("🎤 Lancement Test Final Engine V5 + Microphone Rode...")
    
    try:
        test = FinalEngineV5Test()
        test.run()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()