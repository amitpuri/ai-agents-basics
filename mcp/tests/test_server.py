"""
Tests for MCP Server implementation
"""
import json
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os

# Add parent directory to path to import server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    MCPServer,
    MCPTool,
    MCPResource,
    get_weather,
    calculate_math,
    get_system_info,
    search_files,
    mcp_server
)


class TestMCPTool:
    """Test cases for MCP Tool class"""
    
    def test_tool_initialization(self):
        """Test MCP tool initialization"""
        def test_handler():
            return "test result"
        
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object", "properties": {}},
            handler=test_handler
        )
        
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.input_schema == {"type": "object", "properties": {}}
        assert tool.handler == test_handler
    
    def test_tool_handler_execution(self):
        """Test tool handler execution"""
        def test_handler(param1, param2):
            return f"{param1} + {param2}"
        
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object", "properties": {}},
            handler=test_handler
        )
        
        result = tool.handler("hello", "world")
        assert result == "hello + world"


class TestMCPResource:
    """Test cases for MCP Resource class"""
    
    def test_resource_initialization(self):
        """Test MCP resource initialization"""
        resource = MCPResource(
            uri="file:///test.txt",
            name="Test Resource",
            description="A test resource",
            mime_type="text/plain",
            content="This is test content"
        )
        
        assert resource.uri == "file:///test.txt"
        assert resource.name == "Test Resource"
        assert resource.description == "A test resource"
        assert resource.mime_type == "text/plain"
        assert resource.content == "This is test content"


