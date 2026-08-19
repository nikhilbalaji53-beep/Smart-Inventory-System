import requests
import json

# Test registration
print("=== Testing Registration ===")
reg_data = {"username": "testuser123", "email": "testuser@example.com", "password": "Password123!"}

try:
    response = requests.post("http://localhost:8000/auth/register", json=reg_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test login
print("\n=== Testing Login ===")
login_data = {"username": "testuser123", "password": "Password123!"}

try:
    response = requests.post("http://localhost:8000/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Token: {result['access_token'][:50]}...")
        print(f"Token Type: {result['token_type']}")
        print(f"Username: {result['username']}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
