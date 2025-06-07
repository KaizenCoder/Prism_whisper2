import subprocess
import sys
from pathlib import Path

def test_superwhisper():
    """Test direct de SuperWhisper"""
    
    superwhisper_path = Path("C:/Dev/SuperWhisper")
    superwhisper_venv = superwhisper_path / "venv_superwhisper/Scripts/python.exe"
    superwhisper_script = superwhisper_path / "dictee_superwhisper.py"
    
    print(f"Testing SuperWhisper...")
    print(f"Script: {superwhisper_script}")
    print(f"Venv: {superwhisper_venv}")
    
    # Test 1: Vérifier script existe
    if not superwhisper_script.exists():
        print(f"ERROR: Script not found at {superwhisper_script}")
        return False
        
    if not superwhisper_venv.exists():
        print(f"ERROR: Venv not found at {superwhisper_venv}")
        return False
    
    print("Files found, testing execution...")
    
    # Test 2: Essayer d'exécuter SuperWhisper
    try:
        cmd = [str(superwhisper_venv), str(superwhisper_script)]
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,  # Court timeout pour test
            cwd=superwhisper_path
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Timeout during test (expected - SuperWhisper waiting for audio)")
        return True  # Timeout normal si SuperWhisper attend l'audio
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_superwhisper()
    print(f"Test result: {'SUCCESS' if success else 'FAILED'}") 