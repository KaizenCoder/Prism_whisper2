# Prism_whisper2 - Contraintes Projet 🚨

**Date** : Mise à jour continue  
**Statut** : Règles critiques du projet

---

## 🔒 Contraintes Techniques Absolues

### 1. SuperWhisper Existant - Zone Protégée

**📍 Localisation** : `C:\Dev\SuperWhisper\`

**🚫 INTERDICTIONS STRICTES :**
- ❌ **Modification directe** des fichiers existants
- ❌ **Suppression** de fichiers du projet original
- ❌ **Déplacement** des scripts fonctionnels
- ❌ **Renommage** des modules existants

**✅ AUTORISÉ :**
- ✅ **Lecture** et analyse du code
- ✅ **Copie** pour référence (vers autre répertoire)
- ✅ **Appel subprocess** des scripts existants
- ✅ **Consultation** de la documentation

**📋 Procédure Obligatoire :**
1. **Demander autorisation** utilisateur avant toute modification
2. **Expliquer la raison** de la modification proposée
3. **Attendre validation** explicite
4. **Documenter** toute interaction avec le projet existant

---

## ⚡ Contraintes Performance

### 1. Pas de Fallback CPU

**🚫 REJETÉ :** Fallback CPU pour transcription Whisper

**Raisons :**
- **Performance inacceptable** : CPU 10-50x plus lent que GPU
- **Latence prohibitive** : >5-10 secondes vs <300ms cible
- **Experience utilisateur** : Complètement cassée en mode CPU
- **Cas d'usage** : Temps réel incompatible avec CPU

**✅ ALTERNATIVE :**
- **GPU health monitoring** : Détection proactive des problèmes
- **Restart rapide** : Relance automatique si GPU fail
- **Error graceful** : Message clair si GPU indisponible
- **Diagnostic intégré** : Outils pour détecter problèmes GPU

### 2. GPU RTX 3090 Obligatoire

**Hardware requis :**
- **RTX 3090** sur PCIe Gen5 x16 (GPU 1)
- **24GB VRAM** minimum pour modèles large
- **CUDA 11.8+** compatible

**Pas de support :**
- ❌ GPUs non-NVIDIA
- ❌ GPUs <8GB VRAM
- ❌ Compute Capability <7.0
- ❌ Mode CPU Whisper

---

## 🏗️ Contraintes Architecture

### 1. Approche Évolution vs Révolution

**✅ PRINCIPE :**
- **80% réutilisation** code existant SuperWhisper
- **20% nouveau code** pour intégration Talon + UI
- **Bridge subprocess** vers scripts existants
- **Pas de fusion** des codebases

**🎯 Architecture Imposée :**
```
Prism_whisper2 → Bridge → SuperWhisper existant
     (nouveau)    (nouveau)    (protégé)
```

### 2. Communication Subprocess

**Méthode obligatoire :**
- **Subprocess calls** vers scripts SuperWhisper
- **JSON/text output** parsing pour récupérer résultats
- **Process isolation** pour stabilité
- **Pas d'import direct** des modules SuperWhisper

---

## 📁 Structure Fichiers

### Répertoires Protégés
```
C:\Dev\SuperWhisper\           ← 🔒 ZONE PROTÉGÉE
├── transcription_simple.py   ← 🚫 Ne pas modifier
├── dictee_superwhisper.py    ← 🚫 Ne pas modifier  
├── venv_superwhisper/        ← 🚫 Ne pas modifier
└── secrets/                  ← 🔒 Accès lecture seule
```

### Répertoires de Travail
```
C:\Dev\Superwhisper2\         ← ✅ Zone de développement
├── src/                      ← ✅ Nouveau code ici
├── secrets/                  ← ✅ Nos secrets
└── docs/                     ← ✅ Notre documentation
```

---

## 🔄 Workflow de Validation

### Avant Modification SuperWhisper

1. **Question utilisateur :**
   ```
   "Je dois modifier [FICHIER] dans C:\Dev\SuperWhisper\ 
   pour [RAISON]. Autorisation ?"
   ```

2. **Attendre réponse explicite**

3. **Si autorisé :**
   - Faire backup avant modification
   - Documenter changement
   - Tester après modification

4. **Si refusé :**
   - Chercher alternative sans modification
   - Utiliser approche subprocess/bridge

### En Cas de Blocage

**Si impossible sans modifier SuperWhisper :**
1. **Expliquer le blocage** technique
2. **Proposer alternatives** (subprocess, copie, etc.)
3. **Demander guidance** utilisateur
4. **Ne jamais modifier** sans autorisation

---

## 🎯 Objectifs Contraints

### Performance Targets (avec contraintes)

| Métrique | Cible | Contrainte |
|----------|-------|------------|
| **Latence** | <300ms | GPU uniquement |
| **Qualité** | >95% FR | Modèles existants |
| **Stabilité** | 99.9% | Sans modifier base |
| **Integration** | Seamless | Via subprocess |

### Limitations Acceptées

- **Pas de fallback CPU** → User doit avoir GPU fonctionnel
- **Pas de modification directe** → Subprocess overhead acceptable
- **Architecture bridge** → Complexité supplémentaire OK
- **Process isolation** → Memory overhead acceptable

---

## 📝 Checklist Conformité

Avant tout développement, vérifier :

- [ ] **Aucune modification** planifiée dans `C:\Dev\SuperWhisper\`
- [ ] **Architecture subprocess** respectée
- [ ] **GPU RTX 3090** requis documenté
- [ ] **Pas de fallback CPU** dans le design
- [ ] **Validation utilisateur** obtenue si nécessaire

---

**🚨 Ces contraintes sont NON-NÉGOCIABLES**

**Toute violation nécessite autorisation explicite utilisateur** 