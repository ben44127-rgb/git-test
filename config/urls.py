"""
URL Configuration for image processing backend.
图像处理后端的 URL 配置

这个文件定义了应用的 URL 路由规则
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django 管理后台
    path('', include('api.urls')),    # API 应用的 URL
]
