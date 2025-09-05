"""
Pytest configuration and fixtures for MCP tests
"""
import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def sample_requests():
    """Fixture providing sample MCP requests"""
    return {
        "initialize": {
            "method": "initialize",
            "id": 1,
            "params": {
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        },
        "tools_list": {
            "method": "tools/list",
            "id": 2,
            "params": {}
        },
        "tools_call": {
            "method": "tools/call",
            "id": 3,
            "params": {
                "name": "get_weather",
                "arguments": {"location": "New York"}
            }
        },
        "resources_list": {
            "method": "resources/list",
            "id": 4,
            "params": {}
        },
        "resources_read": {
            "method": "resources/read",
            "id": 5,
            "params": {"uri": "file:///test.txt"}
        },
        "invalid_method": {
            "method": "unknown/method",
            "id": 6,
            "params": {}
        },
        "invalid_json": '{"method": "initialize", "id": 7, "params": {}',
        "notification": {
            "method": "tools/list",
            "params": {}
        }
    }


@pytest.fixture
def expected_responses():
    """Fixture providing expected MCP responses"""
    return {
        "initialize": {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True}
                },
                "serverInfo": {
                    "name": "test-server",
                    "version": "1.0.0"
                }
            }
        },
        "tools_list": {
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
        },
        "tools_call": {
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
        },
        "resources_list": {
            "jsonrpc": "2.0",
            "id": 4,
            "result": {
                "resources": [
                    {
                        "uri": "file:///test.txt",
                        "name": "Test Resource",
                        "description": "A test resource",
                        "mimeType": "text/plain"
                    }
                ]
            }
        },
        "resources_read": {
            "jsonrpc": "2.0",
            "id": 5,
            "result": {
                "contents": [
                    {
                        "uri": "file:///test.txt",
                        "mimeType": "text/plain",
                        "text": "This is test content"
                    }
                ]
            }
        },
        "method_not_found": {
            "jsonrpc": "2.0",
            "id": 6,
            "error": {
                "code": -32601,
                "message": "Method not found",
                "data": "Method 'unknown/method' not found"
            }
        },
        "parse_error": {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error",
                "data": "Expecting ',' delimiter: line 1 column 45 (char 44)"
            }
        }
    }


@pytest.fixture
def sample_tools():
    """Fixture providing sample MCP tools"""
    return {
        "weather_tool": {
            "name": "get_weather",
            "description": "Get current weather information for a specified location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or location to get weather for"
                    }
                },
                "required": ["location"]
            }
        },
        "math_tool": {
            "name": "calculate_math",
            "description": "Calculate mathematical expressions safely",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to calculate"
                    }
                },
                "required": ["expression"]
            }
        },
        "system_tool": {
            "name": "get_system_info",
            "description": "Get system information including platform, CPU, memory, etc.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }


@pytest.fixture
def sample_resources():
    """Fixture providing sample MCP resources"""
    return {
        "text_resource": {
            "uri": "file:///test.txt",
            "name": "Test Text Resource",
            "description": "A test text resource",
            "mime_type": "text/plain",
            "content": "This is test content for a text resource."
        },
        "json_resource": {
            "uri": "file:///data.json",
            "name": "Test JSON Resource",
            "description": "A test JSON resource",
            "mime_type": "application/json",
            "content": json.dumps({
                "users": [
                    {"id": 1, "name": "Alice", "email": "alice@example.com"},
                    {"id": 2, "name": "Bob", "email": "bob@example.com"}
                ],
                "metadata": {
                    "created_at": "2024-01-01",
                    "version": "1.0"
                }
            }, indent=2)
        },
        "yaml_resource": {
            "uri": "file:///config.yaml",
            "name": "Configuration Resource",
            "description": "Server configuration file",
            "mime_type": "text/yaml",
            "content": """# Test Configuration
server:
  name: "test-server"
  version: "1.0.0"
  port: 8000

features:
  weather: true
  math: true
  system_info: true
"""
        }
    }


@pytest.fixture
def sample_tool_calls():
    """Fixture providing sample tool calls"""
    return [
        {
            "name": "get_weather",
            "arguments": {"location": "London"}
        },
        {
            "name": "calculate_math",
            "arguments": {"expression": "2 + 3 * 4"}
        },
        {
            "name": "get_system_info",
            "arguments": {}
        },
        {
            "name": "search_files",
            "arguments": {"query": "*.py", "directory": "."}
        }
    ]


@pytest.fixture
def sample_tool_results():
    """Fixture providing sample tool results"""
    return {
        "weather": {
            "content": [
                {
                    "type": "text",
                    "text": "Weather in London: Cloudy, 15°C"
                }
            ]
        },
        "math": {
            "content": [
                {
                    "type": "text",
                    "text": "Result: 14"
                }
            ]
        },
        "system_info": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "platform": "Windows",
                        "platform_version": "10.0.19041",
                        "architecture": "64bit",
                        "python_version": "3.9.0",
                        "cpu_count": 8,
                        "memory_total": "16.0 GB"
                    }, indent=2)
                }
            ]
        },
        "file_search": {
            "content": [
                {
                    "type": "text",
                    "text": "Found 3 files matching '*.py':\n- server.py\n- client.py\n- test.py"
                }
            ]
        }
    }


