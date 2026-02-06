#!/usr/bin/env python3
"""
PaddiSense YAML Validation Tests

Tests the YAML validation logic for package.yaml and dashboard files.

Usage:
    python3 test_yaml_validation.py
"""

import json
import tempfile
from pathlib import Path

import yaml

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def log_test(name, passed, details=""):
    status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    print(f"  [{status}] {name}")
    if details and not passed:
        print(f"         {details}")


def log_section(name):
    print(f"\n{BLUE}{BOLD}{name}{RESET}")
    print(f"{'-'*50}")


class YAMLValidator:
    """Standalone YAML validator matching module_manager.py logic."""

    def __init__(self, paddisense_dir: Path):
        self.paddisense_dir = paddisense_dir

    def validate_package_yaml(self, module_id: str) -> dict:
        """Validate a module's package.yaml file."""
        errors = []
        warnings = []
        package_file = self.paddisense_dir / module_id / "package.yaml"

        if not package_file.exists():
            return {"valid": False, "errors": ["package.yaml not found"], "warnings": []}

        try:
            content = package_file.read_text(encoding="utf-8")

            if not content.strip():
                return {"valid": False, "errors": ["package.yaml is empty"], "warnings": []}

            try:
                data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                return {"valid": False, "errors": [f"Invalid YAML: {e}"], "warnings": []}

            if data is None:
                return {"valid": False, "errors": ["Parsed as null"], "warnings": []}

            if not isinstance(data, dict):
                return {"valid": False, "errors": [f"Must be dict, got {type(data).__name__}"], "warnings": []}

            # Check for valid HA package keys
            valid_keys = {
                "automation", "binary_sensor", "command_line", "counter",
                "group", "homeassistant", "input_boolean", "input_datetime",
                "input_number", "input_select", "input_text", "light",
                "logger", "media_player", "mqtt", "notify", "recorder",
                "scene", "script", "sensor", "shell_command", "switch",
                "template", "timer", "utility_meter", "zone",
            }

            for key in data.keys():
                if key not in valid_keys:
                    warnings.append(f"Unusual key: '{key}'")

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "keys": list(data.keys()),
            }

        except IOError as e:
            return {"valid": False, "errors": [f"Read error: {e}"], "warnings": []}

    def validate_content(self, content: str) -> dict:
        """Validate YAML content directly."""
        errors = []
        warnings = []

        if not content.strip():
            return {"valid": False, "errors": ["Empty content"], "warnings": []}

        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            return {"valid": False, "errors": [f"Invalid YAML: {e}"], "warnings": []}

        if data is None:
            return {"valid": False, "errors": ["Parsed as null"], "warnings": []}

        if not isinstance(data, dict):
            return {"valid": False, "errors": [f"Must be dict"], "warnings": []}

        return {"valid": True, "errors": [], "warnings": warnings, "data": data}


def test_real_modules():
    """Test validation against real PaddiSense modules."""
    log_section("Testing Real Modules")

    validator = YAMLValidator(Path("/config/PaddiSense"))
    modules = ["ipm", "asm", "weather", "pwm", "rtr", "str", "wss", "registry"]

    all_passed = True
    for mod in modules:
        result = validator.validate_package_yaml(mod)
        passed = result["valid"]
        all_passed = all_passed and passed

        details = ""
        if not passed:
            details = "; ".join(result["errors"])
        elif result.get("warnings"):
            details = f"Warnings: {result['warnings']}"

        log_test(f"{mod}/package.yaml", passed, details)

        if passed and result.get("keys"):
            print(f"         Keys: {result['keys']}")

    return all_passed


