## PaddiSense Farm Management

A modular farm management platform for Home Assistant OS.

### What it does

- **Farm Registry**: Manage paddocks, bays, and growing seasons
- **Modular**: Install only what you need (Inventory, Assets, Weather, Irrigation)
- **Offline-First**: Works without internet
- **Mobile-Friendly**: Large touch targets, dark mode

### License Key Required

PaddiSense requires a **seasonal license key** from your administrator.

- The license key controls which modules you can access
- Updates require a valid (non-expired) license
- **Existing data is preserved** even after license expiry
- Renew via Settings → Devices & Services → PaddiSense → Configure → Renew License

### Installation

After downloading, add the integration via Settings → Devices & Services → Add Integration → PaddiSense.

The setup wizard will guide you through:
1. Setting up your farm identity
2. Entering your license key
3. Selecting modules to install
4. Automatic configuration

### Updates

This integration manages updates for PaddiSense modules. When you update via HACS (with valid license), it will:
- Update the integration code
- Pull latest module changes
- Restart Home Assistant automatically

**Note:** Updates are only available with a valid license. Your installation continues working after expiry, but new features require a renewed license key.
