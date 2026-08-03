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

rem Unsere projektspezifischen Benutzer-Umgebungsvariablen setzen.
rem Allgemeine KiCad-Variablen werden bewusst nicht veraendert.
set "KICAD_Z_ROOT_DIR=%KICAD_USER_DIR%"
set "KICAD_Z_3DMODEL_DIR=%KICAD_USER_DIR%\3dmodels"
set "KICAD_Z_3RDPARTY_DIR=%KICAD_USER_DIR%\3rdparty"
set "KICAD_Z_FOOTPRINT_DIR=%KICAD_USER_DIR%\footprints"
set "KICAD_Z_PLUGIN_DIR=%KICAD_USER_DIR%\plugins"
set "KICAD_Z_PROJECT_DIR=%KICAD_USER_DIR%\projects"
set "KICAD_Z_SCRIPTING_DIR=%KICAD_USER_DIR%\scripting"
set "KICAD_Z_SYMBOL_DIR=%KICAD_USER_DIR%\symbols"
set "KICAD_Z_TEMPLATE_DIR=%KICAD_USER_DIR%\template"

for %%V in (
    KICAD_Z_ROOT_DIR
    KICAD_Z_3DMODEL_DIR
    KICAD_Z_3RDPARTY_DIR
    KICAD_Z_FOOTPRINT_DIR
    KICAD_Z_PLUGIN_DIR
    KICAD_Z_PROJECT_DIR
    KICAD_Z_SCRIPTING_DIR
    KICAD_Z_SYMBOL_DIR
    KICAD_Z_TEMPLATE_DIR
) do call :persist_user_variable %%V

exit /b 0

:persist_user_variable
set "Z_VAR_NAME=%~1"
for /f "tokens=1,* delims==" %%A in ('set %Z_VAR_NAME% 2^>nul') do if /i "%%A"=="%Z_VAR_NAME%" set "Z_VAR_VALUE=%%B"
if defined Z_VAR_VALUE setx "%Z_VAR_NAME%" "%Z_VAR_VALUE%" >nul 2>nul
set "Z_VAR_NAME="
set "Z_VAR_VALUE="
exit /b 0
