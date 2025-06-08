# 🎯 PLAN D'IMPLÉMENTATION ENGINE V5 - CORRECTIFS DÉVELOPPEUR C

## OBJECTIF PRINCIPAL
Corriger les 2 causes racines identifiées dans SuperWhisper2 Engine V5 :
- **Device routing** : Forcer capture Rode NT-USB au lieu du périphérique par défaut
- **Callback signature** : Éliminer TypeError avec décorateur flexible

## MÉTRIQUES DE SUCCÈS GLOBALES
- ✅ **WER < 25%** (vs 94.1% actuel en mode tiny bypass)
- ✅ **Latence < 1.5s** (vs 3s+ actuel)
- ✅ **Callbacks Engine V5 > 10** (vs 1 actuel puis arrêt)
- ✅ **Stabilité streaming continu 60s+** (vs interruption après 1 callback)

---

## 📋 ÉTAPES D'IMPLÉMENTATION

### **E1 - PATCH AUDIO STREAMER (PRIORITÉ CRITIQUE)**
| Élément | Détail | Status | Temps |
|---------|--------|--------|-------|
| **Objectif** | Forcer device=rode_id dans sd.InputStream | ⏳ À faire | 1h |
| **Fichier cible** | `src/audio/audio_streamer.py` | ⏳ | |
| **Modifications** | • Device lookup par nom<br>• Paramètre device= explicite<br>• Fallback gracieux | ⏳ | |
| **Test validation** | `test_audio_simple.py` → RMS > 0.01 | ⏳ | |
| **Critère GO** | ✅ Rode détecté + capture audio confirmée | ⏳ | |
| **Critère NO-GO** | ❌ Rode non détecté ou RMS < 0.001 | ⏳ | |

### **E2 - CALLBACK GUARD FLEXIBLE (PRIORITÉ MAJEURE)**
| Élément | Détail | Status | Temps |
|---------|--------|--------|-------|
| **Objectif** | Décorateur adaptant signatures callback | ⏳ À faire | 2h |
| **Fichier cible** | `src/utils/callback_guard.py` (nouveau) | ⏳ | |
| **Fonctionnalité** | • @signature_guard decorator<br>• Adaptation (text, ts, meta) → (text)<br>• Gestion TypeError gracieuse | ⏳ | |
| **Test validation** | `test_engine_v5_callbacks_v2.py` | ⏳ | |
| **Critère GO** | ✅ Aucun TypeError + callbacks reçus | ⏳ | |
| **Critère NO-GO** | ❌ TypeError persistant ou callbacks bloqués | ⏳ | |

### **E3 - STREAMING PIPELINE DEBUG (PRIORITÉ CRITIQUE)**
| Élément | Détail | Status | Temps |
|---------|--------|--------|-------|
| **Objectif** | Résoudre interruption streaming Engine V5 après 1 callback | 🚀 En cours | 2h |
| **Problème** | • Engine V5 streaming s'arrête après 1 transcription<br>• AudioStreamer continue mais Engine V5 ne process plus<br>• Pipeline audio cassé quelque part | 🚀 | |
| **Investigation** | • Debug AudioStreamer → StreamingManager flow<br>• Vérifier callback chain continuité<br>• Analyser filtrage hallucination impact | 🚀 | |
| **Critère GO** | ✅ Engine V5 callbacks > 10 sur 60s streaming | ⏳ | |
| **Critère NO-GO** | ❌ Streaming s'arrête toujours après 1-2 callbacks | ⏳ | |

### **E4 - DOCUMENTATION & CI (PRIORITÉ NORMALE)**
| Élément | Détail | Status | Temps |
|---------|--------|--------|-------|
| **Objectif** | Documentation des correctifs | ⏳ À faire | 1h |
| **Livrables** | • `journal_developpement_engine_v5.md` v5.1<br>• Tests unitaires mis à jour | ⏳ | |
| **Critère GO** | ✅ Documentation complète + tests passent | ⏳ | |

