#!/usr/bin/env bash
# ==============================================================================
# Universal Fullscreen Launcher for WMU MAE Department Display Board
# Zero local dependencies. Runs directly in Firefox.
# ==============================================================================

# Determine display URL (GitHub Pages hosted or local index.html)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
URL="https://airbreak404.github.io/department-display/"

# If local file exists, prefer local file URL
if [ -f "$REPO_DIR/index.html" ]; then
  URL="file://$REPO_DIR/index.html"
fi

echo "======================================================="
echo "WMU Mechanical & Aerospace Engineering Display"
echo "Launching in Firefox Fullscreen Kiosk Mode..."
echo "Target: $URL"
echo "======================================================="

# Detect operating system
OS="$(uname -s)"

if [ "$OS" = "Darwin" ]; then
  # macOS
  if [ -d "/Applications/Firefox.app" ]; then
    open -a Firefox --args --kiosk "$URL"
  else
    echo "Opening in default browser..."
    open "$URL"
  fi
elif [ "$OS" = "Linux" ]; then
  # Ubuntu / Linux (Wayland / X11)
  export MOZ_ENABLE_WAYLAND=1
  firefox --kiosk "$URL" &
else
  # Windows / Git Bash
  start firefox --kiosk "$URL" 2>/dev/null || start "$URL"
fi
