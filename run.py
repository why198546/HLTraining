"""应用入口文件 - 使用新的模块化结构"""
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
