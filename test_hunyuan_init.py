"""直接测试Hunyuan3D初始化"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("测试Hunyuan3D Generator初始化")
print("=" * 60)

# 检查.env文件
if os.path.exists('.env'):
    print("✅ .env文件存在")
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            if 'TENCENTCLOUD' in line and '=' in line:
                key = line.split('=')[0]
                print(f"   {key}=***")
else:
    print("❌ .env文件不存在")

print("")
print("加载dotenv...")
from dotenv import load_dotenv
load_dotenv()

# 检查环境变量
print("")
print("检查环境变量:")
secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
print(f"  TENCENTCLOUD_SECRET_ID: {'已设置' if secret_id else '未设置'}")
print(f"  TENCENTCLOUD_SECRET_KEY: {'已设置' if secret_key else '未设置'}")

if secret_id:
    print(f"  ID前10位: {secret_id[:10]}...")
if secret_key:
    print(f"  KEY前10位: {secret_key[:10]}...")

print("")
print("初始化Hunyuan3DGenerator...")
try:
    from api.hunyuan3d import Hunyuan3DGenerator
    generator = Hunyuan3DGenerator()
    print("")
    if generator.client:
        print("✅ 初始化成功！Client可用")
    else:
        print("❌ 初始化失败！Client为None")
except Exception as e:
    print(f"❌ 初始化异常: {e}")
    import traceback
    traceback.print_exc()
