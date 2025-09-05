import asyncio
import json
import logging
import signal
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPTool:
    """Represents an MCP Tool with name, description, input schema, and handler"""
    
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any], handler):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler

class MCPResource:
    """Represents an MCP Resource with URI, name, description, and content"""
    
    def __init__(self, uri: str, name: str, description: str, mime_type: str, content: str):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type
        self.content = content

class MCPServer:
    """Model Context Protocol Server Implementation"""
    
    def __init__(self, name: str = "mcp-server", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.request_id = 0
        
    def _get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    def register_tool(self, tool: MCPTool):
        """Register a tool with the server"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def register_resource(self, resource: MCPResource):
        """Register a resource with the server"""
        self.resources[resource.uri] = resource
        logger.info(f"Registered resource: {resource.name} ({resource.uri})")
    
    async def handle_request(self, request_data: str) -> str:
        """Handle incoming MCP requests"""
        try:
            # Parse the JSON request
            request = json.loads(request_data)
            method = request.get('method')
            request_id = request.get('id')
            params = request.get('params', {})
            
            logger.info(f"Received MCP request: {method}")
            
            # Handle the request based on method
            if method == "tools/list":
                result = await self._list_tools()
            elif method == "tools/call":
                result = await self._call_tool(params)
            elif method == "resources/list":
                result = await self._list_resources()
            elif method == "resources/read":
                result = await self._read_resource(params)
            elif method == "initialize":
                result = await self._initialize(params)
            else:
                # Method not found
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": "Method not found",
                        "data": f"Method '{method}' not found"
                    }
                }
                return json.dumps(error_response)
            
            # Create successful response
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
            logger.info(f"Sending MCP response for method: {method}")
            return json.dumps(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error",
                    "data": str(e)
                }
            }
            return json.dumps(error_response)
        
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get('id') if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
            return json.dumps(error_response)
    
    async def _initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the MCP connection"""
        client_info = params.get("clientInfo", {})
        logger.info(f"Initializing MCP connection with client: {client_info}")
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": True, "listChanged": True}
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version
            }
        }
    
    async def _list_tools(self) -> Dict[str, Any]:
        """List all available tools"""
        tools_list = []
        for tool in self.tools.values():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            })
        
        return {"tools": tools_list}
    
    async def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
        
        # Call the tool handler
        if asyncio.iscoroutinefunction(tool.handler):
            result = await tool.handler(**arguments)
        else:
            result = tool.handler(**arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": str(result)
                }
            ]
        }
    
    async def _list_resources(self) -> Dict[str, Any]:
        """List all available resources"""
        resources_list = []
        for resource in self.resources.values():
            resources_list.append({
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type
            })
        
        return {"resources": resources_list}
    
    async def _read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a specific resource"""
        uri = params.get("uri")
        
        if uri not in self.resources:
            raise ValueError(f"Resource '{uri}' not found")
        
        resource = self.resources[uri]
        logger.info(f"Reading resource: {resource.name} ({uri})")
        
        return {
            "contents": [
                {
                    "uri": resource.uri,
                    "mimeType": resource.mime_type,
                    "text": resource.content
                }
            ]
        }

# Global variable to track server state
server_shutdown = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global server_shutdown
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    server_shutdown = True

# Create MCP server instance
mcp_server = MCPServer("example-mcp-server", "1.0.0")

# Tool implementations
async def get_weather(location: str) -> str:
    """Get weather information for a location"""
    # Simulate API call delay
    await asyncio.sleep(0.1)
    
    # Mock weather data
    weather_data = {
        "New York": "Sunny, 22°C",
        "London": "Cloudy, 15°C", 
        "Tokyo": "Rainy, 18°C",
        "Paris": "Partly cloudy, 20°C"
    }
    
    return f"Weather in {location}: {weather_data.get(location, 'Weather data not available')}"

async def calculate_math(expression: str) -> str:
    """Calculate mathematical expressions safely"""
    try:
        # Simple safe evaluation for basic math
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"
        
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating expression: {str(e)}"

async def get_system_info() -> str:
    """Get system information"""
    import platform
    import psutil
    
    info = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": f"{psutil.virtual_memory().total / (1024**3):.1f} GB"
    }
    
    return json.dumps(info, indent=2)

async def search_files(query: str, directory: str = ".") -> str:
    """Search for files matching a query"""
    try:
        import glob
        import os
        
        # Simple file search
        pattern = os.path.join(directory, f"*{query}*")
        files = glob.glob(pattern)
        
        if not files:
            return f"No files found matching '{query}' in {directory}"
        
        result = f"Found {len(files)} files matching '{query}':\n"
        for file in files[:10]:  # Limit to 10 results
            result += f"- {file}\n"
        
        if len(files) > 10:
            result += f"... and {len(files) - 10} more files"
        
        return result
    except Exception as e:
        return f"Error searching files: {str(e)}"

# Register tools
weather_tool = MCPTool(
    name="get_weather",
    description="Get current weather information for a specified location",
    input_schema={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name or location to get weather for"
            }
        },
        "required": ["location"]
    },
    handler=get_weather
)

math_tool = MCPTool(
    name="calculate_math",
    description="Calculate mathematical expressions safely",
    input_schema={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to calculate (e.g., '2 + 3 * 4')"
            }
        },
        "required": ["expression"]
    },
    handler=calculate_math
)

system_info_tool = MCPTool(
    name="get_system_info",
    description="Get system information including platform, CPU, memory, etc.",
    input_schema={
        "type": "object",
        "properties": {},
        "required": []
    },
    handler=get_system_info
)

file_search_tool = MCPTool(
    name="search_files",
    description="Search for files matching a query in a directory",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for file names"
            },
            "directory": {
                "type": "string",
                "description": "Directory to search in (default: current directory)",
                "default": "."
            }
        },
        "required": ["query"]
    },
    handler=search_files
)

# Register all tools
mcp_server.register_tool(weather_tool)
mcp_server.register_tool(math_tool)
mcp_server.register_tool(system_info_tool)
mcp_server.register_tool(file_search_tool)

# Resource implementations
sample_data_resource = MCPResource(
    uri="file:///sample_data.json",
    name="Sample Data",
    description="Sample JSON data for testing",
    mime_type="application/json",
    content=json.dumps({
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
            {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
        ],
        "products": [
            {"id": 1, "name": "Laptop", "price": 999.99},
            {"id": 2, "name": "Mouse", "price": 29.99},
            {"id": 3, "name": "Keyboard", "price": 79.99}
        ]
    }, indent=2)
)

config_resource = MCPResource(
    uri="file:///config.yaml",
    name="Configuration",
    description="Server configuration file",
    mime_type="text/yaml",
    content="""# MCP Server Configuration
