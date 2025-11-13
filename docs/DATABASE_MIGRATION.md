# 数据库迁移管理指南

> 使用Flask-Migrate管理数据库结构变更

## 📋 目录

1. [快速开始](#快速开始)
2. [日常工作流程](#日常工作流程)
3. [迁移命令详解](#迁移命令详解)
4. [本地到服务器同步](#本地到服务器同步)
5. [常见问题](#常见问题)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 本地安装
pip install flask-migrate

# 或者更新requirements.txt后
pip install -r requirements.txt
```

### 2. 初始化迁移仓库（仅首次使用）

```bash
# 设置Flask应用
export FLASK_APP=migrate_db.py

# 初始化迁移目录
flask db init

# 这会创建 migrations/ 目录
```

### 3. 创建初始迁移

```bash
# 生成迁移脚本
flask db migrate -m "初始数据库结构"

# 应用到数据库
flask db upgrade
```

---

## 💻 日常工作流程

### 场景：修改数据库模型

假设你要给 `User` 模型添加一个新字段 `bio`（个人简介）

#### 步骤1: 修改模型

编辑 `models.py`:

```python
class User(UserMixin, db.Model):
    # ...现有字段...
    
    # 新添加的字段
    bio = db.Column(db.Text, nullable=True)  # 个人简介
```

#### 步骤2: 本地生成迁移

```bash
# 1. 设置环境变量
export FLASK_APP=migrate_db.py

# 2. 生成迁移脚本（自动检测变更）
flask db migrate -m "添加用户个人简介字段"

# 输出示例：
# INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
# INFO  [alembic.autogenerate.compare] Detected added column 'users.bio'
# Generating /path/migrations/versions/xxx_添加用户个人简介字段.py ...  done
```

#### 步骤3: 检查生成的迁移脚本

```bash
# 查看迁移文件
ls -l migrations/versions/

# 编辑并验证迁移脚本（如需要）
# migrations/versions/xxx_添加用户个人简介字段.py
```

#### 步骤4: 应用到本地数据库

```bash
# 应用迁移
flask db upgrade

# 输出示例：
# INFO  [alembic.runtime.migration] Running upgrade xxx -> yyy, 添加用户个人简介字段
```

#### 步骤5: 本地测试

```bash
# 启动应用测试
python app.py

# 测试新功能是否正常
```

#### 步骤6: 同步到服务器

```bash
# 1. 同步代码（包括迁移脚本）
./sync_to_server.sh

# 2. SSH到服务器
ssh wordpress

# 3. 在服务器上执行迁移
cd /var/www/hltraining
source venv/bin/activate

# 4. 备份数据库（重要！）
sudo -u postgres pg_dump hltraining_db > /root/db_backup_before_migration_$(date +%Y%m%d_%H%M%S).sql

# 5. 设置环境变量
export FLASK_APP=migrate_db.py

# 6. 查看当前版本
flask db current

# 7. 应用迁移
flask db upgrade

# 8. 验证迁移
flask db current

# 9. 重启服务
sudo systemctl restart hltraining
```

---

## 📚 迁移命令详解

### 初始化命令

```bash
# 初始化迁移仓库（仅首次）
flask db init
```

### 生成迁移

```bash
# 自动检测模型变更并生成迁移
flask db migrate -m "描述变更内容"

# 示例：
flask db migrate -m "添加用户等级字段"
flask db migrate -m "修改作品表索引"
flask db migrate -m "删除废弃的临时表"
```

### 应用迁移

```bash
# 升级到最新版本
flask db upgrade

# 升级到指定版本
flask db upgrade <revision>

# 升级一个版本
flask db upgrade +1
```

### 回滚迁移

```bash
# 回滚到上一个版本
flask db downgrade

# 回滚到指定版本
flask db downgrade <revision>

# 回滚一个版本
flask db downgrade -1
```

### 查看状态

```bash
# 查看当前数据库版本
flask db current

# 查看迁移历史
flask db history

# 查看所有版本
flask db show <revision>
```

---

## 🔄 本地到服务器同步流程

### 完整迁移流程图

```
本地开发
  ↓
修改 models.py
  ↓
flask db migrate -m "描述"
  ↓
flask db upgrade (本地测试)
  ↓
测试功能
  ↓
./sync_to_server.sh (同步代码+迁移脚本)
  ↓
SSH到服务器
  ↓
备份数据库 ⭐
  ↓
flask db upgrade (服务器)
  ↓
重启服务
  ↓
验证功能
```

### 自动化脚本（推荐）

创建 `migrate_to_server.sh`:

```bash
#!/bin/bash
# 数据库迁移到服务器的自动化脚本

echo "🔄 开始数据库迁移流程..."

# 1. 同步代码
./sync_to_server.sh

# 2. 在服务器上执行迁移
ssh wordpress << 'ENDSSH'
    set -e
    cd /var/www/hltraining
    
    # 备份数据库
    echo "💾 备份数据库..."
    BACKUP_FILE="/root/db_backup_$(date +%Y%m%d_%H%M%S).sql"
    sudo -u postgres pg_dump hltraining_db > $BACKUP_FILE
    echo "✅ 数据库已备份: $BACKUP_FILE"
    
    # 应用迁移
    echo "🔄 应用数据库迁移..."
    source venv/bin/activate
    export FLASK_APP=migrate_db.py
    
    flask db current
    flask db upgrade
    flask db current
    
    # 重启服务
    echo "🔄 重启服务..."
    sudo systemctl restart hltraining
    
    echo "✅ 迁移完成！"
ENDSSH

echo "🎉 服务器数据库迁移完成！"
```

---

## 🛠️ 常见场景

### 1. 添加新字段

**模型变更**:
```python
class User(UserMixin, db.Model):
    # 新增字段
    preferences = db.Column(db.JSON, default={})
```

**迁移**:
```bash
flask db migrate -m "添加用户偏好设置"
flask db upgrade
```

### 2. 修改字段类型

**模型变更**:
```python
class Artwork(db.Model):
    # 从 String(50) 改为 String(100)
    title = db.Column(db.String(100), nullable=False)
```

**迁移**:
```bash
flask db migrate -m "扩展作品标题长度"
flask db upgrade
```

### 3. 添加索引

**模型变更**:
```python
class Artwork(db.Model):
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
```

**迁移**:
```bash
flask db migrate -m "为创建时间添加索引"
flask db upgrade
```

### 4. 添加新表

**创建新模型**:
```python
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'))
```

**迁移**:
```bash
flask db migrate -m "添加评论表"
flask db upgrade
```

### 5. 删除字段

**模型变更**:
```python
class User(UserMixin, db.Model):
    # 删除或注释掉不需要的字段
    # old_field = db.Column(db.String(50))
```

**迁移**:
```bash
flask db migrate -m "删除废弃字段"
flask db upgrade
```

---

## ⚠️ 注意事项

### ✅ 最佳实践

1. **迁移前必须备份**
   ```bash
   # 服务器上
   sudo -u postgres pg_dump hltraining_db > backup.sql
   ```

2. **先在本地测试**
   ```bash
   # 本地完整测试迁移流程
   flask db migrate -m "xxx"
   flask db upgrade
   # 测试应用功能
   ```

3. **迁移描述清晰**
   ```bash
   # ❌ 不好的描述
   flask db migrate -m "update"
   
   # ✅ 好的描述
   flask db migrate -m "添加用户等级和积分字段"
   ```

4. **版本控制迁移脚本**
   ```bash
   git add migrations/versions/
   git commit -m "数据库迁移: 添加用户等级字段"
   ```

5. **避免直接修改数据库**
   ```bash
   # ❌ 不要这样做
   ALTER TABLE users ADD COLUMN bio TEXT;
   
   # ✅ 使用迁移
   flask db migrate && flask db upgrade
   ```

### ❌ 常见错误

1. **忘记备份**
   - 后果：数据丢失无法恢复
   - 解决：总是先备份

2. **本地和服务器环境不一致**
   - 后果：迁移脚本在服务器上失败
   - 解决：确保两边都安装了相同的依赖

3. **手动修改迁移脚本导致错误**
   - 后果：迁移无法执行
   - 解决：仔细检查迁移脚本语法

4. **在生产环境直接测试迁移**
   - 后果：可能导致数据损坏
   - 解决：先在本地测试

---

## 🔍 故障排查

### 迁移失败

```bash
# 查看当前状态
flask db current

# 查看迁移历史
flask db history

# 手动标记版本（谨慎使用）
flask db stamp <revision>
```

### 回滚迁移

```bash
# 回滚到上一版本
flask db downgrade

# 从备份恢复数据库
sudo -u postgres psql hltraining_db < backup.sql
```

### 清除迁移重新开始

```bash
# ⚠️ 仅用于开发环境！
rm -rf migrations/
flask db init
flask db migrate -m "初始迁移"
flask db upgrade
```

---

## 📊 迁移文件结构

```
HLTraining/
├── migrations/              # 迁移目录（会被同步）
│   ├── alembic.ini         # Alembic配置
│   ├── env.py              # 迁移环境配置
│   ├── README              # 说明文件
│   ├── script.py.mako      # 迁移脚本模板
│   └── versions/           # 迁移版本
│       ├── abc123_初始迁移.py
│       ├── def456_添加用户字段.py
│       └── ghi789_修改作品表.py
├── models.py               # 数据库模型
├── migrate_db.py           # 迁移管理脚本
└── app.py                  # 主应用
```

---

## 🎯 快速命令参考

```bash
# 本地开发
export FLASK_APP=migrate_db.py
flask db migrate -m "描述"
flask db upgrade

# 同步到服务器
./sync_to_server.sh

# 服务器执行
ssh wordpress
cd /var/www/hltraining
source venv/bin/activate
export FLASK_APP=migrate_db.py
sudo -u postgres pg_dump hltraining_db > backup.sql  # 备份
flask db upgrade                                      # 迁移
sudo systemctl restart hltraining                     # 重启
```

---

## 📚 相关资源

- [Flask-Migrate 文档](https://flask-migrate.readthedocs.io/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 文档](https://www.sqlalchemy.org/)

---

**💡 记住：迁移前必须备份，先本地测试，再生产应用！**
