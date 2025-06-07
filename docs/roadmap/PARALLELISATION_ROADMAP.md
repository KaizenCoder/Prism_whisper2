# ⚡ ROADMAP PARALLÉLISATION - Prism_whisper2
## Optimisations Performance : 7-8s → <3s latence

### **🎯 OBJECTIF PERFORMANCE**
- **Latence actuelle** : 7-8 secondes
- **Latence cible** : <3 secondes  
- **Latence optimale** : <1 seconde (stretch goal)

---

## 📊 **ANALYSE BOTTLENECKS ACTUELS**

### **Profiling Latence Actuelle**
```
Win+Alt+V pressed → [100ms] → Talon detection
    ↓
Trigger file created → [50ms] → Bridge detection  
    ↓
Audio recording → [3000ms] → 3 seconds fixed
    ↓
Model loading → [4000ms] → Whisper model init ⚠️ BOTTLENECK #1
    ↓
Transcription → [800ms] → GPU processing
    ↓
Clipboard + Paste → [150ms] → Windows integration
    ↓
TOTAL: ~8100ms
```

### **Bottlenecks Critiques Identifiés**
1. **🚨 Model Loading (4s)** : Whisper init à chaque appel
2. **⚠️ Fixed Recording (3s)** : Pas de détection fin de phrase
3. **🔄 Sequential Pipeline** : Pas de parallélisation

---

## 🚀 **STRATÉGIES DE PARALLÉLISATION**

### **Phase 1 : Model Pre-loading (Gain: -4s)**

#### **Architecture Proposée : Background Service**
```python
# Service permanent en arrière-plan
class WhisperService:
    def __init__(self):
        self.model = WhisperModel("medium", device="cuda")  # Pré-chargé
        self.queue = asyncio.Queue()
        
    async def start_service(self):
        """Service permanent écoute requests"""
        while True:
            audio_data = await self.queue.get()
            result = await self.transcribe_async(audio_data)
            await self.send_result(result)
```

#### **Communication IPC optimisée**
- **Named Pipes** au lieu de fichiers
- **Memory mapping** pour audio data
- **Async callbacks** pour résultats

#### **Implémentation**
```
Process 1: PrismBridge (hotkey detection)
Process 2: WhisperService (modèle pré-chargé permanent)
Process 3: AudioCapture (recording continu)
```

### **Phase 2 : Smart Audio Capture (Gain: -1.5s)**

#### **VAD (Voice Activity Detection)**
```python
class SmartAudioCapture:
    def __init__(self):
        self.vad = webrtcvad.Vad(3)  # Aggressivité max
        self.buffer = CircularBuffer(5000)  # 5s buffer
        
    async def capture_with_vad(self):
        """Capture jusqu'à détection silence"""
        while True:
            chunk = await self.record_chunk(100ms)
            if self.vad.is_speech(chunk):
                self.buffer.add(chunk)
            elif len(self.buffer) > 500ms:  # Fin détectée
                return self.buffer.get_audio()
```

#### **Streaming Audio**
- **Capture continue** en background
- **Trigger déclenche** processing du buffer
- **Adaptive duration** : 0.5s - 10s selon contenu

### **Phase 3 : Pipeline Async (Gain: -1s)**

#### **Architecture Pipeline**
```python
async def optimized_pipeline():
    # Parallélisation maximale
    audio_task = asyncio.create_task(capture_audio())
    
    # Pendant capture audio, préparer transcription
    model_task = asyncio.create_task(prepare_model())
    
    # Dès audio prêt, démarrer transcription
    audio_data = await audio_task
    transcription_task = asyncio.create_task(
        transcribe_async(audio_data)
    )
    
    # Pendant transcription, préparer clipboard
    clipboard_task = asyncio.create_task(prepare_clipboard())
    
    # Finaliser
    text = await transcription_task
    await paste_text(text)
```

### **Phase 4 : Hardware Optimizations (Gain: -0.5s)**

#### **GPU Stream Parallel**
```python
# Multiple CUDA streams pour paralléliser
stream1 = torch.cuda.Stream()
stream2 = torch.cuda.Stream()

with torch.cuda.stream(stream1):
    # Pre-processing audio
    audio_tensor = preprocess_audio(raw_audio)
    
with torch.cuda.stream(stream2):
    # Pendant ce temps, préparer modèle
    model.prepare_next_inference()
```

