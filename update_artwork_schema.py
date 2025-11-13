"""
更新Artwork表结构，添加版本历史字段
运行此脚本来更新数据库架构
"""

from app import app, db
from models import Artwork
from sqlalchemy import text

def update_artwork_schema():
    """添加新的字段到artworks表"""
    with app.app_context():
        try:
            # 检查字段是否已存在
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('artworks')]
            
            print(f"📋 现有字段: {existing_columns}")
            
            # 需要添加的字段
            new_columns = {
                'all_colored_versions': 'JSON',
                'all_adjusted_versions': 'JSON',
                'artist_name': 'VARCHAR(50)',
                'artist_age': 'INTEGER',
                'category': 'VARCHAR(50)'
            }
            
            # 添加缺失的字段
            for column_name, column_type in new_columns.items():
                if column_name not in existing_columns:
                    print(f"➕ 添加字段: {column_name} ({column_type})")
                    
                    if column_type == 'JSON':
                        # SQLite使用TEXT存储JSON
                        db.session.execute(text(f'ALTER TABLE artworks ADD COLUMN {column_name} TEXT'))
                    else:
                        db.session.execute(text(f'ALTER TABLE artworks ADD COLUMN {column_name} {column_type}'))
                    
                    db.session.commit()
                    print(f"✅ 字段 {column_name} 添加成功")
                else:
                    print(f"⏭️  字段 {column_name} 已存在，跳过")
            
            print("\n✅ 数据库架构更新完成！")
            
        except Exception as e:
            print(f"❌ 更新失败: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("🔧 开始更新Artwork表结构...")
    update_artwork_schema()
