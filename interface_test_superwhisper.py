#!/usr/bin/env python3
"""
Interface Graphique Test SuperWhisper2 Engine V5
Interface moderne pour validation et tests de performance
RTX 3090 + Engine V5 + Interface intuitive
"""

import os
import sys
import time
import threading
import queue
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional
import json
from datetime import datetime

# Configuration RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # RTX 3090 24GB
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajouter src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Texte de validation integre - Version mise a jour
TEXTE_VALIDATION = """Bonjour, ceci est un test de validation pour SuperWhisper2. Je vais maintenant enoncer plusieurs phrases de complexite croissante pour evaluer la precision de transcription.

Premierement, des mots simples : chat, chien, maison, voiture, ordinateur, telephone.

Deuxiemement, des phrases courtes : Il fait beau aujourd'hui. Le cafe est delicieux. J'aime la musique classique.

Troisiemement, des phrases plus complexes : L'intelligence artificielle transforme notre maniere de travailler et de communiquer dans le monde moderne.

Quatriemement, des termes techniques : algorithme, machine learning, GPU RTX 3090, faster-whisper, quantification INT8, latence de transcription.

Cinquiemement, des nombres et dates : vingt-trois, quarante-sept, mille neuf cent quatre-vingt-quinze, le quinze janvier deux mille vingt-quatre.

Sixiemement, des mots difficiles : chrysantheme, anticonstitutionnellement, prestidigitateur, kakemono, yaourt.

Septiemement, une phrase longue et complexe : L'optimisation des performances de transcription vocale necessite une approche methodique combinant la selection appropriee des modeles, l'ajustement des parametres de traitement, et l'implementation d'algorithmes de post-traitement pour ameliorer la qualite du resultat final.

Fin du test de validation."""

# Segments du texte pour suivi de progression
SEGMENTS_VALIDATION = [
    "Introduction",
    "Mots simples",
    "Phrases courtes", 
    "Phrases complexes",
    "Termes techniques",
    "Nombres et dates",
    "Mots difficiles",
    "Phrase complexe finale",
    "Conclusion"
]

