#!/usr/bin/env python3
"""
Main entry point for the Enhanced Weather MCP Server.

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


def main() -> None:
    """Main entry point for the weather MCP server."""

    # Register cleanup function
    def cleanup_wrapper() -> None:
        asyncio.run(cleanup())

    atexit.register(cleanup_wrapper)

    logger.info("Starting Enhanced Weather MCP Server")
    logger.info(f"Configuration: {config}")

    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        asyncio.run(cleanup())


if __name__ == "__main__":
    main()
