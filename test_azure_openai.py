import requests

endpoint = "https://julien-resource.cognitiveservices.azure.com/openai/deployments/gpt-4o-mini-deployment/chat/completions?api-version=2025-01-01-preview"
api_key = "rFTWJj68qMdHTyrzkvUGoCPrTENNIXXQ6YBm8iwHB7pwWUUZ9PKUJQQJ99BGACYeBjFXJ3w3AAAAACOGupic"

headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

payload = {
    "messages": [
        {"role": "user", "content": "Hello! Can you confirm you are working?"}
    ],
    "max_tokens": 50,
    "temperature": 0.7
}

try:
    response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
    print("Status code:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
