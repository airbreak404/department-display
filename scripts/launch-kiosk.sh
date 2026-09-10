#!/usr/bin/env bash
# ==============================================================================
# WMU MAE Department Display - Kiosk Launch Script
# Target: Ubuntu 24.04 LTS (Noble Numbat) on iMac13,2 (GNOME 46 / Wayland)
# Display: 55-inch Commercial Display (2048 x 1152 @ 60Hz)
# ==============================================================================

# Ensure Wayland hardware acceleration is active for Firefox
export MOZ_ENABLE_WAYLAND=1
export GDK_BACKEND=wayland

# Determine URL (local repository clone or GitHub Pages fallback)
DISPLAY_URL="https://airbreak404.github.io/department-display/"

LOCAL_FILE="$HOME/Repos/department-display/index.html"
if [ -f "$LOCAL_FILE" ]; then
  DISPLAY_URL="file://$LOCAL_FILE"
fi

echo "Starting WMU MAE Department Display in Kiosk Mode..."
echo "Target URL: $DISPLAY_URL"

# Launch Firefox in full kiosk mode
# --kiosk locks the UI without tabs, address bar, or close buttons
exec firefox --kiosk "$DISPLAY_URL"
