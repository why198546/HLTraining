#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试腾讯云AI3D API的调用
"""

import os
import base64
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_ai3d_import():
    """测试AI3D模块导入"""
    try:
        from tencentcloud.ai3d.v20250513 import ai3d_client, models
        print("✅ AI3D模块导入成功")
        return ai3d_client, models
    except ImportError as e:
        print(f"❌ AI3D模块导入失败: {e}")
        return None, None

def test_credentials():
    """测试凭证配置"""
    secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
    secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
    
    if secret_id and secret_key:
        print(f"✅ 环境变量配置正确")
        print(f"   SECRET_ID: {secret_id[:8]}...")
        print(f"   SECRET_KEY: {secret_key[:8]}...")
        return True
    else:
        print("❌ 环境变量未配置")
        return False

def test_client_init():
    """测试客户端初始化"""
    try:
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.ai3d.v20250513 import ai3d_client
        
        # 使用环境变量凭据
        cred = credential.EnvironmentVariableCredential().get_credential()
        
        # 配置HTTP选项
        httpProfile = HttpProfile()
        httpProfile.endpoint = "ai3d.tencentcloudapi.com"
        
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        
        # 初始化客户端
        client = ai3d_client.Ai3dClient(cred, "ap-guangzhou", clientProfile)
        
        print("✅ 客户端初始化成功")
        return client
        
    except Exception as e:
        print(f"❌ 客户端初始化失败: {e}")
        return None

def test_api_call():
    """测试API调用"""
    try:
        # 创建一个测试图片的base64
        test_image_path = "uploads/nano_banana_text_1760877952.png"
        
        if not os.path.exists(test_image_path):
            print(f"❌ 测试图片不存在: {test_image_path}")
            return False
        
        # 编码图片
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        print(f"✅ 图片编码成功，大小: {len(image_base64)} 字符")
        
        # 导入模块
        from tencentcloud.ai3d.v20250513 import models
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
        
        # 初始化客户端
        client = test_client_init()
        if not client:
            return False
        
        # 创建请求
        req = models.SubmitHunyuanTo3DJobRequest()
        params = {
            "ImageBase64": image_base64,
            "OutputType": "glb"
        }
        req.from_json_string(json.dumps(params))
        
        print("🚀 发起API调用...")
        
        # 调用API
        resp = client.SubmitHunyuanTo3DJob(req)
        result = json.loads(resp.to_json_string())
        
        print(f"✅ API调用成功")
        print(f"📋 响应: {result}")
        
        return True
        
    except TencentCloudSDKException as e:
        print(f"❌ 腾讯云SDK错误: {e}")
        print(f"   错误代码: {e.code}")
        print(f"   错误消息: {e.message}")
        return False
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=== 腾讯云AI3D API测试 ===\n")
    
    # 测试模块导入
    print("1. 测试模块导入...")
    ai3d_client, models = test_ai3d_import()
    if not ai3d_client:
        return
    
    print()
    
    # 测试凭证
    print("2. 测试凭证配置...")
    if not test_credentials():
        return
        
    print()
    
    # 测试客户端初始化
    print("3. 测试客户端初始化...")
    client = test_client_init()
    if not client:
        return
        
    print()
    
    # 测试API调用
    print("4. 测试API调用...")
    success = test_api_call()
    
    print("\n=== 测试完成 ===")
    
    if success:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查配置")

if __name__ == "__main__":
    main()