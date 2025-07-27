#!/usr/bin/env python
"""
Test runner script with coverage reporting.

Usage:
    python -m scripts.run_tests [--cov] [--html] [--xml] [--verbose]
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Ensure we're running from the project root
project_root = Path(__file__).parent.parent


def run_tests(coverage=False, html=False, xml=False, verbose=False):
    """Run tests with optional coverage reporting.
    
    Args:
        coverage: Whether to run with coverage reporting
        html: Whether to generate HTML coverage report
        xml: Whether to generate XML coverage report
        verbose: Whether to run in verbose mode
    
    Returns:
        Exit code from pytest
    """
    cmd = [sys.executable, "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app"])
        
        if html:
            cmd.extend(["--cov-report=html"])
        
        if xml:
            cmd.extend(["--cov-report=xml"])
            
        if not html and not xml:
            cmd.extend(["--cov-report=term-missing"])
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests with coverage reporting")
    parser.add_argument(
        "--cov", 
        action="store_true", 
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--html", 
        action="store_true", 
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--xml", 
        action="store_true", 
        help="Generate XML coverage report"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Run in verbose mode"
    )
    
    args = parser.parse_args()
    
    exit_code = run_tests(
        coverage=args.cov or args.html or args.xml,
        html=args.html,
        xml=args.xml,
        verbose=args.verbose
    )
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
        if args.cov or args.html or args.xml:
            if args.html:
                print("\nHTML coverage report generated in htmlcov/index.html")
            if args.xml:
                print("\nXML coverage report generated in coverage.xml")
    else:
        print("\n❌ Tests failed!")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()