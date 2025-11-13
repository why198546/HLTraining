# 开发同步指南

> 本地开发 + 服务器部署的完整工作流程

## 📋 目录

1. [环境差异说明](#环境差异说明)
2. [同步方案](#同步方案)
3. [快速开始](#快速开始)
4. [日常开发流程](#日常开发流程)
5. [常见问题](#常见问题)

---

## 🔄 环境差异说明

### 本地开发环境
- **操作系统**: macOS
- **数据库**: SQLite (`hltraining.db`)
- **Python**: 虚拟环境 `.venv/`
- **运行方式**: Flask开发服务器 (`python app.py`)
- **配置文件**: `.env` (本地配置)

### 生产服务器环境
- **操作系统**: Rocky Linux 9
- **服务器**: SSH别名 `wordpress`
- **数据库**: PostgreSQL 14
- **路径**: `/var/www/hltraining`
- **Python**: 虚拟环境 `venv/`
- **运行方式**: Gunicorn + Nginx
- **配置文件**: `.env` (生产配置)

---

## 🚀 同步方案

### 方案选择：rsync + SSH

**优势：**
- ✅ 无需Git（服务器无Git）
- ✅ 快速增量同步
- ✅ 自动排除无关文件
- ✅ 环境变量分离
- ✅ 一键部署

**工作原理：**
```
本地修改代码 → sync_to_server.sh → rsync同步 → 服务器重启服务
```

---

## 🎯 快速开始

### 1. 首次设置

#### 本地准备
```bash
# 1. 给同步脚本添加执行权限
chmod +x sync_to_server.sh
chmod +x server_update.sh

# 2. 测试SSH连接
ssh wordpress "echo 'SSH连接正常'"
```

#### 服务器准备
```bash
# SSH连接到服务器
ssh wordpress

# 1. 确保服务器 .env 文件已配置（PostgreSQL）
cd /var/www/hltraining
sudo nano .env

# 重要配置项：
DATABASE_URL=postgresql://username:password@localhost:5432/hltraining
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=生产环境密钥（与本地不同）

# 2. 上传server_update.sh到服务器
# 从本地执行：
scp server_update.sh wordpress:/var/www/hltraining/
ssh wordpress "chmod +x /var/www/hltraining/server_update.sh"
```

### 2. 配置检查清单

#### ✅ 本地 `.env` 配置
```bash
# 本地开发配置
DATABASE_URL=sqlite:///hltraining.db
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=本地开发密钥
```

#### ✅ 服务器 `.env` 配置
```bash
# 生产环境配置
DATABASE_URL=postgresql://hltraining_user:密码@localhost:5432/hltraining_db
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=生产环境密钥（必须不同！）
```

---

## 💻 日常开发流程

### 标准工作流

```bash
# 1. 本地开发
# 启动本地开发服务器
python app.py
# 或使用VSCode任务：启动Flask开发服务器

# 2. 修改代码
# 在本地修改 app.py, templates/, static/ 等文件

# 3. 本地测试
# 浏览器访问 http://localhost:8080
# 确认功能正常

# 4. 同步到服务器
./sync_to_server.sh

# 完成！代码已同步并自动重启服务
```

### sync_to_server.sh 做了什么？

```
步骤1: 测试SSH连接
  ↓
步骤2: rsync同步代码（排除.env、数据库、日志等）
  ↓
步骤3: 服务器端更新依赖
  ↓
步骤4: 重启Gunicorn和Nginx
  ↓
完成：服务器已更新
```

### 自动排除的文件

以下文件**不会**同步到服务器（保护服务器数据）：
- `.env` - 环境配置（本地和服务器分离）
- `.venv/`, `venv/` - 虚拟环境
- `__pycache__/`, `*.pyc` - Python缓存
- `*.db`, `*.sqlite` - 数据库文件
- `uploads/*` - 用户上传文件
- `creation_sessions/*` - 创作会话
- `models/*` - 生成的模型
- `logs/` - 日志文件
- `instance/` - 实例数据

---

## 🔍 常见问题

### Q1: 如何查看服务器日志？

```bash
# 应用日志
ssh wordpress 'tail -f /var/www/hltraining/logs/hltraining.log'

# 系统服务日志
ssh wordpress 'journalctl -u hltraining -f'

# Nginx日志
ssh wordpress 'tail -f /var/log/nginx/error.log'
```

### Q2: 同步后服务无法启动？

```bash
# 1. 检查服务状态
ssh wordpress 'systemctl status hltraining'

# 2. 查看错误日志
ssh wordpress 'journalctl -u hltraining -n 50'

# 3. 手动重启服务
ssh wordpress 'sudo systemctl restart hltraining'

# 4. 检查.env配置
ssh wordpress 'cat /var/www/hltraining/.env'
```

### Q3: 如何回滚到之前版本？

```bash
# 服务器会自动备份，查看备份
ssh wordpress 'ls -lh /root/hltraining_backups/'

# 恢复备份（在服务器上执行）
ssh wordpress
cd /var/www/hltraining
sudo tar -xzf /root/hltraining_backups/hltraining_20251113_120000.tar.gz
sudo systemctl restart hltraining
```

### Q4: 修改了数据库模型怎么办？

```bash
# 本地测试数据库迁移
flask db migrate -m "描述修改内容"
flask db upgrade

# 同步到服务器后，在服务器执行
ssh wordpress
cd /var/www/hltraining
source venv/bin/activate
flask db upgrade
sudo systemctl restart hltraining
```

### Q5: 需要修改服务器 .env 配置？

```bash
# 方法1: SSH登录编辑
ssh wordpress
sudo nano /var/www/hltraining/.env
# 修改后重启服务
sudo systemctl restart hltraining

# 方法2: 远程单行命令
ssh wordpress "cd /var/www/hltraining && echo 'NEW_VAR=value' >> .env && sudo systemctl restart hltraining"
```

### Q6: 如何添加新的Python依赖？

```bash
# 1. 本地安装并测试
pip install package-name
pip freeze > requirements.txt

# 2. 同步到服务器
./sync_to_server.sh

# 服务器会自动执行 pip install -r requirements.txt
```

---

## 🛠️ 高级操作

### 只同步不重启

修改 `sync_to_server.sh`，注释掉步骤4（重启服务）部分

### 查看同步了哪些文件

```bash
# rsync 预览模式（不实际同步）
rsync -avz --dry-run --delete \
    --exclude='.git/' \
    --exclude='.venv/' \
    --exclude='*.db' \
    . wordpress:/var/www/hltraining/
```

### 同步特定目录

```bash
# 只同步templates
rsync -avz templates/ wordpress:/var/www/hltraining/templates/
ssh wordpress 'sudo systemctl restart hltraining'

# 只同步static
rsync -avz static/ wordpress:/var/www/hltraining/static/
ssh wordpress 'sudo systemctl reload nginx'
```

### 服务器直接测试代码

```bash
# SSH到服务器
ssh wordpress
cd /var/www/hltraining
source venv/bin/activate

# 运行Python脚本测试
python -c "from app import app; print(app.config)"

# 临时启动开发服务器（调试用）
FLASK_ENV=development python app.py
```

---

## 📊 性能优化建议

### 1. 使用SSH密钥认证

```bash
# 本地生成密钥（如果没有）
ssh-keygen -t rsa -b 4096

# 复制到服务器
ssh-copy-id wordpress

# 之后无需输入密码
```

### 2. 压缩传输

`sync_to_server.sh` 已启用 `-z` 参数（压缩）

### 3. 增量同步

rsync 自动只传输变化的文件

---

## 🔐 安全注意事项

1. **✅ 绝不同步 .env 文件**
   - 本地和服务器使用不同的密钥
   - 服务器使用更强的 SECRET_KEY
   
2. **✅ 数据库分离**
   - 本地: SQLite（开发测试）
   - 服务器: PostgreSQL（生产数据）

3. **✅ 备份重要数据**
   - `server_update.sh` 自动备份
   - 定期手动备份数据库

4. **✅ 权限检查**
   - 确保 `nginx` 用户有正确权限
   - 上传目录需要写权限

---

## 📚 相关文档

- [部署指南](DEPLOYMENT.md) - 服务器首次部署
- [README](README.md) - 项目概述
- [.env.example](.env.example) - 环境变量模板

---

## ⚡ 快速命令参考

```bash
# 同步代码到服务器
./sync_to_server.sh

# 查看服务器日志
ssh wordpress 'tail -f /var/www/hltraining/logs/hltraining.log'

# 重启服务
ssh wordpress 'sudo systemctl restart hltraining'

# 检查服务状态
ssh wordpress 'systemctl status hltraining'

# 服务器端手动更新
ssh wordpress 'cd /var/www/hltraining && sudo bash server_update.sh'
```

---

**💡 提示**: 如有问题，先查看日志，90%的问题都能在日志中找到答案！
