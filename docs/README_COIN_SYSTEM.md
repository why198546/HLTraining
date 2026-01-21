# 🎯 松果币充值系统 - 使用说明和总结

## 📋 系统已实现功能概览

### ✅ 已完成的功能清单

#### 1. 教师/管理员月度自动充值
- 📅 每月 1 日凌晨 2:00 自动执行
- 💰 每个教师/管理员自动增加 1000 松果币
- 📊 充值不过期，可永久使用
- 📝 完整的充值记录和日志追踪
- 🔄 本月已充值的用户自动跳过，防止重复充值

#### 2. 游客赠送币过期管理
- ⏱️ 通过二维码获得的币，30 天内未使用自动失效
- 🔍 系统每天凌晨 1:00 自动检查过期币
- 💔 过期币自动从用户账户中扣除
- 📍 每条币都有独立的过期时间追踪
- 📋 完整的失效记录和过期历史

#### 3. 手动充值功能
- 🔐 仅教师和管理员可以使用
- 💻 简单易用的 API 接口
- ⚠️ 单次充值金额限制（最多 10000）
- 📝 可选的充值原因说明
- ✅ 充值成功后立即更新余额

#### 4. 余额和过期币查询
- 📊 查看当前松果币余额
- ⏰ 显示即将过期的币列表
- 🔔 提醒用户待过期币的天数
- 📌 显示每条币的来源和过期日期

#### 5. 详细统计分析页面
- 📈 月度充值统计和趋势图
- 🎯 四个关键指标卡片
- 📊 角色分布分析
- 🔍 支持按月份/年份筛选
- 💾 支持导出 CSV 报告
- 📋 详细的数据表格展示

#### 6. 自动定时任务
- ⏰ 基于 APScheduler 的后台定时任务
- 🔄 应用重启后自动恢复
- 📝 详细的执行日志
- 🛡️ 包含错误处理和异常捕获

## 🚀 部署指南

### 第一步：安装依赖（1 分钟）

```bash
# 方式1：使用 pip
pip install apscheduler

# 方式2：更新整个 requirements.txt
pip install -r requirements.txt
```

### 第二步：运行数据库迁移（1 分钟）

```bash
python migrate_token_system.py
```

**预期输出：**
```
🔄 开始数据库迁移...
✅ 数据库迁移成功！

已创建的新表：
  - monthly_token_grants: 月度充值记录表
  - token_expiries: 过期币追踪表

✓ monthly_token_grants 表结构：
    - id: INTEGER
    - user_id: INTEGER
    - grant_year: INTEGER
    - ...
```

### 第三步：启动应用（1 分钟）

```bash
python run.py
```

**检查启动日志：**

查看是否有：
```
✅ 定时任务已启动
   - 每天凌晨1:00 检查过期币
   - 每月1号凌晨2:00 为教师/管理员充值
```

### 第四步：验证系统（可选）

```bash
# 运行完整性检查
python verify_system.py
```

## 📱 使用场景

### 场景 1：教师查看余额和充值

```javascript
// 前端代码
async function checkBalance() {
    const response = await fetch('/auth/token-balance');
    const data = await response.json();
    
    console.log(`当前余额: ${data.balance}`);
    console.log(`待过期币: ${data.pending_expiry.length}条`);
    
    if (data.pending_expiry.length > 0) {
        data.pending_expiry.forEach(item => {
            console.log(`  - ${item.amount}币, 还剩${item.days_left}天失效`);
        });
    }
}

async function rechargeTokens(amount) {
    const response = await fetch('/auth/recharge-tokens', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            amount: amount,
            description: '补充 AI 图片生成用币'
        })
    });
    
    const data = await response.json();
    if (data.success) {
        alert(`成功充值 ${amount} 币，新余额: ${data.new_balance}`);
    }
}
```

### 场景 2：管理员查看月度充值统计

1. 登录管理员账户
2. 访问 `http://localhost/admin/token-recharge-stats`
3. 选择要查看的时间范围（月份或年份）
4. 点击"查询"按钮
5. 可以：
   - 查看四个关键指标
   - 查看趋势图表
   - 切换不同的表格标签
   - 导出 CSV 报告

### 场景 3：自动月度充值（后台自动执行）

系统会在每月 1 日凌晨 2:00 自动执行：

