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
    
    # ========== 用戶衣服管理端點 ==========
    # 用戶新增衣服（上傳圖片 + AI 処理）
    # POST: /picture/clothes/ （multipart/form-data）
    path('picture/clothes/', views.upload_and_process, name='upload_and_process'),
    
    # 用戶衣服列表（普通用戶看自己的，管理員看所有）
    # GET: /picture/clothes/my
    path('picture/clothes/my', views.user_clothes_list, name='user_clothes_list'),
    
    # 用戶喜歡的衣服列表
    # GET: /picture/clothes/favorites
    path('picture/clothes/favorites', views.favorites_list, name='favorites_list'),
    
    # ========== 衣服詳情端點 ==========
    # GET: 獲取單個衣服詳情（任何用戶均可）
    # PUT: 更新衣服（衣服擁有者或管理員）
    # DELETE: 刪除衣服（衣服擁有者或管理員）
    path('picture/clothes/<str:clothes_uid>/', views.clothes_detail, name='clothes_detail'),
    
    # 標記/取消標記衣服為喜歡
    # PATCH: /picture/clothes/<clothes_uid>/favorite
    path('picture/clothes/<str:clothes_uid>/favorite', views.toggle_favorite, name='toggle_favorite'),
    
    # ========== 用戶個人照片管理端點 ==========
    # POST: 上傳個人照片
    # GET: 獲取用戶的所有照片列表
    path('picture/user/photo', views.upload_user_photo, name='upload_user_photo'),
    
    # GET: 獲取單張照片詳情
    # PUT: 更新照片（替換照片文件）
    # DELETE: 刪除照片
    path('picture/user/photo/<str:user_uid>/', views.photo_detail, name='photo_detail'),
]
