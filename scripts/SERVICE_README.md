# 服务管理脚本使用说明

## 快速开始

### 基本使用

```bash
# 启动服务
./scripts/service.sh start

# 停止服务
./scripts/service.sh stop

# 重启服务
./scripts/service.sh restart

# 查看状态
./scripts/service.sh status

# 查看日志
./scripts/service.sh logs
```

### 高级用法

#### 查看实时日志
```bash
./scripts/service.sh logs -f
```

#### 查看错误日志
```bash
./scripts/service.sh logs -e
```

#### 查看最近N行日志
```bash
./scripts/service.sh logs -n 100
```

## 详细说明

### 服务管理脚本 (service.sh)

这是一个Shell脚本，用于管理Flask应用的后台运行。

**功能特性：**
- ✅ 后台运行Flask应用
- ✅ PID文件管理，防止重复启动
- ✅ 优雅关闭和强制关闭
- ✅ 日志输出和错误日志分离
- ✅ 服务状态查看（进程信息、端口监听、最近日志）
- ✅ 彩色输出，易于识别

**日志文件位置：**
- 应用日志: `logs/app.log`
- 错误日志: `logs/error.log`
- PID文件: `app.pid`

### 系统服务配置模板

项目提供了三种系统服务配置模板，可以让应用在系统启动时自动运行：

#### 1. systemd (Linux)

适用于大多数现代Linux系统（Ubuntu, CentOS, Debian等）

```bash
# 1. 编辑模板文件，修改路径
cp scripts/systemd-service-template.txt /tmp/hltraining.service
# 编辑 /tmp/hltraining.service，修改User和路径

# 2. 安装服务
sudo cp /tmp/hltraining.service /etc/systemd/system/
sudo systemctl daemon-reload

# 3. 启用并启动服务
sudo systemctl enable hltraining
sudo systemctl start hltraining

# 4. 查看状态
sudo systemctl status hltraining

# 5. 查看日志
sudo journalctl -u hltraining -f
```

#### 2. launchd (macOS)

适用于macOS系统

```bash
# 1. 编辑模板文件，修改路径
cp scripts/launchd-plist-template.txt ~/Library/LaunchAgents/com.hltraining.app.plist
# 编辑 ~/Library/LaunchAgents/com.hltraining.app.plist

# 2. 加载服务
launchctl load ~/Library/LaunchAgents/com.hltraining.app.plist

# 3. 启动服务
launchctl start com.hltraining.app

# 4. 查看状态
launchctl list | grep hltraining

# 5. 停止服务
launchctl stop com.hltraining.app

# 6. 卸载服务
launchctl unload ~/Library/LaunchAgents/com.hltraining.app.plist
```

#### 3. Supervisor

跨平台进程管理工具，推荐用于生产环境

```bash
# 1. 安装supervisor
pip install supervisor

# 2. 生成配置文件（如果没有）
echo_supervisord_conf > /etc/supervisord.conf

# 3. 复制配置
sudo cp scripts/supervisor-config-template.conf /etc/supervisor/conf.d/hltraining.conf
# 编辑配置文件，修改路径

# 4. 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 5. 启动服务
sudo supervisorctl start hltraining

# 6. 查看状态
sudo supervisorctl status hltraining

# 7. 查看日志
sudo supervisorctl tail -f hltraining

# 8. 停止服务
sudo supervisorctl stop hltraining

# 9. 重启服务
sudo supervisorctl restart hltraining
```

## 生产环境部署建议

### 使用Gunicorn + Nginx

在生产环境中，建议使用Gunicorn作为WSGI服务器，Nginx作为反向代理：

```bash
# 1. 安装Gunicorn
pip install gunicorn

# 2. 使用Gunicorn启动（修改service.sh中的启动命令）
gunicorn -w 4 -b 127.0.0.1:8088 app:app

# 3. 配置Nginx反向代理
# 在 /etc/nginx/sites-available/ 创建配置文件
```

示例Nginx配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8088;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /Users/hongyuwang/code/HLTraining/static;
    }
}
```

### 监控和日志

推荐工具：
- **日志管理**: logrotate（自动轮转日志）
- **监控**: supervisor + monit
- **性能监控**: New Relic, Datadog, Prometheus

### 安全建议

1. **不要使用root用户运行**
2. **配置防火墙**，只开放必要端口
3. **使用HTTPS**（Let's Encrypt免费证书）
4. **定期更新依赖**
5. **设置日志轮转**，防止磁盘占满

## 故障排查

### 服务无法启动

1. 检查虚拟环境是否存在
```bash
ls -la .venv/bin/python
```

2. 检查端口是否被占用
```bash
lsof -i :8088
```

3. 查看错误日志
```bash
cat logs/error.log
```

### 服务自动停止

1. 检查内存使用
```bash
free -h  # Linux
vm_stat  # macOS
```

2. 检查系统日志
```bash
sudo journalctl -xe  # Linux
log show --predicate 'process == "Python"' --last 1h  # macOS
```

### 权限问题

```bash
# 确保脚本有执行权限
chmod +x scripts/service.sh

# 确保日志目录可写
chmod 755 logs/
```

## 常见问题

**Q: 如何在开机时自动启动？**  
A: 使用systemd（Linux）或launchd（macOS）配置，参考上面的系统服务配置部分。

**Q: 如何更改监听端口？**  
A: 修改 `app.py` 中的端口配置，然后重启服务。

**Q: 日志文件太大怎么办？**  
A: 配置logrotate定期轮转日志，或手动清理：`> logs/app.log`

**Q: 如何实现零停机更新？**  
A: 使用Gunicorn的graceful reload功能：`kill -HUP <gunicorn_pid>`

## 联系方式

如有问题，请查看项目文档或联系维护人员。
