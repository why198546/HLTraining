#!/bin/bash

###############################################################################
# 服务器端代码更新脚本
# 此脚本应放在服务器的 /var/www/hltraining 目录中
# 用途：从GitHub拉取最新代码并重启服务（如果使用Git方式）
###############################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_DIR="/var/www/hltraining"
VENV_DIR="$APP_DIR/venv"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🔄 HLTraining 服务器端更新${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查root权限
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ 此脚本需要root权限运行${NC}"
    echo "   使用: sudo bash server_update.sh"
    exit 1
fi

# 步骤1: 备份当前版本
echo -e "${YELLOW}💾 步骤1/5: 备份当前版本...${NC}"
BACKUP_DIR="/root/hltraining_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份关键文件
tar -czf $BACKUP_DIR/hltraining_$TIMESTAMP.tar.gz \
    -C $APP_DIR \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='uploads' \
    --exclude='creation_sessions' \
    --exclude='*.log' \
    . 2>/dev/null || true

echo -e "${GREEN}✅ 备份完成: $BACKUP_DIR/hltraining_$TIMESTAMP.tar.gz${NC}"
echo ""

# 步骤2: 更新Python依赖
echo -e "${YELLOW}📚 步骤2/5: 更新Python依赖...${NC}"
cd $APP_DIR
source $VENV_DIR/bin/activate
pip install -r requirements.txt --quiet --upgrade
deactivate
echo -e "${GREEN}✅ 依赖更新完成${NC}"
echo ""

# 步骤3: 数据库迁移（如果需要）
echo -e "${YELLOW}🗄️  步骤3/5: 检查数据库...${NC}"
# 如果使用Flask-Migrate
# cd $APP_DIR
# source $VENV_DIR/bin/activate
# flask db upgrade
# deactivate
echo -e "${BLUE}⏭️  跳过（暂无迁移需求）${NC}"
echo ""

# 步骤4: 确保目录和权限
echo -e "${YELLOW}📁 步骤4/5: 检查目录权限...${NC}"
mkdir -p $APP_DIR/{uploads,creation_sessions,static/uploads,instance,logs,models}
chmod 777 $APP_DIR/{uploads,creation_sessions,static/uploads,instance,logs}
chown -R nginx:nginx $APP_DIR
echo -e "${GREEN}✅ 权限设置完成${NC}"
echo ""

# 步骤5: 重启服务
echo -e "${YELLOW}🔄 步骤5/5: 重启服务...${NC}"

# 重启Gunicorn
if systemctl is-active --quiet hltraining; then
    systemctl restart hltraining
    echo -e "${GREEN}✅ Gunicorn服务已重启${NC}"
else
    echo -e "${YELLOW}⚠️  Gunicorn服务未运行，启动中...${NC}"
    systemctl start hltraining
fi

# 重启Nginx
systemctl reload nginx
echo -e "${GREEN}✅ Nginx已重载配置${NC}"

# 检查服务状态
sleep 2
if systemctl is-active --quiet hltraining; then
    echo -e "${GREEN}✅ 服务运行正常${NC}"
else
    echo -e "${RED}❌ 服务启动失败，请检查日志${NC}"
    journalctl -u hltraining -n 20 --no-pager
    exit 1
fi
echo ""

# 完成
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 更新完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "📊 查看服务状态: ${YELLOW}systemctl status hltraining${NC}"
echo -e "📝 查看实时日志: ${YELLOW}tail -f $APP_DIR/logs/hltraining.log${NC}"
echo -e "📝 查看系统日志: ${YELLOW}journalctl -u hltraining -f${NC}"
echo ""
