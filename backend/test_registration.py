import requests
import json

print("Testing registration endpoint...\n")

url = "http://localhost:8000/auth/register"
payload = {
    "username": "testuser123",
    "email": "testuser@example.com",
    "password": "Password123!"
}

try:
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}\n")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f"ERROR: {e}")
