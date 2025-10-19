#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import base64
import time
from dotenv import load_dotenv
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ai3d.v20250513 import ai3d_client, models

# 加载环境变量
load_dotenv()

def test_job_status():
    """测试指定JobId的状态"""
    job_id = "1371476990607368192"  # 从日志中获取的JobId
    
    print(f"🔍 检查JobId {job_id} 的详细状态...")
    
    try:
        # 获取环境变量
        secret_id = os.environ.get('TENCENTCLOUD_SECRET_ID')
        secret_key = os.environ.get('TENCENTCLOUD_SECRET_KEY')
        
        if not secret_id or not secret_key:
            print("❌ 缺少腾讯云API密钥环境变量")
            return
            
        # 创建认证对象
        try:
            cred = credential.EnvironmentVariableCredential().get_credential()
        except Exception:
            # 如果环境变量凭据不可用，尝试直接从环境变量读取
            secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
            secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
            
            if not secret_id or not secret_key:
                print("⚠️ 未找到腾讯云密钥，请设置TENCENTCLOUD_SECRET_ID和TENCENTCLOUD_SECRET_KEY环境变量")
                return
            
            cred = credential.Credential(secret_id, secret_key)
        
        # 配置客户端
        http_profile = HttpProfile()
        http_profile.endpoint = "ai3d.tencentcloudapi.com"
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        
        # 创建客户端
        client = ai3d_client.Ai3dClient(cred, "ap-guangzhou", client_profile)
        
        # 查询任务状态
        req = models.QueryHunyuanTo3DJobRequest()
        params = {
            "JobId": job_id
        }
        req.from_json_string(str(params).replace("'", '"'))
        
        resp = client.QueryHunyuanTo3DJob(req)
        result = resp.to_json_string()
        
        print(f"📋 API原始响应:")
        print(result)
        
        # 解析响应
        import json
        response_data = json.loads(result)
        
        if 'Status' in response_data:
            status = response_data['Status']
            print(f"\n📊 当前状态: {status}")
            
            if 'StatusMsg' in response_data:
                print(f"📝 状态描述: {response_data['StatusMsg']}")
                
            if 'ErrorCode' in response_data:
                print(f"❌ 错误代码: {response_data['ErrorCode']}")
                
            if 'ErrorMessage' in response_data:
                print(f"❌ 错误消息: {response_data['ErrorMessage']}")
                
            if 'ResultFile3Ds' in response_data:
                files = response_data['ResultFile3Ds']
                print(f"📁 结果文件: {len(files)} 个")
                for i, file in enumerate(files):
                    print(f"  文件 {i+1}: {file}")
            
            if 'Progress' in response_data:
                print(f"📈 进度: {response_data['Progress']}%")
        else:
            print("❌ 响应中没有状态信息")
            
    except Exception as e:
        print(f"❌ 查询状态失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_job_status()