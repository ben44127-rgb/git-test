"""
ASGI config for image processing backend.
图像处理后端的 ASGI 配置

ASGI (Asynchronous Server Gateway Interface) 是 Python 异步 Web 应用的标准接口
支持 WebSocket、HTTP/2 等异步协议
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
