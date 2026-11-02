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

cat > "${APP_BUNDLE}/Contents/MacOS/Evalathan" <<EOF
#!/bin/bash
cd "$REPO"
exec bash "$REPO/launch.sh"
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

# Touch so Finder refreshes the icon badge.
touch "$APP_BUNDLE" "${APPDIR}/Evalathan.app" 2>/dev/null || true

cat > "${APPDIR}/README.txt" <<EOF
EVALATHAN (local)

This folder is only a launcher. The program itself lives here:
$REPO

Double-click Evalathan.app on your Desktop (dragon icon).
Evalathan.command is a Terminal fallback if the .app is blocked.
Nothing is hosted on a public website.
EOF

echo "Desktop app: ${APP_BUNDLE}"
echo "Desktop command (fallback): ${DESKTOP}/Evalathan.command"
echo "Desktop folder: ${APPDIR}"
echo "Program folder (local): ${REPO}"
