@echo off
setlocal EnableExtensions
cd /d "%~dp0\..\.."
title Z_Cockpit erzeugen und oeffnen

set "PYTHON_CMD=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_CMD=.venv\Scripts\python.exe"

rem Repositoryzustand fuer den Fehlerbericht erfassen. Ein gesperrter Zustand
rem blockiert nur die GitHub-Vorbereitung, nicht das lokale Z_Cockpit.
%PYTHON_CMD% -m tools.check_repository_version >nul 2>&1

%PYTHON_CMD% -m tools.generate_z_cockpit
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
