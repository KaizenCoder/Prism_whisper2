#!/usr/bin/env python3
"""
🎯 CREATION PACKAGE TRANSMISSION EXTERNE
Script pour créer l'archive complète pour évaluation externe
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def create_transmission_package():
    """Crée l'archive complète pour transmission externe"""
    
    # Timestamp pour nom unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"superwhisper2_engine_v5_diagnostic_{timestamp}"
    
    # Créer dossier temporaire
    temp_dir = Path(package_name)
    temp_dir.mkdir(exist_ok=True)
    
    print(f"📦 Création package: {package_name}")
    
    # Structure du package
    structure = {
        "documentation": [
            "prompt_transmission_externe.md",
            "journal_developpement_engine_v5.md", 
            "prompt_succession_engine_v5.md"
        ],
        "scripts_diagnostic": [
            "test_engine_v5_ultimate.py",
            "diagnostic_engine_v5_architecture.py",
            "test_audio_simple.py",
            "test_engine_v5_rode_solution.py",
            "test_rode_simple.py"
        ],
        "scripts_correction": [
            "fix_engine_v5_callbacks_v2.py",
            "test_engine_v5_rode_force.py"
        ],
        "data_tests": [
            "tests/test_engine_v5_ultimate_20250608_195342.json",
            "tests/test_engine_v5_ultimate_20250608_195342.txt",
            "tests/test_engine_v5_ultimate_20250608_193620.json",
            "tests/test_engine_v5_ultimate_20250608_193620.txt"
        ],
        "source_code": [
            "src/core/whisper_engine_v5.py",
            "src/audio/audio_streamer.py", 
            "src/core/streaming_manager.py"
        ]
    }
    
    # Copier les fichiers
    for category, files in structure.items():
        category_dir = temp_dir / category
        category_dir.mkdir(exist_ok=True)
        
        print(f"📁 Catégorie: {category}")
        
        for file_path in files:
            source = Path(file_path)
            if source.exists():
                dest = category_dir / source.name
                shutil.copy2(source, dest)
                print(f"  ✅ {source.name}")
            else:
                print(f"  ❌ MANQUANT: {file_path}")
    
    # Créer README du package
    create_package_readme(temp_dir)
    
    # Créer l'archive ZIP
    zip_name = f"{package_name}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arc_name)
    
    # Nettoyer dossier temporaire
    shutil.rmtree(temp_dir)
    
    # Statistiques
    zip_size = os.path.getsize(zip_name) / 1024 / 1024  # MB
    print(f"\n🎯 PACKAGE CRÉÉ: {zip_name}")
    print(f"📊 Taille: {zip_size:.1f} MB")
    print(f"📅 Timestamp: {timestamp}")
    
    return zip_name

def create_package_readme(temp_dir):
    """Crée le README du package"""
    
    readme_content = f"""# 📦 PACKAGE DIAGNOSTIC ENGINE V5 SUPERWHISPER2

## 🎯 CONTENU DU PACKAGE

**Créé le** : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Objectif** : Diagnostic complet + demande solution alternative

### 📁 STRUCTURE

**documentation/**
- `prompt_transmission_externe.md` - PROMPT PRINCIPAL pour IA externe
- `journal_developpement_engine_v5.md` - Journal complet diagnostic
- `prompt_succession_engine_v5.md` - Guide reprise développement

**scripts_diagnostic/**
- `test_engine_v5_ultimate.py` - Script test principal interface GitHub
- `diagnostic_engine_v5_architecture.py` - Analyse architecture complète  
- `test_audio_simple.py` - Test basique Rode NT-USB
- `test_engine_v5_rode_solution.py` - Solution patch complète
- `test_rode_simple.py` - Test diagnostic Rode simple

**scripts_correction/**
- `fix_engine_v5_callbacks_v2.py` - Correction callbacks signature flexible
- `test_engine_v5_rode_force.py` - Test forçage device Rode

**data_tests/**
- `test_engine_v5_ultimate_20250608_195342.*` - Résultats test détaillés
- `test_engine_v5_ultimate_20250608_193620.*` - Données supplémentaires

**source_code/**
- `whisper_engine_v5.py` - Engine principal Phase 3
- `audio_streamer.py` - Gestionnaire audio (problématique)
- `streaming_manager.py` - Manager streaming

## 🚨 PROBLÈME PRINCIPAL

**Callbacks audio Engine V5 non fonctionnels** :
- 1 seul callback en 81s au lieu de 19
- Erreur signature: `TypeError: patched_callback() takes 1 positional argument but 3 were given`
- Device routing incorrect: AudioStreamer utilise device par défaut au lieu du Rode

## 🎯 OBJECTIF RECHERCHÉ

**Solution pour atteindre** :
- ⚡ Latence <1.5s par segment
- 🎯 Précision <25% WER  
- 🔄 Callbacks streaming temps réel

## 📋 UTILISATION

1. **Lire en priorité** : `documentation/prompt_transmission_externe.md`
2. **Analyser données** : `data_tests/` pour métriques observées
3. **Examiner scripts** : `scripts_diagnostic/` pour compréhension technique
4. **Étudier source** : `source_code/` pour architecture

## ⚡ URGENCE

**CRITIQUE** - Callbacks audio = goulot d'étranglement absolu du projet
**DÉLAI** - Solution requise sous 48h maximum

---

**Merci d'analyser et proposer solution alternative ! 🚀**
"""
    
    readme_path = temp_dir / "README.md"
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"  ✅ README.md")

if __name__ == "__main__":
    print("🎯 CRÉATION PACKAGE TRANSMISSION EXTERNE")
    print("=" * 50)
    
    try:
        zip_file = create_transmission_package()
        print(f"\n✅ PACKAGE PRÊT: {zip_file}")
        print("\n📋 INSTRUCTIONS:")
        print("1. Envoyer le fichier ZIP à l'IA externe")
        print("2. Inclure le prompt principal comme contexte")
        print("3. Demander analyse critique + solution alternative")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc() 