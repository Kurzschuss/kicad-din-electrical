@echo off
rem Wird mit CALL aufgerufen; Variablen bleiben im aufrufenden Skript erhalten.

set "KICAD_CLI="
set "KICAD_BIN="
set "KICAD_USER_DIR="

rem 1. kicad-cli.exe ueber PATH suchen.
for /f "delims=" %%I in ('where kicad-cli.exe 2^>nul') do if not defined KICAD_CLI set "KICAD_CLI=%%~fI"

rem 2. Uebliche Installationsordner pruefen und die hoechste Version waehlen.
if not defined KICAD_CLI (
    for /f "delims=" %%I in ('dir /b /ad /o-n "%ProgramFiles%\KiCad" 2^>nul') do (
        if not defined KICAD_CLI if exist "%ProgramFiles%\KiCad\%%I\bin\kicad-cli.exe" set "KICAD_CLI=%ProgramFiles%\KiCad\%%I\bin\kicad-cli.exe"
    )
)
if not defined KICAD_CLI if defined ProgramFiles(x86) (
    for /f "delims=" %%I in ('dir /b /ad /o-n "%ProgramFiles(x86)%\KiCad" 2^>nul') do (
        if not defined KICAD_CLI if exist "%ProgramFiles(x86)%\KiCad\%%I\bin\kicad-cli.exe" set "KICAD_CLI=%ProgramFiles(x86)%\KiCad\%%I\bin\kicad-cli.exe"
    )
)

if defined KICAD_CLI (
    for %%I in ("%KICAD_CLI%") do set "KICAD_BIN=%%~dpI"
    set "PATH=%KICAD_BIN%;%PATH%"
)

rem Den tatsaechlich konfigurierten Windows-Dokumenteordner ermitteln.
for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -Command "[Environment]::GetFolderPath('MyDocuments')" 2^>nul`) do if not defined KICAD_DOCUMENTS_DIR set "KICAD_DOCUMENTS_DIR=%%I"
if not defined KICAD_DOCUMENTS_DIR set "KICAD_DOCUMENTS_DIR=%USERPROFILE%\Documents"
set "KICAD_USER_DIR=%KICAD_DOCUMENTS_DIR%\kicad"

rem Fehlende Standardordner anlegen; vorhandene Inhalte niemals veraendern.
for %%D in (3dmodels 3rdparty footprints plugins projects scripting symbols template) do (
    if not exist "%KICAD_USER_DIR%\%%D" mkdir "%KICAD_USER_DIR%\%%D" >nul 2>nul
)

exit /b 0
