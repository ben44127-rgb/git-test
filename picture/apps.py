from django.apps import AppConfig


class PictureConfig(AppConfig):
    """圖片處理應用配置類"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'picture'
    verbose_name = '圖片處理'
