import requests
import os
import shutil
import time

BASE_URL = "http://127.0.0.1:8088"
GENERATE_ENDPOINT = f"{BASE_URL}/generate-image"
STYLES = {
    "cute": "style_cute_ultraman.png",
    "realistic": "style_realistic_ultraman.png",
    "anime": "style_anime_ultraman.png",
    "fantasy": "style_fantasy_ultraman.png",
    "model_3d": "style_3d_model_ultraman.png"
}
PROMPT = "Ultraman"
TARGET_DIR = "/Users/hongyuwang/code/HLTraining/static/images/styles"

def generate_and_save(style, filename):
    print(f"Generating {style} style...")
    try:
        response = requests.post(GENERATE_ENDPOINT, data={
            "prompt": PROMPT,
            "style": style,
            "color_preference": "colorful",
            "expert_mode": "false",
            "aspect_ratio": "1:1"
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                image_url = data.get("image_url")
                # image_url is like /uploads/filename.png
                # Physical path is uploads/filename.png relative to app root
                # We assume app root is /Users/hongyuwang/code/HLTraining
                
                relative_path = image_url.lstrip('/')
                source_path = os.path.join("/Users/hongyuwang/code/HLTraining", relative_path)
                
                if os.path.exists(source_path):
                    target_path = os.path.join(TARGET_DIR, filename)
                    shutil.copy2(source_path, target_path)
                    print(f"✅ Saved to {target_path}")
                    return True
                else:
                    print(f"❌ Source file not found: {source_path}")
            else:
                print(f"❌ API returned error: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return False

def main():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        
    for style, filename in STYLES.items():
        success = generate_and_save(style, filename)
        if not success:
            print(f"⚠️ Failed to generate {style}, retrying in 5 seconds...")
            time.sleep(5)
            generate_and_save(style, filename)
        time.sleep(2) # Wait a bit between requests to avoid rate limits

if __name__ == "__main__":
    main()
