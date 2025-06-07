# SuperWhisper2 - Prompt de Transmission 🔄

**Pour** : Prochains développeurs / IA assistants  
**Date** : Janvier 2025  
**Contexte** : Développement SuperWhisper2 Windows  
**Statut** : Phase de documentation et architecture initiale  

---

## 🎯 Contexte du Projet

Vous prenez la suite du développement de **SuperWhisper2**, un équivalent Windows de SuperWhisper Mac optimisé pour RTX 3090. Le projet vise à créer une solution de transcription vocale native Windows avec intégration Talon.

### Configuration Hardware Cible
- **GPU Principal** : NVIDIA RTX 3090 24GB VRAM sur PCIe Gen5 x16
- **GPU Secondaire** : RTX 5060 Ti pour affichage
- **Modèles IA** : Stockés sur D:\modeles_ia (faster-whisper optimisé)
- **OS** : Windows 10/11 avec Talon Voice installé

### État Actuel du Projet
```
SuperWhisper2/                    # ✅ Créé
├── src/                          # ✅ Structure créée
│   ├── core/                     # ⬜ À implémenter
│   ├── whisper_engine/           # ⬜ À implémenter
│   ├── talon_plugin/             # ⬜ À implémenter
│   └── ui/                       # ⬜ À implémenter
├── config/                       # ✅ Créé
├── docs/                         # ✅ Créé
├── tests/                        # ✅ Créé
├── README.md                     # ✅ Complet
├── MANIFEST.md                   # ✅ Complet
└── HANDOFF_PROMPT.md            # ✅ Ce fichier
```

## 🚀 Objectif Immédiat

Implémenter un **MVP fonctionnel** permettant :
1. **Win+Shift+V** → Capture audio
2. **Transcription RTX 3090** → Texte français/anglais
3. **Insertion automatique** → Dans application active
4. **Interface system tray** → Status et configuration

### Critères de Succès MVP
- [ ] Latence totale < 1 seconde (hotkey → texte inséré)
- [ ] Transcription française > 95% précision
- [ ] Fonctionne dans Word, Teams, Outlook, Chrome
- [ ] Interface system tray avec start/stop
- [ ] Installation automatique fonctionnelle

## 🛠️ Architecture Technique

### Pattern de Développement Recommandé
```python
# 1. Core Engine - Orchestrateur principal
class SuperWhisper2Engine:
    def __init__(self):
        self.whisper_engine = WhisperRTXEngine()
        self.talon_interface = TalonInterface()
        self.audio_capture = AudioCapture()
    
    async def handle_hotkey(self):
        audio = await self.audio_capture.record()
        text = await self.whisper_engine.transcribe(audio)
        await self.talon_interface.insert_text(text)

# 2. Whisper Engine - RTX 3090 optimisé
class WhisperRTXEngine:
    def __init__(self):
        os.environ["HF_HOME"] = "D:/modeles_ia"
        self.model = WhisperModel("medium", device="cuda")
    
    async def transcribe(self, audio):
        # Implémentation faster-whisper optimisée

# 3. Talon Interface - Intégration système
class TalonInterface:
    def setup_global_hotkey(self, callback):
        # Configuration Win+Shift+V
    
    async def insert_text(self, text):
        # Insertion dans app active
```

### Dépendances Critiques
```toml
[tool.poetry.dependencies]
python = "^3.11"
faster-whisper = "^0.10.0"
torch = "^2.0.0+cu118"
sounddevice = "^0.4.0"
pystray = "^0.19.0"
asyncio = "^3.11.0"
```

## 📋 Plan de Développement Suggéré

### Étape 1 : Foundation (Priorité 1)
```bash
# Créer la structure de base
touch src/core/__init__.py
touch src/core/engine.py
touch src/whisper_engine/__init__.py
touch src/whisper_engine/rtx_engine.py
touch pyproject.toml

# Implémenter le core engine minimal
# Test : python -m src.core.engine
```

### Étape 2 : Whisper RTX Integration (Priorité 1)
```python
# Objectif : Transcription fonctionnelle
from faster_whisper import WhisperModel

# Configuration RTX 3090
os.environ["HF_HOME"] = "D:/modeles_ia"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # RTX 3090

# Test de performance
model = WhisperModel("medium", device="cuda", compute_type="float16")
# Benchmark : doit faire 2.5x temps réel minimum
```

### Étape 3 : Talon Plugin (Priorité 2)
```python
# Talon script pour hotkeys globaux
# Fichier : superwhisper2.talon

key(cmd-shift-v): user.superwhisper2_activate()

# Python handler
from talon import Module, actions
module = Module()

@module.action_class
class Actions:
    def superwhisper2_activate():
        """Démarre la transcription SuperWhisper2"""
        # Appel vers engine Python
```

### Étape 4 : Audio Pipeline (Priorité 2)
```python
import sounddevice as sd
import numpy as np

class AudioCapture:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
    
    async def record_until_silence(self):
        # VAD (Voice Activity Detection)
        # Retourne audio array pour Whisper
```

## 🔧 Défis Techniques Anticipés

