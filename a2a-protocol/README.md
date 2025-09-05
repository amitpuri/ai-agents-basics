# A2A (Agent-to-Agent) JSON-RPC Implementation

This directory contains a complete implementation of an Agent-to-Agent communication protocol using the `a2a-json-rpc` library. The implementation demonstrates how AI agents can communicate with each other using JSON-RPC 2.0 protocol.

## Files

- `server.py` - A2A JSON-RPC Server implementation
- `client.py` - A2A JSON-RPC Client implementation  
- `requirements.txt` - Python dependencies
- `README.md` - This documentation file

## Features

### Server (`server.py`)

- **Multiple Method Handlers**: Implements three main agent methods:
  - `agent/status` - Get agent status and capabilities
  - `task/process` - Process agent tasks with various types
  - `data/analyze` - Analyze data with different analysis types

- **Async Support**: Full asynchronous implementation using asyncio
- **Error Handling**: Comprehensive error handling with proper JSON-RPC error responses
- **Logging**: Detailed logging for debugging and monitoring
- **Extensible**: Easy to add new methods and handlers

### Client (`client.py`)

- **A2AClient Class**: Clean, object-oriented client implementation
- **Method Wrappers**: Convenient methods for all server operations
- **Batch Processing**: Support for processing multiple tasks concurrently
- **Error Handling**: Robust error handling and recovery
- **Interactive Mode**: Command-line interface for manual testing
- **Examples**: Comprehensive examples demonstrating all features


## Installation

1. Install the required dependency:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

The server can be run directly to see example requests being processed:

```bash
python server.py
```

This will run a simulation showing how the server processes various types of requests.

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
- `status` - Get agent status
- `task <id> [type]` - Process a task
- `analyze <data> [type]` - Analyze data
- `quit` - Exit


## API Reference

### Server Methods

#### `agent/status`
Get agent status and capabilities.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "agent/status",
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "status": "active",
    "capabilities": ["task/process", "agent/status", "data/analyze"],
    "uptime": 1234567890.123,
    "version": "1.0.0"
  }
}
```

#### `task/process`
Process an agent task.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "task/process",
  "params": {
    "task_id": "task_001",
    "task_type": "analysis",
    "data": {"input": "sample data"}
  },
  "id": 2
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "task_id": "task_001",
    "status": "completed",
    "result": "Task task_001 processed successfully",
    "processed_data": {"input": "sample data"},
    "timestamp": 1234567890.123
  }
}
```

#### `data/analyze`
Analyze provided data.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "data/analyze",
  "params": {
    "data": [1, 2, 3, 4, 5],
    "analysis_type": "statistical"
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
    "count": 5,
    "analysis_type": "statistical",
    "summary": "Analyzed 5 items",
    "insights": ["Data appears to be structured", "No anomalies detected"]
  }
}
```

### Client Methods

#### `A2AClient.get_agent_status()`
```python
status = await client.get_agent_status()
```

#### `A2AClient.process_task(task_id, task_type, data)`
```python
result = await client.process_task(
    task_id="my_task",
    task_type="analysis", 
    data={"input": "data"}
)
```

#### `A2AClient.analyze_data(data, analysis_type)`
```python
analysis = await client.analyze_data(
    data=[1, 2, 3, 4, 5],
    analysis_type="statistical"
)
```

#### `A2AClient.batch_process_tasks(tasks)`
```python
tasks = [
    {"task_id": "task1", "task_type": "processing", "data": {"item": 1}},
    {"task_id": "task2", "task_type": "validation", "data": {"item": 2}}
]
results = await client.batch_process_tasks(tasks)
```

## Error Handling

The implementation includes comprehensive error handling:

- **JSON Parse Errors**: Invalid JSON requests are handled gracefully
- **Method Not Found**: Unknown methods return proper JSON-RPC error responses
- **Internal Errors**: Server errors are caught and returned as error responses
- **Client Errors**: Client-side errors are logged and handled appropriately

## Extending the Implementation

### Adding New Server Methods

1. Create a new async function:
```python
@protocol.method("new/method")
async def new_method(method: str, params: Json) -> Json:
    # Implementation here
    return {"result": "success"}
```

2. Add corresponding client method:
```python
async def new_method(self, param1: str, param2: int) -> Dict[str, Any]:
    params = {"param1": param1, "param2": param2}
    return await self._send_request("new/method", params)
```

### Adding Real Network Transport

The current implementation simulates server responses for testing. To add real network transport:

1. Replace `_simulate_server_response` in the client with actual HTTP/WebSocket calls
2. Add a real HTTP server in the server implementation
3. Update the `handle_agent_request` function to work with real network requests


## Dependencies

- `a2a-json-rpc` - Core JSON-RPC protocol implementation
- `asyncio` - Asynchronous programming support (built-in)
- `json` - JSON handling (built-in)
- `logging` - Logging support (built-in)
- `typing` - Type hints (built-in)

## License

This implementation is part of the OpenAGI Codes AI Agents Basics project and is available under the [MIT License](LICENSE).