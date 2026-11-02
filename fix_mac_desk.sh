#!/bin/bash
# Fix a stuck Mac Evalathan desk (no logos / old UI) without depending on a local script copy.
# Run in Terminal:
#   curl -fsSL https://raw.githubusercontent.com/pedramgoshATgmail/EVALATHAN/main/fix_mac_desk.sh | bash
set -e
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

echo "EVALATHAN Mac desk fix"
echo "----------------------"

REPO=""
# 1) Prefer the clone path baked into the Desktop app launcher.
for APP in \
  "${HOME}/Desktop/Evalathan.app" \
  "${HOME}/Desktop/Evalathan/Evalathan.app"
do
  LAUNCH="${APP}/Contents/MacOS/Evalathan"
  if [ -f "$LAUNCH" ]; then
    CAND="$(grep -E '^REPO=' "$LAUNCH" | head -1 | sed 's/^REPO=//' | tr -d '"' | tr -d "'")"
    if [ -n "$CAND" ] && [ -d "$CAND/.git" ] && [ -f "$CAND/ui/v2/index.html" ]; then
      REPO="$CAND"
      echo "Found Desktop app clone: $REPO"
      break
    fi
  fi
done

# 2) Common install locations.
if [ -z "$REPO" ]; then
  for d in \
    "${HOME}/evalathan-program" \
    "${HOME}/Desktop/evalathan-program" \
    "${HOME}/Documents/evalathan-program" \
    "${HOME}/Developer/evalathan-program" \
    "${HOME}/TOKISH/evalathan" \
    "${HOME}/Desktop/TOKISH/evalathan"
  do
    if [ -d "$d/.git" ] && [ -f "$d/ui/v2/index.html" ]; then
      REPO="$d"
      echo "Found clone: $REPO"
      break
    fi
  done
fi

if [ -z "$REPO" ]; then
  osascript -e 'display alert "EVALATHAN" message "No Evalathan git clone found. Re-run the README Mac install block from https://github.com/pedramgoshATgmail/EVALATHAN" as critical' >/dev/null 2>&1 || true
  echo "No Evalathan git clone found."
  echo "Re-run the README Mac install block, then open Evalathan.app again."
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required."
  exit 1
fi

cd "$REPO"
BEFORE="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "Before: $BEFORE"
echo "Syncing to origin/main..."
git fetch origin
git checkout main
git reset --hard origin/main
AFTER="$(git rev-parse --short HEAD)"
echo "After:  $AFTER"

if [ -x .venv/bin/python ]; then
  .venv/bin/python -m pip install -e . >/dev/null
fi

# Rewrite Desktop Evalathan.app so every future click hard-syncs again.
if [ -f "$REPO/install_desktop_app.sh" ]; then
  bash "$REPO/install_desktop_app.sh"
fi

# Confirm logos CSS is the restored flex layout.
if grep -q "Update-popup proof: hide main dragon" "$REPO/ui/v2/styles.css" 2>/dev/null; then
  echo "WARNING: styles still look like the no-logo proof build."
  exit 2
fi
if ! grep -A6 "^\.splash-art-slot {" "$REPO/ui/v2/styles.css" | grep -q "display: flex"; then
  echo "WARNING: splash-art-slot is not display:flex."
  exit 2
fi

echo
echo "OK - desk is on $AFTER with logos restored."
echo "Open Evalathan.app from your Desktop now."
osascript -e "display alert \"EVALATHAN\" message \"Desk synced to $AFTER. Logos should be back - open Evalathan.app.\" as informational" >/dev/null 2>&1 || true
