#!/usr/bin/env python3
"""
Dictée Interactive Simple pour SuperWhisper2
Interface avec affichage en temps réel - Version simplifiée
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk
import queue
import numpy as np
import traceback
from faster_whisper import WhisperModel

# Configuration GPU RTX 3090 (fallback CPU si problème)
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # RTX 3090 sur GPU 1
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

class DicteeSimple:
    """Interface de dictée simple avec affichage temps réel"""
    
    def __init__(self):
        self.running = False
        self.model = None
        self.root = None
        self.overlay_window = None
        self.recording_thread = None
        self.transcription_queue = queue.Queue()
        
        print("🚀 Initialisation SuperWhisper2 - RTX 3090...")
        # PRIORITÉ RTX 3090 - CUDA:0 (RTX 3090 configurée via CUDA_VISIBLE_DEVICES=1)
        try:
            print("⚡ Test RTX 3090 CUDA:0...")
            self.model = WhisperModel("tiny", device="cuda", compute_type="float16")
            # Test rapide
            dummy_audio = np.zeros(16000).astype(np.float32)
            segments, _ = self.model.transcribe(dummy_audio)
            list(segments)  # Force l'exécution
            print("✅ RTX 3090 OPÉRATIONNELLE")
            self.device_info = "RTX 3090 - float16"
        except Exception as e:
            print(f"⚠️ RTX 3090 échoué ({e})")
            try:
                print("🔄 Fallback CPU...")
                self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
                print("✅ CPU opérationnel (fallback)")
                self.device_info = "CPU (fallback) - int8"
            except Exception as e2:
                print(f"❌ ERREUR CRITIQUE: {e2}")
                raise
        
        # Filtrage hallucinations
        self.unwanted_phrases = [
            "Merci d'avoir regardé cette vidéo!",
            "Merci d'avoir regardé cette vidéo",
            "Merci d'avoir regardé",
            "Abonnez-vous",
            "N'hésitez pas à vous abonner",
            "Sous-titres par la communauté d'Amara.org"
        ]
        self.last_transcription = ""
        
    def setup_interface(self):
        """Configuration interface graphique principale"""
        self.root = tk.Tk()
        self.root.title("SuperWhisper2 - Dictée Simple")
        self.root.geometry("600x450")
        self.root.configure(bg="#2C3E50")
        
        # Titre
        title_label = tk.Label(self.root, text="🎤 SuperWhisper2 - Dictée Interactive", 
                              font=("Arial", 18, "bold"), 
                              bg="#2C3E50", fg="#ECF0F1")
        title_label.pack(pady=20)
        
        # Sélection microphone
        mic_frame = tk.Frame(self.root, bg="#2C3E50")
        mic_frame.pack(pady=10)
        
        tk.Label(mic_frame, text="🎙️ Microphone:", 
                font=("Arial", 12, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(side="left")
        
        self.mic_var = tk.StringVar()
        self.mic_combo = ttk.Combobox(mic_frame, textvariable=self.mic_var, 
                                     width=40, state="readonly")
        self.mic_combo.pack(side="left", padx=10)
        
        tk.Button(mic_frame, text="🔄 Rafraîchir", 
                 command=self.refresh_microphones,
                 bg="#3498DB", fg="white",
                 font=("Arial", 10)).pack(side="left", padx=5)
        
        # Status
        self.status_label = tk.Label(self.root, text="Initialisation...", 
                                   font=("Arial", 14),
                                   bg="#2C3E50", fg="#F39C12")
        self.status_label.pack(pady=10)
        
        # Boutons
        self.start_btn = tk.Button(self.root, text="🎤 Démarrer Dictée", 
                                 command=self.start_dictee, 
                                 bg="#27AE60", fg="white", 
                                 font=("Arial", 14, "bold"),
                                 width=20, height=2)
        self.start_btn.pack(pady=10)
        
        self.stop_btn = tk.Button(self.root, text="⏹️ Arrêter", 
                                command=self.stop_dictee,
                                bg="#E74C3C", fg="white",
                                font=("Arial", 14, "bold"),
                                width=20, height=2,
                                state="disabled")
        self.stop_btn.pack(pady=5)
        
        # Zone de texte pour affichage
        text_frame = tk.Frame(self.root, bg="#2C3E50")
        text_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        tk.Label(text_frame, text="📝 Transcriptions:", 
                font=("Arial", 12, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(anchor="w")
        
        self.text_area = tk.Text(text_frame, width=70, height=10,
                               font=("Arial", 12),
                               wrap="word",
                               bg="#34495E", fg="#ECF0F1")
        self.text_area.pack(fill="both", expand=True)
        
        # Bouton quitter
        tk.Button(self.root, text="❌ Quitter", 
                 command=self.quit_app,
                 bg="#95A5A6", fg="white",
                 font=("Arial", 12)).pack(pady=10)
        
        # Charger microphones
        self.refresh_microphones()
    
    def refresh_microphones(self):
        """Rafraîchir liste des microphones"""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            
            # Filtrer les dispositifs d'entrée
            input_devices = []
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    name = f"{i}: {device['name']}"
                    input_devices.append(name)
            
            self.mic_combo['values'] = input_devices
            
            # Sélectionner le dispositif par défaut
            try:
                default_input = sd.query_devices(kind='input')
                default_name = f"{default_input['name']}"
                for item in input_devices:
                    if default_name in item:
                        self.mic_combo.set(item)
                        break
            except:
                if input_devices:
                    self.mic_combo.set(input_devices[0])
                    
        except Exception as e:
            print(f"❌ Erreur microphones: {e}")
    
    def get_selected_device(self):
        """Obtenir l'ID du dispositif sélectionné"""
        try:
            selected = self.mic_var.get()
            if selected:
                device_id = int(selected.split(':')[0])
                return device_id
        except:
            pass
        return None
    
    def setup_overlay(self):
        """Configuration overlay flottant"""
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.title("SuperWhisper2 - Transcription")
        self.overlay_window.overrideredirect(True)
        self.overlay_window.wm_attributes("-topmost", True)
        self.overlay_window.wm_attributes("-alpha", 0.9)
        
        # Position en haut à droite
        self.overlay_window.geometry("600x150+{}+50".format(
            self.root.winfo_screenwidth() - 650))
        
        # Frame
        overlay_frame = tk.Frame(self.overlay_window, bg="#2C3E50", 
                               relief="raised", bd=3)
        overlay_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Label titre
        tk.Label(overlay_frame, text="🎤 SuperWhisper2 - Transcription Live",
                font=("Arial", 12, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(pady=5)
        
        # Label transcription
        self.overlay_text = tk.Label(overlay_frame, 
                                   text="Prêt pour la dictée...",
                                   font=("Arial", 14),
                                   bg="#2C3E50", fg="#ECF0F1",
                                   wraplength=580,
                                   justify="left")
        self.overlay_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cacher initialement
        self.overlay_window.withdraw()
    

    
    def is_silence(self, audio_data, threshold=0.005):
        """Détecter si l'audio est principalement du silence"""
        # Calcul du volume RMS
        volume = np.sqrt(np.mean(audio_data**2))
        
        # Calcul de l'énergie maximale pour détecter les pics
        max_amplitude = np.max(np.abs(audio_data))
        
        print(f"🔊 Volume: {volume:.6f}, Max: {max_amplitude:.6f}, Seuil: {threshold}")
        
        # Si le volume est très faible ET qu'il n'y a pas de pics significatifs
        is_silent = volume < threshold and max_amplitude < 0.05
        
        if is_silent:
            print(f"🔇 SILENCE DÉTECTÉ (vol: {volume:.6f} < {threshold})")
        else:
            print(f"🔊 AUDIO DÉTECTÉ (vol: {volume:.6f})")
            
        return is_silent
    
    def filter_hallucinations(self, text):
        """Filtrer les hallucinations communes de Whisper"""
        if not text or len(text.strip()) < 3:
            return None
            
        text = text.strip()
        text_lower = text.lower()
        
        # Debug : afficher le texte analysé
        print(f"🔍 Analyse: '{text}' (longueur: {len(text)})")
        
        # Filtrer phrases indésirables (plus strict)
        for phrase in self.unwanted_phrases:
            if phrase.lower().strip() in text_lower:
                print(f"🚫 PHRASE FILTRÉE (hallucination): '{text}' (contient: '{phrase}')")
                return None
        
        # Filtrer si contient "merci" + "vidéo" (capture toutes les variantes)
        if "merci" in text_lower and "vidéo" in text_lower:
            print(f"🚫 FILTRÉ (merci+vidéo): '{text}'")
            return None
            
        # Filtrer si contient "merci" + "regardé"
        if "merci" in text_lower and "regardé" in text_lower:
            print(f"🚫 FILTRÉ (merci+regardé): '{text}'")
            return None
        
        # Éviter répétitions identiques
        if text == self.last_transcription:
            print(f"🔄 RÉPÉTITION IGNORÉE: '{text}'")
            return None
            
        # Filtrer texte trop court
        if len(text) < 5:
            print(f"🚫 TEXTE TROP COURT: '{text}'")
            return None
            
        # Si on arrive ici, le texte est valide
        self.last_transcription = text
        print(f"✅ TEXTE ACCEPTÉ: '{text}'")
        return text
    
    def record_and_transcribe(self):
        """Enregistrement et transcription en boucle"""
        try:
            import sounddevice as sd
            
            # Récupérer dispositif sélectionné
            device_id = self.get_selected_device()
            
            while self.running:
                try:
                    # Enregistrer 3 secondes
                    duration = 3.0
                    sample_rate = 16000
                    
                    self.update_overlay("🎙️ Enregistrement...")
                    
                    audio_data = sd.rec(
                        frames=int(duration * sample_rate),
                        samplerate=sample_rate,
                        channels=1,
                        dtype=np.float32,
                        device=device_id
                    )
                    sd.wait()
                    
                    if not self.running:
                        break
                    
                    # Vérifier si c'est du silence
                    if self.is_silence(audio_data, threshold=0.008):
                        print("🔇 Silence détecté - pas de transcription")
                        self.update_overlay("🔇 Silence détecté...")
                        time.sleep(0.5)  # Petite pause pour éviter de surcharger
                        continue
                    
                    self.update_overlay("🧠 Transcription...")
                    
                    # Transcription avec CPU (stable)
                    audio_flat = audio_data.flatten().astype(np.float32)
                    segments, info = self.model.transcribe(
                        audio_flat,
                        language="fr",
                        beam_size=3,  # Plus conservateur
                        condition_on_previous_text=False,  # Éviter hallucinations
                        temperature=0.0,  # Plus déterministe
                        no_speech_threshold=0.6,  # Plus strict pour éviter faux positifs
                        compression_ratio_threshold=2.4,  # Filtrer répétitions
                        log_prob_threshold=-1.0  # Plus strict
                    )
                    
                    # Collecter texte
                    text_parts = []
                    for segment in segments:
                        text = segment.text.strip()
                        if text:
                            text_parts.append(text)
                    
                    if text_parts:
                        result = " ".join(text_parts)
                        
                        # Filtrer hallucinations
                        filtered_result = self.filter_hallucinations(result)
                        
                        if filtered_result:
                            # Envoyer résultat via queue thread-safe
                            self.transcription_queue.put(filtered_result)
                            print(f"📝 Transcrit: {filtered_result}")
                        else:
                            print("🚫 Transcription filtrée")
                    else:
                        print("🔇 Aucun texte détecté")
                    
                except Exception as e:
                    error_msg = f"❌ Erreur enregistrement: {e}"
                    print(error_msg)
                    self.transcription_queue.put(f"[ERREUR] {str(e)}")
                    time.sleep(1)
        
        except Exception as e:
            print(f"❌ Erreur thread: {e}")
            traceback.print_exc()
    
    def update_overlay(self, text):
        """Mettre à jour overlay (thread-safe)"""
        def update():
            if self.overlay_text:
                self.overlay_text.config(text=text)
        
        if self.root:
            self.root.after(0, update)
    
    def update_display(self, text):
        """Mettre à jour affichage principal (thread-safe)"""
        def update():
            # Ajouter dans zone de texte
            self.text_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {text}\n")
            self.text_area.see(tk.END)
            
            # Mettre à jour overlay
            self.update_overlay(f"💬 {text}")
        
        if self.root:
            self.root.after(0, update)
    
    def check_transcriptions(self):
        """Vérifier nouvelles transcriptions (appelé périodiquement)"""
        try:
            while not self.transcription_queue.empty():
                text = self.transcription_queue.get_nowait()
                self.update_display(text)
                
        except queue.Empty:
            pass
        
        # Programmer prochaine vérification
        if self.running:
            self.root.after(100, self.check_transcriptions)
    
    def start_dictee(self):
        """Démarrer mode dictée"""
        if not self.running and self.model:
            self.running = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="🎤 Dictée active - Parlez!")
            
            # Afficher overlay
            self.overlay_window.deiconify()
            self.update_overlay("🎤 Écoute active...")
            
            # Démarrer thread enregistrement
            self.recording_thread = threading.Thread(target=self.record_and_transcribe)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            # Démarrer vérification transcriptions
            self.check_transcriptions()
            
            # Ajouter message dans zone de texte
            self.text_area.insert(tk.END, f"\n=== SESSION DÉMARRÉE {time.strftime('%H:%M:%S')} ===\n")
            
            print("🎤 Mode dictée démarré - Parlez maintenant!")
    
    def stop_dictee(self):
        """Arrêter mode dictée"""
        if self.running:
            self.running = False
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.status_label.config(text="✅ Prêt")
            
            # Masquer overlay
            self.overlay_window.withdraw()
            
            # Ajouter message dans zone de texte
            self.text_area.insert(tk.END, f"=== SESSION TERMINÉE {time.strftime('%H:%M:%S')} ===\n\n")
            
            print("⏹️ Mode dictée arrêté")
    
    def quit_app(self):
        """Quitter application"""
        self.stop_dictee()
        self.root.destroy()
    
    def run(self):
        """Lancer application"""
        print("🚀 SuperWhisper2 - Dictée Simple")
        print("=" * 50)
        
        # Setup interface
        self.setup_interface()
        self.setup_overlay()
        
        # Modèle déjà initialisé dans __init__
        self.status_label.config(text=f"✅ {self.device_info}")
        
        print("✅ Interface prête!")
        print("💡 Cliquez sur 'Démarrer Dictée' puis parlez")
        print("📺 Une fenêtre overlay apparaîtra pour la transcription live")
        
        # Démarrer interface
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 Application fermée")
        finally:
            self.quit_app()


def main():
    """Point d'entrée principal"""
    app = DicteeSimple()
    app.run()


if __name__ == "__main__":
    main() 