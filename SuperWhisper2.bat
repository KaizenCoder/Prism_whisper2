@echo off
REM SuperWhisper2 - Lanceur Windows Batch
REM Phase 2.1: Interface System Tray

echo 🚀 SuperWhisper2 - Demarrage...
echo ==============================================
echo Phase 2.1: Interface System Tray Professionnelle
echo ==============================================

REM Changer vers le répertoire du projet
cd /d "%~dp0"

REM Lancer avec l'environnement virtuel
"C:\Dev\SuperWhisper\venv_superwhisper\Scripts\python.exe" start_superwhisper.py

REM Pause en cas d'erreur
if errorlevel 1 (
    echo.
    echo ❌ Erreur lors du lancement
    pause
) 