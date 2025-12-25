# 数据库迁移指南 - 服务器部署

本文档说明将本地开发数据库迁移到生产服务器的完整步骤。

## 📋 数据库结构变更概览

### 1. Artwork表 - 新增字段（工作流支持）

本次更新为支持**分步创作工作流**（图片 → 3D → 视频），对`Artwork`表进行了扩展：

| 字段名 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `session_id` | String(36) | **工作流会话ID**（UUID格式），唯一标识一个创作流程 | 必填 |
| `all_colored_versions` | JSON | **图片版本历史**，存储所有AI生成的图片文件名数组 | `[]` |
| `all_3d_versions` | JSON | **3D模型版本历史**（暂未使用） | `[]` |
| `all_video_versions` | JSON | **视频版本历史**（暂未使用） | `[]` |

#### session_id 使用场景：
```python
# 用户在图片页面生成图片后，session_id会通过URL传递：
# /create/3d?session=abc-123-def
# /create/video?session=abc-123-def

# 后端通过session_id查询同一创作流程的作品：
artwork = Artwork.query.filter_by(session_id=session_id).first()
```

### 2. User表 - 游客系统字段（已有）

确保服务器数据库包含以下字段（支持7天试用游客）：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `daily_token_amount` | Integer | 每日自动赠送token数量（游客10，学生30） |
| `trial_end_date` | DateTime | 游客试用结束日期 |
| `last_token_grant_date` | Date | 上次赠送token日期 |
| `course_type` | String(50) | 课程类型（trial_course/formal_course） |

### 3. CreationSession表 - 会话管理（已有）

确保此表存在：

```python
class CreationSession(db.Model):
    __tablename__ = 'creation_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False)  # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_step = db.Column(db.String(20))  # image, 3d, video
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

---

## 🔧 迁移步骤

### 方法1: 使用Flask-Migrate（推荐 - 保留数据）

#### 1.1 生产服务器备份当前数据库

```bash
# SSH到生产服务器
ssh user@your-server.com

# 备份SQLite数据库
cd /path/to/HLTraining
cp instance/hltraining.db instance/hltraining.db.backup_$(date +%Y%m%d_%H%M%S)

# 或备份PostgreSQL/MySQL
# pg_dump dbname > backup.sql
# mysqldump -u user -p dbname > backup.sql
```

#### 1.2 上传新代码到服务器

```bash
# 本地推送代码
git add .
git commit -m "添加分步创作工作流支持"
git push origin main

