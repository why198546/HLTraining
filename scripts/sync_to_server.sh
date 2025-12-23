#!/bin/bash

###############################################################################
# HLTraining 本地到服务器同步脚本
# 用途：将本地代码快速同步到服务器并重启服务
###############################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
SERVER_HOST="47.95.214.47"
SERVER_USER="root"
SERVER_PATH="/var/www/hltraining"
LOCAL_PATH="."
SSH_KEY="$HOME/.ssh/wordpress_openssh"
SSH_CMD="ssh -i $SSH_KEY -o StrictHostKeyChecking=no"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🚀 HLTraining 代码同步到服务器${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查是否在项目根目录
if [ ! -f "run.py" ]; then
    echo -e "${RED}❌ 错误：请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 步骤1: 测试SSH连接
echo -e "${YELLOW}📡 步骤1/4: 测试服务器连接...${NC}"
if eval "$SSH_CMD $SERVER_USER@$SERVER_HOST 'echo 连接成功'" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 服务器连接正常${NC}"
else
    echo -e "${RED}❌ 无法连接到服务器 $SERVER_HOST${NC}"
    echo "   请检查SSH密钥或网络连接"
    exit 1
fi
echo ""

# 步骤2: 同步代码文件
echo -e "${YELLOW}📦 步骤2/4: 同步代码到服务器...${NC}"
echo "   源目录: $LOCAL_PATH"
echo "   目标: $SERVER_HOST:$SERVER_PATH"
echo ""
echo -e "${BLUE}🔒 数据保护: 以下内容不会被同步${NC}"
echo "   • 环境变量 (.env)"
echo "   • 数据库文件 (*.db, *.sqlite)"
echo "   • 用户上传 (uploads/)"
echo "   • 创作会话 (creation_sessions/)"
echo "   • 3D模型 (models/)"
echo "   • 日志文件 (logs/)"
echo ""

# 使用rsync同步，排除不需要的文件
rsync -avz -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" --delete \
    --exclude='.git/' \
    --exclude='.venv/' \
    --exclude='venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='*.db' \
    --exclude='*.sqlite' \
    --exclude='*.sqlite3' \
    --exclude='*.log' \
    --exclude='.DS_Store' \
    --exclude='uploads/*' \
    --exclude='creation_sessions/*' \
    --exclude='models/*' \
    --exclude='instance/' \
    --exclude='logs/' \
    --exclude='.env' \
    --exclude='.env.local' \
    --exclude='.env.production' \
    --exclude='node_modules/' \
    --exclude='static/gallery/*' \
    --exclude='static/uploads/*' \
    --exclude='.playwright-mcp/' \
    $LOCAL_PATH/ $SERVER_USER@$SERVER_HOST:$SERVER_PATH/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 代码同步完成${NC}"
else
    echo -e "${RED}❌ 代码同步失败${NC}"
    exit 1
fi
echo ""

# 步骤3: 服务器端更新操作
echo -e "${YELLOW}🔧 步骤3/4: 服务器端更新...${NC}"
$SSH_CMD $SERVER_USER@$SERVER_HOST "bash -s" << 'ENDSSH'
    set -e
    cd /var/www/hltraining
    
    # 升级 pip
    python3 -m pip install --upgrade pip setuptools wheel
    
    # 激活虚拟环境并更新依赖
    source venv/bin/activate
    pip install -r requirements.txt --quiet || pip install -r requirements.txt
    
    # 确保必要目录存在且权限正确
    mkdir -p uploads creation_sessions static/uploads instance logs models
    chmod 777 uploads creation_sessions static/uploads instance logs
    
    # 收集静态文件（如果有）
    # python -c "from app import app; app.static_folder" 2>/dev/null || true
    
    echo "✅ 服务器端更新完成"
ENDSSH

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 服务器更新完成${NC}"
else
    echo -e "${RED}❌ 服务器更新失败${NC}"
    exit 1
fi
echo ""

# 步骤3.5: 远端数据库迁移检测（如果使用 SQLite）
echo -e "${YELLOW}🗄️ 步骤3.5: 远端数据库迁移检测...${NC}"
if eval "$SSH_CMD $SERVER_USER@$SERVER_HOST 'if [ -f /var/www/hltraining/instance/hltraining.db ]; then echo yes; else echo no; fi'" | grep -q yes; then
    # 执行远端迁移检测脚本
    $SSH_CMD $SERVER_USER@$SERVER_HOST "bash -s" << 'ENDSSH'
        set -e
        cd /var/www/hltraining

        if [ -f instance/hltraining.db ]; then
            # 检查 canvas_projects 表中是否存在需要的列
            missing=0
            for col in project_type width height last_opened_at; do
                if ! sqlite3 instance/hltraining.db "PRAGMA table_info(canvas_projects);" | awk -F'|' '{print $2}' | grep -qx "${col}"; then
                    missing=1
                fi
            done

            if [ "${missing}" -eq 1 ]; then
                echo "🔍 检测到数据库需要迁移，先进行备份..."
                timestamp=$(date +%F_%H%M%S)
                backup_path="instance/hltraining_backup_${timestamp}.db"
                cp instance/hltraining.db "${backup_path}"
                echo "✅ 备份完成: ${backup_path}"
                
                echo "🔧 开始执行数据库迁移..."
                # 激活虚拟环境（若存在）并运行迁移脚本
                if [ -f venv/bin/activate ]; then
                    source venv/bin/activate
                fi
                python3 scripts/add_project_type_column.py || {
                    echo "❌ 迁移失败" >&2
                    exit 1
                }
                echo "✅ 数据库迁移完成"
            else
                echo "✓ 数据库结构正常，无需迁移"
            fi
        else
            echo "⚠️ 数据库文件不存在"
        fi
ENDSSH
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 远端数据库迁移失败，已中止后续操作${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ 远端数据库迁移检测完成${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  远端没有检测到 SQLite 数据库文件，跳过数据库迁移检测${NC}"
fi
echo ""

# 步骤4: 重启服务
echo -e "${YELLOW}🔄 步骤4/4: 重启服务...${NC}"
$SSH_CMD $SERVER_USER@$SERVER_HOST << 'ENDSSH'
    # 重启Gunicorn服务
    if systemctl is-active --quiet hltraining; then
        sudo systemctl restart hltraining
        echo "✅ Gunicorn服务已重启"
    else
        echo "⚠️  Gunicorn服务未运行，尝试启动..."
        sudo systemctl start hltraining
    fi
    
    # 重启Nginx
    sudo systemctl reload nginx
    echo "✅ Nginx已重载配置"
    
    # 检查服务状态
    if systemctl is-active --quiet hltraining; then
        echo "✅ 服务运行正常"
    else
        echo "❌ 服务启动失败"
        exit 1
    fi
ENDSSH

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 服务重启成功${NC}"
else
    echo -e "${RED}❌ 服务重启失败${NC}"
    exit 1
fi
echo ""

# 完成
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 同步完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "📊 查看服务状态: ${YELLOW}ssh $SERVER_HOST 'systemctl status hltraining'${NC}"
echo -e "📝 查看日志: ${YELLOW}ssh $SERVER_HOST 'tail -f /var/www/hltraining/logs/hltraining.log'${NC}"
echo ""
