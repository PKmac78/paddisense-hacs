# PaddiSense Farm Management

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/PKmac78/paddisense-hacs.svg)](https://github.com/PKmac78/paddisense-hacs/releases)

**PaddiSense** is a modular farm management platform for Home Assistant OS (HAOS). It provides tools for managing paddocks, bays, seasons, inventory, assets, weather stations, and irrigation systems.

## Features

- **Farm Registry**: Core paddock/bay/season management with auto-generated IDs
- **Modular Design**: Install only the modules you need
  - **IPM** - Inventory & Product Management
  - **ASM** - Asset Service Management
  - **Weather** - Weather station integration
  - **PWM** - Paddy Water Management
- **Offline-First**: All core workflows run without internet
- **Mobile-First UI**: Large touch targets, dark mode compatible

## License Key System

PaddiSense uses a **seasonal license key** system for access control and updates.

### How It Works

- Each grower receives a **single license key** from their administrator at the start of each season
- The license key contains:
  - Grower and farm identity
  - Season expiry date
  - Enabled modules (IPM, ASM, Weather, PWM)
  - Repository access credentials (embedded GitHub token)
- The license key is entered during initial setup or renewed via the options menu

### What Happens When a License Expires?

**Your existing installation continues working:**
- All installed modules remain functional
- Existing data (paddocks, bays, seasons, inventory, etc.) is preserved
- Day-to-day operations are unaffected

**What is prevented without a valid license:**
- Downloading updates from the PaddiSense repository
- Installing new modules
- Receiving new features and enhancements

### Renewing Your License

When you receive a new license key for the new season:

1. Go to **Settings** → **Devices & Services**
2. Find **PaddiSense** and click **Configure**
3. Select **Renew License**
4. Paste your new license key
5. Click Submit

The new license immediately enables updates and new module installations.

## Installation

### Prerequisites

- Home Assistant OS (HAOS) 2025.1.0 or later
- HACS installed
- Valid PaddiSense license key (contact your administrator)

### Step 1: Add Custom Repository

1. Open **HACS** from the sidebar
2. Click **Integrations**
3. Click the three-dot menu (top right) → **Custom repositories**
4. Add: `https://github.com/PKmac78/paddisense-hacs`
5. Category: **Integration**
6. Click **Add**

### Step 2: Download & Install

1. In HACS → Integrations, click **+ Explore & Download Repositories**
2. Search for "PaddiSense"
3. Click **Download**
4. **Restart Home Assistant**

### Step 3: Setup Wizard

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "PaddiSense"
4. Follow the setup wizard:
   - Enter your farm details (grower name, farm name)
   - Enter your license key
   - Wait for repository download
   - Select modules to install
   - Wait for installation to complete
5. Home Assistant will restart automatically

## Updating

When updates are available and you have a valid license, HACS will notify you. Click **Update** to:

1. Update the integration
2. Pull latest module changes from the PaddiSense repository
3. Automatically restart Home Assistant

You can also check for updates manually in the **PaddiSense Manager** dashboard.

> **Note:** Updates require a valid (non-expired) license key. If your license has expired, contact your administrator for a renewal key.

## Documentation

- [Quick Start Guide](https://github.com/PKmac78/PaddiSense/blob/main/docs/QUICK_START.md)
- [Architecture](https://github.com/PKmac78/PaddiSense/blob/main/docs/ARCHITECTURE.md)
- [Module Documentation](https://github.com/PKmac78/PaddiSense/tree/main/docs)

## Support

- [Report Issues](https://github.com/PKmac78/paddisense-hacs/issues)
- [Discussions](https://github.com/PKmac78/PaddiSense/discussions)

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**For Administrators:** License keys are generated using the `tools/generate_license.py` script in the main PaddiSense repository. Each key embeds a GitHub Personal Access Token for repository access. See the admin documentation for details on seasonal token management.
