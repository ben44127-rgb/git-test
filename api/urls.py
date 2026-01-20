"""
API URL Configuration
API 應用的 URL 路由配置

這個檔案定義了 API 應用內部的所有路由規則
"""
from django.urls import path
from . import views

# URL 路由清單
# path() 函數的參數：
# 1. 第一個參數：URL 模式（路徑）
# 2. 第二個參數：視圖函數
# 3. name：URL 的名稱（用於反向解析）
urlpatterns = [
    # 健康檢查端點
    # 存取：http://localhost:30000/health
    path('health', views.health_check, name='health_check'),
    
    # 圖片上傳和處理端點
    # 存取：http://localhost:30000/api/upload-image
    path('api/upload-image', views.upload_and_process, name='upload_and_process'),
]
