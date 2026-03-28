"""
URL Configuration for Combine App
虛擬試衣管理的 URL 路由

路由說明：
1. /combine/user/virtual-try-on            - 虛擬試衣（Feature 3.1）
2. /combine/user/virtual-try-on-history    - 我的試穿歷史
3. /combine/user/virtual-try-on-detail/<model_uid>  - 試穿詳情
"""

from django.urls import path
from . import views

app_name = 'combine'

urlpatterns = [
    # ========== 虛擬試衣（Feature 3.1） ==========
    # POST：發起虛擬試衣
    path('user/virtual-try-on', views.virtual_try_on, name='user_virtual_try_on'),
    
    # GET：查看我的虛擬試衣歷史
    path('user/virtual-try-on-history', views.get_my_try_ons, name='user_get_my_try_ons'),
    
    # GET：查看單筆試穿詳情
    path('user/virtual-try-on-detail/<str:model_uid>', views.get_try_on_detail, name='user_get_try_on_detail'),
]
