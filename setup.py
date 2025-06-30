#!/usr/bin/env python3
"""
Setup script for the Enhanced Weather MCP Server

This script helps with initial setup, dependency installation,
and basic validation of the enhanced weather MCP server.
"""

import asyncio
import subprocess
import sys


def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status"""
    print(f"🔄 {description}...")
    try:
        subprocess.run(command.split(), capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"⚠️  Command not found: {command.split()[0]}")
        return False


def check_python_version():
    """Check if Python version meets requirements"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 13:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is supported")
        return True
    else:
        print(
            f"❌ Python {version.major}.{version.minor}.{version.micro} is not supported"
        )
        print("   Requires Python >= 3.13")
        return False


def check_uv_installation():
    """Check if uv is installed"""
    print("📦 Checking UV installation...")
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ UV found: {result.stdout.strip()}")
            return True
        else:
            print("❌ UV not found or not working")
            return False
    except FileNotFoundError:
        print("❌ UV not found")
        print("   Install with: pip install uv")
        return False


def install_dependencies():
    """Install project dependencies"""
    commands = [
        ("uv sync", "Installing core dependencies"),
        ("uv sync --group dev", "Installing development dependencies"),
    ]

    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False

    return success


def run_code_quality_checks():
    """Run code quality and formatting checks"""
    print("\n🔍 Running code quality checks...")

    commands = [
        ("ruff check weather_improved.py", "Running ruff linting"),
        ("ruff format --check weather_improved.py", "Checking code formatting"),
    ]

    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False

    return success


def run_tests():
    """Run the test suite"""
    print("\n🧪 Running tests...")

    # First check if pytest is available
    try:
        __import__("pytest")
        print("✅ pytest is available")
    except ImportError:
        print("⚠️  pytest not found, skipping tests")
        return True

    commands = [
        ("pytest test_weather.py -v", "Running test suite"),
    ]

    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False

    return success


async def test_basic_functionality():
    """Test basic server functionality"""
    print("\n🌤️  Testing basic functionality...")

    try:
        # Import and test basic functions
        from weather_improved import (
            health_check,
            validate_coordinates,
            validate_state_code,
        )

        # Test validation functions
        print("   Testing input validation...")
        assert validate_state_code("ca") == "CA"
        assert validate_coordinates(37.7749, -122.4194) == (37.7749, -122.4194)
        print("   ✅ Input validation works")

        # Test health check
        print("   Testing health check...")
        health_result = await health_check()
        assert "Weather Service Health Check" in health_result
        print("   ✅ Health check works")

        print("✅ Basic functionality test passed")
        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def create_example_env_file():
    """Create example environment file"""
    print("\n📄 Creating example environment file...")

    env_content = """# Enhanced Weather MCP Server Configuration
# Copy this file to .env and modify as needed

# API Configuration
WEATHER_TIMEOUT=30
WEATHER_MAX_RETRIES=3
WEATHER_CACHE_TTL=300

# Rate Limiting
WEATHER_RATE_LIMIT_PER_MINUTE=60

# Logging
WEATHER_LOG_LEVEL=INFO

# Example usage:
# export WEATHER_TIMEOUT=45
# export WEATHER_CACHE_TTL=600
"""

    try:
        with open(".env.example", "w") as f:
            f.write(env_content)
        print("✅ Created .env.example file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env.example: {e}")
        return False


def print_usage_info():
    """Print usage information"""
    print("\n" + "=" * 60)
    print("🚀 SETUP COMPLETE! Here's how to use the weather MCP server:")
    print("=" * 60)

    print("\n📋 Quick Start:")
    print("   python weather_improved.py          # Run enhanced server")
    print("   python weather.py                   # Run original server")
    print("   python examples.py                  # Run example demonstrations")

    print("\n🧪 Testing:")
    print("   pytest                              # Run all tests")
    print("   pytest -v --cov=.                  # Run tests with coverage")

    print("\n🔍 Code Quality:")
    print("   ruff check --fix                    # Fix linting issues")
    print("   ruff format                         # Format code")
    print("   pre-commit run --all-files          # Run pre-commit hooks")

    print("\n🐳 Docker:")
    print("   docker build -t weather-mcp .       # Build container")
    print("   docker-compose up -d                # Run with docker-compose")

    print("\n📖 Documentation:")
    print("   See CLAUDE.md for comprehensive documentation")
    print("   See examples.py for usage examples")


async def main():
    """Main setup function"""
    print("🌤️  Enhanced Weather MCP Server - Setup Script")
    print("=" * 60)

    # Track overall success
    all_success = True

    # Check prerequisites
    if not check_python_version():
        all_success = False

    if not check_uv_installation():
        all_success = False
        print("\n💡 To install UV:")
        print("   pip install uv")
        print("   # or")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")

    if not all_success:
        print("\n❌ Prerequisites not met. Please install required tools.")
        return False

    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Dependency installation had issues, but continuing...")

    # Run code quality checks
    if not run_code_quality_checks():
        print("\n⚠️  Code quality checks had issues, but continuing...")

    # Run tests
    if not run_tests():
        print("\n⚠️  Tests had issues, but continuing...")

    # Test basic functionality
    if not await test_basic_functionality():
        print("\n⚠️  Basic functionality test failed, but continuing...")

    # Create example files
    create_example_env_file()

    # Print usage info
    print_usage_info()

    print("\n🎉 Setup process completed!")
    return True


if __name__ == "__main__":
    asyncio.run(main())
