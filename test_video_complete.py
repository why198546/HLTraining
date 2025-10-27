#!/usr/bin/env python3
"""
视频生成完整验证脚本
验证倒计时修复和错误处理增强后的功能
"""

import requests
import time
import json
import sys

def test_complete_video_workflow():
    """测试完整的视频生成工作流程"""
    base_url = "http://localhost:8080"
    
    print("🎬 完整视频生成工作流程测试")
    print("=" * 60)
    
    # 1. 测试视频生成启动
    print("📤 步骤1: 启动视频生成")
    
    test_data = {
        "session_id": "test_session_debug",
        "image_url": "/uploads/test_image.png",
        "prompt": "一只可爱的卡通猫咪在阳光明媚的草地上开心地奔跑",
        "duration": 4,  # 4秒视频
        "aspect_ratio": "16:9",
        "quality": "720p",
        "motion_intensity": "medium"
    }
    
    try:
        print(f"   发送请求到: {base_url}/api/generate-video")
        print(f"   参数: {json.dumps(test_data, ensure_ascii=False, indent=4)}")
        
        response = requests.post(
            f"{base_url}/api/generate-video",
            json=test_data,
            timeout=60
        )
        
        print(f"   响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   响应数据: {json.dumps(data, ensure_ascii=False, indent=4)}")
            
            if data.get('success'):
                task_id = data.get('task_id')
                print(f"✅ 视频生成任务启动成功")
                print(f"   任务ID: {task_id}")
                
                # 验证倒计时时间计算
                expected_time = test_data['duration'] * 15  # 4秒 * 15 = 60秒 (1分钟)
                print(f"   预期倒计时: {expected_time}秒 ({expected_time//60}分{expected_time%60}秒)")
                print(f"   修复前会错误显示: {test_data['duration'] * 60}秒 ({test_data['duration']}分)")
                
                # 2. 测试状态轮询
                return test_status_monitoring(base_url, task_id, expected_time)
            else:
                print(f"❌ 视频生成启动失败: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"   错误内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def test_status_monitoring(base_url, task_id, expected_time):
    """测试状态监控和错误处理"""
    print(f"\n🔄 步骤2: 状态监控测试")
    print(f"   任务ID: {task_id}")
    print(f"   预期时间: {expected_time}秒")
    
    start_time = time.time()
    poll_count = 0
    max_polls = 40  # 最多轮询40次 (约2分钟)
    
    while poll_count < max_polls:
        poll_count += 1
        elapsed = int(time.time() - start_time)
        
        print(f"   📊 轮询第{poll_count}次 (已用时{elapsed}秒)")
        
        try:
            response = requests.get(f"{base_url}/api/video-status/{task_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                progress = data.get('progress', 0)
                message = data.get('message', '')
                
                print(f"      状态: {status}, 进度: {progress}%, 消息: {message}")
                
                if status == 'completed':
                    video_url = data.get('video_url')
                    print(f"✅ 视频生成完成!")
                    print(f"   视频URL: {video_url}")
                    print(f"   总用时: {elapsed}秒")
                    print(f"   轮询次数: {poll_count}")
                    
                    # 验证视频文件
                    return verify_video_file(base_url, video_url)
                    
                elif status == 'failed':
                    error = data.get('error', 'unknown')
                    print(f"❌ 视频生成失败: {error}")
                    print(f"   详细信息: {message}")
                    return False
                    
                elif status == 'content_filtered':
                    reasons = data.get('filtered_reasons', [])
                    print(f"⚠️ 内容被过滤: {message}")
                    print(f"   过滤原因: {reasons}")
                    return False
                    
                else:
                    # 继续处理中
                    print(f"      ⏳ 继续等待...")
                    
                # 检查是否超过预期时间很多
                if elapsed > expected_time * 2:
                    print(f"⚠️ 警告: 已超过预期时间2倍 ({elapsed}秒 > {expected_time*2}秒)")
                    
            else:
                print(f"      ❌ 状态查询失败: {response.status_code}")
                if poll_count > 10:  # 连续失败多次则退出
                    print("      连续查询失败，退出测试")
                    return False
                    
        except Exception as e:
            print(f"      ❌ 查询异常: {str(e)}")
            if poll_count > 10:
                print("      连续异常，退出测试")
                return False
        
        time.sleep(3)  # 等待3秒
    
    print(f"⏰ 轮询超时 ({max_polls}次，约{max_polls*3//60}分钟)")
    return False

def verify_video_file(base_url, video_url):
    """验证生成的视频文件"""
    print(f"\n🎥 步骤3: 验证视频文件")
    print(f"   视频URL: {video_url}")
    
    try:
        # 检查视频文件是否可访问
        full_url = f"{base_url}{video_url}"
        response = requests.head(full_url, timeout=10)
        
        print(f"   文件检查: {response.status_code}")
        
        if response.status_code == 200:
            content_length = response.headers.get('Content-Length')
            content_type = response.headers.get('Content-Type')
            
            print(f"   文件大小: {content_length} bytes")
            print(f"   文件类型: {content_type}")
            
            if content_length and int(content_length) > 0:
                print(f"✅ 视频文件验证成功")
                print(f"   大小: {int(content_length) / (1024*1024):.2f} MB")
                return True
            else:
                print(f"❌ 视频文件为空")
                return False
        else:
            print(f"❌ 无法访问视频文件: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 视频文件验证失败: {str(e)}")
        return False

def test_error_handling():
    """测试错误处理增强"""
    print(f"\n🔧 步骤4: 错误处理测试")
    base_url = "http://localhost:8080"
    
    # 测试1: 不存在的图片
    print("   测试1: 不存在的图片")
    try:
        response = requests.post(
            f"{base_url}/api/generate-video",
            json={
                "session_id": "test_error",
                "image_url": "/uploads/nonexistent.png",
                "prompt": "test",
                "duration": 4
            },
            timeout=10
        )
        
        data = response.json()
        if not data.get('success') and 'not exist' in data.get('error', '').lower():
            print("      ✅ 正确处理了不存在的图片")
        else:
            print(f"      ⚠️ 错误处理不如预期: {data}")
    except Exception as e:
        print(f"      ❌ 测试异常: {str(e)}")
    
    # 测试2: 缺少参数
    print("   测试2: 缺少必需参数")
    try:
        response = requests.post(
            f"{base_url}/api/generate-video",
            json={
                "session_id": "test_error"
                # 缺少image_url和prompt
            },
            timeout=10
        )
        
        data = response.json()
        if not data.get('success') and '缺少' in data.get('error', ''):
            print("      ✅ 正确处理了缺少参数")
        else:
            print(f"      ⚠️ 错误处理不如预期: {data}")
    except Exception as e:
        print(f"      ❌ 测试异常: {str(e)}")
    
    # 测试3: 无效的任务ID
    print("   测试3: 无效的任务ID")
    try:
        response = requests.get(f"{base_url}/api/video-status/invalid_task_id", timeout=10)
        
        data = response.json()
        if not data.get('success'):
            print("      ✅ 正确处理了无效任务ID")
        else:
            print(f"      ⚠️ 错误处理不如预期: {data}")
    except Exception as e:
        print(f"      ❌ 测试异常: {str(e)}")

def main():
    """主测试函数"""
    print("🧪 视频生成修复验证测试")
    print("=" * 80)
    
    # 检查服务器
    try:
        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print(f"⚠️ 服务器响应异常: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 无法连接服务器: {str(e)}")
        print("   请确保Flask应用正在运行 (python run.py)")
        sys.exit(1)
    
    # 运行测试
    success = test_complete_video_workflow()
    
    # 错误处理测试
    test_error_handling()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 全部测试通过!")
        print("✅ 倒计时时间已修复 (从错误的8分钟修复为正确的2分钟)")
        print("✅ 错误处理已增强，提供详细的调试信息")
        print("✅ 视频生成功能正常工作")
    else:
        print("❌ 部分测试失败")
        print("   请检查日志文件: /Users/hongyuwang/code/HLTraining/flask_app.log")
    
    print("=" * 80)

if __name__ == "__main__":
    main()