# 🎯 PROMPT DE SUCCESSION - ENGINE V5 SUPERWHISPER2

## 📋 CONTEXTE & MISSION

**Projet** : SuperWhisper2 - Engine V5 avec optimisations Phase 3  
**Hardware** : RTX 3090 24GB + Rode NT-USB + Windows 10  
**Mission** : **TESTER ET VALIDER** la solution de correction des callbacks audio Engine V5  

### 🏆 ÉTAT ACTUEL (Diagnostic 100% Complet)

**✅ VALIDÉ - Composants fonctionnels :**
- **Engine V5 Phase 3** : 5/7 optimisations actives (INT8, faster-whisper, VRAM 24GB, 4 CUDA streams)
- **Rode NT-USB** : Signal audio parfait (RMS 0.015-0.032, device 4 détecté)
- **Callbacks technique** : Signature flexible implémentée et fonctionnelle
- **Architecture** : SuperWhisper2EngineV5 → StreamingManager → AudioStreamer ✅

**❌ PROBLÈME IDENTIFIÉ (Solution développée) :**
- **Device routing** : AudioStreamer utilise device par défaut au lieu du Rode NT-USB
- **Cause root** : `src/audio/audio_streamer.py` ligne 176 - aucun paramètre `device=` configuré
- **Symptôme** : Hallucinations "Amara.org" (capture audio système au lieu du micro)

**🔧 SOLUTION DÉVELOPPÉE ET PRÊTE :**
- **Script** : `test_engine_v5_rode_solution.py` - Patch AudioStreamer pour forcer Rode
- **Niveau de confiance** : **95%** - Tous composants individuellement validés

## 🎯 MISSION IMMÉDIATE

### **ÉTAPE 1 : TEST SOLUTION PATCH**

**Commande à exécuter :**
```bash
# IMPÉRATIF : Couper complètement audio système (haut-parleurs/casque OFF)
python test_engine_v5_rode_solution.py
```

**Procédure test :**
1. **Parler clairement** dans le Rode NT-USB pendant 30 secondes
2. **Observer callbacks** : `[HH:MM:SS] 📝 Callback #N: 'transcription'`
3. **Vérifier** : Aucune hallucination "Amara.org"/"Merci d'avoir regardé"

### **RÉSULTATS ATTENDUS (Succès)** 
```
✅ Rode NT-USB détecté : Device 4
✅ Engine V5 démarré : 5/7 optimisations Phase 3 actives  
✅ AudioStreamer patché : device=4 forcé
🎤 [HH:MM:SS] 📝 Callback #1: 'bonjour je teste le microphone'
🎤 [HH:MM:SS] 📝 Callback #2: 'la transcription fonctionne parfaitement'
✅ 10+ callbacks reçus avec transcription précise
✅ AUCUNE hallucination détectée
```

### **SI SUCCÈS → ÉTAPE 2 : IMPLÉMENTATION PERMANENTE**

**Modifier** : `src/audio/audio_streamer.py`
```python
# Constructeur - Ajouter paramètre device
def __init__(self, callback, logger, sample_rate=16000, chunk_duration=3.0, device=None):
    # ... code existant ...
    self.device = device

# Méthode _capture_loop - Ajouter device au stream
def _capture_loop(self):
    self.stream = sd.InputStream(
        device=self.device,  # ← LIGNE AJOUTÉE
        samplerate=self.sample_rate,
        channels=self.channels,
        dtype=np.float32,
        blocksize=self.chunk_frames,
        callback=self._audio_callback
    )
```

**Puis modifier** : `src/core/streaming_manager.py`
```python
# Constructeur - Ajouter paramètre et passer au AudioStreamer
def __init__(self, logger, callback, device=None):
    # ... code existant ...
    self.audio_streamer = AudioStreamer(
        self.on_audio_ready, 
        logger, 
        device=device  # ← LIGNE AJOUTÉE
    )
```

**Puis modifier** : `src/core/whisper_engine_v5.py`
```python
# Dans start_engine() - Détecter Rode automatiquement
def find_rode_device(self):
    import sounddevice as sd
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if "RODE NT-USB" in device['name'] and device['max_input_channels'] > 0:
            return i
    return None

def start_engine(self):
    # ... code existant ...
    rode_device = self.find_rode_device()
    self.streaming_manager = StreamingManager(
        self.logger, 
        self.transcriber_callback,
        device=rode_device  # ← LIGNE AJOUTÉE
    )
```

