# API Reference

Complete reference for all MCP tools provided by the Weather MCP Server.

## 🛠️ MCP Tools Overview

The Weather MCP Server provides four main tools for weather data access:

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `get_alerts` | Weather alerts by state | State code, severity filter | Formatted alert list |
| `get_forecast` | Weather forecast by coordinates | Latitude, longitude | Detailed forecast |
| `get_location_forecast` | Forecast by city/state | City name, state code | Location-based forecast |
| `health_check` | Server health status | None | Health metrics |

## 📊 Tool Details

### get_alerts

Retrieves active weather alerts for a specified US state or territory.

**Signature:**
```python
async def get_alerts(state: str, severity_filter: Optional[str] = None) -> str
```

**Parameters:**
- `state` (str, required): Two-letter US state or territory code
- `severity_filter` (str, optional): Filter alerts by severity level

**State Codes:** Valid US state and territory codes:
```
AL, AK, AZ, AR, CA, CO, CT, DE, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD,
MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ, NM, NY, NC, ND, OH, OK, OR, PA, RI, SC,
SD, TN, TX, UT, VT, VA, WA, WV, WI, WY, DC, AS, GU, MP, PR, VI
```

**Severity Levels:**
- `Extreme` - Extraordinary threat to life or property
- `Severe` - Significant threat to life or property
- `Moderate` - Possible threat to life or property
- `Minor` - Minimal to no threat to life or property

**Example Usage:**
```python
# Get all alerts for California
alerts = await get_alerts("CA")

# Get only severe alerts for Texas
severe_alerts = await get_alerts("TX", "Severe")

# Get extreme alerts for Florida
extreme_alerts = await get_alerts("FL", "Extreme")
```

**Return Format:**
```
🚨 Weather Alerts for California (CA)

⚠️ SEVERE - Heat Warning
📍 Areas: Los Angeles County, Orange County
🕐 From: 2024-06-30 12:00 PM PDT
🕐 Until: 2024-07-01 8:00 PM PDT
📋 Dangerous heat expected with temperatures reaching 105-110°F...

💡 1 alert found | Last updated: 2024-06-30 10:30 AM
```

**Error Handling:**
- Invalid state code: Returns validation error message
- No alerts found: Returns "No active alerts" message
- API unavailable: Returns service unavailable message

---

### get_forecast

Retrieves detailed weather forecast for specific geographic coordinates.

**Signature:**
```python
async def get_forecast(latitude: float, longitude: float) -> str
```

**Parameters:**
- `latitude` (float, required): Latitude coordinate (-90 to 90)
- `longitude` (float, required): Longitude coordinate (-180 to 180)

**Coordinate Validation:**
- Latitude must be between -90 and 90 degrees
- Longitude must be between -180 and 180 degrees
- Precision up to 4 decimal places recommended

**Example Usage:**
```python
# San Francisco coordinates
forecast = await get_forecast(37.7749, -122.4194)

# New York City coordinates
forecast = await get_forecast(40.7128, -74.0060)

# Miami coordinates
forecast = await get_forecast(25.7617, -80.1918)
```

**Return Format:**
```
🌤️ Weather Forecast

📍 Location: San Francisco, CA (37.7749, -122.4194)
🏢 Forecast Office: San Francisco Bay Area/Monterey

📅 Today (Saturday)
🌡️ 72°F | Partly Cloudy
💨 Wind: SW 15 mph
💧 Humidity: 65%
🌧️ Chance of rain: 10%
📝 Partly sunny with light winds...

📅 Tonight (Saturday Night)
🌡️ 58°F | Clear
💨 Wind: W 8 mph
💧 Humidity: 80%
🌧️ Chance of rain: 0%
📝 Clear skies with cool temperatures...

[Additional forecast periods...]

🕐 Last updated: 2024-06-30 10:30 AM PDT
```

**Error Handling:**
- Invalid coordinates: Returns validation error message
- Location not supported: Returns coverage area message
- API timeout: Returns timeout error with retry suggestion

---

### get_location_forecast

Retrieves weather forecast using city and state names (requires geocoding).

**Signature:**
```python
async def get_location_forecast(city: str, state: str) -> str
```

**Parameters:**
- `city` (str, required): City name
- `state` (str, required): Two-letter US state code

**Current Status:**
> **Note:** This tool is currently a placeholder. Geocoding functionality is not yet implemented. Use `get_forecast` with coordinates instead.

**Example Usage:**
```python
# This will return a placeholder message
forecast = await get_location_forecast("San Francisco", "CA")
```

