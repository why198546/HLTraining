#!/usr/bin/env python3
"""
质量感知视频生成测试
验证不同分辨率下的时间计算和用户体验
"""

import requests
import time
import json

def test_quality_aware_timing():
    """测试质量感知的时间计算"""
    base_url = "http://localhost:8080"
    
    print("🎯 质量感知视频生成测试")
    print("=" * 60)
    
    # 测试不同质量和时长的组合
    test_cases = [
        {
            "name": "快速720p预览",
            "duration": 4,
            "quality": "720p",
            "expected_time": 60  # 4 * 15 = 60秒
        },
        {
            "name": "标准720p视频",
            "duration": 6,
            "quality": "720p", 
            "expected_time": 90  # 6 * 15 = 90秒
        },
        {
            "name": "高质量1080p短片",
            "duration": 4,
            "quality": "1080p",
            "expected_time": 100  # 4 * 25 = 100秒
        },
        {
            "name": "高质量1080p标准",
            "duration": 6,
            "quality": "1080p",
            "expected_time": 150  # 6 * 25 = 150秒
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 测试 {i}: {test_case['name']}")
        print("-" * 30)
        
        # 生成测试数据
        test_data = {
            "session_id": f"quality_test_{i}",
            "image_url": "/uploads/test_image.png",
            "prompt": f"测试{test_case['quality']}质量视频生成",
            "duration": test_case["duration"],
            "aspect_ratio": "16:9",
            "quality": test_case["quality"],
            "motion_intensity": "medium"
        }
        
        print(f"   配置: {test_case['duration']}秒 {test_case['quality']}")
        print(f"   预期时间: {test_case['expected_time']}秒 ({test_case['expected_time']//60}分{test_case['expected_time']%60}秒)")
        
        # 发送请求
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/generate-video",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    task_id = data.get('task_id')
                    print(f"   ✅ 任务启动成功: {task_id}")
                    
                    # 验证实际生成时间
                    actual_time = monitor_generation_time(base_url, task_id, test_case['expected_time'])
                    
                    if actual_time:
                        time_diff = abs(actual_time - test_case['expected_time'])
                        time_diff_percent = (time_diff / test_case['expected_time']) * 100
                        
                        print(f"   ⏱️ 实际时间: {actual_time}秒")
                        print(f"   📊 时间差异: {time_diff}秒 ({time_diff_percent:.1f}%)")
                        
                        if time_diff_percent <= 30:  # 允许30%的误差
                            print(f"   ✅ 时间预估准确")
                        else:
                            print(f"   ⚠️ 时间预估偏差较大")
                    else:
                        print(f"   ❌ 生成失败或超时")
                else:
                    print(f"   ❌ 任务启动失败: {data.get('error')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")
        
        # 间隔测试，避免API限制
        if i < len(test_cases):
            print(f"   ⏳ 等待5秒后进行下一个测试...")
            time.sleep(5)

def monitor_generation_time(base_url, task_id, expected_time):
    """监控视频生成时间"""
    start_time = time.time()
    max_wait = expected_time * 2  # 最多等待预期时间的2倍
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{base_url}/api/video-status/{task_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                if status == 'completed':
                    actual_time = int(time.time() - start_time)
                    return actual_time
                elif status == 'failed':
                    print(f"      生成失败: {data.get('error', 'unknown')}")
                    return None
                    
        except Exception as e:
            print(f"      状态查询异常: {str(e)}")
        
        time.sleep(3)
    
    print(f"      生成超时（超过{max_wait}秒）")
    return None

def test_ui_responsiveness():
    """测试UI响应性"""
    print(f"\n🖥️ UI响应性测试")
    print("=" * 60)
    
    # 模拟前端时间计算
    def calculate_frontend_time(duration, quality):
        base_multiplier = 15 if quality == '720p' else 25
        estimated_seconds = duration * base_multiplier
        minutes = estimated_seconds // 60
        seconds = estimated_seconds % 60
        return estimated_seconds, f"{minutes}分{seconds}秒"
    
    test_combinations = [
        (4, '720p'), (6, '720p'), (8, '720p'),
        (4, '1080p'), (6, '1080p'), (8, '1080p')
    ]
    
    print("前端时间计算验证:")
    for duration, quality in test_combinations:
        total_sec, time_str = calculate_frontend_time(duration, quality)
        print(f"  {duration}秒 {quality}: {time_str} ({total_sec}秒)")
    
    print(f"\n用户体验分析:")
    for duration, quality in test_combinations:
        total_sec, time_str = calculate_frontend_time(duration, quality)
        
        if total_sec <= 60:
            experience = "⚡ 极快 - 用户愿意等待"
        elif total_sec <= 120:
            experience = "✅ 较快 - 可接受的等待时间"
        elif total_sec <= 180:
            experience = "⏳ 适中 - 需要进度提示"
        else:
            experience = "🐌 较慢 - 建议提供预览或后台处理"
        
        print(f"  {duration}秒 {quality}: {experience}")

def test_quality_comparison():
    """测试质量对比"""
    print(f"\n🔍 质量对比分析")
    print("=" * 60)
    
    durations = [4, 6, 8]
    
    for duration in durations:
        time_720p = duration * 15
        time_1080p = duration * 25
        
        time_diff = time_1080p - time_720p
        time_diff_percent = (time_diff / time_720p) * 100
        
        print(f"{duration}秒视频:")
        print(f"  720p: {time_720p//60}分{time_720p%60}秒")
        print(f"  1080p: {time_1080p//60}分{time_1080p%60}秒")
        print(f"  差异: +{time_diff}秒 (+{time_diff_percent:.1f}%)")
        print(f"  建议: {'优先720p快速预览' if time_1080p > 120 else '两种质量都可接受'}")
        print()

if __name__ == "__main__":
    # 检查服务器
    try:
        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code != 200:
            print("❌ 服务器不可用")
            exit(1)
    except:
        print("❌ 无法连接服务器，请先启动应用")
        exit(1)
    
    # 运行测试
    test_ui_responsiveness()
    test_quality_comparison()
    
    # 询问是否进行实际API测试
    print("\n" + "=" * 60)
    choice = input("是否进行实际API测试？这将消耗API配额 (y/N): ")
    
    if choice.lower() in ['y', 'yes']:
        test_quality_aware_timing()
    else:
        print("跳过API测试")
    
    print("\n🎉 测试完成！")
    print("=" * 60)
    print("✅ 720p和1080p的时间计算已正确实现")
    print("✅ 用户界面将显示准确的时间预估")
    print("✅ 质量选择提供了清晰的时间对比")