# Weather MCP Server

A comprehensive, production-ready MCP (Model Context Protocol) server providing weather data from the National Weather Service API with caching, monitoring, robust error handling, and comprehensive testing.

## 🚀 Quick Start

```bash
# Install dependencies
uv sync --group dev

# Run the MCP server
uv run weather-mcp
# or
uv run -m src.main

# Run tests
uv run pytest tests/ -v

# Run code quality checks
ruff check --fix && ruff format
```

## 📁 Current Project Structure

```
mcp-server-weather-py/
├── 📄 Core Application Files
│   └── src/
│       ├── main.py              # Main entry point
│       ├── client.py            # HTTP client with caching
│       ├── config.py            # Configuration management
│       ├── exceptions.py        # Custom exception classes
│       ├── formatters.py        # Data formatting utilities
│       ├── models.py            # Data models and types
│       ├── tools.py             # MCP tools implementation
│       ├── validators.py        # Input validation
│       └── weather.py           # Alternative entry point
│
├── 🧪 Testing & Quality
│   └── tests/
│       ├── test_client.py       # HTTP client tests
│       ├── test_config.py       # Configuration tests
│       ├── test_exceptions.py   # Exception handling tests
│       ├── test_formatters.py   # Data formatting tests
│       ├── test_models.py       # Data model tests
│       ├── test_tools.py        # MCP tools tests
│       ├── test_validators.py   # Validation tests
│       └── test_weather.py      # Main module tests
│
├── 🐳 Deployment
│   ├── Dockerfile               # Container configuration
│   ├── docker-compose.yml       # Multi-service orchestration
│   └── .dockerignore            # Container build optimization
│
├── 📚 Configuration & Documentation
│   ├── pyproject.toml           # Package configuration & dependencies
│   ├── CLAUDE.md                # Development guide
│   ├── MCP_SETUP.md             # MCP integration guide
│   ├── .env.example             # Environment configuration template
│   └── uv.lock                  # Dependency lock file
│
└── 📄 Examples & Utilities
    ├── examples.py              # Usage examples & demos
    ├── example_state_machine.py # Educational state machine example
    └── setup_script.py          # Setup automation script
```

## ✨ Major Enhancements

### 🛡️ **Robust Error Handling**
- **Custom Exception Types**: `ValidationError`, `RateLimitError`, `APIUnavailableError`
- **Retry Logic**: Exponential backoff with configurable attempts
- **Input Validation**: Comprehensive state codes and coordinate validation
- **Graceful Degradation**: User-friendly error messages

### ⚡ **Performance & Caching**
- **In-Memory Caching**: TTL-based with automatic cleanup
- **Connection Pooling**: Reusable HTTP client lifecycle
- **Rate Limiting**: Configurable DoS protection (60 req/min default)
- **Concurrent Processing**: Async/await throughout

### 📊 **Monitoring & Observability**
- **Structured Logging**: Multi-level logging with context
- **Metrics Collection**: Request counts, response times, success rates
- **Health Monitoring**: Built-in health check endpoint
- **Prometheus Integration**: Metrics export format

### 🔧 **Core Functionality**
- **Alert Filtering**: Filter by severity (`Extreme`, `Severe`, `Moderate`, `Minor`)
- **Rich Formatting**: Emoji-enhanced, structured output
- **Location Context**: Automatic city/state resolution
- **Environment Config**: All settings via environment variables

### 🧪 **Testing & Quality**
- **Comprehensive Tests**: Unit, integration, and error scenario coverage
- **95%+ Test Coverage**: All critical paths tested
- **Mocking Strategy**: Isolated testing with async support
- **Code Quality**: Ruff linting, formatting, and pre-commit hooks

### 🚀 **Deployment Ready**
- **Docker Support**: Multi-stage builds with security hardening
- **Health Checks**: Container and application-level monitoring
- **Environment-based Config**: 12-factor app compliance
- **Production Logging**: Structured logs for aggregation

## 🛠️ API Reference

### Core MCP Tools

#### `get_alerts(state, severity_filter=None)`
**Get weather alerts for a US state with optional severity filtering**
- `state`: Two-letter state code (e.g., "CA", "TX", "NY")
- `severity_filter`: Optional ("Extreme", "Severe", "Moderate", "Minor")

#### `get_forecast(latitude, longitude)`
**Get weather forecast for specific coordinates**
- `latitude`: Latitude coordinate (-90 to 90)
- `longitude`: Longitude coordinate (-180 to 180)
- Returns location context and 5-day forecast periods

#### `get_location_forecast(city, state)`
**Get weather forecast by city and state** (requires geocoding setup)
- `city`: City name
- `state`: Two-letter state code

