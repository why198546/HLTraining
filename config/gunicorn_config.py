"""
Gunicorn配置文件
用于HLTraining Flask应用的生产环境部署
"""
import os
import multiprocessing

# 服务器监听地址和端口
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8080')}"

# Worker进程数量
# 推荐: (2 x CPU核心数) + 1
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))

# Worker类型
# sync: 同步worker（默认）
# gevent/eventlet: 异步worker（需要安装对应库）
worker_class = 'sync'

# 每个worker的线程数
threads = 2

# Worker超时时间（秒）
timeout = 120

# 优雅关闭超时时间（秒）
graceful_timeout = 30

# Keep-alive连接时间（秒）
keepalive = 5

# 最大请求数（防止内存泄漏）
# Worker处理此数量请求后会重启
max_requests = 1000
max_requests_jitter = 50  # 随机抖动，避免同时重启

# 项目根目录（config目录的上级目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 日志配置
accesslog = os.getenv('ACCESS_LOG', os.path.join(BASE_DIR, 'logs/access.log'))
errorlog = os.getenv('ERROR_LOG', os.path.join(BASE_DIR, 'logs/error.log'))
loglevel = os.getenv('LOG_LEVEL', 'info')

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = 'hltraining'

# PID文件
pidfile = os.path.join(BASE_DIR, 'logs/gunicorn.pid')

# Daemon模式（后台运行）
daemon = False

# 工作目录
chdir = os.path.dirname(os.path.abspath(__file__))

# 用户和组（需要root权限）
# user = 'www-data'
# group = 'www-data'

# 临时目录
tmp_upload_dir = '/tmp'

# SSL配置（如果不使用Nginx反向代理）
# keyfile = '/path/to/ssl/key.pem'
# certfile = '/path/to/ssl/cert.pem'

# 预加载应用
# 提高性能，但热重载不可用
preload_app = True

# Worker连接数限制
worker_connections = 1000

# 环境变量
raw_env = [
    f"FLASK_ENV={os.getenv('FLASK_ENV', 'production')}",
]

# 服务器钩子函数
def on_starting(server):
    """服务器启动前执行"""
    print(f"🚀 HLTraining服务器启动中...")
    print(f"   监听地址: {bind}")
    print(f"   Worker数量: {workers}")
    print(f"   Worker类型: {worker_class}")

def on_reload(server):
    """服务器重载时执行"""
    print("🔄 HLTraining服务器重载中...")

def when_ready(server):
    """服务器就绪时执行"""
    print(f"✅ HLTraining服务器已启动！")
    print(f"   访问地址: http://{bind}")

def on_exit(server):
    """服务器退出时执行"""
    print("👋 HLTraining服务器已停止")

def worker_int(worker):
    """Worker被中断时执行"""
    print(f"⚠️  Worker {worker.pid} 被中断")

def worker_abort(worker):
    """Worker异常退出时执行"""
    print(f"❌ Worker {worker.pid} 异常退出")

def pre_fork(server, worker):
    """Worker fork前执行"""
    pass

def post_fork(server, worker):
    """Worker fork后执行"""
    print(f"👶 Worker {worker.pid} 已启动")

def post_worker_init(worker):
    """Worker初始化后执行"""
    pass

def worker_exit(server, worker):
    """Worker退出时执行"""
    print(f"👋 Worker {worker.pid} 已退出")

def child_exit(server, worker):
    """子进程退出时执行"""
    pass

def nworkers_changed(server, new_value, old_value):
    """Worker数量变化时执行"""
    print(f"🔢 Worker数量从 {old_value} 变更为 {new_value}")

# 性能优化
# 禁用请求日志（提高性能，生产环境可选）
# accesslog = None

# 限制请求行大小（防止DOS攻击）
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
