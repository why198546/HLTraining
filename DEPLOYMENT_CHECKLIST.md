# 松果币充值系统 - 部署和测试清单

## ✅ 部署前检查

### 依赖检查
- [ ] 已安装 `apscheduler` 库
  ```bash
  pip install apscheduler
  ```

### 代码检查
- [ ] 确认 `utils/scheduler.py` 存在
- [ ] 确认 `migrate_token_system.py` 存在
- [ ] 确认 `auth/models.py` 包含 `MonthlyTokenGrant` 和 `TokenExpiry` 模型
- [ ] 确认 `auth/routes.py` 包含充值 API 端点
- [ ] 确认 `auth/admin_routes.py` 包含统计 API
- [ ] 确认 `templates/admin/token_recharge_stats.html` 存在
- [ ] 确认 `app/__init__.py` 调用了 `init_scheduler(app)`

## 🚀 部署步骤

### 步骤1：安装依赖
```bash
pip install -r requirements.txt
# 或单独安装
pip install apscheduler
```

### 步骤2：运行数据库迁移
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
```

**验证迁移成功：**
```python
python -c "
from app import create_app
from auth.models import db

app = create_app()
with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'monthly_token_grants' in tables and 'token_expiries' in tables:
        print('✅ 数据库表创建成功')
    else:
        print('❌ 数据库表未创建')
"
```

### 步骤3：启动应用
```bash
python run.py
```

**查看启动日志：**
- 应该看到 `✅ 定时任务已启动`
- 应该看到两行任务信息

### 步骤4：验证系统

#### 验证1：检查定时任务
```python
python -c "
import sys
from app import create_app

app = create_app()
# 应该在启动日志中看到定时任务信息
"
```

#### 验证2：检查统计页面
1. 以管理员身份登录
2. 访问 `http://localhost/admin/token-recharge-stats`
3. 确认页面加载成功（即使没有数据也OK）

#### 验证3：测试充值 API
```bash
# 先登录获取 session，然后：
curl -X POST http://localhost/auth/recharge-tokens \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "description": "test recharge"}'

# 预期响应：
# {
#   "success": true,
#   "message": "充值成功，已增加 100 松果币",
#   "new_balance": 1100,
#   "old_balance": 1000,
#   "amount": 100
# }
```

#### 验证4：测试余额查询 API
```bash
curl http://localhost/auth/token-balance \
  -H "Authorization: Bearer YOUR_TOKEN"

# 预期响应：
# {
#   "balance": 1100,
#   "role": "teacher",
#   "expired_today": 0,
#   "pending_expiry": []
# }
```

## 📊 测试场景

### 场景1：教师自助充值
1. 以教师身份登录
2. 访问个人中心或专用充值页面
3. 输入充值金额（如 500）
4. 提交充值
5. **验证：**
   - 页面显示"充值成功"
   - 余额增加 500
   - 数据库 `token_grant_logs` 表新增一条记录（grant_type='manual_recharge'）

### 场景2：游客赠送币过期
1. 以游客身份登录（或访客身份）
2. 扫描二维码（赠送 50 币）
3. **验证：**
   - 余额增加 50
   - 在 `token_expiries` 表中新增一条记录
   - 该记录的 `expire_date` 是 30 天后

4. 等待过期检查运行或手动触发：
   ```python
   from app import create_app
   from auth.models import User
   
   app = create_app()
   with app.app_context():
       user = User.query.get(user_id)
       expired = user.check_token_expiry()
       print(f"过期币数: {expired}")
   ```
5. **验证：**
   - 过期币被从余额中扣除
   - `token_expiries` 记录被标记为 `is_expired=True`
   - `token_grant_logs` 新增一条负值记录

### 场景3：月度自动充值
1. 创建或更新一个教师用户
2. 确保当前月份没有充值记录
3. 手动触发或等待凌晨 2:00：
   ```python
   from app import create_app
   from auth.models import User
   
   app = create_app()
   with app.app_context():
       teacher = User.query.filter_by(role='teacher').first()
       success = teacher.grant_monthly_tokens()
       if success:
           print(f"✅ {teacher.nickname} 月度充值成功")
       else:
           print(f"❌ 月度充值失败")
   ```
4. **验证：**
   - `monthly_token_grants` 表新增一条记录
   - 教师余额增加 1000
   - `token_grant_logs` 新增一条记录（grant_type='monthly_grant_teacher'）

### 场景4：查看统计数据
1. 以管理员身份登录
2. 访问 `/admin/token-recharge-stats`
3. 选择时间范围（月份或年份）
4. 点击"查询"按钮
5. **验证：**
   - 四个统计卡片显示数据
   - 趋势图正确显示
   - 表格显示相关记录
   - 可以切换选项卡查看不同的表格

### 场景5：导出数据
1. 在统计页面
2. 点击"导出CSV"按钮
3. **验证：**
   - 下载一个 CSV 文件
   - 文件名格式：`token_recharge_2025_01.csv`
   - 文件内容包含充值记录

## 🔍 故障排查

### 问题1：定时任务未启动
**症状：** 应用启动日志中没有"✅ 定时任务已启动"

