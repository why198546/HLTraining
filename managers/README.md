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

## 使用示例

```python
from managers.gallery_manager import GalleryManager
from managers.creation_session_manager import CreationSessionManager

# 创建管理器实例
gallery = GalleryManager()
session_mgr = CreationSessionManager()
```