### **E5 - VALIDATION COMPLÈTE (PRIORITÉ VALIDATION)**
| Élément | Détail | Status | Temps |
|---------|--------|--------|-------|
| **Objectif** | Test complet avec `test_engine_v5_ultimate.py` | ⏳ À faire | 1h |
| **Métriques finales** | • WER, similarité, latence, callbacks<br>• Export JSON + TXT | ⏳ | |
| **Critère GO** | ✅ Toutes métriques de succès atteintes | ⏳ | |
| **Critère NO-GO** | ❌ Une métrique critique échoue | ⏳ | |

---

## 🚨 PLAN DE FALLBACK

### **FALLBACK NIVEAU 1** - Si E1 ou E2 échouent
**Déclencheur** : Rode non détecté OU TypeError persistant  
**Action** : 
- Revenir à l'Engine V5 original
- Activer bypass mode avec modèle "small" français optimisé
- **Objectif dégradé** : WER < 40%, latence < 3s

### **FALLBACK NIVEAU 2** - Si streaming V5 instable
**Déclencheur** : Callbacks < 5 ou interruptions fréquentes  
**Action** :
- Migration vers faster-whisper streaming natif
- Conservation optimisations GPU partielles
- **Objectif dégradé** : WER < 30%, latence < 2s

### **FALLBACK NIVEAU 3** - Si échec total technique
**Déclencheur** : Aucune solution fonctionnelle  
**Action** :
- Retour Engine V4 stable
- Pipeline FFmpeg → PyAudio
- **Objectif minimal** : WER < 50%, latence < 4s

---

## 📊 TABLEAU DE BORD TEMPS RÉEL

### **PROGRESS TRACKER**
- [x] **E1** - Audio Streamer Patch ✅ TERMINÉ
- [x] **E2** - Callback Guard ✅ TERMINÉ
- [ ] **E3** - Streaming Pipeline Debug 🔥 PRIORITÉ CRITIQUE  
- [ ] **E4** - Documentation ⏳
- [ ] **E5** - Final Validation ⏳

### **TEMPS ESTIMÉ vs RÉEL**
| Phase | Estimé | Réel | Delta | Status |
|-------|--------|------|-------|--------|
| E1 | 1h | - | - | ⏳ |
| E2 | 2h | - | - | ⏳ |
| E3 | 3h | - | - | ⏳ |
| E4 | 1h | - | - | ⏳ |
| E5 | 1h | - | - | ⏳ |
| **TOTAL** | **8h** | **-** | **-** | ⏳ |

### **RISK INDICATORS**
- 🟢 **LOW RISK** : E1, E2 (correctifs ciblés)
- 🟡 **MEDIUM RISK** : E3 (performance tuning)  
- 🔴 **HIGH RISK** : Aucun identifié

---

## 🔬 TESTS DE VALIDATION OBLIGATOIRES

### **Tests Unitaires**
1. `test_audio_simple.py` - Capture Rode
2. `test_engine_v5_callbacks_v2.py` - Signature callbacks
3. `test_latency_benchmark.py` - Performance blocksize

### **Tests d'Intégration** 
1. `test_engine_v5_ultimate.py` - Test complet
2. `diagnostic_engine_v5.py` - Monitoring streaming

### **Tests de Régression**
1. Vérification optimisations RTX 3090 préservées
2. VRAM usage < 20GB sur RTX 3090
3. CUDA streams actifs = 4

---

## ✅ CRITÈRES D'ACCEPTATION FINALE

### **MUST HAVE (Go/No-Go)**
- ✅ Engine V5 streaming continu 60s+ sans interruption
- ✅ Callbacks reçus > 10 avec texte cohérent
- ✅ WER < 25% sur texte de référence
- ✅ Latence moyenne < 1.5s

### **SHOULD HAVE (Qualité)**
- ✅ Similarité > 80% vs texte référence
- ✅ Termes techniques correctement transcrits
- ✅ Pas d'hallucinations détectées

### **COULD HAVE (Bonus)**
- ✅ Latence < 1s (objectif stretch)
- ✅ WER < 20% (qualité exceptionnelle)
- ✅ Configuration YAML intégrée

---

**RESPONSABLE IMPLÉMENTATION** : Assistant IA  
**DATE DÉBUT** : 2025-01-XX  
**DEADLINE** : Dans les 48h (avec marge sécurité)  
**NEXT CHECKPOINT** : Fin E1 (Audio Streamer Patch) 