**Return Format:**
```
🚧 Location-based forecasts are not yet implemented.

Please use get_forecast with coordinates instead:
- Use a geocoding service to convert "San Francisco, CA" to coordinates
- Then call get_forecast(37.7749, -122.4194)

For coordinate lookup, try:
- Google Maps: Right-click for coordinates
- GPS coordinates from weather apps
- Online geocoding services
```

**Future Implementation:**
- Integration with geocoding service (Google Maps API, OpenStreetMap)
- Address validation and suggestion
- Support for landmarks and points of interest

---

### health_check

Provides comprehensive health and performance metrics for the MCP server.

**Signature:**
```python
async def health_check() -> str
```

**Parameters:**
- None

**Example Usage:**
```python
# Check server health
health = await health_check()
```

**Return Format:**
```
✅ Weather MCP Server Health Check

🟢 Service Status: Healthy
🕐 Uptime: 2 hours, 45 minutes
📊 Response Time: 125ms (average)

📡 API Connectivity:
  ✅ National Weather Service: Operational
  🕐 Last API Call: 30 seconds ago
  📈 Success Rate: 98.5% (last 100 requests)

💾 Cache Performance:
  📊 Hit Rate: 75.3%
  🗃️ Cached Items: 42 entries
  🧹 Cache Size: 2.4 MB
  ⏰ Oldest Entry: 4 minutes ago

⚡ Rate Limiting:
  📊 Current Usage: 12/60 requests per minute
  ⏳ Reset Time: 48 seconds
  🚦 Status: Normal

🔧 System Metrics:
  💾 Memory Usage: 45.2 MB
  🔄 Active Connections: 3
  📝 Log Level: INFO

Last Health Check: 2024-06-30 10:30:15 AM PDT
```

**Metrics Included:**
- **Service Status**: Overall health (Healthy/Warning/Critical)
- **Uptime**: Time since server start
- **Response Time**: Average API response time
- **API Connectivity**: External API status and success rates
- **Cache Performance**: Hit rates and cache statistics
- **Rate Limiting**: Current usage and limits
- **System Metrics**: Memory usage and connections

**Health Status Levels:**
- `Healthy` (🟢): All systems operational
- `Warning` (🟡): Minor issues, service degraded
- `Critical` (🔴): Major issues, service unavailable

## 🔧 Error Handling

All tools implement comprehensive error handling:

### Validation Errors
```python
# Invalid state code
"❌ Invalid state code 'XX'. Valid codes: AL, AK, AZ..."

# Invalid coordinates
"❌ Invalid latitude '95'. Must be between -90 and 90."
```

### API Errors
```python
# Service unavailable
"🚫 Weather service temporarily unavailable. Please try again later."

# Rate limit exceeded
"⏳ Rate limit exceeded. Please wait before making another request."
```

### Network Errors
```python
# Timeout
"⏰ Request timed out. Please check your connection and try again."

# Connection error
"🌐 Unable to connect to weather service. Please check your internet connection."
```

## 📈 Performance Characteristics

### Response Times
- **get_alerts**: 200-500ms (cached: <50ms)
- **get_forecast**: 300-800ms (cached: <50ms)
- **health_check**: 10-50ms
- **get_location_forecast**: <10ms (placeholder)

### Caching Behavior
- **Default TTL**: 5 minutes (300 seconds)
- **Cache Keys**: Based on function parameters
- **Automatic Cleanup**: Expired entries removed automatically
- **Cache Hit Rate**: Typically 70-80% in normal usage

### Rate Limiting
- **Default Limit**: 60 requests per minute
- **Applies Per**: IP address or client
- **Reset Interval**: 1 minute rolling window
- **Burst Handling**: Short bursts allowed within limits

## 🔗 Integration Examples

### Claude Code Usage
Once configured as an MCP server, these tools can be called naturally:

```
User: "Are there any severe weather alerts in Texas?"
Claude: I'll check for severe weather alerts in Texas.
[Calls get_alerts("TX", "Severe")]

User: "What's the weather forecast for San Francisco?"
Claude: I'll get the weather forecast for San Francisco coordinates.
[Calls get_forecast(37.7749, -122.4194)]
```

### Direct Python Usage
```python
import asyncio
from src.tools import get_alerts, get_forecast, health_check

async def example():
    # Get alerts
    alerts = await get_alerts("CA", "Severe")
    print(alerts)

    # Get forecast
    forecast = await get_forecast(37.7749, -122.4194)
    print(forecast)

    # Check health
    health = await health_check()
    print(health)

asyncio.run(example())
```

---

[[Home]] | [[Examples and Tutorials]] | [[Troubleshooting]]
