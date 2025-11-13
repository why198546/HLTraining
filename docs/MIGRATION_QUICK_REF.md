# 数据库迁移快速参考

## 🚀 常用命令

### 修改模型后的标准流程

```bash
# 1. 修改 models.py (添加/删除/修改字段)

# 2. 生成迁移脚本
export FLASK_APP=migrate_db.py
flask db migrate -m "描述你的修改"

# 3. 查看生成的迁移文件
ls -l migrations/versions/

# 4. 本地测试迁移
flask db upgrade

# 5. 测试应用功能
python app.py

# 6. 同步到服务器（自动备份+迁移）
./migrate_to_server.sh
```

## 📝 示例场景

### 场景1: 给User表添加新字段

**models.py**:
```python
class User(UserMixin, db.Model):
    # ...existing fields...
    level = db.Column(db.Integer, default=1)  # 新增：用户等级
    points = db.Column(db.Integer, default=0)  # 新增：积分
```

**执行**:
```bash
export FLASK_APP=migrate_db.py
flask db migrate -m "添加用户等级和积分系统"
flask db upgrade
./migrate_to_server.sh
```

### 场景2: 修改字段类型

**models.py**:
```python
class Artwork(db.Model):
    # 从 String(50) 改为 String(200)
    description = db.Column(db.String(200))
```

**执行**:
```bash
flask db migrate -m "扩展作品描述长度至200字符"
flask db upgrade
./migrate_to_server.sh
```

### 场景3: 添加索引优化查询

**models.py**:
```python
class Artwork(db.Model):
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
```

**执行**:
```bash
flask db migrate -m "为时间和用户ID添加索引"
flask db upgrade
./migrate_to_server.sh
```

## ⚡ 快速命令

```bash
# 查看当前版本
flask db current

# 查看历史
flask db history

# 回滚一个版本
flask db downgrade

# 升级到最新
flask db upgrade

# 仅同步代码（不迁移）
./sync_to_server.sh

# 同步代码+数据库迁移
./migrate_to_server.sh
```

## ⚠️ 重要提醒

1. **迁移前必须备份** - `migrate_to_server.sh`会自动备份
2. **先本地测试** - 确保`flask db upgrade`成功
3. **描述清晰** - 迁移信息要说明具体改了什么
4. **提交到Git** - 迁移文件要版本控制

## 🆘 故障处理

### 迁移失败

```bash
# 查看错误详情
ssh wordpress 'journalctl -u hltraining -n 50'

# 从备份恢复
ssh wordpress 'ls -l /root/db_backup_*.sql.gz'
ssh wordpress 'gunzip < /root/db_backup_xxx.sql.gz | sudo -u postgres psql hltraining_db'
```

### 重置迁移（仅开发环境）

```bash
# ⚠️ 危险操作，仅用于开发！
rm -rf migrations/
rm hltraining.db
flask db init
flask db migrate -m "重新初始化"
flask db upgrade
```

## 📚 更多信息

详见 [DATABASE_MIGRATION.md](DATABASE_MIGRATION.md)
