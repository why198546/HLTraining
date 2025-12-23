# 开发工作流程规范

## ⚠️ 重要经验教训

### 问题记录 (2025-12-23)
**问题**：实现新功能后立即同步到生产服务器，未经本地充分测试

**影响**：
- 可能将未经验证的代码部署到生产环境
- 增加线上bug风险
- 打断本地调试流程

**改进措施**：
✅ 新功能开发 → 本地调试 → 确认可用 → 请用户确认 → 再同步服务器

## 正确的开发流程

### 1. 本地开发阶段
```bash
# 启动本地Flask服务器
python run.py
# 或使用VS Code任务
# 任务: "启动Flask开发服务器"
```

访问本地环境：
- 主页: http://localhost:8088
- 松果课堂: http://localhost:8088/sunguo-class
- 人物课: http://localhost:8088/sunguo-class/character

### 2. 本地测试
- [ ] 功能是否正常工作
- [ ] UI显示是否正确
- [ ] 交互逻辑是否流畅
- [ ] 控制台无JavaScript错误
- [ ] 响应式布局是否正常

### 3. 确认上线
**只有在以下情况下才同步到生产服务器：**
- ✅ 本地测试完全通过
- ✅ 用户明确表示"可以上线了"或"同步到服务器"
- ✅ 功能已达到预期效果

### 4. 同步到生产环境
```bash
# 方式一：使用同步脚本（推荐）
./scripts/sync_to_server.sh

# 方式二：手动同步
rsync -avz --delete \
  --exclude='.env' \
  --exclude='*.db' \
  --exclude='uploads/' \
  . root@47.95.214.47:/var/www/hltraining/

# 重启服务
ssh -i ~/.ssh/wordpress_openssh root@47.95.214.47 \
  'systemctl restart hltraining && systemctl reload nginx'
```

## 开发环境 vs 生产环境

### 本地开发环境
- 地址: http://localhost:8088
- 用途: 开发、调试、测试新功能
- 特点: 
  - Debug模式开启
  - 代码修改后自动重载
  - 详细错误信息
  - 可以断点调试

### 生产环境
- 地址: http://47.95.214.47 (或域名)
- 用途: 对外提供服务
- 特点:
  - 使用Gunicorn + Nginx
  - 关闭Debug模式
  - 错误日志记录
  - 性能优化

## Git工作流程

### 当前分支策略
- `main`: 稳定的生产版本
- `beta`: 当前开发分支
- 功能分支: 根据需要创建

### 提交规范
```bash
# 功能开发完成后提交
git add .
git commit -m "feat: 添加人物特征选择器功能"

# 推送到远程
git push origin beta

# 合并到main（经过测试后）
git checkout main
git merge beta
git push origin main
```

## 常用命令速查

### 本地开发
```bash
# 启动本地服务器
python run.py

# 查看Python环境
which python
pip list

# 安装依赖
pip install -r requirements.txt

# 检查代码语法
python -m py_compile app.py
```

### 生产环境操作
```bash
# 查看服务状态
ssh -i ~/.ssh/wordpress_openssh root@47.95.214.47 \
  'systemctl status hltraining'

# 查看日志
ssh -i ~/.ssh/wordpress_openssh root@47.95.214.47 \
  'tail -f /var/www/hltraining/logs/hltraining.log'

# 重启服务
ssh -i ~/.ssh/wordpress_openssh root@47.95.214.47 \
  'systemctl restart hltraining && systemctl reload nginx'
```

## 调试技巧

### 前端调试
1. 打开浏览器开发者工具 (F12)
2. Console标签查看JavaScript错误
3. Network标签查看API请求
4. Elements标签检查CSS样式

### 后端调试
1. 查看Flask控制台输出
2. 使用print()或logging记录日志
3. 检查 `logs/hltraining.log`

### 常见问题排查
- **静态文件未更新**: 清除浏览器缓存 (Ctrl+Shift+R)
- **API调用失败**: 检查Network标签，查看返回的错误信息
- **数据库问题**: 检查 `instance/hltraining.db` 权限和结构

## 最佳实践总结

### ✅ 应该做的
- 在本地充分测试后再部署
- 提交前检查代码是否有语法错误
- 记录重要的配置变更
- 保持代码简洁易读
- 添加必要的注释

### ❌ 不应该做的
- ❌ **未经测试就同步到生产环境**
- ❌ 在生产服务器上直接修改代码
- ❌ 提交敏感信息（密钥、密码）到Git
- ❌ 忽略错误日志
- ❌ 跳过备份步骤

## 紧急回滚方案

如果生产环境出现问题：

```bash
# 1. 连接到服务器
ssh -i ~/.ssh/wordpress_openssh root@47.95.214.47

# 2. 查看备份
ls -lh /var/backups/hltraining/

# 3. 恢复数据库（如需要）
cp /var/backups/hltraining/hltraining_YYYYMMDD_HHMMSS.db \
   /var/www/hltraining/instance/hltraining.db

# 4. 回滚代码（使用Git）
cd /var/www/hltraining
git log --oneline  # 查看提交历史
git reset --hard <commit-hash>  # 回滚到指定版本

# 5. 重启服务
systemctl restart hltraining
```

---

**建立日期**: 2025-12-23  
**最后更新**: 2025-12-23  
**重要程度**: 🔴 高 - 必须遵守
