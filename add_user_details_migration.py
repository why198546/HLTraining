#!/usr/bin/env python3
"""
添加用户详细信息字段的数据库迁移脚本
添加性别、联系电话、邮寄地址、出生日期字段，并迁移现有年龄数据
"""

from app import app
from models import db, User
from datetime import date, datetime

def add_user_detail_fields():
    """为用户表添加详细信息字段"""
    try:
        with app.app_context():
            # 检查新字段是否已存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            # 添加新字段
            with db.engine.connect() as conn:
                if 'birth_date' not in columns:
                    print("添加birth_date字段...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN birth_date DATE"))
                    
                if 'gender' not in columns:
                    print("添加gender字段...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN gender VARCHAR(10)"))
                    
                if 'contact_phone' not in columns:
                    print("添加contact_phone字段...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN contact_phone VARCHAR(20)"))
                    
                if 'mailing_address' not in columns:
                    print("添加mailing_address字段...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN mailing_address TEXT"))
                
                conn.commit()
                print("✅ 新字段添加成功")
            
            # 为现有用户迁移数据
            users_to_migrate = User.query.filter(
                (User.birth_date == None) | (User.gender == None) | (User.gender == '')
            ).all()
            
            if users_to_migrate:
                print(f"为 {len(users_to_migrate)} 个用户迁移数据...")
                
                for user in users_to_migrate:
                    # 根据现有年龄计算大概的出生年份
                    if hasattr(user, 'age') and user.age:
                        current_year = datetime.now().year
                        birth_year = current_year - user.age
                        # 设置为当年1月1日（大概日期）
                        user.birth_date = date(birth_year, 1, 1)
                    else:
                        # 如果没有年龄信息，设置默认为10岁
                        current_year = datetime.now().year
                        user.birth_date = date(current_year - 10, 1, 1)
                    
                    # 设置默认性别
                    if not user.gender:
                        user.gender = 'other'  # 默认设置为其他，让用户自己选择
                
                db.session.commit()
                print("✅ 数据迁移完成")
            else:
                print("ℹ️  所有用户数据都已是最新")
            
            # 检查是否可以删除age字段（谨慎操作）
            if 'age' in columns:
                print("⚠️  检测到旧的age字段，建议在确认一切正常后手动删除")
                print("    可以运行：ALTER TABLE users DROP COLUMN age;")
                
            print("🎉 数据库迁移完成!")
            
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        db.session.rollback()

if __name__ == '__main__':
    add_user_detail_fields()