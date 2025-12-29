# 🎯 松果币系统 - 快速参考卡片

## 📌 快速部署命令

```bash
# 1. 安装依赖（1分钟）
pip install apscheduler

# 2. 数据库迁移（1分钟）
python migrate_token_system.py

# 3. 启动应用（1分钟）
python run.py
```

✅ **完成！** 查看日志中的 "✅ 定时任务已启动" 消息

---

## 🔗 核心 API 速查

### 查询余额
```bash
GET /auth/token-balance
# 返回：{ balance, role, expired_today, pending_expiry[] }
```

### 手动充值
```bash
POST /auth/recharge-tokens
# Body: { amount: 100-10000, description: "optional" }
```

### 统计分析
```
访问：http://localhost:5000/admin/token-recharge-stats
或 GET /admin/token-recharge-stats/data?period=month&year=2025&month=1
```

### 手动触发月度充值（管理员）
```bash
POST /admin/grant-monthly-tokens
# Body: { user_id: 123 }
```

---

## 📊 系统特性一览

| 特性 | 说明 | 时间 |
|------|------|------|
| 月度自动充值 | 教师/管理员每月 +1000 币 | 每月1日 2:00 |
| 游客币过期 | 30天未使用自动失效 | 每天1:00 |
| 手动充值 | 教师/管理员自助充值 | 随时 |
| 统计分析 | 完整的数据分析和导出 | 随时 |

---

## 🗂️ 文件导航

| 文件 | 用途 |
|------|------|
| [README_COIN_SYSTEM.md](README_COIN_SYSTEM.md) | 📖 完整使用手册 |
| [COIN_RECHARGE_SYSTEM.md](COIN_RECHARGE_SYSTEM.md) | 🔧 技术架构文档 |
| [COIN_RECHARGE_QUICK_START.md](COIN_RECHARGE_QUICK_START.md) | ⚡ 5分钟快速开始 |
| [DEPLOYMENT_FINAL.md](DEPLOYMENT_FINAL.md) | 📋 部署清单和验证 |
| [auth/models.py](auth/models.py) | 💾 数据库模型 |
| [auth/routes.py](auth/routes.py) | 🔌 用户 API 接口 |
| [auth/admin_routes.py](auth/admin_routes.py) | 👨‍💼 管理员接口 |
| [utils/scheduler.py](utils/scheduler.py) | ⏰ 定时任务 |
| [templates/admin/token_recharge_stats.html](templates/admin/token_recharge_stats.html) | 📊 统计页面 |

---

## 🆘 快速故障排除

**问题：定时任务没有启动**
```bash
python -c "import apscheduler; print('✅ APScheduler OK')"
```

**问题：月度充值未执行**
```python
# 手动执行
python -c "
from app import create_app
from utils.scheduler import grant_monthly_tokens
app = create_app()
with app.app_context():
    grant_monthly_tokens(app)
"
```

**问题：查看所有日志**
```bash
tail -f logs/app.log
```

---

## 📈 关键数据库查询

```sql
-- 查看本月充值情况
SELECT user_id, SUM(tokens_amount) FROM monthly_token_grants 
WHERE grant_year=2025 AND grant_month=1 GROUP BY user_id;

-- 查看待过期币
SELECT * FROM token_expiries 
WHERE is_expired=0 AND expire_date < datetime('now');

-- 查看按角色的充值统计
SELECT u.role, COUNT(*), SUM(m.tokens_amount) 
FROM monthly_token_grants m 
JOIN user u ON m.user_id = u.id 
GROUP BY u.role;
```

---

## 🎓 常见场景

### 场景：教师想查询自己的币和即将过期的币
```javascript
const data = await fetch('/auth/token-balance').then(r => r.json());
console.log(`余额: ${data.balance}, 待过期: ${data.pending_expiry.length}条`);
```

### 场景：管理员想查看本月充值统计
1. 访问 `http://localhost:5000/admin/token-recharge-stats`
2. 选择月份，点击查询
3. 点击导出按钮下载 CSV

### 场景：系统管理员想确认定时任务运行
```bash
grep "定时任务" logs/app.log
# 应该看到：✅ 定时任务已启动
```

### 场景：手动为某个教师充值本月的币
```bash
curl -X POST http://localhost:5000/admin/grant-monthly-tokens \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123}'
```

---

## 💡 系统优势

✅ **全自动** - 无需人工干预，定时执行  
✅ **可追溯** - 每笔交易都有完整记录  
✅ **灵活配置** - 轻松修改参数  
✅ **数据完整** - 支持导出和审计  
✅ **可靠稳定** - 错误自动处理和恢复  

---

## 📞 获取更多帮助

- **技术问题** → 查看 [COIN_RECHARGE_SYSTEM.md](COIN_RECHARGE_SYSTEM.md)
- **部署问题** → 查看 [DEPLOYMENT_FINAL.md](DEPLOYMENT_FINAL.md)
- **快速入门** → 查看 [COIN_RECHARGE_QUICK_START.md](COIN_RECHARGE_QUICK_START.md)
- **使用说明** → 查看 [README_COIN_SYSTEM.md](README_COIN_SYSTEM.md)

---

**最后更新：** 2025年1月  
**版本：** 1.0  
**状态：** ✅ 已完成，可部署
