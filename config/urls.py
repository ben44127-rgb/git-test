"""
URL Configuration for image processing backend.
圖像處理後端的 URL 配置

這個檔案定義了應用的 URL 路由規則
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django 管理後台
    path('', include('api.urls')),    # API 應用的 URL
]
