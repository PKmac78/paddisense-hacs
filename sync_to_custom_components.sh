#!/bin/bash
#
# Sync paddisense-hacs to custom_components for testing
#
# Usage:
#   ./sync_to_custom_components.sh
#

set -e

SOURCE="/config/paddisense-hacs/custom_components/paddisense"
DEST="/config/custom_components/paddisense"

echo "Syncing PaddiSense integration..."
echo "  Source: $SOURCE"
echo "  Dest:   $DEST"

# Backup existing if present
if [ -d "$DEST" ]; then
    BACKUP="$DEST.backup.$(date +%Y%m%d_%H%M%S)"
    echo "  Backing up existing to: $BACKUP"
    mv "$DEST" "$BACKUP"
fi

# Copy new version
echo "  Copying files..."
cp -r "$SOURCE" "$DEST"

# Set permissions
chmod -R 755 "$DEST"

echo ""
echo "Done! Restart Home Assistant to apply changes."
echo ""
echo "To restart:"
echo "  ha core restart"
echo ""
echo "Or via UI: Settings -> System -> Restart"
