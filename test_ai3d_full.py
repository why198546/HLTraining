#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试腾讯云AI3D API的完整流程
"""

import os
import base64
import json
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_complete_workflow():
    """测试完整的工作流程"""
    try:
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.ai3d.v20250513 import ai3d_client, models
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
        
        # 初始化客户端
        cred = credential.EnvironmentVariableCredential().get_credential()
        httpProfile = HttpProfile()
        httpProfile.endpoint = "ai3d.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = ai3d_client.Ai3dClient(cred, "ap-guangzhou", clientProfile)
        
        # 测试图片路径
        test_image_path = "uploads/nano_banana_text_1760877952.png"
        
        if not os.path.exists(test_image_path):
            print(f"❌ 测试图片不存在: {test_image_path}")
            return False
        
        # 编码图片
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        print(f"📸 图片编码成功，大小: {len(image_base64)} 字符")
        
        # 1. 提交任务
        print("🚀 步骤1: 提交3D生成任务...")
        req = models.SubmitHunyuanTo3DJobRequest()
        params = {
            "ImageBase64": image_base64,
            "OutputType": "glb"
        }
        req.from_json_string(json.dumps(params))
        
        resp = client.SubmitHunyuanTo3DJob(req)
        result = json.loads(resp.to_json_string())
        
        if 'JobId' not in result:
            print(f"❌ 任务提交失败: {result}")
            return False
        
        job_id = result['JobId']
        print(f"✅ 任务提交成功，JobId: {job_id}")
        
        # 2. 轮询任务状态
        print("⏳ 步骤2: 轮询任务状态...")
        max_attempts = 5  # 减少测试时间
        
        for attempt in range(max_attempts):
            print(f"   检查状态 ({attempt + 1}/{max_attempts})...")
            
            # 查询状态
            status_req = models.QueryHunyuanTo3DJobRequest()
            status_params = {"JobId": job_id}
            status_req.from_json_string(json.dumps(status_params))
            
            status_resp = client.QueryHunyuanTo3DJob(status_req)
            status_result = json.loads(status_resp.to_json_string())
            
            print(f"   📋 状态响应: {status_result}")
            
            if 'Status' in status_result:
                status = status_result['Status']
                print(f"   📊 当前状态: {status}")
                
                if status == 'SUCCESS':
                    model_url = status_result.get('ModelUrl', '')
                    print(f"🎉 任务完成! 模型URL: {model_url}")
                    return True
                elif status == 'FAILED':
                    error_msg = status_result.get('ErrorMessage', '生成失败')
                    print(f"❌ 任务失败: {error_msg}")
                    return False
                elif status in ['PROCESSING', 'PENDING']:
                    print(f"   ⏳ 状态: {status}，等待中...")
                    time.sleep(10)
                    continue
                else:
                    print(f"   ❓ 未知状态: {status}")
            else:
                print(f"   ⚠️  状态响应中没有Status字段")
            
            time.sleep(5)
        
        print("⏰ 轮询超时，但任务可能仍在处理中")
        return False
        
    except TencentCloudSDKException as e:
        print(f"❌ 腾讯云SDK错误:")
        print(f"   错误代码: {e.code}")
        print(f"   错误消息: {e.message}")
        print(f"   请求ID: {getattr(e, 'requestId', 'N/A')}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=== 腾讯云AI3D完整流程测试 ===\n")
    
    success = test_complete_workflow()
    
    print("\n=== 测试结果 ===")
    if success:
        print("🎉 测试完全成功！")
    else:
        print("⚠️ 测试未完成（可能需要更长时间等待）")

if __name__ == "__main__":
    main()