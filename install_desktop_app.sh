#!/bin/bash
# Puts an Evalathan launcher on the Desktop with the red-dragon icon (macOS .app).
# Program files stay in this clone.
set -e
REPO="$(cd "$(dirname "$0")" && pwd)"
DESKTOP="${HOME}/Desktop"
APPDIR="${DESKTOP}/Evalathan"
APP_BUNDLE="${DESKTOP}/Evalathan.app"
mkdir -p "$APPDIR"

ICON_SRC=""
for candidate in \
  "${REPO}/ui/v2/assets/evalathan-app-icon.png" \
  "${REPO}/ui/v2/assets/icon-256.png" \
  "${REPO}/assets/evalathan-logo.png"
do
  if [ -f "$candidate" ]; then
    ICON_SRC="$candidate"
    break
  fi
done

build_icns() {
  local out_icns="$1"
  [ -n "$ICON_SRC" ] || return 1
  command -v sips >/dev/null 2>&1 || return 1
  command -v iconutil >/dev/null 2>&1 || return 1
  local iconset
  iconset="$(mktemp -d)/Evalathan.iconset"
  mkdir -p "$iconset"
  # Standard iconset sizes for Dock / Desktop / Finder.
  sips -z 16 16     "$ICON_SRC" --out "$iconset/icon_16x16.png" >/dev/null
  sips -z 32 32     "$ICON_SRC" --out "$iconset/icon_16x16@2x.png" >/dev/null
  sips -z 32 32     "$ICON_SRC" --out "$iconset/icon_32x32.png" >/dev/null
  sips -z 64 64     "$ICON_SRC" --out "$iconset/icon_32x32@2x.png" >/dev/null
  sips -z 128 128   "$ICON_SRC" --out "$iconset/icon_128x128.png" >/dev/null
  sips -z 256 256   "$ICON_SRC" --out "$iconset/icon_128x128@2x.png" >/dev/null
  sips -z 256 256   "$ICON_SRC" --out "$iconset/icon_256x256.png" >/dev/null
  sips -z 512 512   "$ICON_SRC" --out "$iconset/icon_256x256@2x.png" >/dev/null
  sips -z 512 512   "$ICON_SRC" --out "$iconset/icon_512x512.png" >/dev/null
  sips -z 1024 1024 "$ICON_SRC" --out "$iconset/icon_512x512@2x.png" >/dev/null
  iconutil -c icns "$iconset" -o "$out_icns"
  rm -rf "$(dirname "$iconset")"
  [ -f "$out_icns" ]
}

# Shell launcher kept for Terminal users / older installs.
COMMAND="${APPDIR}/Evalathan.command"
cat > "$COMMAND" <<EOF
#!/bin/bash
cd "$REPO"
exec bash "$REPO/launch.sh"
EOF
chmod +x "$COMMAND"
cp "$COMMAND" "${DESKTOP}/Evalathan.command"
chmod +x "${DESKTOP}/Evalathan.command"

# Preferred: Evalathan.app on the Desktop with the dragon icon overlay.
rm -rf "$APP_BUNDLE"
mkdir -p "${APP_BUNDLE}/Contents/MacOS" "${APP_BUNDLE}/Contents/Resources"
ICNS="${APP_BUNDLE}/Contents/Resources/AppIcon.icns"
if ! build_icns "$ICNS"; then
  # Fallback: copy PNG as app resource (Finder may still show generic).
  if [ -n "$ICON_SRC" ]; then
    cp "$ICON_SRC" "${APP_BUNDLE}/Contents/Resources/AppIcon.png"
  fi
fi

# Finder-safe launcher: no Terminal required (mirrors Windows Evalathan.bat).
# Logs to ~/.evalathan/launch.log; alerts via osascript on hard failure.
cat > "${APP_BUNDLE}/Contents/MacOS/Evalathan" <<EOF
#!/bin/bash
# EVALATHAN desk opener for double-click from Finder (PATH + logging).
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:\$PATH"
if [ -x /opt/homebrew/bin/brew ]; then
  eval "\$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true
elif [ -x /usr/local/bin/brew ]; then
  eval "\$(/usr/local/bin/brew shellenv)" 2>/dev/null || true
fi

REPO="$REPO"
LOGDIR="\${HOME}/.evalathan"
mkdir -p "\$LOGDIR"
exec >>"\$LOGDIR/launch.log" 2>&1
echo "---- \$(date) Evalathan.app start ----"
cd "\$REPO" || {
  osascript -e 'display alert "EVALATHAN" message "Program folder missing. Re-run the README Mac install block." as critical' >/dev/null 2>&1 || true
  exit 1
}

