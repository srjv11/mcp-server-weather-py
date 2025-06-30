"""
Example usage of the Enhanced Weather MCP Server

This file demonstrates how to use the weather MCP server tools
and provides examples of different use cases.
"""

import asyncio
import json

from weather_improved import (
    get_alerts,
    get_forecast,
    health_check,
)


async def example_basic_usage():
    """Basic usage examples for the weather MCP tools"""
    print("=" * 60)
    print("BASIC USAGE EXAMPLES")
    print("=" * 60)

    # Example 1: Get weather alerts for California
    print("\n1. Getting weather alerts for California:")
    print("-" * 40)
    alerts = await get_alerts("CA")
    print(alerts)

    # Example 2: Get forecast for San Francisco
    print("\n2. Getting forecast for San Francisco:")
    print("-" * 40)
    forecast = await get_forecast(37.7749, -122.4194)
    print(forecast)

    # Example 3: Health check
    print("\n3. Checking service health:")
    print("-" * 40)
    health = await health_check()
    print(health)


async def example_advanced_usage():
    """Advanced usage examples with filtering and error handling"""
    print("\n" + "=" * 60)
    print("ADVANCED USAGE EXAMPLES")
    print("=" * 60)

    # Example 1: Get only severe weather alerts
    print("\n1. Getting only SEVERE alerts for Texas:")
    print("-" * 40)
    severe_alerts = await get_alerts("TX", "Severe")
    print(severe_alerts)

    # Example 2: Get extreme weather alerts
    print("\n2. Getting EXTREME alerts for Florida:")
    print("-" * 40)
    extreme_alerts = await get_alerts("FL", "Extreme")
    print(extreme_alerts)

    # Example 3: Multiple location forecasts
    locations = [
        ("New York City", 40.7128, -74.0060),
        ("Los Angeles", 34.0522, -118.2437),
        ("Chicago", 41.8781, -87.6298),
        ("Miami", 25.7617, -80.1918),
    ]

    print("\n3. Getting forecasts for multiple major cities:")
    print("-" * 50)
    for city, lat, lon in locations:
        print(f"\n🏙️  {city}:")
        forecast = await get_forecast(lat, lon)
        print(forecast[:200] + "..." if len(forecast) > 200 else forecast)


async def example_error_handling():
    """Examples of error handling and validation"""
    print("\n" + "=" * 60)
    print("ERROR HANDLING EXAMPLES")
    print("=" * 60)

    # Example 1: Invalid state code
    print("\n1. Testing invalid state code:")
    print("-" * 40)
    result = await get_alerts("XX")  # Invalid state
    print(result)

    # Example 2: Invalid coordinates
    print("\n2. Testing invalid coordinates:")
    print("-" * 40)
    result = await get_forecast(91, 0)  # Invalid latitude
    print(result)

    # Example 3: Out of range coordinates
    print("\n3. Testing out-of-range longitude:")
    print("-" * 40)
    result = await get_forecast(0, 181)  # Invalid longitude
    print(result)


async def example_performance_testing():
    """Examples of performance testing and caching"""
    print("\n" + "=" * 60)
    print("PERFORMANCE TESTING EXAMPLES")
    print("=" * 60)

    import time

    # Test caching by making the same request twice
    print("\n1. Testing cache performance (same request twice):")
    print("-" * 50)

    # First request (cache miss)
    start_time = time.time()
    await get_forecast(37.7749, -122.4194)
    first_request_time = time.time() - start_time
    print(f"First request time: {first_request_time:.3f}s")

    # Second request (cache hit)
    start_time = time.time()
    await get_forecast(37.7749, -122.4194)
    second_request_time = time.time() - start_time
    print(f"Second request time: {second_request_time:.3f}s")

    speedup = (
        first_request_time / second_request_time
        if second_request_time > 0
        else float("inf")
    )
    print(f"Cache speedup: {speedup:.1f}x faster")

    # Concurrent requests test
    print("\n2. Testing concurrent requests:")
    print("-" * 40)

    start_time = time.time()
    tasks = [
        get_alerts("CA"),
        get_alerts("NY"),
        get_alerts("TX"),
        get_forecast(37.7749, -122.4194),
        get_forecast(40.7128, -74.0060),
    ]

    await asyncio.gather(*tasks)
    concurrent_time = time.time() - start_time
    print(f"5 concurrent requests completed in: {concurrent_time:.3f}s")


