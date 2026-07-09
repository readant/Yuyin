"""Gunicorn配置文件"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 服务器配置
bind = "0.0.0.0:5000"
workers = 4  # 工作进程数
worker_class = "thread"  # 使用线程模式（支持SocketIO）
timeout = 120
keepalive = 5

# 日志配置
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

# 进程配置
preload_app = True  # 预加载应用，提高启动速度
max_requests = 1000  # 每个worker处理1000个请求后重启
max_requests_jitter = 50  # 随机抖动，避免同时重启