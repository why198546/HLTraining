"""测试session和3D生成"""
import requests
import json

# 创建session
print("=" * 60)
print("1. 创建新session")
print("=" * 60)

response = requests.post('http://localhost/api/create-session', json={})
if response.status_code == 200:
    session_data = response.json()
    session_id = session_data.get('session_id')
    print(f"✅ Session创建成功: {session_id}")
else:
    print(f"❌ Session创建失败: {response.status_code}")
    print(response.text)
    exit(1)

# 生成3D模型
print("\n" + "=" * 60)
print("2. 生成3D模型")
print("=" * 60)

test_data = {
    'image_path': 'creation_sessions/11dd9c0b-5c72-44c5-be04-2d2fc0b7b631/image_v1_0294971b.png',
    'session_id': session_id,
    'version_note': '测试3D模型'
}

print(f"测试数据: {test_data}")
print("\n发送请求...")

response = requests.post('http://localhost/generate-3d-model', data=test_data)

print(f"\n响应状态码: {response.status_code}")
print("响应内容:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if response.status_code != 200:
    print("\n❌ 3D模型生成失败")
    if 'trace' in response.json():
        print("\n错误堆栈:")
        print(response.json()['trace'])
else:
    print("\n✅ 3D模型生成成功！")
