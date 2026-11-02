@echo off
REM Desktop icon entry: always take published main, then open the local desk.
setlocal EnableExtensions
cd /d "%~dp0"

if exist ".git\" (
  where git >nul 2>&1
  if not errorlevel 1 (
    echo Updating Evalathan to published main...
    for /f "delims=" %%H in ('git rev-parse HEAD') do set "BEFORE=%%H"
    git fetch origin
    if not errorlevel 1 (
      git checkout main
      git reset --hard origin/main
      for /f "delims=" %%H in ('git rev-parse HEAD') do set "AFTER=%%H"
      if defined BEFORE if defined AFTER if /I not "%BEFORE%"=="%AFTER%" (
        if not defined EVALATHAN_RELAUNCHED (
          echo Update applied. Restarting...
          endlocal
          set "EVALATHAN_RELAUNCHED=1"
          "%~f0" %*
          exit /b %ERRORLEVEL%
        )
      )
    )
  )
)

if not exist "ui\v2\index.html" (
  echo Evalathan files are missing. Run the README PowerShell/CMD install block first.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo First-time setup needed. Running launch.bat...
  call "%~dp0launch.bat"
  exit /b %ERRORLEVEL%
)

set "VENVPY=%~dp0.venv\Scripts\python.exe"
"%VENVPY%" -m pip install -e "%~dp0." >nul 2>&1
echo Opening Evalathan local desk...
"%VENVPY%" -c "from evalathan.webdesk import open_desk; raise SystemExit(open_desk())"
if errorlevel 1 pause
endlocal
