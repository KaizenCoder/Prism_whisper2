#!/usr/bin/env python3
"""
Test rapide niveaux audio Rode NT-USB pour diagnostic E3
"""
import sounddevice as sd
import numpy as np
import time

print('🎤 Test Rode NT-USB - Niveaux audio réels')
print('=' * 50)

# Detect Rode
devices = sd.query_devices()
rode_id = None
for i, dev in enumerate(devices):
    if 'rode' in dev['name'].lower() and dev['max_input_channels'] > 0:
        rode_id = i
        break

if rode_id is None:
    print('❌ Rode non trouvé')
    exit(1)

print(f'✅ Rode détecté: ID {rode_id}')
print('📊 Capture 3s pour analyser niveaux...')

audio_data = []
def audio_callback(indata, frames, time, status):
    audio_data.extend(indata[:, 0])

with sd.InputStream(device=rode_id, channels=1, samplerate=16000, 
                   callback=audio_callback, blocksize=1024):
    time.sleep(3)

if len(audio_data) > 0:
    audio_array = np.array(audio_data)
    rms = np.sqrt(np.mean(audio_array ** 2))
    max_val = np.max(np.abs(audio_array))
    
    print(f'📈 RMS: {rms:.6f}')
    print(f'📈 Max: {max_val:.6f}')
    print(f'📈 Samples: {len(audio_array)}')
    
    # Seuils VAD actuels
    print('\n🔍 Seuils VAD actuels:')
    print(f'   min_energy_threshold: 0.0005')
    print(f'   Audio RMS actuel: {rms:.6f}')
    print(f'   Ratio: {rms/0.0005:.1f}x seuil')
    
    if rms < 0.0005:
        print('❌ RMS trop faible - VAD va filtrer')
    else:
        print('✅ RMS suffisant pour VAD')
else:
    print('❌ Aucun audio capturé') 