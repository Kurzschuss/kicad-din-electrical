@echo off
setlocal EnableExtensions
cd /d "%~dp0\..\.."
set "PYTHON_EXE=.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
set "RESULT=0"
set "PROGRESS=powershell -NoProfile -ExecutionPolicy Bypass -File tools\windows\run_python_with_progress.ps1"

echo ============================================================
echo   ProjectOS - RCD/RCCB 2P/4P 3D-Export
echo ============================================================
echo.

echo [1/5] Pruefe OpenSCAD und FreeCADCmd ...
"%PYTHON_EXE%" tools\export_z_rcd_2p_3d.py --check-tools
if errorlevel 1 goto :failed

echo.
echo [2/5] Pruefe RCD-2P Geometrie 36 x 84 mm ...
%PROGRESS% -Python "%PYTHON_EXE%" -Script "tools\export_z_rcd_2p_3d.py" -Argument "--check-geometry" -Label "RCD-2P Geometrie"
if errorlevel 1 goto :failed

echo.
echo [3/5] Pruefe RCD-4P Geometrie 72 x 84 mm ...
%PROGRESS% -Python "%PYTHON_EXE%" -Script "tools\export_z_rcd_4p_3d.py" -Argument "--check-geometry" -Label "RCD-4P Geometrie"
if errorlevel 1 goto :failed

echo.
echo [4/5] Erzeuge RCD-2P STEP und WRL ...
%PROGRESS% -Python "%PYTHON_EXE%" -Script "tools\export_z_rcd_2p_3d.py" -Label "RCD-2P Export"
if errorlevel 1 goto :failed

echo.
echo [5/5] Erzeuge RCD-4P STEP und WRL ...
%PROGRESS% -Python "%PYTHON_EXE%" -Script "tools\export_z_rcd_4p_3d.py" -Label "RCD-4P Export"
if errorlevel 1 goto :failed

echo.
echo Erfolgreich erzeugt:
echo   models\Z_RCD_2P\generated\Z_RCD_2P.step
echo   models\Z_RCD_2P\generated\Z_RCD_2P.wrl
echo   models\Z_RCD_4P\generated\Z_RCD_4P.step
echo   models\Z_RCD_4P\generated\Z_RCD_4P.wrl
goto :finish

:failed
set "RESULT=1"
echo.
echo FEHLER: RCD-2P/4P-Export oder Masspruefung fehlgeschlagen.

:finish
echo.
echo ============================================================
if "%RESULT%"=="0" (
  echo   FERTIG - RCD-2P/4P 3D-EXPORT ABGESCHLOSSEN
  echo   Alle vorgesehenen Schritte wurden erfolgreich beendet.
) else (
  echo   NICHT ABGESCHLOSSEN - FEHLER AUFGETRETEN
)
echo ============================================================
echo.
echo Druecke eine beliebige Taste, um dieses Fenster zu schliessen ...
pause >nul
exit /b %RESULT%
