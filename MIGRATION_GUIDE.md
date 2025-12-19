"""
应用模块化重构 - 迁移指南

本指南说明如何将app.py中的路由逐步迁移到新的模块化结构中。
"""

## 已完成的基础结构

✅ app/__init__.py - 应用工厂
✅ app/config.py - 配置管理
✅ app/utils.py - 工具函数
✅ app/routes/ - 路由模块目录
✅ run.py - 新入口文件

## 当前状态

新应用已成功启动并运行在 http://127.0.0.1:5000

**✅ 已完成的迁移：**
- 主页、教程、测试页面 (main.py)
- 视频页面 (video.py) 
- 静态文件服务 (static_files.py)
- 画布页面 (canvas.py - 基础)
- **所有API路由 (api.py - 29个端点，1417行代码)** ← 新完成！

**📋 待迁移：**
- create.py - 创作页面路由
- gallery.py - 作品集页面路由
- model3d.py - 3D模型相关路由

## 下一步迁移计划

### 阶段1: 保持兼容（当前阶段）
- ✅ 创建新的模块化结构
- ✅ 验证新应用可以启动
- ⏳ 保留原app.py继续运行
- ⏳ 逐个迁移路由到新结构

### 阶段2: 迁移API路由（✅ 已完成）
**状态**: ✅ **已完成** (2025-12-20)

将app.py中的所有API路由迁移到 app/routes/api.py：

**已迁移的API (29个):**
- ✅ 画布API (9个): generate, chat, modify, projects CRUD
- ✅ 3D模型API (1个): sam3d/info
- ✅ 作品保存API (1个): save-artwork
- ✅ 图片处理API (2个): get-image-info, fetch-image
- ✅ Prompt处理API (3个): translate, organize, generate-info
- ✅ 视频生成API (3个): generate, status, save
- ✅ 作品互动API (4个): feature, vote, view, unfeature
- ✅ 作品管理API (5个): artwork CRUD + privacy
- ✅ 图片生成API (1个): generate-image

📊 **迁移统计**: 1417行代码，29个API端点

### 阶段3: 迁移页面路由（进行中）
- create.py - 创作页面路由
- gallery.py - 作品集页面路由
- model3d.py - 3D模型相关路由

### 阶段4: 迁移会话管理
- 创作会话相关路由
- 版本管理路由

### 阶段5: 清理和优化
- 移除app.py中已迁移的代码
- 优化导入
- 添加类型注解
- 编写测试

## 迁移模板

### API路由迁移示例

```python
# 在 app/routes/api.py 中添加：

from flask import request, jsonify
from flask_login import login_required, current_user
from api.nano_banana import NanoBananaAPI
from ..utils import normalize_path_for_url

@api_bp.route('/canvas/generate', methods=['POST'])
@login_required
def canvas_generate():
    '''画布图片生成API'''
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': '请输入描述'
            }), 400
        
        # ... 业务逻辑 ...
        
        return jsonify({
            'success': True,
            'image_url': image_url
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

### 页面路由迁移示例

```python
# 在 app/routes/create.py 中添加：

from flask import render_template
from flask_login import login_required

@create_bp.route('/')
@login_required
def create():
    '''创作页面'''
    return render_template('create.html')
```

## 测试方法

### 1. 测试新应用
```bash
python run.py
```

### 2. 测试原应用（兼容）
```bash
python app.py
```

### 3. 验证路由
访问各个功能页面，确保正常工作。

## 注意事项

1. **保持向后兼容**: 在完全迁移前，app.py仍需正常工作
2. **逐步迁移**: 每次迁移一个模块，测试通过后再继续
3. **更新导入**: 迁移后需更新相关的导入语句
4. **数据库共享**: 新旧应用共享同一数据库
5. **配置一致**: 确保配置在两个版本中保持一致

## 文档更新

迁移完成后需要更新：
- README.md - 主文档
- .github/copilot-instructions.md - Copilot指令
- 部署文档

## 性能优化建议

1. 使用蓝图延迟加载
2. API路由使用缓存
3. 静态资源使用CDN
4. 数据库查询优化
5. 添加日志记录
