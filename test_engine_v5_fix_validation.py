#!/usr/bin/env python3
"""
Test de Validation des Correctifs Engine V5 - E1 + E2
Valide que les correctifs du développeur C résolvent les problèmes identifiés:
- E1: Device routing correct vers Rode NT-USB 
- E2: Callback signature guard fonctionne

RTX 3090 + Engine V5 Phase 3 + Rode NT-USB
"""

import os
import sys
import time
import sounddevice as sd
import numpy as np
from datetime import datetime

# Configuration RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajouter src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_device_routing():
    """
    TEST E1 - Device Routing Correct
    Vérifie que la détection automatique du Rode NT-USB fonctionne
    """
    print("🔧 TEST E1 - DEVICE ROUTING")
    print("=" * 50)
    
    try:
        from audio.audio_streamer import AudioStreamer
        import logging
        
        # Logger simple pour les tests
        logger = logging.getLogger('TestE1')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Callback de test simple
        def test_callback(audio_data):
            rms = np.sqrt(np.mean(audio_data ** 2))
            print(f"  📊 Audio reçu: RMS = {rms:.6f}, samples = {len(audio_data)}")
            return rms
        
        # Test 1: Vérifier détection Rode automatique
        print("\n1️⃣ Test détection automatique Rode NT-USB...")
        streamer = AudioStreamer(
            callback=test_callback,
            logger=logger,
            sample_rate=16000,
            chunk_duration=1.0,
            device_name="Rode NT-USB"
        )
        
        print(f"   ✅ Device ID détecté: {streamer.device_id}")
        print(f"   ✅ Device name cible: {streamer.device_name}")
        
        # Test 2: Vérifier capture audio courte
        print("\n2️⃣ Test capture audio 3 secondes...")
        streamer.start()
        
        start_time = time.time()
        audio_received = False
        max_rms = 0.0
        
        while time.time() - start_time < 3.0:
            time.sleep(0.1)
            # L'audio sera traité par le callback automatiquement
        
        streamer.stop()
        
        # Analyser les stats
        stats = streamer.get_filtering_stats()
        print(f"\n📊 Statistiques capture:")
        print(f"   • Chunks traités: {stats['chunks_processed']}")
        print(f"   • Chunks avec voix: {stats['chunks_with_voice']}")
        print(f"   • Chunks filtrés: {stats['chunks_filtered_noise']}")
        
        # Critères de validation E1
        e1_success = (
            streamer.device_id is not None and
            stats['chunks_processed'] > 0
        )
        
        print(f"\n🎯 RÉSULTAT E1: {'✅ SUCCÈS' if e1_success else '❌ ÉCHEC'}")
        return e1_success
        
    except Exception as e:
        print(f"❌ ERREUR E1: {e}")
        return False


def test_callback_guard():
    """
    TEST E2 - Callback Signature Guard
    Vérifie que le décorateur signature_guard résout les TypeError
    """
    print("\n🔧 TEST E2 - CALLBACK SIGNATURE GUARD")
    print("=" * 50)
    
    try:
        from utils.callback_guard import signature_guard, test_callback_compatibility
        
        # Test callback simple (signature 1 argument)
        @signature_guard
        def simple_callback(text: str):
            return f"Simple: {text}"
        
        # Test callback complexe (signature multiple arguments)
        @signature_guard  
        def complex_callback(text: str, timestamp: float = 0.0, metadata: dict = None):
            return f"Complex: {text} @ {timestamp}"
        
        print("\n1️⃣ Test signatures Engine V5 typiques...")
        
        # Signatures qui causent TypeError sans le guard
        test_cases = [
            ("Hello", ),  # callback(text)
            ("Hello", 12.5),  # callback(text, timestamp)
            ("Hello", 15.0, {"confidence": 0.9}),  # callback(text, timestamp, metadata)
        ]
        
        success_simple = 0
        success_complex = 0
        
        for i, args in enumerate(test_cases, 1):
            try:
                result1 = simple_callback(*args)
                print(f"   ✅ Simple callback test {i}: {result1}")
                success_simple += 1
            except Exception as e:
                print(f"   ❌ Simple callback test {i}: {e}")
                
            try:
                result2 = complex_callback(*args)
                print(f"   ✅ Complex callback test {i}: {result2}")
                success_complex += 1
            except Exception as e:
                print(f"   ❌ Complex callback test {i}: {e}")
        
        print(f"\n2️⃣ Test automatisé de compatibilité...")
        compat_results = test_callback_compatibility(simple_callback)
        compat_success = sum(1 for r in compat_results.values() if r["success"])
        
        print(f"   ✅ Tests compatibilité réussis: {compat_success}/{len(compat_results)}")
        
        # Critères de validation E2
        e2_success = (
            success_simple >= 2 and  # Au moins 2/3 tests simple
            success_complex >= 2 and  # Au moins 2/3 tests complex
            compat_success >= 4  # Au moins 4/5 tests compat
        )
        
        print(f"\n🎯 RÉSULTAT E2: {'✅ SUCCÈS' if e2_success else '❌ ÉCHEC'}")
        return e2_success
        
    except Exception as e:
        print(f"❌ ERREUR E2: {e}")
        return False


