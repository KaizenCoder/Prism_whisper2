#!/usr/bin/env python3
"""
E3 - STREAMING PIPELINE DEBUG 
Diagnostic approfondi pour résoudre l'interruption du streaming Engine V5

PROBLÈME IDENTIFIÉ:
- E1+E2 corrigés avec succès (device routing + callback guard)
- Engine V5 fait 1 callback puis streaming s'arrête
- AudioStreamer continue mais Engine V5 ne traite plus

OBJECTIF: Identifier le point de rupture dans la chaîne
AudioStreamer → StreamingManager → Engine V5 → Transcription → Callback
"""

import os
import sys
import time
import threading
import queue
import logging
from datetime import datetime
import numpy as np

# Configuration RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajouter src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)


class StreamingPipelineDebugger:
    """
    Debugger spécialisé pour analyser le pipeline streaming Engine V5
    """
    
    def __init__(self):
        self.debug_logs = []
        self.callback_count = 0
        self.audio_chunks_received = 0
        self.engine_callbacks_count = 0
        self.streamer_active = False
        self.engine_active = False
        
        # Setup logging
        self.logger = logging.getLogger('StreamingDebugger')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler pour logs détaillés
        log_file = f"streaming_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler pour l'interface
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter('%(levelname)s: %(message)s')
        
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        print(f"📋 Logs détaillés sauvés dans: {log_file}")
    
    def log_event(self, event_type: str, message: str, data: dict = None):
        """Log un événement avec timestamp et contexte"""
        timestamp = time.time()
        log_entry = {
            'timestamp': timestamp,
            'event_type': event_type,
            'message': message,
            'data': data or {}
        }
        self.debug_logs.append(log_entry)
        self.logger.info(f"[{event_type}] {message}")
        if data:
            self.logger.debug(f"    Data: {data}")
    
    def debug_audio_streamer_flow(self):
        """
        TEST 1: Vérifier que AudioStreamer capture et transmet bien l'audio
        """
        print("\n🔬 TEST 1 - AUDIO STREAMER FLOW")
        print("=" * 60)
        
        try:
            from audio.audio_streamer import AudioStreamer
            from utils.callback_guard import signature_guard
            
            chunks_received = []
            
            @signature_guard
            def debug_audio_callback(audio_data):
                self.audio_chunks_received += 1
                rms = np.sqrt(np.mean(audio_data ** 2)) if len(audio_data) > 0 else 0
                chunks_received.append({
                    'chunk_id': self.audio_chunks_received,
                    'timestamp': time.time(),
                    'rms': rms,
                    'samples': len(audio_data)
                })
                
                self.log_event(
                    "AUDIO_CHUNK", 
                    f"Chunk {self.audio_chunks_received}: RMS={rms:.6f}, samples={len(audio_data)}",
                    {'chunk_id': self.audio_chunks_received, 'rms': rms}
                )
                
                # Simuler que ce chunk va vers Engine V5
                if self.audio_chunks_received <= 3:
                    print(f"  📊 Chunk {self.audio_chunks_received}: RMS={rms:.6f}, {len(audio_data)} samples")
            
            self.log_event("TEST_START", "Starting AudioStreamer flow test")
            
            # Créer AudioStreamer avec nos correctifs E1+E2
            streamer = AudioStreamer(
                callback=debug_audio_callback,
                logger=self.logger,
                sample_rate=16000,
                chunk_duration=1.0,  # 1s chunks pour debug
                device_name="Rode NT-USB"
            )
            
            self.log_event("STREAMER_INIT", f"AudioStreamer created with device_id: {streamer.device_id}")
            print(f"  ✅ AudioStreamer initialisé sur device: {streamer.device_id}")
            
            # Test capture 10 secondes
            print(f"  🎤 Test capture 10 secondes...")
            self.streamer_active = True
            streamer.start()
            
            start_time = time.time()
            while time.time() - start_time < 10:
                time.sleep(1)
                print(f"    {int(time.time() - start_time)}s - Chunks reçus: {self.audio_chunks_received}")
            
            streamer.stop()
            self.streamer_active = False
            
            # Analyse des résultats
            total_chunks = len(chunks_received)
            avg_rms = np.mean([c['rms'] for c in chunks_received]) if chunks_received else 0
            
            self.log_event(
                "TEST_RESULT", 
                f"AudioStreamer test completed: {total_chunks} chunks, avg_rms={avg_rms:.6f}",
                {'total_chunks': total_chunks, 'avg_rms': avg_rms}
            )
            
            print(f"  📊 Résultats: {total_chunks} chunks, RMS moyen: {avg_rms:.6f}")
            
            # Critère de succès: Au moins 8 chunks en 10s (1 chunk/s)
            success = total_chunks >= 8
            print(f"  🎯 TEST 1: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
            return success, chunks_received
            
        except Exception as e:
            self.log_event("ERROR", f"AudioStreamer test failed: {e}")
            print(f"  ❌ ERREUR: {e}")
            return False, []
    
    def debug_engine_v5_integration(self):
        """
        TEST 2: Vérifier l'intégration AudioStreamer → Engine V5
        """
        print("\n🔬 TEST 2 - ENGINE V5 INTEGRATION")
        print("=" * 60)
        
        try:
            from core.whisper_engine_v5 import SuperWhisper2EngineV5
            from utils.callback_guard import signature_guard
            
            transcriptions_received = []
            
            @signature_guard
            def debug_transcription_callback(text: str):
                self.engine_callbacks_count += 1
                timestamp = time.time()
                transcriptions_received.append({
                    'callback_id': self.engine_callbacks_count,
                    'timestamp': timestamp,
                    'text': text[:50] + "..." if len(text) > 50 else text
                })
                
                self.log_event(
                    "ENGINE_CALLBACK", 
                    f"Callback {self.engine_callbacks_count}: '{text[:30]}...'",
                    {'callback_id': self.engine_callbacks_count, 'text_length': len(text)}
                )
                
                print(f"  📝 Callback {self.engine_callbacks_count}: '{text[:50]}...'")
            
            self.log_event("ENGINE_TEST_START", "Starting Engine V5 integration test")
            
            # Initialiser Engine V5
            print(f"  🚀 Initialisation Engine V5...")
            engine = SuperWhisper2EngineV5()
            engine.start_engine()
            
            # Configurer callback protégé par E2
            engine.transcription_callback = debug_transcription_callback
            
            self.log_event("ENGINE_INIT", "Engine V5 initialized and callback configured")
            print(f"  ✅ Engine V5 initialisé")
            
            # Démarrer streaming avec monitoring du pipeline
            print(f"  🌊 Démarrage streaming pipeline...")
            self.engine_active = True
            
            # Accéder au StreamingManager
            streaming_manager = engine.streaming_manager
            
            self.log_event("STREAMING_START", "Starting streaming manager")
            
            # Démarrer le streaming
            streaming_manager.start()
            
            # Monitorer pendant 15 secondes avec diagnostic continu
            start_time = time.time()
            monitoring_interval = 2  # Toutes les 2 secondes
            
            while time.time() - start_time < 15:
                elapsed = int(time.time() - start_time)
                
                # Diagnostic périodique du pipeline
                audio_streamer = streaming_manager.audio_streamer
                
                pipeline_status = {
                    'elapsed': elapsed,
                    'streaming_manager_running': getattr(streaming_manager, 'running', 'unknown'),
                    'audio_streamer_running': getattr(audio_streamer, 'running', 'unknown'),
                    'stream_counter': getattr(streaming_manager, 'stream_counter', 'unknown'),
                    'callbacks_count': self.engine_callbacks_count
                }
                
                self.log_event(
                    "PIPELINE_STATUS", 
                    f"t={elapsed}s: callbacks={self.engine_callbacks_count}, streaming={pipeline_status['streaming_manager_running']}",
                    pipeline_status
                )
                
                print(f"    {elapsed}s - Callbacks reçus: {self.engine_callbacks_count}")
                
                # Alerte si pas de callbacks après 5s
                if elapsed >= 5 and self.engine_callbacks_count == 0:
                    self.log_event("WARNING", "No callbacks received after 5 seconds")
                    print(f"    ⚠️ Aucun callback après 5s - Pipeline probablement cassé")
                
                # Alerte si callbacks s'arrêtent
                if elapsed >= 10 and self.engine_callbacks_count == 1:
                    self.log_event("WARNING", "Streaming stopped after 1 callback")
                    print(f"    ⚠️ Streaming arrêté après 1 callback - Problème confirmé")
                
                time.sleep(monitoring_interval)
            
            # Arrêter streaming
            streaming_manager.stop()
            self.engine_active = False
            
            # Analyse des résultats
            total_callbacks = len(transcriptions_received)
            
            self.log_event(
                "ENGINE_TEST_RESULT", 
                f"Engine V5 test completed: {total_callbacks} callbacks",
                {'total_callbacks': total_callbacks, 'transcriptions': transcriptions_received}
            )
            
            print(f"  📊 Résultats: {total_callbacks} callbacks Engine V5")
            
            # Analyse pattern des callbacks
            if total_callbacks >= 2:
                time_between_callbacks = [
                    transcriptions_received[i]['timestamp'] - transcriptions_received[i-1]['timestamp']
                    for i in range(1, len(transcriptions_received))
                ]
                avg_interval = np.mean(time_between_callbacks)
                print(f"  ⏱️ Intervalle moyen entre callbacks: {avg_interval:.1f}s")
            
            # Critère de succès: Au moins 5 callbacks en 15s
            success = total_callbacks >= 5
            print(f"  🎯 TEST 2: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
            
            return success, transcriptions_received
            
        except Exception as e:
            self.log_event("ERROR", f"Engine V5 test failed: {e}")
            print(f"  ❌ ERREUR: {e}")
            return False, []
    
    def analyze_pipeline_bottleneck(self):
        """
        TEST 3: Analyser les logs pour identifier le bottleneck exact
        """
        print("\n🔬 TEST 3 - PIPELINE BOTTLENECK ANALYSIS")
        print("=" * 60)
        
        # Analyser les événements par type
        events_by_type = {}
        for log in self.debug_logs:
            event_type = log['event_type']
            if event_type not in events_by_type:
                events_by_type[event_type] = []
            events_by_type[event_type].append(log)
        
        print(f"  📊 Événements capturés:")
        for event_type, events in events_by_type.items():
            print(f"    {event_type}: {len(events)} événements")
        
        # Analyser le timing
        if 'AUDIO_CHUNK' in events_by_type and 'ENGINE_CALLBACK' in events_by_type:
            audio_chunks = len(events_by_type['AUDIO_CHUNK'])
            engine_callbacks = len(events_by_type['ENGINE_CALLBACK'])
            
            print(f"\n  📈 Analyse du ratio:")
            print(f"    Audio chunks capturés: {audio_chunks}")
            print(f"    Engine callbacks: {engine_callbacks}")
            print(f"    Ratio: {engine_callbacks/audio_chunks*100:.1f}% callbacks/chunks")
            
            if engine_callbacks == 0:
                print(f"    🔍 PROBLÈME: Aucun callback Engine V5 - Audio n'atteint pas Engine")
            elif engine_callbacks == 1:
                print(f"    🔍 PROBLÈME: 1 seul callback - Streaming s'interrompt après première transcription")
            elif engine_callbacks < audio_chunks * 0.5:
                print(f"    🔍 PROBLÈME: Ratio faible - Perte de chunks entre AudioStreamer et Engine")
        
        # Identifier les gaps temporels
        all_events = sorted(self.debug_logs, key=lambda x: x['timestamp'])
        
        if len(all_events) >= 2:
            print(f"\n  ⏱️ Analyse temporelle:")
            for i in range(1, min(10, len(all_events))):  # Première 10 événements
                prev_event = all_events[i-1]
                curr_event = all_events[i]
                gap = curr_event['timestamp'] - prev_event['timestamp']
                
                if gap > 2.0:  # Gap > 2s suspect
                    print(f"    ⚠️ Gap {gap:.1f}s entre {prev_event['event_type']} et {curr_event['event_type']}")
        
        return events_by_type
    
    def run_full_diagnostic(self):
        """Lance le diagnostic complet E3"""
        print("🔥 DÉMARRAGE DIAGNOSTIC E3 - STREAMING PIPELINE DEBUG")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Objectif: Identifier pourquoi Engine V5 streaming s'interrompt après 1 callback")
        print("=" * 80)
        
        self.log_event("DIAGNOSTIC_START", "Full streaming pipeline diagnostic started")
        
        # Test 1: AudioStreamer flow
        test1_success, audio_chunks = self.debug_audio_streamer_flow()
        
        # Test 2: Engine V5 integration  
        test2_success, transcriptions = self.debug_engine_v5_integration()
        
        # Test 3: Bottleneck analysis
        events_analysis = self.analyze_pipeline_bottleneck()
        
        # Résumé final
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DIAGNOSTIC E3")
        print("=" * 80)
        
        print(f"  Test 1 - AudioStreamer Flow: {'✅ SUCCÈS' if test1_success else '❌ ÉCHEC'}")
        print(f"  Test 2 - Engine V5 Integration: {'✅ SUCCÈS' if test2_success else '❌ ÉCHEC'}")
        print(f"  Audio chunks capturés: {len(audio_chunks)}")
        print(f"  Engine callbacks reçus: {len(transcriptions)}")
        
        # Diagnostic final
        if test1_success and not test2_success:
            conclusion = "🔍 PROBLÈME IDENTIFIÉ: AudioStreamer fonctionne, mais Engine V5 ne traite pas les chunks"
            recommendation = "➡️ SOLUTION: Vérifier le pipeline StreamingManager → Engine V5"
        elif not test1_success:
            conclusion = "🔍 PROBLÈME IDENTIFIÉ: AudioStreamer ne capture pas l'audio correctement"
            recommendation = "➡️ SOLUTION: Revoir la configuration device E1"
        elif test1_success and test2_success:
            conclusion = "✅ PIPELINE FONCTIONNEL: Tests passent, problème peut être intermittent"
            recommendation = "➡️ SOLUTION: Tests plus longs ou conditions spécifiques"
        else:
            conclusion = "🔍 PROBLÈME COMPLEXE: Multiple points de défaillance"
            recommendation = "➡️ SOLUTION: Analyse approfondie des logs"
        
        print(f"\n{conclusion}")
        print(f"{recommendation}")
        
        # Sauver résultats
        result_file = f"diagnostic_e3_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"DIAGNOSTIC E3 - STREAMING PIPELINE DEBUG\n")
            f.write(f"Date: {datetime.now()}\n\n")
            f.write(f"RÉSULTATS:\n")
            f.write(f"- Test AudioStreamer: {'SUCCÈS' if test1_success else 'ÉCHEC'}\n")
            f.write(f"- Test Engine V5: {'SUCCÈS' if test2_success else 'ÉCHEC'}\n")
            f.write(f"- Audio chunks: {len(audio_chunks)}\n")
            f.write(f"- Engine callbacks: {len(transcriptions)}\n\n")
            f.write(f"CONCLUSION: {conclusion}\n")
            f.write(f"RECOMMANDATION: {recommendation}\n")
        
        print(f"\n💾 Résultats sauvés: {result_file}")
        
        self.log_event("DIAGNOSTIC_END", f"Diagnostic completed - conclusion: {conclusion}")
        
        return test1_success and test2_success


def main():
    """Point d'entrée principal du diagnostic E3"""
    debugger = StreamingPipelineDebugger()
    
    try:
        success = debugger.run_full_diagnostic()
        return success
    except KeyboardInterrupt:
        print("\n⏹️ Diagnostic interrompu par l'utilisateur")
        return False
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 