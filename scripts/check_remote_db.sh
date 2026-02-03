#!/bin/bash

###############################################################################
# 远程数据库状态检查脚本
# 用途：检查服务器数据库是否需要迁移
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
SSH_KEY="$HOME/.ssh/wordpress_openssh"
SSH_CMD="ssh -i $SSH_KEY -o StrictHostKeyChecking=no"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🔍 远程数据库状态检查${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查SSH连接
echo -e "${YELLOW}📡 测试服务器连接...${NC}"
if ! eval "$SSH_CMD $SERVER_USER@$SERVER_HOST 'echo'" > /dev/null 2>&1; then
    echo -e "${RED}❌ 无法连接到服务器${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 连接成功${NC}"
echo ""

# 检查数据库状态
echo -e "${YELLOW}🗄️  检查数据库表结构...${NC}"

# 读取本地数据库结构作为参考
LOCAL_DB_PATH="instance/hltraining.db"
if [ -f "$LOCAL_DB_PATH" ]; then
    echo "📖 读取本地数据库结构作为参考..."
    LOCAL_USERS_FIELDS=$(sqlite3 "$LOCAL_DB_PATH" "PRAGMA table_info(users);" 2>/dev/null | awk -F'|' '{print $2}' | tr '\n' ',' | sed 's/,$//')
    LOCAL_CANVAS_FIELDS=$(sqlite3 "$LOCAL_DB_PATH" "PRAGMA table_info(canvas_projects);" 2>/dev/null | awk -F'|' '{print $2}' | tr '\n' ',' | sed 's/,$//')
    
    USERS_FIELD_COUNT=$(echo "$LOCAL_USERS_FIELDS" | tr ',' '\n' | wc -l | tr -d ' ')
    CANVAS_FIELD_COUNT=$(echo "$LOCAL_CANVAS_FIELDS" | tr ',' '\n' | wc -l | tr -d ' ')
    
    echo "   本地 users 表: $USERS_FIELD_COUNT 个字段"
    echo "   本地 canvas_projects 表: $CANVAS_FIELD_COUNT 个字段"
    echo ""
else
    echo -e "${YELLOW}⚠️  本地数据库不存在，使用预设字段列表${NC}"
    LOCAL_USERS_FIELDS="feedback_templates,daily_token_amount,trial_end_date,last_token_grant_date,course_type"
    LOCAL_CANVAS_FIELDS="project_type,width,height,last_opened_at"
    echo ""
fi

$SSH_CMD $SERVER_USER@$SERVER_HOST "bash -s" "$LOCAL_USERS_FIELDS" "$LOCAL_CANVAS_FIELDS" << 'ENDSSH'
    set -e
    cd /var/www/hltraining
    
    # 接收本地字段列表
    LOCAL_USERS_FIELDS="$1"
    LOCAL_CANVAS_FIELDS="$2"

    if [ ! -f instance/hltraining.db ]; then
        echo "❌ 数据库文件不存在: instance/hltraining.db"
        exit 1
    fi

    echo "✅ 数据库文件存在"
    echo ""
    
    # 检查 users 表结构
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Users 表字段检查:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    missing_count=0
    
    # 使用本地字段列表进行检查
    if [ -n "$LOCAL_USERS_FIELDS" ]; then
        IFS=',' read -ra FIELDS <<< "$LOCAL_USERS_FIELDS"
        for field in "${FIELDS[@]}"; do
            if sqlite3 instance/hltraining.db "PRAGMA table_info(users);" | awk -F'|' '{print $2}' | grep -qx "$field"; then
                echo "  ✅ ${field}"
            else
                echo "  ❌ ${field} (缺失)"
                missing_count=$((missing_count + 1))
            fi
        done
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Canvas_Projects 表字段检查:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 使用本地字段列表进行检查
    if [ -n "$LOCAL_CANVAS_FIELDS" ]; then
        IFS=',' read -ra FIELDS <<< "$LOCAL_CANVAS_FIELDS"
        for field in "${FIELDS[@]}"; do
            if sqlite3 instance/hltraining.db "PRAGMA table_info(canvas_projects);" | awk -F'|' '{print $2}' | grep -qx "$field"; then
                echo "  ✅ ${field}"
            else
                echo "  ❌ ${field} (缺失)"
                missing_count=$((missing_count + 1))
            fi
        done
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 统计信息
    user_count=$(sqlite3 instance/hltraining.db "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")
    artwork_count=$(sqlite3 instance/hltraining.db "SELECT COUNT(*) FROM artworks;" 2>/dev/null || echo "0")
    
    echo "📊 数据统计:"
    echo "  用户数: ${user_count}"
    echo "  作品数: ${artwork_count}"
    echo ""
    
    if [ ${missing_count} -eq 0 ]; then
        echo "✅ 数据库结构完整，无需迁移"
        exit 0
    else
        echo "⚠️  发现 ${missing_count} 个缺失字段，需要执行数据库迁移"
        echo ""
        echo "建议执行: ./scripts/sync_to_server.sh"
        exit 1
    fi
ENDSSH

exit_code=$?
echo ""

if [ ${exit_code} -eq 0 ]; then
    echo -e "${GREEN}✅ 检查完成：数据库状态正常${NC}"
else
    echo -e "${YELLOW}⚠️  检查完成：数据库需要迁移${NC}"
fi

exit ${exit_code}
