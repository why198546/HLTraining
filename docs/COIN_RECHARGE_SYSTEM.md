# 松果币充值系统完整指南

## 📋 系统概述

本系统实现了松果币的完整管理机制，包括：
- ✅ 教师/管理员月度自动充值（每月1000币，不过期）
- ✅ 游客赠送币自动过期（30天内未使用自动失效）
- ✅ 手动充值功能（教师/管理员自助充值）
- ✅ 详细的统计和追踪

## 🏗️ 系统架构

### 数据库模型

#### 1. MonthlyTokenGrant（月度充值记录）
```python
- id: 主键
- user_id: 用户ID（教师/管理员）
- grant_year: 充值年份
- grant_month: 充值月份（1-12）
- tokens_amount: 充值金额（默认1000）
- granted_at: 充值时间戳
```

**特点：**
- 只记录教师和管理员的充值
- 每个用户每月最多一条记录
- 松果币不过期

#### 2. TokenExpiry（过期币追踪）
```python
- id: 主键
- user_id: 用户ID
- grant_log_id: 关联的赠送记录
- tokens_amount: 过期币数量
- grant_source: 来源（如'sunguo_qrcode'）
- expire_date: 过期日期
- is_expired: 是否已失效（bool）
- expired_at: 失效时间
- created_at: 记录创建时间
```

**特点：**
- 记录所有有时间限制的币
- 每条币记录都有单独的过期时间
- 系统自动检查并标记过期币

### API 端点

#### 1. 用户充值 API

**POST `/auth/recharge-tokens`** - 教师/管理员自助充值
```json
请求体：{
  "amount": 500,  // 充值金额
  "description": "补充AI图片生成用币"  // 可选说明
}

响应：{
  "success": true,
  "message": "充值成功，已增加 500 松果币",
  "new_balance": 2500,
  "old_balance": 2000,
  "amount": 500
}
```

**GET `/auth/token-balance`** - 获取余额和过期币信息
```json
响应：{
  "balance": 2500,  // 当前余额
  "role": "teacher",  // 用户角色
  "expired_today": 0,  // 今日失效的币
  "pending_expiry": [  // 待过期币列表
    {
      "id": 1,
      "amount": 50,
      "expire_date": "2025-01-26T10:30:00",
      "days_left": 3,  // 剩余天数
      "source": "sunguo_qrcode"
    }
  ]
}
```

**POST `/auth/grant-monthly-tokens`** - 管理员手动触发月度充值
```json
请求体：{
  "user_id": 123
}

响应：{
  "success": true,
  "message": "已为 张老师 充值 1000 松果币",
  "user_balance": 3000
}
```

#### 2. 统计 API

**GET `/admin/token-recharge-stats`** - 统计页面
- 显示月度充值、过期币统计、趋势图

**GET `/admin/token-recharge-stats/data`** - 获取统计数据
```json
参数：
  period: "month" 或 "year"
  year: 2025
  month: 1

响应：{
  "period": "month",
  "year": 2025,
  "month": 1,
  "monthly_grants": {
    "data": [...],
    "count": 15,
    "total": 15000
  },
  "expired_records": {
    "data": [...],
    "count": 8,
    "total": 400
  },
  "pending_expiry": {
    "data": [...],
    "count": 3
  },
  "role_stats": {
    "teacher": {"count": 10, "total": 10000},
    "admin": {"count": 5, "total": 5000}
  },
  "trend": [...]
}
```

**GET `/admin/token-recharge-stats/export`** - 导出CSV
```
参数：period, year, month
```

## 🚀 使用场景

### 场景1：教师获得月度充值

```python
# 自动流程（每月1日凌晨2:00）
teacher = User.query.get(teacher_id)
success = teacher.grant_monthly_tokens()
# 自动增加1000币，记录到MonthlyTokenGrant和TokenGrantLog
```

### 场景2：游客扫描二维码获得币

```python
# 旧方法 - 直接增加币（已弃用）
user.image_token_remaining += 50

# 新方法 - 增加带过期时间的币（推荐）
user.add_temporary_tokens(
    amount=50,
    source='sunguo_qrcode_lesson1',
    expire_days=30  # 30天后过期
)
```