### 1. Latence RTX 3090
**Problème** : Chargement initial du modèle peut prendre 2-3 secondes  
**Solution** : 
```python
# Pre-loading et cache persistant
class WhisperRTXEngine:
    def __init__(self):
        self.model = None
        self._preload_model()
    
    def _preload_model(self):
        # Charger en arrière-plan au démarrage
```

### 2. Intégration Talon
**Problème** : Communication Python ↔ Talon  
**Solution** :
```python
# Socket/pipe communication ou shared memory
# Talon → Python : Hotkey détecté
# Python → Talon : Texte à insérer
```

### 3. Audio Capture
**Problème** : Détection fin de parole (VAD)  
**Solution** :
```python
# Utiliser webrtcvad ou implémentation custom
import webrtcvad
vad = webrtcvad.Vad(2)  # Agressivité moyenne
```

## 🧪 Tests Critiques

### Test Performance RTX 3090
```python
# Benchmark obligatoire
def test_rtx3090_performance():
    model = WhisperModel("medium", device="cuda")
    
    # Test 30 secondes audio français
    start = time.time()
    result = model.transcribe("test_audio_30s.wav")
    duration = time.time() - start
    
    assert duration < 12.0  # 2.5x temps réel minimum
    assert result.language == "fr"
```

### Test Intégration Talon
```python
def test_talon_integration():
    # Simuler Win+Shift+V
    # Vérifier callback appelé
    # Vérifier texte inséré correctement
```

### Test Qualité Transcription
```python
def test_transcription_quality():
    # Audio de référence français
    expected = "Bonjour, ceci est un test de qualité."
    result = engine.transcribe("reference_fr.wav")
    
    wer = calculate_wer(expected, result.text)
    assert wer < 0.05  # 95%+ précision
```

## 📚 Ressources Essentielles

### Documentation Technique
- **Talon API** : https://talonvoice.com/docs/
- **faster-whisper** : https://github.com/guillaumekln/faster-whisper
- **RTX 3090 CUDA** : Optimisations mémoire et compute

### ⭐ **Documents Projet Essentiels**
- **SUPERWHISPER_AUDIT.md** : Audit complet code existant SuperWhisper
- **CODE_ANALYSIS.md** : Analyse technique scripts core fonctionnels
- **ACTION_PLAN.md** : Plan 3 semaines ACTUALISÉ (évolution vs révolution)
- **README.md, MANIFEST.md** : Vision et objectifs du projet

### Code Existant Réutilisable ⭐ **BASE FONCTIONNELLE**
- **C:\Dev\SuperWhisper** : Scripts transcription existants FONCTIONNELS
- **transcription_simple.py** : RTX 3090 engine (3.4KB, PARFAIT)
- **dictee_superwhisper.py** : Système dictée temps réel (12KB, FONCTIONNEL)
- **D:\modeles_ia** : Modèles pré-téléchargés et optimisés
- **venv_superwhisper** : Environment Python configuré

### Configuration Système
```bash
# Variables d'environnement critiques
HF_HOME=D:\modeles_ia
HF_CACHE_DIR=D:\modeles_ia\huggingface\hub
CUDA_VISIBLE_DEVICES=0  # RTX 3090 en priorité
```

## 🎯 Livrables Attendus

### MVP (2-3 semaines)
- [ ] **engine.py** : Core fonctionnel
- [ ] **rtx_engine.py** : Whisper RTX 3090 optimisé
- [ ] **talon_plugin/** : Intégration Win+Shift+V
- [ ] **install.py** : Installation automatique
- [ ] **Tests** : Performance + qualité validés

### V1.0 Complete (4-6 semaines)
- [ ] **system_tray.py** : Interface utilisateur
- [ ] **config_manager.py** : Gestion configuration
- [ ] **error_recovery.py** : Robustesse
- [ ] **installer.exe** : Package Windows
- [ ] **Documentation** : Guide utilisateur complet

## 🚨 Points d'Attention Critiques

1. **RTX 3090 First** : Toute l'architecture doit exploiter ce GPU
2. **Latence <500ms** : Non négociable pour l'expérience utilisateur
3. **Zero Config** : L'utilisateur final ne doit rien configurer
4. **Talon Dependency** : Talon DOIT être installé et fonctionnel
5. **French Priority** : Français en priorité, puis anglais

## 🔄 Communication de Suivi

### Questions à Poser
1. **Architecture** : "L'engine principal suit-il le pattern suggéré ?"
2. **Performance** : "Les benchmarks RTX 3090 sont-ils atteints ?"
3. **Intégration** : "Talon répond-il correctement aux hotkeys ?"
4. **Tests** : "Les tests critiques passent-ils tous ?"

### Métriques à Rapporter
- **Latence mesurée** (hotkey → texte)
- **WER transcription** français/anglais
- **VRAM utilisée** par le modèle
- **Taux de succès** intégration Talon

---

## 🎬 Démarrage Immédiat

**Commande pour reprendre le développement :**

```bash
cd C:\Dev\SuperWhisper2

# 1. Vérifier l'environnement
python check_environment.py

# 2. Commencer par le core engine
code src/core/engine.py

# 3. Première implémentation
python test_core_engine.py
```

**Bonne continuation sur SuperWhisper2 ! 🚀** 