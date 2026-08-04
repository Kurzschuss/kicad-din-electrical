@echo off
setlocal EnableExtensions

if "%~3"=="" (
    echo Verwendung:
    echo   run_with_error_report.bat "Pruefung" "Logdatei" Befehl [Argumente ...]
    exit /b 2
)

set "REPORT_TITLE=%~1"
set "REPORT_LOG=%~2"
shift
shift

python -m tools.run_with_error_report ^
  --title "%REPORT_TITLE%" ^
  --log "%REPORT_LOG%" ^
  --report "build\FEHLERBERICHT.md" ^
  -- %*

set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
    echo.
    echo ============================================================
    echo   Automatischer Fehlerbericht wurde erzeugt
    echo ============================================================
    echo.
    echo   Bericht: build\FEHLERBERICHT.md
    echo   Protokoll: %REPORT_LOG%
    echo.
)

exit /b %RESULT%
