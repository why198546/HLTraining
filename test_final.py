#!/usr/bin/env python3
"""最终测试：验证profile和my_artworks页面都正常工作"""

import sys
import os
sys.path.append('.')

from app import app, db
from models import User
import time

def test_both_pages():
    """测试profile和my_artworks页面"""
    with app.app_context():
        with app.test_client() as client:
            # 获取测试用户
            user = User.query.filter_by(username='test').first()
            if not user:
                print("❌ 测试用户不存在")
                return False
            
            # 模拟登录
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            print("✅ 模拟用户登录成功")
            
            # 测试Profile页面
            print("\n🔍 测试Profile页面...")
            try:
                response = client.get('/auth/profile')
                if response.status_code == 200:
                    print("✅ Profile页面加载成功")
                    if '个人资料' in response.data.decode('utf-8'):
                        print("✅ Profile页面内容正确")
                    else:
                        print("❌ Profile页面内容异常")
                else:
                    print(f"❌ Profile页面错误，状态码: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Profile页面测试失败: {e}")
                return False
            
            # 测试My Artworks页面
            print("\n🔍 测试My Artworks页面...")
            try:
                response = client.get('/auth/my-artworks')
                if response.status_code == 200:
                    print("✅ My Artworks页面加载成功")
                    content = response.data.decode('utf-8')
                    
                    if '我的作品' in content:
                        print("✅ My Artworks页面标题正确")
                    else:
                        print("❌ My Artworks页面标题缺失")
                        
                    if 'TypeError' not in content and 'QueryPagination' not in content:
                        print("✅ My Artworks页面无QueryPagination错误")
                    else:
                        print("❌ My Artworks页面包含错误")
                        return False
                        
                else:
                    print(f"❌ My Artworks页面错误，状态码: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ My Artworks页面测试失败: {e}")
                return False
            
            return True

if __name__ == "__main__":
    print("🚀 开始最终测试...")
    success = test_both_pages()
    if success:
        print("\n🎉 所有页面测试通过！认证系统工作正常！")
    else:
        print("\n❌ 还有页面存在问题！")