### 场景3：检查过期币

```python
# 自动流程（每天凌晨1:00）
user = User.query.get(user_id)
expired_amount = user.check_token_expiry()
# 自动扣除过期币，标记记录，记录到TokenExpiry
```

### 场景4：查看松果币统计

访问 `/admin/token-recharge-stats` 页面查看：
- 本月教师/管理员充值统计
- 本月过期币统计
- 即将过期的币预警
- 二维码赠送币统计
- 充值趋势图表
- 可导出CSV报告

## 📊 统计页面功能

### 四个统计卡片
1. **月度充值** - 本期充值总数和金额
2. **过期松果币** - 本期失效的币总数
3. **7天内即将过期** - 需要关注的币
4. **二维码赠送币** - 通过扫码获得的币

### 可视化图表
- **充值趋势图** - 按日期显示充值金额变化
- **角色分布图** - 教师vs管理员充值对比

### 数据表格
- 月度充值记录 - 每条充值详情
- 过期币记录 - 每条失效币的信息
- 待过期币 - 3天内将失效的币预警
- 二维码赠送 - 最近的二维码赠送记录

## ⚙️ 定时任务配置

### 自动任务说明

```
定时任务由 APScheduler 驱动，在应用启动时自动配置：

1. 每天凌晨1:00 - 检查过期币
   - 扫描所有用户的过期币
   - 标记为失效
   - 从账户中扣除
   - 记录日志

2. 每月1日凌晨2:00 - 自动充值
   - 查询所有教师和管理员
   - 为本月未充值的用户增加1000币
   - 创建MonthlyTokenGrant记录
   - 记录到TokenGrantLog
```

### 自定义定时任务

如需调整执行时间，编辑 `utils/scheduler.py`：

```python
# 修改检查过期币的时间
scheduler.add_job(
    ...,
    trigger=CronTrigger(hour=2, minute=30),  # 改为每天凌晨2:30
    ...
)

# 修改月度充值的时间
scheduler.add_job(
    ...,
    trigger=CronTrigger(day=1, hour=3, minute=30),  # 改为每月1号凌晨3:30
    ...
)
```

## 🔄 qr_routes.py 集成

现有的二维码赠送币逻辑需要更新。在 `auth/qr_routes.py` 的 `handle_sunguo_qrcode` 函数中：

### 旧代码：
```python
if course.tokens_reward > 0:
    current_user.image_token_remaining += course.tokens_reward
    token_log = TokenGrantLog(...)
```

### 新代码：
```python
if course.tokens_reward > 0:
    # 使用新方法增加带过期时间的币
    current_user.add_temporary_tokens(
        amount=course.tokens_reward,
        source=f'sunguo_qrcode_{course.id}',
        expire_days=30
    )
```

## 📱 前端集成

### 显示松果币余额和过期币提醒

```html
<!-- 在导航栏显示余额 -->
<div class="token-badge">
    <img src="/static/images/songuo_coin/songuo_coin_inline_24x24.png" alt="松果币">
    <span id="tokenBalance">{{ current_user.image_token_remaining }}</span>
</div>

<!-- 过期币警告 -->
<div id="expiryWarning" style="display:none;" class="alert alert-warning">
    <i class="fas fa-exclamation-circle"></i>
    你有 <strong id="expiryCount">0</strong> 个松果币将在 
    <strong id="expiryDays">7</strong> 天内失效！
</div>
```

### JavaScript 更新余额

```javascript
async function updateTokenBalance() {
    const response = await fetch('/auth/token-balance');
    const data = await response.json();
    
    // 更新显示
    document.getElementById('tokenBalance').textContent = data.balance;
    
    // 显示过期币警告
    if (data.pending_expiry.length > 0) {
        const total = data.pending_expiry.reduce((sum, p) => sum + p.tokens_amount, 0);
        const minDays = Math.min(...data.pending_expiry.map(p => p.days_left));
        
        document.getElementById('expiryCount').textContent = total;
        document.getElementById('expiryDays').textContent = minDays;
        document.getElementById('expiryWarning').style.display = 'block';
    }
}

// 每30秒更新一次
setInterval(updateTokenBalance, 30000);
```

