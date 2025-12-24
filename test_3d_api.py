"""测试3D模型生成接口"""
import requests
import sys
import io

# 设置控制台编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 测试数据 - 使用一个真实存在的图片路径
test_data = {
    'image_path': 'creation_sessions/11dd9c0b-5c72-44c5-be04-2d2fc0b7b631/image_v1_0294971b.png',
    'session_id': 'test-session-123',
    'version_note': '测试3D模型'
}

print("发送测试请求到 /generate-3d-model")
print(f"测试数据: {test_data}")
print("=" * 60)

try:
    response = requests.post(
        'http://localhost/generate-3d-model',
        data=test_data,
        timeout=10
    )
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容:")
    print(response.text)
    
    if response.status_code == 500:
        print("\n服务器内部错误")
        try:
            error_data = response.json()
            if 'trace' in error_data:
                print("\n错误堆栈:")
                print(error_data['trace'])
        except:
            pass
    
except requests.exceptions.ConnectionError:
    print("无法连接到服务器，请确保服务正在运行")
except Exception as e:
    print(f"请求失败: {str(e)}")
