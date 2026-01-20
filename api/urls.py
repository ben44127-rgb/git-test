"""
API URL Configuration
API 应用的 URL 路由配置

这个文件定义了 API 应用内部的所有路由规则
"""
from django.urls import path
from . import views

# URL 路由列表
# path() 函数的参数：
# 1. 第一个参数：URL 模式（路径）
# 2. 第二个参数：视图函数
# 3. name：URL 的名称（用于反向解析）
urlpatterns = [
    # 健康检查端点
    # 访问：http://localhost:30000/health
    path('health', views.health_check, name='health_check'),
    
    # 图片上传和处理端点
    # 访问：http://localhost:30000/api/upload-image
    path('api/upload-image', views.upload_and_process, name='upload_and_process'),
]
