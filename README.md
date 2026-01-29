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

## Installation

### Prerequisites

- Home Assistant OS (HAOS) 2025.1.0 or later
- HACS installed

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
   - Enter your farm details
   - Select modules to install
   - Wait for installation to complete
5. Home Assistant will restart automatically

## Updating

When updates are available, HACS will notify you. Click **Update** to:

1. Update the integration
2. Pull latest module changes from the PaddiSense repository
3. Automatically restart Home Assistant

You can also check for updates manually in the **PaddiSense Manager** dashboard.

## Documentation

- [Quick Start Guide](https://github.com/PKmac78/PaddiSense/blob/main/docs/QUICK_START.md)
- [Architecture](https://github.com/PKmac78/PaddiSense/blob/main/docs/ARCHITECTURE.md)
- [Module Documentation](https://github.com/PKmac78/PaddiSense/tree/main/docs)

## Support

- [Report Issues](https://github.com/PKmac78/paddisense-hacs/issues)
- [Discussions](https://github.com/PKmac78/PaddiSense/discussions)

## License

MIT License - see [LICENSE](LICENSE) for details.
