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
    # 存取：http://localhost:30000/picture/clothes/upload_image
    path('picture/clothes/upload_image', views.upload_and_process, name='upload_and_process'),
    
    # 衣服 CRUD 端點
    # POST: 創建衣服（需要管理員權限）
    # GET: 列表衣服（支持分頁、篩選）
    path('picture/clothes/', views.clothes_list_create, name='clothes_list_create'),
    
    # 衣服詳情端點
    # GET: 獲取單個衣服
    # PUT: 更新衣服（需要管理員權限）
    # DELETE: 刪除衣服（需要管理員權限）
    path('picture/clothes/<int:clothes_id>/', views.clothes_detail, name='clothes_detail'),
]
