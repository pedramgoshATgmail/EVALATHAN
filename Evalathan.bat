@echo off
REM Desktop icon entry: FUSS launching splash ASAP, then published main, then local desk.
setlocal EnableExtensions
cd /d "%~dp0"

REM Show the centered FUSS "launching..." circle as soon as the Desktop icon is clicked.
call :start_splash

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
  call :stop_splash
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo First-time setup needed. Running launch.bat...
  call "%~dp0launch.bat"
  exit /b %ERRORLEVEL%
)

REM Splash file may have refreshed with main - keep one instance up.
call :start_splash

set "VENVPY=%~dp0.venv\Scripts\python.exe"
"%VENVPY%" -m pip install -e "%~dp0." >nul 2>&1
echo Opening Evalathan local desk...
"%VENVPY%" -c "from evalathan.webdesk import open_desk; raise SystemExit(open_desk())"
set "EC=%ERRORLEVEL%"
call :stop_splash
if not "%EC%"=="0" pause
exit /b %EC%

:start_splash
if not exist "%~dp0ui\v2\launch_splash.py" goto :eof
set "SPY="
if exist "%~dp0.venv\Scripts\pythonw.exe" set "SPY=%~dp0.venv\Scripts\pythonw.exe"
if not defined SPY if exist "%~dp0.venv\Scripts\python.exe" set "SPY=%~dp0.venv\Scripts\python.exe"
if not defined SPY for /f "delims=" %%P in ('where pythonw 2^>nul') do (
  if not defined SPY set "SPY=%%P"
)
if not defined SPY for /f "delims=" %%P in ('where python 2^>nul') do (
  if not defined SPY set "SPY=%%P"
)
if not defined SPY goto :eof
start "" "%SPY%" "%~dp0ui\v2\launch_splash.py"
goto :eof

:stop_splash
if exist "%~dp0ui\v2\launch_splash.py" if exist "%~dp0.venv\Scripts\python.exe" (
  "%~dp0.venv\Scripts\python.exe" "%~dp0ui\v2\launch_splash.py" --close >nul 2>&1
)
goto :eof
