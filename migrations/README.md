# 数据库迁移历史

本目录记录所有数据库结构变更，用于生产环境部署时参考。

## 迁移文件命名规范
格式：`YYYY-MM-DD_描述.md`

## 迁移记录

| 日期 | 文件 | 描述 | 状态 |
|------|------|------|------|
| 2026-02-03 | [2026-02-03_DATABASE_SYNC_REPORT.md](./2026-02-03_DATABASE_SYNC_REPORT.md) | 添加 feedback_templates 字段到 users 表 | ✅ 已完成 |
| 2025-12-21 | [2025-12-21_add_canvas_project_fields.md](./2025-12-21_add_canvas_project_fields.md) | 为 canvas_projects 表添加 project_type, width, height, last_opened_at 字段 | ✅ 已完成 |

## 迁移工具

### 验证工具
- `verify_database.py` - 完整验证数据库结构
  ```bash
  python migrations/verify_database.py
  ```

### 最新迁移
- `add_feedback_templates_column.py` - 添加教师AI点评模板字段
  ```bash
  python migrations/add_feedback_templates_column.py
  ```

## 使用说明

### 开发环境
开发环境使用 SQLite，可以直接运行迁移脚本：
```bash
python migrations/add_feedback_templates_column.py
```

### 生产环境
1. 备份数据库
2. 参考对应的迁移文档执行SQL语句
3. 验证迁移结果
4. 重启应用

### 注意事项
- 始终先在测试环境验证迁移脚本
- 生产环境迁移前必须备份数据库
- 迁移完成后验证应用功能
- 准备回滚方案以防万一
