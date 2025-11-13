#!/bin/bash

###############################################################################
# HLTraining 自动化部署脚本
# 适用于Rocky Linux 9.6 / CentOS / RHEL系统
###############################################################################

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
APP_NAME="hltraining"
APP_DIR="/var/www/hltraining"
APP_USER="www-data"  # 根据系统调整，Rocky Linux可能是nginx或apache
VENV_DIR="$APP_DIR/venv"
PYTHON_BIN="/usr/bin/python3"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🚀 HLTraining 儿童AI创作平台 部署脚本${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查root权限
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ 此脚本需要root权限运行${NC}"
    echo "   使用: sudo bash deploy.sh"
    exit 1
fi

# 步骤1: 检查系统环境
echo -e "${YELLOW}📋 步骤1/9: 检查系统环境...${NC}"
echo "   系统: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "   Python: $($PYTHON_BIN --version)"
echo "   内存: $(free -h | grep Mem | awk '{print $2}')"
echo "   磁盘: $(df -h / | tail -1 | awk '{print $4}') 可用"
echo ""

# 步骤2: 安装系统依赖
echo -e "${YELLOW}📦 步骤2/9: 安装系统依赖...${NC}"
dnf install -y python3-devel gcc postgresql-devel || {
    echo -e "${RED}❌ 系统依赖安装失败${NC}"
    exit 1
}
echo -e "${GREEN}✅ 系统依赖安装完成${NC}"
echo ""

# 步骤3: 创建应用目录
echo -e "${YELLOW}📁 步骤3/9: 创建应用目录...${NC}"
mkdir -p $APP_DIR
mkdir -p $APP_DIR/{uploads,creation_sessions,static/uploads,instance,logs}
chmod 755 $APP_DIR
chmod 777 $APP_DIR/{uploads,creation_sessions,static/uploads,instance,logs}
echo -e "${GREEN}✅ 目录创建完成${NC}"
echo ""

# 步骤4: 创建Python虚拟环境
echo -e "${YELLOW}🐍 步骤4/9: 创建Python虚拟环境...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    $PYTHON_BIN -m venv $VENV_DIR
    echo -e "${GREEN}✅ 虚拟环境创建完成${NC}"
else
    echo -e "${BLUE}⏭️  虚拟环境已存在${NC}"
fi
echo ""

# 步骤5: 复制应用文件
echo -e "${YELLOW}📋 步骤5/9: 复制应用文件...${NC}"
echo "   当前目录: $(pwd)"
echo "   目标目录: $APP_DIR"

# 复制应用代码
cp -r ./{*.py,*.sh,templates,static,auth,api,utils,forms.py,models.py,requirements.txt} $APP_DIR/ 2>/dev/null || true

# 不复制敏感文件和临时文件
rm -rf $APP_DIR/{.git,.env,.venv,__pycache__,*.pyc,*.pyo,.DS_Store}

echo -e "${GREEN}✅ 文件复制完成${NC}"
echo ""

# 步骤6: 安装Python依赖
echo -e "${YELLOW}📚 步骤6/9: 安装Python依赖...${NC}"
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r $APP_DIR/requirements.txt || {
    echo -e "${RED}❌ Python依赖安装失败${NC}"
    exit 1
}
deactivate
echo -e "${GREEN}✅ Python依赖安装完成${NC}"
echo ""

# 步骤7: 配置环境变量
echo -e "${YELLOW}⚙️  步骤7/9: 配置环境变量...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  .env文件不存在，从.env.example创建${NC}"
    cp $APP_DIR/.env.example $APP_DIR/.env
    echo -e "${RED}📝 重要: 请编辑 $APP_DIR/.env 文件，填入真实的配置！${NC}"
    echo "   需要配置的项目："
    echo "   - SECRET_KEY (生成方法: python -c 'import secrets; print(secrets.token_hex(32))')"
    echo "   - DATABASE_URL"
    echo "   - GEMINI_API_KEY"
    echo "   - NOTION_TOKEN (可选)"
else
    echo -e "${BLUE}⏭️  .env文件已存在${NC}"
fi
echo ""

# 步骤8: 初始化数据库
echo -e "${YELLOW}🗄️  步骤8/9: 初始化数据库...${NC}"
echo "   请选择数据库类型："
echo "   1) PostgreSQL (推荐，性能最佳)"
echo "   2) MariaDB/MySQL"
echo "   3) SQLite (仅开发环境)"
read -p "   请输入选择 [1-3]: " db_choice

case $db_choice in
    1)
        echo -e "${BLUE}📊 选择了PostgreSQL${NC}"
        echo "   运行命令: bash $APP_DIR/setup_postgresql.sh"
        ;;
    2)
        echo -e "${BLUE}📊 选择了MariaDB/MySQL${NC}"
        echo "   请手动创建数据库和用户"
        ;;
    3)
        echo -e "${YELLOW}⚠️  SQLite仅适合开发环境${NC}"
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

# 运行数据库迁移
cd $APP_DIR
source $VENV_DIR/bin/activate
python update_artwork_schema.py || true
deactivate
echo -e "${GREEN}✅ 数据库初始化完成${NC}"
echo ""

# 步骤9: 创建systemd服务
echo -e "${YELLOW}🔧 步骤9/9: 创建系统服务...${NC}"
cat > /etc/systemd/system/hltraining.service << 'EOF'
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
EOF

# 重新加载systemd
systemctl daemon-reload
systemctl enable hltraining.service

echo -e "${GREEN}✅ 系统服务创建完成${NC}"
echo ""

# 完成总结
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📝 后续步骤：${NC}"
echo ""
echo "1. 编辑配置文件："
echo "   vi $APP_DIR/.env"
echo ""
echo "2. 配置Nginx反向代理："
echo "   vi /etc/nginx/conf.d/ai.hlylsj.com.conf"
echo ""
echo "3. 启动服务："
echo "   systemctl start hltraining"
echo "   systemctl status hltraining"
echo ""
echo "4. 重载Nginx："
echo "   systemctl reload nginx"
echo ""
echo "5. 查看日志："
echo "   tail -f $APP_DIR/logs/hltraining.log"
echo "   journalctl -u hltraining -f"
echo ""
echo -e "${GREEN}✨ HLTraining儿童AI创作平台已准备就绪！${NC}"
echo ""