```python
# 自动流程（无需手动操作）
1. 查询所有教师和管理员
2. 检查本月是否已充值
3. 如果未充值，增加 1000 币
4. 记录充值日志
5. 通知（可选）
```

### 场景 4：游客币自动过期（后台自动执行）

系统会在每天凌晨 1:00 自动执行：

```python
# 自动流程（无需手动操作）
1. 查找所有过期的币
2. 标记为失效
3. 从用户账户中扣除
4. 记录失效日志
5. 发送通知（可选）
```

## 🔧 API 文档

### 1. 自助充值 API

**请求：**
```
POST /auth/recharge-tokens
Content-Type: application/json

{
    "amount": 500,                      // 必需：充值金额（1-10000）
    "description": "补充图片生成币"     // 可选：充值原因
}
```

**响应（成功）：**
```json
{
    "success": true,
    "message": "充值成功，已增加 500 松果币",
    "new_balance": 2500,
    "old_balance": 2000,
    "amount": 500
}
```

**响应（失败）：**
```json
{
    "success": false,
    "message": "只有教师和管理员可以充值松果币"
}
```

### 2. 查询余额 API

**请求：**
```
GET /auth/token-balance
```

**响应：**
```json
{
    "balance": 2500,                    // 当前余额
    "role": "teacher",                  // 用户角色
    "expired_today": 50,                // 今日失效的币
    "pending_expiry": [                 // 待过期币列表
        {
            "id": 1,
            "amount": 50,
            "expire_date": "2025-01-26T10:30:00",
            "days_left": 3,
            "source": "sunguo_qrcode"
        },
        {
            "id": 2,
            "amount": 100,
            "expire_date": "2025-01-27T10:30:00",
            "days_left": 4,
            "source": "sunguo_qrcode_lesson1"
        }
    ]
}
```

### 3. 手动月度充值 API（管理员）

**请求：**
```
POST /admin/grant-monthly-tokens
Content-Type: application/json

{
    "user_id": 123  // 必需：教师/管理员的用户ID
}
```

**响应（成功）：**
```json
{
    "success": true,
    "message": "已为 张老师 充值 1000 松果币",
    "user_balance": 3000
}
```

**响应（已充值）：**
```json
{
    "success": false,
    "message": "张老师 本月已充值过，无需重复充值"
}
```

### 4. 获取统计数据 API

**请求：**
```
GET /admin/token-recharge-stats/data?period=month&year=2025&month=1
```

**参数：**
- `period`: "month" 或 "year"
- `year`: 2025
- `month`: 1-12（当 period=month 时）

**响应：**
```json
{
    "period": "month",
    "year": 2025,
    "month": 1,
    "monthly_grants": {
        "data": [...],          // 充值记录列表
        "count": 15,            // 充值人数
        "total": 15000          // 充值总额
    },
    "expired_records": {
        "data": [...],          // 过期币记录
        "count": 8,
        "total": 400
    },
    "pending_expiry": {
        "data": [...],          // 待过期币
        "count": 3
    },
    "role_stats": {             // 按角色统计
        "teacher": {"count": 10, "total": 10000},
        "admin": {"count": 5, "total": 5000}
    },
    "trend": [                  // 趋势数据
        {"date": "2025-01-01", "count": 5, "total": 5000},
        ...
    ]
}
```

### 5. 导出统计数据 API

**请求：**
```
GET /admin/token-recharge-stats/export?period=month&year=2025&month=1
```

**响应：**
- 返回 CSV 文件下载
- 文件名：`token_recharge_2025_01.csv`

## 📊 数据库表说明

### monthly_token_grants（月度充值记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| grant_year | INTEGER | 充值年份 |
| grant_month | INTEGER | 充值月份 |
| tokens_amount | INTEGER | 充值金额 |
| granted_at | DATETIME | 充值时间 |

### token_expiries（过期币追踪）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| grant_log_id | INTEGER | 关联的赠送记录ID |
| tokens_amount | INTEGER | 币的数量 |
| grant_source | VARCHAR | 币的来源 |
| expire_date | DATETIME | 过期日期 |
| is_expired | BOOLEAN | 是否已失效 |
| expired_at | DATETIME | 失效时间 |
| created_at | DATETIME | 记录创建时间 |

### token_grant_logs（所有充值日志）

