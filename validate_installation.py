#!/usr/bin/env python3
"""
PaddiSense Installation Validator

Run this script to verify that PaddiSense is correctly installed.

Usage:
    python3 validate_installation.py
"""

import json
import subprocess
import sys
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  {text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_ok(text):
    print(f"  {GREEN}[OK]{RESET} {text}")

def print_fail(text):
    print(f"  {RED}[FAIL]{RESET} {text}")

def print_warn(text):
    print(f"  {YELLOW}[WARN]{RESET} {text}")

def print_info(text):
    print(f"       {text}")

def check_path_exists(path: Path, description: str) -> bool:
    """Check if a path exists."""
    if path.exists():
        print_ok(f"{description}: {path}")
        return True
    else:
        print_fail(f"{description}: {path}")
        return False

def check_file_content(path: Path, description: str) -> bool:
    """Check if file exists and has content."""
    if not path.exists():
        print_fail(f"{description}: File not found")
        return False

    try:
        content = path.read_text(encoding='utf-8').strip()
        if content:
            print_ok(f"{description}: {len(content)} bytes")
            return True
        else:
            print_warn(f"{description}: File is empty")
            return False
    except Exception as e:
        print_fail(f"{description}: {e}")
        return False

def check_json_valid(path: Path, description: str) -> bool:
    """Check if JSON file is valid."""
    if not path.exists():
        print_fail(f"{description}: File not found")
        return False

    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        print_ok(f"{description}: Valid JSON")
        return True
    except json.JSONDecodeError as e:
        print_fail(f"{description}: Invalid JSON - {e}")
        return False

def check_symlink(path: Path, description: str) -> bool:
    """Check if symlink exists and is valid."""
    if path.is_symlink():
        target = path.resolve()
        if target.exists():
            print_ok(f"{description}: -> {target}")
            return True
        else:
            print_fail(f"{description}: Broken symlink -> {path.readlink()}")
            return False
    elif path.exists():
        print_warn(f"{description}: Exists but not a symlink")
        return True
    else:
        print_fail(f"{description}: Not found")
        return False

def check_git_available() -> bool:
    """Check if git is available."""
    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print_ok(f"Git available: {result.stdout.strip()}")
            return True
        else:
            print_fail("Git not available")
            return False
    except Exception as e:
        print_fail(f"Git check failed: {e}")
        return False

def main():
    print_header("PaddiSense Installation Validator")

    config_dir = Path("/config")
    paddisense_dir = config_dir / "PaddiSense"
    custom_components = config_dir / "custom_components" / "paddisense"
    local_data = config_dir / "local_data"

    all_passed = True

    # ==========================================================================
    # 1. System Requirements
    # ==========================================================================
    print_header("1. System Requirements")

    all_passed &= check_path_exists(config_dir / "configuration.yaml", "Home Assistant config")
    all_passed &= check_git_available()

    # ==========================================================================
    # 2. Integration Files
    # ==========================================================================
    print_header("2. Integration Files (custom_components/paddisense)")

    integration_files = [
        "__init__.py",
        "manifest.json",
        "config_flow.py",
        "const.py",
        "sensor.py",
        "helpers.py",
        "services.yaml",
        "strings.json",
        "installer/__init__.py",
        "installer/git_manager.py",
        "installer/module_manager.py",
        "installer/backup_manager.py",
        "installer/config_writer.py",
        "registry/__init__.py",
        "registry/backend.py",
        "registry/sensor.py",
        "www/paddisense-registry-card.js",
        "www/paddisense-manager-card.js",
        "translations/en.json",
    ]

    for f in integration_files:
        all_passed &= check_path_exists(custom_components / f, f)

    # Check manifest.json is valid
    all_passed &= check_json_valid(custom_components / "manifest.json", "manifest.json validity")

    # ==========================================================================
    # 3. PaddiSense Repository
    # ==========================================================================
    print_header("3. PaddiSense Repository")

    all_passed &= check_path_exists(paddisense_dir, "PaddiSense directory")

    # Git repo check - warn if missing (developer setup may not have separate .git)
    git_dir = paddisense_dir / ".git"
    if git_dir.is_dir():
        print_ok("Git repository: Standalone clone")
    elif (config_dir / ".git").is_dir():
        print_warn("Git repository: Part of parent repo (developer setup)")
        # Don't fail - this is valid for developer installs
    else:
        print_fail("Git repository: Not found")
        all_passed = False

    all_passed &= check_file_content(paddisense_dir / "VERSION", "Root VERSION file")
    all_passed &= check_json_valid(paddisense_dir / "modules.json", "modules.json")

    # ==========================================================================
    # 4. Module Directories
    # ==========================================================================
    print_header("4. Module Directories")

    modules = ["ipm", "asm", "weather", "pwm"]
    for mod in modules:
        mod_dir = paddisense_dir / mod
        if mod_dir.is_dir():
            print_ok(f"Module directory: {mod}/")
            check_file_content(mod_dir / "VERSION", f"  {mod}/VERSION")
            check_path_exists(mod_dir / "package.yaml", f"  {mod}/package.yaml")
        else:
            print_warn(f"Module directory not found: {mod}/")

    # ==========================================================================
    # 5. Package Symlinks
    # ==========================================================================
    print_header("5. Package Symlinks")

    packages_dir = paddisense_dir / "packages"
    if packages_dir.is_dir():
        print_ok(f"Packages directory exists")
        for mod in modules:
            symlink = packages_dir / f"{mod}.yaml"
            if symlink.exists() or symlink.is_symlink():
                check_symlink(symlink, f"  {mod}.yaml")
            else:
                print_info(f"  {mod}.yaml not installed (optional)")
    else:
        print_warn("Packages directory not found (will be created on module install)")

    # ==========================================================================
    # 6. Local Data Directories
    # ==========================================================================
    print_header("6. Local Data Directories")

    all_passed &= check_path_exists(local_data, "local_data directory")

    registry_data = local_data / "registry"
    if registry_data.is_dir():
        print_ok("Registry data directory exists")
        check_path_exists(registry_data / "config.json", "  Registry config.json")
    else:
        print_info("Registry data not initialized yet (normal for fresh install)")

    # ==========================================================================
    # 7. Configuration Files
    # ==========================================================================
    print_header("7. Configuration Files")

    # Check configuration.yaml has PaddiSense entries
    config_yaml = config_dir / "configuration.yaml"
    if config_yaml.exists():
        content = config_yaml.read_text(encoding='utf-8')

        if "!include_dir_named PaddiSense/packages" in content:
            print_ok("configuration.yaml has packages include")
        else:
            print_warn("configuration.yaml missing packages include")
            print_info("Add: homeassistant:")
            print_info("       packages: !include_dir_named PaddiSense/packages/")

        if "!include lovelace_dashboards.yaml" in content:
            print_ok("configuration.yaml has dashboards include")
        else:
            print_warn("configuration.yaml missing dashboards include")
            print_info("Add to lovelace section:")
            print_info("       dashboards: !include lovelace_dashboards.yaml")

    # Check lovelace_dashboards.yaml
    lovelace_file = config_dir / "lovelace_dashboards.yaml"
    if lovelace_file.exists():
        print_ok("lovelace_dashboards.yaml exists")
    else:
        print_info("lovelace_dashboards.yaml not created yet (will be created on module install)")

    # ==========================================================================
    # Summary
    # ==========================================================================
    print_header("Summary")

    if all_passed:
        print(f"\n  {GREEN}All critical checks passed!{RESET}")
        print("\n  PaddiSense appears to be correctly installed.")
        print("  If this is a fresh install, add the integration via:")
        print("    Settings -> Devices & Services -> Add Integration -> PaddiSense")
    else:
        print(f"\n  {RED}Some checks failed.{RESET}")
        print("\n  Review the errors above and fix any issues.")
        print("  Common fixes:")
        print("    - Restart Home Assistant after installation")
        print("    - Run the setup wizard if not completed")
        print("    - Check Home Assistant logs for errors")

    print()
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