start_splash() {
  local py=""
  if [ -x "\$REPO/.venv/bin/python" ]; then
    py="\$REPO/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    py="\$(command -v python3)"
  fi
  [ -n "\$py" ] || return 0
  [ -f "\$REPO/ui/v2/launch_splash.py" ] || return 0
  rm -f "\$LOGDIR/splash.stop" 2>/dev/null || true
  "\$py" "\$REPO/ui/v2/launch_splash.py" >/dev/null 2>&1 &
  disown \$! 2>/dev/null || true
}

stop_splash() {
  if [ -x "\$REPO/.venv/bin/python" ] && [ -f "\$REPO/ui/v2/launch_splash.py" ]; then
    "\$REPO/.venv/bin/python" "\$REPO/ui/v2/launch_splash.py" --close >/dev/null 2>&1 || true
  fi
}

# Fast path when the venv + desk files already exist (daily Desktop click).
if [ -x "\$REPO/.venv/bin/python" ] && [ -f "\$REPO/ui/v2/index.html" ]; then
  start_splash
  if [ -d "\$REPO/.git" ] && command -v git >/dev/null 2>&1; then
    git -C "\$REPO" fetch origin >/dev/null 2>&1 || true
  fi
  "\$REPO/.venv/bin/python" -m pip install -e "\$REPO" >/dev/null 2>&1 || true
  # Circle first, then update ask/apply (branded or osascript). Hard-reset if Python fails.
  start_splash
  "\$REPO/.venv/bin/python" -c "from evalathan.desk_update import sync_or_prompt; raise SystemExit(sync_or_prompt())"
  UP=\$?
  if [ "\$UP" = "42" ]; then
    exit 0
  fi
  if [ "\$UP" -ne 0 ]; then
    echo "Python update step failed - forcing published main..."
    git -C "\$REPO" checkout main >/dev/null 2>&1 || true
    git -C "\$REPO" reset --hard origin/main >/dev/null 2>&1 || true
    "\$REPO/.venv/bin/python" -m pip install -e "\$REPO" >/dev/null 2>&1 || true
  fi
  start_splash
  export EVALATHAN_SKIP_UPDATE=1
  echo "Opening desk via .venv"
  "\$REPO/.venv/bin/python" -c "from evalathan.webdesk import open_desk; raise SystemExit(open_desk())"
  EC=\$?
  stop_splash
  if [ "\$EC" -ne 0 ]; then
    osascript -e "display alert \\"EVALATHAN\\" message \\"Desk failed to open (exit \$EC). See ~/.evalathan/launch.log\\" as critical" >/dev/null 2>&1 || true
  fi
  exit "\$EC"
fi

# First-time / incomplete install: full launch.sh (still no Terminal.app).
echo "Falling back to launch.sh (venv or ui/v2 missing)"
start_splash
bash "\$REPO/launch.sh"
EC=\$?
stop_splash
if [ "\$EC" -ne 0 ]; then
  osascript -e "display alert \\"EVALATHAN\\" message \\"Setup/launch failed (exit \$EC). See ~/.evalathan/launch.log\\" as critical" >/dev/null 2>&1 || true
fi
exit "\$EC"
EOF
chmod +x "${APP_BUNDLE}/Contents/MacOS/Evalathan"

cat > "${APP_BUNDLE}/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>
  <string>EVALATHAN</string>
  <key>CFBundleDisplayName</key>
  <string>EVALATHAN</string>
  <key>CFBundleIdentifier</key>
  <string>local.evalathan.desk</string>
  <key>CFBundleVersion</key>
  <string>0.3.2</string>
  <key>CFBundleShortVersionString</key>
  <string>0.3.2</string>
  <key>CFBundleExecutable</key>
  <string>Evalathan</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleIconFile</key>
  <string>AppIcon</string>
  <key>LSMinimumSystemVersion</key>
  <string>11.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
EOF

# Also mirror the .app into Desktop/Evalathan/ for the folder install.
rm -rf "${APPDIR}/Evalathan.app"
cp -R "$APP_BUNDLE" "${APPDIR}/Evalathan.app"

# Touch so Finder refreshes the icon badge; clear quarantine so double-click works.
touch "$APP_BUNDLE" "${APPDIR}/Evalathan.app" 2>/dev/null || true
xattr -dr com.apple.quarantine "$APP_BUNDLE" "${APPDIR}/Evalathan.app" 2>/dev/null || true

cat > "${APPDIR}/README.txt" <<EOF
EVALATHAN (local)

This folder is only a launcher. The program itself lives here:
$REPO

Double-click Evalathan.app on your Desktop (dragon icon).
No Terminal window is required - same idea as the Windows Desktop icon.
Evalathan.command is a Terminal fallback if the .app is blocked.
Launch log: ~/.evalathan/launch.log
Nothing is hosted on a public website.
EOF

echo "Desktop app: ${APP_BUNDLE}"
echo "Desktop command (fallback): ${DESKTOP}/Evalathan.command"
echo "Desktop folder: ${APPDIR}"
echo "Program folder (local): ${REPO}"
