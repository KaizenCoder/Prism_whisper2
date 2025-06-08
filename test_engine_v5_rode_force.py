#!/usr/bin/env python3
"""
🎯 TEST ENGINE V5 - RODE FORCE
Forcer l'Engine V5 à utiliser exclusivement le Rode NT-USB
"""

import sys
import time
import sounddevice as sd
import threading
from pathlib import Path

# Ajouter le dossier src à Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from core.whisper_engine_v5 import SuperWhisper2EngineV5 as EngineV5
    print("✅ Engine V5 importé avec succès")
except ImportError as e:
    print(f"❌ Erreur import Engine V5: {e}")
    sys.exit(1)

class RodeForceTest:
    def __init__(self):
        self.engine = None
        self.rode_device = None
        self.callbacks_received = 0
        
    def find_rode_device(self):
        """Trouve le device Rode NT-USB"""
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if "RODE NT-USB" in device['name'] and device['max_input_channels'] > 0:
                print(f"🎤 Rode trouvé: Device {i} - {device['name']}")
                return i
        return None
        
    def transcription_callback(self, transcription, *args, **kwargs):
        """Callback pour recevoir les transcriptions"""
        self.callbacks_received += 1
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] 📝 Callback #{self.callbacks_received}: '{transcription}'")
        
    def test_engine_v5_rode(self):
        """Test Engine V5 forcé sur Rode"""
        print("🎯 TEST ENGINE V5 - FORCE RODE NT-USB")
        print("=" * 50)
        
        # Trouver le Rode
        self.rode_device = self.find_rode_device()
        if self.rode_device is None:
            print("❌ Rode NT-USB non trouvé !")
            return False
            
        try:
            # Initialiser Engine V5
            print("🚀 Initialisation Engine V5...")
            self.engine = EngineV5()
            
            # Vérifier si Engine V5 a un paramètre pour device
            print("🔧 Configuration device audio...")
            
            # Configurer callback AVANT le démarrage
            if hasattr(self.engine, 'set_transcription_callback'):
                self.engine.set_transcription_callback(self.transcription_callback)
                print("✅ Callback configuré")
            elif hasattr(self.engine, 'transcription_callback'):
                self.engine.transcription_callback = self.transcription_callback
                print("✅ Callback assigné directement")
                
            # Démarrer l'engine
            print("🎙️ Démarrage Engine V5...")
            success = self.engine.start_engine()
            if not success:
                print("❌ Échec démarrage Engine V5")
                return False
                
            # Modifier le device APRÈS démarrage (quand streaming_manager est créé)
            print("🔧 Configuration device audio...")
            if hasattr(self.engine, 'streaming_manager') and self.engine.streaming_manager:
                streamer = self.engine.streaming_manager
                print(f"📊 StreamingManager trouvé: {streamer}")
                
                # Essayer de modifier le device
                if hasattr(streamer, 'device_index'):
                    print(f"🔄 Device actuel: {streamer.device_index}")
                    streamer.device_index = self.rode_device
                    print(f"✅ Device changé vers Rode: {self.rode_device}")
                elif hasattr(streamer, 'device'):
                    print(f"🔄 Device actuel: {streamer.device}")
                    streamer.device = self.rode_device
                    print(f"✅ Device changé vers Rode: {self.rode_device}")
                else:
                    print("⚠️ Impossible de modifier le device audio")
            else:
                print("⚠️ StreamingManager non trouvé")
            
            # Test pendant 20 secondes
            print("🎤 Test audio 20s - Parlez dans le Rode NT-USB !")
            print("🔊 ASSUREZ-VOUS QUE LES HAUT-PARLEURS SONT COUPÉS")
            time.sleep(20)
            
            # Arrêter
            print("🛑 Arrêt Engine V5...")
            self.engine.stop()
            
            print(f"📊 Résultats: {self.callbacks_received} callbacks reçus")
            return self.callbacks_received > 0
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def test_audio_direct_rode(self):
        """Test direct du Rode avec niveau de bruit"""
        print("\n🔍 TEST AUDIO DIRECT RODE")
        print("-" * 30)
        
        def audio_callback(indata, frames, time, status):
            """Callback audio direct"""
            if status:
                print(f"❌ Status: {status}")
            
            # Calculer RMS et Max
            rms = float((indata ** 2).mean() ** 0.5)
            max_val = float(abs(indata).max())
            
            # Niveau
            if max_val > 0.02:
                level = "🔊 FORT"
            elif max_val > 0.005:
                level = "🔉 MOYEN"
            else:
                level = "🔈 FAIBLE"
                
            print(f"Rode Direct: RMS={rms:.6f}, Max={max_val:.6f} {level}")
            
        try:
            print(f"🎤 Écoute Rode Device {self.rode_device} pendant 10s...")
            with sd.InputStream(device=self.rode_device, 
                              samplerate=16000, 
                              channels=1,
                              callback=audio_callback):
                time.sleep(10)
            print("✅ Test audio direct terminé")
            
        except Exception as e:
            print(f"❌ Erreur test direct: {e}")

def main():
    tester = RodeForceTest()
    
    # Test 1: Audio direct Rode
    tester.test_audio_direct_rode()
    
    # Test 2: Engine V5 forcé
    success = tester.test_engine_v5_rode()
    
    if success:
        print("🎉 ENGINE V5 + RODE = SUCCESS !")
    else:
        print("⚠️ Problème persistant - device ou callback")

if __name__ == "__main__":
    main() 