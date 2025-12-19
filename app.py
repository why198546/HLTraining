"""Flask 应用入口文件

本文件是应用的主入口，使用工厂模式创建应用实例。
所有路由和业务逻辑都在 app/ 目录的模块化结构中。

项目结构:
- app/__init__.py        - Flask应用工厂
- app/routes/            - 所有路由蓝图
- managers/              - 业务逻辑管理器
- api/                   - 外部API集成
- auth/                  - 认证和用户管理
"""

from dotenv import load_dotenv

# 加载环境变量（必须在导入app之前）
load_dotenv()

# 导入应用工厂并创建实例
from app import create_app

# 创建全局应用实例
app = create_app()

if __name__ == '__main__':
    # 开发模式直接运行
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
