# JSON-RPC Example

A simple JSON-RPC 2.0 implementation example using Python, demonstrating both server and client functionality.

## Overview

JSON-RPC is a lightweight, stateless remote procedure call (RPC) protocol encoded in JSON, often used for communication between client and server applications. Below is an explanation and a basic example of using JSON-RPC in Python.

### What is JSON-RPC?

JSON-RPC sends requests as JSON objects describing the method to call, its parameters, and an ID for tracking the response.

The server responds with a JSON object containing either the result or an error, along with the same ID for correlation.

It is transport-agnostic—can run over HTTP, WebSocket, etc.—and is commonly found in blockchain and API integrations.


This project demonstrates how to implement a JSON-RPC 2.0 server and client using Python. The server provides several example methods, and the client shows how to interact with these methods.

## Features

- JSON-RPC 2.0 compliant server implementation
- Example RPC methods: `echo`, `add`, and `foobar`
- Simple HTTP-based transport using Werkzeug
- Client implementation with example calls
- Error handling and response validation

## Requirements

- Python 3.6+
- See `requirements.txt` for dependencies

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd json-rpc-example
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

Start the JSON-RPC server on `localhost:4000`:

```bash
python server.py
```

The server will be available at `http://localhost:4000/jsonrpc`

### Running the Client

In a separate terminal, run the client to test the server:

```bash
python client.py
```

The client will make example calls to the server and display the results.

## API Methods

The server provides the following JSON-RPC methods:

### `echo`
Echoes back the input string.

**Parameters:**
- `s` (string): The string to echo

**Example:**
```json
{
  "method": "echo",
  "params": ["Hello World"],
  "jsonrpc": "2.0",
  "id": 1
}
```

### `add`
Adds two numbers together.

**Parameters:**
- `a` (number): First number
- `b` (number): Second number

**Example:**
```json
{
  "method": "add",
  "params": [5, 3],
  "jsonrpc": "2.0",
  "id": 2
}
```

### `foobar`
Concatenates two string parameters.

**Parameters:**
- `foo` (string): First string
- `bar` (string): Second string

**Example:**
```json
{
  "method": "foobar",
  "params": {"foo": "Hello", "bar": "World"},
  "jsonrpc": "2.0",
  "id": 3
}
```

## Project Structure

```
json-rpc/
├── server.py          # JSON-RPC server implementation
├── client.py          # Client example with test calls
├── requirements.txt   # Python dependencies
├── README.md         # This file
├── LICENSE           # MIT License
├── tests/            # Test suite
│   ├── __init__.py   # Test package initialization
│   ├── conftest.py   # Pytest configuration and fixtures
│   ├── test_server.py # Server functionality tests
│   └── test_client.py # Client functionality tests
└── .gitignore        # Git ignore rules
```

## Dependencies

- **json-rpc**: JSON-RPC 2.0 implementation
- **requests**: HTTP client library
- **werkzeug**: WSGI utility library for the server

## Testing

### Running Tests

The project includes comprehensive test suites for both server and client functionality. Tests are located in the `tests/` directory.

#### Run All Tests
```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_server.py
pytest tests/test_client.py
```

#### Test Coverage
The test suite includes:

- **Server Tests** (`test_server.py`):
  - Method functionality testing (echo, add, foobar)
  - Error handling (invalid methods, malformed JSON)
  - Batch request processing
  - Notification handling
  - Request validation

- **Client Tests** (`test_client.py`):
  - Request structure validation
  - Response handling
  - Error scenarios
  - JSON serialization
  - Connection error handling

- **Integration Tests**:
  - End-to-end workflow testing
  - Concurrent request handling
  - Error recovery scenarios

#### Manual Testing
The client script includes basic tests that verify the server responses. Run the client to execute these tests:

```bash
python client.py
```

Expected output:
```
{'result': 'echome!', 'jsonrpc': '2.0', 'id': 0}
Echo test passed!
{'result': 8, 'jsonrpc': '2.0', 'id': 1}
Add test passed!
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).


### Summary

JSON-RPC provides a standard method for clients to call remote methods using JSON messages.

Python libraries like json-rpc and requests make implementation straightforward for both server and client.

The protocol is simple, stateless, and can be integrated into various frameworks.
