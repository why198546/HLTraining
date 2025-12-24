"""应用入口文件 - 使用新的模块化结构"""
import os
import sys

# 确保工作目录是脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from dotenv import load_dotenv

# 加载环境变量 - 明确指定.env文件路径
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path)

print(f"📁 工作目录: {os.getcwd()}")
print(f"🔑 环境变量加载: {'成功' if os.getenv('TENCENTCLOUD_SECRET_ID') else '失败'}")

from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 从环境变量读取配置
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 80))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)
