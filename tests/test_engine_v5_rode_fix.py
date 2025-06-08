#!/usr/bin/env python3
"""
Test Engine V5 SuperWhisper2 - FIX MICROPHONE RODE
Version avec patch AudioStreamer pour forcer l'utilisation du device Rode
RTX 3090 + Engine V5 + Rode NT-USB (Device forcé)
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

class RodeEngineV5Test:
    def __init__(self):
        self.engine = None
        self.listening = False
        self.transcription_complete = ""
        self.transcription_segments = []
        self.start_time = None
        self.rode_device_id = None
        self.patched = False
        
        # Interface
        self.root = tk.Tk()
        self.root.title("🎤 Test Engine V5 - FIX RODE")
        self.root.geometry("1400x800")
        self.root.configure(bg="#0a0e27")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Interface utilisateur"""
        # Header
        header = tk.Frame(self.root, bg="#0a0e27")
        header.pack(fill="x", pady=20)
        
        title = tk.Label(header, 
                        text="🎤 TEST ENGINE V5 - FIX MICROPHONE RODE",
                        font=("Arial", 18, "bold"),
                        bg="#0a0e27", fg="#00d4aa")
        title.pack()
        
        subtitle = tk.Label(header,
                           text="SuperWhisper2 Phase 3 • Patch AudioStreamer • Rode NT-USB Device Force",
                           font=("Arial", 11),
                           bg="#0a0e27", fg="#6366f1")
        subtitle.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self.root, bg="#0a0e27")
        btn_frame.pack(pady=20)
        
        self.init_btn = tk.Button(btn_frame,
                                 text="🔧 INIT + PATCH RODE",
                                 command=self.init_with_rode_patch,
                                 bg="#059669", fg="white",
                                 font=("Arial", 11, "bold"),
                                 width=22, height=2)
        self.init_btn.pack(side="left", padx=8)
        
        self.start_btn = tk.Button(btn_frame,
                                  text="🎙️ DEMARRER TEST",
                                  command=self.start_test,
                                  bg="#3b82f6", fg="white",
                                  font=("Arial", 11, "bold"),
                                  width=22, height=2,
                                  state="disabled")
        self.start_btn.pack(side="left", padx=8)
        
        self.stop_btn = tk.Button(btn_frame,
                                 text="⏹️ ARRETER TEST", 
                                 command=self.stop_test,
                                 bg="#dc2626", fg="white",
                                 font=("Arial", 11, "bold"),
                                 width=22, height=2,
                                 state="disabled")
        self.stop_btn.pack(side="left", padx=8)
        
        self.analyze_btn = tk.Button(btn_frame,
                                    text="📊 ANALYSER",
                                    command=self.analyze_results,
                                    bg="#ea580c", fg="white",
                                    font=("Arial", 11, "bold"),
                                    width=22, height=2,
                                    state="disabled")
        self.analyze_btn.pack(side="left", padx=8)
        
        # Status
        self.status_label = tk.Label(self.root,
                                    text="🔴 Status: Prêt pour patch Rode",
                                    font=("Arial", 13, "bold"),
                                    bg="#0a0e27", fg="#f87171")
        self.status_label.pack(pady=12)
        
        # Output area
        output_frame = tk.Frame(self.root, bg="#0a0e27")
        output_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Transcription
        trans_frame = tk.LabelFrame(output_frame,
                                   text="🎯 TRANSCRIPTION + DEBUG",
                                   font=("Arial", 11, "bold"),
                                   bg="#0a0e27", fg="#00d4aa")
        trans_frame.pack(fill="both", expand=True, pady=5)
        
        self.transcription_text = scrolledtext.ScrolledText(trans_frame,
                                                          font=("Consolas", 10),
                                                          bg="#1e1b4b", fg="#e2e8f0",
                                                          wrap=tk.WORD,
                                                          height=18)
        self.transcription_text.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Stats
        stats_frame = tk.LabelFrame(output_frame,
                                   text="📈 STATISTIQUES",
                                   font=("Arial", 10, "bold"),
                                   bg="#0a0e27", fg="#00d4aa")
        stats_frame.pack(fill="x", pady=5)
        
        self.stats_text = tk.Text(stats_frame,
                                 font=("Consolas", 9),
                                 bg="#1e1b4b", fg="#e2e8f0",
                                 height=3)
        self.stats_text.pack(fill="x", padx=8, pady=4)
        
        # Instructions
        self.show_initial_text()
        
    def show_initial_text(self):
        """Affiche le texte initial"""
        text = f"""=== FIX MICROPHONE RODE POUR ENGINE V5 ===

🔧 INIT + PATCH RODE → Détecte Rode + Patch AudioStreamer
🎙️ DEMARRER TEST → Test avec device forcé
📖 LISEZ LE TEXTE → Parlez dans le Rode NT-USB
⏹️ ARRETER TEST → Termine
📊 ANALYSER → Statistiques

=== TEXTE DE VALIDATION ===
{TEXTE_REFERENCE}

========================================================================================
"""
        self.transcription_text.insert(tk.END, text)
        
    def log_message(self, message, color="#e2e8f0"):
        """Log avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        full_message = f"[{timestamp}] {message}"
        
        print(full_message)
        
        self.transcription_text.insert(tk.END, full_message + "\n")
        self.transcription_text.see(tk.END)
        self.root.update()
        
    def detect_rode_microphone(self):
        """Détecte le microphone Rode"""
        try:
            self.log_message("🔍 Scan microphones...")
            
            devices = sd.query_devices()
            self.log_message(f"📊 {len(devices)} devices détectés")
            
            # Recherche Rode
            rode_keywords = ['rode', 'nt-usb', 'procaster', 'podmic', 'podcaster']
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    device_name = device['name'].lower()
                    self.log_message(f"  [{i}] {device['name']} ({device['max_input_channels']} ch)")
                    
                    # Check Rode
                    for keyword in rode_keywords:
                        if keyword in device_name:
                            self.rode_device_id = i
                            self.log_message(f"✅ RODE TROUVÉ: {device['name']}")
                            self.log_message(f"📊 Device ID: {i} | SR: {device['default_samplerate']}Hz")
                            return True
            
            self.log_message("❌ Aucun Rode détecté")
            return False
            
        except Exception as e:
            self.log_message(f"❌ Erreur détection: {str(e)}")
            return False
    
    def test_rode_audio(self):
        """Test rapide du Rode"""
        if self.rode_device_id is None:
            return False
            
        try:
            self.log_message("🎤 Test Rode (2s)...")
            
            # Test avec device spécifique
            duration = 2.0
            audio_data = sd.rec(int(duration * 16000),
                               samplerate=16000,
                               channels=1,
                               device=self.rode_device_id,
                               dtype=np.float32)
            sd.wait()
            
            rms = np.sqrt(np.mean(audio_data ** 2))
            max_val = np.max(np.abs(audio_data))
            
            self.log_message(f"📊 RMS: {rms:.6f} | Max: {max_val:.6f}")
            
            if rms > 0.0001:
                self.log_message("✅ Rode audio OK!")
                return True
            else:
                self.log_message("⚠️ Niveau faible")
                return True  # Continuer
                
        except Exception as e:
            self.log_message(f"❌ Test Rode échec: {str(e)}")
            return False
    
    def patch_audio_streamer(self):
        """Patch AudioStreamer pour utiliser le device Rode"""
        try:
            self.log_message("🔧 Patch AudioStreamer...")
            
            if self.rode_device_id is None:
                raise Exception("Device Rode non détecté")
            
            # Import AudioStreamer
            from src.audio.audio_streamer import AudioStreamer
            
            # Sauvegarder méthode originale
            original_capture_loop = AudioStreamer._capture_loop
            
            # Device Rode à utiliser
            rode_device = self.rode_device_id
            
            def patched_capture_loop(self):
                """Boucle de capture patchée avec device Rode forcé"""
                self.logger.info(f"🎤 AudioStreamer patché - Device Rode: {rode_device}")
                
                self.stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype=np.float32,
                    blocksize=self.chunk_frames,
                    callback=self._audio_callback,
                    device=rode_device  # DEVICE RODE FORCÉ !
                )
                with self.stream:
                    while self.running:
                        time.sleep(0.1)
            
            # Appliquer le patch
            AudioStreamer._capture_loop = patched_capture_loop
            
            self.log_message(f"✅ AudioStreamer patché pour device {rode_device}")
            self.patched = True
            return True
            
        except Exception as e:
            self.log_message(f"❌ Patch AudioStreamer échec: {str(e)}")
            return False
    
    def init_with_rode_patch(self):
        """Initialise avec patch Rode"""
        self.log_message("🚀 INIT ENGINE V5 + PATCH RODE...")
        self.status_label.config(text="🟡 Patch en cours...", fg="#fbbf24")
        self.init_btn.config(state="disabled")
        
        def init_thread():
            try:
                # 1. Détecter Rode
                if not self.detect_rode_microphone():
                    raise Exception("Rode non détecté")
                
                # 2. Tester Rode
                if not self.test_rode_audio():
                    raise Exception("Test Rode échec")
                
                # 3. Patch AudioStreamer
                if not self.patch_audio_streamer():
                    raise Exception("Patch AudioStreamer échec")
                
                # 4. Init Engine V5
                self.log_message("📦 Import Engine V5...")
                from src.core.whisper_engine_v5 import SuperWhisper2EngineV5
                
                self.log_message("⚙️ Création Engine V5...")
                self.engine = SuperWhisper2EngineV5()
                
                # 5. Start Engine V5
                self.log_message("🎮 Start Engine V5...")
                success = self.engine.start_engine()
                
                if success:
                    self.log_message("✅ ENGINE V5 + RODE PATCH PRÊT!", "#10b981")
                    self.status_label.config(text="🟢 Engine V5 + Patch Rode OK", fg="#10b981")
                    self.start_btn.config(state="normal")
                else:
                    raise Exception("Engine V5 start échec")
                
            except Exception as e:
                error_msg = f"❌ ERREUR: {str(e)}"
                self.log_message(error_msg, "#ef4444")
                self.status_label.config(text="🔴 Erreur init", fg="#ef4444")
                self.init_btn.config(state="normal")
                messagebox.showerror("Erreur", error_msg)
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def start_test(self):
        """Démarre test avec Rode patché"""
        if not self.engine or not self.patched:
            messagebox.showerror("Erreur", "Engine V5 ou patch non prêt!")
            return
            
        self.log_message("="*80)
        self.log_message("🎙️ DÉBUT TEST AVEC RODE PATCHÉ")
        self.log_message("="*80)
        
        # Reset
        self.transcription_complete = ""
        self.transcription_segments = []
        self.start_time = time.time()
        self.listening = True
        
        # Callback transcription
        def on_transcription(text: str):
            if not self.listening:
                return
                
            timestamp = time.time() - self.start_time
            self.transcription_segments.append({
                'text': text,
                'timestamp': timestamp
            })
            
            self.transcription_complete += text + " "
            self.log_message(f"🎯 {text}", "#00d4aa")
            self.update_stats()
        
        try:
            # Config callback
            self.engine.set_transcription_callback(on_transcription)
            
            # UI
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="🔴 ENREGISTREMENT RODE ACTIF", fg="#ef4444")
            
            self.log_message("✅ Engine V5 écoute avec Rode patché")
            self.log_message(f"🎤 Device: {self.rode_device_id}")
            
        except Exception as e:
            self.log_message(f"❌ Erreur start: {str(e)}")
    
    def stop_test(self):
        """Arrête test"""
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
        self.status_label.config(text="🟢 Test terminé", fg="#10b981")
        
        total_time = time.time() - self.start_time if self.start_time else 0
        nb_segments = len(self.transcription_segments)
        self.log_message(f"📊 Durée: {total_time:.1f}s | Segments: {nb_segments}")
        
        if nb_segments > 0:
            self.log_message("✅ Transcriptions reçues - Patch OK!")
        else:
            self.log_message("⚠️ Aucune transcription - Problème possible")
    
    def update_stats(self):
        """Update stats"""
        if not self.transcription_segments:
            return
            
        nb_segments = len(self.transcription_segments)
        total_chars = len(self.transcription_complete)
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        stats = f"Segments: {nb_segments} | Chars: {total_chars} | Temps: {elapsed:.1f}s | Rode: {self.rode_device_id}"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)
    
    def analyze_results(self):
        """Analyse rapide"""
        if not self.transcription_complete.strip():
            messagebox.showwarning("Attention", "Aucune transcription!")
            return
            
        self.log_message("="*80)
        self.log_message("📊 ANALYSE RAPIDE")
        self.log_message("="*80)
        
        # Stats basiques
        ref_words = len(TEXTE_REFERENCE.split())
        trans_words = len(self.transcription_complete.split())
        completion = (trans_words / ref_words * 100) if ref_words > 0 else 0
        
        total_time = time.time() - self.start_time if self.start_time else 1
        
        self.log_message(f"📊 Mots référence: {ref_words}")
        self.log_message(f"📊 Mots transcrits: {trans_words}")
        self.log_message(f"📊 Complétion: {completion:.1f}%")
        self.log_message(f"📊 Durée: {total_time:.1f}s")
        self.log_message(f"📊 Segments: {len(self.transcription_segments)}")
        self.log_message(f"🎤 Device Rode utilisé: {self.rode_device_id}")
        
        # Texte complet
        self.log_message("--- TRANSCRIPTION COMPLETE ---")
        self.log_message(self.transcription_complete)
        
        # Sauvegarde
        self.save_quick_results(completion, total_time)
        
        self.log_message("="*80)
        self.log_message("✅ ANALYSE TERMINÉE")
        self.log_message("="*80)
    
    def save_quick_results(self, completion, total_time):
        """Sauvegarde rapide"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_rode_patch_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("TEST ENGINE V5 - PATCH MICROPHONE RODE\n")
                f.write("="*60 + "\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Device Rode: {self.rode_device_id}\n")
                f.write(f"Patch appliqué: {self.patched}\n\n")
                
                f.write("RÉSULTATS\n")
                f.write("-"*30 + "\n")
                f.write(f"Complétion: {completion:.1f}%\n")
                f.write(f"Durée: {total_time:.1f}s\n")
                f.write(f"Segments: {len(self.transcription_segments)}\n\n")
                
                f.write("TRANSCRIPTION\n")
                f.write("-"*30 + "\n")
                f.write(self.transcription_complete + "\n")
                
            self.log_message(f"💾 Sauvegardé: {filename}")
            
        except Exception as e:
            self.log_message(f"❌ Erreur save: {str(e)}")
    
    def run(self):
        """Lance l'app"""
        self.root.mainloop()

def main():
    """Point d'entrée"""
    print("🎤 Test Engine V5 - Patch Microphone Rode...")
    
    try:
        test = RodeEngineV5Test()
        test.run()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 