# 服务器拉取代码
cd /path/to/HLTraining
git pull origin main
```

#### 1.3 激活虚拟环境

```bash
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\Activate.ps1  # Windows Server
```

#### 1.4 安装依赖（确保Flask-Migrate已安装）

```bash
pip install Flask-Migrate
```

#### 1.5 初始化迁移（如果是首次使用Flask-Migrate）

```bash
# 仅首次使用时执行
flask db init
```

#### 1.6 生成迁移脚本

```bash
# 自动检测模型变更并生成迁移脚本
flask db migrate -m "添加Artwork表session_id和版本历史字段"
```

**检查生成的迁移文件**：
- 位置：`migrations/versions/xxxx_添加artwork表session_id和版本历史字段.py`
- 确认`upgrade()`函数包含以下操作：

```python
def upgrade():
    # 添加session_id字段（可空，稍后更新）
    with op.batch_alter_table('artworks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('session_id', sa.String(length=36), nullable=True))
    
    # 为现有记录生成UUID
    op.execute("""
        UPDATE artworks
        SET session_id = (
            lower(hex(randomblob(4))) || '-' ||
            lower(hex(randomblob(2))) || '-' ||
            '4' || substr(lower(hex(randomblob(2))), 2) || '-' ||
            lower(hex(randomblob(2))) || '-' ||
            lower(hex(randomblob(6)))
        )
        WHERE session_id IS NULL
    """)
    
    # 设置为NOT NULL和UNIQUE
    with op.batch_alter_table('artworks', schema=None) as batch_op:
        batch_op.alter_column('session_id', nullable=False)
        batch_op.create_unique_constraint('uq_artwork_session_id', ['session_id'])
    
    # 添加版本历史字段
    with op.batch_alter_table('artworks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('all_colored_versions', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('all_3d_versions', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('all_video_versions', sa.JSON(), nullable=True))

def downgrade():
    # 回滚操作
    with op.batch_alter_table('artworks', schema=None) as batch_op:
        batch_op.drop_constraint('uq_artwork_session_id', type_='unique')
        batch_op.drop_column('session_id')
        batch_op.drop_column('all_colored_versions')
        batch_op.drop_column('all_3d_versions')
        batch_op.drop_column('all_video_versions')
```

#### 1.7 应用迁移

```bash
# 执行迁移（更新数据库结构）
flask db upgrade

# 查看当前版本
flask db current
```

#### 1.8 验证迁移结果

```bash
# 进入Python shell验证
flask shell

>>> from auth.models import Artwork, db
>>> artwork = Artwork.query.first()
>>> print(artwork.session_id)  # 应该输出UUID
>>> print(artwork.all_colored_versions)  # 应该输出 [] 或 None
>>> exit()
```

---

### 方法2: 手动SQL迁移（适用于小型数据库）

#### 2.1 备份数据库

```bash
cp instance/hltraining.db instance/hltraining.db.backup
```

#### 2.2 执行SQL脚本

创建 `migrations/add_workflow_fields.sql`：

```sql
-- SQLite版本
BEGIN TRANSACTION;

-- 1. 添加session_id字段（先允许NULL）
ALTER TABLE artworks ADD COLUMN session_id VARCHAR(36);

-- 2. 为现有记录生成UUID
UPDATE artworks
SET session_id = (
    lower(hex(randomblob(4))) || '-' ||
    lower(hex(randomblob(2))) || '-' ||
    '4' || substr(lower(hex(randomblob(2))), 2) || '-' ||
    lower(hex(randomblob(2))) || '-' ||
    lower(hex(randomblob(6)))
)
WHERE session_id IS NULL;

-- 3. 创建唯一索引（SQLite不支持直接修改列约束）
CREATE UNIQUE INDEX idx_artwork_session_id ON artworks(session_id);

-- 4. 添加版本历史字段
ALTER TABLE artworks ADD COLUMN all_colored_versions TEXT;  -- JSON存储为TEXT
ALTER TABLE artworks ADD COLUMN all_3d_versions TEXT;
ALTER TABLE artworks ADD COLUMN all_video_versions TEXT;

COMMIT;
```

**PostgreSQL/MySQL版本**：

```sql
-- PostgreSQL
BEGIN;

ALTER TABLE artworks ADD COLUMN session_id VARCHAR(36);
UPDATE artworks SET session_id = gen_random_uuid()::text WHERE session_id IS NULL;
ALTER TABLE artworks ALTER COLUMN session_id SET NOT NULL;
ALTER TABLE artworks ADD CONSTRAINT uq_artwork_session_id UNIQUE (session_id);

ALTER TABLE artworks ADD COLUMN all_colored_versions JSON;
ALTER TABLE artworks ADD COLUMN all_3d_versions JSON;
ALTER TABLE artworks ADD COLUMN all_video_versions JSON;

COMMIT;
```

#### 2.3 应用SQL脚本

```bash
# SQLite
sqlite3 instance/hltraining.db < migrations/add_workflow_fields.sql

# PostgreSQL
psql -U username -d dbname -f migrations/add_workflow_fields.sql

# MySQL
mysql -u username -p dbname < migrations/add_workflow_fields.sql
```

---

### 方法3: Python脚本迁移（最灵活）

创建 `migrations/upgrade_database.py`：

```python
#!/usr/bin/env python
"""数据库升级脚本 - 添加工作流字段"""
import os
import uuid
from app import create_app
from auth.models import db, Artwork

def upgrade():
    """执行数据库升级"""
    app = create_app()
    
    with app.app_context():
        print("🔧 开始数据库升级...")
        
        # 检查是否已有session_id字段
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('artworks')]
        
        if 'session_id' not in columns:
            print("📝 添加session_id字段...")
            # 使用原生SQL添加字段
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE artworks ADD COLUMN session_id VARCHAR(36);
                """))
                conn.commit()
            
            # 为现有记录生成UUID
            print("🔑 为现有作品生成session_id...")
            artworks = Artwork.query.all()
            for artwork in artworks:
                if not artwork.session_id:
                    artwork.session_id = str(uuid.uuid4())
            db.session.commit()
            print(f"✅ 已更新 {len(artworks)} 条记录")
        else:
            print("⏭️ session_id字段已存在，跳过")
        
        # 添加版本历史字段
        if 'all_colored_versions' not in columns:
            print("📝 添加版本历史字段...")
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE artworks ADD COLUMN all_colored_versions TEXT;
                    ALTER TABLE artworks ADD COLUMN all_3d_versions TEXT;
                    ALTER TABLE artworks ADD COLUMN all_video_versions TEXT;
                """))
                conn.commit()
            print("✅ 版本历史字段添加成功")
        else:
            print("⏭️ 版本历史字段已存在，跳过")
        
        print("🎉 数据库升级完成！")

if __name__ == '__main__':
    upgrade()
```

执行脚本：

```bash
python migrations/upgrade_database.py
```

---

## ✅ 验证清单

迁移完成后，逐项检查：

### 1. 数据库结构验证

```bash
# SQLite
sqlite3 instance/hltraining.db ".schema artworks"

