# HLTraining v1.0 - Windows 安装使用说明

## 🎯 简介
HLTraining 是一个专为10-14岁儿童设计的AI培训网站，支持：
- AI图片生成（基于Google Gemini 2.5 Flash Image）
- 图片智能调整和编辑
- 3D模型生成（基于腾讯云AI3D）
- 作品画廊展示

## 📦 安装方法

### 方法一：运行可执行文件（推荐）
1. 下载发布的 `HLTraining-v1.0-Windows.zip` 文件
2. 解压到任意目录
3. 双击 `HLTraining.exe` 即可启动
4. 等待2秒后浏览器会自动打开网站

### 方法二：Python源码运行
如果您的系统已安装Python 3.8+：

1. 下载并解压源码
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行应用：
   ```bash
   python run_app.py
   ```

## 🔧 配置说明

### API密钥配置
为了使用AI功能，需要配置以下API密钥：

1. **Google Gemini API**（图片生成）
   - 复制 `.env.example` 为 `.env`
   - 在 `.env` 中设置 `GEMINI_API_KEY=your_api_key`
   - 获取地址：https://ai.google.dev/

2. **腾讯云AI3D API**（3D模型生成）
   - 在 `.env` 中设置：
     ```
     AI3D_SECRET_ID=your_secret_id
     AI3D_SECRET_KEY=your_secret_key
     ```
   - 获取地址：https://cloud.tencent.com/

### 网络要求
- 需要互联网连接以访问AI服务
- 首次运行会创建必要的文件夹

## 🚀 使用方法

1. **启动应用**
   - Windows：双击 `HLTraining.exe`
   - Python：运行 `python run_app.py`

2. **访问网站**
   - 自动打开：http://127.0.0.1:8080
   - 手动访问：在浏览器中输入上述地址

3. **开始创作**
   - 点击"开始创作"按钮
   - 输入创意描述或上传参考图片
   - 等待AI生成图片
   - 可选择调整图片
   - 生成3D模型

4. **查看作品**
   - 点击"作品画廊"查看所有创作
   - 支持3D模型交互展示

## 🛠️ 故障排除

### 常见问题

1. **启动失败**
   - 检查是否有其他程序占用8080端口
   - 确保Python版本为3.8或更高

2. **AI功能不可用**
   - 检查`.env`文件中的API密钥是否正确
   - 确保网络连接正常

3. **图片生成失败**
   - 检查Google Gemini API密钥
   - 确认API额度未用完

4. **3D模型生成失败**
   - 检查腾讯云AI3D API配置
   - 确认云服务余额充足

### 日志查看
- 控制台窗口会显示详细的运行日志
- 错误信息会显示在控制台中

## 📞 技术支持

如遇到问题，请：
1. 查看控制台错误信息
2. 检查API配置是否正确
3. 确认网络连接状态
4. 联系开发者获取支持

## 📝 更新日志

### v1.0 (2025-10-22)
- ✅ 完整的AI图片生成功能
- ✅ 图片智能调整和编辑
- ✅ 3D模型生成和展示
- ✅ 作品画廊系统
- ✅ 版本管理功能
- ✅ 儿童友好界面设计
- ✅ Windows一键安装包

---

🎨 **HLTraining v1.0** - 让AI创作更简单，让想象力飞翔！