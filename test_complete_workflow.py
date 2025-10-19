#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整测试3D模型生成和前端访问
"""

import os
import requests
import time

def test_complete_3d_workflow():
    """测试完整的3D模型生成工作流"""
    print("🧪 测试完整的3D模型生成工作流...")
    
    base_url = "http://127.0.0.1:8080"
    
    try:
        # 1. 检查服务器是否运行
        print("🔍 检查Flask服务器...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code != 200:
            print("❌ Flask服务器未运行，请先启动应用")
            return
        print("✅ Flask服务器运行正常")
        
        # 2. 测试生成文字图片
        print("🎨 测试图片生成...")
        image_data = {
            'text': '一个可爱的机器人'
        }
        
        response = requests.post(f"{base_url}/generate-image", json=image_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                image_url = result.get('image_url')
                print(f"✅ 图片生成成功: {image_url}")
                
                # 3. 测试3D模型生成
                print("🧊 测试3D模型生成...")
                model_data = {
                    'image_url': image_url
                }
                
                response = requests.post(f"{base_url}/generate-3d-model", json=model_data, timeout=300)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        model_url = result.get('model_url')
                        print(f"✅ 3D模型生成成功: {model_url}")
                        
                        # 4. 测试模型文件访问
                        print("📂 测试模型文件访问...")
                        response = requests.head(f"{base_url}{model_url}", timeout=10)
                        if response.status_code == 200:
                            print(f"✅ 模型文件可访问")
                            print(f"📏 文件大小: {response.headers.get('Content-Length')} 字节")
                            print(f"📋 文件类型: {response.headers.get('Content-Type')}")
                        else:
                            print(f"❌ 模型文件访问失败: HTTP {response.status_code}")
                    else:
                        print(f"❌ 3D模型生成失败: {result.get('error', '未知错误')}")
                else:
                    print(f"❌ 3D模型生成请求失败: HTTP {response.status_code}")
            else:
                print(f"❌ 图片生成失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ 图片生成请求失败: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求错误: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_complete_3d_workflow()