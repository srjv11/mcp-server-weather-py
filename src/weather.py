"""
Enhanced Weather MCP Server - Modular Version

A comprehensive, production-ready MCP (Model Context Protocol) server providing
weather data from the National Weather Service API with modular architecture.
"""

import asyncio
import atexit
import logging

from .client import cleanup
from .config import config
from .tools import mcp

# Configure structured logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # Register cleanup function
    def cleanup_wrapper() -> None:
        asyncio.run(cleanup())

    atexit.register(cleanup_wrapper)

    logger.info("Starting Enhanced Weather MCP Server (Modular)")
    logger.info(f"Configuration: {config}")

    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        asyncio.run(cleanup())
