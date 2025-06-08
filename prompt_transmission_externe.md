# 🎯 PROMPT DE TRANSMISSION - DIAGNOSTIC ENGINE V5 SUPERWHISPER2

## 📋 CONTEXTE & DEMANDE

**Projet** : SuperWhisper2 - Engine de transcription vocale temps réel  
**Version** : Engine V5 avec optimisations Phase 3  
**Hardware** : RTX 3090 24GB + Rode NT-USB + Windows 10  
**Problème** : Callbacks audio non fonctionnels malgré architecture technique correcte  

**DEMANDE** : Analyse critique du diagnostic + proposition solution alternative

---

## 🚨 PROBLÈME CRITIQUE IDENTIFIÉ

### **Symptômes observés :**
- **Engine V5** : 1 seul callback en 81s au lieu de 19 attendus
- **Erreurs répétées** : `TypeError: patched_callback() takes 1 positional argument but 3 were given`
- **Hallucinations audio** : "Sous-titres réalisés para la communauté d'Amara.org" (capture audio système)
- **Performance dégradée** : 15-16s par traitement vs 5.5s en bypass

### **Architecture technique validée :**
```
✅ Engine V5 Phase 3 : 5/7 optimisations actives
✅ RTX 3090 : INT8 + faster-whisper + 4 CUDA streams + VRAM cache 24GB
✅ Rode NT-USB : Signal audio parfait (RMS 0.015-0.032)
✅ Modèle MEDIUM INT8 : Chargé correctement en 0.1s
❌ Device routing : AudioStreamer utilise device par défaut au lieu du Rode
❌ Callbacks : Signature incompatible avec Engine V5
```

---

## 📊 DONNÉES DE PERFORMANCE OBSERVÉES

### **Test réel du 2025-06-08 19:53:42 :**
- **Durée totale** : 81.4s
- **Segments** : 19 (18 bypass + 1 engine_v5)
- **WER** : 34.9% (majoritairement bypass faster-whisper)
- **Latence bypass** : ~5.5s par segment
- **GPU** : RTX 3090 configurée CUDA + INT8

### **Baseline technique :**
- **faster-whisper bypass** : CUDA + INT8, 5.5s par segment, 36% WER
- **Engine V5 cassé** : 1 callback/81s, erreurs signature, hallucinations

---

## 🔧 DIAGNOSTIC TECHNIQUE EFFECTUÉ

### **1. Tests exhaustifs créés :**
- `test_engine_v5_ultimate.py` - Interface GitHub-style
- `diagnostic_engine_v5_architecture.py` - Analyse composants
- `fix_engine_v5_callbacks_v2.py` - Correction callbacks signature flexible
- `test_audio_simple.py` - Validation Rode NT-USB
- `test_engine_v5_rode_solution.py` - Patch AudioStreamer complet

### **2. Root causes identifiées :**

**A. Device Audio Routing :**
```python
# PROBLÈME src/audio/audio_streamer.py ligne 176
self.stream = sd.InputStream(
    samplerate=self.sample_rate,
    channels=self.channels,
    dtype=np.float32,
    # ❌ AUCUN PARAMÈTRE device= !
    # Utilise device par défaut (audio système) au lieu du Rode
)
```

**B. Callbacks Signature :**
```python
# ERREUR RÉPÉTÉE
TypeError: patched_callback() takes 1 positional argument but 3 were given
# Engine V5 envoie (text, timestamp, metadata)
# Callback attendait seulement (text)
```

### **3. Solutions développées :**

**Solution A - Patch AudioStreamer :**
```python
def patched_capture_loop():
    audio_streamer.stream = sd.InputStream(
        device=rode_device_id,  # LIGNE MAGIQUE
        samplerate=audio_streamer.sample_rate,
        channels=audio_streamer.channels,
        # ... reste identique
    )
```

**Solution B - Callbacks flexibles :**
```python
def flexible_callback(*args, **kwargs):
    # Gestion robuste multiples signatures
    if len(args) >= 1:
        text = args[0]
        print(f"📝 Transcription: {text}")
```

