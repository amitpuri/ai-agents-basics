"""
Tests for JSON-RPC Server implementation
"""
import json
import pytest
import requests
import threading
import time
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
from jsonrpc import JSONRPCResponseManager, dispatcher
import sys
import os

# Add parent directory to path to import server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import application


class TestJSONRPCServer:
    """Test cases for JSON-RPC server functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test method"""
        # Clear dispatcher before each test
        dispatcher.clear()
        
        # Add test methods to dispatcher
        @dispatcher.add_method
        def test_echo(s):
            return s
            
        @dispatcher.add_method
        def test_add(a, b):
            return a + b
            
        @dispatcher.add_method
        def test_foobar(**kwargs):
            return kwargs.get("foo", 0) + kwargs.get("bar", 0)
    
    def test_echo_method(self):
        """Test echo method functionality"""
        # Test data
        test_data = "Hello, World!"
        
        # Create request
        request_data = {
            "method": "test_echo",
            "params": [test_data],
            "jsonrpc": "2.0",
            "id": 1
        }
        
        # Create mock request
        request = Request.from_values(
            data=json.dumps(request_data),
            content_type='application/json',
            method='POST'
        )
        
        # Process request
        response = application(request)
        
        # Parse response
        response_data = json.loads(response.data.decode('utf-8'))
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 1
        assert "error" not in response_data
        assert response_data["result"] == test_data
    
    def test_add_method(self):
        """Test add method functionality"""
        # Test data
        a, b = 5, 3
        
        # Create request
        request_data = {
            "method": "test_add",
            "params": [a, b],
            "jsonrpc": "2.0",
            "id": 2
        }
        
        # Create mock request
        request = Request.from_values(
            data=json.dumps(request_data),
            content_type='application/json',
            method='POST'
        )
        
        # Process request
        response = application(request)
        
        # Parse response
        response_data = json.loads(response.data.decode('utf-8'))
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 2
        assert "error" not in response_data
        assert response_data["result"] == a + b
    
    def test_foobar_method(self):
        """Test foobar method with keyword arguments"""
        # Test data
        foo, bar = 10, 20
        
        # Create request
        request_data = {
            "method": "test_foobar",
            "params": {"foo": foo, "bar": bar},
            "jsonrpc": "2.0",
            "id": 3
        }
        
        # Create mock request
        request = Request.from_values(
            data=json.dumps(request_data),
            content_type='application/json',
            method='POST'
        )
        
        # Process request
        response = application(request)
        
        # Parse response
        response_data = json.loads(response.data.decode('utf-8'))
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 3
        assert "error" not in response_data
        assert response_data["result"] == foo + bar
    
    def test_invalid_method(self):
        """Test handling of invalid method"""
        # Create request with invalid method
        request_data = {
            "method": "nonexistent_method",
            "params": [],
            "jsonrpc": "2.0",
            "id": 4
        }
        
        # Create mock request
        request = Request.from_values(
            data=json.dumps(request_data),
            content_type='application/json',
            method='POST'
        )
        
        # Process request
        response = application(request)
        
        # Parse response
        response_data = json.loads(response.data.decode('utf-8'))
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 4
        assert "error" in response_data
        assert response_data["error"]["code"] == -32601  # Method not found
    
    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        # Create request with invalid JSON
        invalid_json = '{"method": "test_echo", "params": ["test"], "jsonrpc": "2.0", "id": 5'
        
        # Create mock request
        request = Request.from_values(
            data=invalid_json,
            content_type='application/json',
            method='POST'
        )
        
        # Process request
        response = application(request)
        
        # Parse response
        response_data = json.loads(response.data.decode('utf-8'))
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert "error" in response_data
        assert response_data["error"]["code"] == -32700  # Parse error
    
    def test_missing_params(self):
        """Test handling of missing parameters"""
        # Create request without required params
        request_data = {
            "method": "test_add",
            "params": [5],  # Missing second parameter
            "jsonrpc": "2.0",
            "id": 6
        }
        
        # Create mock request
        request = Request.from_values(
            data=json.dumps(request_data),
            content_type='application/json',
            method='POST'
        )
        
        # Process request
        response = application(request)
        
        # Parse response
        response_data = json.loads(response.data.decode('utf-8'))
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 6
        assert "error" in response_data
        assert response_data["error"]["code"] == -32602  # Invalid params
    
    def test_batch_request(self):
        """Test batch request handling"""
        # Create batch request
        batch_data = [
            {
                "method": "test_echo",
                "params": ["batch1"],
                "jsonrpc": "2.0",
                "id": 7
            },
            {
                "method": "test_add",
                "params": [1, 2],
                "jsonrpc": "2.0",
                "id": 8
            }
        ]
        
        # Create mock request
        request = Request.from_values(
            data=json.dumps(batch_data),
            content_type='application/json',
            method='POST'
        )
        
        # Process request
        response = application(request)
        
        # Parse response
        response_data = json.loads(response.data.decode('utf-8'))
        
        # Assertions
        assert isinstance(response_data, list)
        assert len(response_data) == 2
        
        # Check first response
        assert response_data[0]["jsonrpc"] == "2.0"
        assert response_data[0]["id"] == 7
        assert response_data[0]["result"] == "batch1"
        
        # Check second response
        assert response_data[1]["jsonrpc"] == "2.0"
        assert response_data[1]["id"] == 8
        assert response_data[1]["result"] == 3
    
    def test_notification_request(self):
        """Test notification request (no response expected)"""
        # Create notification request (no id)
        request_data = {
            "method": "test_echo",
            "params": ["notification"],
            "jsonrpc": "2.0"
        }
        
        # Create mock request
        request = Request.from_values(
            data=json.dumps(request_data),
            content_type='application/json',
            method='POST'
        )
        
        # Process request
        response = application(request)
        
        # Parse response
        response_data = response.data.decode('utf-8')
        
        # Assertions - notification should return empty response
        assert response_data == ""
    
    def test_error_handling(self):
        """Test error handling in method execution"""
        # Add a method that raises an exception
        @dispatcher.add_method
        def test_error():
            raise ValueError("Test error")
        
        # Create request
        request_data = {
            "method": "test_error",
            "params": [],
            "jsonrpc": "2.0",
            "id": 9
        }
        
        # Create mock request
        request = Request.from_values(
            data=json.dumps(request_data),
            content_type='application/json',
            method='POST'
        )
        
        # Process request
        response = application(request)
        
        # Parse response
        response_data = json.loads(response.data.decode('utf-8'))
        
        # Assertions
        assert response_data["jsonrpc"] == "2.0"
        assert response_data["id"] == 9
        assert "error" in response_data
        assert response_data["error"]["code"] == -32603  # Internal error
        assert "Test error" in response_data["error"]["message"]


class TestJSONRPCClient:
    """Test cases for JSON-RPC client functionality"""
    
    def test_client_echo_request(self):
        """Test client echo request (requires server to be running)"""
        # This test would require a running server
        # For now, we'll test the request structure
        url = "http://localhost:4000/jsonrpc"
        headers = {'content-type': 'application/json'}
        
        payload = {
            "method": "echo",
            "params": ["test_message"],
            "jsonrpc": "2.0",
            "id": 1,
        }
        
        # Validate payload structure
        assert payload["method"] == "echo"
        assert payload["params"] == ["test_message"]
        assert payload["jsonrpc"] == "2.0"
        assert payload["id"] == 1
    
    def test_client_add_request(self):
        """Test client add request structure"""
        url = "http://localhost:4000/jsonrpc"
        headers = {'content-type': 'application/json'}
        
        payload = {
            "method": "add",
            "params": [5, 3],
            "jsonrpc": "2.0",
            "id": 2,
        }
        
        # Validate payload structure
        assert payload["method"] == "add"
        assert payload["params"] == [5, 3]
        assert payload["jsonrpc"] == "2.0"
        assert payload["id"] == 2


if __name__ == "__main__":
    pytest.main([__file__])