新增的 grant_type 值：
- `monthly_grant_teacher` - 月度自动充值（教师）
- `monthly_grant_admin` - 月度自动充值（管理员）
- `manual_recharge` - 手动充值
- `sunguo_qrcode` - 扫码赠送（已有，现在带过期时间）
- `token_expired` - 币过期

## ⚙️ 系统配置

### 修改月度充值金额

编辑 `auth/models.py`，在 `User.grant_monthly_tokens()` 方法中：

```python
# 修改前
tokens_amount = 1000

# 修改后
tokens_amount = 2000  # 改为 2000 币
```

### 修改过期天数

编辑 `auth/routes.py` 或 `auth/qr_routes.py`，找到 `add_temporary_tokens()` 调用：

```python
# 修改前
user.add_temporary_tokens(amount, source, expire_days=30)

# 修改后
user.add_temporary_tokens(amount, source, expire_days=60)  # 改为 60 天
```

### 修改定时任务时间

编辑 `utils/scheduler.py`：

```python
# 修改过期检查时间（默认每天凌晨 1:00）
scheduler.add_job(
    ...,
    trigger=CronTrigger(hour=2, minute=30),  # 改为凌晨 2:30
    ...
)

# 修改月度充值时间（默认每月 1 日凌晨 2:00）
scheduler.add_job(
    ...,
    trigger=CronTrigger(day=1, hour=3, minute=30),  # 改为 3:30
    ...
)
```

## 🔐 权限管理

| 功能 | 游客 | 学生 | 教师 | 管理员 |
|------|------|------|------|--------|
| 查看余额 | ✅ | ✅ | ✅ | ✅ |
| 手动充值 | ❌ | ❌ | ✅ | ✅ |
| 手动触发月度充值 | ❌ | ❌ | ❌ | ✅ |
| 访问统计页面 | ❌ | ❌ | ❌ | ✅ |

## 🎓 最佳实践

### 1. 定期备份数据
定期备份以下表：
- monthly_token_grants
- token_expiries
- token_grant_logs

### 2. 监控过期币
- 定期查看统计页面
- 关注待过期币警告
- 在 UI 中明显显示过期币提醒

### 3. 审计日志
- TokenGrantLog 记录所有变化
- 定期导出和存档
- 用于审计和分析

### 4. 用户教育
- 告诉用户游客币有 30 天有效期
- 在余额显示中提醒待过期币
- 发送邮件提醒即将过期

## 🆘 故障排除

### 问题 1：定时任务未执行

**症状：** 凌晨没有自动充值或过期检查

**解决方案：**
```bash
# 检查是否安装了 apscheduler
pip show apscheduler

# 重启应用
python run.py

# 查看启动日志中是否有 "定时任务已启动" 消息
```

### 问题 2：游客币未过期

**症状：** TokenExpiry 记录存在但未标记失效

**解决方案：**
```python
# 手动触发过期检查
from app import create_app
from auth.models import User

app = create_app()
with app.app_context():
    for user in User.query.all():
        expired = user.check_token_expiry()
        if expired > 0:
            print(f"{user.nickname}: -{expired}")
```

### 问题 3：月度充值不工作

**症状：** MonthlyTokenGrant 表为空

**解决方案：**
```python
# 手动执行月度充值
from app import create_app
from auth.models import User

app = create_app()
with app.app_context():
    teachers = User.query.filter(User.role.in_(['teacher', 'admin'])).all()
    for teacher in teachers:
        success = teacher.grant_monthly_tokens()
        print(f"{teacher.nickname}: {'✅' if success else '❌'}")
```

## 📞 获取帮助

查看以下文档：

1. [COIN_RECHARGE_SYSTEM.md](COIN_RECHARGE_SYSTEM.md) - 完整系统文档
2. [COIN_RECHARGE_QUICK_START.md](COIN_RECHARGE_QUICK_START.md) - 快速开始指南
3. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - 部署检查清单
4. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - 实现总结

## 🎉 系统特色

- ✅ **完全自动化** - 无需人工干预
- ✅ **灵活配置** - 轻松修改参数
- ✅ **完整追踪** - 每笔都有记录
- ✅ **详细统计** - 数据分析和报告
- ✅ **安全可靠** - 权限验证和错误处理
- ✅ **易于扩展** - 清晰的代码结构

---

**现在可以开始使用了！** 🚀

**步骤：**
```bash
1. pip install apscheduler
2. python migrate_token_system.py
3. python run.py
```

有任何问题，请参考相关文档或查看应用日志。
