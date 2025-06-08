#!/usr/bin/env python3
"""
Diagnostic Architecture Engine V5 SuperWhisper2
Analyse laser-focalisée sur l'architecture interne pour identifier le problème callbacks
RTX 3090 24GB + Engine V5 Phase 3 + Analyse complète
"""

import os
import sys
import inspect
import threading
import time
from datetime import datetime
import numpy as np
import sounddevice as sd

# Configuration RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # RTX 3090 24GB
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajouter src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)


class EngineV5ArchitectureDiagnostic:
    def __init__(self):
        self.engine = None
        self.components = {}
        self.analysis_results = {}
        
    def log(self, message, level="INFO"):
        """Logging avec timestamp et niveau"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")
    
    def initialize_engine(self):
        """Initialisation Engine V5"""
        self.log("🚀 INITIALISATION ENGINE V5", "INIT")
        
        try:
            # Import Engine V5
            from src.core.whisper_engine_v5 import SuperWhisper2EngineV5
            
            # Create instance
            self.engine = SuperWhisper2EngineV5()
            
            # Start engine
            success = self.engine.start_engine()
            
            if success:
                self.log("✅ Engine V5 initialisé avec succès", "SUCCESS")
                return True
            else:
                self.log("❌ Échec initialisation Engine V5", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur initialisation: {e}", "ERROR")
            return False
    
    def analyze_complete_architecture(self):
        """Analyse complète de l'architecture Engine V5"""
        self.log("="*80, "HEADER")
        self.log("🏗️ ANALYSE ARCHITECTURE COMPLETE ENGINE V5", "HEADER")
        self.log("="*80, "HEADER")
        
        # 1. Components discovery
        self.log("🔍 DÉCOUVERTE COMPOSANTS", "SECTION")
        self.discover_components()
        
        # 2. Callback chain analysis
        self.log("🔗 ANALYSE CHAÎNE CALLBACKS", "SECTION")
        self.analyze_callback_chain()
        
        # 3. Audio pipeline analysis
        self.log("🎵 ANALYSE PIPELINE AUDIO", "SECTION")
        self.analyze_audio_pipeline()
        
        # 4. StreamingManager deep dive
        self.log("🎧 ANALYSE STREAMING MANAGER", "SECTION")
        self.analyze_streaming_manager()
        
        # 5. AudioStreamer analysis
        self.log("🎤 ANALYSE AUDIO STREAMER", "SECTION")
        self.analyze_audio_streamer()
        
        # 6. Method signatures analysis
        self.log("📝 ANALYSE SIGNATURES MÉTHODES", "SECTION")
        self.analyze_method_signatures()
        
        # 7. State monitoring
        self.log("📊 MONITORING ÉTATS", "SECTION")
        self.monitor_states()
        
        # 8. Generate report
        self.log("📋 RAPPORT DIAGNOSTIC", "SECTION")
        self.generate_diagnostic_report()
    
    def discover_components(self):
        """Découverte de tous les composants Engine V5"""
        engine_attrs = dir(self.engine)
        
        # Filter interesting attributes
        interesting_attrs = [
            attr for attr in engine_attrs 
            if not attr.startswith('__') and 
            not attr.startswith('_') and
            attr not in ['start_engine', 'stop_engine', 'get_phase3_status']
        ]
        
        self.log(f"📦 Attributs intéressants trouvés: {len(interesting_attrs)}")
        
        for attr_name in interesting_attrs:
            try:
                attr_obj = getattr(self.engine, attr_name)
                attr_type = type(attr_obj).__name__
                
                if attr_obj is not None:
                    self.components[attr_name] = attr_obj
                    self.log(f"   ✅ {attr_name}: {attr_type}")
                    
                    # If it's a class instance, analyze its methods
                    if hasattr(attr_obj, '__dict__'):
                        methods = [m for m in dir(attr_obj) if callable(getattr(attr_obj, m)) and not m.startswith('_')]
                        if methods:
                            self.log(f"      📋 Methods: {', '.join(methods[:5])}{'...' if len(methods) > 5 else ''}")
                else:
                    self.log(f"   ⚪ {attr_name}: None")
                    
            except Exception as e:
                self.log(f"   ❌ {attr_name}: Error accessing - {e}")
    
    def analyze_callback_chain(self):
        """Analyse de la chaîne de callbacks"""
        # 1. Engine-level callback
        callback_attrs = [
            '_transcription_callback', 'transcription_callback', 'callback',
            'on_transcription', 'transcription_handler'
        ]
        
        self.log("🔗 Callbacks au niveau Engine:")
        for attr in callback_attrs:
            if hasattr(self.engine, attr):
                callback = getattr(self.engine, attr)
                self.log(f"   ✅ {attr}: {callback}")
            else:
                self.log(f"   ❌ {attr}: Not found")
        
        # 2. Component-level callbacks
        for comp_name, comp_obj in self.components.items():
            if comp_obj and hasattr(comp_obj, '__dict__'):
                self.log(f"🔗 Callbacks dans {comp_name}:")
                
                for attr in callback_attrs:
                    if hasattr(comp_obj, attr):
                        callback = getattr(comp_obj, attr)
                        self.log(f"   ✅ {comp_name}.{attr}: {callback}")
        
        # 3. Method-based callbacks
        self.log("🔗 Méthodes callback potentielles:")
        for comp_name, comp_obj in self.components.items():
            if comp_obj:
                callback_methods = [
                    m for m in dir(comp_obj) 
                    if 'callback' in m.lower() or 'transcrib' in m.lower()
                ]
                
                if callback_methods:
                    self.log(f"   📞 {comp_name}: {callback_methods}")
    
    def analyze_audio_pipeline(self):
        """Analyse du pipeline audio"""
        # 1. Audio sources
        audio_sources = ['audio_streamer', 'microphone', 'audio_input', 'audio_source']
        
        self.log("🎵 Sources audio:")
        for source in audio_sources:
            if source in self.components:
                obj = self.components[source]
                self.log(f"   ✅ {source}: {type(obj).__name__}")
                
                # Analyze audio source configuration
                if hasattr(obj, 'device_id'):
                    device_id = getattr(obj, 'device_id', 'N/A')
                    self.log(f"      📊 device_id: {device_id}")
                
                if hasattr(obj, 'sample_rate'):
                    sample_rate = getattr(obj, 'sample_rate', 'N/A')
                    self.log(f"      📊 sample_rate: {sample_rate}")
                
                if hasattr(obj, 'is_recording'):
                    is_recording = getattr(obj, 'is_recording')
                    if callable(is_recording):
                        is_recording = is_recording()
                    self.log(f"      📊 is_recording: {is_recording}")
        
        # 2. Audio processors
        processors = ['streaming_manager', 'audio_processor', 'processor']
        
        self.log("🔄 Processeurs audio:")
        for proc in processors:
            if proc in self.components:
                obj = self.components[proc]
                self.log(f"   ✅ {proc}: {type(obj).__name__}")
                
                # Look for audio processing methods
                audio_methods = [
                    m for m in dir(obj) 
                    if any(keyword in m.lower() for keyword in ['audio', 'stream', 'process'])
                ]
                
                if audio_methods:
                    self.log(f"      🔧 Audio methods: {audio_methods[:3]}{'...' if len(audio_methods) > 3 else ''}")
    
    def analyze_streaming_manager(self):
        """Analyse approfondie du StreamingManager"""
        if 'streaming_manager' not in self.components:
            self.log("❌ StreamingManager non trouvé")
            return
        
        manager = self.components['streaming_manager']
        self.log(f"🎧 StreamingManager: {type(manager).__name__}")
        
        # 1. All attributes
        attrs = [attr for attr in dir(manager) if not attr.startswith('__')]
        self.log(f"   📋 Total attributs: {len(attrs)}")
        
        # 2. Critical attributes
        critical_attrs = [
            'running', 'active', 'is_streaming', 'stream_counter',
            'audio_streamer', 'transcriber', 'callback'
        ]
        
        self.log("   📊 Attributs critiques:")
        for attr in critical_attrs:
            if hasattr(manager, attr):
                try:
                    value = getattr(manager, attr)
                    if callable(value):
                        # Try to call with no args
                        try:
                            value = value()
                        except:
                            value = f"<method {attr}>"
                    self.log(f"      ✅ {attr}: {value}")
                except Exception as e:
                    self.log(f"      ❌ {attr}: Error - {e}")
        
        # 3. Audio-related methods
        audio_methods = [
            m for m in dir(manager) 
            if any(keyword in m.lower() for keyword in ['audio', 'stream', 'start', 'stop'])
        ]
        
        self.log(f"   🎵 Méthodes audio ({len(audio_methods)}):")
        for method in audio_methods:
            if callable(getattr(manager, method)):
                try:
                    sig = inspect.signature(getattr(manager, method))
                    self.log(f"      📝 {method}{sig}")
                except:
                    self.log(f"      📝 {method}()")
        
        # 4. Callback-related methods
        callback_methods = [
            m for m in dir(manager) 
            if any(keyword in m.lower() for keyword in ['callback', 'transcrib', 'ready'])
        ]
        
        if callback_methods:
            self.log(f"   📞 Méthodes callback ({len(callback_methods)}):")
            for method in callback_methods:
                self.log(f"      📞 {method}")
    
    def analyze_audio_streamer(self):
        """Analyse approfondie de l'AudioStreamer"""
        if 'audio_streamer' not in self.components:
            self.log("❌ AudioStreamer non trouvé")
            return
        
        streamer = self.components['audio_streamer']
        self.log(f"🎤 AudioStreamer: {type(streamer).__name__}")
        
        # 1. Configuration attributes
        config_attrs = [
            'device_id', 'sample_rate', 'chunk_size', 'format', 'channels',
            'buffer_size', 'latency', 'dtype'
        ]
        
        self.log("   ⚙️ Configuration:")
        for attr in config_attrs:
            if hasattr(streamer, attr):
                try:
                    value = getattr(streamer, attr)
                    self.log(f"      📊 {attr}: {value}")
                except Exception as e:
                    self.log(f"      ❌ {attr}: Error - {e}")
        
        # 2. State attributes
        state_attrs = [
            'is_recording', 'is_active', 'running', 'active', 'started',
            'stream', 'status'
        ]
        
        self.log("   📊 État:")
        for attr in state_attrs:
            if hasattr(streamer, attr):
                try:
                    value = getattr(streamer, attr)
                    if callable(value):
                        try:
                            value = value()
                        except:
                            value = f"<method {attr}>"
                    self.log(f"      📊 {attr}: {value}")
                except Exception as e:
                    self.log(f"      ❌ {attr}: Error - {e}")
        
        # 3. Control methods
        control_methods = [
            'start', 'stop', 'restart', 'pause', 'resume',
            'begin_recording', 'stop_recording'
        ]
        
        self.log("   🎮 Méthodes de contrôle:")
        for method in control_methods:
            if hasattr(streamer, method) and callable(getattr(streamer, method)):
                self.log(f"      🎮 {method}()")
    
    def analyze_method_signatures(self):
        """Analyse des signatures de méthodes importantes"""
        # Key methods to analyze
        key_methods = [
            ('engine', self.engine, [
                'set_transcription_callback', 'start_listening', 'stop_listening',
                'process_audio', 'on_audio_ready'
            ])
        ]
        
        # Add component methods
        for comp_name, comp_obj in self.components.items():
            if comp_obj:
                methods = []
                if 'streaming' in comp_name.lower():
                    methods = ['start', 'stop', 'on_audio_ready', 'transcriber_callback']
                elif 'audio' in comp_name.lower():
                    methods = ['start', 'stop', 'process_audio', 'on_audio']
                
                if methods:
                    key_methods.append((comp_name, comp_obj, methods))
        
        for obj_name, obj, methods in key_methods:
            self.log(f"📝 Signatures {obj_name}:")
            
            for method_name in methods:
                if hasattr(obj, method_name):
                    method = getattr(obj, method_name)
                    if callable(method):
                        try:
                            sig = inspect.signature(method)
                            self.log(f"   📝 {method_name}{sig}")
                        except Exception as e:
                            self.log(f"   ❌ {method_name}: Signature error - {e}")
    
    def monitor_states(self):
        """Monitoring des états en temps réel"""
        self.log("📊 Démarrage monitoring états...")
        
        def monitoring_thread():
            for i in range(10):  # Monitor for 10 seconds
                self.log(f"📊 État #{i+1}:")
                
                # Monitor StreamingManager
                if 'streaming_manager' in self.components:
                    manager = self.components['streaming_manager']
                    
                    states = ['running', 'stream_counter', 'active']
                    for state in states:
                        if hasattr(manager, state):
                            try:
                                value = getattr(manager, state)
                                if callable(value):
                                    value = value()
                                self.log(f"   📊 StreamingManager.{state}: {value}")
                            except:
                                pass
                
                # Monitor AudioStreamer
                if 'audio_streamer' in self.components:
                    streamer = self.components['audio_streamer']
                    
                    states = ['is_recording', 'is_active']
                    for state in states:
                        if hasattr(streamer, state):
                            try:
                                value = getattr(streamer, state)
                                if callable(value):
                                    value = value()
                                self.log(f"   📊 AudioStreamer.{state}: {value}")
                            except:
                                pass
                
                time.sleep(1)
        
        threading.Thread(target=monitoring_thread, daemon=True).start()
    
    def generate_diagnostic_report(self):
        """Génération du rapport de diagnostic"""
        self.log("="*80, "HEADER")
        self.log("📋 RAPPORT DIAGNOSTIC ENGINE V5", "HEADER")
        self.log("="*80, "HEADER")
        
        # 1. Components summary
        self.log(f"📦 Composants trouvés: {len(self.components)}")
        for name, obj in self.components.items():
            self.log(f"   • {name}: {type(obj).__name__}")
        
        # 2. Critical issues identification
        self.log("🚨 PROBLÈMES CRITIQUES IDENTIFIÉS:")
        
        issues = []
        
        # Check if audio streamer exists and is configured
        if 'audio_streamer' not in self.components:
            issues.append("❌ AudioStreamer manquant")
        else:
            streamer = self.components['audio_streamer']
            if not hasattr(streamer, 'device_id'):
                issues.append("❌ AudioStreamer sans device_id")
        
        # Check if streaming manager exists
        if 'streaming_manager' not in self.components:
            issues.append("❌ StreamingManager manquant")
        else:
            manager = self.components['streaming_manager']
            if not hasattr(manager, 'on_audio_ready'):
                issues.append("❌ StreamingManager sans on_audio_ready()")
        
        # Check callback chain
        if not hasattr(self.engine, '_transcription_callback'):
            issues.append("❌ Pas de callback configuré sur l'engine")
        
        if issues:
            for issue in issues:
                self.log(f"   {issue}")
        else:
            self.log("   ✅ Aucun problème critique détecté")
        
        # 3. Recommendations
        self.log("💡 RECOMMANDATIONS:")
        
        if 'streaming_manager' in self.components and 'audio_streamer' in self.components:
            self.log("   1. Forcer la connexion AudioStreamer → StreamingManager")
            self.log("   2. Configurer le device_id sur l'AudioStreamer")
            self.log("   3. Activer manuellement le StreamingManager")
            self.log("   4. Injecter de l'audio de test via on_audio_ready()")
        
        self.log("="*80, "HEADER")
    
    def run_diagnostic(self):
        """Lancement du diagnostic complet"""
        print("🎯 ENGINE V5 ARCHITECTURE DIAGNOSTIC")
        print("="*50)
        
        # Initialize
        if not self.initialize_engine():
            return False
        
        # Run complete analysis
        self.analyze_complete_architecture()
        
        return True


def main():
    """Point d'entrée principal"""
    diagnostic = EngineV5ArchitectureDiagnostic()
    
    try:
        success = diagnostic.run_diagnostic()
        
        if success:
            print("\n✅ Diagnostic terminé avec succès")
        else:
            print("\n❌ Diagnostic échoué")
            
    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 