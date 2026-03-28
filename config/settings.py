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
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'django-backend',  # Docker 容器名
]

# 可以透過環境變數擴展
extra_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', '').strip()
if extra_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in extra_hosts.split(',')])


# Application definition
# 應用程式定義
INSTALLED_APPS = [
    'django.contrib.admin',          # Django 管理後台
    'django.contrib.auth',           # 認證系統
    'django.contrib.contenttypes',   # 內容類型框架
    'django.contrib.sessions',       # 會話框架
    'django.contrib.messages',       # 訊息框架
    'django.contrib.staticfiles',    # 靜態檔案管理
    'rest_framework',                # Django REST Framework
    'rest_framework_simplejwt',      # JWT 認證
    'rest_framework_simplejwt.token_blacklist',  # JWT Token 黑名單（登出用）
    'corsheaders',                   # 跨域資源共享(CORS)支援
    'picture',                       # 圖片處理應用
    'accounts',                      # 用戶認證應用
    'combine',                       # 穿搭與虛擬試穿應用
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
# 資料庫配置 - 使用 PostgreSQL 存儲用戶數據
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'auth_db'),
        'USER': os.getenv('DB_USER', 'auth_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'auth_password_123'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '9090'),
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
# 前端配置（用於 CORS 和重定向）
# ============================================
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# ============================================
# CORS (跨域資源共享) 配置
# ============================================
# 根據環境變數決定是否允許所有來源
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False') == 'True'

# CORS 白名單（前端地址）
# 格式: 逗號分隔的 URL 列表
cors_origins_str = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
CORS_ALLOWED_ORIGINS = [url.strip() for url in cors_origins_str.split(',') if url.strip()]

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
# REST Framework 配置
# ============================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# ============================================
# Simple JWT 配置
# ============================================
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # Access Token 有效期 1 小時
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),       # Refresh Token 有效期 7 天
    'ROTATE_REFRESH_TOKENS': True,                     # 刷新時輪換 Refresh Token
    'BLACKLIST_AFTER_ROTATION': True,                  # 輪換後將舊 Token 加入黑名單
    'AUTH_HEADER_TYPES': ('Bearer',),                  # Authorization header 格式
    'USER_ID_FIELD': 'user_id',                        # 自定義 User ID 欄位
    'USER_ID_CLAIM': 'user_id',                        # JWT payload 中的 user_id claim
    'USERNAME_FIELD': 'user_name',                     # 自定義 username 欄位
}

# ============================================
# 自定義配置：MinIO 和 AI 後端
# ============================================
# MinIO 物件儲存配置
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
MINIO_CONTAINER_ENDPOINT = os.getenv('MINIO_CONTAINER_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'processed-images')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'False') == 'True'

# MinIO 外部訪問地址（用於生成預簽名 URL 返回給前端）
# 前端瀏覽器需要用這個地址來訪問圖片
MINIO_EXTERNAL_URL = os.getenv('MINIO_EXTERNAL_URL', 'http://localhost:9000')

# ==========================================
# AI 後端配置（單一變數，用戶手動切換）
# ==========================================
# 【重點】AI_BACKEND_URL 是單一變數，用戶根據環境手動設置：
# 
# 本地開發（模擬 AI）：
#   AI_BACKEND_URL=http://localhost:8002
#
# Docker 容器（模擬 AI）：
#   AI_BACKEND_URL=http://172.17.0.1:8002
#
# 與組員協作（真實 AI）：
#   AI_BACKEND_URL=http://[真實AI服務器IP]:8002
#
AI_BACKEND_URL = os.getenv(
    'AI_BACKEND_URL', 
    'http://localhost:8002'  # 預設為本地模擬 AI
)

# AI 虛擬試穿端點（相對於 AI_BACKEND_URL 的路徑）
AI_VIRTUAL_TRY_ON_ENDPOINT = os.getenv(
    'AI_VIRTUAL_TRY_ON_ENDPOINT',
    '/virtual_try_on/clothes/combine'
)

# 組合完整的虛擬試穿 URL（為了向後相容）
AI_BACKEND_VIRTUAL_TRY_ON_URL = (
    AI_BACKEND_URL + AI_VIRTUAL_TRY_ON_ENDPOINT
    if not AI_BACKEND_URL.endswith(AI_VIRTUAL_TRY_ON_ENDPOINT)
    else AI_BACKEND_URL
)

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

# 自定義用戶模型
AUTH_USER_MODEL = 'accounts.User'

# Django 認證後端
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
