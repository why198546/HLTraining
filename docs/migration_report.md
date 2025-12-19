# app.py 代码迁移状态报告

生成时间: 2025-12-20
项目: HLTraining (儿童AI培训网站)

## 📊 总体进度

- **总路由数**: 67 个
- **✅ 已迁移**: 53 个 (79.1%)
- **❌ 待迁移**: 14 个 (20.9%)

## ✅ 已完成迁移的模块

### 1. Canvas功能 (11个路由) → `app/routes/canvas.py` 和 `app/routes/api.py`
- `/canvas` - Canvas编辑器页面
- `/canvas-infinite` - 无限画布页面  
- `/api/canvas/generate` - 生成图片
- `/api/canvas/chat` - AI对话
- `/api/canvas/modify` - 修改图片
- `/api/canvas/projects` - 项目列表
- `/api/canvas/projects/create` - 创建项目
- `/api/canvas/projects/<project_id>` - 项目CRUD操作
- `/api/canvas/projects/<project_id>/chat` - 项目对话

### 2. 创作相关 (4个路由) → `app/routes/create.py` 和 `app/routes/api.py`
- `/create` - 创作页面
- `/edit/<artwork_id>` - 编辑作品
- `/artwork/<artwork_id>` - 查看作品

### 3. 画廊相关 (6个路由) → `app/routes/gallery.py` 和 `app/routes/api.py`
- `/gallery` - 画廊页面
- `/api/feature-artwork/<artwork_id>` - 推荐作品
- `/api/unfeature-artwork/<artwork_id>` - 取消推荐
- `/api/vote-artwork/<artwork_id>` - 投票
- `/api/increment-view/<artwork_id>` - 增加浏览量
- `/api/artwork/<artwork_id>/privacy` - 隐私设置

### 4. 视频功能 (2个路由) → `app/routes/video.py` 和 `app/routes/api.py`
- `/video` - 视频生成页面
- `/api/generate-video` - 生成视频
- `/api/video-status/<task_id>` - 视频状态
- `/api/save-video` - 保存视频

### 5. 静态文件 (5个路由) → `app/routes/static_files.py`
- `/uploads/<path:filepath>` - 上传文件访问
- `/models/<filename>` - 3D模型文件
- `/creation_sessions/<path:filepath>` - 创作会话文件
- `/static/creation_sessions/<path:filename>` - 静态创作文件

### 6. API接口 (13个路由) → `app/routes/api.py`
- `/api/translate-prompt` - 翻译提示词
- `/api/organize-prompt` - 整理提示词
- `/api/generate-artwork-info` - 生成作品信息
- `/api/get-image-info` - 获取图片信息
- `/api/fetch-image` - 获取外部图片
- `/api/save-artwork` - 保存作品
- `/api/artwork/<artwork_id>` - 作品CRUD
- `/api/sam3d/info` - SAM3D信息

### 7. 主页和测试页 (12个路由) → `app/routes/main.py`
- `/` - 首页
- `/sunguo-class` - 松果课堂导航
- `/sunguo-class/<lesson_key>` - 课程页面
- `/tutorial` - 教程
- `/test`, `/debug`, `/test-controls`, `/simple-test` - 测试页面
- `/test-3d`, `/test-model` - 3D测试
- `/test-privacy-toggles`, `/test-content-indicators` - 功能测试

## ❌ 待迁移的模块

### 1. 3D模型功能 (8个路由) → 需要迁移到 `app/routes/model3d.py`

**待迁移路由列表:**
1. `POST /generate-image` - 从简笔画生成图片
2. `POST /adjust-image` - 调整图片风格
3. `POST /generate-multi-view` - 生成多视图
4. `POST /upload-reference-image` - 上传参考图
5. `POST /generate-3d-model` - 使用Hunyuan3D生成3D模型
6. `POST /generate-3d-model-sam` - 使用SAM3D生成3D模型
7. `POST /compare-3d-engines` - 对比3D引擎

**相关工具函数需要迁移到 `managers/model3d_manager.py`:**
- `generate_3d_model_from_image()` - 单图生成3D
- `generate_3d_model_from_multi_view()` - 多视图生成3D
- `preprocess_sketch()` - 预处理简笔画
- `allowed_file()` - 文件验证

### 2. Session管理 (6个路由) → 需要迁移到 `app/routes/api.py`