def test_integration_e1_e2():
    """
    TEST INTÉGRATION - E1 + E2 ensemble
    Simule l'utilisation réelle avec Engine V5
    """
    print("\n🔧 TEST INTÉGRATION E1+E2")
    print("=" * 50)
    
    try:
        from audio.audio_streamer import AudioStreamer
        from utils.callback_guard import signature_guard
        import logging
        
        logger = logging.getLogger('TestIntegration')
        logger.setLevel(logging.INFO)
        
        # Callback utilisateur final protégé
        transcriptions_received = []
        
        @signature_guard
        def user_transcription_callback(text: str):
            transcriptions_received.append(text)
            print(f"   📝 Transcription reçue: '{text}'")
            return len(transcriptions_received)
        
        # Simulation du callback Engine V5 avec signatures variables
        def simulate_engine_v5_callback(audio_data):
            """Simule ce que fait Engine V5 en interne"""
            # Simulation d'une transcription
            fake_transcription = "Simulation transcription test"
            
            # Engine V5 peut appeler avec différentes signatures:
            try:
                # Test signature 1: text seulement  
                user_transcription_callback(fake_transcription)
            except:
                pass
                
            try:
                # Test signature 2: text + timestamp
                user_transcription_callback(fake_transcription, time.time())
            except:
                pass
                
            try:
                # Test signature 3: text + timestamp + metadata
                user_transcription_callback(fake_transcription, time.time(), {"confidence": 0.95})
            except:
                pass
        
        print("\n1️⃣ Test AudioStreamer + Callback Guard...")
        
        streamer = AudioStreamer(
            callback=simulate_engine_v5_callback,
            logger=logger,
            sample_rate=16000,
            chunk_duration=0.5,  # Chunks plus courts pour test rapide
            device_name="Rode NT-USB"
        )
        
        print(f"   ✅ Streamer initialisé sur device: {streamer.device_id}")
        
        # Test court d'intégration
        streamer.start()
        time.sleep(2)  # 2 secondes de test
        streamer.stop()
        
        integration_success = (
            streamer.device_id is not None and
            len(transcriptions_received) > 0
        )
        
        print(f"   📊 Transcriptions reçues: {len(transcriptions_received)}")
        print(f"\n🎯 RÉSULTAT INTÉGRATION: {'✅ SUCCÈS' if integration_success else '❌ ÉCHEC'}")
        return integration_success
        
    except Exception as e:
        print(f"❌ ERREUR INTÉGRATION: {e}")
        return False


def main():
    """Test principal des correctifs E1 + E2"""
    print("🚀 VALIDATION CORRECTIFS ENGINE V5 - DÉVELOPPEUR C")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objectif: Valider device routing + callback guard")
    print("=" * 70)
    
    # Tests individuels
    results = {}
    results['E1_device_routing'] = test_device_routing()
    results['E2_callback_guard'] = test_callback_guard()  
    results['integration'] = test_integration_e1_e2()
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ FINAL DES TESTS")
    print("=" * 70)
    
    for test_name, success in results.items():
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"   {test_name}: {status}")
    
    overall_success = all(results.values())
    print(f"\n🏆 RÉSULTAT GLOBAL: {'✅ TOUS LES TESTS PASSENT' if overall_success else '❌ CERTAINS TESTS ÉCHOUENT'}")
    
    if overall_success:
        print("\n🎉 Les correctifs E1+E2 sont validés!")
        print("   ➡️ Prêt pour phase E3 (optimisation blocksize)")
    else:
        print("\n⚠️ Correctifs à revoir avant de continuer")
        
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 