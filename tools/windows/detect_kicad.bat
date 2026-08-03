@echo off
rem Wird mit CALL aufgerufen; Variablen bleiben im aufrufenden Skript erhalten.

set "KICAD_CLI="
set "KICAD_BIN="
set "KICAD_USER_DIR="
set "KICAD_Z_REGISTRATION="
set "KICAD_Z_REGISTERED="
set "KICAD_Z_EXISTING="
set "KICAD_Z_MISSING_NAMES="
set "KICAD_Z_ADDED_NAMES="
set "KICAD_Z_EXISTING_NAMES="
set "KICAD_Z_MISMATCH_NAMES="
set "KICAD_Z_LIBRARY_REGISTRATION="
set "KICAD_Z_LIBRARY_ADDED="
set "KICAD_Z_LIBRARY_EXISTING="
set "KICAD_Z_LIBRARY_MISMATCH="
set "KICAD_Z_SYMBOL_LIBRARIES="
set "KICAD_Z_FOOTPRINT_LIBRARIES="
set "KICAD_Z_DESIGN_BLOCK_LIBRARIES="
set "KICAD_Z_3DMODEL_FILES="
set "KICAD_Z_REQUIRED_ENTRIES="

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

rem Fehlende Standardordner anlegen; vorhandene Inhalte niemals loeschen.
for %%D in (3dmodels 3rdparty designblocks footprints plugins projects scripting symbols template) do (
    if not exist "%KICAD_USER_DIR%\%%D" mkdir "%KICAD_USER_DIR%\%%D" >nul 2>nul
)

rem Eigene KiCad-3D-Modellbibliothek anlegen. KiCad erwartet fuer
rem 3D-Modellbibliotheken die Endung .3dshapes.
if not exist "%KICAD_USER_DIR%\3dmodels\Z_3DModell.3dshapes" mkdir "%KICAD_USER_DIR%\3dmodels\Z_3DModell.3dshapes" >nul 2>nul

rem Unsere projektspezifischen Variablen fuer den aktuellen Prozess setzen.
rem Allgemeine KiCad-Variablen werden bewusst nicht veraendert.
set "KICAD_Z_ROOT_DIR=%KICAD_USER_DIR%"
set "KICAD_Z_3DMODEL_DIR=%KICAD_USER_DIR%\3dmodels\Z_3DModell.3dshapes"
set "KICAD_Z_3RDPARTY_DIR=%KICAD_USER_DIR%\3rdparty"
set "KICAD_Z_DESIGN_BLOCK_DIR=%KICAD_USER_DIR%\designblocks"
set "KICAD_Z_FOOTPRINT_DIR=%KICAD_USER_DIR%\footprints"
set "KICAD_Z_PLUGIN_DIR=%KICAD_USER_DIR%\plugins"
set "KICAD_Z_PROJECT_DIR=%KICAD_USER_DIR%\projects"
set "KICAD_Z_SCRIPTING_DIR=%KICAD_USER_DIR%\scripting"
set "KICAD_Z_SYMBOL_DIR=%KICAD_USER_DIR%\symbols"
set "KICAD_Z_TEMPLATE_DIR=%KICAD_USER_DIR%\template"

rem Fehlende KICAD_Z_-Pfade direkt in vorhandenen KiCad-Konfigurationen
rem registrieren. Vorhandene oder abweichende Eintraege bleiben unveraendert.
for /f "usebackq tokens=1,* delims==" %%A in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0register_kicad_z_paths.ps1" -RootDirectory "%KICAD_USER_DIR%" 2^>nul`) do (
    if /i "%%A"=="KICAD_Z_REGISTRATION" set "KICAD_Z_REGISTRATION=%%B"
    if /i "%%A"=="KICAD_Z_REGISTERED" set "KICAD_Z_REGISTERED=%%B"
    if /i "%%A"=="KICAD_Z_EXISTING" set "KICAD_Z_EXISTING=%%B"
    if /i "%%A"=="KICAD_Z_MISSING_NAMES" set "KICAD_Z_MISSING_NAMES=%%B"
    if /i "%%A"=="KICAD_Z_ADDED_NAMES" set "KICAD_Z_ADDED_NAMES=%%B"
    if /i "%%A"=="KICAD_Z_EXISTING_NAMES" set "KICAD_Z_EXISTING_NAMES=%%B"
    if /i "%%A"=="KICAD_Z_MISMATCH_NAMES" set "KICAD_Z_MISMATCH_NAMES=%%B"
)

rem Z_-Bibliotheksdateien in den Benutzerordner kopieren und in allen
rem vorhandenen globalen KiCad-Bibliothekstabellen registrieren.
for /f "usebackq tokens=1,* delims==" %%A in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0register_kicad_z_libraries.ps1" -RepositoryRoot "%~dp0..\.." -UserRoot "%KICAD_USER_DIR%" 2^>nul`) do (
    if /i "%%A"=="KICAD_Z_LIBRARY_REGISTRATION" set "KICAD_Z_LIBRARY_REGISTRATION=%%B"
    if /i "%%A"=="KICAD_Z_LIBRARY_ADDED" set "KICAD_Z_LIBRARY_ADDED=%%B"
    if /i "%%A"=="KICAD_Z_LIBRARY_EXISTING" set "KICAD_Z_LIBRARY_EXISTING=%%B"
    if /i "%%A"=="KICAD_Z_LIBRARY_MISMATCH" set "KICAD_Z_LIBRARY_MISMATCH=%%B"
    if /i "%%A"=="KICAD_Z_SYMBOL_LIBRARIES" set "KICAD_Z_SYMBOL_LIBRARIES=%%B"
    if /i "%%A"=="KICAD_Z_FOOTPRINT_LIBRARIES" set "KICAD_Z_FOOTPRINT_LIBRARIES=%%B"
    if /i "%%A"=="KICAD_Z_DESIGN_BLOCK_LIBRARIES" set "KICAD_Z_DESIGN_BLOCK_LIBRARIES=%%B"
    if /i "%%A"=="KICAD_Z_3DMODEL_FILES" set "KICAD_Z_3DMODEL_FILES=%%B"
    if /i "%%A"=="KICAD_Z_REQUIRED_ENTRIES" set "KICAD_Z_REQUIRED_ENTRIES=%%B"
)

exit /b 0
