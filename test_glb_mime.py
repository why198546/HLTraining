"""测试GLB文件MIME类型"""
import requests

# 测试GLB文件访问
glb_url = "http://localhost/creation_sessions/809e3bf8-a486-45d2-b9ce-a86fc2ea5b98/model_v1_b1847a44.glb"

print("=" * 60)
print("测试GLB文件MIME类型")
print("=" * 60)
print(f"URL: {glb_url}")

response = requests.head(glb_url)
print(f"\n状态码: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Content-Length: {response.headers.get('Content-Length')}")

if response.status_code == 200:
    print("\n✅ 文件可访问")
    
    # 下载前几个字节检查文件头
    response = requests.get(glb_url, stream=True)
    first_bytes = next(response.iter_content(chunk_size=4))
    print(f"文件头: {first_bytes.hex()} ({first_bytes})")
    
    # GLB文件应该以 "glTF" (67 6C 54 46) 开头
    if first_bytes == b'glTF':
        print("✅ 文件头正确 - 这是有效的GLB文件")
    else:
        print(f"❌ 文件头错误 - 预期 'glTF'，实际 '{first_bytes}'")
else:
    print(f"\n❌ 文件不可访问")
