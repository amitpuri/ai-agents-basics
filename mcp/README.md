# Model Context Protocol (MCP) Implementation

This directory contains a complete implementation of the Model Context Protocol (MCP) for enabling large language models to interact with tools and resources. The implementation demonstrates how to create an MCP server that exposes tools and resources, and an MCP client that can invoke these tools and access resources.

## Files

- `server.py` - MCP Server implementation with tools and resources
- `client.py` - MCP Client implementation for tool invocation and resource access
- `requirements.txt` - Python dependencies
- `README.md` - This documentation file
- `LICENSE` - MIT License
- `tests/` - Comprehensive test suite
  - `__init__.py` - Test package initialization
  - `conftest.py` - Pytest configuration and fixtures
  - `test_server.py` - Server functionality tests
  - `test_client.py` - Client functionality tests

## Features

### Server (`server.py`)

- **MCP Protocol Compliance**: Full implementation of the Model Context Protocol specification
- **Tool Registration**: Easy registration of tools with input schemas and handlers
- **Resource Management**: Support for various resource types (JSON, YAML, Markdown)
- **Async Support**: Full asynchronous implementation using asyncio
- **Error Handling**: Comprehensive error handling with proper JSON-RPC error responses
- **Logging**: Detailed logging for debugging and monitoring
- **Extensible**: Easy to add new tools and resources

### Client (`client.py`)

- **MCPClient Class**: Clean, object-oriented client implementation
- **Tool Invocation**: Convenient methods for calling server tools
- **Resource Access**: Methods for listing and reading server resources
- **Batch Operations**: Support for calling multiple tools concurrently
- **Error Handling**: Robust error handling and recovery
- **Interactive Mode**: Command-line interface for manual testing
- **Examples**: Comprehensive examples demonstrating all features


## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

Start the MCP server:

```bash
python server.py
```

The server will start on `http://localhost:8000` and provide the following endpoints:
- `POST /mcp` - MCP protocol endpoint
- `GET /health` - Health check
- `GET /tools` - List available tools
- `GET /resources` - List available resources

### Running the Client

#### Basic Examples
```bash
python client.py
```

This runs comprehensive examples demonstrating all client functionality.

#### Interactive Mode
```bash
python client.py interactive
```

This starts an interactive command-line interface where you can manually test different operations.

Available commands:
- `tools` - List available tools
- `resources` - List available resources
- `weather <location>` - Get weather for location
- `math <expression>` - Calculate mathematical expression
- `system` - Get system information
- `search <query> [directory]` - Search for files
- `read <uri>` - Read a resource
- `call <tool_name> <json_args>` - Call a tool with custom arguments
- `quit` - Exit


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


## API Reference

### Server Methods

#### `initialize`
Initialize the MCP connection.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "clientInfo": {
      "name": "mcp-client",
      "version": "1.0.0"
    }
  },
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {"listChanged": true},
      "resources": {"subscribe": true, "listChanged": true}
    },
    "serverInfo": {
      "name": "example-mcp-server",
      "version": "1.0.0"
    }
  }
}
```

#### `tools/list`
List all available tools.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 2
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather information for a specified location",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name or location to get weather for"
            }
          },
          "required": ["location"]
        }
      }
    ]
  }
}
```

#### `tools/call`
Call a specific tool.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "New York"
    }
  },
  "id": 3
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Weather in New York: Sunny, 22°C"
      }
    ]
  }
}
```

#### `resources/list`
List all available resources.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "resources/list",
  "id": 4
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "resources": [
      {
        "uri": "file:///sample_data.json",
        "name": "Sample Data",
        "description": "Sample JSON data for testing",
        "mimeType": "application/json"
      }
    ]
  }
}
```

