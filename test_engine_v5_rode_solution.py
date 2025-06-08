#!/usr/bin/env python3
"""
🎯 TEST ENGINE V5 - SOLUTION FINALE RODE
Modification directe de l'AudioStreamer pour forcer le Rode NT-USB
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

class RodeSolutionTest:
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
        
    def patch_audio_streamer(self):
        """Modifie l'AudioStreamer pour utiliser le Rode"""
        if not hasattr(self.engine, 'streaming_manager'):
            print("❌ StreamingManager non trouvé")
            return False
            
        audio_streamer = self.engine.streaming_manager.audio_streamer
        print(f"📊 AudioStreamer trouvé: {audio_streamer}")
        
        # Sauvegarder la méthode originale
        original_capture_loop = audio_streamer._capture_loop
        
        def patched_capture_loop():
            """Version patchée qui force le device Rode"""
            print(f"🔧 Démarrage capture audio avec Rode Device {self.rode_device}")
            audio_streamer.stream = sd.InputStream(
                device=self.rode_device,  # FORCER LE RODE !
                samplerate=audio_streamer.sample_rate,
                channels=audio_streamer.channels,
                dtype='float32',
                blocksize=audio_streamer.chunk_frames,
                callback=audio_streamer._audio_callback
            )
            with audio_streamer.stream:
                while audio_streamer.running:
                    time.sleep(0.1)
        
        # Remplacer la méthode
        audio_streamer._capture_loop = patched_capture_loop
        print(f"✅ AudioStreamer patché pour utiliser Rode Device {self.rode_device}")
        return True
        
    def test_engine_v5_rode_solution(self):
        """Test Engine V5 avec solution Rode définitive"""
        print("🎯 TEST ENGINE V5 - SOLUTION FINALE RODE")
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
            
            # Configurer callback
            self.engine.set_transcription_callback(self.transcription_callback)
            print("✅ Callback configuré")
                
            # Démarrer l'engine
            print("🎙️ Démarrage Engine V5...")
            success = self.engine.start_engine()
            if not success:
                print("❌ Échec démarrage Engine V5")
                return False
                
            # PATCH CRITIQUE - Forcer le Rode
            print("🔧 Application du patch Rode...")
            if not self.patch_audio_streamer():
                print("❌ Échec patch AudioStreamer")
                return False
                
            # Redémarrer le streaming avec le nouveau device
            print("🔄 Redémarrage streaming avec Rode...")
            self.engine.streaming_manager.audio_streamer.stop()
            time.sleep(1)
            self.engine.streaming_manager.audio_streamer.start()
            
            # Test pendant 30 secondes
            print("🎤 Test audio 30s - Parlez dans le Rode NT-USB !")
            print("🔊 HAUT-PARLEURS COUPÉS + PARLEZ CLAIREMENT")
            
            for i in range(30):
                print(f"⏱️ {30-i}s restantes - Callbacks reçus: {self.callbacks_received}")
                time.sleep(1)
            
            # Arrêter
            print("🛑 Arrêt Engine V5...")
            self.engine.stop_engine()
            
            print(f"📊 RÉSULTATS FINAUX: {self.callbacks_received} callbacks reçus")
            
            if self.callbacks_received > 0:
                print("🎉 SUCCESS ! Engine V5 + Rode NT-USB = FONCTIONNEL")
                return True
            else:
                print("⚠️ Aucun callback reçu - vérifier audio/configuration")
                return False
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    print("🎯 SUPERWHISPER2 - TEST FINAL ENGINE V5 + RODE")
    print("=" * 60)
    
    tester = RodeSolutionTest()
    success = tester.test_engine_v5_rode_solution()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ DIAGNOSTIC COMPLET - ENGINE V5 FONCTIONNEL AVEC RODE !")
        print("🚀 La solution est opérationnelle !")
    else:
        print("❌ Problème persistant - investigation supplémentaire requise")
    print("=" * 60)

if __name__ == "__main__":
    main() 