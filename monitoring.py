import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """Metrics for individual requests"""

    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: float
    error: str | None = None


@dataclass
class ServiceMetrics:
    """Aggregated service metrics"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    rate_limit_hits: int = 0
    uptime_seconds: float = 0.0
    start_time: float = field(default_factory=time.time)

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def cache_hit_rate(self) -> float:
        total_cache_requests = self.cache_hits + self.cache_misses
        if total_cache_requests == 0:
            return 0.0
        return (self.cache_hits / total_cache_requests) * 100


class MetricsCollector:
    """Collects and aggregates metrics for the weather service"""

    def __init__(self, max_request_history: int = 1000):
        self.max_request_history = max_request_history
        self.request_history: deque = deque(maxlen=max_request_history)
        self.metrics = ServiceMetrics()
        self.endpoint_metrics: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def record_request(self, metrics: RequestMetrics):
        """Record a request and update metrics"""
        async with self._lock:
            self.request_history.append(metrics)
            self.metrics.total_requests += 1

            if 200 <= metrics.status_code < 400:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1

            # Update average response time
            self._update_avg_response_time(metrics.response_time)

            # Track endpoint-specific metrics
            self.endpoint_metrics[metrics.endpoint].append(metrics.response_time)

            # Keep only recent metrics for endpoints
            if len(self.endpoint_metrics[metrics.endpoint]) > 100:
                self.endpoint_metrics[metrics.endpoint] = self.endpoint_metrics[
                    metrics.endpoint
                ][-100:]

    def _update_avg_response_time(self, new_time: float):
        """Update running average response time"""
        if self.metrics.total_requests == 1:
            self.metrics.avg_response_time = new_time
        else:
            # Simple running average
            alpha = 0.1  # Smoothing factor
            self.metrics.avg_response_time = (
                alpha * new_time + (1 - alpha) * self.metrics.avg_response_time
            )

    async def record_cache_hit(self):
        """Record a cache hit"""
        async with self._lock:
            self.metrics.cache_hits += 1

    async def record_cache_miss(self):
        """Record a cache miss"""
        async with self._lock:
            self.metrics.cache_misses += 1

    async def record_rate_limit_hit(self):
        """Record a rate limit hit"""
        async with self._lock:
            self.metrics.rate_limit_hits += 1

    async def get_metrics_summary(self) -> dict:
        """Get current metrics summary"""
        async with self._lock:
            self.metrics.uptime_seconds = time.time() - self.metrics.start_time

            # Calculate endpoint statistics
            endpoint_stats = {}
            for endpoint, times in self.endpoint_metrics.items():
                if times:
                    endpoint_stats[endpoint] = {
                        "count": len(times),
                        "avg_response_time": sum(times) / len(times),
                        "min_response_time": min(times),
                        "max_response_time": max(times),
                    }

            # Recent error analysis
            recent_errors = []
            cutoff_time = time.time() - 3600  # Last hour
            for req in reversed(self.request_history):
                if req.timestamp < cutoff_time:
                    break
                if req.error:
                    recent_errors.append(
                        {
                            "timestamp": req.timestamp,
                            "endpoint": req.endpoint,
                            "error": req.error,
                            "status_code": req.status_code,
                        }
                    )

            return {
                "service_metrics": {
                    "total_requests": self.metrics.total_requests,
                    "successful_requests": self.metrics.successful_requests,
                    "failed_requests": self.metrics.failed_requests,
                    "success_rate": round(self.metrics.success_rate, 2),
                    "avg_response_time": round(self.metrics.avg_response_time, 3),
                    "cache_hits": self.metrics.cache_hits,
                    "cache_misses": self.metrics.cache_misses,
                    "cache_hit_rate": round(self.metrics.cache_hit_rate, 2),
                    "rate_limit_hits": self.metrics.rate_limit_hits,
                    "uptime_seconds": round(self.metrics.uptime_seconds, 1),
                },
                "endpoint_metrics": endpoint_stats,
                "recent_errors": recent_errors[:10],  # Last 10 errors
            }

    async def get_health_status(self) -> dict:
        """Get health status based on metrics"""
        async with self._lock:
            recent_requests = [
                req
                for req in self.request_history
                if time.time() - req.timestamp < 300  # Last 5 minutes
            ]

            if not recent_requests:
                status = "idle"
                details = "No recent requests"
            elif self.metrics.success_rate >= 95:
                status = "healthy"
                details = f"Success rate: {self.metrics.success_rate:.1f}%"
            elif self.metrics.success_rate >= 80:
                status = "degraded"
                details = f"Success rate: {self.metrics.success_rate:.1f}%"
            else:
                status = "unhealthy"
                details = f"Success rate: {self.metrics.success_rate:.1f}%"

            return {
                "status": status,
                "details": details,
                "last_check": time.time(),
                "uptime": self.metrics.uptime_seconds,
            }


# Global metrics collector instance
metrics_collector = MetricsCollector()


class MetricsMiddleware:
    """Middleware to automatically collect metrics for requests"""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    async def __call__(self, endpoint: str, func, *args, **kwargs):
        """Wrapper function to collect metrics"""
        start_time = time.time()
        error = None
        status_code = 200

        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            error = str(e)
            status_code = 500
            raise
        finally:
            response_time = time.time() - start_time
            metrics = RequestMetrics(
                endpoint=endpoint,
                method="GET",  # Assuming GET for weather API
                status_code=status_code,
                response_time=response_time,
                timestamp=start_time,
                error=error,
            )
            await self.collector.record_request(metrics)


# Create middleware instance
metrics_middleware = MetricsMiddleware(metrics_collector)


async def export_metrics_to_file(filepath: str = "metrics.json"):
    """Export current metrics to a JSON file"""
    try:
        metrics = await metrics_collector.get_metrics_summary()
        with open(filepath, "w") as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Metrics exported to {filepath}")
    except Exception as e:
        logger.error(f"Failed to export metrics: {e}")


async def log_metrics_summary():
    """Log a summary of current metrics"""
    try:
        metrics = await metrics_collector.get_metrics_summary()
        service = metrics["service_metrics"]

        logger.info(
            f"Metrics Summary - "
            f"Requests: {service['total_requests']}, "
            f"Success Rate: {service['success_rate']}%, "
            f"Avg Response: {service['avg_response_time']}s, "
            f"Cache Hit Rate: {service['cache_hit_rate']}%"
        )
    except Exception as e:
        logger.error(f"Failed to log metrics summary: {e}")


# Periodic metrics logging
async def start_metrics_logging(interval: int = 300):  # 5 minutes
    """Start periodic metrics logging"""
    while True:
        try:
            await asyncio.sleep(interval)
            await log_metrics_summary()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in metrics logging: {e}")


def get_prometheus_metrics() -> str:
    """Export metrics in Prometheus format"""
    # This is a simplified version - in production you'd use prometheus_client
    try:
        metrics = asyncio.run(metrics_collector.get_metrics_summary())
        service = metrics["service_metrics"]

        prometheus_output = f"""# HELP weather_mcp_requests_total Total number of requests
