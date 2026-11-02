#!/bin/bash
set -e
cd "$(dirname "$0")"

start_fuss_splash() {
  if [ ! -f ui/v2/launch_splash.py ]; then
    return 0
  fi
  local py=""
  if [ -x .venv/bin/python ]; then
    py=".venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    py="$(command -v python3)"
  fi
  [ -n "$py" ] || return 0
  # Intentional start: clear prior stop so a fresh splash may paint.
  rm -f "${HOME}/.evalathan/splash.stop" 2>/dev/null || true
  "$py" ui/v2/launch_splash.py >/dev/null 2>&1 &
  disown $! 2>/dev/null || true
}

stop_fuss_splash() {
  if [ -f ui/v2/launch_splash.py ]; then
    if [ -x .venv/bin/python ]; then
      .venv/bin/python ui/v2/launch_splash.py --close >/dev/null 2>&1 || true
    elif command -v python3 >/dev/null 2>&1; then
      python3 ui/v2/launch_splash.py --close >/dev/null 2>&1 || true
    fi
  fi
}

trap stop_fuss_splash EXIT
start_fuss_splash

# Always take published main when this folder is a git clone (old Tk desk -> browser desk).
if [ -d .git ] && command -v git >/dev/null 2>&1; then
  echo "Updating Evalathan to the published main tree..."
  BEFORE="$(git rev-parse HEAD)"
  if git fetch origin; then
    git checkout main
    git reset --hard origin/main
    AFTER="$(git rev-parse HEAD)"
    if [ "$BEFORE" != "$AFTER" ] && [ -z "${EVALATHAN_RELAUNCHED:-}" ]; then
      echo "Update applied. Restarting launcher..."
      export EVALATHAN_RELAUNCHED=1
      # Keep splash up across relaunch; do not stop it here.
      trap - EXIT
      exec bash "$0" "$@"
    fi
  else
    echo "git fetch failed. Continuing with the files already on disk."
  fi
fi
# Splash script may have refreshed with main.
start_fuss_splash

if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi

has_window() {
  "$1" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1 \
    && "$1" -c 'import tkinter' >/dev/null 2>&1
}

find_python() {
  local candidate
  for candidate in python3 \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3 \
    /Library/Frameworks/Python.framework/Versions/Current/bin/python3
  do
    if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then
      if has_window "$candidate"; then
        command -v "$candidate"
        return 0
      fi
    fi
  done
  local framework
  for framework in /Library/Frameworks/Python.framework/Versions/*/bin/python3; do
    [ -x "$framework" ] || continue
    if has_window "$framework"; then
      echo "$framework"
      return 0
    fi
  done
  return 1
}

BASE=""
if BASE="$(find_python)"; then
  :
else
  if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3.10 or newer was not found."
    echo "Install it from https://www.python.org/downloads/macos/"
    exit 1
  fi
  VER="$(python3 -c 'import sys; print("%d.%d" % (sys.version_info.major, sys.version_info.minor))')"
  MACOS_MAJOR="$(sw_vers -productVersion 2>/dev/null | cut -d. -f1)"
  if [ -n "$MACOS_MAJOR" ] && [ "$MACOS_MAJOR" -ge 14 ] && command -v brew >/dev/null 2>&1; then
    echo "Python ${VER} has no window library (tkinter)."
    echo "Installing python-tk@${VER} ..."
    if ! brew install "python-tk@${VER}"; then
      echo "Homebrew could not install the window library."
      echo "Install Python from https://www.python.org/downloads/macos/ and run bash launch.sh again."
      exit 1
    fi
  else
    echo "Python ${VER} has no window library (tkinter)."
    echo "Install Python from https://www.python.org/downloads/macos/ and run bash launch.sh again."
    echo "That macOS installer includes the window library."
    exit 1
  fi
  if ! BASE="$(find_python)"; then
    echo "The window library is still missing after python-tk@${VER}."
    echo "Install Python from https://www.python.org/downloads/macos/ and run bash launch.sh again."
    exit 1
  fi
fi

if [ -x .venv/bin/python ] && ! .venv/bin/python -c 'import tkinter' >/dev/null 2>&1; then
  rm -rf .venv
fi

if [ ! -x .venv/bin/python ]; then
  "$BASE" -m venv .venv
fi

if [ ! -f ui/v2/index.html ]; then
  echo "ui/v2 is missing. This checkout is too old or incomplete."
  echo "From this folder run:"
  echo "  git fetch origin"
  echo "  git checkout main"
  echo "  git reset --hard origin/main"
  echo "Then run bash launch.sh again. Expected: v0.3.2 local desk."
  exit 1
fi

. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
echo
echo "Installing the Evalathan Desktop launcher..."
bash "$(dirname "$0")/install_desktop_app.sh" || true
echo
echo "Starting Evalathan v0.3.2 local desk window..."
echo "Look for Evalathan.app on your Desktop (dragon icon), or Evalathan.command as a fallback."
echo "Keep this terminal open while the desk is running, or use the Desktop launcher next time."
echo
exec python -c "from evalathan.webdesk import open_desk; raise SystemExit(open_desk())"
