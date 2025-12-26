"""创建画布项目数据库表"""
import importlib.util
import os
import sys

# 确保当前目录在Python路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 直接加载app.py文件（而不是app目录）
spec = importlib.util.spec_from_file_location("app_module", os.path.join(current_dir, "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)

app = app_module.app
db = app_module.db

with app.app_context():
    db.create_all()
    print('✅ 数据库表已创建成功')
    print('✅ CanvasProject 表已就绪')
