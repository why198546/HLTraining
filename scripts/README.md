# 脚本工具目录

本目录包含项目的各类脚本工具。

## 部署脚本

- `deploy.sh` - 完整部署脚本
- `sync_to_server.sh` - 同步代码到服务器
- `migrate_to_server.sh` - 迁移到服务器
- `server_backup.sh` - 服务器备份脚本
- `server_update.sh` - 服务器更新脚本

## 数据库脚本

- `migrate_db.py` - 数据库迁移
- `setup_postgresql.sh` - PostgreSQL安装配置
- `update_artwork_schema.py` - 更新作品表结构
- `update_user_schema.py` - 更新用户表结构

## 维护脚本

- `cleanup_empty_artworks.py` - 清理空作品
- `cleanup_project.py` - 清理项目文件
- `manage_users.sh` - 用户管理工具

## 使用说明

所有脚本应从项目根目录执行：

```bash
# 示例：同步到服务器
./scripts/sync_to_server.sh

# 示例：管理用户
./scripts/manage_users.sh
```
