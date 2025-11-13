#!/bin/bash

# 用户管理脚本 - 列出和删除用户

DB_PATH="instance/hltraining.db"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  📋 HLTraining 用户管理${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# 列出所有用户
echo -e "${YELLOW}📊 当前用户列表:${NC}\n"
sqlite3 $DB_PATH << 'EOFSQL'
.mode column
.headers on
SELECT 
    id as ID,
    username as 用户名,
    parent_email as 家长邮箱,
    CASE 
        WHEN is_verified = 1 THEN '✅已验证'
        ELSE '⏳未验证'
    END as 状态,
    datetime(created_at, 'localtime') as 创建时间
FROM users
ORDER BY id;
EOFSQL

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# 提示输入
read -p "请输入要删除的用户ID或用户名 (输入q退出): " input

if [ "$input" = "q" ] || [ "$input" = "Q" ]; then
    echo -e "\n${GREEN}✅ 已取消操作${NC}"
    exit 0
fi

# 查询用户信息
echo -e "\n${YELLOW}🔍 查询用户信息...${NC}\n"
user_info=$(sqlite3 $DB_PATH << EOFSQL
.mode list
.separator '|'
SELECT id, username, parent_email FROM users 
WHERE id = '$input' OR username = '$input';
EOFSQL
)

if [ -z "$user_info" ]; then
    echo -e "${RED}❌ 未找到该用户${NC}"
    exit 1
fi

# 解析用户信息
IFS='|' read -r user_id username parent_email <<< "$user_info"

echo -e "${YELLOW}找到用户:${NC}"
echo -e "  ID: ${BLUE}$user_id${NC}"
echo -e "  用户名: ${BLUE}$username${NC}"
echo -e "  邮箱: ${BLUE}$parent_email${NC}\n"

# 确认删除
read -p "确认删除该用户？(y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "\n${GREEN}✅ 已取消删除${NC}"
    exit 0
fi

# 执行删除
echo -e "\n${YELLOW}🗑️  正在删除用户...${NC}\n"

sqlite3 $DB_PATH << EOFSQL
-- 删除验证记录（如果表存在）
DELETE FROM parent_verification WHERE child_id = $user_id;

-- 删除用户
DELETE FROM users WHERE id = $user_id;

-- 确认删除
.mode column
.headers on
SELECT '✅ 用户已删除' as 结果;
SELECT COUNT(*) as 剩余用户数 FROM users WHERE id = $user_id;
EOFSQL

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 删除成功！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
