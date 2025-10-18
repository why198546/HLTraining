# AI创意工坊 - 儿童版

一个专为10-14岁儿童设计的AI培训网站，让孩子们通过手绘简笔画体验AI技术的魅力。

## 🎨 项目特色

- **简笔画上传** - 支持多种图片格式，拖拽式上传体验
- **AI智能上色** - 使用Nano Banana API为简笔画自动上色
- **手办风格转换** - 生成精美的手办风格图片
- **3D模型生成** - 通过Hunyuan3D API将2D图像转换为3D模型
- **交互式3D预览** - 使用Three.js技术实现360度模型查看
- **作品展示** - 精美的作品画廊和社区分享功能
- **教育内容** - 寓教于乐的AI知识学习模块

## 🚀 技术栈

### 后端
- **Python Flask** - Web应用框架
- **Pillow** - 图像处理库
- **OpenCV** - 计算机视觉库
- **Requests** - HTTP请求库

### 前端
- **HTML5** - 语义化结构
- **CSS3** - 现代样式设计
- **JavaScript (ES6+)** - 交互逻辑
- **Three.js** - 3D图形渲染

### AI服务
- **Nano Banana API** - 图像上色和风格转换
- **Hunyuan3D API** - 3D模型生成

## 📁 项目结构

```
HLTraining/
├── .github/
│   └── copilot-instructions.md    # GitHub Copilot指导文件
├── static/                        # 静态资源目录
│   ├── css/
│   │   └── style.css             # 主样式文件
│   ├── js/
│   │   ├── main.js               # 主页面JavaScript
│   │   ├── gallery.js            # 作品展示页JavaScript
│   │   └── tutorial.js           # 教程页JavaScript
│   └── images/                   # 图片资源
├── templates/                    # HTML模板目录
│   ├── index.html               # 主页模板
│   ├── gallery.html             # 作品展示页模板
│   └── tutorial.html            # 教程页模板
├── api/                         # API集成模块
│   ├── nano_banana.py           # Nano Banana API集成
│   └── hunyuan3d.py            # Hunyuan3D API集成
├── uploads/                     # 用户上传文件目录
├── models/                      # 生成的3D模型存储
├── app.py                       # Flask应用主文件
├── requirements.txt             # Python依赖包列表
└── README.md                    # 项目说明文档
```

## 🛠️ 安装和运行

### 1. 克隆项目
```bash
git clone <repository-url>
cd HLTraining
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置API密钥
设置环境变量：
```bash
export NANO_BANANA_API_KEY="your-nano-banana-api-key"
export HUNYUAN3D_API_KEY="your-hunyuan3d-api-key"
```

### 5. 运行应用
```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 🎯 使用指南

### 儿童用户
1. **准备简笔画** - 在纸上画一个简单的图案
2. **拍照上传** - 用手机或相机拍摄简笔画并上传
3. **等待AI处理** - 系统自动进行图像预处理、上色和3D生成
4. **查看结果** - 欣赏AI生成的彩色图片、手办风格和3D模型
5. **下载分享** - 保存作品并与朋友分享

### 开发者
- 查看 `api/` 目录了解AI服务集成
- 修改 `static/css/style.css` 调整界面样式
- 编辑 `templates/` 目录下的HTML文件修改页面结构
- 在 `static/js/` 目录中添加或修改JavaScript功能

## 🔧 API集成

### Nano Banana API
负责图像上色和风格转换功能。主要方法：
- `colorize_sketch()` - 为简笔画上色
- `generate_figurine_style()` - 生成手办风格图片

### Hunyuan3D API  
负责3D模型生成功能。主要方法：
- `generate_3d_model()` - 从2D图像生成3D模型
- `optimize_for_web()` - 优化模型以适合Web显示

## 🎨 设计理念

### 儿童友好
- 色彩鲜明的界面设计
- 简单直观的操作流程
- 有趣的动画效果
- 友好的错误提示

### 教育性
- AI技术知识普及
- 创作过程可视化
- 激发创造力和想象力
- 培养对技术的兴趣

### 安全性
- 文件类型和大小限制
- 用户输入验证
- 错误处理和恢复
- 隐私保护措施

## 🔄 开发流程

1. **文件上传** - 用户上传简笔画图片
2. **图像预处理** - 转换为灰度图并二值化
3. **AI上色** - 调用Nano Banana API进行智能上色
4. **风格转换** - 生成手办风格效果
5. **3D建模** - 使用Hunyuan3D API生成3D模型
6. **结果展示** - 在Web界面展示所有处理结果

## 🌟 主要功能

### 主页 (index.html)
- 项目介绍和功能展示
- 文件上传界面
- 处理进度显示
- 结果展示区域

### 作品展示 (gallery.html)
- 精选作品展示
- 分类筛选功能
- 互动点赞系统
- 创作灵感分享

### 使用教程 (tutorial.html)
- 详细使用指南
- AI技术科普
- 常见问题解答
- 绘画技巧分享

## 🚧 注意事项

### 开发环境
- Python 3.8+ 
- 现代浏览器 (Chrome, Firefox, Safari)
- 稳定的网络连接（用于API调用）

### API限制
- 请确保有效的API密钥
- 注意API调用频率限制
- 处理超时和失败情况

### 文件管理
- 定期清理uploads和models目录
- 监控磁盘空间使用
- 实现文件过期删除机制

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -am '添加新功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 创建 Pull Request

## 📝 许可证

本项目专为教育目的设计，适用于10-14岁儿童的AI学习体验。

## 📞 联系我们

如有问题或建议，请通过以下方式联系：
- 创建 Issue
- 发送邮件至技术支持团队
- 查看项目Wiki获取更多信息

---

**AI创意工坊** - 让每个孩子都能体验AI技术的神奇魅力！ ✨