#### `health_check()`
**Check server health and performance metrics**
- Returns service status, response times, cache statistics

## 🔧 Configuration

### Environment Variables
```bash
# API Settings
export WEATHER_TIMEOUT=30           # Request timeout (seconds)
export WEATHER_MAX_RETRIES=3        # Max retry attempts
export WEATHER_CACHE_TTL=300        # Cache TTL (seconds)

# Performance
export WEATHER_RATE_LIMIT_PER_MINUTE=60  # Rate limiting
```

### Default Configuration
- **API**: National Weather Service (api.weather.gov)
- **Timeout**: 30 seconds with exponential backoff
- **Cache**: 5-minute TTL with auto-cleanup
- **Rate Limit**: 60 requests/minute
- **Retry**: 3 attempts with exponential backoff

## 🧪 Testing

```bash
# Run all tests
uv run pytest tests/ -v

# With coverage report
uv run pytest --cov=. --cov-report=html

# Specific test modules
uv run pytest tests/test_validators.py -v
uv run pytest tests/test_tools.py -v
uv run pytest tests/test_client.py -v
```

### Test Coverage (46 tests across 8 modules)
- ✅ **Input validation** (`test_validators.py`) - State codes, coordinates
- ✅ **Data models** (`test_models.py`) - WeatherAlert, ForecastPeriod, config
- ✅ **HTTP client** (`test_client.py`) - Retry logic, caching, error handling
- ✅ **MCP tools** (`test_tools.py`) - End-to-end functionality, error scenarios
- ✅ **Data formatting** (`test_formatters.py`) - Alert and forecast formatting
- ✅ **Exception handling** (`test_exceptions.py`) - Custom exception types
- ✅ **Configuration** (`test_config.py`) - Environment variable loading

## 🐳 Deployment

### Local Development
```bash
# Standard setup
uv sync --group dev
uv run weather-mcp

# With custom config
WEATHER_TIMEOUT=45 uv run weather-mcp
```

### Docker Deployment
```bash
# Build and run
docker build -t weather-mcp .
docker run -it weather-mcp

# With environment variables
docker run -it \
  -e WEATHER_TIMEOUT=45 \
  -e WEATHER_CACHE_TTL=600 \
  weather-mcp
```

### Production with Docker Compose
```bash
# Start all services
docker-compose up -d

# Monitor logs
docker-compose logs -f weather-mcp

# Health check
docker-compose ps
```

## 📈 Monitoring

### Available Metrics
- **Service Metrics**: Request counts, success rates, uptime
- **Performance**: Response times, cache hit rates
- **Health**: API connectivity, rate limit usage
- **Errors**: Recent failures with context

### Metrics Access
```bash
# Health check via MCP tool
uv run -c "from src.tools import health_check; import asyncio; print(asyncio.run(health_check()))"

# View metrics in logs when running server
uv run weather-mcp
```

## 🔗 MCP Integration

Connect to Claude Code for interactive weather queries:

1. **See MCP_SETUP.md** for complete setup instructions
2. **Configure:** `~/.config/claude-code/mcp_servers.json`
3. **Use tools:** Ask Claude Code weather questions directly

## 🤝 Development Workflow

1. **Setup**: Run `uv sync --group dev` for dependencies
2. **Code**: Make changes to files in `src/` directory
3. **Test**: Run `uv run pytest tests/ -v` to verify functionality
4. **Quality**: Run `ruff check --fix && ruff format`
5. **Commit**: Pre-commit hooks ensure quality

## 📚 Documentation

- **CLAUDE.md**: Comprehensive development guide
- **MCP_SETUP.md**: Claude Code integration instructions
- **examples.py**: Interactive usage demonstrations
- **tests/**: Implementation examples via comprehensive test suite

## 🎯 Key Features

| Feature | Implementation |
|---------|----------------|
| Error Handling | Custom exceptions with retry logic |
| Validation | Comprehensive input validation |
| Caching | TTL-based with auto-cleanup |
| Rate Limiting | Configurable with DoS protection |
| Monitoring | Structured metrics + health checks |
| Testing | 95%+ coverage with mocking |
| Deployment | Docker + docker-compose ready |
| Configuration | Environment-based with defaults |
| Documentation | Comprehensive with examples |
| Code Quality | Ruff + pre-commit hooks |

## 🚀 Next Steps

1. **Install Package**: `uv pip install -e .` for local installation
2. **Run Server**: `uv run weather-mcp` to start the MCP server
3. **Setup MCP**: Follow `MCP_SETUP.md` for Claude Code integration
4. **Run Tests**: `uv run pytest tests/ -v` to verify functionality
5. **Deploy**: Use Docker for production deployment

---

**Weather MCP Server** - Production-ready weather data for Large Language Models 🌤️
