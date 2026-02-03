#!/bin/bash

###############################################################################
# 实时监控服务器生成日志，显示完整提示词
###############################################################################

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SERVER_HOST="47.95.214.47"
SSH_KEY="$HOME/.ssh/wordpress_openssh"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  👀 实时监控服务器生成日志${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📡 连接到服务器，实时显示图像生成日志...${NC}"
echo -e "${GREEN}提示：按 Ctrl+C 退出监控${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 实时监控日志，过滤关键信息
ssh -i "$SSH_KEY" root@"$SERVER_HOST" "tail -f /var/www/hltraining/logs/error.log" | \
  grep --line-buffered -E "(===|🎨|📝|📋|🔬|🔧|Vision提取|完整Prompt|使用的完整提示词|提示词长度|开始生成|生成成功|生成失败)" | \
  while IFS= read -r line; do
    # 根据内容添加颜色
    if [[ "$line" == *"完整Prompt"* ]] || [[ "$line" == *"使用的完整提示词"* ]]; then
      echo -e "${GREEN}$line${NC}"
    elif [[ "$line" == *"Vision提取"* ]]; then
      echo -e "${BLUE}$line${NC}"
    elif [[ "$line" == *"成功"* ]]; then
      echo -e "${GREEN}$line${NC}"
    elif [[ "$line" == *"失败"* ]]; then
      echo -e "${RED}$line${NC}"
    elif [[ "$line" == *"==="* ]]; then
      echo -e "${YELLOW}$line${NC}"
    else
      echo "$line"
    fi
  done
