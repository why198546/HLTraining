import requests

# 测试generate-image API
url = "http://127.0.0.1:8080/generate-image"
data = {"prompt": "一只可爱的小猫"}

print("🧪 测试 generate-image API...")

try:
    response = requests.post(url, data=data, timeout=30)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"错误: {e}")