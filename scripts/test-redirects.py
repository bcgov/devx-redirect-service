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
from urllib.parse import urlparse

local_host = "localhost"
allowed_hosts = {local_host}  # Always allow localhost


def load_test_cases(yaml_file: str) -> List[Dict[str, Any]]:
    """Load test cases from YAML file."""
    if not os.path.exists(yaml_file):
        print(f"❌ Test data file not found: {yaml_file}")
        sys.exit(1)
    
    try:
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML: {e}")
        sys.exit(1)
    
    return config.get('test_ports', [])


def build_url(protocol: str, host: str, port: int | None, path: str) -> str:
    """Build a URL from protocol, host, port, and path."""
    if port:
        return f"{protocol}://{host}:{port}{path}"
    return f"{protocol}://{host}{path}"


def test_redirect(protocol: str, host: str, port: int | None, path: str, expected_url: str) -> bool:
    """
    Test a single redirect.
    Returns True if the redirect matches expected URL, False otherwise.
    """
    url = build_url(protocol, host, port, path)

    if not check_host_allowed(url):
        return False
    
    print(f"🔎 Testing {path}")
    print(f"   ↳ Expect: {expected_url}")
    
    try:
        response = requests.head(url, allow_redirects=False, timeout=5)
        status = response.status_code
        location = response.headers.get('Location', '')
        
        if status == 301 and location == expected_url:
            print("   ✅ OK")
            return True
        else:
            print(f"   ❌ FAIL: Status={status}, Location={location}")
            return False
    
    except requests.RequestException as e:
        print(f"   ❌ ERROR: {e}")
        return False


def test_404_error(protocol: str, host: str, port: int | None) -> bool:
    """Test that non-existent path returns 404."""
    url = build_url(protocol, host, port, '/non-existent-path/')

    if not check_host_allowed(url):
        return False
    
    print("🔎 Testing error handling (/non-existent-path/)")
    
    try:
        response = requests.head(url, allow_redirects=False, timeout=5)
        status = response.status_code
        
        if status == 404:
            print("   ✅ 404 handling OK")
            return True
        else:
            print(f"   ❌ Expected 404 but got {status}")
            return False
    
    except requests.RequestException as e:
        print(f"   ❌ ERROR: {e}")
        return False

def check_host_allowed(url: str) -> bool:
    """Validate that a hostname is in the allowed hosts list.
    
    Fixes issue: https://sonarcloud.io/organizations/bcgov-sonarcloud/rules?open=pythonsecurity%3AS8703&rule_key=pythonsecurity%3AS8703
    """
    if urlparse(url).hostname not in allowed_hosts:
        print(f"❌ Host '{urlparse(url).hostname}' is not allowed.")
        return False
    else:
        return True

def run_tests(
    protocol: str,
    host: str,
    configs_to_test: List[Dict[str, Any]],
    port_override: int | None = None
) -> bool:
    """
    Run tests for matching configurations.
    
    Args:
        protocol: HTTP protocol (http or https)
        host: Target host (localhost for local dev, or domain for production)
        configs_to_test: List of test configurations to run
        port_override: Optional port override (for localhost testing)
    Returns:
        True if all tests passed, False if any test failed.
    """
    all_passed = True        
    
    print(f"🚀 Starting redirect tests on {host}")
    print()
    
    for test_config in configs_to_test:
        # Determine which endpoint to use
        if host == local_host:
            port = port_override or test_config.get('port')
            endpoint_display = f"{host}:{port}"
        else:
            # Production: use hostname directly (HTTPS assumed)
            port = None
            endpoint_display = host
        
        test_404 = test_config.get('test_404', True)
        cases = test_config.get('cases', [])
        
        print(f"🧪 Testing redirects on {endpoint_display}")
        
        for case in cases:
            path = case['path']
            expected = case['expected']
            
            if not test_redirect(protocol, host, port, path, expected):
                all_passed = False
        
        # Test 404 if enabled
        if test_404:
            if not test_404_error(protocol, host, port):
                all_passed = False
        
        print()
    
    return all_passed

def get_test_configs_for_host(test_configs, host, port_override=None):
    # Filter configurations based on host and port. 
    # Allows testing of specific ports for localhost, and specific hostnames for production.
    configs_to_test = []
    if host == local_host and port_override is None:
        configs_to_test = test_configs
    else:
        filter_key, filter_value = (
            ("port", port_override) if host == local_host else ("hostname", host)
        )
        configs_to_test = [
                cfg for cfg in test_configs
                if cfg.get(filter_key) == filter_value
            ]
    return configs_to_test
    
def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test redirect service functionality',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Test locally (uses port from test-cases.yaml)
  %(prog)s --host localhost
  
  # Test production hostname
  %(prog)s --host docs.developer.gov.bc.ca
  
  # Test specific local port
  %(prog)s --host localhost --port 2015
    '''
    )
    parser.add_argument(
        '--host',
        default=local_host,
        help=f'Host to test. Use "{local_host}" for local dev, or domain for production (default: {local_host})'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help=f'Optional port override for {local_host} testing. If not specified, will test all ports from test-cases.yaml. Ignored if including a hostname other than {local_host}.'
    )
    
    
    args = parser.parse_args()

    if args.host != local_host and args.port is not None:
        print(f"❌ Port override is not allowed for host '{args.host}'.")
        sys.exit(1)
    
    protocol = 'http' if args.host == local_host else 'https'
    
    script_dir = Path(__file__).parent
    yaml_file = script_dir / "test-cases.yaml"
    
    # Load test cases
    test_configs = load_test_cases(str(yaml_file))

    allowed_hosts.update(
        str(cfg['hostname']) for cfg in test_configs if isinstance(cfg.get('hostname'), str)
    )


    configs_to_test = get_test_configs_for_host(test_configs, args.host, args.port)

    if not configs_to_test:
        print(f"❌ No test configurations found for host '{args.host}'" + (f" and port '{args.port}'" if args.port else ""))
        sys.exit(1)

    print(f"Configuration: {protocol}://{args.host}" + (f":{args.port}" if args.port else ""))
    print()
    
    # Run tests
    if run_tests(protocol, args.host, configs_to_test, port_override=args.port):
        print("🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