## 📈 系统流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    松果币管理系统流程                        │
└─────────────────────────────────────────────────────────────┘

1. 月度充值流程
   ├─ 每月1日凌晨2:00触发
   ├─ 查询所有teacher/admin用户
   ├─ 检查本月是否已充值
   ├─ 增加1000币 → image_token_remaining
   ├─ 创建MonthlyTokenGrant记录
   └─ 记录到TokenGrantLog

2. 游客赠送币流程
   ├─ 用户扫描二维码
   ├─ 调用user.add_temporary_tokens()
   ├─ 增加币数 → image_token_remaining
   ├─ 创建TokenExpiry记录（设定过期日期）
   └─ 记录到TokenGrantLog

3. 过期检查流程
   ├─ 每天凌晨1:00触发
   ├─ 遍历所有用户
   ├─ 调用user.check_token_expiry()
   ├─ 查找过期的TokenExpiry记录
   ├─ 标记为失效 → is_expired=True
   ├─ 扣除币数 → image_token_remaining
   └─ 记录到TokenGrantLog（负值）

4. 统计查询流程
   ├─ 访问/admin/token-recharge-stats
   ├─ 选择时间范围（月/年）
   ├─ 获取MonthlyTokenGrant数据
   ├─ 获取TokenExpiry失效记录
   ├─ 获取待过期币预警
   ├─ 生成趋势图和分布图
   └─ 支持导出CSV
```

## 🛠️ 安装和迁移

### 1. 安装依赖
```bash
pip install apscheduler
```

### 2. 运行迁移脚本
```bash
python migrate_token_system.py
```

### 3. 重启应用
```bash
# 应用会自动初始化定时任务
python run.py
```

## ✅ 验证清单

- [ ] 数据库表创建成功
- [ ] 定时任务已启动（查看启动日志）
- [ ] 访问 `/admin/token-recharge-stats` 页面可正常加载
- [ ] 可以查看月度充值统计数据
- [ ] 教师/管理员可以手动充值
- [ ] 游客二维码赠送币有过期时间

## 📝 日志记录

系统会在以下事件中产生日志记录（TokenGrantLog）：

```
grant_type 值：
- 'daily_grant'             - 每日赠送
- 'monthly_grant_teacher'   - 月度自动充值（教师）
- 'monthly_grant_admin'     - 月度自动充值（管理员）
- 'manual_recharge'         - 手动充值
- 'sunguo_qrcode'          - 扫码获得
- 'token_expired'          - 币过期
- 'qr_scan_trial'          - 体验课扫码
- 'qr_scan_formal'         - 正式课扫码
```

## 🐛 故障排除

### 问题1：定时任务未启动
**症状：** 启动日志中没有"定时任务已启动"消息
**解决：** 
```bash
pip install apscheduler
# 重启应用
```

### 问题2：过期币未被扣除
**症状：** TokenExpiry记录exists but未标记为失效
**解决：**
1. 检查定时任务是否在运行
2. 手动执行过期检查：
```python
python -c "
from app import create_app
from auth.models import User
app = create_app()
with app.app_context():
    for user in User.query.all():
        user.check_token_expiry()
"
```

### 问题3：月度充值未执行
**症状：** 月度充值记录（MonthlyTokenGrant）为空
**解决：**
1. 检查系统日期是否正确
2. 确认教师/管理员用户存在
3. 手动触发充值：
   - 访问管理员面板
   - 使用 `POST /auth/grant-monthly-tokens` API

## 💡 最佳实践

1. **定期备份** - MonthlyTokenGrant 和 TokenExpiry 表包含重要数据
2. **监控统计** - 定期查看统计页面，了解币的流向
3. **用户提醒** - 在UI中明显展示待过期币提醒
4. **审计日志** - TokenGrantLog 记录所有变化，用于审计

## 📞 支持

如有问题，请查看：
- TokenGrantLog 表中的日志记录
- 应用启动日志（查找 scheduler 相关信息）
- 数据库直接查询（检查表数据完整性）