#### **Memory Pool Management**
- **Pre-allocated tensors** pour éviter malloc/free
- **Circular buffers** GPU memory
- **Zero-copy** transfers CPU↔GPU

---

## 📋 **PLAN D'IMPLÉMENTATION**

### **Sprint 1 : Background Service (Week 1)**
**Effort** : 8-12h  
**Gain attendu** : 8s → 4s

#### **Tasks**
- [ ] **Whisper Service Process** : Service permanent + IPC
- [ ] **Bridge Refactor** : Communication async avec service
- [ ] **Process Management** : Auto-restart, healthcheck
- [ ] **Testing** : Validation performance + stabilité

#### **Code Changes**
```
src/services/whisper_service.py     # Nouveau service
src/bridge/prism_bridge.py          # Refactor communication
src/ipc/named_pipes.py             # Communication optimisée
tests/test_background_service.py   # Tests performance
```

### **Sprint 2 : Smart Audio (Week 2)**
**Effort** : 6-8h  
**Gain attendu** : 4s → 2.5s

#### **Tasks**
- [ ] **VAD Integration** : webrtcvad ou similar
- [ ] **Adaptive Recording** : Dynamic duration
- [ ] **Audio Buffers** : Circular buffer management
- [ ] **Edge Cases** : Silence handling, noise filtering

### **Sprint 3 : Pipeline Async (Week 3)**
**Effort** : 4-6h  
**Gain attendu** : 2.5s → 1.5s

#### **Tasks**
- [ ] **Async Pipeline** : Refactor séquentiel → async
- [ ] **Task Management** : asyncio orchestration
- [ ] **Error Handling** : Async error propagation
- [ ] **Performance Monitoring** : Latency tracking

### **Sprint 4 : Hardware Optimization (Week 4)**
**Effort** : 6-10h  
**Gain attendu** : 1.5s → <1s

#### **Tasks**
- [ ] **GPU Streams** : CUDA parallel processing
- [ ] **Memory Optimization** : Pre-allocation, zero-copy
- [ ] **Batch Processing** : Multiple requests handling
- [ ] **Profiling** : GPU utilization optimization

---

## 📊 **MÉTRIQUES & MONITORING**

### **Performance Tracking**
```python
class PerformanceMonitor:
    def track_latency(self):
        stages = {
            'hotkey_detection': 0,
            'audio_capture': 0,
            'transcription': 0,
            'clipboard_paste': 0,
            'total': 0
        }
        return stages
```

### **Target Metrics Par Sprint**
| Sprint | Latence Cible | Bottleneck Focus | Success Criteria |
|--------|---------------|------------------|------------------|
| 1 | <4s | Model loading | Service starts <200ms |
| 2 | <2.5s | Audio capture | VAD detection <500ms |
| 3 | <1.5s | Pipeline sync | Async overlap 70% |
| 4 | <1s | GPU utilization | GPU usage >80% |

### **Monitoring Dashboard**
- **Real-time latency** : Per-stage timing
- **Resource usage** : CPU, GPU, Memory
- **Error rates** : Failed transcriptions, timeouts
- **User satisfaction** : Perceived responsiveness

---

## 🚨 **RISQUES & MITIGATION**

### **Risques Techniques**
1. **Complexity increase** → Phased rollout, extensive testing
2. **Memory usage spike** → Resource monitoring, limits
3. **Service stability** → Auto-restart, health checks
4. **GPU contention** → Queue management, priority system

### **Fallback Strategy**
- **Graceful degradation** : Si service fails → fallback mode actuel
- **Performance monitoring** : Auto-switch si latence dégradée
- **User notification** : Feedback si problème détecté

---

## 🎯 **SUCCESS CRITERIA**

### **MVP Optimisé (End of Sprint 2)**
- **Latence <3s** : Objectif principal atteint
- **Reliability >99%** : Pas de régression stabilité
- **User feedback positive** : Tests utilisateurs

### **Production Ready (End of Sprint 4)**
- **Latence <1s** : Performance optimale
- **Monitoring complet** : Dashboard + alerting
- **Documentation** : Setup, troubleshooting, tuning

---

**🚀 ROADMAP EXECUTION : 4 sprints x 1 semaine = 1 mois pour transformation complète performance** 