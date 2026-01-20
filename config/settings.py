"""
Django settings for image processing backend.
Django 图像处理后端的设置配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量文件
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# 构建项目内部路径，比如: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# 安全警告：在生产环境中保密密钥必须保密！
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production-123456789')

# SECURITY WARNING: don't run with debug turned on in production!
# 安全警告：在生产环境中不要开启调试模式！
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# 允许的主机列表
# 在生产环境中，应该设置为具体的域名
ALLOWED_HOSTS = ['*']  # 开发环境允许所有主机，生产环境需要修改

# Application definition
# 应用程序定义
INSTALLED_APPS = [
    'django.contrib.admin',          # Django 管理后台
    'django.contrib.auth',           # 认证系统
    'django.contrib.contenttypes',   # 内容类型框架
    'django.contrib.sessions',       # 会话框架
    'django.contrib.messages',       # 消息框架
    'django.contrib.staticfiles',    # 静态文件管理
    'corsheaders',                   # 跨域资源共享(CORS)支持
    'api',                           # 我们的 API 应用
]

# 中间件配置
# 中间件是处理请求和响应的钩子
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',      # 安全中间件
    'corsheaders.middleware.CorsMiddleware',             # CORS 中间件（必须在 CommonMiddleware 之前）
    'django.contrib.sessions.middleware.SessionMiddleware',  # 会话中间件
    'django.middleware.common.CommonMiddleware',         # 通用中间件
    'django.middleware.csrf.CsrfViewMiddleware',         # CSRF 保护中间件
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 认证中间件
    'django.contrib.messages.middleware.MessageMiddleware',  # 消息中间件
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 点击劫持保护
]

# URL 配置
ROOT_URLCONF = 'config.urls'

# 模板配置
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

# WSGI 应用配置
WSGI_APPLICATION = 'config.wsgi.application'

# Database
# 数据库配置（这个应用不需要数据库，使用 SQLite 作为占位）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# 密码验证（本应用不涉及用户认证，保留默认配置）
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
# 国际化配置
LANGUAGE_CODE = 'zh-hans'  # 简体中文
TIME_ZONE = 'Asia/Shanghai'  # 上海时区
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# 静态文件配置
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# CORS (跨域资源共享) 配置
# ============================================
# 允许所有来源进行跨域请求（开发环境）
# 生产环境应该设置为具体的前端域名
CORS_ALLOW_ALL_ORIGINS = True

# 或者使用白名单（生产环境推荐）：
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173",  # Vite 开发服务器
#     "http://127.0.0.1:5173",
# ]

# 允许携带认证信息（如 cookies）
CORS_ALLOW_CREDENTIALS = True

# 允许的 HTTP 方法
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

# 允许的请求头
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
# 自定义配置：MinIO 和 AI 后端
# ============================================
# MinIO 对象存储配置
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'processed-images')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'False') == 'True'

# AI 后端服务配置
AI_BACKEND_URL = os.getenv('AI_BACKEND_URL', 'http://localhost:8080/api/remove_bg')

# 文件上传配置
UPLOAD_FOLDER = BASE_DIR / 'output'
LOG_FOLDER = BASE_DIR / 'logs'

# 确保必要的目录存在
UPLOAD_FOLDER.mkdir(exist_ok=True)
LOG_FOLDER.mkdir(exist_ok=True)

# 文件上传大小限制（10MB）
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# 日志配置
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
