# 应用模块化重构说明

## 目录结构

```
HLTraining/
├── app/                          # 主应用模块（新增）
│   ├── __init__.py              # 应用工厂
│   ├── config.py                # 配置文件
│   ├── utils.py                 # 工具函数
│   └── routes/                  # 路由模块
│       ├── __init__.py
│       ├── main.py              # 主页和通用路由
│       ├── canvas.py            # 画布路由
│       ├── create.py            # 创作路由
│       ├── gallery.py           # 作品集路由
│       ├── video.py             # 视频路由
│       ├── model3d.py           # 3D模型路由
│       ├── api.py               # API路由
│       └── static_files.py      # 静态文件服务
├── app.py                        # 原始应用文件（保留以兼容）
├── run.py                        # 新的应用入口
└── ...
```

## 模块说明

### app/__init__.py
- 应用工厂函数 `create_app()`
- 初始化数据库、登录管理器、邮件服务
- 注册所有蓝图

### app/config.py
- 集中管理所有配置
- 包括数据库、上传、邮件等配置

### app/utils.py
- 通用工具函数
- `normalize_path_for_url()` - 路径转换
- `allowed_file()` - 文件验证
- `preprocess_sketch()` - 图片预处理

### app/routes/
每个路由模块负责特定功能：
- **main.py**: 首页、教程、测试页面
- **canvas.py**: 画布页面
- **create.py**: 创作相关功能
- **gallery.py**: 作品集展示
- **video.py**: 视频生成
- **model3d.py**: 3D模型生成
- **api.py**: 所有API接口
- **static_files.py**: 静态文件服务

## 使用方式

### 1. 使用新的模块化结构
```bash
python run.py
```

### 2. 继续使用原有app.py（兼容）
```bash
python app.py
# 或
.\app.ps1 start
```

## 迁移进度

### ✅ 已完成
- [x] 创建应用工厂模式
- [x] 拆分配置文件
- [x] 创建路由蓝图骨架
- [x] 迁移主页路由
- [x] 迁移画布基础路由
- [x] 迁移视频路由
- [x] 迁移静态文件路由

### 🔄 进行中
- [ ] 迁移画布API路由到api.py
- [ ] 迁移创作路由到create.py
- [ ] 迁移作品集路由到gallery.py
- [ ] 迁移3D模型路由到model3d.py
- [ ] 迁移所有API路由到api.py

### 📋 待办
- [ ] 完全移除app.py依赖
- [ ] 更新部署脚本
- [ ] 添加单元测试
- [ ] 优化导入路径

## 优势

1. **代码组织清晰**: 按功能模块拆分，易于维护
2. **易于扩展**: 新功能只需添加新蓝图
3. **便于测试**: 每个模块可独立测试
4. **团队协作**: 多人可并行开发不同模块
5. **性能优化**: 按需加载路由

## 注意事项

1. 原有app.py保留作为兼容层
2. 新功能应该添加到app/routes/对应模块
3. 逐步迁移旧代码到新结构
4. 确保导入路径正确
