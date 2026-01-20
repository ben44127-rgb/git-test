"""
Django settings for image processing backend.
Django 圖像處理後端的設定配置檔案
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# 建構專案內部路徑，比如: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# 載入環境變數檔案
# 確保從專案根目錄載入 .env 檔案
from dotenv import load_dotenv
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 已載入環境變數檔案: {env_path}")
else:
    # Docker 環境中可能直接使用環境變數，不需要 .env 檔案
    load_dotenv()  # 嘗試從預設位置載入
    print("⚠️  未找到 .env 檔案，使用預設環境變數或系統環境變數")

# SECURITY WARNING: keep the secret key used in production secret!
# 安全警告：在生產環境中保密金鑰必須保密！
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production-123456789')

# SECURITY WARNING: don't run with debug turned on in production!
# 安全警告：在生產環境中不要開啟除錯模式！
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# 允許的主機清單
# 在生產環境中，應該設定為具體的域名
ALLOWED_HOSTS = ['*']  # 開發環境允許所有主機，生產環境需要修改

# Application definition
# 應用程式定義
INSTALLED_APPS = [
    'django.contrib.admin',          # Django 管理後台
    'django.contrib.auth',           # 認證系統
    'django.contrib.contenttypes',   # 內容類型框架
    'django.contrib.sessions',       # 會話框架
    'django.contrib.messages',       # 訊息框架
    'django.contrib.staticfiles',    # 靜態檔案管理
    'corsheaders',                   # 跨域資源共享(CORS)支援
    'api',                           # 我們的 API 應用
]

# 中間件配置
# 中間件是處理請求和響應的鉤子
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',      # 安全中間件
    'corsheaders.middleware.CorsMiddleware',             # CORS 中間件（必須在 CommonMiddleware 之前）
    'django.contrib.sessions.middleware.SessionMiddleware',  # 會話中間件
    'django.middleware.common.CommonMiddleware',         # 通用中間件
    'django.middleware.csrf.CsrfViewMiddleware',         # CSRF 保護中間件
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 認證中間件
    'django.contrib.messages.middleware.MessageMiddleware',  # 訊息中間件
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 點擊劫持保護
]

# URL 配置
ROOT_URLCONF = 'config.urls'

# 範本配置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI 應用配置
WSGI_APPLICATION = 'config.wsgi.application'

# Database
# 資料庫配置（這個應用不需要資料庫，使用 SQLite 作為占位）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# 密碼驗證（本應用不涉及使用者認證，保留預設配置）
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# 國際化配置
LANGUAGE_CODE = 'zh-hans'  # 簡體中文
TIME_ZONE = 'Asia/Shanghai'  # 上海時區
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# 靜態檔案配置
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# 預設主鍵欄位類型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# CORS (跨域資源共享) 配置
# ============================================
# 允許所有來源進行跨域請求（開發環境）
# 生產環境應該設定為具體的前端域名
CORS_ALLOW_ALL_ORIGINS = True

# 或者使用白名單（生產環境推薦）：
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173",  # Vite 開發伺服器
#     "http://127.0.0.1:5173",
# ]

# 允許攜帶認證資訊（如 cookies）
CORS_ALLOW_CREDENTIALS = True

# 允許的 HTTP 方法
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

# 允許的請求標頭
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ============================================
# 自定義配置：MinIO 和 AI 後端
# ============================================
# MinIO 物件儲存配置
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'processed-images')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'False') == 'True'

# AI 後端服務配置
AI_BACKEND_URL = os.getenv('AI_BACKEND_URL', 'http://localhost:8002/api/remove_bg')

# 檔案上傳配置
UPLOAD_FOLDER = BASE_DIR / 'output'
LOG_FOLDER = BASE_DIR / 'logs'

# 確保必要的目錄存在
UPLOAD_FOLDER.mkdir(exist_ok=True)
LOG_FOLDER.mkdir(exist_ok=True)

# 檔案上傳大小限制（10MB）
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# 日誌配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_FOLDER / 'django_app.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
