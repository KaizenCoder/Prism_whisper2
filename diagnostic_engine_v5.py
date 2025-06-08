#!/usr/bin/env python3
"""
Diagnostic complet Engine V5 SuperWhisper2
Script pour investiguer en profondeur les problèmes de streaming audio
"""

import os
import sys
import time
import sounddevice as sd

# Configuration RTX 3090
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajouter src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def detect_rode():
    """Detect Rode microphone"""
    print("🔍 Detecting Rode microphone...")
    devices = sd.query_devices()
    rode_keywords = ['rode', 'nt-usb', 'nt usb', 'procaster', 'podmic']
    
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            device_name = device['name'].lower()
            for keyword in rode_keywords:
                if keyword in device_name:
                    print(f"✅ RODE FOUND: {device['name']} (ID: {i})")
                    return i
    return None

def diagnostic_engine_v5():
    """Diagnostic complet Engine V5"""
    print("=" * 80)
    print("🔧 DIAGNOSTIC ENGINE V5 COMPLET")
    print("=" * 80)
    
    # Step 1: Import Engine V5
    try:
        print("📦 Importing SuperWhisper2 Engine V5...")
        from src.core.whisper_engine_v5 import SuperWhisper2EngineV5
        print("✅ Import successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Step 2: Create instance
    try:
        print("⚙️ Creating Engine V5 instance...")
        engine = SuperWhisper2EngineV5()
        print("✅ Instance created")
    except Exception as e:
        print(f"❌ Instance creation failed: {e}")
        return
    
    # Step 3: Start engine
    try:
        print("🎮 Starting Engine V5...")
        success = engine.start_engine()
        print(f"Engine start result: {success}")
        
        if success:
            print("✅ Engine started successfully")
            status = engine.get_phase3_status()
            print(f"📊 Optimizations: {status['optimizations_count']}/{status['total_optimizations']}")
        else:
            print("❌ Engine start failed")
            return
    except Exception as e:
        print(f"❌ Engine start error: {e}")
        return
    
    # Step 4: Complete method inspection
    print("\n" + "=" * 60)
    print("🔍 COMPLETE ENGINE V5 METHOD INSPECTION")
    print("=" * 60)
    
    all_attrs = dir(engine)
    public_attrs = [attr for attr in all_attrs if not attr.startswith('_')]
    
    methods = []
    attributes = []
    
    for attr in public_attrs:
        try:
            obj = getattr(engine, attr)
            if callable(obj):
                methods.append(attr)
                print(f"✅ METHOD: {attr}()")
            else:
                attributes.append(attr)
                print(f"📦 ATTRIBUTE: {attr} = {type(obj).__name__}")
        except Exception as e:
            print(f"❌ ERROR accessing {attr}: {e}")
    
    print(f"\n📊 Total methods: {len(methods)}")
    print(f"📊 Total attributes: {len(attributes)}")
    
    # Step 5: Audio components inspection
    print("\n" + "=" * 60)
    print("🎤 AUDIO COMPONENTS DEEP DIVE")
    print("=" * 60)
    
    # Check streaming_manager
    if hasattr(engine, 'streaming_manager') and engine.streaming_manager:
        manager = engine.streaming_manager
        print(f"🎧 StreamingManager found: {type(manager).__name__}")
        
        print("   🔍 StreamingManager methods:")
        manager_attrs = dir(manager)
        for attr in manager_attrs:
            if not attr.startswith('_'):
                try:
                    obj = getattr(manager, attr)
                    if callable(obj):
                        print(f"     ✅ {attr}()")
                        
                        # Try to get method info
                        try:
                            import inspect
                            sig = inspect.signature(obj)
                            print(f"       → {attr}{sig}")
                        except:
                            pass
                    else:
                        print(f"     📦 {attr} = {type(obj).__name__}")
                except Exception as e:
                    print(f"     ❌ {attr}: {e}")
    
    # Check audio_streamer
    if hasattr(engine, 'audio_streamer') and engine.audio_streamer:
        streamer = engine.audio_streamer
        print(f"\n🎵 AudioStreamer found: {type(streamer).__name__}")
        
        print("   🔍 AudioStreamer methods:")
        streamer_attrs = dir(streamer)
        for attr in streamer_attrs:
            if not attr.startswith('_'):
                try:
                    obj = getattr(streamer, attr)
                    if callable(obj):
                        print(f"     ✅ {attr}()")
                    else:
                        print(f"     📦 {attr} = {type(obj).__name__}")
                except Exception as e:
                    print(f"     ❌ {attr}: {e}")
    
    # Step 6: Callback test
    print("\n" + "=" * 60)
    print("🔄 CALLBACK SYSTEM TEST")
    print("=" * 60)
    
    callback_received = False
    
    def test_callback(text):
        global callback_received
        callback_received = True
        print(f"✅ CALLBACK RECEIVED: '{text}'")
    
    try:
        print("🔧 Setting test callback...")
        engine.set_transcription_callback(test_callback)
        print("✅ Callback set successfully")
        
        # Wait for potential callbacks
        print("⏳ Waiting 10 seconds for callbacks...")
        time.sleep(10)
        
        if callback_received:
            print("✅ Callback system is working!")
        else:
            print("⚠️ No callbacks received - streaming may not be active")
            
    except Exception as e:
        print(f"❌ Callback setup error: {e}")
    
    # Step 7: Force streaming activation
    print("\n" + "=" * 60)
    print("🚀 FORCE STREAMING ACTIVATION TEST")
    print("=" * 60)
    
    # Detect Rode
    rode_id = detect_rode()
    if rode_id is not None:
        print(f"🎤 Using Rode device ID: {rode_id}")
        
        # Try all possible activation methods
        if hasattr(engine, 'streaming_manager') and engine.streaming_manager:
            manager = engine.streaming_manager
            
            activation_methods = [
                'start_streaming', 'start', 'begin', 'activate', 'enable',
                'listen', 'record', 'capture', 'force_restart', 'resume'
            ]
            
            for method_name in activation_methods:
                if hasattr(manager, method_name):
                    try:
                        method = getattr(manager, method_name)
                        if callable(method):
                            print(f"🎯 Trying {method_name}()...")
                            result = method()
                            print(f"✅ {method_name}() → {result}")
                    except Exception as e:
                        print(f"⚠️ {method_name}() error: {e}")
            
            # Test state methods
            state_methods = ['is_streaming', 'is_active', 'is_listening', 'get_status']
            for method_name in state_methods:
                if hasattr(manager, method_name):
                    try:
                        method = getattr(manager, method_name)
                        if callable(method):
                            state = method()
                            print(f"📊 {method_name}() → {state}")
                    except Exception as e:
                        print(f"⚠️ {method_name}() error: {e}")
    
    # 🎯 Phase 3: Test d'activation complète
    print("\n=== 🎯 PHASE 3: ACTIVATION TEST ===")
    print("🔧 Testing StreamingManager activation...")
    
    manager = engine.streaming_manager
    initial_running = getattr(manager, 'running', 'N/A')
    initial_counter = getattr(manager, 'stream_counter', 'N/A')
    
    print(f"📊 Initial state: running={initial_running}, counter={initial_counter}")
    
    # Test activation methods
    activation_methods = ['start', 'start_streaming', 'begin', 'activate', 'enable']
    for method_name in activation_methods:
        if hasattr(manager, method_name) and callable(getattr(manager, method_name)):
            try:
                method = getattr(manager, method_name)
                result = method()
                print(f"✅ {method_name}() → {result}")
                
                # Check state after activation
                post_running = getattr(manager, 'running', 'N/A')
                post_counter = getattr(manager, 'stream_counter', 'N/A')
                print(f"📊 Post-{method_name}: running={post_running}, counter={post_counter}")
                break
                
            except Exception as e:
                print(f"⚠️ {method_name}() error: {e}")
    
    # 🎵 Phase 4: AudioStreamer Deep Dive
    print("\n=== 🎵 PHASE 4: AUDIOSTREAMER ANALYSIS ===")
    if hasattr(manager, 'audio_streamer') and manager.audio_streamer:
        streamer = manager.audio_streamer
        print(f"✅ AudioStreamer found: {type(streamer).__name__}")
        
        # Get all AudioStreamer attributes
        streamer_info = {}
        test_attrs = [
            'device_id', 'device', 'sample_rate', 'chunk_size', 
            'is_recording', 'active', 'running', 'streaming',
            'channels', 'format', 'frames_per_buffer'
        ]
        
        for attr in test_attrs:
            if hasattr(streamer, attr):
                try:
                    value = getattr(streamer, attr)
                    streamer_info[attr] = value
                    print(f"  📊 {attr}: {value}")
                except Exception as e:
                    print(f"  ⚠️ {attr}: error - {e}")
        
        # Test AudioStreamer methods
        print("\n🔧 Testing AudioStreamer methods:")
        streamer_methods = ['start', 'begin_recording', 'activate', 'enable', 'listen']
        for method_name in streamer_methods:
            if hasattr(streamer, method_name) and callable(getattr(streamer, method_name)):
                try:
                    method = getattr(streamer, method_name)
                    # Check method signature
                    import inspect
                    sig = inspect.signature(method)
                    print(f"  📝 {method_name}{sig}")
                    
                    # Try to call if no parameters needed
                    if len(sig.parameters) == 0:
                        result = method()
                        print(f"  ✅ {method_name}() → {result}")
                    else:
                        print(f"  📋 {method_name} requires parameters: {list(sig.parameters.keys())}")
                        
                except Exception as e:
                    print(f"  ⚠️ {method_name} error: {e}")
    
    else:
        print("❌ No AudioStreamer found in StreamingManager")
    
    # 🔗 Phase 5: Callback Chain Analysis  
    print("\n=== 🔗 PHASE 5: CALLBACK CHAIN ===")
    
    # Test callback setup
    def test_callback(text):
        print(f"🎯 TEST CALLBACK RECEIVED: '{text}'")
        
    print("🔧 Setting up test callback...")
    try:
        engine.set_transcription_callback(test_callback)
        print("✅ Callback configured successfully")
    except Exception as e:
        print(f"⚠️ Callback configuration error: {e}")
    
    # Analyze callback chain
    callback_methods = ['transcriber_callback', 'on_audio_ready', 'on_transcription']
    for method_name in callback_methods:
        if hasattr(manager, method_name):
            try:
                method = getattr(manager, method_name)
                if callable(method):
                    import inspect
                    sig = inspect.signature(method)
                    print(f"📞 {method_name}{sig}")
                else:
                    print(f"📦 {method_name}: {method}")
            except Exception as e:
                print(f"⚠️ {method_name} analysis error: {e}")
    
    # 🎤 Phase 6: Device Configuration Test
    print("\n=== 🎤 PHASE 6: DEVICE CONFIGURATION ===")
    
    # Test device methods on StreamingManager
    device_methods = ['set_device', 'set_audio_device', 'configure_device', 'set_device_id']
    rode_device_id = detect_rode()
    
    if rode_device_id is not None:
        print(f"🎤 Testing device configuration with Rode ID: {rode_device_id}")
        for method_name in device_methods:
            if hasattr(manager, method_name) and callable(getattr(manager, method_name)):
                try:
                    method = getattr(manager, method_name)
                    result = method(rode_device_id)
                    print(f"✅ {method_name}({rode_device_id}) → {result}")
                except Exception as e:
                    print(f"⚠️ {method_name}({rode_device_id}) error: {e}")
        
        # Test device methods on AudioStreamer
        if hasattr(manager, 'audio_streamer') and manager.audio_streamer:
            streamer = manager.audio_streamer
            print(f"\n🎵 Testing AudioStreamer device configuration:")
            for method_name in device_methods:
                if hasattr(streamer, method_name) and callable(getattr(streamer, method_name)):
                    try:
                        method = getattr(streamer, method_name)
                        result = method(rode_device_id)
                        print(f"✅ AudioStreamer.{method_name}({rode_device_id}) → {result}")
                    except Exception as e:
                        print(f"⚠️ AudioStreamer.{method_name}({rode_device_id}) error: {e}")
    
    print("\n" + "="*80)
    print("✅ DIAGNOSTIC ENGINE V5 COMPLET")
    print("="*80)
    
    return True

if __name__ == "__main__":
    diagnostic_engine_v5() 