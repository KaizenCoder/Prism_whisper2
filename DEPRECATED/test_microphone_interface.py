#!/usr/bin/env python3
"""
Test validation sélection microphone et interface utilisateur
Teste la nouvelle fonctionnalité de sélection de microphone dans l'interface
"""

import os
import sys
import time
import tkinter as tk
from tkinter import ttk
import threading

def test_microphone_detection():
    """Test détection des microphones disponibles"""
    print("🎤 Test détection microphones...")
    
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        input_devices = []
        print("\n📋 Dispositifs d'entrée détectés:")
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                name = f"{i}: {device['name']}"
                input_devices.append(name)
                
                # Informations détaillées
                print(f"   ID {i}: {device['name']}")
                print(f"        Canaux: {device['max_input_channels']}")
                print(f"        Fréq.: {device['default_samplerate']}Hz")
                print(f"        API: {device['hostapi']}")
                print()
        
        # Dispositif par défaut
        try:
            default_input = sd.query_devices(kind='input')
            print(f"🎯 Dispositif par défaut: {default_input['name']}")
        except Exception as e:
            print(f"⚠️ Erreur dispositif par défaut: {e}")
        
        return input_devices
        
    except ImportError:
        print("❌ sounddevice non disponible")
        return []
    except Exception as e:
        print(f"❌ Erreur détection: {e}")
        return []

def test_microphone_recording(device_id=None):
    """Test enregistrement avec microphone sélectionné"""
    print(f"\n🎙️ Test enregistrement microphone {device_id}...")
    
    try:
        import sounddevice as sd
        import numpy as np
        
        duration = 3.0
        sample_rate = 16000
        
        print(f"   📹 Enregistrement {duration}s...")
        
        # Enregistrement
        audio_data = sd.rec(
            frames=int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.float32,
            device=device_id
        )
        sd.wait()
        
        # Analyse signal
        audio_flat = audio_data.flatten()
        energy = np.mean(audio_flat ** 2)
        max_amplitude = np.max(np.abs(audio_flat))
        
        print(f"   📊 Énergie: {energy:.6f}")
        print(f"   📊 Amplitude max: {max_amplitude:.6f}")
        
        # Vérification signal
        if energy > 0.0001:
            print("   ✅ Signal audio détecté")
            return True
        else:
            print("   ⚠️ Signal très faible ou silence")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur enregistrement: {e}")
        return False

class MicrophoneTestGUI:
    """Interface test microphone"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.recording = False
        self.setup_ui()
    
    def setup_ui(self):
        """Configuration interface"""
        self.root.title("🎤 Test Sélection Microphone")
        self.root.geometry("500x400")
        self.root.configure(bg="#2C3E50")
        
        # Titre
        tk.Label(self.root, text="🎤 Test Sélection Microphone",
                font=("Arial", 16, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(pady=10)
        
        # Sélection microphone
        mic_frame = tk.LabelFrame(self.root, text="Microphone", 
                                 bg="#34495E", fg="#ECF0F1")
        mic_frame.pack(fill="x", padx=20, pady=10)
        
        select_frame = tk.Frame(mic_frame, bg="#34495E")
        select_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(select_frame, text="🎙️", 
                bg="#34495E", fg="#ECF0F1").pack(side="left")
        
        self.mic_var = tk.StringVar()
        self.mic_combo = ttk.Combobox(select_frame, textvariable=self.mic_var,
                                     width=35, state="readonly")
        self.mic_combo.pack(side="left", padx=10, expand=True, fill="x")
        
        tk.Button(select_frame, text="🔄",
                 command=self.refresh_microphones,
                 bg="#3498DB", fg="white").pack(side="right")
        
        # Boutons test
        buttons_frame = tk.Frame(self.root, bg="#2C3E50")
        buttons_frame.pack(pady=20)
        
        self.test_btn = tk.Button(buttons_frame, text="🎤 Test Enregistrement",
                                 command=self.test_recording,
                                 bg="#27AE60", fg="white",
                                 font=("Arial", 12))
        self.test_btn.pack(pady=5)
        
        # Zone résultats
        results_frame = tk.LabelFrame(self.root, text="Résultats",
                                    bg="#34495E", fg="#ECF0F1")
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.results_text = tk.Text(results_frame, height=10,
                                   bg="#2C3E50", fg="#ECF0F1",
                                   font=("Consolas", 10))
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialiser
        self.refresh_microphones()
        self.log("🚀 Interface test microphone initialisée")
    
    def refresh_microphones(self):
        """Rafraîchir liste microphones"""
        try:
            devices = test_microphone_detection()
            self.mic_combo['values'] = devices
            
            if devices:
                self.mic_combo.set(devices[0])
                self.log(f"✅ {len(devices)} microphones détectés")
            else:
                self.log("❌ Aucun microphone détecté")
                
        except Exception as e:
            self.log(f"❌ Erreur refresh: {e}")
    
    def get_selected_device_id(self):
        """Obtenir ID dispositif sélectionné"""
        try:
            selected = self.mic_var.get()
            if selected:
                return int(selected.split(':')[0])
        except:
            pass
        return None
    
    def test_recording(self):
        """Test enregistrement avec microphone sélectionné"""
        if self.recording:
            return
            
        device_id = self.get_selected_device_id()
        
        self.log(f"🎙️ Test avec microphone ID {device_id}")
        self.log("📢 Parlez maintenant pendant 3 secondes...")
        
        self.recording = True
        self.test_btn.config(state="disabled", text="🎙️ Enregistrement...")
        
        def record_thread():
            try:
                success = test_microphone_recording(device_id)
                
                if success:
                    self.log("✅ Enregistrement réussi!")
                else:
                    self.log("⚠️ Signal faible - vérifiez le microphone")
                    
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                
            finally:
                self.recording = False
                self.test_btn.config(state="normal", text="🎤 Test Enregistrement")
        
        threading.Thread(target=record_thread, daemon=True).start()
    
    def log(self, message):
        """Ajouter message aux résultats"""
        timestamp = time.strftime("%H:%M:%S")
        self.results_text.insert("end", f"[{timestamp}] {message}\n")
        self.results_text.see("end")
        self.root.update()
    
    def run(self):
        """Lancer interface"""
        self.root.mainloop()

def main():
    """Test principal"""
    print("🚀 TEST SÉLECTION MICROPHONE - SUPERWHISPER2")
    print("=" * 50)
    
    # Test console
    print("\n1. 🔍 Test détection microphones (console)")
    devices = test_microphone_detection()
    
    if devices:
        print(f"\n✅ {len(devices)} microphones disponibles")
        
        # Test avec premier microphone
        print("\n2. 🎙️ Test enregistrement (premier microphone)")
        device_id = int(devices[0].split(':')[0])
        test_microphone_recording(device_id)
        
    else:
        print("\n❌ Aucun microphone détecté")
    
    # Interface graphique
    print("\n3. 🖥️ Lancement interface graphique...")
    gui = MicrophoneTestGUI()
    gui.run()

if __name__ == "__main__":
    main() 