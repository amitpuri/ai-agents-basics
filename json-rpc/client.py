import requests
import json


def main():
    url = "http://localhost:4000/jsonrpc"
    headers = {'content-type': 'application/json'}

    # Example echo method
    payload = {
        "method": "echo",
        "params": ["echome!"],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    print(response)
    assert response["result"] == "echome!"
    assert response["jsonrpc"]
    assert response["id"] == 0
    print("Echo test passed!")

    # Example add method
    payload = {
        "method": "add",
        "params": [5, 3],
        "jsonrpc": "2.0",
        "id": 1,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    print(response)
    assert response["result"] == 8
    assert response["jsonrpc"]
    assert response["id"] == 1
    print("Add test passed!")   


if __name__ == "__main__":
    main()
