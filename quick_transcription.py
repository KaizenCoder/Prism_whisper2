#!/usr/bin/env python3
"""
Script de transcription rapide pour Prism_whisper2
Compatible RTX 3090, timeout court, gestion erreurs robuste
"""

import sys
import os
import time
import traceback

# Force utilisation GPU RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # RTX 3090 sur GPU 1
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

def transcribe_audio():
    """Transcription audio 3 secondes"""
    try:
        print("PRISM: Initialisation...")
        
        # Imports avec gestion d'erreurs
        try:
            import sounddevice as sd
            import numpy as np
            from faster_whisper import WhisperModel
        except ImportError as e:
            print(f"ERROR: Module manquant: {e}")
            return
        
        # Configuration audio
        duration = 3.0  # 3 secondes
        sample_rate = 16000
        channels = 1
        
        print(f"PRISM: Enregistrement {duration}s...")
        
        # Enregistrement audio (FIX: force float32)
        audio_data = sd.rec(
            frames=int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype=np.float32  # FIX: Force float32 pour éviter erreur ONNX
        )
        
        # Attendre fin enregistrement
        sd.wait()
        
        print("PRISM: Transcription...")
        
        # Initialisation modèle Whisper
        try:
            model = WhisperModel(
                "medium", 
                device="cpu", 
                compute_type="int8"
            )
        except Exception as e:
            print(f"ERROR: Echec chargement modele: {e}")
            return
        
        # Conversion audio (FIX: s'assurer que c'est float32)
        audio_flat = audio_data.flatten().astype(np.float32)
        
        # Transcription avec gestion d'erreurs
        try:
            segments, info = model.transcribe(
                audio_flat, 
                language="fr",
                condition_on_previous_text=False  # Plus rapide
            )
            
            # Collecte résultats
            text_parts = []
            for segment in segments:
                text = segment.text.strip()
                if text:
                    text_parts.append(text)
            
            if text_parts:
                result = " ".join(text_parts)
                print(f"RESULT: {result}")
            else:
                print("RESULT: ")
                
        except Exception as e:
            print(f"ERROR: Echec transcription: {e}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    transcribe_audio() 