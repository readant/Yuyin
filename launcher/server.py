"""Web服务管理"""
import os
import sys


class WebServer:
    """Web服务器管理器"""

    def __init__(self, port=5000):
        self.port = port
        self.server = None

    def start(self):
        """在后台启动Web服务"""
        # 将web目录加入路径
        web_dir = os.path.join(os.path.dirname(__file__), '..', 'web')
        sys.path.insert(0, web_dir)

        import uvicorn
        from app import app

        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=self.port,
            log_level="warning",
            access_log=False
        )
        self.server = uvicorn.Server(config)
        self.server.run()

    def stop(self):
        """停止Web服务"""
        if self.server:
            self.server.should_exit = True
