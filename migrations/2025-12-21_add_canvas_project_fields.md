# 数据库迁移记录 - 2025-12-21

## 变更概述
为 `canvas_projects` 表添加新字段，支持项目类型区分和画布尺寸记录。

## 影响的表
- `canvas_projects`

## 新增字段

### 1. project_type
- **类型**: VARCHAR(20)
- **默认值**: 'infinite'
- **说明**: 项目类型，区分手绘项目(sketch)和创意项目(infinite)
- **可为空**: 否

### 2. width
- **类型**: INTEGER
- **默认值**: 512
- **说明**: 画布宽度
- **可为空**: 否

### 3. height
- **类型**: INTEGER
- **默认值**: 512
- **说明**: 画布高度
- **可为空**: 否

### 4. last_opened_at
- **类型**: DATETIME
- **默认值**: NULL
- **说明**: 最后打开时间
- **可为空**: 是

## SQL迁移脚本

### SQLite (开发环境)
```sql
-- 添加 project_type 字段
ALTER TABLE canvas_projects 
ADD COLUMN project_type VARCHAR(20) DEFAULT 'infinite';

-- 添加 width 字段
ALTER TABLE canvas_projects 
ADD COLUMN width INTEGER DEFAULT 512;

-- 添加 height 字段
ALTER TABLE canvas_projects 
ADD COLUMN height INTEGER DEFAULT 512;

-- 添加 last_opened_at 字段
ALTER TABLE canvas_projects 
ADD COLUMN last_opened_at DATETIME;

-- 更新现有记录的 project_type 为 'infinite'
UPDATE canvas_projects 
SET project_type = 'infinite' 
WHERE project_type IS NULL;
```

### MySQL/MariaDB (生产环境)
```sql
-- 添加 project_type 字段
ALTER TABLE canvas_projects 
ADD COLUMN project_type VARCHAR(20) DEFAULT 'infinite' NOT NULL;

-- 添加 width 字段
ALTER TABLE canvas_projects 
ADD COLUMN width INT DEFAULT 512 NOT NULL;

-- 添加 height 字段
ALTER TABLE canvas_projects 
ADD COLUMN height INT DEFAULT 512 NOT NULL;

-- 添加 last_opened_at 字段
ALTER TABLE canvas_projects 
ADD COLUMN last_opened_at DATETIME NULL;

-- 更新现有记录
UPDATE canvas_projects 
SET project_type = 'infinite' 
WHERE project_type IS NULL OR project_type = '';
```

### PostgreSQL (如果使用)
```sql
-- 添加 project_type 字段
ALTER TABLE canvas_projects 
ADD COLUMN project_type VARCHAR(20) DEFAULT 'infinite' NOT NULL;

-- 添加 width 字段
ALTER TABLE canvas_projects 
ADD COLUMN width INTEGER DEFAULT 512 NOT NULL;

-- 添加 height 字段
ALTER TABLE canvas_projects 
ADD COLUMN height INTEGER DEFAULT 512 NOT NULL;

-- 添加 last_opened_at 字段
ALTER TABLE canvas_projects 
ADD COLUMN last_opened_at TIMESTAMP NULL;

-- 更新现有记录
UPDATE canvas_projects 
SET project_type = 'infinite' 
WHERE project_type IS NULL;
```

## 部署步骤

### 1. 备份数据库
```bash
# MySQL
mysqldump -u username -p database_name > backup_before_migration_20251221.sql

# PostgreSQL
pg_dump -U username database_name > backup_before_migration_20251221.sql

# SQLite
cp instance/hltraining.db instance/hltraining_backup_20251221.db
```

### 2. 执行迁移脚本
可以使用项目提供的自动迁移脚本：
```bash
python scripts/add_project_type_column.py
```

或者手动执行上述SQL语句。

### 3. 验证迁移
```sql
-- 检查表结构
DESC canvas_projects;  -- MySQL
\d canvas_projects;    -- PostgreSQL
PRAGMA table_info(canvas_projects);  -- SQLite

-- 检查数据
SELECT id, project_id, project_type, width, height, last_opened_at 
FROM canvas_projects 
LIMIT 5;
```

### 4. 重启应用
```bash
./run.ps1 restart
# 或
systemctl restart hltraining  # 如果使用 systemd
```

## 回滚方案

如果迁移出现问题，可以回滚：

```sql
-- SQLite 不支持 DROP COLUMN，需要重建表
-- 建议恢复备份

-- MySQL/MariaDB
ALTER TABLE canvas_projects DROP COLUMN project_type;
ALTER TABLE canvas_projects DROP COLUMN width;
ALTER TABLE canvas_projects DROP COLUMN height;
ALTER TABLE canvas_projects DROP COLUMN last_opened_at;

-- PostgreSQL
ALTER TABLE canvas_projects DROP COLUMN project_type;
ALTER TABLE canvas_projects DROP COLUMN width;
ALTER TABLE canvas_projects DROP COLUMN height;
ALTER TABLE canvas_projects DROP COLUMN last_opened_at;
```

## 相关代码变更

### 模型更新
- `auth/models.py`: CanvasProject 类
  - 添加了新字段定义
  - 更新了 `__init__` 方法支持新参数
  - 更新了 `to_dict()` 方法包含新字段

### 路由更新
- `app/routes/canvas.py`
  - 更新了项目保存逻辑
  - 添加了项目标题自动生成功能
  - 改进了项目列表查询（兼容旧数据）

### 前端更新
- `templates/canvas_sketch.html`
- `templates/canvas_infinite.html`
- `templates/canvas_projects.html`
  - 支持项目类型区分
  - 添加自动标题生成
  - 改进用户体验

## 测试检查清单

- [ ] 创建新的手绘项目（project_type='sketch'）
- [ ] 创建新的创意项目（project_type='infinite'）
- [ ] 保存项目并验证所有字段正确保存
- [ ] 加载已有项目并验证数据完整性
- [ ] 验证项目列表正确区分两种类型
- [ ] 验证自动标题生成功能
- [ ] 验证项目重命名功能
- [ ] 验证项目删除功能
- [ ] 检查现有旧数据是否能正常访问

## 注意事项

1. **向后兼容**: 新字段都有默认值，确保现有数据不受影响
2. **数据类型**: 根据实际数据库类型调整SQL语句
3. **索引**: 如果 project_type 字段查询频繁，建议添加索引：
   ```sql
   CREATE INDEX idx_canvas_projects_type ON canvas_projects(project_type);
   ```
4. **性能**: 在大数据量情况下，建议在低峰期执行迁移

## 联系信息
- 迁移日期: 2025-12-21
- 执行人: [待填写]
- 数据库版本: [待填写]
