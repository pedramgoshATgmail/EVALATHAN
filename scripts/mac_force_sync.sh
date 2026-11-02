#!/bin/bash
# One-shot Mac unblock: pull published main (restores logos) and rewrite Desktop Evalathan.app.
set -e
CANDIDATES=(
  "$HOME/evalathan-program"
  "$HOME/Desktop/evalathan-program"
  "$HOME/Desktop/TOKISH/evalathan"
  "$(pwd)"
)
REPO=""
for d in "${CANDIDATES[@]}"; do
  if [ -d "$d/.git" ] && [ -f "$d/ui/v2/index.html" ]; then
    REPO="$d"
    break
  fi
done
if [ -z "$REPO" ]; then
  echo "Could not find an Evalathan git clone."
  echo "cd into your evalathan-program folder and run: bash scripts/mac_force_sync.sh"
  exit 1
fi
echo "Syncing: $REPO"
cd "$REPO"
git fetch origin
git checkout main
git reset --hard origin/main
if [ -x .venv/bin/python ]; then
  .venv/bin/python -m pip install -e . >/dev/null
fi
bash "$REPO/install_desktop_app.sh"
echo
echo "Done. Logos and desk are on published main."
echo "Open Evalathan.app from your Desktop."
