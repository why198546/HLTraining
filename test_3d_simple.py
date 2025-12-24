import requests
import json

# Create session
response = requests.post('http://localhost/api/create-session', json={})
session_data = response.json()
session_id = session_data.get('session_id')
print(f"Session ID: {session_id}")

# Generate 3D model
test_data = {
    'image_path': 'creation_sessions/11dd9c0b-5c72-44c5-be04-2d2fc0b7b631/image_v1_0294971b.png',
    'session_id': session_id,
    'version_note': 'Test 3D model'
}

print("Sending request...")
response = requests.post('http://localhost/generate-3d-model', data=test_data)

print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))
