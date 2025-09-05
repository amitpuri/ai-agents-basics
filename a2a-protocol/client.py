import asyncio
import json
import logging
from typing import Dict, Any, Optional
from a2a_json_rpc.protocol import JSONRPCProtocol
from a2a_json_rpc.models import Json
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class A2AClient:
    """A2A (Agent-to-Agent) JSON-RPC Client"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.protocol = JSONRPCProtocol()
        self.request_id = 0
        self.session = None
        
    def _get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server"""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._get_next_id()
        }
        
        if params:
            request["params"] = params
        
        request_str = json.dumps(request)
        logger.info(f"Sending request: {method}")
        
        # Send HTTP request to the server
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.server_url}/rpc",
                    data=request_str,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    response_text = await response.text()
                    if response.status == 200:
                        return json.loads(response_text)
                    else:
                        logger.error(f"Server returned status {response.status}: {response_text}")
                        return {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {
                                "code": -32603,
                                "message": "Server error",
                                "data": f"HTTP {response.status}: {response_text}"
                            }
                        }
            except aiohttp.ClientError as e:
                logger.error(f"Connection error: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": request["id"],
                    "error": {
                        "code": -32603,
                        "message": "Connection error",
                        "data": str(e)
                    }
                }
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": request["id"],
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": str(e)
                    }
                }
    
    async def check_server_health(self) -> bool:
        """Check if the server is running and healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"Server health check failed: {e}")
            return False
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return await self._send_request("agent/status")
    
    async def process_task(self, task_id: str, task_type: str = "general", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a task on the server"""
        params = {
            "task_id": task_id,
            "task_type": task_type
        }
        
        if data:
            params["data"] = data
        
        return await self._send_request("task/process", params)
    
    async def analyze_data(self, data: Any, analysis_type: str = "basic") -> Dict[str, Any]:
        """Analyze data on the server"""
        params = {
            "data": data,
            "analysis_type": analysis_type
        }
        
        return await self._send_request("data/analyze", params)
    
    async def batch_process_tasks(self, tasks: list) -> list:
        """Process multiple tasks in batch"""
        results = []
        
        for task in tasks:
            try:
                result = await self.process_task(
                    task_id=task.get("task_id"),
                    task_type=task.get("task_type", "general"),
                    data=task.get("data")
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing task {task.get('task_id')}: {e}")
                results.append({
                    "task_id": task.get("task_id"),
                    "status": "error",
                    "error": str(e)
                })
        
        return results

# Example usage and testing
async def run_client_examples():
    """Run client examples to demonstrate functionality"""
    logger.info("Starting A2A Client examples")
    
    # Create client instance
    client = A2AClient()
    
    try:
        # Check server health first
        print("=" * 60)
        print("Checking server health...")
        print("=" * 60)
        if not await client.check_server_health():
            print("❌ Server is not running or not accessible!")
            print("Please start the server first with: python server.py")
            return
        print("✅ Server is running and healthy!")
        
        # Example 1: Get agent status
        print("\n" + "=" * 60)
        print("Example 1: Getting agent status")
        print("=" * 60)
        status = await client.get_agent_status()
        print(f"Agent Status: {json.dumps(status, indent=2)}")
        
        # Example 2: Process a single task
        print("\n" + "=" * 60)
        print("Example 2: Processing a single task")
        print("=" * 60)
        task_result = await client.process_task(
            task_id="client_task_001",
            task_type="analysis",
            data={"input": "client data", "priority": "high"}
        )
        print(f"Task Result: {json.dumps(task_result, indent=2)}")
        
        # Example 3: Analyze data
        print("\n" + "=" * 60)
        print("Example 3: Analyzing data")
        print("=" * 60)
        analysis_result = await client.analyze_data(
            data=[10, 20, 30, 40, 50],
            analysis_type="statistical"
        )
        print(f"Analysis Result: {json.dumps(analysis_result, indent=2)}")
        
        # Example 4: Batch processing
        print("\n" + "=" * 60)
        print("Example 4: Batch processing tasks")
        print("=" * 60)
        batch_tasks = [
            {"task_id": "batch_001", "task_type": "processing", "data": {"item": 1}},
            {"task_id": "batch_002", "task_type": "validation", "data": {"item": 2}},
            {"task_id": "batch_003", "task_type": "analysis", "data": {"item": 3}}
        ]
        
        batch_results = await client.batch_process_tasks(batch_tasks)
        for i, result in enumerate(batch_results):
            print(f"Batch Task {i+1} Result: {json.dumps(result, indent=2)}")
        
        # Example 5: Error handling
        print("\n" + "=" * 60)
        print("Example 5: Error handling demonstration")
        print("=" * 60)
        try:
            # This will trigger an error in the server
            error_result = await client._send_request("nonexistent/method", {"test": "data"})
            print(f"Error Result: {json.dumps(error_result, indent=2)}")
        except Exception as e:
            print(f"Caught exception: {e}")
        
    except Exception as e:
        logger.error(f"Error in client examples: {e}")
    
    logger.info("A2A Client examples completed")

# Interactive client for manual testing
async def interactive_client():
    """Interactive client for manual testing"""
    client = A2AClient()
    
    print("A2A Interactive Client")
    print("Checking server connection...")
    
    if not await client.check_server_health():
        print("❌ Server is not running or not accessible!")
        print("Please start the server first with: python server.py")
        return
    
    print("✅ Connected to server!")
    print("\nAvailable commands:")
    print("1. status - Get agent status")
    print("2. task <id> [type] - Process a task")
    print("3. analyze <data> [type] - Analyze data")
    print("4. quit - Exit")
    
    while True:
        try:
            command = input("\nEnter command: ").strip().split()
            
            if not command:
                continue
                
            if command[0] == "quit":
                break
            elif command[0] == "status":
                result = await client.get_agent_status()
                print(json.dumps(result, indent=2))
            elif command[0] == "task":
                if len(command) < 2:
                    print("Usage: task <id> [type]")
                    continue
                task_id = command[1]
                task_type = command[2] if len(command) > 2 else "general"
                result = await client.process_task(task_id, task_type)
                print(json.dumps(result, indent=2))
            elif command[0] == "analyze":
                if len(command) < 2:
                    print("Usage: analyze <data> [type]")
                    continue
                data = json.loads(command[1]) if command[1].startswith('[') or command[1].startswith('{') else command[1]
                analysis_type = command[2] if len(command) > 2 else "basic"
                result = await client.analyze_data(data, analysis_type)
                print(json.dumps(result, indent=2))
            else:
                print("Unknown command")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_client())
    else:
        asyncio.run(run_client_examples())
