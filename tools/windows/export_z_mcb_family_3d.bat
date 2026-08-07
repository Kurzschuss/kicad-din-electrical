@echo off
setlocal EnableExtensions
cd /d "%~dp0\..\.."

set "PYTHON_EXE=.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
set "RESULT=0"

echo ============================================================
echo   ProjectOS - MCB 1P/3P 3D-Export
echo ============================================================
echo.

echo [1/5] Pruefe OpenSCAD und FreeCADCmd ...
"%PYTHON_EXE%" tools\export_z_mcb_3d.py --check-tools
if errorlevel 1 goto :failed

echo.
echo [2/5] Pruefe MCB-1P Geometrie 18 x 84 mm ...
"%PYTHON_EXE%" tools\export_z_mcb_3d.py --check-geometry
if errorlevel 1 goto :failed

echo.
echo [3/5] Pruefe MCB-3P Geometrie 54 x 84 mm ...
"%PYTHON_EXE%" tools\export_z_mcb_3p_3d.py --check-geometry
if errorlevel 1 goto :failed

echo.
echo [4/5] Erzeuge MCB-1P STEP und WRL ...
"%PYTHON_EXE%" tools\export_z_mcb_3d.py
if errorlevel 1 goto :failed

echo.
echo [5/5] Erzeuge MCB-3P STEP und WRL ...
"%PYTHON_EXE%" tools\export_z_mcb_3p_3d.py
if errorlevel 1 goto :failed

echo.
echo Erfolgreich erzeugt:
echo   models\Z_MCB_1P\generated\Z_MCB_1P.step
echo   models\Z_MCB_1P\generated\Z_MCB_1P.wrl
echo   models\Z_MCB_3P\generated\Z_MCB_3P.step
echo   models\Z_MCB_3P\generated\Z_MCB_3P.wrl
echo.
echo Danach run_tests.bat einmal neu starten, damit die Dateien nach
echo Documents\kicad synchronisiert werden.
goto :finish

:failed
set "RESULT=1"
echo.
echo FEHLER: MCB-1P/3P-Export oder Masspruefung fehlgeschlagen.

:finish
echo.
echo ============================================================
if "%RESULT%"=="0" (
    echo   Vorgang erfolgreich beendet.
) else (
    echo   Vorgang mit Fehlercode %RESULT% beendet.
)
echo ============================================================
echo.
pause
exit /b %RESULT%