@pytest.fixture
def mock_aiohttp_response():
    """Fixture for creating mock aiohttp responses"""
    def _create_response(status=200, json_data=None, text_data=None):
        response = MagicMock()
        response.status = status
        
        if json_data:
            response.json = AsyncMock(return_value=json_data)
        if text_data:
            response.text = AsyncMock(return_value=text_data)
        
        return response
    
    return _create_response


@pytest.fixture
def mock_aiohttp_session():
    """Fixture for creating mock aiohttp sessions"""
    def _create_session(responses=None):
        session = MagicMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=None)
        
        if responses:
            session.post.return_value.__aenter__ = AsyncMock(return_value=responses)
            session.get.return_value.__aenter__ = AsyncMock(return_value=responses)
        
        return session
    
    return _create_session


@pytest.fixture
def mcp_client():
    """Fixture to create MCP client instance"""
    from client import MCPClient
    return MCPClient("http://localhost:8000")


@pytest.fixture
def mcp_server():
    """Fixture to create MCP server instance"""
    from server import MCPServer
    return MCPServer("test-server", "1.0.0")


@pytest.fixture
def sample_weather_data():
    """Fixture providing sample weather data"""
    return {
        "New York": "Sunny, 22°C",
        "London": "Cloudy, 15°C",
        "Tokyo": "Rainy, 18°C",
        "Paris": "Partly cloudy, 20°C",
        "Sydney": "Clear, 25°C"
    }


@pytest.fixture
def sample_math_expressions():
    """Fixture providing sample math expressions"""
    return {
        "simple": "2 + 3",
        "complex": "2 + 3 * 4 - 1",
        "with_parentheses": "(10 + 5) * 2",
        "division": "15 / 3",
        "decimal": "3.14 * 2",
        "invalid": "2 + + 3",
        "invalid_chars": "2 + import os"
    }


@pytest.fixture
def sample_system_info():
    """Fixture providing sample system information"""
    return {
        "platform": "Windows",
        "platform_version": "10.0.19041",
        "architecture": "64bit",
        "processor": "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel",
        "python_version": "3.9.0",
        "cpu_count": 8,
        "memory_total": "16.0 GB"
    }


@pytest.fixture
def sample_file_search_results():
    """Fixture providing sample file search results"""
    return {
        "python_files": ["server.py", "client.py", "test.py", "utils.py"],
        "text_files": ["README.txt", "config.txt", "notes.txt"],
        "json_files": ["config.json", "data.json", "settings.json"],
        "no_results": []
    }


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_server_responses():
    """Fixture providing mock server responses for different scenarios"""
    return {
        "success": {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"status": "success"}
        },
        "error": {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32603,
                "message": "Internal error"
            }
        },
        "method_not_found": {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        },
        "invalid_params": {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32602,
                "message": "Invalid params"
            }
        }
    }
