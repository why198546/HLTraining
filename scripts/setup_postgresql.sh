#!/bin/bash

###############################################################################
# HLTraining PostgreSQL数据库初始化脚本
# 用于在服务器上创建数据库和用户
###############################################################################

set -e  # 遇到错误立即退出

echo "🗄️  开始初始化PostgreSQL数据库..."

# 配置变量
DB_NAME="hltraining_db"
DB_USER="hltraining_user"
DB_PASSWORD="hl_training_2025_secure_password"  # 请修改为安全密码！

# 检查是否以postgres用户运行
if [ "$USER" != "postgres" ] && [ "$EUID" -ne 0 ]; then
    echo "❌ 此脚本需要以root或postgres用户运行"
    echo "   使用: sudo bash setup_postgresql.sh"
    exit 1
fi

echo "📋 数据库配置："
echo "   数据库名: $DB_NAME"
echo "   用户名: $DB_USER"
echo ""

# 切换到postgres用户执行SQL命令
sudo -u postgres psql << EOF
-- 创建用户
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
        RAISE NOTICE '✅ 用户 $DB_USER 创建成功';
    ELSE
        RAISE NOTICE '⏭️  用户 $DB_USER 已存在';
    END IF;
END
\$\$;

-- 创建数据库
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER ENCODING ''UTF8'''
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- 连接到新数据库并授予schema权限
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

-- 设置默认权限（未来创建的表也有权限）
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 用于文本搜索

\q
EOF

echo ""
echo "✅ PostgreSQL数据库初始化完成！"
echo ""
echo "📝 数据库连接信息："
echo "   DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "⚠️  重要提醒："
echo "   1. 请将上述连接字符串添加到服务器的 .env 文件中"
echo "   2. 请立即修改数据库密码以确保安全！"
echo "   3. 修改密码命令："
echo "      sudo -u postgres psql -c \"ALTER USER $DB_USER WITH PASSWORD '新密码';\""
echo ""
echo "🧪 测试数据库连接："
echo "   PGPASSWORD='$DB_PASSWORD' psql -U $DB_USER -h localhost -d $DB_NAME -c 'SELECT version();'"
echo ""
