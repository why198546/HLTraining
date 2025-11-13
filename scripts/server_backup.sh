#!/bin/bash

###############################################################################
# HLTraining 服务器数据备份脚本
# 用途：备份生产环境的数据库和用户文件
# 建议：配置cron定时任务，每天自动备份
###############################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
BACKUP_DIR="/root/hltraining_backups"
APP_DIR="/var/www/hltraining"
DB_NAME="hltraining_db"
DB_USER="hltraining_user"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_ONLY=$(date +%Y%m%d)

# 保留天数
KEEP_DAYS=30

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  💾 HLTraining 数据备份${NC}"
echo -e "${BLUE}  时间: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查root权限
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ 此脚本需要root权限运行${NC}"
    exit 1
fi

# 创建备份目录
mkdir -p $BACKUP_DIR/{database,user_data,code}
echo -e "${GREEN}✅ 备份目录已准备: $BACKUP_DIR${NC}"
echo ""

# 1. 备份PostgreSQL数据库
echo -e "${YELLOW}📊 步骤1/4: 备份PostgreSQL数据库...${NC}"
DB_BACKUP_FILE="$BACKUP_DIR/database/hltraining_db_$TIMESTAMP.sql"

if sudo -u postgres pg_dump $DB_NAME > $DB_BACKUP_FILE 2>/dev/null; then
    DB_SIZE=$(du -h $DB_BACKUP_FILE | cut -f1)
    echo -e "${GREEN}✅ 数据库备份完成${NC}"
    echo "   文件: $DB_BACKUP_FILE"
    echo "   大小: $DB_SIZE"
    
    # 压缩数据库备份
    gzip $DB_BACKUP_FILE
    echo -e "${GREEN}✅ 数据库备份已压缩: ${DB_BACKUP_FILE}.gz${NC}"
else
    echo -e "${RED}❌ 数据库备份失败${NC}"
    echo -e "${YELLOW}⚠️  继续备份其他内容...${NC}"
fi
echo ""

# 2. 备份用户上传文件
echo -e "${YELLOW}📁 步骤2/4: 备份用户数据...${NC}"
USER_DATA_BACKUP="$BACKUP_DIR/user_data/user_data_$DATE_ONLY.tar.gz"

# 检查是否今天已经备份过
if [ -f "$USER_DATA_BACKUP" ]; then
    echo -e "${BLUE}ℹ️  今天已有用户数据备份，跳过...${NC}"
else
    tar -czf $USER_DATA_BACKUP \
        -C $APP_DIR \
        uploads \
        creation_sessions \
        models \
        static/gallery \
        2>/dev/null || true
    
    if [ -f "$USER_DATA_BACKUP" ]; then
        USER_SIZE=$(du -h $USER_DATA_BACKUP | cut -f1)
        echo -e "${GREEN}✅ 用户数据备份完成${NC}"
        echo "   文件: $USER_DATA_BACKUP"
        echo "   大小: $USER_SIZE"
    else
        echo -e "${YELLOW}⚠️  用户数据备份失败或无数据${NC}"
    fi
fi
echo ""

# 3. 备份代码（轻量级备份）
echo -e "${YELLOW}📝 步骤3/4: 备份代码和配置...${NC}"
CODE_BACKUP="$BACKUP_DIR/code/code_$TIMESTAMP.tar.gz"

tar -czf $CODE_BACKUP \
    -C $APP_DIR \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='uploads' \
    --exclude='creation_sessions' \
    --exclude='models' \
    --exclude='static/gallery' \
    . 2>/dev/null || true

if [ -f "$CODE_BACKUP" ]; then
    CODE_SIZE=$(du -h $CODE_BACKUP | cut -f1)
    echo -e "${GREEN}✅ 代码备份完成${NC}"
    echo "   文件: $CODE_BACKUP"
    echo "   大小: $CODE_SIZE"
fi
echo ""

# 4. 清理旧备份
echo -e "${YELLOW}🗑️  步骤4/4: 清理旧备份（保留${KEEP_DAYS}天）...${NC}"

# 清理旧数据库备份
OLD_DB_COUNT=$(find $BACKUP_DIR/database -name "*.sql.gz" -mtime +$KEEP_DAYS -type f | wc -l)
if [ $OLD_DB_COUNT -gt 0 ]; then
    find $BACKUP_DIR/database -name "*.sql.gz" -mtime +$KEEP_DAYS -type f -delete
    echo -e "${GREEN}✅ 已删除 $OLD_DB_COUNT 个旧数据库备份${NC}"
else
    echo -e "${BLUE}ℹ️  无需清理数据库备份${NC}"
fi

# 清理旧用户数据备份
OLD_DATA_COUNT=$(find $BACKUP_DIR/user_data -name "*.tar.gz" -mtime +$KEEP_DAYS -type f | wc -l)
if [ $OLD_DATA_COUNT -gt 0 ]; then
    find $BACKUP_DIR/user_data -name "*.tar.gz" -mtime +$KEEP_DAYS -type f -delete
    echo -e "${GREEN}✅ 已删除 $OLD_DATA_COUNT 个旧用户数据备份${NC}"
else
    echo -e "${BLUE}ℹ️  无需清理用户数据备份${NC}"
fi

# 清理旧代码备份（保留最近5个）
CODE_COUNT=$(ls -1 $BACKUP_DIR/code/*.tar.gz 2>/dev/null | wc -l)
if [ $CODE_COUNT -gt 5 ]; then
    ls -1t $BACKUP_DIR/code/*.tar.gz | tail -n +6 | xargs rm -f
    REMOVED=$((CODE_COUNT - 5))
    echo -e "${GREEN}✅ 已删除 $REMOVED 个旧代码备份（保留最近5个）${NC}"
else
    echo -e "${BLUE}ℹ️  无需清理代码备份${NC}"
fi
echo ""

# 5. 备份摘要
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 备份完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📊 备份统计："
echo "   数据库备份: $(ls -1 $BACKUP_DIR/database/*.sql.gz 2>/dev/null | wc -l) 个文件"
echo "   用户数据备份: $(ls -1 $BACKUP_DIR/user_data/*.tar.gz 2>/dev/null | wc -l) 个文件"
echo "   代码备份: $(ls -1 $BACKUP_DIR/code/*.tar.gz 2>/dev/null | wc -l) 个文件"
echo ""
echo "💾 总备份大小: $(du -sh $BACKUP_DIR | cut -f1)"
echo ""
echo "📁 备份位置: $BACKUP_DIR"
echo ""

# 6. 生成备份日志
LOG_FILE="$BACKUP_DIR/backup.log"
echo "$(date '+%Y-%m-%d %H:%M:%S') - 备份完成" >> $LOG_FILE
echo "   数据库: $(ls -lh $BACKUP_DIR/database/hltraining_db_$TIMESTAMP.sql.gz 2>/dev/null | awk '{print $5}' || echo 'N/A')" >> $LOG_FILE
echo "   用户数据: $(ls -lh $USER_DATA_BACKUP 2>/dev/null | awk '{print $5}' || echo 'N/A')" >> $LOG_FILE
echo "   代码: $(ls -lh $CODE_BACKUP 2>/dev/null | awk '{print $5}' || echo 'N/A')" >> $LOG_FILE
echo "" >> $LOG_FILE

echo -e "${YELLOW}💡 提示：${NC}"
echo "   查看备份列表: ls -lh $BACKUP_DIR/database/"
echo "   恢复数据库: gunzip < backup.sql.gz | sudo -u postgres psql $DB_NAME"
echo "   恢复用户数据: tar -xzf user_data.tar.gz -C $APP_DIR"
echo ""
