# 3D模型生成配置指南

## 错误信息
如果看到"**腾讯云AI3D服务未配置，请联系管理员设置API密钥**"错误，说明需要配置腾讯云API密钥。

## 配置步骤

### 1. 获取腾讯云API密钥

1. 访问 [腾讯云控制台 - API密钥管理](https://console.cloud.tencent.com/cam/capi)
2. 登录腾讯云账号
3. 点击"新建密钥"创建API密钥对
4. 复制 **SecretId** 和 **SecretKey**（注意保密）

### 2. 开通AI3D服务

1. 访问 [腾讯云AI3D产品页](https://cloud.tencent.com/product/ai3d)
2. 开通"图生3D"服务
3. 根据需要选择付费套餐或免费试用

### 3. 配置环境变量

#### 方法一：使用.env文件（推荐）

1. 在项目根目录创建 `.env` 文件（如果没有的话）
2. 添加以下配置：

```env
TENCENTCLOUD_SECRET_ID=你的SecretId
TENCENTCLOUD_SECRET_KEY=你的SecretKey
```

#### 方法二：系统环境变量

**Windows PowerShell：**
```powershell
$env:TENCENTCLOUD_SECRET_ID="你的SecretId"
$env:TENCENTCLOUD_SECRET_KEY="你的SecretKey"
```

**Linux/Mac：**
```bash
export TENCENTCLOUD_SECRET_ID="你的SecretId"
export TENCENTCLOUD_SECRET_KEY="你的SecretKey"
```

### 4. 重启应用

配置完成后重启Flask应用使配置生效：

```powershell
# 停止当前应用（Ctrl+C）
# 重新运行
python run.py
```

## 验证配置

启动应用后查看日志：
- ✅ **正确配置**：`✅ 腾讯云AI3D客户端初始化成功`
- ❌ **配置错误**：`⚠️ 未找到腾讯云密钥，AI3D功能将不可用`

## 测试3D生成

1. 访问 `/create` 页面
2. 上传一张简笔画或图片
3. 点击"生成3D模型"按钮
4. 等待3D模型生成（通常需要30-60秒）

## 常见问题

### Q: 提示"腾讯云AI3D服务未配置"
**A:** 检查 `.env` 文件是否正确配置了 `TENCENTCLOUD_SECRET_ID` 和 `TENCENTCLOUD_SECRET_KEY`

### Q: 配置后仍然报错
**A:** 
1. 确认密钥格式正确（无空格、引号等）
2. 重启应用使环境变量生效
3. 检查腾讯云账户是否开通AI3D服务

### Q: 生成时间过长
**A:** 
- 3D模型生成是计算密集型任务，通常需要30-60秒
- 如果超过2分钟未完成，可能是网络或API服务问题

### Q: 如何获取免费试用
**A:** 
- 腾讯云AI3D通常提供免费试用额度
- 访问 [AI3D控制台](https://console.cloud.tencent.com/ai3d) 查看可用额度

## 安全提醒

⚠️ **密钥安全**
- 不要将 `.env` 文件提交到Git仓库
- 不要在代码中硬编码密钥
- 定期更换API密钥
- 使用子账号密钥（而非主账号密钥）

## 相关文档

- [腾讯云AI3D官方文档](https://cloud.tencent.com/document/product/1719)
- [Python SDK使用说明](https://cloud.tencent.com/document/sdk/Python)
- [API密钥管理](https://console.cloud.tencent.com/cam/capi)

## 支持与反馈

如遇到配置问题，请查看：
- 应用日志：`logs/hltraining.log`
- 后端代码：`api/hunyuan3d.py`
- 管理器代码：`managers/model3d_manager.py`
