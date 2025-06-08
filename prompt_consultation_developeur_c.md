# 🔬 CONSULTATION DÉVELOPPEUR C - ENGINE V5 STREAMING ISSUE

## 📊 **RÉSUMÉ EXÉCUTIF**
**Problème** : SuperWhisper2 Engine V5 streaming audio s'interrompt après 1 callback  
**Contexte** : Correctifs E1+E2 appliqués avec succès, mais E3 révèle architecture complexe  
**Status** : BLOQUÉ après 4h30 d'investigation et multiple root causes traitées  
**Demande** : Avis technique sur approche alternative ou révision architecture streaming

---

## ✅ **CORRECTIFS RÉUSSIS (E1+E2)**

### **E1 - Device Routing** ✅ RÉSOLU
```python
# Avant: sd.InputStream() → capture device par défaut (ID 0)
# Après: sd.InputStream(device=4) → force Rode NT-USB
# IMPACT: WER bypass 94.1% → 59.8% (-34% amélioration)
```

### **E2 - Callback Signature** ✅ RÉSOLU  
```python
@signature_guard  # Adapte (text, timestamp, metadata) → (text)
def callback(text): pass
# IMPACT: Plus de TypeError callback
```

---

## ❌ **PROBLÈME PERSISTANT (E3)**

### **Symptômes**
- ✅ AudioStreamer détecte Rode correctement (device ID 4)
- ✅ Engine V5 s'initialise sans erreur (optimisations 5/7)
- ❌ **Streaming callbacks = 0** (vs attendu > 10 en 60s)
- ❌ **Tests manuel fonctionne** : `manager.on_audio_ready(test_chunk)` → transcription OK
- ❌ **Streaming automatique cassé** : Aucun callback reçu

### **Tests Diagnostiques**
```bash
# Test 1 - AudioStreamer standalone
python debug_streaming_pipeline_e3.py
→ Résultat: 0 chunks audio (VAD filtre tout)

# Test 2 - Engine V5 integration  
→ Résultat: 0 callbacks Engine V5 (pipeline cassé)

# Test 3 - Manuel trigger
manager.on_audio_ready(test_audio) → ✅ Fonctionne
```

---

## 🔍 **ROOT CAUSES MULTIPLES TRAITÉES**

### **1. VAD Over-filtering** (Partiellement corrigé)
```python
# AVANT: 
self.min_voice_ratio = 0.3     # 30% du chunk = voix
self.vad.set_mode(2)           # Mode agressif

# APRÈS:
self.min_voice_ratio = 0.1     # 10% du chunk = voix  
self.vad.set_mode(1)           # Mode moins agressif

# LOGS: chunks_with_voice: 0, chunks_filtered_noise: 9
# STATUS: Amélioration mais insufficient
```

### **2. Threading Issues** (Corrigé)
```python
# AVANT: 
threading.Thread(target=self.transcriber_callback, args=...).start()

# APRÈS:
thread = threading.Thread(
    target=self._safe_transcriber_callback,
    args=...,
    daemon=True  # ✅ Daemon pour continuité
)
thread.start()
```

### **3. Hallucination Filter Continuity** (Corrigé)
```python
# AVANT: 
if self._is_hallucination(text):
    return  # CASSAIT le streaming

# APRÈS:
if self._is_hallucination(text):
    self.logger.debug("🔄 Streaming continue malgré hallucination...")
    return  # OK - juste ignorer cette transcription
```

---

## 🏗️ **ARCHITECTURE ANALYSÉE**

### **Pipeline Actuel**
```
AudioStreamer(device=4) → StreamingManager.on_audio_ready() → Engine.process_audio_chunk()
     ↑ ✅ OK                      ↑ ❌ PROBLÈME                     ↑ ✅ Fonctionne manuellement
```

### **Diagnostic Points de Rupture**
1. **AudioStreamer → VAD** : ❌ Filtre 100% chunks  
2. **VAD → StreamingManager** : ❌ Aucun chunk transmis
3. **StreamingManager → Engine** : ⚠️ Fonctionne si appelé manuellement
4. **Engine → Callback** : ✅ Fonctionne si audio fourni

---

## 📄 **CODE CLÉS ANALYSÉS**

### **AudioStreamer._audio_callback()** (src/audio/audio_streamer.py:216)
```python
def _audio_callback(self, indata, frames, time_info, status):
    # 1. Vérifier activité vocale avec VAD (E3: mode permissif)
    if not self.vad.has_voice_activity(audio_chunk):
        self.stats['chunks_filtered_noise'] += 1
        # E3 DEBUG: Log détails filtrage
        energy = np.mean(audio_chunk ** 2)
        self.logger.debug(f"🔇 Chunk filtré - Énergie: {energy:.6f}")
        return  # ← POINT DE RUPTURE: Tous les chunks filtrés
```

