"""在Flask应用上下文中测试Hunyuan3D"""
import os
import sys

# 确保工作目录正确
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from dotenv import load_dotenv
load_dotenv()

# 导入Flask应用
from app import create_app
app = create_app()

print("=" * 60)
print("在Flask应用上下文中测试3D生成")
print("=" * 60)

with app.app_context():
    print("\n✅ Flask应用上下文已创建")
    
    print("\n检查环境变量:")
    secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
    secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
    print(f"  SECRET_ID: {'已设置' if secret_id else '未设置'}")
    print(f"  SECRET_KEY: {'已设置' if secret_key else '未设置'}")
    
    print("\n初始化Hunyuan3DGenerator...")
    from api.hunyuan3d import Hunyuan3DGenerator
    
    try:
        generator = Hunyuan3DGenerator()
        
        if generator.client:
            print("✅ Client初始化成功")
            print(f"   Client类型: {type(generator.client)}")
        else:
            print("❌ Client为None")
            
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
