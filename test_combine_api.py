#!/usr/bin/env python3
"""Test the combine-images API"""

import io
import os
import tempfile

import requests
from PIL import Image


# Create test images
def create_test_image(filename, color=(255, 0, 0)):
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color=color)
    img.save(filename)
    return filename

import os
# Create test images
import tempfile

temp_dir = tempfile.gettempdir()
photo_file = create_test_image(os.path.join(temp_dir, 'test_photo.png'), (255, 0, 0))
artwork_file = create_test_image(os.path.join(temp_dir, 'test_artwork.png'), (0, 255, 0))

# Prepare files for upload
with open(photo_file, 'rb') as f:
    photo_data = f.read()
with open(artwork_file, 'rb') as f:
    artwork_data = f.read()

files = {
    'photo': ('photo.png', photo_data, 'image/png'),
    'artwork': ('artwork.png', artwork_data, 'image/png')
}

data = {
    'lesson_key': 'formal_hairstyle'
}

print("Testing /api/combine-images endpoint...")
print(f"Files: {list(files.keys())}")
print(f"Data: {data}")

try:
    response = requests.post(
        'http://localhost:80/api/combine-images',
        files=files,
        data=data,
        timeout=180
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Text: {response.text[:500]}")
    
    try:
        json_data = response.json()
        print(f"JSON Response: {json_data}")
    except:
        print("Could not parse JSON response")
        
except Exception as e:
    print(f"Error: {e}")

# Clean up
try:
    os.remove(photo_file)
    os.remove(artwork_file)
except:
    pass