# PostgreSQL
psql -U user -d dbname -c "\d artworks"
```

**预期输出应包含**：
```sql
session_id VARCHAR(36) UNIQUE NOT NULL
all_colored_versions JSON (或TEXT)
all_3d_versions JSON
all_video_versions JSON
```

### 2. 应用功能验证

访问测试页面：

1. **图片生成页面**：http://your-server.com/create/image
   - [ ] 可以输入文字生成图片
   - [ ] 生成后URL包含 `?session=xxx`
   - [ ] 显示"继续制作3D"按钮

2. **3D模型页面**：http://your-server.com/create/3d?session=xxx
   - [ ] 自动加载前一步的图片
   - [ ] 可以生成3D模型
   - [ ] 显示"继续制作视频"按钮

3. **视频生成页面**：http://your-server.com/create/video?session=xxx
   - [ ] 自动加载前面的图片/3D
   - [ ] 可以生成视频

4. **数据库验证**：
```python
flask shell
>>> from auth.models import Artwork
>>> artwork = Artwork.query.first()
>>> print(f"Session ID: {artwork.session_id}")
>>> print(f"Colored versions: {artwork.all_colored_versions}")
```

### 3. 日志检查

查看Flask日志确认无错误：

```bash
tail -f logs/app_$(date +%Y%m%d)*.log | grep -i error
```

---

## 🔄 回滚方案

如果迁移失败，按以下步骤回滚：

### 使用Flask-Migrate回滚

```bash
# 查看迁移历史
flask db history

# 回滚到上一个版本
flask db downgrade

# 或回滚到指定版本
flask db downgrade <revision_id>
```

### 手动回滚

```bash
# 1. 停止应用
systemctl stop hltraining  # 或 supervisorctl stop hltraining

# 2. 恢复备份数据库
cp instance/hltraining.db.backup instance/hltraining.db

# 3. 回滚代码
git checkout HEAD~1

# 4. 重启应用
systemctl start hltraining
```

---

## 📦 生产环境部署检查

### 1. 环境变量

确保 `.env` 包含：

```bash
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@localhost/hltraining  # 或SQLite路径
GEMINI_API_KEY=your-api-key
HUNYUAN3D_API_KEY=your-api-key
```

### 2. 权限设置

```bash
# 确保uploads目录可写
chmod 755 uploads/
chown www-data:www-data uploads/  # Nginx/Apache用户

# 数据库文件权限
chmod 644 instance/hltraining.db
chown www-data:www-data instance/hltraining.db
```

### 3. 服务重启

```bash
# Gunicorn + Systemd
systemctl restart hltraining

# Supervisor
supervisorctl restart hltraining

# 开发服务器（不推荐生产使用）
./run.ps1 restart  # Windows
./run.sh restart   # Linux
```

---

## 📞 常见问题

### Q1: `session_id`冲突错误

**错误信息**：`IntegrityError: UNIQUE constraint failed: artworks.session_id`

**解决方案**：
```python
from app import create_app
from auth.models import db, Artwork
import uuid

app = create_app()
with app.app_context():
    # 查找重复的session_id
    duplicates = db.session.query(Artwork.session_id).group_by(Artwork.session_id).having(db.func.count() > 1).all()
    
    # 为重复的记录重新生成UUID
    for (session_id,) in duplicates:
        artworks = Artwork.query.filter_by(session_id=session_id).all()
        for artwork in artworks[1:]:  # 保留第一个，更新其他
            artwork.session_id = str(uuid.uuid4())
    
    db.session.commit()
```

### Q2: JSON字段为空

SQLite的JSON字段可能存储为`NULL`，需要初始化：

```python
from auth.models import Artwork, db
artworks = Artwork.query.filter(Artwork.all_colored_versions.is_(None)).all()
for artwork in artworks:
    artwork.all_colored_versions = []
db.session.commit()
```

### Q3: 旧版浏览器不支持新页面

确保用户清除浏览器缓存：
- Chrome: `Ctrl + Shift + Delete`
- 或在代码中添加缓存版本号：`<link href="style.css?v=2">`

---

## 📚 相关文档

- [API_MIGRATION_SUCCESS.md](./API_MIGRATION_SUCCESS.md) - API路由重构文档
- [CSS_MODULARIZATION_COMPLETE.md](./CSS_MODULARIZATION_COMPLETE.md) - CSS模块化文档
- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - 原始迁移指南

---

## 📝 修改记录

| 日期 | 修改人 | 说明 |
|------|--------|------|
| 2025-12-25 | GitHub Copilot | 创建文档：添加session_id和版本历史字段支持分步工作流 |

---

## 🆘 紧急联系

如遇到迁移问题无法解决，请：
1. 立即停止服务：`systemctl stop hltraining`
2. 恢复备份：`cp instance/hltraining.db.backup instance/hltraining.db`
3. 联系技术支持

**测试环境优先**：强烈建议先在测试环境完整执行一遍迁移流程，确认无误后再在生产环境操作。
