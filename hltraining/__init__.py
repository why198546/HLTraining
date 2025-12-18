"""Application factory for HLTraining.
Phased refactor: temporarily returns the existing Flask app from root `app.py`.
"""
from typing import Any
import sys
import os

# 添加项目根目录到 sys.path（优先级更高）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def create_app() -> Any:
    # 直接导入根目录的 app.py 中的 app 实例
    import app as app_module
    return app_module.app
