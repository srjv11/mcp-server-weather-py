# MCP Setup Guide for Weather Server

This guide shows how to connect the Enhanced Weather MCP Server to Claude Code.

## 🚀 Quick Setup

### 1. **Configure Claude Code MCP**

Create the MCP configuration file:

**Location:** `~/.config/claude-code/mcp_servers.json`

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": ["run", "weather-mcp"],
      "cwd": "/home/raghu/mcp-server-weather-py"
    }
  }
}
```

### 2. **Alternative Configuration (if package is globally installed)**

```json
{
  "mcpServers": {
    "weather": {
      "command": "weather-mcp",
      "args": []
    }
  }
}
```

### 3. **Restart Claude Code**

After creating the configuration file, restart Claude Code to load the new MCP server.

## 🔧 Available Tools

Once connected, these tools will be available in Claude Code:

### `get_alerts(state, severity_filter?)`
Get weather alerts for a US state.
- **state**: Two-letter state code (e.g., "CA", "TX", "NY")
- **severity_filter**: Optional filter ("Extreme", "Severe", "Moderate", "Minor")

**Example:** `get_alerts("CA", "Severe")`

### `get_forecast(latitude, longitude)`
Get weather forecast for specific coordinates.
- **latitude**: Latitude coordinate (-90 to 90)
- **longitude**: Longitude coordinate (-180 to 180)

**Example:** `get_forecast(37.7749, -122.4194)`

### `get_location_forecast(city, state)`
Get weather forecast by city and state (placeholder - requires geocoding).
- **city**: City name
- **state**: Two-letter state code

**Example:** `get_location_forecast("San Francisco", "CA")`

### `health_check()`
Check the health and status of the weather MCP server.

**Example:** `health_check()`

## 🧪 Testing the Connection

### 1. **Check MCP Server Status**
In Claude Code, you can run: `/mcp`

This should show the weather server as connected.

### 2. **Test a Simple Query**
Ask Claude Code: "Can you check the weather alerts for California?"

### 3. **Test Forecast Query**
Ask Claude Code: "What's the weather forecast for coordinates 37.7749, -122.4194?"

## 🔍 Troubleshooting

### **Server Not Connecting**
1. Check that the config file exists: `~/.config/claude-code/mcp_servers.json`
2. Verify the path in `cwd` points to your project directory
3. Test the server manually: `uv run weather-mcp`
4. Restart Claude Code completely

### **Tools Not Available**
1. Check Claude Code's MCP status with `/mcp`
2. Look for any error messages in Claude Code's logs
3. Verify the server starts without errors

### **Weather Data Issues**
1. Check internet connectivity
2. Verify the National Weather Service API is accessible
3. Run `health_check()` tool to diagnose issues

## 📊 Features

- **Real-time weather data** from the National Weather Service
- **Caching** for improved performance
- **Rate limiting** to respect API limits
- **Retry logic** with exponential backoff
- **Comprehensive error handling**
- **Multiple query types** (alerts, forecasts, coordinates)

## 🌐 Data Sources

All weather data comes from the **National Weather Service (NWS) API**:
- Official US government weather data
- No API key required
- High reliability and accuracy
- Real-time updates

## 📝 Example Usage in Claude Code

Once configured, you can ask Claude Code natural language questions like:

- "Are there any severe weather alerts in Texas?"
- "What's the weather forecast for San Francisco?"
- "Check if there are any extreme weather alerts nationwide"
- "Get the forecast for coordinates 40.7128, -74.0060"

The MCP server will automatically handle the API calls and return formatted, easy-to-read weather information!
