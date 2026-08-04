@echo off
setlocal EnableExtensions
cd /d "%~dp0\..\.."
title Z_Cockpit erzeugen und oeffnen

set "PYTHON_CMD=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_CMD=.venv\Scripts\python.exe"

%PYTHON_CMD% tools\generate_z_cockpit.py
if errorlevel 1 (
    echo.
    echo FEHLER: Z_Cockpit konnte nicht erzeugt werden.
    echo Starte zuerst run_tests.bat, damit die Entwicklungsumgebung eingerichtet wird.
    echo.
    pause
    exit /b 1
)

if not exist "docs\site\z-cockpit.html" (
    echo.
    echo FEHLER: Die erzeugte HTML-Datei wurde nicht gefunden.
    echo.
    pause
    exit /b 1
)

start "Z_Cockpit" "docs\site\z-cockpit.html"
exit /b 0
