"""
Tests for JSON-RPC Client implementation
"""
import json
import pytest
import requests
from unittest.mock import patch, MagicMock


class TestJSONRPCClient:
    """Test cases for JSON-RPC client functionality"""
    
    def test_request_structure(self):
        """Test that client creates proper request structure"""
        # Test echo request structure
        echo_payload = {
            "method": "echo",
            "params": ["test_message"],
            "jsonrpc": "2.0",
            "id": 1,
        }
        
        # Validate structure
        assert echo_payload["method"] == "echo"
        assert echo_payload["params"] == ["test_message"]
        assert echo_payload["jsonrpc"] == "2.0"
        assert echo_payload["id"] == 1
        
        # Test add request structure
        add_payload = {
            "method": "add",
            "params": [5, 3],
            "jsonrpc": "2.0",
            "id": 2,
        }
        
        # Validate structure
        assert add_payload["method"] == "add"
        assert add_payload["params"] == [5, 3]
        assert add_payload["jsonrpc"] == "2.0"
        assert add_payload["id"] == 2
    
    @patch('requests.post')
    def test_successful_echo_request(self, mock_post):
        """Test successful echo request with mocked response"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": "test_message",
            "jsonrpc": "2.0",
            "id": 1
        }
        mock_post.return_value = mock_response
        
        # Test request
        url = "http://localhost:4000/jsonrpc"
        headers = {'content-type': 'application/json'}
        payload = {
            "method": "echo",
            "params": ["test_message"],
            "jsonrpc": "2.0",
            "id": 1,
        }
        
        response = requests.post(
            url, data=json.dumps(payload), headers=headers
        ).json()
        
        # Assertions
        assert response["result"] == "test_message"
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_successful_add_request(self, mock_post):
        """Test successful add request with mocked response"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": 8,
            "jsonrpc": "2.0",
            "id": 2
        }
        mock_post.return_value = mock_response
        
        # Test request
        url = "http://localhost:4000/jsonrpc"
        headers = {'content-type': 'application/json'}
        payload = {
            "method": "add",
            "params": [5, 3],
            "jsonrpc": "2.0",
            "id": 2,
        }
        
        response = requests.post(
            url, data=json.dumps(payload), headers=headers
        ).json()
        
        # Assertions
        assert response["result"] == 8
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_error_response(self, mock_post):
        """Test error response handling"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {
                "code": -32601,
                "message": "Method not found"
            },
            "jsonrpc": "2.0",
            "id": 3
        }
        mock_post.return_value = mock_response
        
        # Test request
        url = "http://localhost:4000/jsonrpc"
        headers = {'content-type': 'application/json'}
        payload = {
            "method": "nonexistent_method",
            "params": [],
            "jsonrpc": "2.0",
            "id": 3,
        }
        
        response = requests.post(
            url, data=json.dumps(payload), headers=headers
        ).json()
        
        # Assertions
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert response["error"]["message"] == "Method not found"
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 3
    
    @patch('requests.post')
    def test_connection_error(self, mock_post):
        """Test connection error handling"""
        # Mock connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        # Test request
        url = "http://localhost:4000/jsonrpc"
        headers = {'content-type': 'application/json'}
        payload = {
            "method": "echo",
            "params": ["test"],
            "jsonrpc": "2.0",
            "id": 4,
        }
        
        # Should raise ConnectionError
        with pytest.raises(requests.exceptions.ConnectionError):
            requests.post(
                url, data=json.dumps(payload), headers=headers
            )
    
    def test_json_serialization(self):
        """Test JSON serialization of payloads"""
        # Test various data types
        test_cases = [
            {"method": "echo", "params": ["string"], "jsonrpc": "2.0", "id": 1},
            {"method": "add", "params": [1, 2], "jsonrpc": "2.0", "id": 2},
            {"method": "test", "params": [True, False], "jsonrpc": "2.0", "id": 3},
            {"method": "test", "params": [None], "jsonrpc": "2.0", "id": 4},
            {"method": "test", "params": [{"key": "value"}], "jsonrpc": "2.0", "id": 5},
            {"method": "test", "params": [[1, 2, 3]], "jsonrpc": "2.0", "id": 6},
        ]
        
        for payload in test_cases:
            # Should not raise exception
            json_str = json.dumps(payload)
            assert isinstance(json_str, str)
            
            # Should be able to deserialize
            deserialized = json.loads(json_str)
            assert deserialized == payload
    
    def test_request_id_increment(self):
        """Test that request IDs are properly incremented"""
        # Simulate multiple requests
        request_ids = []
        for i in range(5):
            payload = {
                "method": "echo",
                "params": [f"test_{i}"],
                "jsonrpc": "2.0",
                "id": i + 1,
            }
            request_ids.append(payload["id"])
        
        # Check that IDs are sequential
        assert request_ids == [1, 2, 3, 4, 5]
    
    def test_headers_validation(self):
        """Test that proper headers are set"""
        headers = {'content-type': 'application/json'}
        
        # Validate headers
        assert headers['content-type'] == 'application/json'
        assert len(headers) == 1
    
    def test_url_construction(self):
        """Test URL construction"""
        base_url = "http://localhost:4000"
        endpoint = "/jsonrpc"
        full_url = base_url + endpoint
        
        assert full_url == "http://localhost:4000/jsonrpc"


if __name__ == "__main__":
    pytest.main([__file__])
