# Installation Guide

Complete installation instructions for the Weather MCP Server.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.13 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 256MB RAM
- **Network**: Internet connection for NWS API access

### Required Tools
- **uv**: Modern Python package manager (recommended)
- **Git**: For cloning the repository
- **Docker**: Optional, for containerized deployment

## 🚀 Installation Methods

### Method 1: Using uv (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/srjv11/mcp-server-weather-py.git
cd mcp-server-weather-py

# 2. Install dependencies
uv sync --group dev

# 3. Install in editable mode
uv pip install -e .

# 4. Verify installation
uv run weather-mcp --help
```

### Method 2: Using pip

```bash
# 1. Clone the repository
git clone https://github.com/srjv11/mcp-server-weather-py.git
cd mcp-server-weather-py

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e .

# 4. Verify installation
weather-mcp --help
```

### Method 3: Docker Installation

```bash
# 1. Clone the repository
git clone https://github.com/srjv11/mcp-server-weather-py.git
cd mcp-server-weather-py

# 2. Build Docker image
docker build -t weather-mcp .

# 3. Run container
docker run -it weather-mcp

# 4. Or use docker-compose
docker-compose up -d
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Settings
WEATHER_TIMEOUT=30
WEATHER_MAX_RETRIES=3
WEATHER_CACHE_TTL=300

# Performance
WEATHER_RATE_LIMIT_PER_MINUTE=60

# Logging (optional)
WEATHER_LOG_LEVEL=INFO
```

### Configuration File

Alternatively, modify settings in `src/config.py`:

```python
class WeatherConfig:
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    CACHE_TTL: int = 300
    RATE_LIMIT_PER_MINUTE: int = 60
```

## 🧪 Verification

### Run Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Check specific functionality
uv run pytest tests/test_tools.py -v
```

### Health Check

```bash
# Test MCP server health
uv run python -c "
import asyncio
from src.tools import health_check
print(asyncio.run(health_check()))
"
```

### Test API Connection

```bash
# Test weather data retrieval
uv run python -c "
import asyncio
from src.tools import get_forecast
print(asyncio.run(get_forecast(37.7749, -122.4194)))
"
```

## 🔧 Development Setup

### Additional Dependencies

```bash
# Install development dependencies
uv sync --group dev

# Install pre-commit hooks
pre-commit install
```

### Code Quality Tools

```bash
# Run linting
ruff check --fix
ruff format

# Run type checking
mypy src/ --ignore-missing-imports
```

## 🐳 Docker Development

### Build Development Image

```bash
# Build with development dependencies
docker build -t weather-mcp-dev --target development .

# Run with volume mount for development
docker run -it -v $(pwd):/app weather-mcp-dev
```

### Docker Compose Development

```bash
# Use development configuration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 🔗 MCP Integration Setup

After installation, configure for Claude Code:

1. **Create MCP configuration file**:
   ```bash
   mkdir -p ~/.config/claude-code
   ```

2. **Add server configuration**:
   ```json
   {
     "mcpServers": {
       "weather": {
         "command": "uv",
         "args": ["run", "weather-mcp"],
         "cwd": "/path/to/mcp-server-weather-py"
       }
     }
   }
   ```

3. **Restart Claude Code** to load the MCP server

For detailed MCP setup, see [[MCP Integration]].

## 🚨 Troubleshooting

### Common Issues

**Installation fails with uv**:
```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or using pip
pip install uv
```

**Module not found errors**:
```bash
# Ensure proper installation
uv pip install -e .
# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**API connection issues**:
```bash
# Test network connectivity
curl -I https://api.weather.gov/alerts
# Check firewall/proxy settings
```

**Permission errors on Docker**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Or run with sudo
sudo docker run -it weather-mcp
```

### Getting Help

- Check [[Troubleshooting]] for detailed solutions
- Review [GitHub Issues](https://github.com/srjv11/mcp-server-weather-py/issues)
- Ask in [Discussions](https://github.com/srjv11/mcp-server-weather-py/discussions)

## ✅ Next Steps

After successful installation:

1. **Configure environment** - Set up [[Configuration]]
2. **Integrate with Claude Code** - Follow [[MCP Integration]]
3. **Explore examples** - Check [[Examples and Tutorials]]
4. **Deploy to production** - See [[Docker Deployment]]

---

[[Home]] | [[Configuration]] | [[MCP Integration]]