class TestMCPServer:
    """Test cases for MCP Server class"""
    
    @pytest.fixture
    def server(self):
        """Fixture to create MCP server instance"""
        return MCPServer("test-server", "1.0.0")
    
    def test_server_initialization(self, server):
        """Test MCP server initialization"""
        assert server.name == "test-server"
        assert server.version == "1.0.0"
        assert server.request_id == 0
        assert len(server.tools) == 0
        assert len(server.resources) == 0
    
    def test_get_next_id(self, server):
        """Test request ID generation"""
        first_id = server._get_next_id()
        second_id = server._get_next_id()
        
        assert first_id == 1
        assert second_id == 2
        assert second_id > first_id
    
    def test_register_tool(self, server):
        """Test tool registration"""
        def test_handler():
            return "test"
        
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object"},
            handler=test_handler
        )
        
        server.register_tool(tool)
        
        assert "test_tool" in server.tools
        assert server.tools["test_tool"] == tool
    
    def test_register_resource(self, server):
        """Test resource registration"""
        resource = MCPResource(
            uri="file:///test.txt",
            name="Test Resource",
            description="A test resource",
            mime_type="text/plain",
            content="test content"
        )
        
        server.register_resource(resource)
        
        assert "file:///test.txt" in server.resources
        assert server.resources["file:///test.txt"] == resource
    
    @pytest.mark.asyncio
    async def test_initialize(self, server):
        """Test MCP initialization"""
        params = {
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
        
        result = await server._initialize(params)
        
        assert result["protocolVersion"] == "2024-11-05"
        assert "capabilities" in result
        assert "serverInfo" in result
        assert result["serverInfo"]["name"] == "test-server"
        assert result["serverInfo"]["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_list_tools_empty(self, server):
        """Test listing tools when none are registered"""
        result = await server._list_tools()
        
        assert "tools" in result
        assert result["tools"] == []
    
    @pytest.mark.asyncio
    async def test_list_tools_with_tools(self, server):
        """Test listing tools when tools are registered"""
        def test_handler():
            return "test"
        
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object"},
            handler=test_handler
        )
        
        server.register_tool(tool)
        
        result = await server._list_tools()
        
        assert "tools" in result
        assert len(result["tools"]) == 1
        assert result["tools"][0]["name"] == "test_tool"
        assert result["tools"][0]["description"] == "A test tool"
        assert result["tools"][0]["inputSchema"] == {"type": "object"}
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self, server):
        """Test successful tool call"""
        def test_handler(param1, param2):
            return f"{param1} + {param2}"
        
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object"},
            handler=test_handler
        )
        
        server.register_tool(tool)
        
        params = {
            "name": "test_tool",
            "arguments": {"param1": "hello", "param2": "world"}
        }
        
        result = await server._call_tool(params)
        
        assert "content" in result
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"
        assert result["content"][0]["text"] == "hello + world"
    
    @pytest.mark.asyncio
    async def test_call_tool_async_handler(self, server):
        """Test calling tool with async handler"""
        async def async_handler(param1, param2):
            await asyncio.sleep(0.01)  # Simulate async operation
            return f"{param1} + {param2}"
        
        tool = MCPTool(
            name="async_tool",
            description="An async test tool",
            input_schema={"type": "object"},
            handler=async_handler
        )
        
        server.register_tool(tool)
        
        params = {
            "name": "async_tool",
            "arguments": {"param1": "hello", "param2": "world"}
        }
        
        result = await server._call_tool(params)
        
        assert "content" in result
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"
        assert result["content"][0]["text"] == "hello + world"
    
    @pytest.mark.asyncio
    async def test_call_tool_not_found(self, server):
        """Test calling non-existent tool"""
        params = {
            "name": "nonexistent_tool",
            "arguments": {}
        }
        
        with pytest.raises(ValueError, match="Tool 'nonexistent_tool' not found"):
            await server._call_tool(params)
    
    @pytest.mark.asyncio
    async def test_list_resources_empty(self, server):
        """Test listing resources when none are registered"""
        result = await server._list_resources()
        
        assert "resources" in result
        assert result["resources"] == []
    
    @pytest.mark.asyncio
    async def test_list_resources_with_resources(self, server):
        """Test listing resources when resources are registered"""
        resource = MCPResource(
            uri="file:///test.txt",
            name="Test Resource",
            description="A test resource",
            mime_type="text/plain",
            content="test content"
        )
        
        server.register_resource(resource)
        
        result = await server._list_resources()
        
        assert "resources" in result
        assert len(result["resources"]) == 1
        assert result["resources"][0]["uri"] == "file:///test.txt"
        assert result["resources"][0]["name"] == "Test Resource"
        assert result["resources"][0]["description"] == "A test resource"
        assert result["resources"][0]["mimeType"] == "text/plain"
    
    @pytest.mark.asyncio
    async def test_read_resource_success(self, server):
        """Test successful resource reading"""
        resource = MCPResource(
            uri="file:///test.txt",
            name="Test Resource",
            description="A test resource",
            mime_type="text/plain",
            content="This is test content"
        )
        
        server.register_resource(resource)
        
        params = {"uri": "file:///test.txt"}
        
        result = await server._read_resource(params)
        
        assert "contents" in result
        assert len(result["contents"]) == 1
        assert result["contents"][0]["uri"] == "file:///test.txt"
        assert result["contents"][0]["mimeType"] == "text/plain"
        assert result["contents"][0]["text"] == "This is test content"
    
    @pytest.mark.asyncio
    async def test_read_resource_not_found(self, server):
        """Test reading non-existent resource"""
        params = {"uri": "file:///nonexistent.txt"}
        
        with pytest.raises(ValueError, match="Resource 'file:///nonexistent.txt' not found"):
            await server._read_resource(params)
    
    @pytest.mark.asyncio
    async def test_handle_request_initialize(self, server):
        """Test handling initialize request"""
        request_data = json.dumps({
            "method": "initialize",
            "id": 1,
            "params": {
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        })
        
        response = await server.handle_request(request_data)
        response_data = json.loads(response)
        
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 1
        assert "result" in response_data
        assert "error" not in response_data
        assert response_data["result"]["protocolVersion"] == "2024-11-05"
    
    @pytest.mark.asyncio
    async def test_handle_request_tools_list(self, server):
        """Test handling tools/list request"""
        request_data = json.dumps({
            "method": "tools/list",
            "id": 2,
            "params": {}
        })
        
        response = await server.handle_request(request_data)
        response_data = json.loads(response)
        
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 2
        assert "result" in response_data
        assert "error" not in response_data
        assert "tools" in response_data["result"]
    
    @pytest.mark.asyncio
    async def test_handle_request_tools_call(self, server):
        """Test handling tools/call request"""
        def test_handler(param):
            return f"Hello {param}"
        
        tool = MCPTool(
            name="greet",
            description="A greeting tool",
            input_schema={"type": "object"},
            handler=test_handler
        )
        
        server.register_tool(tool)
        
        request_data = json.dumps({
            "method": "tools/call",
            "id": 3,
            "params": {
                "name": "greet",
                "arguments": {"param": "World"}
            }
        })
        
        response = await server.handle_request(request_data)
        response_data = json.loads(response)
        
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 3
        assert "result" in response_data
        assert "error" not in response_data
        assert response_data["result"]["content"][0]["text"] == "Hello World"
    
    @pytest.mark.asyncio
    async def test_handle_request_resources_list(self, server):
        """Test handling resources/list request"""
        request_data = json.dumps({
            "method": "resources/list",
            "id": 4,
            "params": {}
        })
        
        response = await server.handle_request(request_data)
        response_data = json.loads(response)
        
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 4
        assert "result" in response_data
        assert "error" not in response_data
        assert "resources" in response_data["result"]
    
    @pytest.mark.asyncio
    async def test_handle_request_resources_read(self, server):
        """Test handling resources/read request"""
        resource = MCPResource(
            uri="file:///test.txt",
            name="Test Resource",
            description="A test resource",
            mime_type="text/plain",
            content="Test content"
        )
        
        server.register_resource(resource)
        
        request_data = json.dumps({
            "method": "resources/read",
            "id": 5,
            "params": {"uri": "file:///test.txt"}
        })
        
        response = await server.handle_request(request_data)
        response_data = json.loads(response)
        
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 5
        assert "result" in response_data
        assert "error" not in response_data
        assert response_data["result"]["contents"][0]["text"] == "Test content"
    
    @pytest.mark.asyncio
    async def test_handle_request_method_not_found(self, server):
        """Test handling unknown method"""
        request_data = json.dumps({
            "method": "unknown/method",
            "id": 6,
            "params": {}
        })
        
        response = await server.handle_request(request_data)
        response_data = json.loads(response)
        
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 6
        assert "error" in response_data
        assert "result" not in response_data
        assert response_data["error"]["code"] == -32601
        assert response_data["error"]["message"] == "Method not found"
    
    @pytest.mark.asyncio
    async def test_handle_request_invalid_json(self, server):
        """Test handling invalid JSON"""
        request_data = '{"method": "initialize", "id": 7, "params": {}'
        
        response = await server.handle_request(request_data)
        response_data = json.loads(response)
        
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] is None
        assert "error" in response_data
        assert "result" not in response_data
        assert response_data["error"]["code"] == -32700
        assert response_data["error"]["message"] == "Parse error"


