# 数据分离与同步策略

> 本地开发环境 vs 生产服务器环境的数据隔离方案

## 📊 数据分类

### 1. **代码和配置** (需要同步)
- ✅ Python代码 (`*.py`)
- ✅ 模板文件 (`templates/`)
- ✅ 静态资源 (`static/css/`, `static/js/`)
- ✅ 依赖配置 (`requirements.txt`)
- ✅ Nginx配置 (`nginx/`)
- ❌ 环境变量 (`.env` - 本地和服务器分离)

### 2. **数据库** (完全分离)

#### 本地开发环境
```
数据库: SQLite (hltraining.db)
位置: 项目根目录
用途: 开发测试
数据: 测试用户和作品
```

#### 生产服务器环境
```
数据库: PostgreSQL
位置: localhost:5432
用途: 真实用户数据
数据: 正式注册用户和作品
```

**分离原则**: 
- ❌ **永不同步数据库文件**
- ❌ **永不在生产环境执行DROP TABLE**
- ✅ 仅同步数据库迁移脚本

### 3. **用户生成内容** (完全分离)

#### 本地测试数据
```
uploads/              # 本地上传的测试图片
creation_sessions/    # 本地创作会话
models/              # 本地生成的3D模型
static/gallery/      # 本地作品画廊
static/uploads/      # 本地静态上传
instance/            # SQLite数据库文件
```

#### 服务器真实数据
```
/var/www/hltraining/uploads/           # 用户上传
/var/www/hltraining/creation_sessions/ # 用户会话
/var/www/hltraining/models/            # 3D模型
/var/www/hltraining/static/gallery/    # 作品画廊
/var/www/hltraining/static/uploads/    # 静态上传
/var/www/hltraining/instance/          # 数据库相关
```

**分离原则**:
- ❌ **永不同步用户数据目录**
- ✅ 仅保留目录结构 (`.gitkeep`)
- ✅ 服务器数据独立备份

### 4. **日志文件** (完全分离)
```
本地: flask_app.log (开发调试)
服务器: /var/www/hltraining/logs/ (生产日志)
```

---

## 🔄 同步策略

### sync_to_server.sh 排除规则

```bash
# 当前已排除的内容
--exclude='.git/'              # Git仓库
--exclude='.venv/'             # 本地虚拟环境
--exclude='venv/'              # 服务器虚拟环境
--exclude='__pycache__/'       # Python缓存
--exclude='*.pyc'              # 编译文件
--exclude='*.pyo'              # 优化编译文件
--exclude='*.db'               # ✅ SQLite数据库
--exclude='*.sqlite'           # ✅ SQLite数据库
--exclude='*.log'              # ✅ 日志文件
--exclude='.DS_Store'          # macOS文件
--exclude='uploads/*'          # ✅ 用户上传
--exclude='creation_sessions/*' # ✅ 创作会话
--exclude='models/*'           # ✅ 3D模型
--exclude='instance/'          # ✅ 实例数据
--exclude='logs/'              # ✅ 日志目录
--exclude='.env'               # ✅ 环境变量
--exclude='node_modules/'      # Node依赖
```

### 同步内容（会被同步）

```
✅ *.py - Python代码
✅ templates/ - HTML模板
✅ static/css/ - 样式文件
✅ static/js/ - JavaScript
✅ static/images/sample/ - 示例图片（代码自带）
✅ api/ - API接口
✅ auth/ - 认证模块
✅ utils/ - 工具函数
✅ requirements.txt - 依赖列表
✅ gunicorn_config.py - 服务器配置
✅ *.sh - Shell脚本
✅ *.md - 文档
✅ .gitignore - Git配置
✅ .env.example - 环境变量模板
```

---

## 🗃️ 数据库迁移策略

### 本地开发流程

```bash
# 1. 修改models.py
# 例如：添加新字段到User模型

# 2. 本地测试迁移（如果使用Flask-Migrate）
flask db migrate -m "添加用户偏好设置字段"
flask db upgrade

# 3. 测试确认无误
python app.py
# 测试新功能
```

### 同步到服务器

```bash
# 1. 同步代码（包含迁移脚本）
./sync_to_server.sh

# 2. SSH到服务器执行迁移
ssh wordpress
cd /var/www/hltraining
source venv/bin/activate

# 3. 备份数据库（重要！）
pg_dump -U hltraining_user hltraining_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 4. 执行迁移
flask db upgrade

# 5. 重启服务
sudo systemctl restart hltraining
```

---

## 🔐 环境变量分离

### 本地 `.env` (开发环境)

```env
# 开发环境配置
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///hltraining.db  # ⭐ SQLite
PORT=8088
SECRET_KEY=开发环境密钥

# API密钥（测试用）
GEMINI_API_KEY=测试密钥
```

### 服务器 `.env` (生产环境)

```env
# 生产环境配置
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost:5432/hltraining_db  # ⭐ PostgreSQL
PORT=8088
SECRET_KEY=生产环境强密钥（不同于本地！）

# API密钥（正式密钥）
GEMINI_API_KEY=正式密钥
MAIL_PASSWORD=正式邮箱密码
```

**重要**:
- ❌ `.env` 文件永不同步
- ✅ 使用 `.env.example` 作为模板
- ✅ 服务器上手动配置 `.env`

