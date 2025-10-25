#!/usr/bin/env python3
"""测试my_artworks页面是否修复了QueryPagination错误"""

import sys
import os
sys.path.append('.')

from app import app, db
from models import User
import time

def test_my_artworks_page():
    """直接测试my_artworks页面"""
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
            
            try:
                response = client.get('/auth/my-artworks')
                print(f"My Artworks页面状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ My Artworks页面加载成功！")
                    
                    content = response.data.decode('utf-8')
                    
                    # 检查页面内容
                    if '我的作品' in content:
                        print("✅ 页面标题正确")
                    else:
                        print("❌ 页面标题缺失")
                    
                    # 检查是否有错误信息
                    if 'TypeError' in content or 'QueryPagination' in content:
                        print("❌ 页面包含QueryPagination错误")
                        return False
                    else:
                        print("✅ 页面无QueryPagination错误")
                    
                    return True
                    
                elif response.status_code == 500:
                    print(f"❌ My Artworks页面服务器错误")
                    error_content = response.data.decode('utf-8')[:500]
                    print(f"错误内容: {error_content}")
                    return False
                else:
                    print(f"❌ My Artworks页面访问失败，状态码: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ 测试过程中发生错误: {e}")
                import traceback
                traceback.print_exc()
                return False

if __name__ == "__main__":
    print("开始测试my_artworks页面...")
    success = test_my_artworks_page()
    if success:
        print("\n🎉 My Artworks页面测试通过！")
    else:
        print("\n❌ My Artworks页面测试失败！")