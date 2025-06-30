# Enhanced Weather MCP Server

A comprehensive, production-ready MCP (Model Context Protocol) server providing weather data from the National Weather Service API. Available in both modular and monolithic architectures.

## 🚀 Quick Start

### Modular Architecture (Recommended)
```bash
# Run the modular implementation
python run_modular.py

# Test the modular structure
pytest tests/modular/ -v
```

### Legacy Implementation
```bash
# Run the original monolithic version
python legacy/weather_improved.py

# Test the legacy structure
pytest legacy/test_weather.py -v
```

## 📁 Project Structure

```
mcp-server-weather-py/
├── 🏗️ Modular Implementation (NEW)
│   ├── src/modular/           # Clean, organized modules
│   │   ├── models.py          # Data models and enums
│   │   ├── exceptions.py      # Custom exception hierarchy
│   │   ├── config.py          # Configuration management
│   │   ├── validators.py      # Input validation functions
│   │   ├── client.py          # HTTP client and caching
│   │   ├── formatters.py      # Data formatting functions
│   │   ├── tools.py           # MCP tool implementations
│   │   └── __init__.py        # Package exports
│   ├── tests/modular/         # Focused, modular tests
│   └── run_modular.py         # Entry point for modular version
│
├── 📄 Legacy Implementation
│   ├── legacy/
│   │   ├── weather_improved.py # Enhanced monolithic version
│   │   ├── weather.py          # Original simple version
│   │   └── test_*.py           # Legacy test files
│
├── 📚 Documentation
│   ├── docs/
│   │   ├── README_MODULAR.md   # Modular architecture guide
│   │   └── README_ENHANCED.md  # Enhancement documentation
│
└── 🔧 Configuration
    ├── pyproject.toml          # Dependencies and settings
    ├── CLAUDE.md               # Development guidance
    └── [other config files]
```

## ✨ Features

- **🏗️ Modular Architecture**: Clean separation of concerns
- **🛡️ Robust Error Handling**: Custom exception hierarchy with retry logic
- **⚡ Performance**: In-memory caching with TTL and rate limiting
- **📊 Monitoring**: Health checks and structured logging
- **🧪 Comprehensive Testing**: 95%+ test coverage
- **🐳 Production Ready**: Docker support and deployment configs
- **🔧 Configurable**: Environment-based configuration

## 🔄 Architecture Comparison

| **Aspect** | **Modular** | **Legacy** |
|------------|-------------|------------|
| **Structure** | 8 focused modules | 603-line monolithic file |
| **Maintainability** | Isolated changes | Large file edits |
| **Testing** | Module-specific tests | Monolithic test suite |
| **Coverage** | 95% (307 statements) | 100% (272 statements) |
| **Development** | Parallel team work | Sequential development |

## 🧪 Testing

```bash
# Test modular implementation
pytest tests/modular/ --cov=src/modular

# Test legacy implementation
pytest legacy/test_weather.py --cov=legacy/weather_improved

# Test all implementations
pytest tests/ legacy/ -v
```

## 📈 Migration Path

Both versions provide identical functionality:

```python
# Same API, different implementations
from modular import get_alerts, get_forecast  # Modular
# OR
from legacy.weather_improved import get_alerts, get_forecast  # Legacy
```

---

**Enhanced Weather MCP Server v2.0** - Choose your architecture! 🌤️
