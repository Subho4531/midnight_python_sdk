#!/usr/bin/env python3
"""
Test runner for comprehensive CLI route testing.
Provides different test execution modes and reporting options.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False, output_file=None):
    """Run CLI tests with specified options"""
    
    cmd = ["python", "-m", "pytest", "test_complete_cli_routes.py"]
    
    # Add verbosity
    if verbose:
        cmd.extend(["-v", "-s"])
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=midnight_sdk.cli", "--cov-report=html", "--cov-report=term"])
    
    # Filter by test type
    if test_type == "unit":
        cmd.extend(["-k", "not integration and not slow"])
    elif test_type == "integration":
        cmd.extend(["-k", "integration"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    elif test_type == "wallet":
        cmd.extend(["-k", "wallet"])
    elif test_type == "config":
        cmd.extend(["-k", "config"])
    elif test_type == "contract":
        cmd.extend(["-k", "contract"])
    elif test_type == "transfer":
        cmd.extend(["-k", "transfer"])
    elif test_type == "system":
        cmd.extend(["-k", "system"])
    
    # Output to file if specified
    if output_file:
        cmd.extend(["--junitxml", output_file])
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run Midnight CLI comprehensive tests")
    
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "fast", "wallet", "config", "contract", "transfer", "system"],
        default="all",
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true", 
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output test results to XML file"
    )
    
    parser.add_argument(
        "--list-tests", "-l",
        action="store_true",
        help="List all available tests without running them"
    )
    
    args = parser.parse_args()
    
    if args.list_tests:
        # List all tests
        cmd = ["python", "-m", "pytest", "test_complete_cli_routes.py", "--collect-only", "-q"]
        subprocess.run(cmd)
        return 0
    
    return run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage,
        output_file=args.output
    )


if __name__ == "__main__":
    sys.exit(main())