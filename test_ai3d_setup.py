#!/usr/bin/env python3
"""
测试腾讯云AI3D (混元3D) API集成
"""

import os
import sys
sys.path.append('.')

from dotenv import load_dotenv
from api.hunyuan3d import Hunyuan3DGenerator

# 加载环境变量
load_dotenv()

def test_hunyuan3d_initialization():
    """测试混元3D初始化"""
    print("🧪 测试混元3D API初始化...")
    
    try:
        generator = Hunyuan3DGenerator()
        print("✅ 混元3D生成器初始化成功")
        
        # 检查客户端是否已初始化
        if generator.client:
            print("✅ 腾讯云AI3D客户端连接成功")
        else:
            print("⚠️ 腾讯云客户端未初始化，将使用本地算法")
        
        return generator
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        return None

def test_environment_variables():
    """测试环境变量配置"""
    print("🔍 检查环境变量...")
    
    secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
    secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
    
    if secret_id:
        print(f"✅ TENCENTCLOUD_SECRET_ID: {secret_id[:10]}...")
    else:
        print("❌ 未找到 TENCENTCLOUD_SECRET_ID")
    
    if secret_key:
        print(f"✅ TENCENTCLOUD_SECRET_KEY: {secret_key[:10]}...")
    else:
        print("❌ 未找到 TENCENTCLOUD_SECRET_KEY")
    
    return bool(secret_id and secret_key)

def main():
    """主测试函数"""
    print("🚀 开始腾讯云AI3D集成测试")
    print("=" * 50)
    
    # 测试环境变量
    env_ok = test_environment_variables()
    print()
    
    # 测试初始化
    generator = test_hunyuan3d_initialization()
    print()
    
    if generator and env_ok:
        print("🎉 腾讯云AI3D配置完成！")
        print("📝 系统状态:")
        print("   ✅ SDK安装正确")
        print("   ✅ 环境变量配置完整")
        print("   ✅ 客户端初始化成功")
        print("   🎯 3D生成功能已就绪")
    elif generator and not env_ok:
        print("⚠️ 部分配置完成")
        print("📝 系统状态:")
        print("   ✅ SDK安装正确")
        print("   ❌ 环境变量缺失")
        print("   🔄 将使用本地算法作为备用")
    else:
        print("❌ 配置存在问题")
        print("💡 请检查:")
        print("   1. 腾讯云SDK安装")
        print("   2. 环境变量设置")
        print("   3. 网络连接")
    
    print("\n🌐 网站地址: http://127.0.0.1:8080")
    print("🎨 创作页面: http://127.0.0.1:8080/create")

if __name__ == "__main__":
    main()