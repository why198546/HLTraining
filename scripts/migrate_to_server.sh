#!/bin/bash

###############################################################################
# 数据库迁移到服务器的自动化脚本
# 用途：安全地将数据库结构变更应用到生产服务器
###############################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
SERVER_HOST="wordpress"
SERVER_PATH="/var/www/hltraining"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🗄️  数据库迁移到生产服务器${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 步骤1: 确认迁移文件存在
echo -e "${YELLOW}📋 步骤1/6: 检查迁移文件...${NC}"
if [ ! -d "migrations/versions" ]; then
    echo -e "${RED}❌ 找不到migrations/versions目录${NC}"
    echo "   请先运行: flask db init && flask db migrate -m '描述'"
    exit 1
fi

MIGRATION_COUNT=$(ls migrations/versions/*.py 2>/dev/null | grep -v __pycache__ | wc -l)
if [ $MIGRATION_COUNT -eq 0 ]; then
    echo -e "${YELLOW}⚠️  没有找到迁移文件${NC}"
    echo "   如果你修改了models.py，请先运行："
    echo "   export FLASK_APP=migrate_db.py"
    echo "   flask db migrate -m '描述变更'"
    read -p "   是否继续同步代码？(y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        exit 0
    fi
else
    echo -e "${GREEN}✅ 找到 $MIGRATION_COUNT 个迁移文件${NC}"
    echo "   最新迁移："
    ls -lt migrations/versions/*.py | grep -v __pycache__ | head -1 | awk '{print "   "$9}'
fi
echo ""

# 步骤2: 同步代码到服务器
echo -e "${YELLOW}📦 步骤2/6: 同步代码到服务器...${NC}"
if ./sync_to_server.sh; then
    echo -e "${GREEN}✅ 代码同步完成${NC}"
else
    echo -e "${RED}❌ 代码同步失败${NC}"
    exit 1
fi
echo ""

# 步骤3: 备份数据库
echo -e "${YELLOW}💾 步骤3/6: 备份生产数据库...${NC}"
BACKUP_FILE="db_backup_before_migration_$(date +%Y%m%d_%H%M%S).sql"
ssh $SERVER_HOST << ENDSSH
    set -e
    echo "正在备份数据库..."
    if sudo -u postgres pg_dump hltraining_db > /root/$BACKUP_FILE 2>/dev/null; then
        SIZE=\$(du -h /root/$BACKUP_FILE | cut -f1)
        echo "✅ 数据库已备份: /root/$BACKUP_FILE (\$SIZE)"
        
        # 压缩备份
        gzip /root/$BACKUP_FILE
        echo "✅ 备份已压缩: /root/${BACKUP_FILE}.gz"
    else
        echo "❌ 数据库备份失败！"
        exit 1
    fi
ENDSSH

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 数据库备份成功${NC}"
else
    echo -e "${RED}❌ 数据库备份失败，中止迁移${NC}"
    exit 1
fi
echo ""

# 步骤4: 查看当前数据库版本
echo -e "${YELLOW}🔍 步骤4/6: 检查服务器数据库状态...${NC}"
ssh $SERVER_HOST << 'ENDSSH'
    cd /var/www/hltraining
    source venv/bin/activate
    export FLASK_APP=migrate_db.py
    
    echo "当前数据库版本："
    flask db current || echo "尚未初始化迁移"
ENDSSH
echo ""

# 步骤5: 应用迁移
echo -e "${YELLOW}🔄 步骤5/6: 应用数据库迁移...${NC}"
read -p "确认应用迁移到生产数据库？(y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}⚠️  迁移已取消${NC}"
    exit 0
fi

ssh $SERVER_HOST << 'ENDSSH'
    set -e
    cd /var/www/hltraining
    source venv/bin/activate
    export FLASK_APP=migrate_db.py
    
    # 如果migrations目录不存在，先初始化
    if [ ! -d "migrations" ]; then
        echo "初始化迁移仓库..."
        flask db init
    fi
    
    echo "应用数据库迁移..."
    flask db upgrade
    
    echo ""
    echo "迁移后的数据库版本："
    flask db current
ENDSSH

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 数据库迁移成功${NC}"
else
    echo -e "${RED}❌ 数据库迁移失败${NC}"
    echo -e "${YELLOW}💡 可以从备份恢复:${NC}"
    echo "   ssh $SERVER_HOST 'gunzip < /root/${BACKUP_FILE}.gz | sudo -u postgres psql hltraining_db'"
    exit 1
fi
echo ""

# 步骤6: 重启服务
echo -e "${YELLOW}🔄 步骤6/6: 重启应用服务...${NC}"
ssh $SERVER_HOST 'sudo systemctl restart hltraining && sleep 2 && systemctl is-active hltraining'

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 服务重启成功${NC}"
else
    echo -e "${RED}❌ 服务重启失败${NC}"
    echo "   请检查服务状态: ssh $SERVER_HOST 'systemctl status hltraining'"
fi
echo ""

# 完成
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 数据库迁移完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📊 后续操作："
echo "   • 验证功能: 访问网站测试新功能"
echo "   • 查看日志: ssh $SERVER_HOST 'tail -f $SERVER_PATH/logs/hltraining.log'"
echo "   • 检查版本: ssh $SERVER_HOST 'cd $SERVER_PATH && source venv/bin/activate && flask db current'"
echo ""
echo "💾 备份位置: /root/${BACKUP_FILE}.gz"
echo ""