def test_edge_cases():
    """Test validation with edge case YAML content."""
    log_section("Testing Edge Cases")

    validator = YAMLValidator(Path("/tmp"))
    all_passed = True

    # Test cases: (name, content, should_be_valid)
    test_cases = [
        ("Empty string", "", False),
        ("Whitespace only", "   \n\n   ", False),
        ("Just a comment", "# This is a comment", False),
        ("Null value", "null", False),
        ("Plain string", "just a string", False),
        ("List instead of dict", "- item1\n- item2", False),
        ("Number", "42", False),
        ("Valid minimal", "template: []", True),
        ("Valid with multiple keys", "template: []\nautomation: []", True),
        ("Invalid YAML syntax", "template:\n  - bad indent\n bad", False),
        ("Duplicate keys (YAML allows, last wins)", "template: []\ntemplate: [sensor: test]", True),
        ("Unicode content", "template:\n  - sensor:\n      name: 'Tëst Sënsör'", True),
        ("Very nested structure", """
template:
  - sensor:
      - name: Test
        state: "{{ states('sensor.test') }}"
        attributes:
          deep:
            nested:
              value: 123
""", True),
    ]

    for name, content, expected_valid in test_cases:
        result = validator.validate_content(content)
        passed = result["valid"] == expected_valid

        if not passed:
            details = f"Expected valid={expected_valid}, got valid={result['valid']}"
            if result.get("errors"):
                details += f" errors={result['errors']}"
        else:
            details = ""

        log_test(name, passed, details)
        all_passed = all_passed and passed

    return all_passed


def test_ha_specific_validation():
    """Test Home Assistant specific validation rules."""
    log_section("Testing HA-Specific Rules")

    validator = YAMLValidator(Path("/tmp"))
    all_passed = True

    # Test valid HA package keys
    valid_content = """
automation:
  - id: test
    alias: Test Automation
template:
  - sensor:
      - name: Test Sensor
shell_command:
  test_cmd: echo hello
input_boolean:
  test_toggle:
    name: Test Toggle
"""
    result = validator.validate_content(valid_content)
    log_test("Valid HA package keys", result["valid"])
    all_passed = all_passed and result["valid"]

    # Test with unusual (but potentially valid) keys
    unusual_content = """
custom_domain:
  - config: test
template:
  - sensor:
      - name: Test
"""
    result = validator.validate_content(unusual_content)
    has_warning = len(result.get("warnings", [])) > 0
    log_test("Unusual keys trigger warning", result["valid"] and has_warning,
             f"warnings={result.get('warnings', [])}")
    all_passed = all_passed and result["valid"]

    return all_passed


def test_dashboard_validation():
    """Test dashboard YAML validation."""
    log_section("Testing Dashboard Validation")

    all_passed = True

    # Valid dashboard
    valid_dashboard = """
title: Test Dashboard
views:
  - title: Overview
    path: overview
    cards:
      - type: markdown
        content: Hello World
"""
    try:
        data = yaml.safe_load(valid_dashboard)
        passed = isinstance(data, dict) and "title" in data and "views" in data
        log_test("Valid dashboard structure", passed)
        all_passed = all_passed and passed
    except Exception as e:
        log_test("Valid dashboard structure", False, str(e))
        all_passed = False

    # Test real dashboards
    dashboard_files = [
        Path("/config/PaddiSense/rtr/dashboards/views.yaml"),
        Path("/config/PaddiSense/str/dashboards/views.yaml"),
        Path("/config/PaddiSense/wss/dashboards/views.yaml"),
    ]

    for dash_file in dashboard_files:
        if dash_file.exists():
            try:
                content = dash_file.read_text()
                data = yaml.safe_load(content)
                passed = isinstance(data, dict) and "views" in data
                log_test(f"{dash_file.parent.parent.name} dashboard", passed)
                all_passed = all_passed and passed
            except Exception as e:
                log_test(f"{dash_file.parent.parent.name} dashboard", False, str(e))
                all_passed = False
        else:
            log_test(f"{dash_file.parent.parent.name} dashboard", False, "File not found")
            all_passed = False

    return all_passed


def main():
    print(f"\n{BOLD}PaddiSense YAML Validation Tests{RESET}")
    print(f"{'='*50}")

    results = []

    results.append(("Real Modules", test_real_modules()))
    results.append(("Edge Cases", test_edge_cases()))
    results.append(("HA-Specific Rules", test_ha_specific_validation()))
    results.append(("Dashboard Validation", test_dashboard_validation()))

    # Summary
    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}Summary{RESET}")
    print(f"{'-'*50}")

    total_passed = sum(1 for _, p in results if p)
    total_tests = len(results)

    for name, passed in results:
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  {name}: [{status}]")

    print(f"\n  Total: {total_passed}/{total_tests} test suites passed")

    if total_passed == total_tests:
        print(f"\n  {GREEN}{BOLD}ALL TESTS PASSED{RESET}")
        return 0
    else:
        print(f"\n  {RED}{BOLD}SOME TESTS FAILED{RESET}")
        return 1


if __name__ == "__main__":
    exit(main())
