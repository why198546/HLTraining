# 松果币充值系统 - 快速开始指南

## 5分钟快速启用

### 第一步：安装依赖（1分钟）
```bash
pip install apscheduler
```

### 第二步：运行数据库迁移（1分钟）
```bash
python migrate_token_system.py
```

预期输出：
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
    - grant_month: INTEGER
    - tokens_amount: INTEGER
    - granted_at: DATETIME
    ...
```

### 第三步：重启应用（1分钟）
```bash
# 关闭当前应用（Ctrl+C）
# 重新启动
python run.py
```

查看启动日志中是否有：
```
✅ 定时任务已启动
   - 每天凌晨1:00 检查过期币
   - 每月1号凌晨2:00 为教师/管理员充值
```

### 第四步：验证系统（2分钟）

#### 验证1：访问统计页面
- 打开浏览器访问 `http://localhost:80/admin/token-recharge-stats`
- 应该看到四个统计卡片和趋势图
- 如果显示"暂无数据"是正常的（首次运行）

#### 验证2：测试自助充值
```bash
# 以教师身份登录，然后：
# 使用 JavaScript 或 API 测试工具
curl -X POST http://localhost:80/auth/recharge-tokens \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "description": "test"}'
```

#### 验证3：检查数据库表
```bash
python -c "
from app import create_app
from auth.models import db, MonthlyTokenGrant, TokenExpiry

app = create_app()
with app.app_context():
    # 查看表是否存在
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print('数据库中的表：')
    for table in sorted(tables):
        if 'token' in table.lower():
            print(f'  ✓ {table}')
"
```

## 核心功能一览表

| 功能 | 位置 | 说明 |
|------|------|------|
| 月度自动充值 | 每月1日凌晨2:00 | 教师/管理员自动获得1000币 |
| 过期币检查 | 每天凌晨1:00 | 检查并失效30天未使用的币 |
| 自助充值 | `/auth/recharge-tokens` | 教师/管理员可随时充值 |
| 查看余额 | `/auth/token-balance` | 查看余额和待过期币 |
| 统计查看 | `/admin/token-recharge-stats` | 管理员查看详细统计 |

## 使用示例

### 示例1：教师自助充值

**前端界面代码：**
```html
<div class="recharge-form">
    <h2>充值松果币</h2>
    <input type="number" id="rechargeAmount" placeholder="输入充值金额" min="1" max="10000">
    <textarea id="rechargeDesc" placeholder="充值原因（可选）"></textarea>
    <button onclick="rechargeTokens()">确认充值</button>
</div>

<script>
async function rechargeTokens() {
    const amount = document.getElementById('rechargeAmount').value;
    const description = document.getElementById('rechargeDesc').value;
    
    const response = await fetch('/auth/recharge-tokens', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount, description })
    });
    
    const data = await response.json();
    if (data.success) {
        alert(`✅ ${data.message}\n新余额: ${data.new_balance}`);
    } else {
        alert(`❌ 充值失败: ${data.message}`);
    }
}
</script>
```

### 示例2：游客赠送币

**Python代码（在qr_routes.py中）：**
```python
# 当用户扫描二维码时
if course.tokens_reward > 0:
    current_user.add_temporary_tokens(
        amount=course.tokens_reward,
        source=f'sunguo_qrcode_{course.id}',
        expire_days=30  # 30天后失效
    )
    # 自动记录日志和创建过期追踪记录
```

### 示例3：手动检查过期币

```python
from app import create_app
from auth.models import User

app = create_app()
with app.app_context():
    # 为指定用户检查过期币
    user = User.query.get(user_id)
    expired_amount = user.check_token_expiry()
    print(f"用户 {user.nickname} 过期币数: {expired_amount}")
    
    # 为所有用户检查
    for user in User.query.all():
        expired = user.check_token_expiry()
        if expired > 0:
            print(f"  - {user.nickname}: -{expired}")
```

## 常见问题

### Q1: 定时任务不运行怎么办？
**A:** 检查应用启动日志，如果没有"定时任务已启动"消息：
1. 确保已安装 `apscheduler`
2. 检查 `utils/scheduler.py` 文件是否存在
3. 重启应用

### Q2: 可以改变充值金额或过期天数吗？
**A:** 可以，修改以下代码：

```python
# 修改月度充值金额（models.py User.grant_monthly_tokens方法）
tokens_amount = 2000  # 改为2000

# 修改过期天数（models.py User.add_temporary_tokens方法）
expire_date = datetime.utcnow() + timedelta(days=60)  # 改为60天
```

### Q3: 如何导出充值数据？
**A:** 在统计页面右上角有"导出CSV"按钮，可直接导出当前筛选的数据。

### Q4: 充值记录保存在哪？
**A:** 有三个表记录：
- `monthly_token_grants` - 月度充值记录
- `token_expiries` - 过期币追踪
- `token_grant_logs` - 所有充值日志

### Q5: 可以给多个用户同时充值吗？
**A:** 可以，但需要在管理后台逐个操作，或者写脚本批量操作：

```python
from auth.models import User, db

app = create_app()
with app.app_context():
    # 给所有教师增加500币
    for teacher in User.query.filter_by(role='teacher'):
        teacher.image_token_remaining += 500
    db.session.commit()
    print("✅ 已为所有教师增加500币")
```

## 系统设计特点

✅ **自动化**
- 月度自动充值（无需手动操作）
- 自动过期检查（无需手动标记）

✅ **灵活**
- 支持手动充值（教师/管理员自助）
- 支持不同的过期时间配置

✅ **可追踪**
- 完整的日志记录
- TokenGrantLog记录所有交易
- TokenExpiry记录每条币的生命周期

✅ **可视化**
- 详细的统计页面
- 趋势图表
- 角色分布分析

✅ **可审计**
- 所有操作都有记录
- 可导出CSV报告
- 支持按时间段查询

## 📊 统计页面亮点

1. **四个关键指标** - 一目了然
2. **趋势图表** - 直观展示充值变化
3. **角色分布** - 对比教师和管理员
4. **详细表格** - 查看每条记录
5. **导出功能** - 支持CSV下载
6. **灵活筛选** - 按月份或年份统计

## 🔒 安全特性

- 只有教师和管理员可以使用自助充值
- 所有操作都被记录在案
- 充值金额有上限限制（单次最多10000）
- 支持按时间段审计

## 📈 后续扩展建议

1. **充值套餐** - 不同数量的预设套餐
2. **充值历史** - 用户个人查看自己的充值历史
3. **充值统计** - 每个用户的充值趋势
4. **过期提醒** - 发送邮件/短信提醒用户即将过期的币
5. **批量操作** - 支持批量充值多个用户
6. **充值审批** - 管理员审批用户申请的充值

---

**需要帮助？** 查看完整文档：[COIN_RECHARGE_SYSTEM.md](COIN_RECHARGE_SYSTEM.md)
