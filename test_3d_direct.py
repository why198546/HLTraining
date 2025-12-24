"""直接测试腾讯云AI3D API调用"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置工作目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

print("=" * 60)
print("测试腾讯云AI3D API直接调用")
print("=" * 60)

# 验证环境变量
secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
print(f"✅ Secret ID: {secret_id[:10]}... (已设置)")
print(f"✅ Secret Key: {secret_key[:10]}... (已设置)")

# 导入API
from api.hunyuan3d import Hunyuan3DGenerator

# 测试图片路径
test_image = "creation_sessions/11dd9c0b-5c72-44c5-be04-2d2fc0b7b631/image_v1_0294971b.png"
if not os.path.exists(test_image):
    print(f"❌ 测试图片不存在: {test_image}")
    sys.exit(1)

print(f"📁 测试图片: {test_image}")
print("=" * 60)

# 创建生成器实例
print("\n创建Hunyuan3DGenerator实例...")
generator = Hunyuan3DGenerator()

# 直接调用生成方法
print("\n调用generate_3d_model方法...")
try:
    result = generator.generate_3d_model(test_image)
    print(f"\n✅ 生成成功！")
    print(f"📦 模型文件: {result}")
except Exception as e:
    print(f"\n❌ 生成失败: {str(e)}")
    import traceback
    print(f"\n堆栈跟踪:\n{traceback.format_exc()}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
