@echo off
REM Desktop icon: splash, hard-sync to GitHub main, then local desk.
setlocal EnableExtensions
cd /d "%~dp0"

call :start_splash

REM Always take published main so Mac/Windows cannot stay on a stale desk (e.g. no-logo proof).
if exist ".git\" (
  where git >nul 2>&1
  if not errorlevel 1 (
    echo Syncing Evalathan to published main...
    git fetch origin
    if not errorlevel 1 (
      git checkout main
      git reset --hard origin/main
    ) else (
      echo git fetch failed. Continuing with the files already on disk.
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

call :start_splash
set "VENVPY=%~dp0.venv\Scripts\python.exe"
"%VENVPY%" -m pip install -e "%~dp0." >nul 2>&1
set "EVALATHAN_SKIP_UPDATE=1"
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
if exist "%USERPROFILE%\.evalathan\splash.stop" del /q "%USERPROFILE%\.evalathan\splash.stop" >nul 2>&1
start "" "%SPY%" "%~dp0ui\v2\launch_splash.py"
goto :eof

:stop_splash
if exist "%~dp0ui\v2\launch_splash.py" if exist "%~dp0.venv\Scripts\python.exe" (
  "%~dp0.venv\Scripts\python.exe" "%~dp0ui\v2\launch_splash.py" --close >nul 2>&1
)
goto :eof
