#!/usr/bin/env python3
"""
Script de diagnostic et correction CUDA pour SuperWhisper2
Corrige le problème cublas64_12.dll et optimise l'installation CUDA
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_cuda_version():
    """Vérifier version CUDA installée"""
    print("🔍 Diagnostic CUDA...")
    
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ NVCC trouvé: {result.stdout.strip()}")
            return True
        else:
            print("❌ NVCC non trouvé")
            return False
    except FileNotFoundError:
        print("❌ CUDA Toolkit non installé")
        return False

def check_pytorch_cuda():
    """Vérifier PyTorch CUDA"""
    print("\n🔍 Diagnostic PyTorch CUDA...")
    
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ CUDA disponible: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"🎮 GPU détecté: {torch.cuda.get_device_name(0)}")
            print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
            return True
        else:
            print("❌ CUDA non disponible dans PyTorch")
            return False
            
    except ImportError:
        print("❌ PyTorch non installé")
        return False

def check_faster_whisper():
    """Vérifier faster-whisper"""
    print("\n🔍 Diagnostic faster-whisper...")
    
    try:
        from faster_whisper import WhisperModel
        print("✅ faster-whisper importé avec succès")
        
        # Test création modèle
        try:
            model = WhisperModel("tiny", device="cuda")
            print("✅ Modèle CUDA créé avec succès")
            return True
        except Exception as e:
            print(f"❌ Erreur création modèle CUDA: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ faster-whisper import error: {e}")
        return False

def check_cublas_libraries():
    """Vérifier librairies cuBLAS"""
    print("\n🔍 Diagnostic librairies cuBLAS...")
    
    # Chemins typiques Windows
    cuda_paths = [
        "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA",
        "C:/Program Files/NVIDIA Corporation/NVSMI",
        os.environ.get('CUDA_PATH', ''),
        os.environ.get('CUDA_HOME', '')
    ]
    
    cublas_found = False
    
    for cuda_path in cuda_paths:
        if not cuda_path or not os.path.exists(cuda_path):
            continue
            
        print(f"🔍 Recherche dans: {cuda_path}")
        
        # Recherche récursive des DLLs cuBLAS
        for root, dirs, files in os.walk(cuda_path):
            for file in files:
                if 'cublas' in file.lower() and file.endswith('.dll'):
                    print(f"   ✅ Trouvé: {os.path.join(root, file)}")
                    cublas_found = True
    
    if not cublas_found:
        print("❌ Aucune librairie cuBLAS trouvée")
    
    return cublas_found

def fix_cuda_installation():
    """Proposer corrections CUDA"""
    print("\n🛠️ PROPOSITIONS DE CORRECTION")
    print("=" * 50)
    
    print("\n1. 📥 MISE À JOUR CUDA TOOLKIT")
    print("   Télécharger CUDA 12.x depuis:")
    print("   https://developer.nvidia.com/cuda-downloads")
    print("   Sélectionner: Windows > x86_64 > Version > Installer")
    
    print("\n2. 🔄 RÉINSTALLATION PYTORCH")
    print("   Commandes à exécuter:")
    print("   poetry run pip uninstall torch torchvision torchaudio")
    print("   poetry run pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    
    print("\n3. 🔧 VARIABLES D'ENVIRONNEMENT")
    print("   Ajouter au PATH:")
    print("   C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.x/bin")
    print("   C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.x/libnvvp")
    
    print("\n4. 🚀 FALLBACK CPU")
    print("   Si problème persiste, utiliser CPU temporairement:")
    print("   Modifier whisper_engine_v5.py: device='cpu'")

def create_diagnostic_report():
    """Créer rapport de diagnostic"""
    print("\n📋 Création rapport diagnostic...")
    
    report = {
        "timestamp": "",
        "cuda_available": False,
        "pytorch_cuda": False,
        "faster_whisper": False,
        "cublas_libraries": False,
        "recommendations": []
    }
    
    # Exécuter diagnostics
    report["cuda_available"] = check_cuda_version()
    report["pytorch_cuda"] = check_pytorch_cuda()
    report["faster_whisper"] = check_faster_whisper()
    report["cublas_libraries"] = check_cublas_libraries()
    
    # Recommandations
    if not report["cuda_available"]:
        report["recommendations"].append("Installer CUDA Toolkit 12.x")
    
    if not report["pytorch_cuda"]:
        report["recommendations"].append("Réinstaller PyTorch avec support CUDA 12.1")
    
    if not report["cublas_libraries"]:
        report["recommendations"].append("Vérifier installation cuBLAS")
    
    # Sauvegarder rapport
    with open("cuda_diagnostic_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("✅ Rapport sauvegardé: cuda_diagnostic_report.json")

def main():
    """Diagnostic principal"""
    print("🚀 DIAGNOSTIC CUDA SUPERWHISPER2")
    print("=" * 40)
    
    # Exécuter diagnostics
    create_diagnostic_report()
    
    # Proposer corrections
    fix_cuda_installation()
    
    print("\n🎯 PROCHAINES ÉTAPES:")
    print("1. Appliquer corrections CUDA")
    print("2. Redémarrer système")
    print("3. Tester: poetry run python verify_rtx3090.py")
    print("4. Tester: poetry run python interface_test_superwhisper.py")

if __name__ == "__main__":
    main() 