### **StreamingManager.on_audio_ready()** (src/core/streaming_manager.py:42)
```python
def on_audio_ready(self, audio_chunk: np.ndarray):
    if not self.running:
        return
    
    # E3.2 FIX: Thread daemon pour maintenir continuité
    thread = threading.Thread(
        target=self._safe_transcriber_callback,
        args=(audio_chunk, model, stream_id),
        daemon=True
    )
    thread.start()  # ← Jamais appelé car AudioStreamer filtre tout
```

---

## 🧪 **TESTS TECHNIQUES DISPONIBLES**

### **Scripts de Diagnostic**
1. `debug_streaming_pipeline_e3.py` - Diagnostic pipeline complet
2. `test_engine_v5_ultimate.py` - Test intégration + bypass
3. `test_engine_v5_fix_validation.py` - Validation E1+E2

### **Logs Disponibles**
- `streaming_debug_*.log` - Logs détaillés pipeline
- `diagnostic_e3_results_*.txt` - Résultats diagnostic
- Tests Engine V5 JSON + TXT

---

## 🔧 **OPTIONS TECHNIQUES ENVISAGÉES**

### **Option A - VAD Bypass Temporaire**
```python
# Désactiver VAD temporairement pour validation
def has_voice_activity(self, audio_chunk: np.ndarray) -> bool:
    return True  # Force passage de tous les chunks
```
**Pros** : Test rapide si VAD est vraiment le problème  
**Cons** : Perte filtrage hallucinations

### **Option B - Seuils VAD Ultra-Permissifs**
```python
self.min_voice_ratio = 0.01      # 1% du chunk
self.min_energy_threshold = 0.0001  # Seuil très bas
```
**Pros** : Garde logique VAD  
**Cons** : Peut laisser passer beaucoup de bruit

### **Option C - Architecture Streaming Alternative**
```python
# Remplacer pipeline par capture directe
def simple_streaming_loop():
    while running:
        chunk = capture_audio_chunk()
        if len(chunk) > 0:  # Bypass VAD
            process_chunk(chunk)
```
**Pros** : Simple, pas de VAD complexe  
**Cons** : Refactoring important

### **Option D - Investigation Hardware**
```python
# Test niveaux audio réels Rode NT-USB
def diagnose_rode_levels():
    # Vérifier si gain micro suffisant
    # Tester différents sample rates 
    # Analyser RMS réels vs seuils VAD
```

---

## 🎯 **QUESTIONS TECHNIQUES SPÉCIFIQUES**

1. **VAD Strategy** : Faut-il désactiver complètement VAD pour Engine V5 ?

2. **Threading Model** : L'approche daemon threads est-elle correcte ou faut-il un pool ?

3. **Architecture Alternative** : Préférer capture directe vs pipeline AudioStreamer→StreamingManager ?

4. **Hardware Specific** : Y a-t-il des spécificités Rode NT-USB (gain, sample rate) à considérer ?

5. **Performance Trade-offs** : Quel équilibre entre filtrage hallucinations et streaming continu ?

---

## 🚀 **DEMANDE CONSULTATION**

### **Avis Demandé**
1. **Diagnostic** : Quelle approche privilégier pour débloquer le streaming ?
2. **Architecture** : Faut-il refactoriser le pipeline ou corriger VAD ?
3. **Priorités** : Streaming continu vs filtrage hallucinations ?

### **Livrable Attendu**
- Recommandation technique claire (Option A/B/C/D ou autre)
- Code exemple si refactoring nécessaire
- Estimation temps pour implémentation

### **Contexte Budget**
- **Temps déjà investi** : 4h30 (E1: 30min, E2: 45min, E3: 3h15min)
- **Temps restant estimé** : 2-3h selon solution
- **Criticité** : Haute - Engine V5 est l'objectif principal du projet

---

## 📎 **FICHIERS TECHNIQUES ANNEXES**

### **Logs & Diagnostics**
- `streaming_debug_20250609_005200.log` - Debug pipeline complet
- `diagnostic_e3_results_20250609_005237.txt` - Résultats tests
- `test_engine_v5_ultimate_20250609_005651.json` - Métriques performance

### **Code Modifié**
- `src/audio/audio_streamer.py` - E1+E3 (device routing + VAD tuning)
- `src/core/streaming_manager.py` - E3 (threading fixes)
- `src/core/whisper_engine_v5.py` - E3 (hallucination continuity)
- `src/utils/callback_guard.py` - E2 (signature adaptation)

---

**🎯 Question finale : Quelle approche recommandes-tu pour débloquer définitivement le streaming Engine V5 ?** 