#!/bin/bash

###############################################################################
# 从服务器获取最新生成时使用的完整提示词
###############################################################################

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SERVER_HOST="47.95.214.47"
SSH_KEY="$HOME/.ssh/wordpress_openssh"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  📋 获取服务器最新生成的提示词${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}🔍 正在从服务器获取最新日志...${NC}"
echo ""

# 获取最新的Vision模式提示词（完整版）
echo -e "${GREEN}=== Vision提取模式 - 完整Prompt ===${NC}"
ssh -i "$SSH_KEY" root@"$SERVER_HOST" "grep '📝 完整Prompt (全文):' /var/www/hltraining/logs/error.log | tail -n 1" | sed 's/.*📝 完整Prompt (全文): //'

echo ""
echo -e "${GREEN}=== Vision提取模式 - Prompt长度 ===${NC}"
ssh -i "$SSH_KEY" root@"$SERVER_HOST" "grep '📋 提示词长度:' /var/www/hltraining/logs/error.log | tail -n 1" | sed 's/.* //'

echo ""
echo -e "${GREEN}=== 传统模式 - 完整提示词 ===${NC}"
ssh -i "$SSH_KEY" root@"$SERVER_HOST" "grep '完整提示词:' /var/www/hltraining/logs/error.log | tail -n 1" | sed 's/.*完整提示词: //'

echo ""
echo -e "${GREEN}=== 最新5次生成的模式选择 ===${NC}"
ssh -i "$SSH_KEY" root@"$SERVER_HOST" "grep 'Vision提取模式:' /var/www/hltraining/logs/error.log | tail -n 5"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  ✅ 提示词获取完成${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