**待迁移路由列表:**
1. `POST /create-session` - 创建创作会话
2. `GET /session/<session_id>/info` - 获取会话信息
3. `GET /session/<session_id>/versions` - 获取版本列表
4. `GET /session/<session_id>/selected-versions` - 获取选中版本
5. `POST /session/<session_id>/select-version` - 选择版本
6. `DELETE /session/<session_id>/delete-version` - 删除版本

**说明:** 这些路由逻辑已经有对应的 `CreationSessionManager`，只需要移动路由定义。

## 🔧 工具函数迁移建议

### 需要保留在 app.py 的函数:
- `normalize_path_for_url()` - 路径转换工具（全局使用）

### 需要迁移到 `app/utils.py`:
- `allowed_file()` - 文件验证
- `auto_save_artwork_to_db()` - 自动保存作品

### 需要迁移到 `managers/model3d_manager.py`:
- `generate_3d_model_from_image()` - 单图生成3D
- `generate_3d_model_from_multi_view()` - 多视图生成3D
- `preprocess_sketch()` - 简笔画预处理

### 需要迁移到 `managers/prompt_manager.py`:
- `detect_and_split_multi_generation()` - 多图生成检测

## 📋 迁移步骤建议

### 第一阶段: 迁移3D模型功能
1. 创建 `managers/model3d_manager.py`
2. 迁移工具函数到 manager
3. 在 `app/routes/model3d.py` 中添加路由
4. 测试3D生成功能
5. 从 app.py 删除相应代码

### 第二阶段: 迁移Session管理
1. 在 `app/routes/api.py` 中添加session相关路由
2. 使用现有的 `CreationSessionManager`
3. 测试会话管理功能
4. 从 app.py 删除相应代码

### 第三阶段: 清理和优化
1. 迁移工具函数到对应的 utils 和 managers
2. 整理导入语句
3. 更新文档
4. 完整回归测试

## 🎯 迁移后的文件结构

```
app/
├── __init__.py                 # Flask应用工厂
├── config.py                   # 配置
├── utils.py                    # 通用工具函数
└── routes/
    ├── __init__.py            # 路由注册
    ├── main.py                # 主页和测试页 ✅
    ├── canvas.py              # Canvas功能 ✅
    ├── create.py              # 创作相关 ✅
    ├── gallery.py             # 画廊相关 ✅
    ├── video.py               # 视频功能 ✅
    ├── model3d.py             # 3D模型功能 ❌ (待完成)
    ├── api.py                 # API接口 ⚠️ (需添加session路由)
    └── static_files.py        # 静态文件 ✅

managers/
├── gallery_manager.py         # 画廊管理 ✅
├── creation_session_manager.py # 会话管理 ✅
├── model3d_manager.py         # 3D模型管理 ❌ (需创建)
└── prompt_manager.py          # 提示词管理 ❌ (需创建)

auth/
├── __init__.py                # 认证蓝图 ✅
├── models.py                  # 数据模型 ✅
├── forms.py                   # 表单 ✅
└── routes.py                  # 认证路由 ✅

api/
├── nano_banana.py             # Nano Banana API ✅
├── hunyuan3d.py               # Hunyuan3D API ✅
├── sam3d_api.py               # SAM3D API ✅
├── veo31.py                   # VEO视频API ✅
└── prompt_translator.py       # 提示词翻译 ✅
```

## ⚠️ 注意事项

1. **向后兼容性**: 迁移过程中要保证旧的URL路径仍然可用
2. **导入路径**: 注意更新所有相关的导入语句
3. **测试覆盖**: 每迁移一个模块都要进行完整测试
4. **数据库迁移**: 确认数据模型没有遗漏
5. **配置文件**: 检查环境变量和配置项

## ✅ 下一步行动

**优先级1 - 3D模型功能迁移:**
1. 创建 `managers/model3d_manager.py`
2. 迁移3D相关工具函数
3. 完善 `app/routes/model3d.py` 路由
4. 测试3D生成流程

**优先级2 - Session管理迁移:**
1. 在 `app/routes/api.py` 添加session路由
2. 测试会话管理功能

**优先级3 - 最终清理:**
1. 删除 app.py 中已迁移的代码
2. 重构为纯粹的应用入口文件
3. 完整回归测试

---

**迁移完成后的 app.py 应该只包含:**
- Flask应用创建（或调用 `create_app()`）
- 基本配置
- 全局错误处理器
- 应用启动代码

目标行数: < 50 行 (当前 2845 行)