---

## 📦 备份策略

### 本地数据备份（可选）

```bash
# 备份本地测试数据库
cp hltraining.db backups/hltraining_$(date +%Y%m%d).db

# 清理测试数据
rm -rf uploads/* creation_sessions/* models/*
```

### 服务器数据备份（重要！）

```bash
# 在服务器上执行

# 1. 数据库备份
pg_dump -U hltraining_user hltraining_db > /root/backups/db_$(date +%Y%m%d_%H%M%S).sql

# 2. 用户文件备份
tar -czf /root/backups/user_data_$(date +%Y%m%d).tar.gz \
    /var/www/hltraining/uploads \
    /var/www/hltraining/creation_sessions \
    /var/www/hltraining/models \
    /var/www/hltraining/static/gallery

# 3. 自动备份脚本（定时任务）
# 编辑 crontab
crontab -e

# 添加每天凌晨3点备份
0 3 * * * /root/scripts/backup_hltraining.sh
```

---

## 🚨 重要注意事项

### ❌ 永远不要做的事

1. **不要同步 .env 文件**
   ```bash
   # 错误示例
   scp .env wordpress:/var/www/hltraining/  # ❌ 危险！
   ```

2. **不要覆盖生产数据库**
   ```bash
   # 错误示例
   scp hltraining.db wordpress:/var/www/hltraining/  # ❌ 灾难！
   ```

3. **不要删除服务器用户数据**
   ```bash
   # 错误示例
   ssh wordpress 'rm -rf /var/www/hltraining/uploads/*'  # ❌ 数据丢失！
   ```

4. **不要在生产环境开启DEBUG模式**
   ```python
   # 服务器 .env
   FLASK_DEBUG=False  # ✅ 正确
   FLASK_DEBUG=True   # ❌ 安全风险！
   ```

### ✅ 推荐做法

1. **代码同步前先测试**
   ```bash
   # 本地测试通过后再同步
   python app.py
   # 访问 http://localhost:8088 测试功能
   # 确认无误后
   ./sync_to_server.sh
   ```

2. **数据库变更前先备份**
   ```bash
   # 服务器上
   pg_dump -U hltraining_user hltraining_db > backup.sql
   ```

3. **使用版本控制**
   ```bash
   # 提交代码到Git
   git add .
   git commit -m "修复xxx功能"
   git push origin beta
   
   # 然后同步到服务器
   ./sync_to_server.sh
   ```

4. **分阶段部署**
   ```bash
   # 先同步代码，不重启服务
   rsync -avz ... wordpress:/var/www/hltraining/
   
   # 验证文件
   ssh wordpress 'ls -l /var/www/hltraining/app.py'
   
   # 确认无误后重启
   ssh wordpress 'sudo systemctl restart hltraining'
   ```

---

## 🔍 数据查看与调试

### 本地数据检查

```bash
# 查看SQLite数据库
sqlite3 hltraining.db
> .tables
> SELECT * FROM users;
> .quit

# 查看测试数据
ls -lh uploads/
ls -lh creation_sessions/
```

### 服务器数据检查

```bash
# 连接PostgreSQL
ssh wordpress
sudo -u postgres psql hltraining_db

# 查询用户
SELECT id, username, nickname, is_verified FROM users;

# 查询作品数量
SELECT COUNT(*) FROM artworks;

# 退出
\q

# 查看用户数据
ls -lh /var/www/hltraining/uploads/
du -sh /var/www/hltraining/creation_sessions/
```

---

## 📊 数据目录结构对比

```
本地开发环境 (/Users/hongyuwang/code/HLTraining)
├── hltraining.db          # SQLite（测试数据）
├── uploads/               # 测试上传
├── creation_sessions/     # 测试会话
├── models/                # 测试3D模型
├── instance/              # SQLite相关
├── .venv/                 # 本地虚拟环境
└── .env                   # 开发配置

生产服务器 (/var/www/hltraining)
├── (无SQLite)             # 使用PostgreSQL
├── uploads/               # 真实用户上传
├── creation_sessions/     # 真实用户会话
├── models/                # 真实3D模型
├── instance/              # 生产实例数据
├── venv/                  # 服务器虚拟环境
├── logs/                  # 生产日志
└── .env                   # 生产配置（与本地不同！）
```

---

## 🎯 快速参考

```bash
# 同步代码到服务器（安全，不会覆盖数据）
./sync_to_server.sh

# 查看服务器日志
ssh wordpress 'tail -f /var/www/hltraining/logs/hltraining.log'

# 重启服务器服务
ssh wordpress 'sudo systemctl restart hltraining'

# 备份服务器数据库
ssh wordpress 'pg_dump -U hltraining_user hltraining_db > ~/backup.sql'

# 查看服务器用户数据大小
ssh wordpress 'du -sh /var/www/hltraining/{uploads,creation_sessions,models}'
```

---

## 📚 相关文档

- [开发同步指南](DEVELOPMENT_SYNC.md) - 详细同步流程
- [部署指南](DEPLOYMENT.md) - 服务器部署
- [.gitignore](.gitignore) - 排除规则

---

**💡 核心原则**: 代码同步，数据隔离！
