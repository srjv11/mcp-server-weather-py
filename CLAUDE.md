# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that provides weather data from the National Weather Service (NWS) API to Large Language Models. The server exposes two main tools: weather alerts by state and weather forecasts by coordinates.

## Architecture

- **weather.py**: Main MCP server implementation using FastMCP framework
  - `get_alerts(state)`: Retrieves active weather alerts for a US state
  - `get_forecast(latitude, longitude)`: Gets detailed weather forecast for coordinates
  - Uses NWS API with proper error handling and rate limiting
- **main.py**: Basic entry point (currently just prints hello message)

## Development Commands

### Environment Management
- This project uses `uv` for dependency management
- Install dependencies: `uv sync`
- Run the MCP server: `python weather.py` or `uv run python weather.py`

### Code Quality
- **Linting and formatting**: `ruff check --fix && ruff format`
- **Pre-commit hooks**: `pre-commit run --all-files`
- The project uses Ruff for both linting and formatting (replaces Black)
- Pre-commit is configured to run uv-lock, ruff-check, ruff-format, and basic file checks

### Testing the MCP Server
- The server runs with stdio transport for MCP communication
- Test tools by running the server and sending MCP requests
- Example coordinates for testing: San Francisco (37.7749, -122.4194)
- Example state codes: CA, NY, TX, FL

## Key Implementation Details

### API Integration
- Uses National Weather Service API (api.weather.gov)
- Requires proper User-Agent header for API requests
- Implements retry logic and error handling for network requests
- Rate limiting handled by httpx AsyncClient with 30-second timeout

### MCP Tool Functions
- Both tools are async and return formatted strings
- Error handling returns user-friendly messages when API calls fail
- Forecast limited to next 5 periods to keep responses manageable
- Alert formatting includes event, area, severity, description, and instructions

### Dependencies
- **httpx**: Async HTTP client for NWS API calls
- **mcp[cli]**: FastMCP framework for MCP server implementation
- **pre-commit**: Git hooks for code quality
- **ruff**: Linting and formatting
- Requires Python >=3.13
