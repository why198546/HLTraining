#!/usr/bin/env python3
"""
简单测试：验证用户资料更新功能
"""

from app import app
from models import User, db
from flask_login import login_user

def test_profile_update_directly():
    """直接测试个人资料更新功能"""
    
    with app.app_context():
        with app.test_request_context():
            # 找到测试用户
            user = User.query.filter_by(username='why').first()
            if not user:
                print("❌ 测试用户不存在")
                return False
                
            print(f"📝 当前用户昵称: {user.nickname}")
            print(f"📝 当前用户年龄: {user.age}")
            
            # 更新用户信息
            old_nickname = user.nickname
            new_nickname = "更新后的昵称"
            
            user.nickname = new_nickname
            user.age = 13
            
            try:
                db.session.commit()
                db.session.refresh(user)
                print(f"✅ 数据库更新成功")
                print(f"✅ 昵称从 '{old_nickname}' 更新为 '{user.nickname}'")
                return True
            except Exception as e:
                print(f"❌ 数据库更新失败: {e}")
                db.session.rollback()
                return False

if __name__ == "__main__":
    print("🧪 开始直接测试用户资料更新...")
    success = test_profile_update_directly()
    
    if success:
        print("\n🎉 数据库层面的更新功能正常！")
        print("如果页面显示仍然不变，可能是前端或会话缓存问题")
    else:
        print("\n❌ 数据库层面的更新失败！")