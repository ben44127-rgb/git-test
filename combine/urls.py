"""
URL Configuration for Combine App
穿搭組合和虛擬試衣管理的 URL 路由

路由說明：
1. /combine/outfit/                    - 穿搭列表（OUTFIT-001）
2. /combine/outfit/create              - 新增穿搭（OUTFIT-002）
3. /combine/outfit/<uid>/              - 穿搭詳情、編輯、刪除
4. /combine/outfit/<uid>/favorite      - 標記喜歡（OUTFIT-004-01）
5. /combine/outfit/<uid>/rating        - 評分（OUTFIT-004-02）
6. /combine/outfit/my                  - 我的穿搭
7. /combine/outfit/favorites           - 我的收藏
8. /combine/virtual-try-on/            - 虛擬試衣（OUTFIT-003-01）
9. /combine/virtual-try-on/<uid>/confirm  - 確認保存（OUTFIT-003-02）
10. /combine/virtual-try-on/<uid>/reject   - 拒絕（OUTFIT-003-03）
"""

from django.urls import path
from . import views

app_name = 'combine'

urlpatterns = [
    # ========== 穿搭列表和詳情（OUTFIT-001, OUTFIT-002） ==========
    # 1. GET：查看所有穿搭（含篩選、搜索、分頁）
    #    POST：創建新穿搭
    path('outfit/', views.outfit_list, name='outfit_list'),
    
    # 2. POST：創建穿搭（顯式端點，同時也可用 outfit_list POST）
    path('outfit/create', views.outfit_create, name='outfit_create'),
    
    # 3. GET：查看穿搭詳情（包含完整衣服列表和評分）
    #    PUT：編輯穿搭
    #    DELETE：刪除穿搭
    path('outfit/<str:outfit_uid>/', views.outfit_detail, name='outfit_detail'),
    path('outfit/<str:outfit_uid>/update', views.outfit_update, name='outfit_update'),
    path('outfit/<str:outfit_uid>/delete', views.outfit_delete, name='outfit_delete'),
    
    # 4. 我的穿搭列表
    path('outfit/my', views.my_outfits, name='my_outfits'),
    
    # ========== 穿搭互動（OUTFIT-004） ==========
    # 5. PATCH：標記/取消標記為喜歡
    path('outfit/<str:outfit_uid>/favorite', views.outfit_toggle_favorite, name='outfit_toggle_favorite'),
    
    # 6. 我的收藏列表
    path('outfit/my/favorites', views.my_favorite_outfits, name='my_favorite_outfits'),
    
    # 7. POST/PUT：評分和評論
    path('outfit/<str:outfit_uid>/rating', views.outfit_rating, name='outfit_rating'),
    
    # ========== 虛擬試衣（OUTFIT-003） ==========
    # 8. POST：發起虛擬試衣
    #    流程：選擇穿搭/衣服 → AI合成 → 立即返回結果圖
    path('virtual-try-on/', views.virtual_try_on, name='virtual_try_on'),
    
    # 8.5 GET：查看我的虛擬試衣歷史
    path('virtual-try-on/my', views.get_my_try_ons, name='get_my_try_ons'),
    
    # 9. POST：確認虛擬試衣結果並保存為穿搭
    path('virtual-try-on/<str:try_on_uid>/save-as-outfit', views.save_try_on_as_outfit, name='save_try_on_as_outfit'),
]
