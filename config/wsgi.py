"""
WSGI config for image processing backend.
图像处理后端的 WSGI 配置

WSGI (Web Server Gateway Interface) 是 Python Web 应用和 Web 服务器之间的标准接口
这个文件提供了 WSGI 应用对象，用于部署到生产环境

使用方法:
- 开发环境: python manage.py runserver
- 生产环境: gunicorn config.wsgi:application
"""

import os
from django.core.wsgi import get_wsgi_application

# 设置 Django 设置模块的环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 获取 WSGI 应用对象
application = get_wsgi_application()
