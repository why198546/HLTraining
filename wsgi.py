"""WSGI entrypoint for production servers (gunicorn/uwsgi).

使用新的模块化应用结构。
"""
import os
import sys

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 确保工作目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入 run.py 模块
import importlib.util

spec = importlib.util.spec_from_file_location("run_module", "run.py")
run_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_module)

# WSGI服务器需要的变量名
application = run_module.app

print("[OK] WSGI app loaded successfully")
