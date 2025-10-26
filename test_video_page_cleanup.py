#!/usr/bin/env python3
"""
测试删除裁剪功能后的视频页面
"""

import requests
import sys
import os

def test_video_page():
    """测试视频页面是否正常加载"""
    print("🧪 测试删除裁剪功能后的视频页面")
    print("=" * 50)
    
    try:
        # 测试视频页面路由
        response = requests.get('http://localhost:5000/video', timeout=5)
        
        if response.status_code == 200:
            print("✅ 视频页面路由正常")
            
            # 检查页面内容是否包含必要元素
            content = response.text
            
            # 应该包含的元素
            should_have = [
                'AI视频生成',
                'source-image',
                'video-prompt',
                'aspect-ratio',
                'generate-video-btn'
            ]
            
            # 不应该包含的元素（已删除的裁剪功能）
            should_not_have = [
                'crop-selector',
                'crop-box',
                'crop-handle',
                'auto-fit-btn',
                'crop-controls'
            ]
            
            print("\n🔍 检查页面元素:")
            
            # 检查必需元素
            missing_elements = []
            for element in should_have:
                if element in content:
                    print(f"✅ 包含: {element}")
                else:
                    print(f"❌ 缺失: {element}")
                    missing_elements.append(element)
            
            # 检查已删除元素
            unwanted_elements = []
            for element in should_not_have:
                if element not in content:
                    print(f"✅ 已删除: {element}")
                else:
                    print(f"⚠️ 仍存在: {element}")
                    unwanted_elements.append(element)
            
            if not missing_elements and not unwanted_elements:
                print(f"\n🎉 页面完全正确!")
                print("✅ 包含所有必需元素")
                print("✅ 已删除所有裁剪功能")
                return True
            else:
                print(f"\n⚠️ 页面存在问题:")
                if missing_elements:
                    print(f"   缺失元素: {missing_elements}")
                if unwanted_elements:
                    print(f"   多余元素: {unwanted_elements}")
                return False
                
        else:
            print(f"❌ 视频页面请求失败: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask服务器")
        print("💡 请确保Flask应用正在运行: python app.py")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_video_page()
    
    if success:
        print("\n🏁 测试结果: 成功")
        print("视频页面已正确删除裁剪功能，保留了核心视频生成功能")
    else:
        print("\n🏁 测试结果: 失败")
        sys.exit(1)