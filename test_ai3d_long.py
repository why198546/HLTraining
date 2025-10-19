#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
长时间测试腾讯云AI3D API
"""

import os
import base64
import json
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_long_run():
    """长时间测试"""
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
        print("🚀 提交3D生成任务...")
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
        
        # 2. 长时间轮询
        print("⏳ 开始长时间轮询...")
        max_attempts = 60  # 最多等待10分钟
        
        for attempt in range(max_attempts):
            print(f"⏳ 检查状态 ({attempt + 1}/{max_attempts})...")
            
            # 查询状态
            status_req = models.QueryHunyuanTo3DJobRequest()
            status_params = {"JobId": job_id}
            status_req.from_json_string(json.dumps(status_params))
            
            status_resp = client.QueryHunyuanTo3DJob(status_req)
            status_result = json.loads(status_resp.to_json_string())
            
            if 'Status' in status_result:
                status = status_result['Status']
                print(f"📊 当前状态: {status}")
                
                if status == 'SUCCESS':
                    print(f"🎉 任务完成!")
                    
                    # 检查模型文件
                    result_files = status_result.get('ResultFile3Ds', [])
                    if result_files:
                        for i, file_info in enumerate(result_files):
                            print(f"📁 文件 {i+1}: {file_info}")
                            model_url = file_info.get('Url', '')
                            if model_url:
                                print(f"🔗 模型URL: {model_url}")
                                return True
                    else:
                        # 尝试旧字段
                        model_url = status_result.get('ModelUrl', '')
                        if model_url:
                            print(f"🔗 模型URL: {model_url}")
                            return True
                        else:
                            print("❌ 未找到模型下载链接")
                            print(f"📋 完整响应: {status_result}")
                            return False
                elif status == 'FAILED':
                    error_msg = status_result.get('ErrorMessage', '生成失败')
                    print(f"❌ 任务失败: {error_msg}")
                    print(f"📋 完整响应: {status_result}")
                    return False
                elif status in ['PROCESSING', 'PENDING', 'RUN']:
                    print(f"⏳ 任务进行中，等待10秒...")
                    time.sleep(10)
                    continue
                else:
                    print(f"❓ 未知状态: {status}")
                    print(f"📋 完整响应: {status_result}")
                    time.sleep(10)
            else:
                print(f"⚠️ 响应中没有Status字段")
                print(f"📋 完整响应: {status_result}")
                time.sleep(10)
        
        print("⏰ 达到最大轮询次数")
        return False
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=== AI3D长时间测试 ===\n")
    
    start_time = time.time()
    success = test_long_run()
    end_time = time.time()
    
    duration = end_time - start_time
    
    print(f"\n=== 测试完成 ===")
    print(f"⏱️ 耗时: {duration:.1f} 秒")
    
    if success:
        print("🎉 测试成功！")
    else:
        print("❌ 测试失败")

if __name__ == "__main__":
    main()