class SuperWhisperTestGUI:
    """Interface graphique pour tests SuperWhisper2 Engine V5"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.engine = None
        self.listening = False
        self.transcriptions = []
        self.result_queue = queue.Queue()
        self.stats = {
            'start_time': None,
            'total_segments': 0,
            'avg_latency': 0.0,
            'total_chars': 0
        }
        
        # NOUVEAU: Variables pour la protection anti-arret
        self.auto_stop_protection = False
        self.test_start_time = 0
        
        self.setup_ui()
        self.setup_engine_thread = None
        
    def setup_ui(self):
        """Configuration interface utilisateur"""
        self.root.title("[AUDIO] SuperWhisper2 Test Interface - Engine V5")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2C3E50")
        
        # Style moderne
        style = ttk.Style()
        style.theme_use('clam')
        
        # Titre principal
        title_frame = tk.Frame(self.root, bg="#2C3E50")
        title_frame.pack(pady=10, fill="x")
        
        tk.Label(title_frame, 
                text="[INIT] SuperWhisper2 Engine V5 - Interface de Test",
                font=("Arial", 18, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack()
        
        tk.Label(title_frame,
                text="RTX 3090 24GB • Performance <1s • Phase 3",
                font=("Arial", 12),
                bg="#2C3E50", fg="#BDC3C7").pack()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#2C3E50")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Colonne gauche - Controles
        left_frame = tk.Frame(main_frame, bg="#34495E", relief="raised", bd=2)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        
        self.setup_controls(left_frame)
        
        # Colonne droite - Resultats  
        right_frame = tk.Frame(main_frame, bg="#34495E", relief="raised", bd=2)
        right_frame.pack(side="right", fill="both", expand=True)
        
        self.setup_results(right_frame)
        
    def setup_controls(self, parent):
        """Zone controles gauche"""
        tk.Label(parent, text="🎛️ CONTRÔLES", 
                font=("Arial", 14, "bold"),
                bg="#34495E", fg="#ECF0F1").pack(pady=10)
        
        # Selection microphone
        mic_frame = tk.LabelFrame(parent, text="[MIC] Selection Microphone", 
                                bg="#34495E", fg="#ECF0F1",
                                font=("Arial", 10, "bold"))
        mic_frame.pack(fill="x", padx=10, pady=5)
        
        mic_select_frame = tk.Frame(mic_frame, bg="#34495E")
        mic_select_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(mic_select_frame, text="[AUDIO]", 
                bg="#34495E", fg="#ECF0F1",
                font=("Arial", 12)).pack(side="left")
        
        self.mic_var = tk.StringVar()
        self.mic_combo = ttk.Combobox(mic_select_frame, textvariable=self.mic_var, 
                                     width=25, state="readonly")
        self.mic_combo.pack(side="left", padx=5, expand=True, fill="x")
        
        refresh_btn = tk.Button(mic_select_frame, text="[REFRESH]", 
                               command=self.refresh_microphones,
                               bg="#3498DB", fg="white",
                               font=("Arial", 8), width=3)
        refresh_btn.pack(side="right", padx=2)
        
        # Initialiser liste microphones
        self.refresh_microphones()
        
        # Status Engine
        status_frame = tk.LabelFrame(parent, text="[STAT] Status Engine V5", 
                                   bg="#34495E", fg="#ECF0F1",
                                   font=("Arial", 10, "bold"))
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, 
                                   text="[ERR] Non initialise",
                                   bg="#34495E", fg="#E74C3C",
                                   font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        self.gpu_label = tk.Label(status_frame,
                                text="[GPU] GPU: En attente...",
                                bg="#34495E", fg="#BDC3C7",
                                font=("Arial", 9))
        self.gpu_label.pack()
        
        # Boutons principaux
        buttons_frame = tk.LabelFrame(parent, text="[AUDIO] Actions", 
                                    bg="#34495E", fg="#ECF0F1",
                                    font=("Arial", 10, "bold"))
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        self.init_btn = tk.Button(buttons_frame, 
                                text="[INIT] Initialiser Engine V5",
                                command=self.init_engine,
                                bg="#3498DB", fg="white",
                                font=("Arial", 11, "bold"),
                                height=2)
        self.init_btn.pack(fill="x", pady=5)
        
        self.start_btn = tk.Button(buttons_frame,
                                 text="[AUDIO] Demarrer Test",
                                 command=self.start_test,
                                 bg="#27AE60", fg="white", 
                                 font=("Arial", 11, "bold"),
                                 height=2, state="disabled")
        self.start_btn.pack(fill="x", pady=5)
        
        self.stop_btn = tk.Button(buttons_frame,
                                text="[STOP] Arreter Test",
                                command=self.stop_test,
                                bg="#E74C3C", fg="white",
                                font=("Arial", 11, "bold"),
                                height=2, state="disabled")
        self.stop_btn.pack(fill="x", pady=5)
        
        # Metriques temps reel
        metrics_frame = tk.LabelFrame(parent, text="📈 Metriques Temps Reel",
                                    bg="#34495E", fg="#ECF0F1",
                                    font=("Arial", 10, "bold"))
        metrics_frame.pack(fill="x", padx=10, pady=10)
        
        self.segments_label = tk.Label(metrics_frame, text="[TEXT] Segments: 0",
                                     bg="#34495E", fg="#ECF0F1")
        self.segments_label.pack(anchor="w")
        
        self.latency_label = tk.Label(metrics_frame, text="[TIME] Latence moy: 0.00s",
                                    bg="#34495E", fg="#ECF0F1")
        self.latency_label.pack(anchor="w")
        
        self.chars_label = tk.Label(metrics_frame, text="📏 Caracteres: 0",
                                  bg="#34495E", fg="#ECF0F1")
        self.chars_label.pack(anchor="w")
        
        # Guide de test micro
        guide_frame = tk.LabelFrame(parent, text="[COPY] Guide Test Micro",
                                  bg="#34495E", fg="#ECF0F1",
                                  font=("Arial", 10, "bold"))
        guide_frame.pack(fill="x", padx=10, pady=5)
        
        # Progression du test
        progress_frame = tk.Frame(guide_frame, bg="#34495E")
        progress_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(progress_frame, text="[STAT] Progression:",
                bg="#34495E", fg="#ECF0F1",
                font=("Arial", 9, "bold")).pack(anchor="w")
        
        self.progress_label = tk.Label(progress_frame, 
                                     text="[WAIT] En attente du test...",
                                     bg="#34495E", fg="#F39C12",
                                     font=("Arial", 9))
        self.progress_label.pack(anchor="w")
        
        # Boutons de controle du test
        test_controls_frame = tk.Frame(guide_frame, bg="#34495E")
        test_controls_frame.pack(fill="x", padx=5, pady=5)
        
        self.show_text_btn = tk.Button(test_controls_frame,
                                     text="[READ] Afficher Texte",
                                     command=self.toggle_text_window,
                                     bg="#9B59B6", fg="white",
                                     font=("Arial", 9, "bold"))
        self.show_text_btn.pack(side="left", padx=(0, 5))
        
        self.reset_test_btn = tk.Button(test_controls_frame,
                                      text="[REFRESH] Reset Test",
                                      command=self.reset_test_progress,
                                      bg="#E67E22", fg="white",
                                      font=("Arial", 9, "bold"))
        self.reset_test_btn.pack(side="left")
        
        # Texte de validation (reduit)
        text_frame = tk.LabelFrame(parent, text="[READ] Apercu Texte",
                                 bg="#34495E", fg="#ECF0F1",
                                 font=("Arial", 10, "bold"))
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.text_validation = scrolledtext.ScrolledText(text_frame,
                                                       width=35, height=8,
                                                       font=("Arial", 9),
                                                       bg="#2C3E50", fg="#ECF0F1",
                                                       wrap="word")
        self.text_validation.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Afficher un apercu reduit
        apercu_text = "[COPY] TEXTE DE TEST MICRO\n\n" + TEXTE_VALIDATION[:200] + "\n\n[...] Cliquez 'Afficher Texte' pour voir le texte complet dans une fenetre separee."
        self.text_validation.insert("1.0", apercu_text)
        self.text_validation.config(state="disabled")
        
        # Variables pour le suivi
        self.test_progress = 0
        self.text_window = None
        
    def setup_results(self, parent):
        """Zone resultats droite"""
        tk.Label(parent, text="[TEXT] TRANSCRIPTIONS TEMPS RÉEL",
                font=("Arial", 14, "bold"),
                bg="#34495E", fg="#ECF0F1").pack(pady=10)
        
        # Zone transcriptions temps reel
        self.transcription_area = scrolledtext.ScrolledText(parent,
                                                          width=70, height=25,
                                                          font=("Consolas", 11),
                                                          bg="#2C3E50", fg="#ECF0F1",
                                                          wrap="word")
        self.transcription_area.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Boutons analyse
        analysis_frame = tk.Frame(parent, bg="#34495E")
        analysis_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(analysis_frame, text="[STAT] Analyser Resultats",
                 command=self.analyze_results,
                 bg="#9B59B6", fg="white",
                 font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Button(analysis_frame, text="[SAVE] Sauvegarder",
                 command=self.save_results,
                 bg="#34495E", fg="white",
                 font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Button(analysis_frame, text="🧹 Effacer",
                 command=self.clear_results,
                 bg="#95A5A6", fg="white",
                 font=("Arial", 10)).pack(side="left", padx=5)
    
    def init_engine(self):
        """Initialisation Engine V5 en thread"""
        def init_thread():
            try:
                self.log_message("[INIT] Demarrage SuperWhisper2 Engine V5...")
                self.init_btn.config(state="disabled", text="[WAIT] Initialisation...")
                
                from core.whisper_engine_v5 import SuperWhisper2EngineV5
                
                self.engine = SuperWhisper2EngineV5()
                
                # NOUVEAU: Ne pas configurer le callback ici - il sera configuré dans start_test
                # pour éviter les conflits et les doubles callbacks
                
                self.log_message("[FAST] Demarrage optimisations RTX 3090...")
                success = self.engine.start_engine()
                
                if success:
                    status = self.engine.get_phase3_status()
                    
                    self.root.after(0, lambda: self.status_label.config(
                        text="[OK] Engine V5 Ready", fg="#27AE60"))
                    
                    self.root.after(0, lambda: self.gpu_label.config(
                        text=f"[GPU] RTX 3090: {status['gpu_status']['vram_cache_gb']:.1f}GB • {status['optimizations_count']}/{status['total_optimizations']} opt"))
                    
                    self.root.after(0, lambda: self.start_btn.config(state="normal"))
                    self.root.after(0, lambda: self.init_btn.config(text="[OK] Engine Ready", bg="#27AE60"))
                    
                    self.log_message("[OK] SuperWhisper2 Engine V5 initialise avec succes!")
                    self.log_message(f"[FAST] {status['optimizations_count']}/{status['total_optimizations']} optimisations actives")
                    self.log_message(f"[GPU] RTX 3090: {status['gpu_status']['vram_cache_gb']:.1f}GB VRAM cache")
                    self.log_message(f"🔀 {status['gpu_status']['cuda_streams']} CUDA Streams")
                else:
                    self.root.after(0, lambda: self.status_label.config(
                        text="[ERR] Échec Engine", fg="#E74C3C"))
                    self.root.after(0, lambda: self.init_btn.config(
                        state="normal", text="[INIT] Reessayer", bg="#E74C3C"))
                    
            except Exception as e:
                self.log_message(f"[ERR] Erreur initialisation: {e}")
                self.root.after(0, lambda: self.init_btn.config(
                    state="normal", text="[INIT] Reessayer", bg="#E74C3C"))
        
        self.setup_engine_thread = threading.Thread(target=init_thread)
        self.setup_engine_thread.daemon = True
        self.setup_engine_thread.start()
    
    def start_test(self):
        """Demarrer test microphone - ENGINE V5 UNIQUEMENT"""
        if not self.engine:
            messagebox.showerror("Erreur", "Engine non initialise!")
            return
            
        # Obtenir microphone selectionne
        device_id = self.get_selected_microphone_id()
        if device_id is None:
            messagebox.showerror("Erreur", "Aucun microphone selectionne!")
            return
            
        # Protection contre l'arret automatique
        self.auto_stop_protection = True
        self.test_start_time = time.time()
        
        self.listening = True
        self.transcriptions = []
        self.stats['start_time'] = time.time()
        self.stats['total_segments'] = 0
        
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="[AUDIO] ÉCOUTE ACTIVE", fg="#F39C12")
        
        self.log_message("[AUDIO] TEST DÉMARRÉ - Commencez a lire le texte...")
        self.log_message(f"[MIC] Microphone selectionne: ID {device_id}")
        self.log_message("=" * 60)
        
        # Configuration du callback de transcription ENGINE V5 UNIQUEMENT
        try:
            def on_transcription(text: str):
                if text and text.strip():
                    # Filtrer les hallucinations communes de Whisper
                    if self.is_hallucination(text.strip()):
                        return  # Ignorer les hallucinations
                    
                    timestamp = time.time()
                    # Format compatible avec l'analyse (pas de transcribe_time pour Engine V5)
                    self.result_queue.put((timestamp, text.strip()))
                    self.update_test_progress(text.strip())
            
            self.engine.set_transcription_callback(on_transcription)
            self.log_message("🎤 Engine V5 configuré et prêt")
            
        except Exception as e:
            self.log_message(f"❌ Erreur configuration Engine V5: {e}")
            self.stop_test()
            return
        
        # Démarrage monitoring uniquement
        self.root.after(500, self.monitor_transcriptions)
        
        # Protection auto-arrêt
        def disable_auto_stop_protection():
            self.auto_stop_protection = False
        self.root.after(10000, disable_auto_stop_protection)
    
    def stop_test(self):
        """Arrêter test - ENGINE V5 UNIQUEMENT"""
        # Protection anti-arrêt prématuré
        if hasattr(self, 'auto_stop_protection') and self.auto_stop_protection:
            elapsed_time = time.time() - getattr(self, 'test_start_time', 0)
            if elapsed_time < 5.0:
                return  # Bloquer arrêt prématuré
        
        self.listening = False
        self.auto_stop_protection = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="[OK] Engine Ready", fg="#27AE60")
        
        self.log_message("⏹️ Test terminé")
        self.analyze_results()
    
    def monitor_transcriptions(self):
        """Monitoring transcriptions ENGINE V5 UNIQUEMENT"""
        if not self.listening:
            self.log_message("DEBUG: Monitoring arrete (listening = False)")
            return
            
        try:
            processed = 0
            while not self.result_queue.empty():
                # Format Engine V5: (timestamp, text) sans transcribe_time
                try:
                    timestamp, text = self.result_queue.get_nowait()
                except:
                    continue
                    
                processed += 1
                
                # Calculer latence relative
                if self.stats['start_time']:
                    relative_time = timestamp - self.stats['start_time']
                else:
                    relative_time = 0
                
                # Ajouter aux stats (Engine V5 - pas de transcribe_time individuel)
                self.transcriptions.append({
                    'timestamp': timestamp,
                    'relative_time': relative_time, 
                    'text': text
                })
                
                self.stats['total_segments'] += 1
                self.stats['total_chars'] += len(text)
                
                # Affichage simplifié pour Engine V5
                self.log_message(f"[TIME] [{relative_time:.1f}s] {text}")
                
                # Mettre a jour metriques temps réel
                self.update_metrics()
            
            # Logs de progression simplifiés
            if processed > 0:
                self.log_message(f"📝 {processed} transcriptions")
                
        except queue.Empty:
            pass
        except Exception as e:
            self.log_message(f"DEBUG: Erreur monitoring: {e}")
        
        # Monitoring standard pour Engine V5
        if self.listening:
            self.root.after(500, self.monitor_transcriptions)
        else:
            self.log_message("DEBUG: Monitoring termine car listening = False")
    
    def update_metrics(self):
        """Mise a jour metriques temps reel"""
        self.segments_label.config(text=f"[TEXT] Segments: {self.stats['total_segments']}")
        self.chars_label.config(text=f"📏 Caracteres: {self.stats['total_chars']}")
        
        if len(self.transcriptions) > 1:
            latencies = [t['relative_time'] for t in self.transcriptions[1:]]
            if latencies:
                avg_lat = sum(latencies) / len(latencies)
                self.stats['avg_latency'] = avg_lat
                self.latency_label.config(text=f"[TIME] Latence moy: {avg_lat:.2f}s")
    
    def analyze_results(self):
        """Analyse finale des performances ENGINE V5"""
        if not self.transcriptions:
            self.log_message("[ERR] Aucune transcription a analyser")
            return
            
        # Calculs statistiques
        total_transcriptions = len(self.transcriptions)
        total_chars = sum(len(t['text']) for t in self.transcriptions)
        
        # Analyse hallucinations
        valid_transcriptions = []
        hallucination_count = 0
        
        for transcription in self.transcriptions:
            if self.is_hallucination(transcription['text']):
                hallucination_count += 1
            else:
                valid_transcriptions.append(transcription)
        
        # Latences relatives (temps global Engine V5)
        relative_latencies = [t['relative_time'] for t in self.transcriptions if t['relative_time'] > 0]
        avg_relative_latency = sum(relative_latencies) / len(relative_latencies) if relative_latencies else 0
        min_relative_latency = min(relative_latencies) if relative_latencies else 0
        max_relative_latency = max(relative_latencies) if relative_latencies else 0
        
        # Resultats
        self.log_message("=" * 60)
        self.log_message("[STAT] ANALYSE FINALE DES RÉSULTATS")
        self.log_message("=" * 60)
        self.log_message(f"[TEXT] Total transcriptions: {total_transcriptions}")
        self.log_message(f"[OK] Transcriptions valides: {len(valid_transcriptions)}")
        self.log_message(f"[BLOCK] Hallucinations filtrees: {hallucination_count}")
        self.log_message(f"📏 Caracteres totaux: {total_chars}")
        
        # Métriques de latence Engine V5
        self.log_message(f"[TIME] Latence moyenne: {avg_relative_latency:.2f}s")
        self.log_message(f"[FAST] Latence minimale: {min_relative_latency:.2f}s") 
        self.log_message(f"🐌 Latence maximale: {max_relative_latency:.2f}s")
        
        # Objectifs Phase 3
        self.log_message("=" * 40)
        self.log_message("[TARGET] VALIDATION OBJECTIFS PHASE 3")
        self.log_message("=" * 40)
        
        # Critere latence < 1s (Engine V5 latence globale)
        if avg_relative_latency < 1.0:
            self.log_message(f"[OK] Latence <1s: RÉUSSI ({avg_relative_latency:.2f}s)")
        else:
            self.log_message(f"[ERR] Latence <1s: ÉCHEC ({avg_relative_latency:.2f}s)")
        
        # Critere hallucinations < 10%
        hallucination_rate = (hallucination_count / total_transcriptions * 100) if total_transcriptions > 0 else 0
        if hallucination_rate < 10:
            self.log_message(f"[OK] Hallucinations <10%: RÉUSSI ({hallucination_rate:.1f}%)")
        else:
            self.log_message(f"[ERR] Hallucinations <10%: ÉCHEC ({hallucination_rate:.1f}%)")
        
        # Critere transcriptions valides > 80%
        valid_rate = (len(valid_transcriptions) / total_transcriptions * 100) if total_transcriptions > 0 else 0
        if valid_rate > 80:
            self.log_message(f"[OK] Transcriptions valides >80%: RÉUSSI ({valid_rate:.1f}%)")
        else:
            self.log_message(f"[ERR] Transcriptions valides >80%: ÉCHEC ({valid_rate:.1f}%)")
    
    def save_results(self):
        """Sauvegarde resultats JSON"""
        if not self.transcriptions:
            messagebox.showinfo("Info", "Aucun resultat a sauvegarder")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        
        results = {
            'timestamp': timestamp,
            'engine_version': 'V5',
            'gpu': 'RTX 3090',
            'stats': self.stats,
            'transcriptions': self.transcriptions
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            self.log_message(f"[SAVE] Resultats sauvegardes: {filename}")
        except Exception as e:
            self.log_message(f"[ERR] Erreur sauvegarde: {e}")
    
    def is_hallucination(self, text: str) -> bool:
        """
        Detecte les hallucinations communes de Whisper
        """
        if not text or len(text.strip()) == 0:
            return True
            
        text_lower = text.lower().strip()
        
        # Patterns d'hallucination identifies
        hallucination_patterns = [
            "sous-titres realises par la communaute d'amara.org",
            "sous-titres realises par l'amara.org", 
            "merci d'avoir regarde cette video",
            "merci d'avoir regarde",
            "n'hesitez pas a vous abonner",
            "like et abonne-toi",
            "commentez et partagez",
            "a bientot pour une nouvelle video",
            "musique libre de droit",
            "copyright",
            "creative commons"
        ]
        
        # Verifier patterns exacts
        for pattern in hallucination_patterns:
            if pattern in text_lower:
                return True
                
        # Verifier repetitions suspectes
        words = text_lower.split()
        if len(words) > 3:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.5:  # Plus de 50% de repetitions
                return True
                
        return False
    
    def clear_results(self):
        """Effacer resultats"""
        self.transcription_area.delete("1.0", tk.END)
        self.transcriptions = []
        self.stats = {
            'start_time': None,
            'total_segments': 0,
            'avg_latency': 0.0,
            'total_chars': 0
        }
        self.update_metrics()
    
    def clean_message_for_console(self, message):
        """Nettoie un message pour l'affichage console Windows"""
        # Remplacer les emojis courants par des equivalents ASCII
        emoji_map = {
            "[INIT]": "[INIT]", "[FAST]": "[FAST]", "[OK]": "[OK]", "[ERR]": "[ERR]", 
            "[CONF]": "[CONF]", "[GPU]": "[GPU]", "[STAT]": "[STAT]", "[WAIT]": "[WAIT]",
            "[REFRESH]": "[REFRESH]", "[STREAM]": "[STREAM]", "[MIC]": "[MIC]", "[STOP]": "[STOP]",
            "[TEXT]": "[TEXT]", "[TIME]": "[TIME]", "[BLOCK]": "[BLOCK]", "[AUDIO]": "[AUDIO]",
            "[COPY]": "[COPY]", "[HOT]": "[HOT]", "[SAVE]": "[SAVE]", "[WARN]": "[WARN]",
            "[STOP]": "[STOP]", "[READ]": "[READ]", "[AI]": "[AI]"
        }
        
        cleaned = message
        for emoji, replacement in emoji_map.items():
            cleaned = cleaned.replace(emoji, replacement)
        
        # Nettoyer les caracteres non-ASCII restants
        try:
            cleaned.encode('cp1252')
            return cleaned
        except UnicodeEncodeError:
            return cleaned.encode('ascii', errors='ignore').decode('ascii')
    
    def log_message(self, message):
        """Afficher message dans zone transcription"""
        # Verifier si transcription_area existe (eviter erreur lors initialisation)
        if hasattr(self, 'transcription_area') and self.transcription_area:
            self.transcription_area.insert(tk.END, f"{message}\n")
            self.transcription_area.see(tk.END)
            self.root.update_idletasks()
        else:
            # Fallback: afficher en console si interface pas encore prete
            try:
                print(f"[INIT] {message}")
            except UnicodeEncodeError:
                # Nettoyer le message pour la console Windows
                clean_message = self.clean_message_for_console(message)
                print(f"[INIT] {clean_message}")
    
    def on_closing(self):
        """Nettoyage a la fermeture"""
        if self.engine:
            try:
                self.engine.stop_engine()
            except:
                pass
        self.root.destroy()
    
    def run(self):
        """Lancer interface"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def refresh_microphones(self):
        """Rafraichir liste des microphones disponibles"""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            
            # Filtrer les dispositifs d'entree et eviter les doublons
            input_devices = []
            seen_core_names = set()  # Pour eviter les doublons bases sur le nom principal
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    device_name = device['name'].strip()
                    
                    # Filtrer les peripheriques virtuels/indesirables d'abord
                    skip_keywords = [
                        'mappeur de sons microsoft', 'pilote de capture audio principal',
                        'mixage stereo', 'entree ligne', 'stereo input', 'line input',
                        'loopback', 'what u hear', 'stereo mix', 'wave out mix',
                        'communications', 'hands-free', 'input ()', '@system32'
                    ]
                    
                    if any(keyword in device_name.lower() for keyword in skip_keywords):
                        continue
                    
                    # Extraire le nom principal du microphone (sans les prefixes/suffixes)
                    core_name = device_name.lower()
                    
                    # Nettoyer le nom : enlever les prefixes communs
                    prefixes_to_remove = [
                        'microphone (', 'microphone(', 'casque (',
                        'microphone (2- ', 'microphone(2- '
                    ]
                    for prefix in prefixes_to_remove:
                        if core_name.startswith(prefix):
                            core_name = core_name[len(prefix):]
                            break
                    
                    # Enlever les suffixes communs
                    suffixes_to_remove = [')', ' audio)', ' audio', ' mic input', ' input']
                    for suffix in suffixes_to_remove:
                        if core_name.endswith(suffix):
                            core_name = core_name[:-len(suffix)]
                    
                    # Nettoyer encore (espaces multiples, etc.)
                    core_name = ' '.join(core_name.split())
                    
                    # Verifier si ce nom principal n'est pas deja vu
                    is_duplicate = False
                    for seen_name in seen_core_names:
                        # Similarite basee sur les mots cles principaux
                        seen_words = set(seen_name.split())
                        current_words = set(core_name.split())
                        
                        # Si plus de 70% des mots sont identiques, c'est un doublon
                        if len(seen_words & current_words) / max(len(seen_words), len(current_words)) > 0.7:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        # Stocker l'ID original et le nom pour renumerotation
                        input_devices.append((i, device_name))
                        seen_core_names.add(core_name)
            
            # Renumeroter les microphones de 0 a N-1 avec mapping vers l'ID original
            self.mic_id_mapping = {}  # Nouveau ID -> ID original sounddevice
            renumbered_devices = []
            
            for new_id, (original_id, device_name) in enumerate(input_devices):
                self.mic_id_mapping[new_id] = original_id
                display_name = f"{new_id}: {device_name}"
                renumbered_devices.append(display_name)
            
            input_devices = renumbered_devices
            
            self.mic_combo['values'] = input_devices
            
            # Selectionner le dispositif par defaut
            try:
                default_input = sd.query_devices(kind='input')
                default_name = default_input['name'].strip()
                
                # Chercher le dispositif par defaut dans notre liste filtree
                for item in input_devices:
                    item_name = item.split(': ', 1)[1]  # Extraire le nom sans l'ID
                    if default_name == item_name:
                        self.mic_combo.set(item)
                        break
                
                # Si aucun match, selectionner le premier dispositif reel
                if not self.mic_combo.get() and input_devices:
                    self.mic_combo.set(input_devices[0])
                    
            except Exception as e:
                if input_devices:
                    self.mic_combo.set(input_devices[0])
                    
            self.log_message(f"MICRO: {len(input_devices)} microphones uniques detectes")
                    
        except Exception as e:
            self.log_message(f"ERREUR: Erreur refresh microphones: {e}")
    
    def get_selected_microphone_id(self):
        """Obtenir l'ID du microphone selectionne"""
        try:
            selected = self.mic_var.get()
            if selected:
                new_id = int(selected.split(':')[0])
                # Convertir le nouvel ID vers l'ID original sounddevice
                if hasattr(self, 'mic_id_mapping') and new_id in self.mic_id_mapping:
                    original_id = self.mic_id_mapping[new_id]
                    self.log_message(f"DEBUG: Microphone {new_id} -> sounddevice ID {original_id}")
                    return original_id
                else:
                    self.log_message(f"DEBUG: Mapping non trouve, utilisation ID direct: {new_id}")
                    return new_id
        except Exception as e:
            self.log_message(f"WARN: Erreur ID microphone: {e}")
        return None
    
    def toggle_text_window(self):
        """Affiche/cache la fenetre avec le texte complet"""
        if self.text_window is None or not self.text_window.winfo_exists():
            self.show_text_window()
        else:
            self.text_window.destroy()
            self.text_window = None
            self.show_text_btn.configure(text="[READ] Afficher Texte")
    
    def show_text_window(self):
        """Cree une fenetre separee pour afficher le texte complet"""
        self.text_window = tk.Toplevel(self.root)
        self.text_window.title("[READ] Texte de Test Micro - SuperWhisper2")
        self.text_window.geometry("600x700")
        self.text_window.configure(bg="#2C3E50")
        
        # Empecher la fermeture accidentelle
        self.text_window.protocol("WM_DELETE_WINDOW", self.on_text_window_close)
        
        # Titre
        title_label = tk.Label(self.text_window,
                              text="[COPY] TEXTE DE VALIDATION MICRO",
                              font=("Arial", 16, "bold"),
                              bg="#2C3E50", fg="#ECF0F1")
        title_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.text_window,
                               text="Instructions: Lisez ce texte clairement au microphone\npour tester la transcription SuperWhisper2",
                               font=("Arial", 11),
                               bg="#2C3E50", fg="#BDC3C7",
                               justify="center")
        instructions.pack(pady=5)
        
        # Zone de texte avec scrollbar
        text_frame = tk.Frame(self.text_window, bg="#2C3E50")
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.full_text_area = scrolledtext.ScrolledText(text_frame,
                                                       font=("Arial", 12),
                                                       bg="#34495E", fg="#ECF0F1",
                                                       wrap="word",
                                                       relief="ridge", bd=2)
        self.full_text_area.pack(fill="both", expand=True)
        
        # Inserer le texte avec formatage
        self.full_text_area.insert("1.0", TEXTE_VALIDATION)
        
        # Configurer tags pour mise en evidence
        self.full_text_area.tag_configure("section", foreground="#3498DB", font=("Arial", 12, "bold"))
        
        # Mise en evidence des sections
        sections = [
            "Premierement", "Deuxiemement", "Troisiemement", 
            "Quatriemement", "Cinquiemement", "Sixiemement", "Septiemement"
        ]
        
        for section in sections:
            start_idx = "1.0"
            while True:
                start_idx = self.full_text_area.search(section, start_idx, tk.END)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(section)}c"
                self.full_text_area.tag_add("section", start_idx, end_idx)
                start_idx = end_idx
        
        self.full_text_area.config(state="disabled")
        
        # Boutons de controle
        button_frame = tk.Frame(self.text_window, bg="#2C3E50")
        button_frame.pack(pady=10)
        
        close_btn = tk.Button(button_frame,
                             text="[ERR] Fermer",
                             command=self.on_text_window_close,
                             bg="#E74C3C", fg="white",
                             font=("Arial", 11, "bold"))
        close_btn.pack(side="left", padx=5)
        
        copy_btn = tk.Button(button_frame,
                            text="[COPY] Copier Texte",
                            command=self.copy_text_to_clipboard,
                            bg="#3498DB", fg="white",
                            font=("Arial", 11, "bold"))
        copy_btn.pack(side="left", padx=5)
        
        # Mettre a jour le bouton principal
        self.show_text_btn.configure(text="[READ] Cacher Texte")
        
        # Centrer la fenetre
        self.center_window(self.text_window)
    
    def on_text_window_close(self):
        """Gere la fermeture de la fenetre de texte"""
        if self.text_window:
            self.text_window.destroy()
            self.text_window = None
            self.show_text_btn.configure(text="[READ] Afficher Texte")
    
    def copy_text_to_clipboard(self):
        """Copie le texte dans le presse-papiers"""
        self.root.clipboard_clear()
        self.root.clipboard_append(TEXTE_VALIDATION)
        
        # Feedback visuel
        if self.text_window and self.text_window.winfo_exists():
            original_text = "[COPY] Copier Texte"
            copy_btn = None
            for widget in self.text_window.winfo_children():
                if isinstance(widget, tk.Frame):
                    for btn in widget.winfo_children():
                        if isinstance(btn, tk.Button) and "Copier" in btn.cget("text"):
                            copy_btn = btn
                            break
            
            if copy_btn:
                copy_btn.config(text="[OK] Copie!", bg="#27AE60")
                self.root.after(2000, lambda: copy_btn.config(text=original_text, bg="#3498DB"))
    
    def reset_test_progress(self):
        """Remet a zero la progression du test"""
        self.test_progress = 0
        self.progress_label.config(text="WAIT: Test remis a zero - Pret a commencer")
        self.log_message("REFRESH: Progression du test remise a zero")
    
    def update_test_progress(self, transcription_text):
        """Met a jour la progression basee sur le contenu transcrit"""
        if not transcription_text:
            return
        
        # Chercher des mots-cles pour determiner la progression
        keywords = {
            0: ["bonjour", "validation", "superwhisper"],
            1: ["chat", "chien", "maison", "telephone"],
            2: ["fait beau", "cafe", "musique"],
            3: ["intelligence artificielle", "communiquer"],
            4: ["algorithme", "machine learning", "rtx", "faster"],
            5: ["vingt-trois", "quarante", "janvier"],
            6: ["chrysantheme", "anticonstitutionnellement", "yaourt"],
            7: ["optimisation", "methodique", "post-traitement"],
            8: ["fin du test", "validation"]
        }
        
        text_lower = transcription_text.lower()
        for level, words in keywords.items():
            if level > self.test_progress and any(word in text_lower for word in words):
                self.test_progress = level
                section_name = SEGMENTS_VALIDATION[level] if level < len(SEGMENTS_VALIDATION) else "Section inconnue"
                self.progress_label.config(
                    text=f"[STAT] Section actuelle: {section_name} ({level+1}/{len(SEGMENTS_VALIDATION)})",
                    fg="#27AE60" if level < len(SEGMENTS_VALIDATION)-1 else "#E74C3C"
                )
                break
    
    def center_window(self, window):
        """Centre une fenetre sur l'ecran"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

def main():
    """Point d'entree principal"""
    app = SuperWhisperTestGUI()
    app.run()

if __name__ == "__main__":
    main() 