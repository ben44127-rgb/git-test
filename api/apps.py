from django.apps import AppConfig


class ApiConfig(AppConfig):
    """API 应用配置类"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = '图片处理 API'
