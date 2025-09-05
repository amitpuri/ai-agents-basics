"""
Tests for A2A Protocol Client implementation
"""
import json
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os

# Add parent directory to path to import client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client import A2AClient


class TestA2AClient:
    """Test cases for A2A client functionality"""
    
    @pytest.fixture
    def client(self):
        """Fixture to create A2A client instance"""
        return A2AClient("http://localhost:8000")
    
    def test_client_initialization(self, client):
        """Test client initialization"""
        assert client.server_url == "http://localhost:8000"
        assert client.request_id == 0
        assert client.session is None
    
    def test_get_next_id(self, client):
        """Test request ID generation"""
        # Test first ID
        first_id = client._get_next_id()
        assert first_id == 1
        
        # Test second ID
        second_id = client._get_next_id()
        assert second_id == 2
        
        # Test that IDs are sequential
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
            "result": {"status": "active"}
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client._send_request("agent/status")
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert result["result"]["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_send_request_with_params(self, client):
        """Test request sending with parameters"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"task_id": "test_task", "status": "completed"}
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            params = {"task_id": "test_task", "task_type": "analysis"}
            result = await client._send_request("task/process", params)
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert result["result"]["task_id"] == "test_task"
    
    @pytest.mark.asyncio
    async def test_send_request_server_error(self, client):
        """Test handling of server error response"""
        # Mock server error response
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client._send_request("agent/status")
            
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
            
            result = await client._send_request("agent/status")
            
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
            
            result = await client._send_request("agent/status")
            
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
    async def test_get_agent_status(self, client):
        """Test getting agent status"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "status": "active",
                "capabilities": ["task/process", "agent/status"],
                "uptime": 123.45,
                "version": "1.0.0"
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.get_agent_status()
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert result["result"]["status"] == "active"
            assert "task/process" in result["result"]["capabilities"]
    
    @pytest.mark.asyncio
    async def test_process_task(self, client):
        """Test task processing"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "task_id": "test_task",
                "status": "completed",
                "result": "Task processed successfully",
                "processed_data": {"input": "test data"},
                "timestamp": 123.45
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.process_task(
                task_id="test_task",
                task_type="analysis",
                data={"input": "test data"}
            )
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert result["result"]["task_id"] == "test_task"
            assert result["result"]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_process_task_minimal_params(self, client):
        """Test task processing with minimal parameters"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "task_id": "minimal_task",
                "status": "completed",
                "result": "Task processed successfully",
                "processed_data": {},
                "timestamp": 123.45
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.process_task(task_id="minimal_task")
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert result["result"]["task_id"] == "minimal_task"
    
    @pytest.mark.asyncio
    async def test_analyze_data(self, client):
        """Test data analysis"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "count": 3,
                "analysis_type": "basic",
                "summary": "Analyzed 3 items",
                "insights": ["Data appears to be structured"]
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.analyze_data(
                data=[1, 2, 3],
                analysis_type="basic"
            )
            
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert result["result"]["count"] == 3
            assert result["result"]["analysis_type"] == "basic"
    
    @pytest.mark.asyncio
    async def test_batch_process_tasks(self, client):
        """Test batch task processing"""
        # Mock successful responses
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "task_id": "batch_task",
                "status": "completed",
                "result": "Task processed successfully",
                "processed_data": {},
                "timestamp": 123.45
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            tasks = [
                {"task_id": "batch_001", "task_type": "processing"},
                {"task_id": "batch_002", "task_type": "analysis"}
            ]
            
            results = await client.batch_process_tasks(tasks)
            
            assert len(results) == 2
            for result in results:
                assert result["jsonrpc"] == "2.0"
                assert result["result"]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_batch_process_tasks_with_error(self, client):
        """Test batch task processing with error handling"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32603,
                "message": "Internal error"
            }
        }))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            tasks = [
                {"task_id": "error_task", "task_type": "processing"}
            ]
            
            results = await client.batch_process_tasks(tasks)
            
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


class TestA2AClientIntegration:
    """Integration tests for A2A client"""
    
    @pytest.mark.asyncio
    async def test_client_workflow(self):
        """Test complete client workflow"""
        client = A2AClient("http://localhost:8000")
        
        # Mock all responses
        mock_responses = [
            # Health check
            MagicMock(status=200),
            # Agent status
            MagicMock(status=200, text=AsyncMock(return_value=json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"status": "active", "capabilities": ["task/process"]}
            }))),
            # Task processing
            MagicMock(status=200, text=AsyncMock(return_value=json.dumps({
                "jsonrpc": "2.0",
                "id": 2,
                "result": {"task_id": "workflow_task", "status": "completed"}
            }))),
            # Data analysis
            MagicMock(status=200, text=AsyncMock(return_value=json.dumps({
                "jsonrpc": "2.0",
                "id": 3,
                "result": {"count": 3, "analysis_type": "basic"}
            })))
        ]
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_responses[0]
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_responses[1]
            
            # Test health check
            health = await client.check_server_health()
            assert health is True
            
            # Test agent status
            status = await client.get_agent_status()
            assert status["result"]["status"] == "active"
            
            # Test task processing
            with patch('aiohttp.ClientSession') as mock_session2:
                mock_session2.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_responses[2]
                
                task_result = await client.process_task("workflow_task", "analysis")
                assert task_result["result"]["status"] == "completed"
            
            # Test data analysis
            with patch('aiohttp.ClientSession') as mock_session3:
                mock_session3.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_responses[3]
                
                analysis_result = await client.analyze_data([1, 2, 3])
                assert analysis_result["result"]["count"] == 3


if __name__ == "__main__":
    pytest.main([__file__])