#### `resources/read`
Read a specific resource.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "resources/read",
  "params": {
    "uri": "file:///sample_data.json"
  },
  "id": 5
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "contents": [
      {
        "uri": "file:///sample_data.json",
        "mimeType": "application/json",
        "text": "{\"users\": [{\"id\": 1, \"name\": \"Alice\"}]}"
      }
    ]
  }
}
```

### Client Methods

#### `MCPClient.initialize(client_info)`
```python
result = await client.initialize({"name": "my-client", "version": "1.0.0"})
```

#### `MCPClient.list_tools()`
```python
tools = await client.list_tools()
```

#### `MCPClient.call_tool(name, arguments)`
```python
result = await client.call_tool("get_weather", {"location": "London"})
```

#### `MCPClient.list_resources()`
```python
resources = await client.list_resources()
```

#### `MCPClient.read_resource(uri)`
```python
content = await client.read_resource("file:///sample_data.json")
```

#### `MCPClient.batch_call_tools(tool_calls)`
```python
tool_calls = [
    {"name": "get_weather", "arguments": {"location": "New York"}},
    {"name": "calculate_math", "arguments": {"expression": "2 + 2"}}
]
results = await client.batch_call_tools(tool_calls)
```

## Error Handling

The implementation includes comprehensive error handling:

- **JSON Parse Errors**: Invalid JSON requests are handled gracefully
- **Method Not Found**: Unknown methods return proper JSON-RPC error responses
- **Tool Not Found**: Unknown tools return appropriate error messages
- **Resource Not Found**: Unknown resources return proper error responses
- **Internal Errors**: Server errors are caught and returned as error responses
- **Client Errors**: Client-side errors are logged and handled appropriately

## Extending the Implementation

### Adding New Tools

1. Create a new tool handler function:
```python
async def my_new_tool(param1: str, param2: int) -> str:
    # Implementation here
    return f"Result: {param1} and {param2}"
```

2. Create and register the tool:
```python
new_tool = MCPTool(
    name="my_new_tool",
    description="Description of what this tool does",
    input_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First parameter"},
            "param2": {"type": "integer", "description": "Second parameter"}
        },
        "required": ["param1", "param2"]
    },
    handler=my_new_tool
)

mcp_server.register_tool(new_tool)
```

3. Add corresponding client method:
```python
async def my_new_tool(self, param1: str, param2: int) -> Dict[str, Any]:
    return await self.call_tool("my_new_tool", {"param1": param1, "param2": param2})
```

### Adding New Resources

1. Create a new resource:
```python
new_resource = MCPResource(
    uri="file:///my_resource.txt",
    name="My Resource",
    description="Description of this resource",
    mime_type="text/plain",
    content="Resource content here"
)

mcp_server.register_resource(new_resource)
```

### Adding Real Network Transport

The current implementation uses HTTP for transport. To add other transport methods:

1. **WebSocket Transport**: Implement WebSocket-based communication
2. **STDIO Transport**: Implement standard input/output communication
3. **Custom Transport**: Implement any custom transport protocol

## Security Considerations

- **Input Validation**: All tool inputs are validated against their schemas
- **Safe Evaluation**: Mathematical expressions use safe evaluation methods
- **Resource Access**: Resources are served from predefined URIs only
- **Error Information**: Error messages don't expose sensitive system information


## Testing

### Running Tests

The project includes comprehensive test suites for both server and client functionality. Tests are located in the `tests/` directory.

#### Run All Tests
```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_server.py
pytest tests/test_client.py
```

#### Test Coverage
The test suite includes:

- **Server Tests** (`test_server.py`):
  - MCP protocol compliance testing
  - Tool registration and invocation
  - Resource management and access
  - Error handling (invalid methods, tools, resources)
  - Async operation testing
  - Tool handler functionality (weather, math, system info, file search)

- **Client Tests** (`test_client.py`):
  - Request structure validation
  - Response handling and error scenarios
  - Connection error handling
  - Tool invocation and resource access
  - Batch operations testing
  - JSON serialization testing

- **Integration Tests**:
  - End-to-end workflow testing
  - Client-server communication
  - Tool and resource lifecycle testing
  - Error recovery scenarios

#### Test Fixtures
The test suite includes comprehensive fixtures for:
- Sample MCP requests and responses
- Mock HTTP responses and sessions
- Test tools and resources
- Sample data for various scenarios
- Async event loop management

## Dependencies

- `aiohttp>=3.8.0` - Asynchronous HTTP client/server framework
- `aiohttp-cors>=0.7.0` - CORS support for aiohttp
- `psutil>=5.9.0` - System and process utilities
- `pytest` - Testing framework (for running tests)

## Model Context Protocol Specification

This implementation follows the Model Context Protocol specification. For more details about the protocol, visit:
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)

## License

This implementation is part of the OpenAGI Codes AI Agents Basics project and is available under the [MIT License](LICENSE).
