import asyncio
import json
import logging
import signal
import sys
from typing import Dict, Any
from a2a_json_rpc.protocol import JSONRPCProtocol
from a2a_json_rpc.models import Json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create A2A-specific protocol instance
protocol = JSONRPCProtocol()

# Register agent method handlers
@protocol.method("task/process")
async def process_task(method: str, params: Json) -> Json:
    """Process an agent task"""
    task_id = params.get("task_id")
    task_type = params.get("task_type", "general")
    data = params.get("data", {})
    
    logger.info(f"Processing task {task_id} of type {task_type}")
    
    # Simulate task processing
    await asyncio.sleep(0.1)  # Simulate processing time
    
    return {
        "task_id": task_id,
        "status": "completed",
        "result": f"Task {task_id} processed successfully",
        "processed_data": data,
        "timestamp": asyncio.get_event_loop().time()
    }

@protocol.method("agent/status")
async def get_agent_status(method: str, params: Json) -> Json:
    """Get agent status information"""
    return {
        "status": "active",
        "capabilities": ["task/process", "agent/status", "data/analyze"],
        "uptime": asyncio.get_event_loop().time(),
        "version": "1.0.0"
    }

@protocol.method("data/analyze")
async def analyze_data(method: str, params: Json) -> Json:
    """Analyze provided data"""
    data = params.get("data", [])
    analysis_type = params.get("analysis_type", "basic")
    
    logger.info(f"Analyzing {len(data)} items with {analysis_type} analysis")
    
    # Simple analysis simulation
    if isinstance(data, list):
        result = {
            "count": len(data),
            "analysis_type": analysis_type,
            "summary": f"Analyzed {len(data)} items",
            "insights": ["Data appears to be structured", "No anomalies detected"]
        }
    else:
        result = {
            "analysis_type": analysis_type,
            "summary": "Single item analysis",
            "insights": ["Item processed successfully"]
        }
    
    return result

# Handle A2A communication
async def handle_agent_request(request_data: str) -> str:
    """Handle incoming agent requests"""
    try:
        # Parse the JSON request
        request = json.loads(request_data)
        method = request.get('method')
        request_id = request.get('id')
        params = request.get('params', {})
        
        logger.info(f"Received request: {method}")
        
        # Handle the request based on method
        if method == "agent/status":
            result = await get_agent_status(method, params)
        elif method == "task/process":
            result = await process_task(method, params)
        elif method == "data/analyze":
            result = await analyze_data(method, params)
        else:
            # Method not found
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": "Method not found",
                    "data": f"Method '{method}' not found"
                }
            }
            return json.dumps(error_response)
        
        # Create successful response
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        
        logger.info(f"Sending response for method: {method}")
        return json.dumps(response)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error",
                "data": str(e)
            }
        }
        return json.dumps(error_response)
    
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        error_response = {
            "jsonrpc": "2.0",
            "id": request.get('id') if 'request' in locals() else None,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        }
        return json.dumps(error_response)

# Global variable to track server state
server_shutdown = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global server_shutdown
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    server_shutdown = True

# Server implementation
async def run_server(host: str = "localhost", port: int = 8000):
    """Run the A2A JSON-RPC server"""
    from aiohttp import web, web_request
    import aiohttp_cors
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    async def handle_request(request: web_request.Request) -> web.Response:
        """Handle incoming HTTP requests"""
        try:
            # Get the request data
            request_data = await request.text()
            logger.info(f"Received HTTP request from {request.remote}")
            
            # Process the JSON-RPC request
            response_data = await handle_agent_request(request_data)
            
            # Return the response
            return web.Response(
                text=response_data,
                content_type='application/json',
                headers={'Access-Control-Allow-Origin': '*'}
            )
            
        except Exception as e:
            logger.error(f"Error handling HTTP request: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
            return web.Response(
                text=json.dumps(error_response),
                content_type='application/json',
                status=500
            )
    
    # Create the web application
    app = web.Application()
    
    # Configure CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    app.router.add_post('/rpc', handle_request)
    app.router.add_get('/health', lambda r: web.Response(text='OK'))
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    logger.info(f"A2A Server starting on http://{host}:{port}")
    logger.info("Available endpoints:")
    logger.info(f"  POST http://{host}:{port}/rpc - JSON-RPC endpoint")
    logger.info(f"  GET  http://{host}:{port}/health - Health check")
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    logger.info("A2A Server is running and ready to accept connections")
    logger.info("Press Ctrl+C to gracefully shutdown the server")
    
    # Keep the server running until shutdown signal
    try:
        while not server_shutdown:
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down server...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Cleaning up server resources...")
        await runner.cleanup()
        logger.info("A2A Server shutdown complete")

if __name__ == "__main__":
    asyncio.run(run_server())