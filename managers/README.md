# 管理器模块

本目录包含各类业务管理器。

## 文件说明

- `creation_session_manager.py` - 创作会话管理器
  - 管理用户的创作会话
  - 处理图片版本和历史记录
  
- `gallery_manager.py` - 作品画廊管理器
  - 管理作品集数据
  - 处理作品的保存和展示
  
- `version_manager.py` - 版本管理器
  - 管理作品的多个版本
  - 处理版本切换和历史记录
  
- `flask_manager.py` - Flask进程管理器
  - 管理Flask开发服务器进程
  - 处理服务器启动和重启

- `model3d_manager.py` - 3D模型管理器 ✨ 新增
  - 管理3D模型生成逻辑
  - 支持Hunyuan3D和SAM3D两种引擎
  - 处理单图和多视角3D生成
  - 提供引擎对比功能

- `prompt_manager.py` - 提示词管理器 ✨ 新增
  - 处理提示词解析和优化
  - 支持多图生成检测
  - 自动添加默认国籍标签
  - 提供提示词规范化功能

## 使用示例

```python
from managers.gallery_manager import GalleryManager
from managers.creation_session_manager import CreationSessionManager
from managers.model3d_manager import Model3DManager
from managers.prompt_manager import PromptManager

# 创建管理器实例
gallery = GalleryManager()
session_mgr = CreationSessionManager()

# 使用3D模型管理器
model_path = Model3DManager.generate_3d_model_from_image('path/to/image.jpg')

# 使用提示词管理器
prompt = PromptManager.add_default_nationality('一个小女孩')  # 自动添加"中国人形象"
```
session_mgr = CreationSessionManager()
```