async def example_monitoring_integration():
    """Examples of monitoring and metrics usage"""
    print("\n" + "=" * 60)
    print("MONITORING INTEGRATION EXAMPLES")
    print("=" * 60)

    from monitoring import export_metrics_to_file, metrics_collector

    # Make some requests to generate metrics
    await get_alerts("CA")
    await get_forecast(37.7749, -122.4194)
    await health_check()

    # Get metrics summary
    print("\n1. Current metrics summary:")
    print("-" * 40)
    metrics = await metrics_collector.get_metrics_summary()
    print(json.dumps(metrics, indent=2))

    # Export metrics to file
    print("\n2. Exporting metrics to file:")
    print("-" * 40)
    await export_metrics_to_file("example_metrics.json")
    print("Metrics exported to example_metrics.json")

    # Health status
    print("\n3. Current health status:")
    print("-" * 40)
    health_status = await metrics_collector.get_health_status()
    print(json.dumps(health_status, indent=2))


async def example_configuration_demo():
    """Demonstrate configuration options"""
    print("\n" + "=" * 60)
    print("CONFIGURATION EXAMPLES")
    print("=" * 60)

    from weather_improved import config

    print("\n1. Current configuration:")
    print("-" * 40)
    print(f"API Base URL: {config.nws_api_base}")
    print(f"User Agent: {config.user_agent}")
    print(f"Timeout: {config.timeout}s")
    print(f"Max Retries: {config.max_retries}")
    print(f"Cache TTL: {config.cache_ttl}s")
    print(f"Rate Limit: {config.rate_limit_per_minute}/min")
    print(f"Max Forecast Periods: {config.max_forecast_periods}")

    print("\n2. Environment variable examples:")
    print("-" * 40)
    print("export WEATHER_TIMEOUT=45")
    print("export WEATHER_MAX_RETRIES=5")
    print("export WEATHER_CACHE_TTL=600")


def example_docker_usage():
    """Show Docker usage examples"""
    print("\n" + "=" * 60)
    print("DOCKER USAGE EXAMPLES")
    print("=" * 60)

    print("\n1. Basic Docker commands:")
    print("-" * 40)
    print("# Build the image")
    print("docker build -t weather-mcp .")
    print()
    print("# Run with default configuration")
    print("docker run -it weather-mcp")
    print()
    print("# Run with custom environment variables")
    print("docker run -it -e WEATHER_TIMEOUT=45 -e WEATHER_CACHE_TTL=600 weather-mcp")

    print("\n2. Docker Compose usage:")
    print("-" * 40)
    print("# Start the service")
    print("docker-compose up -d")
    print()
    print("# View logs")
    print("docker-compose logs -f weather-mcp")
    print()
    print("# Check health status")
    print("docker-compose ps")
    print()
    print("# Stop the service")
    print("docker-compose down")


async def example_integration_patterns():
    """Show integration patterns with other systems"""
    print("\n" + "=" * 60)
    print("INTEGRATION PATTERNS")
    print("=" * 60)

    print("\n1. MCP Client Integration Example:")
    print("-" * 40)
    print("""
# Example MCP client configuration
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["weather_improved.py"],
      "env": {
        "WEATHER_TIMEOUT": "30",
        "WEATHER_CACHE_TTL": "300"
      }
    }
  }
}
""")

    print("\n2. API Gateway Integration:")
    print("-" * 40)
    print("""
# Example nginx configuration for HTTP mode
location /weather/ {
    proxy_pass http://weather-mcp:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_timeout 60s;
}
""")

    print("\n3. Monitoring Integration:")
    print("-" * 40)
    print("""
# Prometheus scrape configuration
scrape_configs:
  - job_name: 'weather-mcp'
    static_configs:
      - targets: ['weather-mcp:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
""")


async def run_all_examples():
    """Run all examples in sequence"""
    try:
        await example_basic_usage()
        await example_advanced_usage()
        await example_error_handling()
        await example_performance_testing()
        await example_monitoring_integration()
        await example_configuration_demo()
        example_docker_usage()
        await example_integration_patterns()

        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        print(
            "This might be expected if the NWS API is unavailable or rate limiting is active."
        )


if __name__ == "__main__":
    print("🌤️  Enhanced Weather MCP Server - Examples & Demonstrations")
    print("This script demonstrates various features and usage patterns.")
    print("Note: Some examples may fail if the NWS API is unavailable.")

    asyncio.run(run_all_examples())
