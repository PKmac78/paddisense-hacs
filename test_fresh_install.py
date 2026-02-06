#!/usr/bin/env python3
"""
PaddiSense Fresh Install Simulation

Simulates the full HACS installation flow:
1. Integration files present (custom_components/paddisense/)
2. Git clone of PaddiSense repo
3. Module installation via ModuleManager logic
4. Configuration validation

Usage:
    python3 test_fresh_install.py [--clean]

    --clean: Remove test artifacts after completion
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import yaml

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


def log(msg, color=RESET):
    print(f"{color}{msg}{RESET}")


def log_step(step_num, msg):
    print(f"\n{CYAN}[Step {step_num}]{RESET} {BOLD}{msg}{RESET}")


def log_ok(msg):
    print(f"  {GREEN}[OK]{RESET} {msg}")


def log_fail(msg):
    print(f"  {RED}[FAIL]{RESET} {msg}")


def log_warn(msg):
    print(f"  {YELLOW}[WARN]{RESET} {msg}")


def log_info(msg):
    print(f"       {msg}")


class FreshInstallSimulator:
    """Simulate a fresh PaddiSense installation."""

    def __init__(self, test_dir: Path):
        self.test_dir = test_dir
        self.config_dir = test_dir / "config"
        self.custom_components = self.config_dir / "custom_components" / "paddisense"
        self.paddisense_dir = self.config_dir / "PaddiSense"
        self.local_data = self.config_dir / "local_data"
        self.results = {
            "steps": [],
            "passed": 0,
            "failed": 0,
            "warnings": 0,
        }

    def record(self, step: str, passed: bool, message: str = "", warning: bool = False):
        """Record a test result."""
        self.results["steps"].append({
            "step": step,
            "passed": passed,
            "message": message,
            "warning": warning,
        })
        if warning:
            self.results["warnings"] += 1
        elif passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1

    def setup_test_environment(self) -> bool:
        """Create a simulated /config directory structure."""
        log_step(1, "Setting up test environment")

        try:
            # Create directory structure
            self.config_dir.mkdir(parents=True, exist_ok=True)
            (self.config_dir / "custom_components").mkdir(exist_ok=True)
            log_ok(f"Created test config dir: {self.config_dir}")

            # Create minimal configuration.yaml
            config_yaml = """
# Test Home Assistant configuration
homeassistant:
  name: Test Farm
  packages: !include_dir_named PaddiSense/packages

lovelace:
  mode: yaml
  dashboards: !include lovelace_dashboards.yaml