class TestMCPToolHandlers:
    """Test cases for MCP tool handlers"""
    
    @pytest.mark.asyncio
    async def test_get_weather(self):
        """Test weather tool handler"""
        result = await get_weather("New York")
        
        assert "Weather in New York" in result
        assert "Sunny, 22°C" in result
    
    @pytest.mark.asyncio
    async def test_get_weather_unknown_location(self):
        """Test weather tool with unknown location"""
        result = await get_weather("Unknown City")
        
        assert "Weather in Unknown City" in result
        assert "Weather data not available" in result
    
    @pytest.mark.asyncio
    async def test_calculate_math_success(self):
        """Test math calculation tool with valid expression"""
        result = await calculate_math("2 + 3 * 4")
        
        assert "Result: 14" in result
    
    @pytest.mark.asyncio
    async def test_calculate_math_invalid_chars(self):
        """Test math calculation tool with invalid characters"""
        result = await calculate_math("2 + 3 * import os")
        
        assert "Error: Invalid characters in expression" in result
    
    @pytest.mark.asyncio
    async def test_calculate_math_invalid_expression(self):
        """Test math calculation tool with invalid expression"""
        result = await calculate_math("2 + + 3")
        
        assert "Error calculating expression" in result
    
    @pytest.mark.asyncio
    async def test_get_system_info(self):
        """Test system info tool"""
        with patch('platform.system', return_value="Windows"):
            with patch('platform.version', return_value="10.0.19041"):
                with patch('platform.architecture', return_value=("64bit", "WindowsPE")):
                    with patch('platform.processor', return_value="Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"):
                        with patch('platform.python_version', return_value="3.9.0"):
                            with patch('psutil.cpu_count', return_value=8):
                                with patch('psutil.virtual_memory') as mock_memory:
                                    mock_memory.return_value.total = 16 * 1024**3  # 16 GB
                                    
                                    result = await get_system_info()
                                    result_data = json.loads(result)
                                    
                                    assert result_data["platform"] == "Windows"
                                    assert result_data["platform_version"] == "10.0.19041"
                                    assert result_data["architecture"] == "64bit"
                                    assert result_data["processor"] == "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"
                                    assert result_data["python_version"] == "3.9.0"
                                    assert result_data["cpu_count"] == 8
                                    assert result_data["memory_total"] == "16.0 GB"
    
    @pytest.mark.asyncio
    async def test_search_files_success(self):
        """Test file search tool with successful search"""
        with patch('glob.glob', return_value=["test_file.py", "test_file.txt"]):
            result = await search_files("test_file", ".")
            
            assert "Found 2 files matching 'test_file'" in result
            assert "test_file.py" in result
            assert "test_file.txt" in result
    
    @pytest.mark.asyncio
    async def test_search_files_no_results(self):
        """Test file search tool with no results"""
        with patch('glob.glob', return_value=[]):
            result = await search_files("nonexistent", ".")
            
            assert "No files found matching 'nonexistent'" in result
    
    @pytest.mark.asyncio
    async def test_search_files_many_results(self):
        """Test file search tool with many results (truncation)"""
        many_files = [f"file_{i}.txt" for i in range(15)]
        with patch('glob.glob', return_value=many_files):
            result = await search_files("file_", ".")
            
            assert "Found 15 files matching 'file_'" in result
            assert "file_0.txt" in result
            assert "file_9.txt" in result
            assert "... and 5 more files" in result
    
    @pytest.mark.asyncio
    async def test_search_files_error(self):
        """Test file search tool with error"""
        with patch('glob.glob', side_effect=Exception("Permission denied")):
            result = await search_files("test", ".")
            
            assert "Error searching files" in result
            assert "Permission denied" in result