**排查步骤：**
1. 检查 `apscheduler` 是否已安装
   ```bash
   pip show apscheduler
   ```
2. 检查 `utils/scheduler.py` 是否存在
3. 检查 `app/__init__.py` 是否导入了 `init_scheduler`
4. 查看应用启动日志是否有错误信息

**解决方案：**
```bash
# 重新安装依赖
pip install apscheduler
# 重启应用
python run.py
```

### 问题2：统计页面加载失败
**症状：** `/admin/token-recharge-stats` 返回 404 或 500 错误

**排查步骤：**
1. 检查 `templates/admin/token_recharge_stats.html` 是否存在
2. 检查 `admin_routes.py` 是否有相关路由
3. 查看应用日志中的错误信息

**解决方案：**
```bash
# 确认文件存在
ls -la templates/admin/token_recharge_stats.html

# 重启应用
python run.py
```

### 问题3：过期币未被自动扣除
**症状：** TokenExpiry 记录存在但未被标记为失效

**排查步骤：**
1. 检查定时任务是否在运行
2. 检查过期检查函数是否正确执行
3. 手动触发过期检查：
   ```python
   from datetime import datetime, timedelta
   from app import create_app
   from auth.models import User, TokenExpiry, db
   
   app = create_app()
   with app.app_context():
       # 获取所有过期的币
       expired = TokenExpiry.query.filter(
           TokenExpiry.is_expired == False,
           TokenExpiry.expire_date <= datetime.utcnow()
       ).all()
       
       print(f"找到 {len(expired)} 条过期币")
       
       # 手动检查一个用户
       user = User.query.first()
       if user:
           amount = user.check_token_expiry()
           print(f"用户 {user.nickname} 过期币: {amount}")
   ```

### 问题4：月度充值不执行
**症状：** MonthlyTokenGrant 表为空，用户月度余额未增加

**排查步骤：**
1. 检查系统日期和时间是否正确
2. 检查教师/管理员用户是否存在
3. 手动触发充值：
   ```python
   from app import create_app
   from auth.models import User
   
   app = create_app()
   with app.app_context():
       teachers = User.query.filter(User.role.in_(['teacher', 'admin'])).all()
       for teacher in teachers:
           success = teacher.grant_monthly_tokens()
           print(f"{teacher.nickname}: {'✅' if success else '❌'}")
   ```

## 📈 性能测试

### 并发充值测试
```python
import threading
from app import create_app
from auth.models import User, db

app = create_app()

def recharge_user(user_id):
    with app.app_context():
        user = User.query.get(user_id)
        if user:
            user.image_token_remaining += 100
            db.session.commit()

# 创建 10 个线程并发充值
threads = []
for i in range(10):
    t = threading.Thread(target=recharge_user, args=(1,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("✅ 并发测试完成")
```

### 大数据集过期检查测试
```python
from app import create_app
from auth.models import User
import time

app = create_app()

with app.app_context():
    start = time.time()
    
    users = User.query.all()
    for user in users:
        user.check_token_expiry()
    
    elapsed = time.time() - start
    print(f"✅ 检查 {len(users)} 个用户耗时 {elapsed:.2f} 秒")
```

## 📋 验收标准

### 功能验收
- [ ] 教师/管理员可以自助充值
- [ ] 充值成功后余额正确更新
- [ ] 月度自动充值在每月 1 日执行
- [ ] 游客赠送的币在 30 天后自动失效
- [ ] 过期币自动从余额中扣除
- [ ] 统计页面显示所有数据
- [ ] 可以导出 CSV 报告

### 性能验收
- [ ] 充值响应时间 < 1 秒
- [ ] 过期检查（1000 用户）< 10 秒
- [ ] 统计查询（1 年数据）< 2 秒
- [ ] 页面加载时间 < 3 秒

### 稳定性验收
- [ ] 定时任务持续运行无崩溃
- [ ] 大并发充值无数据库锁死
- [ ] 应用重启后定时任务正常恢复
- [ ] 数据库连接异常后自动重试

## 🎉 上线前最后检查

```bash
# 1. 运行迁移脚本
python migrate_token_system.py

# 2. 启动应用
python run.py &

# 3. 等待 5 秒
sleep 5

# 4. 检查日志
tail -f /path/to/app.log | grep "定时任务"

# 5. 访问统计页面
curl http://localhost/admin/token-recharge-stats

# 6. 检查数据库
python -c "
from app import create_app
from auth.models import db

app = create_app()
with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print('✅ 数据库就绪' if 'monthly_token_grants' in tables else '❌ 数据库未就绪')
"
```

## 📞 紧急联系

如部署出现问题：
1. 查看完整文档：[COIN_RECHARGE_SYSTEM.md](COIN_RECHARGE_SYSTEM.md)
2. 查看快速指南：[COIN_RECHARGE_QUICK_START.md](COIN_RECHARGE_QUICK_START.md)
3. 检查应用日志文件
4. 检查数据库连接状态

---

**部署日期：** ____________________
**部署人员：** ____________________
**验收状态：** ☐ 通过  ☐ 需要修改
**备注：** _______________________________________________
