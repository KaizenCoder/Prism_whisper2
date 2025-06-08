#!/usr/bin/env python3
"""
Test Audio Simple - Diagnostic Rode NT-USB
Vérification rapide de ce qui se passe avec l'audio
"""

import sounddevice as sd
import numpy as np
import time
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def detect_rode():
    """Détection Rode"""
    log("🔍 Recherche Rode NT-USB...")
    
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        device_name = device['name'].lower()
        if any(keyword in device_name for keyword in ['rode', 'nt-usb', 'usb microphone']):
            if device['max_input_channels'] > 0:
                log(f"✅ Rode trouvé: Device {i} - {device['name']}")
                log(f"   📊 Sample Rate: {device['default_samplerate']}Hz")
                log(f"   🎵 Channels: {device['max_input_channels']}")
                return i
    
    log("❌ Rode non trouvé")
    return None

def test_audio_levels(device_id, duration=10):
    """Test des niveaux audio"""
    log(f"🎤 Test audio pendant {duration}s...")
    log("Parlez maintenant dans le microphone !")
    
    try:
        # Capture continue
        chunk_size = int(0.1 * 16000)  # 100ms chunks
        total_chunks = duration * 10  # 10 chunks per second
        
        for i in range(total_chunks):
            # Capture 100ms
            audio_data = sd.rec(chunk_size, samplerate=16000, channels=1, device=device_id)
            sd.wait()
            
            # Analyze
            audio_flat = audio_data.flatten()
            rms = np.sqrt(np.mean(audio_flat**2))
            max_level = np.max(np.abs(audio_flat))
            
            # Status
            if rms > 0.01:  # Strong signal
                status = "🔊 FORT"
            elif rms > 0.005:  # Medium signal
                status = "🔉 MOYEN"
            elif rms > 0.001:  # Weak signal
                status = "🔈 FAIBLE"
            else:  # Very weak/silence
                status = "🔇 SILENCE"
            
            log(f"Chunk {i+1:2d}/{total_chunks}: RMS={rms:.6f}, Max={max_level:.6f} {status}")
            
            time.sleep(0.1)  # Wait for next chunk
            
    except Exception as e:
        log(f"❌ Erreur test audio: {e}")

def test_system_audio():
    """Test audio système"""
    log("🔍 Vérification audio système...")
    
    try:
        # Liste tous les devices
        devices = sd.query_devices()
        
        log("📋 Devices audio disponibles:")
        for i, device in enumerate(devices):
            input_ch = device['max_input_channels']
            output_ch = device['max_output_channels']
            
            if input_ch > 0:
                log(f"   🎤 IN  [{i:2d}] {device['name']} ({input_ch}ch)")
            if output_ch > 0:
                log(f"   🔊 OUT [{i:2d}] {device['name']} ({output_ch}ch)")
        
        # Current default
        default_input = sd.default.device[0]
        default_output = sd.default.device[1]
        
        log(f"📊 Default input: {default_input}")
        log(f"📊 Default output: {default_output}")
        
    except Exception as e:
        log(f"❌ Erreur système audio: {e}")

def main():
    log("🎯 TEST AUDIO SIMPLE - DIAGNOSTIC RODE")
    log("="*50)
    
    # Step 1: System check
    test_system_audio()
    
    # Step 2: Rode detection
    rode_id = detect_rode()
    
    if rode_id is not None:
        # Step 3: Audio test
        log("-" * 30)
        test_audio_levels(rode_id, duration=10)
    else:
        log("❌ Impossible de tester sans Rode")
    
    log("✅ Test terminé")

if __name__ == "__main__":
    main() 