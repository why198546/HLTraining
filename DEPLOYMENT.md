# HLTraining 部署指南

> 儿童AI创作平台 - 生产环境部署文档

## 📋 目录

1. [服务器要求](#服务器要求)
2. [数据库选择](#数据库选择)
3. [部署步骤](#部署步骤)
4. [配置说明](#配置说明)
5. [维护操作](#维护操作)
6. [故障排查](#故障排查)

---

## 🖥️ 服务器要求

### 最低配置
- **操作系统**: Rocky Linux 9 / CentOS / RHEL / Ubuntu 20.04+
- **CPU**: 2核心
- **内存**: 2GB（推荐4GB）
- **磁盘**: 20GB可用空间
- **Python**: 3.9+
- **Web服务器**: Nginx 1.18+
- **数据库**: PostgreSQL 14+ / MariaDB 10.5+

### 当前服务器环境 ✅
- **系统**: Rocky Linux 9.6 (Blue Onyx)
- **CPU**: x86_64
- **内存**: 3.5GB
- **磁盘**: 40GB (25GB可用)
- **Python**: 3.9.21
- **Nginx**: 1.20.1
- **PostgreSQL**: 14.19 ⭐ **推荐**
- **MariaDB**: 10.5.29

---

## 🗄️ 数据库选择

### PostgreSQL 14 （✅ 强烈推荐）

**优势：**
- ✅ **JSONB性能卓越** - 完美支持版本历史功能
- ✅ **并发性能优秀** - MVCC多版本并发控制
- ✅ **数据完整性最佳** - 严格ACID事务
- ✅ **扩展性强** - 支持丰富扩展
- ✅ **已安装并运行** - 直接使用，无需额外配置

**适合场景：**
- ✅ 需要存储复杂JSON数据（艺术品版本历史）
- ✅ 高并发用户访问
- ✅ 需要高级查询功能

### MariaDB 10.5 （备选方案）

**优势：**
- ✅ **轻量级** - 内存占用小
- ✅ **与WordPress共用** - 便于统一管理
- ✅ **MySQL兼容** - 生态成熟

**适合场景：**
- ✅ 资源受限环境
- ✅ 简单数据结构
- ✅ 希望统一数据库管理

### 推荐配置

```bash
# PostgreSQL (推荐)
DATABASE_URL=postgresql://hltraining_user:your_password@localhost:5432/hltraining_db

# MariaDB (备选)
DATABASE_URL=mysql+pymysql://hltraining_user:your_password@localhost:3306/hltraining_db
```

---

## 🚀 部署步骤

### 方式一：自动化部署（推荐）

```bash
# 1. 上传代码到服务器
cd ~
git clone https://github.com/why198546/HLTraining.git
# 或使用rsync上传
rsync -avz --exclude='.git' --exclude='__pycache__' \
    /path/to/local/HLTraining/ \
    wordpress:/tmp/hltraining/

# 2. 连接到服务器
ssh wordpress

# 3. 运行自动化部署脚本
cd /tmp/hltraining
sudo bash deploy.sh

# 4. 按提示选择数据库类型
# 选项1: PostgreSQL (推荐)
# 选项2: MariaDB/MySQL
# 选项3: SQLite (仅开发)

# 5. 初始化PostgreSQL数据库
sudo bash /var/www/hltraining/setup_postgresql.sh

# 6. 配置环境变量
sudo vi /var/www/hltraining/.env
# 填入实际的API密钥和数据库连接信息

# 7. 配置Nginx
sudo cp /var/www/hltraining/nginx/ai.hlylsj.com.conf \
    /etc/nginx/conf.d/
sudo nginx -t  # 测试配置
sudo systemctl reload nginx

# 8. 启动服务
sudo systemctl start hltraining
sudo systemctl status hltraining

# 9. 访问应用
# https://ai.hlylsj.com
```

### 方式二：手动部署

#### 步骤1：安装系统依赖

```bash
# Rocky Linux / CentOS / RHEL
sudo dnf install -y python3-devel gcc postgresql-devel

# Ubuntu / Debian
sudo apt install -y python3-dev gcc libpq-dev
```

#### 步骤2：创建应用目录

```bash
sudo mkdir -p /var/www/hltraining
sudo mkdir -p /var/www/hltraining/{uploads,creation_sessions,static/uploads,instance,logs}
sudo chmod 755 /var/www/hltraining
sudo chmod 777 /var/www/hltraining/{uploads,creation_sessions,static/uploads,instance,logs}
```

#### 步骤3：上传代码

```bash
# 从本地上传
rsync -avz --exclude='.git' --exclude='__pycache__' \
    --exclude='.env' --exclude='*.pyc' \
    /path/to/HLTraining/ \
    wordpress:/var/www/hltraining/
```

#### 步骤4：创建虚拟环境

```bash
cd /var/www/hltraining
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 步骤5：配置PostgreSQL数据库

```bash
# 运行数据库初始化脚本
sudo bash setup_postgresql.sh

# 或手动创建
sudo -u postgres psql << EOF
CREATE USER hltraining_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE hltraining_db OWNER hltraining_user ENCODING 'UTF8';
GRANT ALL PRIVILEGES ON DATABASE hltraining_db TO hltraining_user;
\c hltraining_db
GRANT ALL ON SCHEMA public TO hltraining_user;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
\q
EOF
```

#### 步骤6：配置环境变量

```bash
cd /var/www/hltraining
cp .env.example .env
vi .env
```

**必须配置的项目：**

```bash
# 生成安全密钥
python -c "import secrets; print(secrets.token_hex(32))"
# 复制生成的密钥到.env文件的SECRET_KEY

# 数据库连接
DATABASE_URL=postgresql://hltraining_user:your_password@localhost:5432/hltraining_db

# Google AI API
GEMINI_API_KEY=your-gemini-api-key

# Notion集成（可选）
NOTION_TOKEN=your-notion-token
NOTION_DATABASE_ID=your-database-id
```

#### 步骤7：初始化数据库

```bash
source venv/bin/activate
python update_artwork_schema.py
deactivate
```

#### 步骤8：配置systemd服务

```bash
sudo vi /etc/systemd/system/hltraining.service
```

```ini
[Unit]
Description=HLTraining Flask Application
After=network.target postgresql-14.service

[Service]
Type=notify
User=nginx
Group=nginx
WorkingDirectory=/var/www/hltraining
Environment="PATH=/var/www/hltraining/venv/bin"
ExecStart=/var/www/hltraining/venv/bin/gunicorn --config gunicorn_config.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable hltraining
sudo systemctl start hltraining
```

#### 步骤9：配置Nginx

```bash
sudo vi /etc/nginx/conf.d/ai.hlylsj.com.conf
```

复制 `nginx/ai.hlylsj.com.conf` 的内容，然后：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## ⚙️ 配置说明

### 环境变量完整列表

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `SECRET_KEY` | ✅ | Flask密钥 | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_ENV` | ✅ | 环境 | `production` |
| `DATABASE_URL` | ✅ | 数据库连接 | `postgresql://user:pass@localhost:5432/db` |
| `GEMINI_API_KEY` | ✅ | Gemini API | 从 https://aistudio.google.com/ 获取 |
| `NANO_BANANA_API_KEY` | ❌ | Nano Banana API | 可选 |
| `NOTION_TOKEN` | ❌ | Notion集成 | 可选，用于作品同步 |
| `NOTION_DATABASE_ID` | ❌ | Notion数据库ID | 与NOTION_TOKEN配套 |
| `HOST` | ❌ | 监听地址 | `0.0.0.0` (默认) |
| `PORT` | ❌ | 监听端口 | `8080` (默认) |
| `WORKERS` | ❌ | Gunicorn worker数 | `4` (默认: CPU*2+1) |
| `LOG_LEVEL` | ❌ | 日志级别 | `INFO` (默认) |

### Gunicorn配置优化

编辑 `gunicorn_config.py`：

```python
# Worker数量建议
# 3.5GB内存服务器: 4-6 workers
# 2GB内存服务器: 2-4 workers
workers = 4

# 超时设置
timeout = 120  # AI生成可能需要较长时间

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50
```

---

## 🔧 维护操作

### 启动/停止/重启服务

```bash
# 启动
sudo systemctl start hltraining

# 停止
sudo systemctl stop hltraining

# 重启
sudo systemctl restart hltraining

# 重载配置（不中断服务）
sudo systemctl reload hltraining

# 查看状态
sudo systemctl status hltraining
```

### 查看日志

```bash
# 应用日志
tail -f /var/www/hltraining/logs/hltraining.log

# Gunicorn日志
tail -f /var/www/hltraining/logs/access.log
tail -f /var/www/hltraining/logs/error.log

# 系统日志
journalctl -u hltraining -f

# Nginx日志
tail -f /var/log/nginx/hltraining_access.log
tail -f /var/log/nginx/hltraining_error.log
```

### 更新代码

```bash
# 1. 备份当前代码
cd /var/www
sudo tar czf hltraining_backup_$(date +%Y%m%d_%H%M%S).tar.gz hltraining/

# 2. 上传新代码
rsync -avz --exclude='.env' --exclude='*.pyc' \
    /path/to/new/code/ wordpress:/tmp/hltraining_new/

# 3. 更新代码
ssh wordpress
cd /tmp/hltraining_new
sudo cp -r * /var/www/hltraining/

# 4. 更新依赖
cd /var/www/hltraining
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 5. 重启服务
sudo systemctl restart hltraining
```

### 数据库备份

```bash
# PostgreSQL备份
sudo -u postgres pg_dump hltraining_db > hltraining_backup_$(date +%Y%m%d).sql

# 恢复
sudo -u postgres psql hltraining_db < hltraining_backup_20251113.sql

# 自动备份脚本
cat > /usr/local/bin/backup_hltraining_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/hltraining"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump hltraining_db | gzip > $BACKUP_DIR/hltraining_$DATE.sql.gz
# 保留最近30天的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x /usr/local/bin/backup_hltraining_db.sh

# 添加到crontab（每天凌晨3点备份）
echo "0 3 * * * /usr/local/bin/backup_hltraining_db.sh" | sudo crontab -
```

---

## 🔍 故障排查

### 服务无法启动

```bash
# 1. 查看详细错误
journalctl -u hltraining -n 50 --no-pager

# 2. 检查配置文件
cat /var/www/hltraining/.env

# 3. 检查端口占用
sudo netstat -tlnp | grep 8080

# 4. 手动启动测试
cd /var/www/hltraining
source venv/bin/activate
gunicorn --config gunicorn_config.py app:app
```

### 数据库连接失败

```bash
# 测试PostgreSQL连接
PGPASSWORD='your_password' psql -U hltraining_user -h localhost -d hltraining_db -c 'SELECT version();'

# 检查PostgreSQL状态
sudo systemctl status postgresql-14

# 查看PostgreSQL日志
sudo tail -f /var/lib/pgsql/14/data/log/postgresql-*.log
```

### Nginx 502错误

```bash
# 1. 检查Flask服务是否运行
sudo systemctl status hltraining

# 2. 检查端口是否正确
curl http://127.0.0.1:8080

# 3. 检查Nginx错误日志
sudo tail -f /var/log/nginx/hltraining_error.log

# 4. 检查SELinux（Rocky Linux）
sudo setsebool -P httpd_can_network_connect 1
```

### 图片上传失败

```bash
# 检查目录权限
ls -la /var/www/hltraining/uploads
ls -la /var/www/hltraining/creation_sessions

# 修复权限
sudo chmod 777 /var/www/hltraining/uploads
sudo chmod 777 /var/www/hltraining/creation_sessions

# 检查磁盘空间
df -h /var/www
```

### 内存不足

```bash
# 查看内存使用
free -h

# 减少Gunicorn worker数量
# 编辑 gunicorn_config.py
workers = 2  # 从4减少到2

# 重启服务
sudo systemctl restart hltraining
```

---

## 📊 性能优化

### PostgreSQL优化

编辑 `/var/lib/pgsql/14/data/postgresql.conf`：

```ini
# 内存设置（3.5GB总内存）
shared_buffers = 512MB
effective_cache_size = 2GB
maintenance_work_mem = 128MB
work_mem = 16MB

# 连接设置
max_connections = 100

# WAL设置
wal_buffers = 16MB
checkpoint_completion_target = 0.9

# 查询优化
random_page_cost = 1.1  # SSD
effective_io_concurrency = 200
```

重启PostgreSQL：

```bash
sudo systemctl restart postgresql-14
```

### Nginx缓存配置

在 `/etc/nginx/conf.d/ai.hlylsj.com.conf` 中添加：

```nginx
# 添加到http块
proxy_cache_path /var/cache/nginx/hltraining levels=1:2 keys_zone=hltraining_cache:10m max_size=500m inactive=60m use_temp_path=off;

# 在location /static/ 中添加
proxy_cache hltraining_cache;
proxy_cache_valid 200 30d;
proxy_cache_use_stale error timeout http_500 http_502 http_503;
```

---

## 🔐 安全建议

1. **定期更新系统和依赖**
```bash
sudo dnf update -y
pip install --upgrade -r requirements.txt
```

2. **配置防火墙**
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

3. **使用强密码**
   - 数据库密码至少16位
   - SECRET_KEY使用随机生成
   - 定期轮换API密钥

4. **监控日志**
```bash
# 安装fail2ban防止暴力破解
sudo dnf install -y fail2ban
sudo systemctl enable --now fail2ban
```

5. **备份策略**
   - 数据库：每天自动备份
   - 代码：使用Git版本控制
   - 上传文件：定期备份到对象存储

---

## 📞 支持

如有问题，请查看：
- GitHub Issues: https://github.com/why198546/HLTraining/issues
- 日志文件: `/var/www/hltraining/logs/`

---

**部署完成！祝你使用愉快！** 🎉
