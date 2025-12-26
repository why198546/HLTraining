import requests
import sys

url = "http://localhost/generate-3d-model"
data = {
    'image_path': 'creation_sessions/11dd9c0b-5c72-44c5-be04-2d2fc0b7b631/image_v1_0294971b.png',
    'session_id': 'test-123',
    'version_note': 'test'
}

try:
    print("Sending request...")
    sys.stdout.flush()
    
    response = requests.post(url, data=data, timeout=5)
    
    print(f"Status: {response.status_code}")
    sys.stdout.flush()
    
    print("Response:")
    print(response.text[:2000])  # First 2000 chars
    sys.stdout.flush()
    
except requests.Timeout:
    print("Request timed out - 3D generation takes time")
except Exception as e:
    print(f"Error: {e}")
    sys.stdout.flush()
