#!/usr/bin/env python3
"""
Test SuperWhisper2 Engine V3 avec streaming
Validation intégration complète pre-loading + streaming
"""

import sys
import time
sys.path.append('src')

def test_engine_v3():
    """Test complet Engine V3"""
    try:
        from core.whisper_engine_v3 import SuperWhisper2EngineV3
        
        print('🧪 Test Engine V3 avec Streaming...')
        engine = SuperWhisper2EngineV3()
        
        if engine.start_engine():
            print('✅ Engine V3 démarré avec succès')
            
            # Test 1: Transcription classique (backward compatible)
            print('\n🔄 Test 1: Transcription classique...')
            success, result = engine.transcribe_now(timeout=10)
            if success:
                print(f'✅ Transcription classique: {result[:50]}...')
            else:
                print(f'❌ Échec transcription: {result}')
            
            # Test 2: Mode streaming
            print('\n🌊 Test 2: Mode streaming (5s)...')
            if engine.start_streaming_mode():
                print('✅ Streaming mode activé')
                
                # Écouter résultats streaming
                for i in range(5):
                    result = engine.get_streaming_result(timeout=1.0)
                    if result and result.get('success'):
                        text = result.get('text', 'N/A')
                        duration = result.get('duration', 0)
                        print(f'🎵 Stream result {i+1}: {text[:30]}... ({duration:.1f}s)')
                    else:
                        print(f'⏳ Stream {i+1}: Pas de résultat')
                    time.sleep(1)
                
                engine.stop_streaming_mode()
                print('⏹️ Streaming mode arrêté')
            else:
                print('❌ Échec démarrage streaming')
            
            # Test 3: Status complet
            print('\n📊 Test 3: Status V3...')
            status = engine.get_status()
            print(f'Version: {status.get("version")}')
            print(f'Model loaded: {status.get("model_loaded")}')
            print(f'Streaming mode: {status.get("streaming_mode")}')
            if 'streaming_stats' in status:
                stats = status['streaming_stats']
                print(f'Streaming stats: {stats}')
            
            engine.stop_engine()
            print('\n✅ Test V3 terminé avec succès')
            
        else:
            print('❌ Échec démarrage Engine V3')
            
    except ImportError as e:
        print(f'❌ Import error: {e}')
    except Exception as e:
        print(f'❌ Erreur test: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_engine_v3() 