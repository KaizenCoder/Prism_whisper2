#!/usr/bin/env python3
"""
Test Simple Engine V5 SuperWhisper2
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

class SimpleEngineTest:
    def __init__(self):
        self.engine = None
        self.listening = False
        self.transcription_complete = ""
        self.transcription_segments = []
        self.start_time = None
        self.latencies = []
        
        # Interface minimale
        self.root = tk.Tk()
        self.root.title("Test Engine V5 SuperWhisper2 - Simple")
        self.root.geometry("1000x600")
        self.root.configure(bg="#1e1e1e")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Interface utilisateur minimale"""
        # Titre
        title = tk.Label(self.root, 
                        text="TEST ENGINE V5 - SuperWhisper2",
                        font=("Consolas", 16, "bold"),
                        bg="#1e1e1e", fg="#00ff00")
        title.pack(pady=10)
        
        # Boutons de contrôle
        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(pady=10)
        
        self.init_btn = tk.Button(btn_frame,
                                 text="INITIALISER ENGINE V5",
                                 command=self.init_engine,
                                 bg="#0080ff", fg="white",
                                 font=("Consolas", 12, "bold"),
                                 width=20, height=2)
        self.init_btn.pack(side="left", padx=5)
        
        self.start_btn = tk.Button(btn_frame,
                                  text="DEMARRER TEST",
                                  command=self.start_test,
                                  bg="#00ff00", fg="black",
                                  font=("Consolas", 12, "bold"),
                                  width=20, height=2,
                                  state="disabled")
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(btn_frame,
                                 text="ARRETER TEST",
                                 command=self.stop_test,
                                 bg="#ff0000", fg="white",
                                 font=("Consolas", 12, "bold"),
                                 width=20, height=2,
                                 state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        self.analyze_btn = tk.Button(btn_frame,
                                    text="ANALYSER RESULTATS",
                                    command=self.analyze_results,
                                    bg="#ff8000", fg="white",
                                    font=("Consolas", 12, "bold"),
                                    width=20, height=2,
                                    state="disabled")
        self.analyze_btn.pack(side="left", padx=5)
        
        # Status
        self.status_label = tk.Label(self.root,
                                    text="Status: Non initialisé",
                                    font=("Consolas", 12),
                                    bg="#1e1e1e", fg="#ffff00")
        self.status_label.pack(pady=5)
        
        # Zone d'affichage transcription temps réel
        transcription_frame = tk.LabelFrame(self.root,
                                          text="TRANSCRIPTION TEMPS RÉEL",
                                          font=("Consolas", 12, "bold"),
                                          bg="#1e1e1e", fg="#00ff00")
        transcription_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.transcription_text = scrolledtext.ScrolledText(transcription_frame,
                                                          font=("Consolas", 11),
                                                          bg="#000000", fg="#00ff00",
                                                          wrap=tk.WORD,
                                                          height=15)
        self.transcription_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Zone de statistiques
        stats_frame = tk.LabelFrame(self.root,
                                   text="STATISTIQUES",
                                   font=("Consolas", 10, "bold"), 
                                   bg="#1e1e1e", fg="#00ff00")
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.stats_text = tk.Text(stats_frame,
                                 font=("Consolas", 9),
                                 bg="#000000", fg="#00ff00",
                                 height=4)
        self.stats_text.pack(fill="x", padx=5, pady=2)
        
    def log_message(self, message, color="#00ff00"):
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
         self.log_message("INITIALISATION ENGINE V5...")
         self.status_label.config(text="Status: Initialisation en cours...", fg="#ffff00")
         
         def init_thread():
             try:
                 # Import Engine V5
                 from src.core.whisper_engine_v5 import SuperWhisper2EngineV5
                 
                 self.log_message("Création instance Engine V5...")
                 self.engine = SuperWhisper2EngineV5()
                 
                 self.log_message("Configuration GPU RTX 3090...")
                 self.engine.start_engine()
                 
                 self.log_message("ENGINE V5 PRET!", "#00ff00")
                 self.status_label.config(text="Status: Engine V5 initialisé", fg="#00ff00")
                 self.start_btn.config(state="normal")
                 
             except Exception as e:
                 error_msg = f"ERREUR INITIALISATION: {str(e)}"
                 self.log_message(error_msg, "#ff0000")
                 self.status_label.config(text="Status: Erreur initialisation", fg="#ff0000")
                 messagebox.showerror("Erreur", error_msg)
         
         threading.Thread(target=init_thread, daemon=True).start()
        
    def start_test(self):
        """Démarre le test de transcription"""
        if not self.engine:
            messagebox.showerror("Erreur", "Engine V5 non initialisé!")
            return
            
        self.log_message("=== DEBUT TEST ENGINE V5 ===", "#ffff00")
        self.log_message("Prêt à recevoir audio...")
        self.log_message("LISEZ LE TEXTE DE VALIDATION MAINTENANT!", "#ffff00")
        
        # Reset données
        self.transcription_complete = ""
        self.transcription_segments = []
        self.latencies = []
        self.start_time = time.time()
        self.listening = True
        
                 # Configuration callbacks
         def on_transcription_callback(text: str):
             if not self.listening:
                 return
                 
             # Enregistrer segment
             timestamp = time.time() - self.start_time
             self.transcription_segments.append({
                 'text': text,
                 'timestamp': timestamp,
                 'latency': 0.0  # Latence calculée séparément
             })
             
             # Ajouter à transcription complète
             self.transcription_complete += text + " "
             
             # Affichage temps réel
             self.log_message(f"[TRANSCRIPTION] {text}", "#00ffff")
             
             # Mise à jour stats
             self.update_live_stats()
         
         try:
             # Configurer callback et démarrer Engine V5
             self.engine.set_transcription_callback(on_transcription_callback)
            
            # Mise à jour UI
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="Status: Test en cours - PARLEZ!", fg="#ffff00")
            
        except Exception as e:
            error_msg = f"ERREUR DEMARRAGE: {str(e)}"
            self.log_message(error_msg, "#ff0000")
            messagebox.showerror("Erreur", error_msg)
    
    def stop_test(self):
        """Arrête le test"""
        if not self.listening:
            return
            
        self.listening = False
        self.log_message("=== ARRET TEST ENGINE V5 ===", "#ffff00")
        
        try:
            if self.engine:
                self.engine.stop_transcription()
                
            # Mise à jour UI
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.analyze_btn.config(state="normal")
            self.status_label.config(text="Status: Test terminé", fg="#00ff00")
            
            total_time = time.time() - self.start_time if self.start_time else 0
            self.log_message(f"Test terminé - Durée: {total_time:.1f}s")
            self.log_message("Utilisez 'ANALYSER RESULTATS' pour voir les statistiques détaillées")
            
        except Exception as e:
            error_msg = f"ERREUR ARRET: {str(e)}"
            self.log_message(error_msg, "#ff0000")
    
    def update_live_stats(self):
        """Mise à jour statistiques temps réel"""
        if not self.transcription_segments:
            return
            
        nb_segments = len(self.transcription_segments)
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        total_chars = len(self.transcription_complete)
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        stats = f"Segments: {nb_segments} | Latence moy: {avg_latency:.3f}s | Caractères: {total_chars} | Temps: {elapsed:.1f}s"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)
    
    def analyze_results(self):
        """Analyse détaillée des résultats vs texte de référence"""
        if not self.transcription_complete.strip():
            messagebox.showwarning("Attention", "Aucune transcription à analyser!")
            return
            
        self.log_message("=== ANALYSE DETAILLEE ===", "#ffff00")
        
        # Nettoyage textes pour comparaison
        ref_clean = self.clean_text_for_comparison(TEXTE_REFERENCE)
        trans_clean = self.clean_text_for_comparison(self.transcription_complete)
        
        # Statistiques générales
        self.log_message("--- STATISTIQUES GENERALES ---")
        self.log_message(f"Texte référence: {len(TEXTE_REFERENCE)} caractères, {len(ref_clean.split())} mots")
        self.log_message(f"Transcription: {len(self.transcription_complete)} caractères, {len(trans_clean.split())} mots")
        
        # Segments
        nb_segments = len(self.transcription_segments)
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        max_latency = max(self.latencies) if self.latencies else 0
        min_latency = min(self.latencies) if self.latencies else 0
        
        self.log_message(f"Segments de transcription: {nb_segments}")
        self.log_message(f"Latence moyenne: {avg_latency:.3f}s")
        self.log_message(f"Latence min/max: {min_latency:.3f}s / {max_latency:.3f}s")
        
        # Analyse de précision
        self.log_message("--- ANALYSE DE PRECISION ---")
        
        # Similarité globale
        similarity = difflib.SequenceMatcher(None, ref_clean, trans_clean).ratio()
        self.log_message(f"Similarité globale: {similarity*100:.1f}%")
        
        # Mots corrects
        ref_words = ref_clean.split()
        trans_words = trans_clean.split()
        
        correct_words = 0
        total_words = max(len(ref_words), len(trans_words))
        
        for i in range(min(len(ref_words), len(trans_words))):
            if ref_words[i].lower() == trans_words[i].lower():
                correct_words += 1
        
        word_accuracy = (correct_words / total_words * 100) if total_words > 0 else 0
        self.log_message(f"Précision mots: {word_accuracy:.1f}% ({correct_words}/{total_words})")
        
        # Analyse par segments de complexité
        self.analyze_complexity_segments(trans_clean)
        
        # Erreurs fréquentes
        self.analyze_common_errors(ref_clean, trans_clean)
        
        # Sauvegarde résultats
        self.save_test_results(similarity, word_accuracy, avg_latency)
        
        self.log_message("=== ANALYSE TERMINEE ===", "#00ff00")
    
    def clean_text_for_comparison(self, text):
        """Nettoie le texte pour comparaison précise"""
        # Suppression ponctuation, accents, mise en minuscules
        cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Normalisation accents basique
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
        self.log_message("--- ANALYSE PAR COMPLEXITE ---")
        
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
            self.log_message(f"{segment_name}: {found}/{total} ({percentage:.1f}%)")
    
    def analyze_common_errors(self, reference, transcription):
        """Analyse des erreurs courantes"""
        self.log_message("--- ERREURS COURANTES ---")
        
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
            self.log_message(f"Mots manqués: {', '.join(missing_words[:10])}")
        
        # Mots ajoutés (possibles hallucinations)
        added_words = []
        for word, count in trans_counter.items():
            if ref_counter[word] < count:
                added_words.append(word)
        
        if added_words:
            self.log_message(f"Mots ajoutés: {', '.join(added_words[:10])}")
    
    def save_test_results(self, similarity, word_accuracy, avg_latency):
        """Sauvegarde résultats détaillés"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_engine_v5_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== RESULTATS TEST ENGINE V5 SuperWhisper2 ===\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"GPU: RTX 3090\n\n")
                
                f.write("=== METRIQUES PRINCIPALES ===\n")
                f.write(f"Similarité globale: {similarity*100:.1f}%\n")
                f.write(f"Précision mots: {word_accuracy:.1f}%\n")
                f.write(f"Latence moyenne: {avg_latency:.3f}s\n")
                f.write(f"Segments: {len(self.transcription_segments)}\n\n")
                
                f.write("=== TEXTE DE REFERENCE ===\n")
                f.write(TEXTE_REFERENCE + "\n\n")
                
                f.write("=== TRANSCRIPTION COMPLETE ===\n")
                f.write(self.transcription_complete + "\n\n")
                
                f.write("=== SEGMENTS DETAILLES ===\n")
                for i, segment in enumerate(self.transcription_segments):
                    f.write(f"[{i+1}] {segment['timestamp']:.1f}s (latence: {segment.get('latency', 0):.3f}s): {segment['text']}\n")
            
            self.log_message(f"Résultats sauvegardés: {filename}", "#00ff00")
            
        except Exception as e:
            self.log_message(f"Erreur sauvegarde: {str(e)}", "#ff0000")
    
    def run(self):
        """Lance l'interface"""
        self.log_message("=== TEST ENGINE V5 SuperWhisper2 ===")
        self.log_message("1. Cliquez 'INITIALISER ENGINE V5'")
        self.log_message("2. Cliquez 'DEMARRER TEST'")
        self.log_message("3. Lisez le texte de validation")
        self.log_message("4. Cliquez 'ARRETER TEST'")
        self.log_message("5. Cliquez 'ANALYSER RESULTATS' pour statistiques")
        self.log_message("")
        self.log_message("=== TEXTE DE VALIDATION A LIRE ===")
        self.log_message(TEXTE_REFERENCE)
        self.log_message("="*50)
        
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    print("Lancement Test Engine V5 SuperWhisper2...")
    
    try:
        test = SimpleEngineTest()
        test.run()
    except KeyboardInterrupt:
        print("\nTest interrompu par l'utilisateur")
    except Exception as e:
        print(f"Erreur fatale: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()