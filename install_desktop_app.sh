#!/bin/bash
# Puts an Evalathan launcher on the Desktop. Program files stay in this clone.
set -e
REPO="$(cd "$(dirname "$0")" && pwd)"
DESKTOP="${HOME}/Desktop"
APPDIR="${DESKTOP}/Evalathan"
mkdir -p "$APPDIR"

COMMAND="${APPDIR}/Evalathan.command"
cat > "$COMMAND" <<EOF
#!/bin/bash
cd "$REPO"
exec bash "$REPO/launch.sh"
EOF
chmod +x "$COMMAND"

# Also drop a one-click command on the Desktop itself.
cp "$COMMAND" "${DESKTOP}/Evalathan.command"
chmod +x "${DESKTOP}/Evalathan.command"

cat > "${APPDIR}/README.txt" <<EOF
EVALATHAN (local)

This folder is only a launcher. The program itself lives here:
$REPO

Double-click Evalathan.command.
It opens the local desk window. Nothing is hosted on a public website.
EOF

echo "Desktop launcher: ${DESKTOP}/Evalathan.command"
echo "Desktop folder: ${APPDIR}"
echo "Program folder (local): ${REPO}"
