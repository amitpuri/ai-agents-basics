import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClient:
    """Model Context Protocol Client Implementation"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.request_id = 0
        self.session = None
        self.initialized = False
        
    def _get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send an MCP request to the server"""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._get_next_id()
        }
        
        if params:
            request["params"] = params
        
        request_str = json.dumps(request)
        logger.info(f"Sending MCP request: {method}")
        
        # Send HTTP request to the server
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.server_url}/mcp",
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
    
    async def initialize(self, client_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initialize the MCP connection"""
        if client_info is None:
            client_info = {
                "name": "mcp-client",
                "version": "1.0.0"
            }
        
        params = {"clientInfo": client_info}
        response = await self._send_request("initialize", params)
        
        if "error" not in response:
            self.initialized = True
            logger.info("MCP connection initialized successfully")
        
        return response
    
    async def list_tools(self) -> Dict[str, Any]:
        """List all available tools"""
        return await self._send_request("tools/list")
    
    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call a specific tool"""
        if arguments is None:
            arguments = {}
        
        params = {
            "name": name,
            "arguments": arguments
        }
        
        return await self._send_request("tools/call", params)
    
    async def list_resources(self) -> Dict[str, Any]:
        """List all available resources"""
        return await self._send_request("resources/list")
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a specific resource"""
        params = {"uri": uri}
        return await self._send_request("resources/read", params)
    
    async def get_weather(self, location: str) -> Dict[str, Any]:
        """Convenience method to get weather"""
        return await self.call_tool("get_weather", {"location": location})
    
    async def calculate_math(self, expression: str) -> Dict[str, Any]:
        """Convenience method to calculate math"""
        return await self.call_tool("calculate_math", {"expression": expression})
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Convenience method to get system info"""
        return await self.call_tool("get_system_info", {})
    
    async def search_files(self, query: str, directory: str = ".") -> Dict[str, Any]:
        """Convenience method to search files"""
        return await self.call_tool("search_files", {"query": query, "directory": directory})
    
    async def batch_call_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Call multiple tools in batch"""
        results = []
        
        for tool_call in tool_calls:
            try:
                name = tool_call.get("name")
                arguments = tool_call.get("arguments", {})
                result = await self.call_tool(name, arguments)
                results.append(result)
            except Exception as e:
                logger.error(f"Error calling tool {tool_call.get('name')}: {e}")
                results.append({
                    "error": {
                        "code": -32603,
                        "message": "Tool call failed",
                        "data": str(e)
                    }
                })
        
        return results

# Example usage and testing
async def run_client_examples():
    """Run client examples to demonstrate functionality"""
    logger.info("Starting MCP Client examples")
    
    # Create client instance
    client = MCPClient()
    
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
        
        # Initialize MCP connection
        print("\n" + "=" * 60)
        print("Initializing MCP connection...")
        print("=" * 60)
        init_result = await client.initialize()
        if "error" in init_result:
            print(f"❌ Initialization failed: {init_result['error']}")
            return
        print("✅ MCP connection initialized!")
        print(f"Server info: {json.dumps(init_result.get('result', {}), indent=2)}")
        
        # Example 1: List available tools
        print("\n" + "=" * 60)
        print("Example 1: Listing available tools")
        print("=" * 60)
        tools_result = await client.list_tools()
        if "error" not in tools_result:
            tools = tools_result.get("result", {}).get("tools", [])
            print(f"Available tools ({len(tools)}):")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        else:
            print(f"Error listing tools: {tools_result['error']}")
        
        # Example 2: Call weather tool
        print("\n" + "=" * 60)
        print("Example 2: Getting weather information")
        print("=" * 60)
        weather_result = await client.get_weather("New York")
        if "error" not in weather_result:
            content = weather_result.get("result", {}).get("content", [])
            if content:
                print(f"Weather result: {content[0].get('text', 'No text content')}")
        else:
            print(f"Weather error: {weather_result['error']}")
        
        # Example 3: Calculate math
        print("\n" + "=" * 60)
        print("Example 3: Calculating mathematical expressions")
        print("=" * 60)
        math_expressions = ["2 + 3 * 4", "10 / 2 + 5", "(100 - 25) / 3"]
        for expr in math_expressions:
            math_result = await client.calculate_math(expr)
            if "error" not in math_result:
                content = math_result.get("result", {}).get("content", [])
                if content:
                    print(f"{expr} = {content[0].get('text', 'No result')}")
            else:
                print(f"Math error for '{expr}': {math_result['error']}")
        
        # Example 4: Get system info
        print("\n" + "=" * 60)
        print("Example 4: Getting system information")
        print("=" * 60)
        system_result = await client.get_system_info()
        if "error" not in system_result:
            content = system_result.get("result", {}).get("content", [])
            if content:
                print("System Information:")
                print(content[0].get('text', 'No system info'))
        else:
            print(f"System info error: {system_result['error']}")
        
        # Example 5: List and read resources
        print("\n" + "=" * 60)
        print("Example 5: Working with resources")
        print("=" * 60)
        
        # List resources
        resources_result = await client.list_resources()
        if "error" not in resources_result:
            resources = resources_result.get("result", {}).get("resources", [])
            print(f"Available resources ({len(resources)}):")
            for resource in resources:
                print(f"  - {resource['name']} ({resource['uri']})")
            
            # Read a sample resource
            if resources:
                sample_resource = resources[0]
                print(f"\nReading resource: {sample_resource['name']}")
                read_result = await client.read_resource(sample_resource['uri'])
                if "error" not in read_result:
                    contents = read_result.get("result", {}).get("contents", [])
                    if contents:
                        content_text = contents[0].get("text", "")
                        # Truncate long content for display
                        if len(content_text) > 200:
                            content_text = content_text[:200] + "..."
                        print(f"Resource content: {content_text}")
                else:
                    print(f"Error reading resource: {read_result['error']}")
        else:
            print(f"Error listing resources: {resources_result['error']}")
        
        # Example 6: Batch tool calls
        print("\n" + "=" * 60)
        print("Example 6: Batch tool calls")
        print("=" * 60)
        batch_calls = [
            {"name": "get_weather", "arguments": {"location": "London"}},
            {"name": "calculate_math", "arguments": {"expression": "15 * 3 + 7"}},
            {"name": "get_weather", "arguments": {"location": "Tokyo"}}
        ]
        
        batch_results = await client.batch_call_tools(batch_calls)
        for i, result in enumerate(batch_results):
            if "error" not in result:
                content = result.get("result", {}).get("content", [])
                if content:
                    print(f"Batch call {i+1}: {content[0].get('text', 'No result')}")
            else:
                print(f"Batch call {i+1} error: {result['error']}")
        
        # Example 7: Error handling
        print("\n" + "=" * 60)
        print("Example 7: Error handling demonstration")
        print("=" * 60)
        try:
            # This will trigger an error - calling non-existent tool
            error_result = await client.call_tool("nonexistent_tool", {"test": "data"})
            print(f"Error result: {json.dumps(error_result, indent=2)}")
        except Exception as e:
            print(f"Caught exception: {e}")
        
    except Exception as e:
        logger.error(f"Error in client examples: {e}")
    
    logger.info("MCP Client examples completed")

# Interactive client for manual testing
async def interactive_client():
    """Interactive client for manual testing"""
    client = MCPClient()
    
    print("MCP Interactive Client")
    print("Checking server connection...")
    
    if not await client.check_server_health():
        print("❌ Server is not running or not accessible!")
        print("Please start the server first with: python server.py")
        return
    
    # Initialize connection
    init_result = await client.initialize()
    if "error" in init_result:
        print(f"❌ Initialization failed: {init_result['error']}")
        return
    
    print("✅ Connected to MCP server!")
    print("\nAvailable commands:")
    print("1. tools - List available tools")
    print("2. resources - List available resources")
    print("3. weather <location> - Get weather for location")
    print("4. math <expression> - Calculate mathematical expression")
    print("5. system - Get system information")
    print("6. search <query> [directory] - Search for files")
    print("7. read <uri> - Read a resource")
    print("8. call <tool_name> <json_args> - Call a tool with custom arguments")
    print("9. quit - Exit")
    
    while True:
        try:
            command = input("\nEnter command: ").strip().split()
            
            if not command:
                continue
                
            if command[0] == "quit":
                break
            elif command[0] == "tools":
                result = await client.list_tools()
                print(json.dumps(result, indent=2))
            elif command[0] == "resources":
                result = await client.list_resources()
                print(json.dumps(result, indent=2))
            elif command[0] == "weather":
                if len(command) < 2:
                    print("Usage: weather <location>")
                    continue
                location = " ".join(command[1:])
                result = await client.get_weather(location)
                print(json.dumps(result, indent=2))
            elif command[0] == "math":
                if len(command) < 2:
                    print("Usage: math <expression>")
                    continue
                expression = " ".join(command[1:])
                result = await client.calculate_math(expression)
                print(json.dumps(result, indent=2))
            elif command[0] == "system":
                result = await client.get_system_info()
                print(json.dumps(result, indent=2))
            elif command[0] == "search":
                if len(command) < 2:
                    print("Usage: search <query> [directory]")
                    continue
                query = command[1]
                directory = command[2] if len(command) > 2 else "."
                result = await client.search_files(query, directory)
                print(json.dumps(result, indent=2))
            elif command[0] == "read":
                if len(command) < 2:
                    print("Usage: read <uri>")
                    continue
                uri = command[1]
                result = await client.read_resource(uri)
                print(json.dumps(result, indent=2))
            elif command[0] == "call":
                if len(command) < 3:
                    print("Usage: call <tool_name> <json_args>")
                    continue
                tool_name = command[1]
                try:
                    args = json.loads(" ".join(command[2:]))
                    result = await client.call_tool(tool_name, args)
                    print(json.dumps(result, indent=2))
                except json.JSONDecodeError:
                    print("Error: Invalid JSON arguments")
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
