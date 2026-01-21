# 松果币生成监控功能完成

## 已完成的功能

### 1. 数据库表 `token_grant_logs`
记录所有松果币的生成来源：
- `daily_grant`: 每日自动赠送
- `qr_scan_trial`: 二维码扫描（体验课）
- `qr_scan_formal`: 二维码扫描（正式课）
- `admin_manual`: 管理员手动增加
- `teacher_manual`: 教师手动增加
- `purchase`: 购买获得（预留）
- `activity_reward`: 活动奖励（预留）
- `refund`: 退款补偿（预留）

### 2. 自动记录日志
所有松果币增加的地方都会自动记录到 `token_grant_logs` 表：
- ✅ 每日自动赠送 (`User.grant_daily_tokens()`)
- ✅ 二维码扫描赠送 (`User.upgrade_to_trial_student()`, `User.upgrade_to_formal_student()`)
- ✅ 管理员手动增加 (`admin_routes.add_user_tokens()`)
- ✅ 教师手动增加 (`routes.add_student_tokens()`)

### 3. 统计API
`GET /admin/token-grant/stats?period=day|week|month|year`

返回数据：
```json
{
    "success": true,
    "period": "day",
    "total_stats": {
        "total_granted": 5610,     // 总生成松果币数
        "total_count": 150,        // 总生成次数
        "user_count": 7            // 受益用户数
    },
    "trend_data": [...],           // 趋势数据（按日期和来源）
    "source_distribution": [...],  // 来源分布统计
    "recent_grants": [...]         // 最近20条记录
}
```

### 4. 前端UI
在 `/admin/token-usage` 页面新增了 **「生成监控」** Tab，包含：

#### 统计卡片
- 总生成松果币数
- 生成次数
- 受益用户数

#### 可视化图表
- 📈 **松果币生成趋势图**：按时间和来源分类的折线图
- 🥧 **生成来源分布图**：饼图显示各来源占比
- 📊 **来源统计详情**：列表显示每个来源的详细数据

#### 详细记录表
显示最近20条生成记录，包括：
- 时间
- 用户信息
- 生成来源
- 松果币数量
- 操作者（如果是手动增加）
- 描述信息

## 访问方式

1. 登录管理后台
2. 进入「松果币监控」页面：`http://localhost:8088/admin/token-usage`
3. 点击顶部的「生成监控」Tab

## 测试数据

已通过 `test_token_grant.py` 生成了150条测试记录，包括最近30天的各种来源的松果币生成记录。

## 数据库迁移

使用 `create_token_grant_table.py` 创建了 `token_grant_logs` 表，包含字段：
- id, user_id, grant_type, tokens_granted, created_at
- description, operator_id, operator_name
- related_id, related_info

## 注意事项

- 现有系统中，所有松果币增加操作都已自动记录日志
- 历史数据不会自动生成记录，只记录新的操作
- 正式课二维码扫描不直接赠送松果币（tokens_granted=0），而是解锁每日30个的权限
