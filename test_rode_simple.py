#!/usr/bin/env python3
"""
🎯 TEST RODE SIMPLE - DIAGNOSTIC
"""

import sounddevice as sd

def main():
    print("🎯 TEST RODE SIMPLE")
    print("=" * 30)
    
    try:
        # Lister tous les devices
        print("📋 Devices audio disponibles:")
        devices = sd.query_devices()
        
        rode_found = False
        rode_device = None
        
        for i, device in enumerate(devices):
            device_name = device['name']
            if device['max_input_channels'] > 0:
                print(f"🎤 IN  [{i:2d}] {device_name} ({device['max_input_channels']}ch)")
                
                if "RODE NT-USB" in device_name:
                    rode_found = True
                    rode_device = i
                    print(f"    ✅ RODE TROUVÉ ! Device {i}")
            
            if device['max_output_channels'] > 0:
                print(f"🔊 OUT [{i:2d}] {device_name} ({device['max_output_channels']}ch)")
        
        if rode_found:
            print(f"\n🎤 Rode NT-USB: Device {rode_device}")
            print("✅ Test réussi - Rode détecté")
        else:
            print("\n❌ Rode NT-USB NON TROUVÉ")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 