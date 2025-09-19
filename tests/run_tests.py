"""
Test runner script for local development.

This script allows developers to run tests locally before committing.
"""

import subprocess
import sys
import os


def run_command(command):
    """Run a command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False
    
    print(result.stdout)
    return True


def main():
    """Main test runner function."""
    print("🧪 Running Jira Issue Action Test Suite")
    print("=" * 50)
    
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    # Install test dependencies
    print("📦 Installing test dependencies...")
    if not run_command("pip install pytest pytest-cov pytest-mock responses"):
        sys.exit(1)
    
    # Install project dependencies
    print("📦 Installing project dependencies...")
    if not run_command("pip install -r requirements.txt"):
        sys.exit(1)
    
    # Run tests with coverage
    print("🔍 Running tests with coverage...")
    test_command = "python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html"
    if not run_command(test_command):
        print("❌ Tests failed!")
        sys.exit(1)
    
    print("✅ All tests passed!")
    print("📊 Coverage report generated in htmlcov/index.html")


if __name__ == "__main__":
    main()