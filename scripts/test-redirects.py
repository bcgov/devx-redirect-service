#!/usr/bin/env python3
"""
Test script for redirect functionality.
Parses test cases from test-cases.yaml and validates redirects.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Dict, List, Any

import yaml
import requests

local_host = "http://localhost"

def load_test_cases(yaml_file: str) -> List[Dict[str, Any]]:
    """Load test cases from YAML file."""
    if not os.path.exists(yaml_file):
        print(f"❌ Test data file not found: {yaml_file}")
        sys.exit(1)

    try:
        with open(yaml_file, "r") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML: {e}")
        sys.exit(1)

    return config.get("test_services", [])


def build_url(port: int | None, path: str) -> str:
    """Build a URL from port and path."""
    return f"{local_host}:{port}{path}"


def test_redirect(port: int | None, path: str, expected_url: str) -> bool:
    """
    Test a single redirect.
    Returns True if the redirect matches expected URL, False otherwise.
    """
    url = build_url(port, path)

    print(f"🔎 Testing {path}")
    print(f"   ↳ Expect: {expected_url}")

    try:
        response = requests.head(url, allow_redirects=False, timeout=5)
        status = response.status_code
        location = response.headers.get("Location", "")

        if status == 301 and location == expected_url:
            print("   ✅ OK")
            return True

        print(f"   ❌ FAIL: Status={status}, Location={location}")
        return False

    except requests.RequestException as e:
        print(f"   ❌ ERROR: {e}")
        return False


def test_404_error(port: int | None) -> bool:
    """Test that non-existent path returns 404."""
    url = build_url(port, "/non-existent-path/")

    print("🔎 Testing error handling (/non-existent-path/)")

    try:
        response = requests.head(url, allow_redirects=False, timeout=5)
        status = response.status_code

        if status == 404:
            print("   ✅ 404 handling OK")
            return True

        print(f"   ❌ Expected 404 but got {status}")
        return False

    except requests.RequestException as e:
        print(f"   ❌ ERROR: {e}")
        return False


def check_service_allowed(service: str, test_configs: List[Dict[str, Any]]) -> bool:
    if any(cfg.get("service") == service for cfg in test_configs):
        return True

    print(f"❌ Service '{service}' is not defined in test-cases.yaml")
    return False


def get_test_configs(test_configs: List[Dict[str, Any]], service: str | None = None) -> List[Dict[str, Any]]:
    if service is None:
        return test_configs
    return [cfg for cfg in test_configs if cfg.get("service") == service]


def run_tests(configs_to_test: List[Dict[str, Any]]) -> bool:
    """
    Run tests for matching configurations.

    Args:
        configs_to_test: List of test configurations to run locally
    Returns:
        True if all tests passed, False if any test failed.
    """
    all_passed = True

    print("🚀 Starting redirect tests in local")
    print()

    for test_config in configs_to_test:
        service = test_config.get("service")
        port = test_config.get("port")

        if not service:
            print("❌ Test config is missing required field 'service'")
            all_passed = False
            continue
        
        if not port:
            print(f"❌ Test config for service '{service}' is missing required field 'port'")
            all_passed = False
            continue
        

        test_404 = test_config.get("test_404", True)
        cases = test_config.get("cases", [])

        print(f"🧪 Testing {service} redirects on {local_host}:{port}")

        for case in cases:
            path = case["path"]
            expected = case["expected"]

            if not test_redirect(port, path, expected):
                all_passed = False

        if test_404 and not test_404_error(port):
            all_passed = False

        print()

    return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test redirect service functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test all services locally
    %(prog)s

    # Test a single local service
    %(prog)s --service docs
    """,
    )
    parser.add_argument(
        "--service",
        default=None,
        help="Optional service name filter from test-cases.yaml (for example: docs, stackoverflow, rocketchat, just-ask)",
    )

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    yaml_file = script_dir / "test-cases.yaml"

    test_configs = load_test_cases(str(yaml_file))

    if args.service and not check_service_allowed(args.service, test_configs):
        sys.exit(1)

    configs_to_test = get_test_configs(test_configs, args.service)

    if not configs_to_test:
        print("❌ No test configurations found" + (f" for service '{args.service}'" if args.service else ""))
        sys.exit(1)

    print("Configuration:" + (f", service={args.service}" if args.service else ", service=all"))
    print()

    if run_tests(configs_to_test):
        print("🎉 All tests passed successfully!")
        sys.exit(0)

    print("❌ Some tests failed!")
    sys.exit(1)


if __name__ == "__main__":
    main()
