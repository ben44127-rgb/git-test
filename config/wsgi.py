"""
WSGI config for image processing backend.
圖像處理後端的 WSGI 配置

WSGI (Web Server Gateway Interface) 是 Python Web 應用和 Web 服務器之間的標準介面
這個檔案提供了 WSGI 應用物件，用於部署到生產環境

使用方法:
- 開發環境: python manage.py runserver
- 生產環境: gunicorn config.wsgi:application
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# 提前載入環境變數，確保 WSGI 應用能使用 .env 中的配置
try:
    from dotenv import load_dotenv
    # 找到專案根目錄的 .env 檔案
    base_dir = Path(__file__).resolve().parent.parent
    env_path = base_dir / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # 如果沒有安裝 python-dotenv，略過（Docker 環境中會直接使用環境變數）
    pass

# 設定 Django 設定模組的環境變數
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 获取 WSGI 应用对象
application = get_wsgi_application()