server:
  name: "example-mcp-server"
  version: "1.0.0"
  port: 8000

tools:
  weather:
    enabled: true
    api_key: "your_api_key_here"
  
  math:
    enabled: true
    max_expression_length: 1000

resources:
  sample_data:
    path: "/data/sample.json"
    cache_ttl: 3600
"""
)

readme_resource = MCPResource(
    uri="file:///README.md",
    name="Documentation",
    description="MCP Server documentation and examples",
    mime_type="text/markdown",
    content="""# MCP Server Documentation

## Available Tools

### get_weather
Get current weather information for a specified location.

**Parameters:**
- `location` (string): City name or location

**Example:**
```json
{
  "name": "get_weather",
  "arguments": {
    "location": "New York"
  }
}
```

### calculate_math
Calculate mathematical expressions safely.

**Parameters:**
- `expression` (string): Mathematical expression

**Example:**
```json
{
  "name": "calculate_math",
  "arguments": {
    "expression": "2 + 3 * 4"
  }
}
```

### get_system_info
Get system information including platform, CPU, memory, etc.

**Example:**
```json
{
  "name": "get_system_info",
  "arguments": {}
}
```

### search_files
Search for files matching a query in a directory.

**Parameters:**
- `query` (string): Search query for file names
- `directory` (string, optional): Directory to search in

**Example:**
```json
{
  "name": "search_files",
  "arguments": {
    "query": "*.py",
    "directory": "."
  }
}
```

## Available Resources

- `file:///sample_data.json` - Sample JSON data
- `file:///config.yaml` - Server configuration
- `file:///README.md` - This documentation
"""
)

# Register all resources
mcp_server.register_resource(sample_data_resource)
mcp_server.register_resource(config_resource)
mcp_server.register_resource(readme_resource)

# HTTP Server implementation
async def run_server(host: str = "localhost", port: int = 8000):
    """Run the MCP HTTP server"""
    from aiohttp import web, web_request
    import aiohttp_cors
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    async def handle_request(request: web_request.Request) -> web.Response:
        """Handle incoming HTTP requests"""
        try:
            # Get the request data
            request_data = await request.text()
            logger.info(f"Received HTTP request from {request.remote}")
            
            # Process the MCP request
            response_data = await mcp_server.handle_request(request_data)
            
            # Return the response
            return web.Response(
                text=response_data,
                content_type='application/json',
                headers={'Access-Control-Allow-Origin': '*'}
            )
            
        except Exception as e:
            logger.error(f"Error handling HTTP request: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
            return web.Response(
                text=json.dumps(error_response),
                content_type='application/json',
                status=500
            )
    
    # Create the web application
    app = web.Application()
    
    # Configure CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    app.router.add_post('/mcp', handle_request)
    app.router.add_get('/health', lambda r: web.Response(text='OK'))
    app.router.add_get('/tools', lambda r: web.Response(
        text=json.dumps({"tools": list(mcp_server.tools.keys())}),
        content_type='application/json'
    ))
    app.router.add_get('/resources', lambda r: web.Response(
        text=json.dumps({"resources": list(mcp_server.resources.keys())}),
        content_type='application/json'
    ))
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    logger.info(f"MCP Server starting on http://{host}:{port}")
    logger.info("Available endpoints:")
    logger.info(f"  POST http://{host}:{port}/mcp - MCP protocol endpoint")
    logger.info(f"  GET  http://{host}:{port}/health - Health check")
    logger.info(f"  GET  http://{host}:{port}/tools - List available tools")
    logger.info(f"  GET  http://{host}:{port}/resources - List available resources")
    logger.info(f"Registered {len(mcp_server.tools)} tools and {len(mcp_server.resources)} resources")
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    logger.info("MCP Server is running and ready to accept connections")
    logger.info("Press Ctrl+C to gracefully shutdown the server")
    
    # Keep the server running until shutdown signal
    try:
        while not server_shutdown:
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down server...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Cleaning up server resources...")
        await runner.cleanup()
        logger.info("MCP Server shutdown complete")

if __name__ == "__main__":
    asyncio.run(run_server())
