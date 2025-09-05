import signal
import sys
import logging
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dispatcher.add_method
def foobar(**kwargs):
    return kwargs["foo"] + kwargs["bar"]


@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b

    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    logger.info("JSON-RPC Server shutdown complete")
    sys.exit(0)


if __name__ == '__main__':
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("JSON-RPC Server starting on http://localhost:4000")
    logger.info("Available methods: echo, add, foobar")
    logger.info("Press Ctrl+C to gracefully shutdown the server")
    
    try:
        run_simple('localhost', 4000, application)
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down server...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("JSON-RPC Server shutdown complete")
