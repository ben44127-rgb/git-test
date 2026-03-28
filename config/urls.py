"""
URL Configuration for image processing backend.
圖像處理後端的 URL 設定

這個檔案定義了應用的 URL 路由規則
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),                        # Django 管理後台
    path('', include('picture.urls')),                      # 圖片處理應用的 URL
    path('account/user/', include('accounts.urls')),        # 認證系統的 URL
    path('combine/', include('combine.urls')),              # 穿搭/虛擬試穿 URL
    path('aichat_service/', include('aichat_service.urls')),  # AI 聊天和推薦服務 URL
]