"""
            (self.config_dir / "configuration.yaml").write_text(config_yaml)
            log_ok("Created configuration.yaml")

            # Create empty lovelace_dashboards.yaml
            (self.config_dir / "lovelace_dashboards.yaml").write_text("# PaddiSense dashboards\n")
            log_ok("Created lovelace_dashboards.yaml")

            self.record("setup_environment", True)
            return True

        except Exception as e:
            log_fail(f"Setup failed: {e}")
            self.record("setup_environment", False, str(e))
            return False

    def simulate_hacs_download(self) -> bool:
        """Simulate HACS downloading the integration."""
        log_step(2, "Simulating HACS integration download")

        # Source: paddisense-hacs/custom_components/paddisense
        source = Path("/config/paddisense-hacs/custom_components/paddisense")

        if not source.is_dir():
            log_fail(f"Source not found: {source}")
            self.record("hacs_download", False, "Source directory missing")
            return False

        try:
            # Copy integration files
            shutil.copytree(source, self.custom_components)
            log_ok(f"Copied integration to: {self.custom_components}")

            # Verify critical files
            critical_files = [
                "__init__.py",
                "manifest.json",
                "config_flow.py",
                "const.py",
            ]

            for f in critical_files:
                if (self.custom_components / f).exists():
                    log_ok(f"  {f} present")
                else:
                    log_fail(f"  {f} MISSING")
                    self.record("hacs_download", False, f"Missing {f}")
                    return False

            self.record("hacs_download", True)
            return True

        except Exception as e:
            log_fail(f"Copy failed: {e}")
            self.record("hacs_download", False, str(e))
            return False

    def simulate_git_clone(self) -> bool:
        """Simulate cloning the PaddiSense module repository."""
        log_step(3, "Simulating git clone of PaddiSense repo")

        # Source: /config/PaddiSense (the actual repo)
        source = Path("/config/PaddiSense")

        if not source.is_dir():
            log_fail(f"Source repo not found: {source}")
            self.record("git_clone", False, "Source repo missing")
            return False

        try:
            # Copy repo (excluding .git, __pycache__, and existing symlinks in packages/)
            def ignore_patterns(directory, files):
                ignored = []
                if '.git' in files:
                    ignored.append('.git')
                if '__pycache__' in files:
                    ignored.append('__pycache__')
                # For packages dir, only copy the directory itself (exclude symlinks)
                if directory.endswith('packages'):
                    ignored.extend([f for f in files if f.endswith('.yaml')])
                return ignored

            shutil.copytree(source, self.paddisense_dir, ignore=ignore_patterns)
            log_ok(f"Cloned repo to: {self.paddisense_dir}")

            # Verify structure
            required = ["VERSION", "modules.json", "install.sh"]
            for f in required:
                if (self.paddisense_dir / f).exists():
                    log_ok(f"  {f} present")
                else:
                    log_warn(f"  {f} missing")

            # Check modules
            modules = ["ipm", "asm", "weather", "pwm", "rtr", "str", "wss"]
            for mod in modules:
                mod_dir = self.paddisense_dir / mod
                if mod_dir.is_dir() and (mod_dir / "package.yaml").exists():
                    log_ok(f"  Module {mod}/ ready")
                else:
                    log_warn(f"  Module {mod}/ incomplete")

            self.record("git_clone", True)
            return True

        except Exception as e:
            log_fail(f"Clone failed: {e}")
            self.record("git_clone", False, str(e))
            return False

    def simulate_module_installation(self) -> bool:
        """Simulate installing modules."""
        log_step(4, "Simulating module installation")

        packages_dir = self.paddisense_dir / "packages"
        packages_dir.mkdir(exist_ok=True)

        modules_to_install = ["rtr", "str", "wss"]
        success_count = 0

        # Load modules.json
        modules_json_path = self.paddisense_dir / "modules.json"
        if modules_json_path.exists():
            modules_meta = json.loads(modules_json_path.read_text()).get("modules", {})
        else:
            modules_meta = {}

        for module_id in modules_to_install:
            log_info(f"\n  Installing {module_id}...")

            module_dir = self.paddisense_dir / module_id
            package_file = module_dir / "package.yaml"

            # Check module exists
            if not module_dir.is_dir():
                log_fail(f"    Module directory not found")
                continue

            if not package_file.exists():
                log_fail(f"    package.yaml not found")
                continue

            # Validate YAML
            try:
                content = package_file.read_text()
                data = yaml.safe_load(content)
                if not isinstance(data, dict):
                    log_fail(f"    Invalid package.yaml structure")
                    continue
                log_ok(f"    YAML validation passed")
            except yaml.YAMLError as e:
                log_fail(f"    YAML error: {e}")
                continue

            # Create symlink
            symlink_path = packages_dir / f"{module_id}.yaml"
            relative_target = Path("..") / module_id / "package.yaml"
            try:
                # Remove existing symlink/file if present
                if symlink_path.exists() or symlink_path.is_symlink():
                    symlink_path.unlink()
                symlink_path.symlink_to(relative_target)
                log_ok(f"    Symlink created")
            except OSError as e:
                log_fail(f"    Symlink failed: {e}")
                continue

            # Create data directory
            data_dir = self.local_data / module_id
            data_dir.mkdir(parents=True, exist_ok=True)
            (data_dir / "backups").mkdir(exist_ok=True)
            log_ok(f"    Data directory created")

            # Update lovelace_dashboards.yaml
            meta = modules_meta.get(module_id, {})
            slug = meta.get("dashboard_slug", f"{module_id}-dashboard")
            title = meta.get("dashboard_title", module_id)
            icon = meta.get("icon", "mdi:package")
            dashboard_file = meta.get("dashboard_file", f"{module_id}/dashboards/views.yaml")

            dashboards_file = self.config_dir / "lovelace_dashboards.yaml"
            dashboards = yaml.safe_load(dashboards_file.read_text()) or {}
            dashboards[slug] = {
                "mode": "yaml",
                "title": title,
                "icon": icon,
                "show_in_sidebar": True,
                "filename": f"PaddiSense/{dashboard_file}",
            }
            dashboards_file.write_text(yaml.dump(dashboards, default_flow_style=False))
            log_ok(f"    Dashboard registered: {slug}")

            success_count += 1

        passed = success_count == len(modules_to_install)
        if passed:
            log_ok(f"\n  All {success_count} modules installed successfully")
        else:
            log_warn(f"\n  {success_count}/{len(modules_to_install)} modules installed")

        self.record("module_installation", passed, f"{success_count}/{len(modules_to_install)}")
        return passed

    def verify_installation(self) -> bool:
        """Verify the simulated installation."""
        log_step(5, "Verifying installation")

        checks = []

        # Check configuration.yaml
        config_yaml = self.config_dir / "configuration.yaml"
        content = config_yaml.read_text()
        if "PaddiSense/packages" in content:
            log_ok("configuration.yaml has packages include")
            checks.append(True)
        else:
            log_fail("configuration.yaml missing packages include")
            checks.append(False)

        # Check symlinks exist and resolve
        packages_dir = self.paddisense_dir / "packages"
        for mod in ["rtr", "str", "wss"]:
            symlink = packages_dir / f"{mod}.yaml"
            if symlink.is_symlink():
                resolved = symlink.resolve()
                if resolved.exists():
                    log_ok(f"Symlink {mod}.yaml -> {resolved.name}")
                    checks.append(True)
                else:
                    log_fail(f"Symlink {mod}.yaml broken")
                    checks.append(False)
            else:
                log_fail(f"Symlink {mod}.yaml not found")
                checks.append(False)

        # Check lovelace_dashboards.yaml
        dashboards_file = self.config_dir / "lovelace_dashboards.yaml"
        dashboards = yaml.safe_load(dashboards_file.read_text()) or {}
        for slug in ["rtr-predictions", "str-stock", "wss-safety"]:
            if slug in dashboards:
                log_ok(f"Dashboard {slug} registered")
                checks.append(True)
            else:
                log_fail(f"Dashboard {slug} not registered")
                checks.append(False)

        # Check data directories
        for mod in ["rtr", "str", "wss"]:
            data_dir = self.local_data / mod
            if data_dir.is_dir():
                log_ok(f"Data directory {mod}/ exists")
                checks.append(True)
            else:
                log_fail(f"Data directory {mod}/ missing")
                checks.append(False)

        passed = all(checks)
        self.record("verification", passed)
        return passed

    def print_summary(self):
        """Print test summary."""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}  Fresh Install Simulation Summary{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")

        print(f"\n  Test directory: {self.test_dir}")
        print(f"\n  Results:")
        print(f"    {GREEN}Passed:{RESET}   {self.results['passed']}")
        print(f"    {RED}Failed:{RESET}   {self.results['failed']}")
        print(f"    {YELLOW}Warnings:{RESET} {self.results['warnings']}")

        if self.results['failed'] == 0:
            print(f"\n  {GREEN}{BOLD}SIMULATION PASSED{RESET}")
            print(f"  The HACS installation flow works correctly.")
        else:
            print(f"\n  {RED}{BOLD}SIMULATION FAILED{RESET}")
            print(f"  Review the errors above and fix issues.")

        return self.results['failed'] == 0

    def run(self) -> bool:
        """Run the full simulation."""
        print(f"\n{BOLD}PaddiSense Fresh Install Simulation{RESET}")
        print(f"{'='*60}")
        print(f"Test directory: {self.test_dir}")
        print(f"Started: {datetime.now().isoformat()}")

        steps = [
            self.setup_test_environment,
            self.simulate_hacs_download,
            self.simulate_git_clone,
            self.simulate_module_installation,
            self.verify_installation,
        ]

        for step in steps:
            if not step():
                log(f"\n{RED}Simulation aborted due to failure{RESET}")
                break

        return self.print_summary()


def main():
    parser = argparse.ArgumentParser(description="PaddiSense Fresh Install Simulation")
    parser.add_argument("--clean", action="store_true", help="Remove test artifacts after")
    parser.add_argument("--keep", action="store_true", help="Keep test directory for inspection")
    args = parser.parse_args()

    # Create temp directory
    test_dir = Path(tempfile.mkdtemp(prefix="paddisense_test_"))

    try:
        simulator = FreshInstallSimulator(test_dir)
        success = simulator.run()

        if args.keep:
            print(f"\n{YELLOW}Test directory kept at: {test_dir}{RESET}")
        elif args.clean or success:
            shutil.rmtree(test_dir)
            print(f"\n{CYAN}Test directory cleaned up{RESET}")
        else:
            print(f"\n{YELLOW}Test directory preserved for debugging: {test_dir}{RESET}")

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted{RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
