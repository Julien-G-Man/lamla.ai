import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Get the token
token = os.getenv('HUGGING_FACE_API_TOKEN')
print(f"Token exists: {bool(token)}")
print(f"Token preview: {token[:4]}...{token[-4:] if token else 'None'}")

# Test with a simple model
API_URL = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": f"Bearer {token}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    print(f"Status code: {response.status_code}")
    print(f"Raw response: {response.text}")
    try:
        return response.json()
    except Exception as e:
        print(f"JSON decode error: {e}")
        return None

try:
    output = query({
        "inputs": "Hello, I am",
        "parameters": {
            "max_new_tokens": 10,
            "temperature": 0.7
        }
    })
    print("\nTest generation successful!")
    print(f"Response: {output}")
    
except Exception as e:
    print(f"\nError occurred: {str(e)}") 