@echo off
setlocal

set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Konnte venv nicht aktivieren. Bitte zuerst setup_and_run.bat ausführen.
    pause
    exit /b 1
)

python main.py

endlocal
