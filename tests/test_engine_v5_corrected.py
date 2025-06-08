#!/usr/bin/env python3
"""
Test Simple Engine V5 SuperWhisper2 - VERSION CORRIGEE
Interface minimale pour test direct du moteur
RTX 3090 + Engine V5 + Console Output
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

class SimpleEngineV5Test:
    def __init__(self):
        self.engine = None
        self.listening = False
        self.transcription_complete = ""
        self.transcription_segments = []
        self.start_time = None
        self.latencies = []
        
        # Interface minimale
        self.root = tk.Tk()
        self.root.title("Test Engine V5 SuperWhisper2 - Corrigé")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1a1a1a")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Interface utilisateur minimale"""
        # Titre
        title = tk.Label(self.root, 
                        text="🚀 TEST ENGINE V5 - SuperWhisper2",
                        font=("Consolas", 18, "bold"),
                        bg="#1a1a1a", fg="#00ff88")
        title.pack(pady=15)
        
        # Sous-titre
        subtitle = tk.Label(self.root,
                           text="RTX 3090 • Phase 3 • INT8 Quantification • Performance <1s",
                           font=("Consolas", 11),
                           bg="#1a1a1a", fg="#888888")
        subtitle.pack(pady=5)
        
        # Boutons de contrôle
        btn_frame = tk.Frame(self.root, bg="#1a1a1a")
        btn_frame.pack(pady=15)
        
        self.init_btn = tk.Button(btn_frame,
                                 text="🔧 INITIALISER ENGINE V5",
                                 command=self.init_engine,
                                 bg="#0066cc", fg="white",
                                 font=("Consolas", 11, "bold"),
                                 width=25, height=2)
        self.init_btn.pack(side="left", padx=5)
        
        self.start_btn = tk.Button(btn_frame,
                                  text="🎤 DEMARRER TEST",
                                  command=self.start_test,
                                  bg="#00aa00", fg="white",
                                  font=("Consolas", 11, "bold"),
                                  width=25, height=2,
                                  state="disabled")
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(btn_frame,
                                 text="⏹️ ARRETER TEST",
                                 command=self.stop_test,
                                 bg="#cc0000", fg="white",
                                 font=("Consolas", 11, "bold"),
                                 width=25, height=2,
                                 state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        self.analyze_btn = tk.Button(btn_frame,
                                    text="📊 ANALYSER RESULTATS",
                                    command=self.analyze_results,
                                    bg="#ff6600", fg="white",
                                    font=("Consolas", 11, "bold"),
                                    width=25, height=2,
                                    state="disabled")
        self.analyze_btn.pack(side="left", padx=5)
        
        # Status
        self.status_label = tk.Label(self.root,
                                    text="🔴 Status: Non initialisé",
                                    font=("Consolas", 14, "bold"),
                                    bg="#1a1a1a", fg="#ffaa00")
        self.status_label.pack(pady=10)
        
        # Zone d'affichage transcription temps réel
        transcription_frame = tk.LabelFrame(self.root,
                                          text="TRANSCRIPTION TEMPS RÉEL",
                                          font=("Consolas", 12, "bold"),
                                          bg="#1a1a1a", fg="#00ff88")
        transcription_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.transcription_text = scrolledtext.ScrolledText(transcription_frame,
                                                          font=("Consolas", 10),
                                                          bg="#000000", fg="#00ff88",
                                                          wrap=tk.WORD,
                                                          height=15)
        self.transcription_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Zone de statistiques
        stats_frame = tk.LabelFrame(self.root,
                                   text="📈 STATISTIQUES TEMPS RÉEL",
                                   font=("Consolas", 11, "bold"), 
                                   bg="#1a1a1a", fg="#00ff88")
        stats_frame.pack(fill="x", padx=15, pady=5)
        
        self.stats_text = tk.Text(stats_frame,
                                 font=("Consolas", 10),
                                 bg="#000000", fg="#00ff88",
                                 height=3)
        self.stats_text.pack(fill="x", padx=10, pady=5)
        
    def log_message(self, message, color="#00ff88"):
        """Affiche message dans console et interface"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        full_message = f"[{timestamp}] {message}"
        
        # Console
        print(full_message)
        
        # Interface
        self.transcription_text.insert(tk.END, full_message + "\n")
        self.transcription_text.see(tk.END)
        self.root.update()
        
    def init_engine(self):
        """Initialisation Engine V5"""
        self.log_message("🚀 INITIALISATION ENGINE V5 - PHASE 3...")
        self.status_label.config(text="🟡 Status: Initialisation en cours...", fg="#ffaa00")
        self.init_btn.config(state="disabled")
        
        def init_thread():
            try:
                # Import Engine V5 - Chemin corrigé
                self.log_message("📦 Import SuperWhisper2 Engine V5...")
                from src.core.whisper_engine_v5 import SuperWhisper2EngineV5
                
                self.log_message("⚙️ Création instance Engine V5...")
                self.engine = SuperWhisper2EngineV5()
                
                # Configurer le microphone Rode automatiquement
                self.log_message("🎤 Configuration microphone Rode...")
                self.configure_rode_microphone()
                
                self.log_message("🎮 Configuration RTX 3090 + Phase 3...")
                success = self.engine.start_engine()
                
                if success:
                    self.log_message("✅ ENGINE V5 PRÊT - PHASE 3 ACTIVÉE!", "#00ff88")
                    self.status_label.config(text="🟢 Status: Engine V5 initialisé", fg="#00ff88")
                    self.start_btn.config(state="normal")
                else:
                    raise Exception("Échec start_engine()")
                
            except Exception as e:
                error_msg = f"❌ ERREUR INITIALISATION: {str(e)}"
                self.log_message(error_msg, "#ff0000")
                self.status_label.config(text="🔴 Status: Erreur initialisation", fg="#ff0000")
                self.init_btn.config(state="normal")
                messagebox.showerror("Erreur Engine V5", error_msg)
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def configure_rode_microphone(self):
        """Détecte et configure automatiquement le microphone Rode"""
        try:
            import sounddevice as sd
            
            self.log_message("🔍 Détection microphone Rode...")
            
            # Obtenir liste des périphériques
            devices = sd.query_devices()
            rode_device = None
            rode_device_id = None
            
            # Rechercher microphone Rode
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                if any(keyword in device_name for keyword in ['rode', 'procaster', 'podmic', 'podcaster']):
                    if device['max_input_channels'] > 0:  # Vérifier que c'est un device d'entrée
                        rode_device = device
                        rode_device_id = i
                        break
            
            if rode_device:
                self.log_message(f"✅ Microphone Rode détecté: {rode_device['name']}")
                self.log_message(f"📊 Device ID: {rode_device_id}")
                self.log_message(f"📊 Sample Rate: {rode_device['default_samplerate']} Hz")
                self.log_message(f"📊 Canaux: {rode_device['max_input_channels']}")
                
                # Configurer comme device par défaut
                sd.default.device[0] = rode_device_id  # Input device
                
                self.log_message("🎤 Microphone Rode configuré comme device par défaut")
                
                # Test rapide du microphone
                self.test_microphone_level(rode_device_id)
                
            else:
                self.log_message("⚠️ Microphone Rode non détecté, utilisation device par défaut")
                self.log_message("🔍 Devices audio disponibles:")
                for i, device in enumerate(devices):
                    if device['max_input_channels'] > 0:
                        self.log_message(f"  [{i}] {device['name']}")
                
        except Exception as e:
            self.log_message(f"⚠️ Erreur configuration microphone: {str(e)}", "#ffaa00")
    
    def test_microphone_level(self, device_id):
        """Test rapide du niveau audio du microphone"""
        try:
            import sounddevice as sd
            import numpy as np
            
            self.log_message("🎤 Test niveau microphone (2 secondes)...")
            
            # Enregistrer 2 secondes d'audio
            duration = 2.0
            sample_rate = 16000
            
            audio_data = sd.rec(int(duration * sample_rate), 
                               samplerate=sample_rate, 
                               channels=1, 
                               device=device_id,
                               dtype=np.float32)
            sd.wait()
            
            # Calculer niveau RMS
            rms_level = np.sqrt(np.mean(audio_data ** 2))
            max_level = np.max(np.abs(audio_data))
            
            self.log_message(f"📊 Niveau RMS: {rms_level:.4f}")
            self.log_message(f"📊 Niveau Max: {max_level:.4f}")
            
            if rms_level > 0.001:
                self.log_message("✅ Microphone fonctionnel - Niveau audio détecté")
            else:
                self.log_message("⚠️ Niveau audio très faible - Vérifiez le microphone", "#ffaa00")
                
        except Exception as e:
            self.log_message(f"⚠️ Erreur test microphone: {str(e)}", "#ffaa00")
        
    def start_test(self):
        """Démarre le test de transcription"""
        if not self.engine:
            messagebox.showerror("Erreur", "Engine V5 non initialisé!")
            return
            
        self.log_message("=" * 60, "#ffaa00")
        self.log_message("🎤 DÉBUT TEST ENGINE V5 - LISEZ LE TEXTE!", "#ffaa00")
        self.log_message("=" * 60, "#ffaa00")
        
        # Reset données
        self.transcription_complete = ""
        self.transcription_segments = []
        self.latencies = []
        self.start_time = time.time()
        self.listening = True
        
        # Configuration callback pour Engine V5
        def on_transcription_callback(text: str):
            if not self.listening:
                return
                
            # Enregistrer segment avec timing
            timestamp = time.time() - self.start_time
            self.transcription_segments.append({
                'text': text,
                'timestamp': timestamp,
                'latency': 0.0  # Engine V5 calcule latence interne
            })
            
            # Ajouter à transcription complète
            self.transcription_complete += text + " "
            
            # Affichage temps réel avec couleur
            self.log_message(f"🎯 [TRANSCRIPTION] {text}", "#00ffff")
            
            # Mise à jour stats
            self.update_live_stats()
        
        try:
            # Configurer callback Engine V5
            self.engine.set_transcription_callback(on_transcription_callback)
            
            # Mise à jour UI
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="🔴 RECORDING - PARLEZ MAINTENANT!", fg="#ff0000")
            
            self.log_message("✅ Engine V5 en écoute - Streaming actif")
            
        except Exception as e:
            error_msg = f"❌ ERREUR DÉMARRAGE: {str(e)}"
            self.log_message(error_msg, "#ff0000")
            messagebox.showerror("Erreur", error_msg)
    
    def stop_test(self):
        """Arrête le test"""
        if not self.listening:
            return
            
        self.listening = False
        self.log_message("=" * 60, "#ffaa00")
        self.log_message("⏹️ ARRÊT TEST ENGINE V5", "#ffaa00")
        self.log_message("=" * 60, "#ffaa00")
        
        try:
            # Mise à jour UI
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.analyze_btn.config(state="normal")
            self.status_label.config(text="🟢 Status: Test terminé", fg="#00aa00")
            
            total_time = time.time() - self.start_time if self.start_time else 0
            self.log_message(f"📊 Test terminé - Durée: {total_time:.1f}s")
            self.log_message("📊 Cliquez 'ANALYSER RESULTATS' pour statistiques détaillées")
            
        except Exception as e:
            error_msg = f"❌ ERREUR ARRÊT: {str(e)}"
            self.log_message(error_msg, "#ff0000")
    
    def update_live_stats(self):
        """Mise à jour statistiques temps réel"""
        if not self.transcription_segments:
            return
            
        nb_segments = len(self.transcription_segments)
        total_chars = len(self.transcription_complete)
        elapsed = time.time() - self.start_time if self.start_time else 0
        chars_per_sec = total_chars / elapsed if elapsed > 0 else 0
        
        stats = f"📊 Segments: {nb_segments} | Caractères: {total_chars} | Temps: {elapsed:.1f}s | Vitesse: {chars_per_sec:.1f} car/s"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)
    
    def analyze_results(self):
        """Analyse détaillée des résultats vs texte de référence"""
        if not self.transcription_complete.strip():
            messagebox.showwarning("Attention", "Aucune transcription à analyser!")
            return
            
        self.log_message("=" * 60, "#ffaa00")
        self.log_message("📊 ANALYSE DÉTAILLÉE ENGINE V5", "#ffaa00")
        self.log_message("=" * 60, "#ffaa00")
        
        # Nettoyage textes pour comparaison
        ref_clean = self.clean_text_for_comparison(TEXTE_REFERENCE)
        trans_clean = self.clean_text_for_comparison(self.transcription_complete)
        
        # Statistiques générales
        self.log_message("--- 📈 STATISTIQUES GÉNÉRALES ---")
        self.log_message(f"📝 Texte référence: {len(TEXTE_REFERENCE)} caractères, {len(ref_clean.split())} mots")
        self.log_message(f"🎤 Transcription: {len(self.transcription_complete)} caractères, {len(trans_clean.split())} mots")
        
        # Performance temporelle
        total_time = time.time() - self.start_time if self.start_time else 1
        nb_segments = len(self.transcription_segments)
        self.log_message(f"⏱️ Durée totale: {total_time:.1f}s")
        self.log_message(f"📦 Segments de transcription: {nb_segments}")
        
        # Analyse de précision
        self.log_message("--- 🎯 ANALYSE DE PRÉCISION ---")
        
        # Similarité globale
        similarity = difflib.SequenceMatcher(None, ref_clean, trans_clean).ratio()
        self.log_message(f"🎯 Similarité globale: {similarity*100:.1f}%")
        
        # Analyse par mots
        ref_words = ref_clean.split()
        trans_words = trans_clean.split()
        
        # Calcul précision WER (Word Error Rate)
        word_errors = self.calculate_wer(ref_words, trans_words)
        wer = (word_errors / len(ref_words) * 100) if ref_words else 0
        word_accuracy = 100 - wer
        
        self.log_message(f"📊 Précision mots: {word_accuracy:.1f}% (WER: {wer:.1f}%)")
        self.log_message(f"📊 Erreurs mots: {word_errors}/{len(ref_words)}")
        
        # Analyse par segments de complexité
        self.analyze_complexity_segments(trans_clean)
        
        # Erreurs fréquentes
        self.analyze_common_errors(ref_clean, trans_clean)
        
        # Performance Engine V5
        self.analyze_engine_performance()
        
        # Sauvegarde résultats
        self.save_test_results(similarity, word_accuracy, total_time)
        
        self.log_message("=" * 60, "#00ff88")
        self.log_message("✅ ANALYSE TERMINÉE - ENGINE V5", "#00ff88")
        self.log_message("=" * 60, "#00ff88")
    
    def calculate_wer(self, ref_words, hyp_words):
        """Calcule le Word Error Rate (WER)"""
        # Algorithme simple de distance d'édition
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
    
    def clean_text_for_comparison(self, text):
        """Nettoie le texte pour comparaison précise"""
        # Suppression ponctuation, accents, mise en minuscules
        cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Normalisation accents français
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
    
    def analyze_complexity_segments(self, transcription):
        """Analyse par segments de complexité"""
        self.log_message("--- 🧩 ANALYSE PAR COMPLEXITÉ ---")
        
        segments = [
            ("🔤 Mots simples", ["chat", "chien", "maison", "voiture", "ordinateur", "telephone"]),
            ("🔧 Termes techniques", ["algorithme", "machine learning", "gpu", "rtx", "faster whisper", "quantification", "int8"]),
            ("🔢 Nombres/Dates", ["vingt trois", "quarante sept", "mille neuf cent", "quinze janvier", "deux mille"]),
            ("💎 Mots difficiles", ["chrysantheme", "anticonstitutionnellement", "prestidigitateur", "kakemono", "yaourt"])
        ]
        
        for segment_name, keywords in segments:
            found = sum(1 for keyword in keywords if keyword in transcription.lower())
            total = len(keywords)
            percentage = (found / total * 100) if total > 0 else 0
            status = "✅" if percentage >= 70 else "⚠️" if percentage >= 50 else "❌"
            self.log_message(f"{status} {segment_name}: {found}/{total} ({percentage:.1f}%)")
    
    def analyze_common_errors(self, reference, transcription):
        """Analyse des erreurs courantes"""
        self.log_message("--- 🐛 ERREURS COURANTES ---")
        
        ref_words = reference.split()
        trans_words = transcription.split()
        
        # Mots manqués
        ref_counter = Counter(ref_words)
        trans_counter = Counter(trans_words)
        
        missing_words = []
        for word, count in ref_counter.items():
            if trans_counter[word] < count:
                missing_words.append(word)
        
        if missing_words:
            self.log_message(f"❌ Mots manqués: {', '.join(missing_words[:15])}")
        else:
            self.log_message("✅ Aucun mot manqué détecté")
        
        # Mots ajoutés (hallucinations possibles)
        added_words = []
        for word, count in trans_counter.items():
            if ref_counter[word] < count:
                added_words.append(word)
        
        if added_words:
            self.log_message(f"➕ Mots ajoutés: {', '.join(added_words[:10])}")
        else:
            self.log_message("✅ Aucune hallucination détectée")
    
    def analyze_engine_performance(self):
        """Analyse performance spécifique Engine V5"""
        self.log_message("--- ⚡ PERFORMANCE ENGINE V5 ---")
        
        if self.engine and hasattr(self.engine, 'get_phase3_status'):
            try:
                status = self.engine.get_phase3_status()
                
                self.log_message("🎮 Optimisations Phase 3:")
                for opt_name, enabled in status.get('optimizations', {}).items():
                    status_icon = "✅" if enabled else "❌"
                    self.log_message(f"  {status_icon} {opt_name}")
                    
                gpu_info = status.get('gpu_info', {})
                if gpu_info:
                    self.log_message(f"🎮 GPU: {gpu_info.get('name', 'N/A')}")
                    self.log_message(f"💾 VRAM: {gpu_info.get('memory_gb', 0):.1f}GB")
                    
            except Exception as e:
                self.log_message(f"⚠️ Impossible de récupérer le statut Engine V5: {e}")
        else:
            self.log_message("⚠️ Statut Engine V5 non disponible")
    
    def save_test_results(self, similarity, word_accuracy, total_time):
        """Sauvegarde résultats détaillés"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_engine_v5_corrected_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("RÉSULTATS TEST ENGINE V5 SuperWhisper2 - PHASE 3\n")
                f.write("=" * 80 + "\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"GPU: RTX 3090 24GB\n")
                f.write(f"Phase: 3 (INT8 Quantification)\n\n")
                
                f.write("MÉTRIQUES PRINCIPALES\n")
                f.write("-" * 40 + "\n")
                f.write(f"Similarité globale: {similarity*100:.1f}%\n")
                f.write(f"Précision mots: {word_accuracy:.1f}%\n")
                f.write(f"Durée totale: {total_time:.1f}s\n")
                f.write(f"Segments: {len(self.transcription_segments)}\n\n")
                
                f.write("TEXTE DE RÉFÉRENCE\n")
                f.write("-" * 40 + "\n")
                f.write(TEXTE_REFERENCE + "\n\n")
                
                f.write("TRANSCRIPTION COMPLÈTE\n")
                f.write("-" * 40 + "\n")
                f.write(self.transcription_complete + "\n\n")
                
                f.write("SEGMENTS DÉTAILLÉS\n")
                f.write("-" * 40 + "\n")
                for i, segment in enumerate(self.transcription_segments):
                    f.write(f"[{i+1}] {segment['timestamp']:.1f}s: {segment['text']}\n")
            
            self.log_message(f"💾 Résultats sauvegardés: {filename}", "#00ff88")
            
        except Exception as e:
            self.log_message(f"❌ Erreur sauvegarde: {str(e)}", "#ff0000")
    
    def run(self):
        """Lance l'interface"""
        self.log_message("=" * 80)
        self.log_message("🚀 TEST ENGINE V5 SuperWhisper2 - PHASE 3")
        self.log_message("=" * 80)
        self.log_message("📋 PROCÉDURE:")
        self.log_message("1. 🔧 Cliquez 'INITIALISER ENGINE V5'")
        self.log_message("2. 🎤 Cliquez 'DEMARRER TEST'")
        self.log_message("3. 📖 Lisez le texte de validation à voix haute")
        self.log_message("4. ⏹️ Cliquez 'ARRETER TEST'")
        self.log_message("5. 📊 Cliquez 'ANALYSER RESULTATS' pour statistiques")
        self.log_message("")
        self.log_message("📝 TEXTE DE VALIDATION À LIRE:")
        self.log_message("-" * 80)
        self.log_message(TEXTE_REFERENCE)
        self.log_message("=" * 80)
        
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    print("🚀 Lancement Test Engine V5 SuperWhisper2 - Version Corrigée...")
    
    try:
        test = SimpleEngineV5Test()
        test.run()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur fatale: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()