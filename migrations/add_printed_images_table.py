"""
添加打印图片记录表的迁移脚本
记录用户打印过的图片，用于打包下载时区分
"""

from datetime import datetime

# 创建打印图片记录表
def upgrade(db):
    """升级数据库 - 添加打印图片记录表"""
    from sqlalchemy import text
    
    with db.engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS printed_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lesson_key VARCHAR(100) NOT NULL,
                image_url VARCHAR(500) NOT NULL,
                printed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_printed_images_user_lesson 
            ON printed_images(user_id, lesson_key)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_printed_images_date 
            ON printed_images(printed_at)
        """))
        
        conn.commit()
    
    print("✅ 打印图片记录表创建成功")

def downgrade(db):
    """降级数据库 - 删除打印图片记录表"""
    from sqlalchemy import text
    
    with db.engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS printed_images"))
        conn.commit()
    
    print("✅ 打印图片记录表已删除")

if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from app import create_app
    from auth.models import db
    
    app = create_app()
    with app.app_context():
        upgrade(db)
