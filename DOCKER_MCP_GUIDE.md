# Docker MCP Deployment Guide

This guide covers deploying the Weather MCP Server using Docker for production and development environments.

## 🚀 Quick Start

### Basic MCP Server Deployment
```bash
# Build the container
docker build -t weather-mcp .

# Run MCP server (stdio mode)
docker run -it weather-mcp

# Run with custom environment
docker run -it \
  -e WEATHER_TIMEOUT=45 \
  -e WEATHER_CACHE_TTL=600 \
  weather-mcp
```

### Using Docker Compose
```bash
# Standard deployment
docker-compose up -d

# MCP-optimized deployment with monitoring
docker-compose -f docker-compose.mcp.yml up -d

# With monitoring profile
docker-compose -f docker-compose.mcp.yml --profile monitoring up -d
```

## 🐳 Container Modes

The Docker container supports multiple deployment modes via the `MCP_MODE` environment variable:

### MCP Mode (Default)
```bash
# Standard MCP server with stdio communication
docker run -it -e MCP_MODE=mcp weather-mcp
```

### HTTP Mode
```bash
# HTTP mode for debugging/testing
docker run -it -p 8000:8000 -e MCP_MODE=http weather-mcp
```

### Health Check Mode
```bash
# Run health check and exit
docker run --rm -e MCP_MODE=health weather-mcp
```

### Test Mode
```bash
# Run tests and exit
docker run --rm -e MCP_MODE=test weather-mcp
```

### Shell Mode
```bash
# Interactive shell for debugging
docker run -it -e MCP_MODE=shell weather-mcp
```

## ⚙️ Configuration

### Environment Variables
```bash
# Core settings
WEATHER_TIMEOUT=30                    # API timeout in seconds
WEATHER_MAX_RETRIES=3                # Maximum retry attempts
WEATHER_CACHE_TTL=300                # Cache TTL in seconds
WEATHER_RATE_LIMIT_PER_MINUTE=60     # Rate limiting

# Container mode
MCP_MODE=mcp                         # Container startup mode
```

### Volume Mounts
```bash
# Persistent logs
-v ./logs:/app/logs

# Cache persistence
-v weather-cache:/tmp/weather-cache

# Configuration override
-v ./config:/app/config
```

## 🔧 MCP Integration with Docker

### Claude Code MCP Configuration

Add to `~/.config/claude-code/mcp_servers.json`:

```json
{
  "mcpServers": {
    "weather-docker": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--name", "weather-mcp-instance",
        "weather-mcp"
      ]
    }
  }
}
```

### Alternative: Using Docker Compose
```json
{
  "mcpServers": {
    "weather-compose": {
      "command": "docker-compose",
      "args": [
        "run", "--rm", "weather-mcp"
      ],
      "cwd": "/path/to/mcp-server-weather-py"
    }
  }
}
```

## 📊 Production Deployment

### Resource Limits
```yaml
# docker-compose.mcp.yml includes resource limits
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

### Health Monitoring
```bash
# Check container health
docker-compose ps

# View health check logs
docker inspect weather-mcp-server --format='{{.State.Health.Status}}'

# Monitor resource usage
docker stats weather-mcp-server
```

### Log Management
```bash
# View container logs
docker-compose logs -f weather-mcp

# Log rotation with limits
docker run -it \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  weather-mcp
```

## 🔍 Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check build logs
docker build -t weather-mcp . --no-cache

# Run with verbose output
docker run -it -e MCP_MODE=shell weather-mcp
```

**MCP not connecting:**
```bash
# Test health check
docker run --rm -e MCP_MODE=health weather-mcp

# Check container logs
docker logs weather-mcp-server

# Verify MCP communication
docker run -it weather-mcp
# Then manually test MCP protocol
```

**Performance issues:**
```bash
# Monitor resource usage
docker stats weather-mcp-server

# Check cache performance
docker exec weather-mcp-server uv run python -c "from src.tools import health_check; import asyncio; print(asyncio.run(health_check()))"
```

### Debug Mode
```bash
# Run with debug logging
docker run -it \
  -e PYTHONUNBUFFERED=1 \
  -e WEATHER_LOG_LEVEL=DEBUG \
  weather-mcp
```

## 🚀 Advanced Deployments

### Multi-Container Setup
```bash
# Main MCP server + monitoring
docker-compose -f docker-compose.mcp.yml --profile monitoring up -d

# Check all services
docker-compose -f docker-compose.mcp.yml ps
```

### Container Registry
```bash
# Tag for registry
docker tag weather-mcp your-registry/weather-mcp:latest

# Push to registry
docker push your-registry/weather-mcp:latest

# Deploy from registry
docker run -it your-registry/weather-mcp:latest
```

### Kubernetes Deployment
```yaml
# Example Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weather-mcp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: weather-mcp
  template:
    metadata:
      labels:
        app: weather-mcp
    spec:
      containers:
      - name: weather-mcp
        image: weather-mcp:latest
        env:
        - name: WEATHER_TIMEOUT
          value: "30"
        - name: WEATHER_CACHE_TTL
          value: "300"
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
```

## 📈 Monitoring & Metrics

### Built-in Health Checks
- Container-level health checks every 30 seconds
- Application-level health monitoring
- Automatic restart on failure

### Optional Monitoring Stack
```bash
# Enable monitoring profile
docker-compose -f docker-compose.mcp.yml --profile monitoring up -d

# Access Prometheus metrics
curl http://localhost:9090
```

### Log Aggregation
```bash
# Enable logging profile
docker-compose -f docker-compose.mcp.yml --profile logging up -d

# Access Loki logs
curl http://localhost:3100
```

## 🔐 Security Considerations

### Non-root User
- Container runs as non-root `weather` user
- Minimal system dependencies
- No unnecessary privileges

### Network Security
- No exposed ports by default (MCP uses stdio)
- Optional HTTP mode only for debugging
- Isolated container networking

### Data Security
- No persistent sensitive data
- Environment-based configuration
- Secure API communication with NWS

---

**Docker MCP Deployment** - Containerized weather data for production MCP usage 🌤️
