#!/usr/bin/env python3
"""测试家长控制台功能"""

import sys
import os
sys.path.append('.')

from app import app, db
from models import User
import time

def test_parent_dashboard():
    """测试家长控制台页面"""
    with app.app_context():
        with app.test_client() as client:
            # 获取测试用户
            user = User.query.filter_by(username='test').first()
            if not user:
                print("❌ 测试用户不存在")
                return False
            
            print(f"✅ 找到测试用户: {user.username}")
            print(f"✅ 验证token: {user.verification_token}")
            
            if not user.verification_token:
                print("❌ 用户没有验证token")
                return False
            
            # 测试家长控制台访问
            try:
                url = f'/auth/parent-dashboard/{user.verification_token}'
                print(f"🔍 测试访问: {url}")
                
                response = client.get(url)
                print(f"📄 响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ 家长控制台页面加载成功！")
                    
                    content = response.data.decode('utf-8')
                    
                    # 检查页面内容
                    if '家长监护面板' in content or '孩子的作品' in content:
                        print("✅ 页面内容正确")
                    else:
                        print("❌ 页面内容缺失")
                        print("页面内容预览:", content[:500])
                    
                    # 检查是否有错误信息
                    if 'TypeError' in content or '500 Internal Server Error' in content:
                        print("❌ 页面包含错误信息")
                        print("错误内容:", content[:1000])
                        return False
                    else:
                        print("✅ 页面无错误信息")
                    
                    return True
                    
                elif response.status_code == 302:
                    print(f"📄 页面重定向到: {response.headers.get('Location', '未知')}")
                    return False
                    
                elif response.status_code == 500:
                    print(f"❌ 家长控制台服务器错误")
                    error_content = response.data.decode('utf-8')[:500]
                    print(f"错误内容: {error_content}")
                    return False
                    
                else:
                    print(f"❌ 家长控制台访问失败，状态码: {response.status_code}")
                    content = response.data.decode('utf-8')[:500]
                    print(f"响应内容: {content}")
                    return False
                    
            except Exception as e:
                print(f"❌ 测试过程中发生错误: {e}")
                import traceback
                traceback.print_exc()
                return False

if __name__ == "__main__":
    print("🚀 开始测试家长控制台...")
    success = test_parent_dashboard()
    if success:
        print("\n🎉 家长控制台测试通过！")
    else:
        print("\n❌ 家长控制台测试失败！")