# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive MCP (Model Context Protocol) server that provides weather data from the National Weather Service (NWS) API to Large Language Models. The server includes caching, monitoring, robust error handling, and comprehensive testing.

## Architecture

### Core Files
- **main.py**: MCP server implementation with full feature set
  - `get_alerts(state, severity_filter)`: Retrieves active weather alerts with optional filtering
  - `get_forecast(latitude, longitude)`: Gets detailed weather forecast with location info
  - `get_location_forecast(city, state)`: Placeholder for geocoding functionality
  - `health_check()`: Service health monitoring endpoint
- **weather.py**: Alternative entry point
- **main.py**: Basic entry point (legacy)

### New Enhancement Files
- **test_weather.py**: Comprehensive test suite with unit and integration tests
- **monitoring.py**: Advanced metrics collection and monitoring system
- **Dockerfile**: Container configuration for deployment
- **docker-compose.yml**: Multi-service orchestration
- **.dockerignore**: Container build optimization

## Development Commands

### Environment Management
- This project uses `uv` for dependency management
- Install dependencies: `uv sync`
- Install dev dependencies: `uv sync --group dev`

### Running the Server
The app is now properly packaged and can be run in multiple ways:

**Using uv (recommended):**
- `uv run weather-mcp` - Run via script entry point
- `uv run -m src.main` - Run as module

**After installation:**
- `uv pip install -e .` - Install in editable mode
- `weather-mcp` - Run installed script

### Code Quality & Testing
- **Linting and formatting**: `ruff check --fix && ruff format`
- **Pre-commit hooks**: `pre-commit run --all-files`
- **Run tests**: `uv run pytest tests/ -v`
- **Test with coverage**: `uv run pytest --cov=. --cov-report=html`
- **Type checking**: `mypy src/ --ignore-missing-imports`

### Docker Deployment
- **Build container**: `docker build -t weather-mcp .`
- **Run container**: `docker run -it weather-mcp`
- **Use docker-compose**: `docker-compose up -d`
- **Health check**: `docker-compose ps` to see health status

### Environment Variables
Configure the service using these environment variables:
- `WEATHER_TIMEOUT`: Request timeout in seconds (default: 30)
- `WEATHER_MAX_RETRIES`: Maximum retry attempts (default: 3)
- `WEATHER_CACHE_TTL`: Cache TTL in seconds (default: 300)

## Key Features

### Error Handling & Resilience
- **Custom Exception Types**: `ValidationError`, `RateLimitError`, `APIUnavailableError`
- **Retry Logic**: Exponential backoff with configurable max retries
- **Input Validation**: Comprehensive validation for state codes and coordinates
- **Graceful Degradation**: Meaningful error messages for all failure scenarios

### Performance & Caching
- **In-Memory Caching**: TTL-based caching with automatic cleanup
- **Connection Pooling**: Reusable HTTP client with proper lifecycle management
- **Rate Limiting**: Configurable rate limiting to prevent API abuse
- **Response Optimization**: Structured data models for efficient processing

### Monitoring & Observability
- **Structured Logging**: Comprehensive logging with proper levels
- **Metrics Collection**: Request counts, response times, success rates
- **Health Monitoring**: Built-in health check endpoint
- **Prometheus Integration**: Metrics export in Prometheus format
- **Performance Tracking**: Per-endpoint performance metrics

### Core Functionality
- **Alert Filtering**: Filter alerts by severity level
- **Rich Formatting**: Emoji-enhanced, user-friendly output
- **Location Context**: City/state information in forecasts
- **Extended Validation**: Comprehensive input sanitization

### Security Features
- **Input Sanitization**: Protection against injection attacks
- **Rate Limiting**: DoS protection with configurable limits
- **Non-root Container**: Security-hardened Docker configuration
- **Environment-based Config**: Secure configuration management

## API Reference

### MCP Tools

#### get_alerts(state, severity_filter=None)
- **Purpose**: Get weather alerts with optional severity filtering
- **Parameters**:
  - `state`: Two-letter US state/territory code (validated against official list)
  - `severity_filter`: Optional filter ("Extreme", "Severe", "Moderate", "Minor")
- **Returns**: Formatted alert information with emojis and structured layout
- **Validation**: Comprehensive state code validation with helpful error messages

#### get_forecast(latitude, longitude)
- **Purpose**: Get detailed weather forecast with location context
- **Parameters**:
  - `latitude`: Latitude (-90 to 90, validated)
  - `longitude`: Longitude (-180 to 180, validated)
- **Returns**: Rich forecast with location info, emojis, and structured periods
- **Features**: Automatic city/state resolution, error handling for invalid locations

#### health_check()
- **Purpose**: Monitor service health and performance
- **Returns**: Comprehensive health status with metrics
- **Includes**: Response times, cache statistics, API connectivity status

## Testing Strategy

### Test Coverage
- **Unit Tests**: Individual function testing with mocks
- **Integration Tests**: Full workflow testing with API simulation
- **Error Scenario Tests**: Comprehensive error condition coverage
- **Performance Tests**: Caching, rate limiting, and timeout validation

### Test Categories
- **Validation Tests**: Input validation and sanitization
- **Data Model Tests**: Data structure and formatting
- **Client Tests**: HTTP client behavior and retry logic
- **MCP Tool Tests**: End-to-end tool functionality
- **Monitoring Tests**: Metrics collection and health checks

### Running Tests
```bash
# Basic test run
pytest

# Verbose output with coverage
pytest -v --cov=. --cov-report=html

# Specific test categories
pytest test_weather.py::TestValidation -v
pytest test_weather.py::TestWeatherClient -v
```

## Deployment Options

### Local Development
```bash
# Install and run locally
uv sync --group dev
python weather_improved.py
```

### Docker Deployment
```bash
# Build and run container
docker build -t weather-mcp .
docker run -it -e WEATHER_TIMEOUT=45 weather-mcp
```

### Production Deployment
```bash
# Use docker-compose for production
docker-compose up -d
docker-compose logs -f weather-mcp
```

## Configuration Management

### Default Configuration
- API Base: `https://api.weather.gov`
- Timeout: 30 seconds
- Max Retries: 3
- Cache TTL: 5 minutes
- Rate Limit: 60 requests/minute

### Environment Override
All configuration can be overridden via environment variables for different deployment environments.

## Monitoring & Metrics

### Available Metrics
- Request counts and success rates
- Response time statistics
- Cache hit/miss ratios
- Rate limiting statistics
- Service uptime and health

### Metrics Export
- JSON format for programmatic access
- Prometheus format for monitoring systems
- Structured logging for log aggregation systems

## Dependencies

### Core Dependencies
- **httpx**: Async HTTP client with timeout and retry support
- **mcp[cli]**: FastMCP framework for MCP server implementation
- **pre-commit**: Git hooks for code quality
- **ruff**: Modern Python linting and formatting

### Development Dependencies
- **pytest**: Testing framework with async support
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Advanced mocking capabilities

### System Requirements
- Python >=3.13
- Docker (optional, for containerized deployment)
- uv (recommended for dependency management)
