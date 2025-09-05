![AI Generated](https://img.shields.io/badge/AI-Generated-blueviolet?style=for-the-badge&logo=openai&logoColor=white)

# OpenAGI Codes AI Agents Basics

A collection of AI agent implementations demonstrating various communication protocols and patterns for building intelligent agent systems.

## Overview of AI Agents

Artificial Intelligence is evolving beyond monolithic models into dynamic ecosystems where multiple specialized agents work in unison. AI agents can operate autonomously, collaborate on complex tasks, and integrate diverse capabilities—from natural language understanding to visual reasoning.

### Key AI Agent Capabilities

- **Autonomy**: Each agent functions without constant human supervision by dynamically assessing data and executing tailored actions
- **Specialization**: Agents are often engineered to excel at specific tasks—whether generating content, managing tasks, integrating tools, or handling natural language interactions
- **Collaboration**: Many systems are designed to work together. Multi-agent frameworks allow teams of AI to share information, coordinate workflows, and handle complex problem solving
- **Adaptability**: With built-in learning and memory mechanisms, agents evolve over time, becoming more effective as they process new data and user feedback

In multi-agent systems, these features combine to produce robust, scalable solutions for challenges in software development, customer service, research, content creation, and more.

## MCP (Model Context Protocol)

The Model Context Protocol (MCP) is a standardized way for AI applications to securely connect to data sources and tools. MCP enables large language models to interact with external systems through a well-defined protocol that supports:

- **Tool Integration**: Seamless connection to external APIs and services
- **Resource Access**: Secure access to files, databases, and other data sources
- **Standardized Communication**: Consistent protocol for AI-tool interactions
- **Security**: Built-in security measures for safe tool execution

For more information about MCP, visit:
- [Official MCP Documentation](https://modelcontextprotocol.io/)
- [OpenAGI MCP Documentation](https://openagi.news/mcp)

## JSON-RPC

JSON-RPC is a stateless, light-weight remote procedure call (RPC) protocol. This repository demonstrates JSON-RPC 2.0 implementations for:

- **Agent-to-Agent Communication**: Enabling AI agents to communicate with each other
- **Service Integration**: Connecting different AI services and tools
- **Asynchronous Operations**: Supporting concurrent and non-blocking operations
- **Error Handling**: Robust error management and response validation

For more information about JSON-RPC, visit [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification).

## A2A Protocol

The Agent-to-Agent (A2A) Protocol is an application-level protocol for agents to discover each other, negotiate interaction modalities, manage shared tasks, and exchange conversational context or complex results. A2A focuses on how agents partner or delegate work to each other.

Key features of A2A Protocol:
- **Agent Discovery**: Standardized way for agents to find and connect with each other
- **Multi-Transport Support**: JSON-RPC 2.0, gRPC, and HTTP+JSON/REST transports
- **Task Management**: Comprehensive task lifecycle management with streaming support
- **Authentication & Authorization**: Built-in security mechanisms for secure agent interactions

For more information about A2A Protocol, visit [A2A Protocol Specification](https://a2a-protocol.org/dev/specification/).

## Project Structure

This repository contains several subdirectories, each focusing on different aspects of AI agent development:

### `json-rpc/`
Simple JSON-RPC 2.0 implementation demonstrating:
- **JSON-RPC 2.0 Compliance**: Standard-compliant server and client implementations
- **Example Methods**: Echo, add, and foobar RPC methods
- **HTTP Transport**: Simple HTTP-based transport using Werkzeug
- **Error Handling**: Comprehensive error handling and response validation
- **Comprehensive Tests**: Full test suite with server, client, and integration tests

### `mcp/`
Complete Model Context Protocol implementation featuring:
- **MCP Server**: Full MCP protocol compliance with tool registration and resource management
- **MCP Client**: Object-oriented client with tool invocation and resource access
- **Comprehensive Tools**: Weather, math calculation, system info, and file search capabilities
- **Resource Management**: Support for JSON, YAML, and Markdown resources
- **Test Suite**: Complete testing framework for server-client communication

### `a2a-protocol/`
Agent-to-Agent communication protocol implementation including:
- **Multiple Method Handlers**: Agent status, task processing, and data analysis
- **Async Support**: Full asynchronous implementation using asyncio
- **Batch Processing**: Concurrent task processing capabilities
- **Interactive Testing**: Command-line interface for manual testing
- **Comprehensive Tests**: Full test suite with async testing and mock fixtures

## How to Use

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-agents-basic
   ```

2. **Choose your implementation**:
   - For MCP: Navigate to `mcp/` directory
   - For A2A Protocol: Navigate to `a2a-protocol/` directory  
   - For JSON-RPC: Navigate to `json-rpc/` directory

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run examples**:
   ```bash
   # MCP Server
   python server.py
   
   # MCP Client
   python client.py
   ```

5. **Run tests**:
   ```bash
   # Install pytest if not already installed
   pip install pytest
   
   # Run all tests in a specific implementation
   pytest tests/
   
   # Run with verbose output
   pytest tests/ -v
   ```

### Detailed Usage

Each subdirectory contains comprehensive documentation with:
- **Installation instructions**
- **Usage examples**
- **API reference**
- **Extension guidelines**
- **Testing instructions**

Refer to the individual README files in each directory for specific setup and usage instructions.

## Requirements

### System Requirements
- **Python 3.6+** (recommended: Python 3.8+)
- **Operating System**: Windows, macOS, or Linux

### Dependencies
Each implementation has its own specific requirements:

- **MCP**: `aiohttp`, `aiohttp-cors`, `psutil`, `pytest`
- **A2A Protocol**: `a2a-json-rpc`, `asyncio`, `pytest`
- **JSON-RPC**: `werkzeug`, `requests`, `pytest`

See individual `requirements.txt` files in each subdirectory for complete dependency lists.

## License

This project is open source and available under the [MIT License](LICENSE).

## Summary

This repository serves as a comprehensive learning resource for understanding AI agent communication patterns and protocols. It provides:

- **Educational Examples**: Well-documented implementations demonstrating best practices
- **Multiple Protocols**: Coverage of MCP, A2A, and JSON-RPC communication patterns
- **Production-Ready Code**: Robust implementations with comprehensive error handling
- **Comprehensive Testing**: Full test suites for all implementations with unit, integration, and async tests
- **Extensibility**: Easy-to-extend architectures for custom implementations

Whether you're learning about AI agents, implementing agent communication systems, or building multi-agent applications, this repository provides the foundational knowledge and practical examples needed to get started.

For more AI agent resources and insights, visit [OpenAGI AI Agents](https://openagi.news/ai-agents/).
