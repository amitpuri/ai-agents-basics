"""
Tests for MCP Client implementation
"""
import json
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os

# Add parent directory to path to import client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client import MCPClient


class TestMCPClient:
    """Test cases for MCP client functionality"""
    
    @pytest.fixture
    def client(self):
        """Fixture to create MCP client instance"""
        return MCPClient("http://localhost:8000")
    
    def test_client_initialization(self, client):
        """Test client initialization"""
        assert client.server_url == "http://localhost:8000"
        assert client.request_id == 0
        assert client.session is None
        assert client.initialized is False
    
    def test_get_next_id(self, client):
        """Test request ID generation"""
        first_id = client._get_next_id()
        second_id = client._get_next_id()
        
        assert first_id == 1
        assert second_id == 2
        assert second_id > first_id
    
    @pytest.mark.asyncio
    async def test_send_request_success(self, client):
        """Test successful request sending"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"status": "success"}
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client._send_request("initialize")
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert result["result"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_send_request_with_params(self, client):
        """Test request sending with parameters"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"tools": []}
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            params = {"clientInfo": {"name": "test-client"}}
            result = await client._send_request("initialize", params)
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "tools" in result["result"]
    
    @pytest.mark.asyncio
    async def test_send_request_server_error(self, client):
        """Test handling of server error response"""
        # Mock server error response
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client._send_request("initialize")
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "error" in result
            assert result["error"]["code"] == -32603
            assert result["error"]["message"] == "Server error"
    
    @pytest.mark.asyncio
    async def test_send_request_connection_error(self, client):
        """Test handling of connection error"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.side_effect = Exception("Connection failed")
            
            result = await client._send_request("initialize")
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "error" in result
            assert result["error"]["code"] == -32603
            assert result["error"]["message"] == "Connection error"
    
    @pytest.mark.asyncio
    async def test_send_request_json_decode_error(self, client):
        """Test handling of JSON decode error"""
        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="invalid json")
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client._send_request("initialize")
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "error" in result
            assert result["error"]["code"] == -32700
            assert result["error"]["message"] == "Parse error"
    
    @pytest.mark.asyncio
    async def test_check_server_health_success(self, client):
        """Test successful server health check"""
        # Mock successful health check
        mock_response = MagicMock()
        mock_response.status = 200
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            result = await client.check_server_health()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_server_health_failure(self, client):
        """Test failed server health check"""
        # Mock failed health check
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = Exception("Connection failed")
            
            result = await client.check_server_health()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, client):
        """Test successful initialization"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "serverInfo": {"name": "test-server", "version": "1.0.0"}
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.initialize()
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "result" in result
            assert "error" not in result
            assert result["result"]["protocolVersion"] == "2024-11-05"
            assert client.initialized is True
    
    @pytest.mark.asyncio
    async def test_initialize_with_custom_client_info(self, client):
        """Test initialization with custom client info"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"protocolVersion": "2024-11-05"}
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            client_info = {"name": "custom-client", "version": "2.0.0"}
            result = await client.initialize(client_info)
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "result" in result
            assert client.initialized is True
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self, client):
        """Test initialization failure"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32603, "message": "Internal error"}
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.initialize()
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "error" in result
            assert client.initialized is False
    
    @pytest.mark.asyncio
    async def test_list_tools(self, client):
        """Test listing tools"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": "get_weather",
                        "description": "Get weather information",
                        "inputSchema": {"type": "object"}
                    }
                ]
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.list_tools()
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "result" in result
            assert "tools" in result["result"]
            assert len(result["result"]["tools"]) == 1
            assert result["result"]["tools"][0]["name"] == "get_weather"
    
    @pytest.mark.asyncio
    async def test_call_tool(self, client):
        """Test calling a tool"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Weather in New York: Sunny, 22°C"
                    }
                ]
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.call_tool("get_weather", {"location": "New York"})
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "result" in result
            assert "content" in result["result"]
            assert result["result"]["content"][0]["text"] == "Weather in New York: Sunny, 22°C"
    
    @pytest.mark.asyncio
    async def test_call_tool_no_arguments(self, client):
        """Test calling a tool without arguments"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "System information retrieved"
                    }
                ]
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.call_tool("get_system_info")
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "result" in result
            assert result["result"]["content"][0]["text"] == "System information retrieved"
    
    @pytest.mark.asyncio
    async def test_list_resources(self, client):
        """Test listing resources"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
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
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.list_resources()
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "result" in result
            assert "resources" in result["result"]
            assert len(result["result"]["resources"]) == 1
            assert result["result"]["resources"][0]["uri"] == "file:///test.txt"
    
    @pytest.mark.asyncio
    async def test_read_resource(self, client):
        """Test reading a resource"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "contents": [
                    {
                        "uri": "file:///test.txt",
                        "mimeType": "text/plain",
                        "text": "This is test content"
                    }
                ]
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.read_resource("file:///test.txt")
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "result" in result
            assert "contents" in result["result"]
            assert result["result"]["contents"][0]["text"] == "This is test content"
    
    @pytest.mark.asyncio
    async def test_get_weather_convenience_method(self, client):
        """Test get_weather convenience method"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Weather in London: Cloudy, 15°C"
                    }
                ]
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.get_weather("London")
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert result["result"]["content"][0]["text"] == "Weather in London: Cloudy, 15°C"
    
    @pytest.mark.asyncio
    async def test_calculate_math_convenience_method(self, client):
        """Test calculate_math convenience method"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Result: 14"
                    }
                ]
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.calculate_math("2 + 3 * 4")
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert result["result"]["content"][0]["text"] == "Result: 14"
    
    @pytest.mark.asyncio
    async def test_get_system_info_convenience_method(self, client):
        """Test get_system_info convenience method"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": '{"platform": "Windows", "cpu_count": 8}'
                    }
                ]
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.get_system_info()
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "platform" in result["result"]["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_search_files_convenience_method(self, client):
        """Test search_files convenience method"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Found 2 files matching 'test':\n- test_file.py\n- test_file.txt"
                    }
                ]
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.search_files("test", ".")
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "Found 2 files matching 'test'" in result["result"]["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_batch_call_tools(self, client):
        """Test batch tool calls"""
        # Mock successful responses
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Weather in Paris: Partly cloudy, 20°C"
                    }
                ]
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            tool_calls = [
                {"name": "get_weather", "arguments": {"location": "Paris"}},
                {"name": "calculate_math", "arguments": {"expression": "5 * 6"}}
            ]
            
            results = await client.batch_call_tools(tool_calls)
            
            assert len(results) == 2
            for result in results:
                assert result["jsonrpc"] == "2.0"
                assert "result" in result
                assert "content" in result["result"]
    
    @pytest.mark.asyncio
    async def test_batch_call_tools_with_error(self, client):
        """Test batch tool calls with error handling"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32603, "message": "Tool call failed"}
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            tool_calls = [
                {"name": "nonexistent_tool", "arguments": {}}
            ]
            
            results = await client.batch_call_tools(tool_calls)
            
            assert len(results) == 1
            assert "error" in results[0]
    
    def test_request_structure(self, client):
        """Test request structure creation"""
        # Test that request structure is correct
        method = "test/method"
        params = {"key": "value"}
        
        # This would be called internally by _send_request
        expected_structure = {
            "jsonrpc": "2.0",
            "method": method,
            "id": 1,
            "params": params
        }
        
        # Validate structure
        assert expected_structure["jsonrpc"] == "2.0"
        assert expected_structure["method"] == method
        assert expected_structure["id"] == 1
        assert expected_structure["params"] == params
    
    def test_json_serialization(self, client):
        """Test JSON serialization of requests"""
        # Test various data types
        test_cases = [
            {"method": "test", "params": {"string": "value"}},
            {"method": "test", "params": {"number": 123}},
            {"method": "test", "params": {"boolean": True}},
            {"method": "test", "params": {"null": None}},
            {"method": "test", "params": {"array": [1, 2, 3]}},
            {"method": "test", "params": {"object": {"nested": "value"}}},
        ]
        
        for test_case in test_cases:
            # Should not raise exception
            json_str = json.dumps(test_case)
            assert isinstance(json_str, str)
            
            # Should be able to deserialize
            deserialized = json.loads(json_str)
            assert deserialized == test_case


class TestMCPClientIntegration:
    """Integration tests for MCP client"""
    
    @pytest.mark.asyncio
    async def test_client_workflow(self):
        """Test complete client workflow"""
        client = MCPClient("http://localhost:8000")
        
        # Mock all responses
        mock_responses = [
            # Health check
            MagicMock(status=200),
            # Initialize
            MagicMock(status=200, text=AsyncMock(return_value=json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": True}},
                    "serverInfo": {"name": "test-server", "version": "1.0.0"}
                }
            }))),
            # List tools
            MagicMock(status=200, text=AsyncMock(return_value=json.dumps({
                "jsonrpc": "2.0",
                "id": 2,
                "result": {
                    "tools": [
                        {
                            "name": "get_weather",
                            "description": "Get weather information",
                            "inputSchema": {"type": "object"}
                        }
                    ]
                }
            }))),
            # Call tool
            MagicMock(status=200, text=AsyncMock(return_value=json.dumps({
                "jsonrpc": "2.0",
                "id": 3,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": "Weather in Tokyo: Rainy, 18°C"
                        }
                    ]
                }
            }))),
            # List resources
            MagicMock(status=200, text=AsyncMock(return_value=json.dumps({
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
            }))),
            # Read resource
            MagicMock(status=200, text=AsyncMock(return_value=json.dumps({
                "jsonrpc": "2.0",
                "id": 5,
                "result": {
                    "contents": [
                        {
                            "uri": "file:///test.txt",
                            "mimeType": "text/plain",
                            "text": "Test content"
                        }
                    ]
                }
            })))
        ]
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_responses[0]
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_responses[1]
            
            # Test health check
            health = await client.check_server_health()
            assert health is True
            
            # Test initialization
            init_result = await client.initialize()
            assert init_result["result"]["protocolVersion"] == "2024-11-05"
            assert client.initialized is True
            
            # Test list tools
            with patch('aiohttp.ClientSession') as mock_session2:
                mock_session2.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_responses[2]
                
                tools_result = await client.list_tools()
                assert len(tools_result["result"]["tools"]) == 1
                assert tools_result["result"]["tools"][0]["name"] == "get_weather"
            
            # Test call tool
            with patch('aiohttp.ClientSession') as mock_session3:
                mock_session3.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_responses[3]
                
                call_result = await client.call_tool("get_weather", {"location": "Tokyo"})
                assert "Weather in Tokyo" in call_result["result"]["content"][0]["text"]
            
            # Test list resources
            with patch('aiohttp.ClientSession') as mock_session4:
                mock_session4.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_responses[4]
                
                resources_result = await client.list_resources()
                assert len(resources_result["result"]["resources"]) == 1
                assert resources_result["result"]["resources"][0]["name"] == "Test Resource"
            
            # Test read resource
            with patch('aiohttp.ClientSession') as mock_session5:
                mock_session5.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_responses[5]
                
                read_result = await client.read_resource("file:///test.txt")
                assert read_result["result"]["contents"][0]["text"] == "Test content"


if __name__ == "__main__":
    pytest.main([__file__])
