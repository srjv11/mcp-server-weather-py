#!/bin/bash
set -e

# MCP Server Docker Entrypoint Script
# Provides flexible startup options for different MCP deployment scenarios

# Default to MCP mode unless specified otherwise
MODE="${MCP_MODE:-mcp}"

echo "Starting Weather MCP Server in mode: $MODE"

case "$MODE" in
    "mcp")
        # Standard MCP server mode (stdio communication)
        echo "Starting MCP server with stdio communication..."
        exec uv run weather-mcp
        ;;
    "http")
        # HTTP mode for debugging/testing
        echo "Starting MCP server in HTTP mode..."
        exec uv run python -m src.main --http
        ;;
    "health")
        # Health check mode
        echo "Running health check..."
        uv run python -c "import asyncio; from src.tools import health_check; print(asyncio.run(health_check()))"
        ;;
    "test")
        # Test mode - run tests and exit
        echo "Running tests..."
        exec uv run pytest tests/ -v
        ;;
    "shell")
        # Interactive shell for debugging
        echo "Starting interactive shell..."
        exec /bin/bash
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo "Available modes: mcp, http, health, test, shell"
        exit 1
        ;;
esac
