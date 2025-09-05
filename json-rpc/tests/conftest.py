"""
Pytest configuration and fixtures for JSON-RPC tests
"""
import pytest
import json
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


@pytest.fixture(scope="session")
def test_server():
    """Fixture to start a test server for integration tests"""
    server_thread = None
    server_url = "http://localhost:4001"
    
    def run_test_server():
        run_simple('localhost', 4001, application, use_reloader=False, use_debugger=False)
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_test_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(1)
    
    yield server_url
    
    # Server will be cleaned up automatically when thread dies


@pytest.fixture
def sample_requests():
    """Fixture providing sample JSON-RPC requests"""
    return {
        "echo": {
            "method": "echo",
            "params": ["Hello, World!"],
            "jsonrpc": "2.0",
            "id": 1
        },
        "add": {
            "method": "add",
            "params": [5, 3],
            "jsonrpc": "2.0",
            "id": 2
        },
        "foobar": {
            "method": "foobar",
            "params": {"foo": 10, "bar": 20},
            "jsonrpc": "2.0",
            "id": 3
        },
        "invalid_method": {
            "method": "nonexistent_method",
            "params": [],
            "jsonrpc": "2.0",
            "id": 4
        },
        "invalid_json": '{"method": "echo", "params": ["test"], "jsonrpc": "2.0", "id": 5',
        "notification": {
            "method": "echo",
            "params": ["notification"],
            "jsonrpc": "2.0"
        }
    }


@pytest.fixture
def expected_responses():
    """Fixture providing expected JSON-RPC responses"""
    return {
        "echo": {
            "result": "Hello, World!",
            "jsonrpc": "2.0",
            "id": 1
        },
        "add": {
            "result": 8,
            "jsonrpc": "2.0",
            "id": 2
        },
        "foobar": {
            "result": 30,
            "jsonrpc": "2.0",
            "id": 3
        },
        "method_not_found": {
            "error": {
                "code": -32601,
                "message": "Method not found"
            },
            "jsonrpc": "2.0",
            "id": 4
        },
        "parse_error": {
            "error": {
                "code": -32700,
                "message": "Parse error"
            },
            "jsonrpc": "2.0",
            "id": None
        }
    }


@pytest.fixture
def mock_request():
    """Fixture for creating mock requests"""
    def _create_request(data, content_type='application/json', method='POST'):
        return Request.from_values(
            data=data if isinstance(data, str) else json.dumps(data),
            content_type=content_type,
            method=method
        )
    return _create_request


@pytest.fixture(autouse=True)
def clear_dispatcher():
    """Fixture to clear dispatcher before each test"""
    dispatcher.clear()
    
    # Add test methods
    @dispatcher.add_method
    def echo(s):
        return s
        
    @dispatcher.add_method
    def add(a, b):
        return a + b
        
    @dispatcher.add_method
    def foobar(**kwargs):
        return kwargs.get("foo", 0) + kwargs.get("bar", 0)
    
    yield
    
    # Cleanup after test
    dispatcher.clear()
