@echo off
setlocal

set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

echo ============================================
echo Prompt-Launcher Setup und Start
echo ============================================

if not exist "venv" (
    echo [INFO] Virtuelle Umgebung wird erstellt...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Konnte virtuelle Umgebung nicht erstellen.
        pause
        exit /b 1
    )
) else (
    echo [INFO] Virtuelle Umgebung bereits vorhanden.
)

call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Konnte venv nicht aktivieren.
    pause
    exit /b 1
)

echo [INFO] Installiere Python-Abhängigkeiten...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Installation der Abhängigkeiten fehlgeschlagen.
    pause
    exit /b 1
)

echo [INFO] Starte Prompt-Launcher...
python main.py

endlocal