---

## 🎯 OBJECTIFS & CONTRAINTES

### **Objectifs performance :**
- **Latence** : <1.5s par segment (actuellement 5.5s bypass, 15s+ engine cassé)
- **Précision** : <25% WER (actuellement ~35% bypass)
- **Temps réel** : Callbacks streaming continus

### **Contraintes techniques :**
- **Hardware fixe** : RTX 3090 24GB + Rode NT-USB + Windows 10
- **Architecture existante** : SuperWhisper2 Engine V5 Phase 3
- **Optimisations à préserver** : INT8 + faster-whisper + CUDA streams + VRAM cache

### **Contraintes opérationnelles :**
- **Pas de refactoring massif** : Corrections ciblées préférées
- **Tests validables** : Solution testable immédiatement
- **Documentation** : Compréhension technique claire

---

## ❓ QUESTIONS SPÉCIFIQUES POUR ANALYSE

### **1. Diagnostic technique :**
- Le diagnostic des root causes est-il correct et complet ?
- Y a-t-il des aspects techniques manqués ou mal analysés ?
- Les solutions proposées sont-elles appropriées architecturalement ?

### **2. Approche alternative :**
- Existe-t-il une approche radicalement différente plus robuste ?
- Faut-il contourner l'Engine V5 complètement ?
- Y a-t-il des optimisations Phase 3 exploitables différemment ?

### **3. Architecture système :**
- L'architecture AudioStreamer → StreamingManager → Engine V5 est-elle viable ?
- Faut-il repenser la chaîne de callbacks ?
- Le device routing peut-il être géré autrement ?

### **4. Performance objective :**
- L'objectif <1.5s est-il réaliste avec cette architecture ?
- Quelles sont les optimisations prioritaires pour y arriver ?
- Les estimations de performance post-correction sont-elles crédibles ?

---

## 📁 FICHIERS FOURNIS

### **Scripts diagnostic :**
- `test_engine_v5_ultimate.py` - Script de test principal avec interface
- `diagnostic_engine_v5_architecture.py` - Analyse architecture complète
- `test_audio_simple.py` - Test basique Rode NT-USB
- `test_engine_v5_rode_solution.py` - Solution patch complète

### **Scripts correction :**
- `fix_engine_v5_callbacks_v2.py` - Correction callbacks signature
- `test_engine_v5_rode_force.py` - Test forçage device Rode

### **Données de test :**
- `tests/test_engine_v5_ultimate_20250608_195342.json` - Résultats détaillés
- `tests/test_engine_v5_ultimate_20250608_195342.txt` - Logs formatés

### **Documentation :**
- `journal_developpement_engine_v5.md` - Journal complet diagnostic
- `prompt_succession_engine_v5.md` - Guide reprise développement

### **Code source (extraits) :**
- `src/core/whisper_engine_v5.py` - Engine principal
- `src/audio/audio_streamer.py` - Gestionnaire audio problématique
- `src/core/streaming_manager.py` - Manager streaming

---

## 🚀 ATTENDU EN RETOUR

### **1. Analyse critique :**
- Validation ou correction du diagnostic effectué
- Identification d'éventuels points manqués
- Évaluation de la viabilité des solutions proposées

### **2. Solution alternative :**
- Architecture alternative si pertinente
- Approche de contournement si l'Engine V5 est trop complexe
- Optimisations prioritaires pour atteindre <1.5s

### **3. Roadmap technique :**
- Étapes précises de mise en œuvre
- Estimation temps de développement
- Points de validation intermédiaires

### **4. Évaluation faisabilité :**
- Probabilité de succès des corrections proposées
- Alternative de fallback si échec
- Recommandations stratégiques

---

## ⚡ URGENCE & PRIORITÉS

**CRITIQUE** : Les callbacks audio sont le goulot d'étranglement absolu du projet  
**OBJECTIF** : Solution opérationnelle sous 48h maximum  
**BACKUP** : Alternative de contournement si Engine V5 non récupérable  

**Merci d'analyser cette situation complexe et de proposer la meilleure voie forward ! 🎯** 