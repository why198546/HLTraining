# 📧 邮件配置指南

## 问题诊断
邮件验证功能当前处于**模拟模式**，因为缺少必要的SMTP配置。用户无法收到真实的验证邮件。

## 配置方法

### 1. Gmail SMTP 配置（推荐）

在 `.env` 文件中添加以下配置：

```bash
# 邮件服务配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-gmail-address@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=AI创意工坊 <your-gmail-address@gmail.com>
```

### 2. Gmail 应用密码设置步骤

1. **启用两步验证**
   - 登录 Google 账户：https://myaccount.google.com/
   - 转到"安全性" → "两步验证"
   - 按照指引启用

2. **生成应用密码**
   - 在"安全性"页面，找到"应用密码"
   - 选择"邮件"和"其他(自定义名称)"
   - 输入"AI创意工坊"作为应用名称
   - 复制生成的16位密码

3. **配置环境变量**
   ```bash
   MAIL_USERNAME=your-gmail-address@gmail.com
   MAIL_PASSWORD=abcd efgh ijkl mnop  # 应用密码，非Gmail登录密码
   ```

### 3. 其他邮件服务商配置

#### 163邮箱
```bash
MAIL_SERVER=smtp.163.com
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=your-username@163.com
MAIL_PASSWORD=your-authorization-code
```

#### QQ邮箱
```bash
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-qq-number@qq.com
MAIL_PASSWORD=your-authorization-code
```

### 4. 配置验证

配置完成后重启应用：
```bash
cd /Users/hongyuwang/code/HLTraining
source .venv/bin/activate
python app.py
```

测试邮件发送：
- 访问注册页面
- 填写家长邮箱
- 检查是否收到验证邮件

## 当前状态

✅ **已实现功能**
- 邮件服务架构完整
- 模拟模式工作正常
- 验证流程完整

⚠️  **需要配置**
- SMTP服务器凭据
- 邮件发送权限

📧 **模拟模式日志示例**
```
[2025-10-25 11:26:33,359] INFO in email_service: 邮件发送模拟 - 收件人: 409100323@qq.com
[2025-10-25 11:26:33,359] INFO in email_service: 验证码: 595244
[2025-10-25 11:26:33,359] INFO in email_service: 验证链接: http://localhost:8080/auth/parent-verify/f1de15b8-3c80-45a3-aac5-0a3bff7889f5
```

## 安全提醒

- 🔐 不要将真实邮箱密码用于应用密码
- 🛡️ 使用专门的应用密码
- 📝 不要将邮件凭据提交到代码仓库
- 🔒 定期更换应用密码