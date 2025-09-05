"""
Tests for A2A Protocol Server implementation
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
    handle_agent_request,
    process_task,
    get_agent_status,
    analyze_data,
    run_server
)


class TestA2AServer:
    """Test cases for A2A server functionality"""
    
    @pytest.mark.asyncio
    async def test_process_task_success(self):
        """Test successful task processing"""
        # Test data
        method = "task/process"
        params = {
            "task_id": "test_task_001",
            "task_type": "analysis",
            "data": {"input": "test data", "priority": "high"}
        }
        
        # Call the function
        result = await process_task(method, params)
        
        # Assertions
        assert result["task_id"] == "test_task_001"
        assert result["status"] == "completed"
        assert "result" in result
        assert "processed_data" in result
        assert "timestamp" in result
        assert result["processed_data"] == params["data"]
    
    @pytest.mark.asyncio
    async def test_get_agent_status(self):
        """Test agent status retrieval"""
        # Test data
        method = "agent/status"
        params = {}
        
        # Call the function
        result = await get_agent_status(method, params)
        
        # Assertions
        assert result["status"] == "active"
        assert "capabilities" in result
        assert "uptime" in result
        assert "version" in result
        assert "task/process" in result["capabilities"]
        assert "agent/status" in result["capabilities"]
        assert "data/analyze" in result["capabilities"]
    
    @pytest.mark.asyncio
    async def test_analyze_data_list(self):
        """Test data analysis with list data"""
        # Test data
        method = "data/analyze"
        params = {
            "data": [1, 2, 3, 4, 5],
            "analysis_type": "statistical"
        }
        
        # Call the function
        result = await analyze_data(method, params)
        
        # Assertions
        assert result["count"] == 5
        assert result["analysis_type"] == "statistical"
        assert "summary" in result
        assert "insights" in result
        assert len(result["insights"]) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_data_single_item(self):
        """Test data analysis with single item"""
        # Test data
        method = "data/analyze"
        params = {
            "data": "single item",
            "analysis_type": "basic"
        }
        
        # Call the function
        result = await analyze_data(method, params)
        
        # Assertions
        assert result["analysis_type"] == "basic"
        assert "summary" in result
        assert "insights" in result
        assert "count" not in result  # Should not have count for single item
    
    @pytest.mark.asyncio
    async def test_handle_agent_request_success(self):
        """Test successful agent request handling"""
        # Test data
        request_data = json.dumps({
            "method": "agent/status",
            "id": 1,
            "params": {}
        })
        
        # Call the function
        response = await handle_agent_request(request_data)
        response_data = json.loads(response)
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 1
        assert "result" in response_data
        assert "error" not in response_data
        assert response_data["result"]["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_handle_agent_request_task_processing(self):
        """Test task processing request handling"""
        # Test data
        request_data = json.dumps({
            "method": "task/process",
            "id": 2,
            "params": {
                "task_id": "test_task_002",
                "task_type": "processing",
                "data": {"test": "data"}
            }
        })
        
        # Call the function
        response = await handle_agent_request(request_data)
        response_data = json.loads(response)
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 2
        assert "result" in response_data
        assert "error" not in response_data
        assert response_data["result"]["task_id"] == "test_task_002"
        assert response_data["result"]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_handle_agent_request_data_analysis(self):
        """Test data analysis request handling"""
        # Test data
        request_data = json.dumps({
            "method": "data/analyze",
            "id": 3,
            "params": {
                "data": [10, 20, 30],
                "analysis_type": "basic"
            }
        })
        
        # Call the function
        response = await handle_agent_request(request_data)
        response_data = json.loads(response)
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 3
        assert "result" in response_data
        assert "error" not in response_data
        assert response_data["result"]["count"] == 3
        assert response_data["result"]["analysis_type"] == "basic"
    
    @pytest.mark.asyncio
    async def test_handle_agent_request_method_not_found(self):
        """Test handling of unknown method"""
        # Test data
        request_data = json.dumps({
            "method": "unknown/method",
            "id": 4,
            "params": {}
        })
        
        # Call the function
        response = await handle_agent_request(request_data)
        response_data = json.loads(response)
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 4
        assert "error" in response_data
        assert "result" not in response_data
        assert response_data["error"]["code"] == -32601
        assert response_data["error"]["message"] == "Method not found"
    
    @pytest.mark.asyncio
    async def test_handle_agent_request_invalid_json(self):
        """Test handling of invalid JSON"""
        # Test data - invalid JSON
        request_data = '{"method": "agent/status", "id": 5, "params": {}'
        
        # Call the function
        response = await handle_agent_request(request_data)
        response_data = json.loads(response)
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] is None
        assert "error" in response_data
        assert "result" not in response_data
        assert response_data["error"]["code"] == -32700
        assert response_data["error"]["message"] == "Parse error"
    
    @pytest.mark.asyncio
    async def test_handle_agent_request_missing_method(self):
        """Test handling of request without method"""
        # Test data
        request_data = json.dumps({
            "id": 6,
            "params": {}
        })
        
        # Call the function
        response = await handle_agent_request(request_data)
        response_data = json.loads(response)
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 6
        assert "error" in response_data
        assert "result" not in response_data
        assert response_data["error"]["code"] == -32601
        assert response_data["error"]["message"] == "Method not found"
    
    @pytest.mark.asyncio
    async def test_handle_agent_request_missing_id(self):
        """Test handling of request without id"""
        # Test data
        request_data = json.dumps({
            "method": "agent/status",
            "params": {}
        })
        
        # Call the function
        response = await handle_agent_request(request_data)
        response_data = json.loads(response)
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] is None
        assert "result" in response_data
        assert "error" not in response_data
        assert response_data["result"]["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_handle_agent_request_empty_params(self):
        """Test handling of request with empty params"""
        # Test data
        request_data = json.dumps({
            "method": "agent/status",
            "id": 7,
            "params": None
        })
        
        # Call the function
        response = await handle_agent_request(request_data)
        response_data = json.loads(response)
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 7
        assert "result" in response_data
        assert "error" not in response_data
        assert response_data["result"]["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_process_task_with_minimal_params(self):
        """Test task processing with minimal parameters"""
        # Test data
        method = "task/process"
        params = {
            "task_id": "minimal_task"
        }
        
        # Call the function
        result = await process_task(method, params)
        
        # Assertions
        assert result["task_id"] == "minimal_task"
        assert result["status"] == "completed"
        assert result["task_type"] == "general"  # Default value
        assert result["processed_data"] == {}  # Default empty dict
    
    @pytest.mark.asyncio
    async def test_analyze_data_with_defaults(self):
        """Test data analysis with default parameters"""
        # Test data
        method = "data/analyze"
        params = {
            "data": [1, 2, 3]
        }
        
        # Call the function
        result = await analyze_data(method, params)
        
        # Assertions
        assert result["count"] == 3
        assert result["analysis_type"] == "basic"  # Default value
        assert "summary" in result
        assert "insights" in result


class TestA2AServerIntegration:
    """Integration tests for A2A server"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow from request to response"""
        # Test workflow: status -> task processing -> data analysis
        
        # 1. Get agent status
        status_request = json.dumps({
            "method": "agent/status",
            "id": 1,
            "params": {}
        })
        
        status_response = await handle_agent_request(status_request)
        status_data = json.loads(status_response)
        
        assert status_data["result"]["status"] == "active"
        
        # 2. Process a task
        task_request = json.dumps({
            "method": "task/process",
            "id": 2,
            "params": {
                "task_id": "workflow_task",
                "task_type": "analysis",
                "data": {"items": [1, 2, 3, 4, 5]}
            }
        })
        
        task_response = await handle_agent_request(task_request)
        task_data = json.loads(task_response)
        
        assert task_data["result"]["status"] == "completed"
        
        # 3. Analyze the processed data
        analysis_request = json.dumps({
            "method": "data/analyze",
            "id": 3,
            "params": {
                "data": task_data["result"]["processed_data"]["items"],
                "analysis_type": "statistical"
            }
        })
        
        analysis_response = await handle_agent_request(analysis_request)
        analysis_data = json.loads(analysis_response)
        
        assert analysis_data["result"]["count"] == 5
        assert analysis_data["result"]["analysis_type"] == "statistical"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        # Create multiple concurrent requests
        requests = []
        for i in range(5):
            request_data = json.dumps({
                "method": "agent/status",
                "id": i + 1,
                "params": {}
            })
            requests.append(handle_agent_request(request_data))
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*requests)
        
        # Verify all responses
        for i, response in enumerate(responses):
            response_data = json.loads(response)
            assert response_data["jsonrpc"] == "2.0"
            assert response_data["id"] == i + 1
            assert "result" in response_data
            assert response_data["result"]["status"] == "active"


if __name__ == "__main__":
    pytest.main([__file__])