class TestMCPServerIntegration:
    """Integration tests for MCP server"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete MCP workflow"""
        server = MCPServer("integration-test", "1.0.0")
        
        # Register a test tool
        def test_handler(param):
            return f"Processed: {param}"
        
        tool = MCPTool(
            name="test_processor",
            description="A test processor",
            input_schema={"type": "object", "properties": {"param": {"type": "string"}}},
            handler=test_handler
        )
        
        server.register_tool(tool)
        
        # Register a test resource
        resource = MCPResource(
            uri="file:///test_data.json",
            name="Test Data",
            description="Test data resource",
            mime_type="application/json",
            content='{"test": "data"}'
        )
        
        server.register_resource(resource)
        
        # 1. Initialize
        init_request = json.dumps({
            "method": "initialize",
            "id": 1,
            "params": {"clientInfo": {"name": "test-client"}}
        })
        
        init_response = await server.handle_request(init_request)
        init_data = json.loads(init_response)
        
        assert init_data["result"]["serverInfo"]["name"] == "integration-test"
        
        # 2. List tools
        tools_request = json.dumps({
            "method": "tools/list",
            "id": 2,
            "params": {}
        })
        
        tools_response = await server.handle_request(tools_request)
        tools_data = json.loads(tools_response)
        
        assert len(tools_data["result"]["tools"]) == 1
        assert tools_data["result"]["tools"][0]["name"] == "test_processor"
        
        # 3. Call tool
        call_request = json.dumps({
            "method": "tools/call",
            "id": 3,
            "params": {
                "name": "test_processor",
                "arguments": {"param": "test_value"}
            }
        })
        
        call_response = await server.handle_request(call_request)
        call_data = json.loads(call_response)
        
        assert call_data["result"]["content"][0]["text"] == "Processed: test_value"
        
        # 4. List resources
        resources_request = json.dumps({
            "method": "resources/list",
            "id": 4,
            "params": {}
        })
        
        resources_response = await server.handle_request(resources_request)
        resources_data = json.loads(resources_response)
        
        assert len(resources_data["result"]["resources"]) == 1
        assert resources_data["result"]["resources"][0]["name"] == "Test Data"
        
        # 5. Read resource
        read_request = json.dumps({
            "method": "resources/read",
            "id": 5,
            "params": {"uri": "file:///test_data.json"}
        })
        
        read_response = await server.handle_request(read_request)
        read_data = json.loads(read_response)
        
        assert read_data["result"]["contents"][0]["text"] == '{"test": "data"}'


if __name__ == "__main__":
    pytest.main([__file__])
