#!/bin/bash

###############################################################################
# 从服务器获取最近一小时生成的图片
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
SSH_KEY="$HOME/.ssh/wordpress_openssh"
SSH_CMD="ssh -i $SSH_KEY -o StrictHostKeyChecking=no"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  📸 从服务器获取最近一小时生成的图片${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查SSH连接
echo -e "${YELLOW}📡 测试服务器连接...${NC}"
if eval "$SSH_CMD $SERVER_USER@$SERVER_HOST 'echo 连接成功'" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 服务器连接正常${NC}"
else
    echo -e "${RED}❌ 无法连接到服务器 $SERVER_HOST${NC}"
    exit 1
fi
echo ""

# 创建临时目录存放下载的图片
DOWNLOAD_DIR="downloads/recent_images_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DOWNLOAD_DIR"
echo -e "${YELLOW}📁 本地保存目录: $DOWNLOAD_DIR${NC}"
echo ""
˚∑
# 步骤1: 查找最近一小时内生成的图片
echo -e "${YELLOW}🔍 步骤1: 查找最近一小时内的图片...${NC}"
echo ""
# 使用find命令查找过去60分钟内修改的图片
TEMP_LIST=$(mktemp)
eval "$SSH_CMD $SERVER_USER@$SERVER_HOST" << ENDSSH > "$TEMP_LIST"
find /var/www/hltraining/uploads -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" \) -mmin -60 2>/dev/null | sort
find /var/www/hltraining/static/uploads -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" \) -mmin -60 2>/dev/null | sort
find /var/www/hltraining/static/gallery -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" \) -mmin -60 2>/dev/null | sort
ENDSSH

# 统计找到的文件数量
FILE_COUNT=$(grep -c . "$TEMP_LIST" || echo 0)
echo -e "${BLUE}找到 $FILE_COUNT 个图片文件${NC}"
echo ""

if [ "$FILE_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  过去一小时内没有找到生成的图片${NC}"
    rm "$TEMP_LIST"
    exit 0
fi

# 显示找到的文件列表
echo -e "${BLUE}📋 找到的图片列表:${NC}"
cat "$TEMP_LIST" | while read -r file; do
    echo "   • $(basename "$file")"
done
echo ""

# 步骤2: 下载图片
echo -e "${YELLOW}📥 步骤2: 下载图片到本地...${NC}"
echo ""

# 建立临时目录用于rsync
TEMP_FILE_LIST=$(mktemp)
cat "$TEMP_LIST" > "$TEMP_FILE_LIST"

# 使用rsync下载所有找到的文件
while IFS= read -r remote_file; do
    if [ -z "$remote_file" ]; then
        continue
    fi
    
    # 去掉路径前缀，保留相对路径
    relative_path="${remote_file#/var/www/hltraining/}"
    local_file="$DOWNLOAD_DIR/$relative_path"
    
    # 创建本地目录
    mkdir -p "$(dirname "$local_file")"
    
    # 下载文件
    if rsync -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" -a \
        "$SERVER_USER@$SERVER_HOST:$remote_file" "$local_file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $(basename "$local_file")"
    else
        echo -e "${RED}✗${NC} $(basename "$local_file") - 下载失败"
    fi
done < "$TEMP_FILE_LIST"

echo ""

# 步骤3: 汇总信息
echo -e "${YELLOW}📊 步骤3: 汇总信息...${NC}"
echo ""

DOWNLOADED_COUNT=$(find "$DOWNLOAD_DIR" -type f | wc -l)
TOTAL_SIZE=$(du -sh "$DOWNLOAD_DIR" | awk '{print $1}')

echo -e "${GREEN}✅ 下载完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "📊 统计信息:"
echo -e "   • 总文件数: ${YELLOW}$DOWNLOADED_COUNT${NC}"
echo -e "   • 总大小: ${YELLOW}$TOTAL_SIZE${NC}"
echo -e "   • 保存位置: ${YELLOW}$DOWNLOAD_DIR${NC}"
echo ""
echo -e "💡 提示："
echo -e "   • 在 Finder 中打开: ${YELLOW}open $DOWNLOAD_DIR${NC}"
echo -e "   • 查看文件夹: ${YELLOW}ls -lh $DOWNLOAD_DIR${NC}"
echo ""

# 清理临时文件
rm -f "$TEMP_LIST" "$TEMP_FILE_LIST"
