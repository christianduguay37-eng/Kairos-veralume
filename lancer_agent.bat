@echo off
title VERALUME MISSION CONTROL (Qwen 2.5 14B)
color 0A

echo ===============================================================================
echo            VERALUME x KAIROS V6 -- MISSION CONTROL AGENT
echo                Assistant Autonome Local (Qwen 2.5 14B)
echo ===============================================================================
echo.

:: 1. Verifier si Ollama tourne
echo [*] Verification du moteur Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Ollama est actif en arriere-plan.
) else (
    echo [!] Demarrage d'Ollama...
    start "" ollama serve
    timeout /t 3 /nobreak >nul
)

:: 2. Ouvrir le navigateur
echo [*] Ouverture de l'interface Mission Control...
start http://localhost:7860

:: 3. Demarrer le serveur Veralume
echo [*] Demarrage du Kernel VERALUME sur le port 7860...
echo.
python server.py

pause
