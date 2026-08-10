@echo off
setlocal EnableExtensions
cd /d "%~dp0\..\.."
title Z_Cockpit erzeugen und oeffnen

set "PYTHON_CMD=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_CMD=.venv\Scripts\python.exe"

rem Lokale URI-Protokolle fuer KiCad-Editoraufrufe und ProjectOS-Projektdateien
rem registrieren. Die Registrierung erfolgt nur im aktuellen Benutzerprofil (HKCU)
rem und benoetigt keine Administratorrechte. Bei Fehlern bleibt das Cockpit nutzbar.
powershell -NoProfile -ExecutionPolicy Bypass -File "tools\windows\register_z_kicad_protocol.ps1" -RepositoryRoot "%CD%" >nul 2>&1
if errorlevel 1 (
    echo HINWEIS: KiCad-Editorlinks konnten nicht registriert werden.
    echo Das Z_Cockpit wird trotzdem geoeffnet.
)
powershell -NoProfile -ExecutionPolicy Bypass -File "tools\windows\register_z_project_protocol.ps1" -RepositoryRoot "%CD%" >nul 2>&1
if errorlevel 1 (
    echo HINWEIS: ProjectOS-Projektaktionen konnten nicht registriert werden.
    echo Das Z_Cockpit wird trotzdem geoeffnet.
)

rem Repositoryzustand fuer den Fehlerbericht erfassen. Ein gesperrter Zustand
rem blockiert nur die GitHub-Vorbereitung, nicht das lokale Z_Cockpit.
%PYTHON_CMD% -m tools.check_repository_version >nul 2>&1

rem Technische 3D-Vorschauen aus dem aktuellen Footprint-/Modellstand erzeugen.
%PYTHON_CMD% -m tools.generate_3d_previews
if errorlevel 1 (
    echo.
    echo FEHLER: 3D-Vorschauen konnten nicht erzeugt werden.
    echo.
    pause
    exit /b 1
)

rem Ein zuvor im Cockpit erzeugtes und weiterhin gueltiges ProjectOS-v4-Bundle
rem automatisch wiederverwenden. Ein fehlender oder ungueltiger Aktivzustand
rem ergibt bewusst keine Ausgabe und startet das Cockpit ohne Projektbundle.
set "PROJECT_BUNDLE="
for /f "usebackq delims=" %%P in (`%PYTHON_CMD% -m tools.projectos_project_cli active --path-only 2^>nul`) do set "PROJECT_BUNDLE=%%P"

if defined PROJECT_BUNDLE (
    %PYTHON_CMD% -m tools.generate_z_cockpit --project-bundle "%PROJECT_BUNDLE%"
) else (
    %PYTHON_CMD% -m tools.generate_z_cockpit
)
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
