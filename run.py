"""应用入口文件 - 使用新的模块化结构"""
import os

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 从环境变量读取配置
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 80))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)
