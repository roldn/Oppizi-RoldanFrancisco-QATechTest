@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM  Oppizi – OCM API Test Automation Runner (Windows)
REM ═══════════════════════════════════════════════════════════════════════

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║       OPPIZI – Open Charge Map API Test Automation          ║
echo ║                   QA Automation Runner v1.0                 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

SET SCRIPT_DIR=%~dp0
SET COLLECTION=%SCRIPT_DIR%OCM_API_Tests.postman_collection.json
SET ENVIRONMENT=%SCRIPT_DIR%OCM_API_Tests.postman_environment.json
SET REPORTS_DIR=%SCRIPT_DIR%reports

IF NOT EXIST "%REPORTS_DIR%" mkdir "%REPORTS_DIR%"

REM ── Get API Key ──────────────────────────────────────────────────────
IF "%OCM_API_KEY%"=="" (
    echo Ingresa tu API key de Open Charge Map:
    SET /P OCM_API_KEY="> "
)

IF "%OCM_API_KEY%"=="" (
    echo ERROR: La API key es requerida.
    exit /b 1
)

REM ── Timestamp ────────────────────────────────────────────────────────
FOR /F "tokens=2 delims==" %%I IN ('wmic os get localdatetime /value') DO SET DT=%%I
SET TIMESTAMP=%DT:~0,8%_%DT:~8,6%
SET RUN_ID=OCM_RUN_%TIMESTAMP%

SET JSON_OUT=%REPORTS_DIR%\%RUN_ID%_results.json
SET HTML_OUT=%REPORTS_DIR%\%RUN_ID%_report.html

echo Run ID    : %RUN_ID%
echo Timestamp : %DATE% %TIME%
echo.
echo Ejecutando tests...
echo.

REM ── Run Newman ───────────────────────────────────────────────────────
newman run "%COLLECTION%" ^
  --environment "%ENVIRONMENT%" ^
  --env-var "apiKey=%OCM_API_KEY%" ^
  --reporters cli,json,htmlextra ^
  --reporter-json-export "%JSON_OUT%" ^
  --reporter-htmlextra-export "%HTML_OUT%" ^
  --reporter-htmlextra-title "Oppizi – OCM API Test Report" ^
  --reporter-htmlextra-darkTheme ^
  --reporter-htmlextra-logs ^
  --delay-request 300 ^
  --timeout-request 5000

echo.
echo ────────────────────────────────────────────────────
echo  Reportes generados:
echo  HTML  ^> %HTML_OUT%
echo  JSON  ^> %JSON_OUT%
echo ────────────────────────────────────────────────────
echo.

REM ── Run Python analysis ──────────────────────────────────────────────
IF EXIST "%JSON_OUT%" (
    python "%SCRIPT_DIR%scripts\parse_results.py" "%JSON_OUT%" "%RUN_ID%"
)

REM ── Open HTML report ─────────────────────────────────────────────────
start "" "%HTML_OUT%"

echo.
echo Proceso completado. El reporte se abrio en tu browser.
pause
