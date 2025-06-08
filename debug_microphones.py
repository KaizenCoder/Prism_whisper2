#!/usr/bin/env python3
import sounddevice as sd

print("=== TOUS LES DISPOSITIFS AUDIO ===")
devices = sd.query_devices()
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"{i}: {device['name']} (in:{device['max_input_channels']}, channels:{device['max_output_channels']})")

print(f"\nTotal: {len([d for d in devices if d['max_input_channels'] > 0])} microphones") 