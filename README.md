# Weather MCP Server

[![Build Status](https://github.com/raghu/mcp-server-weather-py/workflows/PR%20Tests/badge.svg)](https://github.com/raghu/mcp-server-weather-py/actions)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com/raghu/mcp-server-weather-py)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://hub.docker.com/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green)](https://modelcontextprotocol.io/)

A comprehensive, production-ready MCP (Model Context Protocol) server providing weather data from the National Weather Service API with caching, monitoring, robust error handling, and comprehensive testing.

## 🚀 Quick Start

```bash
# Install dependencies
uv sync --group dev

# Run the weather MCP server
uv run weather-mcp
# or
uv run -m src.main

# Run tests
uv run pytest tests/ -v

# Run code quality checks
ruff check --fix && ruff format
```

## 📁 Project Structure

```
mcp-server-weather-py/
├── 📄 Core Application
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
│   └── docs/README_ENHANCED.md  # Detailed enhancement documentation
│
└── 📄 Examples & Utilities
    ├── examples.py              # Usage examples & demos
    ├── example_state_machine.py # Educational state machine example
    └── setup_script.py          # Setup automation script
```

## ✨ Features

- **🛡️ Robust Error Handling**: Custom exception hierarchy with retry logic
- **⚡ Performance**: In-memory caching with TTL and rate limiting
- **📊 Monitoring**: Health checks and structured logging
- **🧪 Comprehensive Testing**: 95%+ test coverage across 8 modules
- **🐳 Production Ready**: Docker support and deployment configs
- **🔧 Configurable**: Environment-based configuration
- **🌐 MCP Integration**: Ready for Claude Code integration

## 🛠️ API Reference

### Core MCP Tools

- **`get_alerts(state, severity_filter=None)`**: Get weather alerts with optional severity filtering
- **`get_forecast(latitude, longitude)`**: Get weather forecast for specific coordinates
- **`get_location_forecast(city, state)`**: Get weather forecast by city and state
- **`health_check()`**: Check server health and performance metrics

## 🧪 Testing

```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=. --cov-report=html

# Run specific test modules
uv run pytest tests/test_validators.py -v
uv run pytest tests/test_tools.py -v
```

**Test Coverage**: 46 tests across 8 modules covering validation, data models, HTTP client, MCP tools, formatting, exceptions, and configuration.

## 🐳 Deployment

### Local Development
```bash
uv sync --group dev
uv run weather-mcp
```

### Docker Deployment
```bash
docker build -t weather-mcp .
docker run -it weather-mcp
```

### Production with Docker Compose
```bash
docker-compose up -d
```

## 🔗 MCP Integration

Connect to Claude Code for interactive weather queries. See **MCP_SETUP.md** for complete setup instructions.

## 📚 Documentation

- **CLAUDE.md**: Comprehensive development guide with commands and architecture details
- **MCP_SETUP.md**: Claude Code integration instructions
- **docs/README_ENHANCED.md**: Detailed feature documentation and examples
- **examples.py**: Interactive usage demonstrations

---

**Weather MCP Server** - Production-ready weather data for Large Language Models 🌤️