# TYPE weather_mcp_requests_total counter
weather_mcp_requests_total {service["total_requests"]}

# HELP weather_mcp_requests_successful_total Total number of successful requests
# TYPE weather_mcp_requests_successful_total counter
weather_mcp_requests_successful_total {service["successful_requests"]}

# HELP weather_mcp_requests_failed_total Total number of failed requests
# TYPE weather_mcp_requests_failed_total counter
weather_mcp_requests_failed_total {service["failed_requests"]}

# HELP weather_mcp_response_time_avg Average response time in seconds
# TYPE weather_mcp_response_time_avg gauge
weather_mcp_response_time_avg {service["avg_response_time"]}

# HELP weather_mcp_cache_hits_total Total number of cache hits
# TYPE weather_mcp_cache_hits_total counter
weather_mcp_cache_hits_total {service["cache_hits"]}

# HELP weather_mcp_cache_misses_total Total number of cache misses
# TYPE weather_mcp_cache_misses_total counter
weather_mcp_cache_misses_total {service["cache_misses"]}

# HELP weather_mcp_uptime_seconds Service uptime in seconds
# TYPE weather_mcp_uptime_seconds gauge
weather_mcp_uptime_seconds {service["uptime_seconds"]}
"""
        return prometheus_output
    except Exception as e:
        logger.error(f"Failed to generate Prometheus metrics: {e}")
        return "# Error generating metrics\n"
