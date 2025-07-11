# Use Python 3.13 slim image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash weather

# Set work directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code and entrypoint
COPY src/ ./src/
COPY pyproject.toml ./
COPY CLAUDE.md ./
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Change ownership to non-root user
RUN chown -R weather:weather /app

# Switch to non-root user
USER weather

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "import asyncio; from src.tools import health_check; print(asyncio.run(health_check()))" || exit 1

# Expose port (if needed for HTTP mode)
EXPOSE 8000

# Use entrypoint script for flexible deployment
ENTRYPOINT ["./docker-entrypoint.sh"]
