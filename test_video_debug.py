#!/usr/bin/env python3
"""
视频生成调试测试脚本
用于验证倒计时修复和错误处理增强
"""

import requests
import time
import json

def test_video_generation():
    """测试视频生成功能"""
    
    # 测试参数
    base_url = "http://localhost:8080"
    test_session_id = "test_session_123"
    test_image_url = "/uploads/test_image.png"  # 假设存在的测试图片
    test_prompt = "一只可爱的卡通猫咪在草地上开心地跑跳，阳光明媚，画面温馨"
    
    print("🧪 开始测试视频生成功能")
    print(f"   Base URL: {base_url}")
    print(f"   Session ID: {test_session_id}")
    print(f"   提示词: {test_prompt}")
    
    # 1. 测试视频生成启动
    print("\n📤 步骤1: 发送视频生成请求")
    
    try:
        response = requests.post(f"{base_url}/api/generate-video", 
            json={
                "session_id": test_session_id,
                "image_url": test_image_url,
                "prompt": test_prompt,
                "duration": 8,
                "aspect_ratio": "16:9",
                "quality": "720p",
                "motion_intensity": "medium"
            },
            timeout=30
        )
        
        print(f"   响应状态: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get('success'):
                task_id = data.get('task_id')
                print(f"✅ 视频生成任务启动成功: {task_id}")
                
                # 2. 测试状态轮询
                print(f"\n🔄 步骤2: 轮询任务状态")
                test_status_polling(base_url, task_id)
            else:
                print(f"❌ 视频生成启动失败: {data.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"   错误内容: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误 - 请确保Flask服务器正在运行")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

def test_status_polling(base_url, task_id):
    """测试状态轮询"""
    
    max_polls = 10  # 最多轮询10次
    poll_count = 0
    
    while poll_count < max_polls:
        poll_count += 1
        print(f"   📊 轮询第{poll_count}次: {task_id}")
        
        try:
            response = requests.get(f"{base_url}/api/video-status/{task_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   状态: {data.get('status')}, 进度: {data.get('progress', 'N/A')}%")
                print(f"   消息: {data.get('message', 'N/A')}")
                
                if data.get('status') == 'completed':
                    print(f"✅ 视频生成完成: {data.get('video_url')}")
                    break
                elif data.get('status') == 'failed':
                    print(f"❌ 视频生成失败: {data.get('error')}")
                    break
                elif data.get('status') == 'content_filtered':
                    print(f"⚠️ 内容被过滤: {data.get('message')}")
                    break
                else:
                    print(f"   ⏳ 继续等待...")
                    time.sleep(3)  # 等待3秒
            else:
                print(f"   ❌ 状态查询失败: {response.status_code}")
                print(f"   错误内容: {response.text}")
                break
                
        except Exception as e:
            print(f"   ❌ 状态查询异常: {str(e)}")
            time.sleep(3)
    
    if poll_count >= max_polls:
        print(f"⏰ 轮询超时（{max_polls}次）")

def test_timing_calculation():
    """测试时间计算修复"""
    print("\n🕐 测试倒计时时间计算:")
    
    # 测试不同视频时长的预估时间
    durations = [4, 6, 8]
    
    for duration in durations:
        estimated_seconds = duration * 15  # 每秒视频约需15秒处理时间
        minutes = estimated_seconds // 60
        seconds = estimated_seconds % 60
        
        print(f"   {duration}秒视频 -> 预估{estimated_seconds}秒 ({minutes}分{seconds}秒)")
        
        # 验证修复前后的差异
        old_calculation = duration * 60  # 旧的错误计算
        old_minutes = old_calculation // 60
        
        print(f"   修复前: {duration}秒视频 -> 错误的{old_calculation}秒 ({old_minutes}分)")
        print(f"   修复后: {duration}秒视频 -> 正确的{estimated_seconds}秒 ({minutes}分{seconds}秒)")
        print()

def check_server_status():
    """检查服务器状态"""
    print("🔍 检查服务器状态...")
    
    try:
        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"⚠️ 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 服务器未运行 - 请先启动Flask应用")
        return False
    except Exception as e:
        print(f"❌ 服务器检查失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 视频生成调试测试")
    print("=" * 60)
    
    # 1. 测试时间计算修复
    test_timing_calculation()
    
    # 2. 检查服务器状态
    if check_server_status():
        # 3. 测试视频生成（如果服务器可用）
        print("\n" + "=" * 60)
        test_video_generation()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)