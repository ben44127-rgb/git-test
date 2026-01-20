"""
ASGI config for image processing backend.
圖像處理後端的 ASGI 配置

ASGI (Asynchronous Server Gateway Interface) 是 Python 異步 Web 應用的標準接口
支援 WebSocket、HTTP/2 等異步協議
"""

import os
from pathlib import Path
from django.core.asgi import get_asgi_application

# 提前載入環境變數，確保 ASGI 應用能使用 .env 中的配置
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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