### **SI ÉCHEC → DIAGNOSTIC APPROFONDI**

**Commandes diagnostic :**
```bash
# Vérifier devices audio
python test_rode_simple.py

# Vérifier Engine V5 seul
python diagnostic_engine_v5_architecture.py

# Vérifier environnement
python -c "import sounddevice as sd; print('Devices:', len(sd.query_devices()))"
```

**Points à vérifier :**
- Rode NT-USB bien détecté comme device d'entrée
- Engine V5 démarre avec optimisations Phase 3
- Aucun conflit package Python/CUDA
- Audio système complètement coupé

## 📁 SCRIPTS DISPONIBLES

### **Scripts de test :**
- `test_engine_v5_rode_solution.py` - **SCRIPT PRINCIPAL** pour test final
- `test_rode_simple.py` - Test diagnostic Rode NT-USB basique
- `diagnostic_engine_v5_architecture.py` - Diagnostic architecture complète
- `test_audio_simple.py` - Test capture audio générique

### **Scripts de correction :**
- `fix_engine_v5_callbacks_v2.py` - Correction callbacks (signature flexible)
- `test_engine_v5_ultimate.py` - Test GitHub-style (référence)

### **Documentation :**
- `journal_developpement_engine_v5.md` - **JOURNAL COMPLET** diagnostic
- `prompt_succession_engine_v5.md` - **CE DOCUMENT**

## 🚨 POINTS CRITIQUES À RETENIR

### **1. Prérequis absolus pour test :**
- **Audio système COUPÉ** (haut-parleurs/casque OFF) - CRITIQUE
- **Rode NT-USB connecté** et reconnu Windows
- **Environment Python** : torch + faster-whisper + sounddevice

### **2. Signatures techniques validées :**
- **Engine V5** : Classe `SuperWhisper2EngineV5` dans `src/core/whisper_engine_v5.py`
- **Méthode démarrage** : `start_engine()` (PAS `start()`)
- **Device Rode** : Généralement device 4, à détecter dynamiquement
- **Callback flexible** : `def callback(*args, **kwargs)` pour compatibilité

### **3. Métriques de performance attendues :**
- **Engine V5** : 5/7 optimisations Phase 3 actives minimum
- **INT8** : Modèle MEDIUM INT8 chargé (pas LARGE)
- **VRAM** : 5GB/24GB utilisés RTX 3090
- **Audio** : RMS > 0.01 sur parole Rode

## 💡 CONSEILS D'EXÉCUTION

### **Si nouveau développeur :**
1. **Lire entièrement** `journal_developpement_engine_v5.md` 
2. **Comprendre** architecture : Engine V5 → StreamingManager → AudioStreamer
3. **Exécuter tests** dans l'ordre : audio simple → diagnostic → solution

### **Si erreurs Python :**
```bash
# Vérifier packages
pip list | grep -E "torch|whisper|sounddevice"

# Vérifier CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Vérifier imports Engine V5
python -c "import sys; sys.path.insert(0,'src'); from core.whisper_engine_v5 import SuperWhisper2EngineV5"
```

### **Si pas de callbacks :**
- **Vérifier** : Audio système vraiment coupé ?
- **Vérifier** : Parole assez forte dans Rode ?
- **Vérifier** : Engine V5 a bien démarré avec optimisations ?
- **Debug** : Ajouter `print()` dans callbacks pour tracer

## 🎯 OBJECTIF FINAL

**SUCCÈS ATTENDU** :
- ✅ Engine V5 + Rode NT-USB fonctionnent ensemble parfaitement
- ✅ Callbacks temps réel avec transcriptions précises
- ✅ Zero hallucination (audio système correctement ignoré)
- ✅ Performance Phase 3 maintenue (RTX 3090 optimisée)

**LIVRABLES** :
- ✅ Test solution patch validé
- ✅ Modification permanente AudioStreamer implémentée  
- ✅ Documentation mise à jour
- ✅ Configuration robuste Rode NT-USB

**Niveau de confiance solution** : **95%** 
**Estimation durée** : **30 min max** (test + implémentation si succès)

---

## 🚀 COMMANDE DE DÉMARRAGE

```bash
# ⚠️  ÉTAPE OBLIGATOIRE : Couper audio système (haut-parleurs/casque)
# 🎯 PUIS exécuter :
python test_engine_v5_rode_solution.py
```

**Le diagnostic est terminé, la solution est prête. À toi de jouer ! 🚀** 