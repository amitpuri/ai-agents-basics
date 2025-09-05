"""
Pytest configuration and fixtures for A2A Protocol tests
"""
import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def sample_requests():
    """Fixture providing sample A2A requests"""
    return {
        "agent_status": {
            "method": "agent/status",
            "id": 1,
            "params": {}
        },
        "task_process": {
            "method": "task/process",
            "id": 2,
            "params": {
                "task_id": "test_task_001",
                "task_type": "analysis",
                "data": {"input": "test data", "priority": "high"}
            }
        },
        "data_analyze": {
            "method": "data/analyze",
            "id": 3,
            "params": {
                "data": [1, 2, 3, 4, 5],
                "analysis_type": "statistical"
            }
        },
        "invalid_method": {
            "method": "unknown/method",
            "id": 4,
            "params": {}
        },
        "invalid_json": '{"method": "agent/status", "id": 5, "params": {}',
        "notification": {
            "method": "agent/status",
            "params": {}
        }
    }


@pytest.fixture
def expected_responses():
    """Fixture providing expected A2A responses"""
    return {
        "agent_status": {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "status": "active",
                "capabilities": ["task/process", "agent/status", "data/analyze"],
                "uptime": 123.45,
                "version": "1.0.0"
            }
        },
        "task_process": {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "task_id": "test_task_001",
                "status": "completed",
                "result": "Task test_task_001 processed successfully",
                "processed_data": {"input": "test data", "priority": "high"},
                "timestamp": 123.45
            }
        },
        "data_analyze": {
            "jsonrpc": "2.0",
            "id": 3,
            "result": {
                "count": 5,
                "analysis_type": "statistical",
                "summary": "Analyzed 5 items",
                "insights": ["Data appears to be structured", "No anomalies detected"]
            }
        },
        "method_not_found": {
            "jsonrpc": "2.0",
            "id": 4,
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
def sample_task_data():
    """Fixture providing sample task data"""
    return {
        "task_id": "sample_task_001",
        "task_type": "processing",
        "data": {
            "input_file": "data.csv",
            "output_format": "json",
            "parameters": {
                "batch_size": 100,
                "timeout": 30
            }
        }
    }


@pytest.fixture
def sample_analysis_data():
    """Fixture providing sample analysis data"""
    return {
        "list_data": [10, 20, 30, 40, 50],
        "single_data": "test string",
        "complex_data": {
            "users": [
                {"id": 1, "name": "Alice", "score": 95},
                {"id": 2, "name": "Bob", "score": 87},
                {"id": 3, "name": "Charlie", "score": 92}
            ],
            "metadata": {
                "created_at": "2024-01-01",
                "version": "1.0"
            }
        }
    }


@pytest.fixture
def sample_batch_tasks():
    """Fixture providing sample batch tasks"""
    return [
        {
            "task_id": "batch_001",
            "task_type": "processing",
            "data": {"item": 1, "priority": "high"}
        },
        {
            "task_id": "batch_002",
            "task_type": "validation",
            "data": {"item": 2, "priority": "medium"}
        },
        {
            "task_id": "batch_003",
            "task_type": "analysis",
            "data": {"item": 3, "priority": "low"}
        }
    ]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def a2a_client():
    """Fixture to create A2A client instance"""
    from client import A2AClient
    return A2AClient("http://localhost:8000")


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
        }
    }
