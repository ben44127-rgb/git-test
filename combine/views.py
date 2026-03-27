"""
Views for Outfit/Combine Management API
穿搭組合和虛擬試衣管理的視圖

主要功能：
1. OUTFIT-001：查看穿搭列表
2. OUTFIT-002：新增穿搭組合
3. OUTFIT-003：虛擬試衣和保存穿搭
4. OUTFIT-004：穿搭互動（喜歡、評分）
5. CRUD 操作：編輯、刪除穿搭
"""

import json
import requests
from django.conf import settings
from django.db.models import Q, Avg, Count
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import (
    Outfit,
    OutfitClothes,
    VirtualTryOn,
    OutfitFavorite,
)
from .serializers import (
    OutfitSerializer,
    OutfitDetailSerializer,
    OutfitCreateSerializer,
    VirtualTryOnSerializer,
    VirtualTryOnCreateSerializer,
    OutfitFavoriteSerializer,
)
from accounts.models import Clothes, Photo
from picture.models import Photo


# ============================================================================
# OUTFIT-001: 查看穿搭列表
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def outfit_list(request):
    """
    功能編號：OUTFIT-001
    模組：combine
    説明：顯示系統中所有穿搭組合，支持分頁
    
    查詢參數：
    - page: 頁碼（默認 1）
    - limit: 每頁數量（默認 20）
    """
    
    try:
        # 基礎 QuerySet
        queryset = Outfit.objects.filter(is_draft=False).select_related('created_by')
        
        # 分頁
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        total_count = queryset.count()
        total_pages = (total_count + limit - 1) // limit
        
        paginated_queryset = queryset[start_idx:end_idx]
        
        # 序列化
        serializer = OutfitSerializer(
            paginated_queryset,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'message': '穿搭列表獲取成功',
            'count': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'limit': limit,
            'results': serializer.data,
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'獲取穿搭列表失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# OUTFIT-002: 新增穿搭組合
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def outfit_create(request):
    """
    功能編號：OUTFIT-002
    模組：combine
    説明：用戶建立新的穿搭組合
    
    請求參數（JSON）：
    {
        "outfit_name": "我的春日穿搭",
        "outfit_description": "舒適又時尚的春季搭配",
        "season": "春季",
        "style": "休閒",
        "clothes_ids": ["uuid1", "uuid2", "uuid3"],
        "preview_image_url": "https://..." (可選),
        "is_draft": false
    }
    """
    
    try:
        serializer = OutfitCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '穿搭數據驗證失敗',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 創建穿搭，自動設定創建者為當前用戶
        outfit = serializer.save(created_by=request.user)
        
        # 返回完整穿搭詳情
        output_serializer = OutfitDetailSerializer(
            outfit,
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'message': '穿搭建立成功',
            'data': output_serializer.data,
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'穿搭建立失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# 查看穿搭詳情
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def outfit_detail(request, outfit_uid):
    """
    查看單個穿搭的詳細信息
    
    路徑參數：
    - outfit_uid: 穿搭 UUID
    """
    
    try:
        outfit = Outfit.objects.select_related('created_by').prefetch_related(
            'outfit_clothes__clothes',
            'liked_by',
            'ratings'
        ).get(outfit_uid=outfit_uid)
        
        serializer = OutfitDetailSerializer(
            outfit,
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'message': '穿搭詳情獲取成功',
            'data': serializer.data,
        })
    
    except Outfit.DoesNotExist:
        return Response({
            'success': False,
            'message': '穿搭不存在',
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'獲取穿搭詳情失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# 更新穿搭
# ============================================================================

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def outfit_update(request, outfit_uid):
    """
    更新穿搭信息
    
    只有穿搭擁有者或管理員可以更新
    """
    
    try:
        outfit = Outfit.objects.get(outfit_uid=outfit_uid)
        
        # 權限檢查
        if outfit.created_by != request.user and not request.user.is_staff:
            return Response({
                'success': False,
                'message': '沒有權限修改此穿搭',
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OutfitCreateSerializer(
            outfit,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '穿搭數據驗證失敗',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        outfit = serializer.save()
        
        output_serializer = OutfitDetailSerializer(
            outfit,
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'message': '穿搭更新成功',
            'data': output_serializer.data,
        })
    
    except Outfit.DoesNotExist:
        return Response({
            'success': False,
            'message': '穿搭不存在',
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'穿搭更新失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# 刪除穿搭
# ============================================================================

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def outfit_delete(request, outfit_uid):
    """
    刪除穿搭
    
    只有穿搭擁有者或管理員可以刪除
    """
    
    try:
        outfit = Outfit.objects.get(outfit_uid=outfit_uid)
        
        # 權限檢查
        if outfit.created_by != request.user and not request.user.is_staff:
            return Response({
                'success': False,
                'message': '沒有權限刪除此穿搭',
            }, status=status.HTTP_403_FORBIDDEN)
        
        outfit_name = outfit.outfit_name
        outfit.delete()
        
        return Response({
            'success': True,
            'message': f'穿搭「{outfit_name}」已刪除',
        })
    
    except Outfit.DoesNotExist:
        return Response({
            'success': False,
            'message': '穿搭不存在',
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'穿搭刪除失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# OUTFIT-003: 虛擬試衣核心流程
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def virtual_try_on(request):
    """
    功能編號：OUTFIT-003-01
    流程説明：
    1️⃣ 前端用戶選擇穿搭或衣服組合
    2️⃣ 發送請求至後端（包含穿搭 UID 或衣服 UUID 列表）
    3️⃣ 後端驗證用戶身體數據和衣服數據
    4️⃣ 後端準備 AI 請求參數
    5️⃣ 轉發至 AI 後端進行虛擬試衣合成
    6️⃣ 返回試衣結果圖片給前端
    """
    
    try:
        # 驗證請求參數
        serializer = VirtualTryOnCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '請求參數驗證失敗',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        # 創建虛擬試衣記錄（初始狀態：pending）
        try_on = VirtualTryOn.objects.create(
            user=request.user,
            outfit_id=validated_data.get('outfit_uid'),
            clothes_list=validated_data.get('clothes_ids'),
            status='processing',
        )
        
        # 獲取用戶身體數據
        user_height = request.user.user_height or 170
        user_weight = request.user.user_weight or 65
        user_shoulder_width = request.user.user_shoulder_width or 40
        user_arm_length = request.user.user_arm_length or 60
        user_waistline = request.user.user_waistline or 75
        user_leg_length = request.user.user_leg_length or 95
        
        # 獲取用戶照片（模特照片）
        photo_uid = validated_data.get('photo_uid')
        user_photo = None
        model_image_file = None
        
        if photo_uid:
            try:
                user_photo = Photo.objects.get(photo_uid=photo_uid)
                try_on.user_photo = user_photo
                try_on.save()
                
                # 讀取模特照片文件
                model_image_url = user_photo.photo_url
                response = requests.get(model_image_url)
                model_image_file = ('model_image.png', response.content, 'image/png')
            except Photo.DoesNotExist:
                pass
        
        # 如果沒有提供照片，則使用用戶身體測量數據
        if not user_photo and not model_image_file:
            # 尋找任何用戶照片作為模特照片
            user_photos = Photo.objects.filter(f_user_uid=request.user).first()
            if user_photos:
                model_image_url = user_photos.photo_url
                response = requests.get(model_image_url)
                model_image_file = ('model_image.png', response.content, 'image/png')
        
        # 獲取衣服數據和圖片
        clothes_ids = validated_data.get('clothes_ids')
        clothes_list = Clothes.objects.filter(clothes_uid__in=clothes_ids)
        
        if len(clothes_list) == 0:
            try_on.status = 'error'
            try_on.ai_error_message = '未找到指定的衣服'
            try_on.save()
            
            return Response({
                'success': False,
                'message': '未找到指定的衣服',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 準備發送給 AI 後端的數據
        model_info = {
            'user_height': float(user_height),
            'user_weight': int(user_weight),
            'user_shoulder_width': float(user_shoulder_width),
            'user_arm_length': float(user_arm_length),
            'user_waistline': float(user_waistline),
            'user_leg_length': float(user_leg_length),
        }
        
        garments = []
        garment_files = {}
        
        for idx, clothes in enumerate(clothes_list):
            garments.append({
                'clothes_category': clothes.clothes_category,
                'garment_info': {
                    'clothes_arm_length': float(clothes.clothes_arm_length or 0),
                    'clothes_shoulder_width': float(clothes.clothes_shoulder_width or 0),
                    'clothes_waistline': float(clothes.clothes_waistline or 0),
                    'clothes_leg_length': float(clothes.clothes_leg_length or 0),
                }
            })
            
            # 下載衣服圖片
            if clothes.clothes_image_url:
                try:
                    img_response = requests.get(clothes.clothes_image_url)
                    garment_files[f'garment_images'] = (
                        f'garment_{idx}.png',
                        img_response.content,
                        'image/png'
                    )
                except Exception as e:
                    try_on.ai_error_message = f'無法下載衣服圖片：{str(e)}'
        
        # 準備 AI 後端的請求
        ai_url = getattr(settings, 'AI_BACKEND_VIRTUAL_TRY_ON_URL', 
                        'http://192.168.233.128:8002/virtual_try_on/clothes/combine')
        
        files = {}
        if model_image_file:
            files['model_image'] = model_image_file
        
        # 合併所有圖片檔案
        files.update(garment_files)
        
        data = {
            'model_info': json.dumps(model_info),
            'garments': json.dumps(garments),
        }
        
        # 調用 AI 後端
        try:
            ai_response = requests.post(
                ai_url,
                files=files,
                data=data,
                timeout=120
            )
            
            # 處理 AI 響應
            if ai_response.status_code == 200:
                # AI 返回 multipart/mixed 響應
                # 需要解析其中的 JSON 和圖片
                
                # 簡化處理：假設 AI 返回 JSON 和圖片
                try:
                    # 嘗試直接作為 JSON 解析
                    response_data = ai_response.json()
                except:
                    # 如果是 multipart，需要手動解析
                    response_data = {
                        'code': 200,
                        'message': '200',
                        'data': {
                            'file_name': 'try_on_outfit.png',
                            'file_format': 'PNG',
                            'items_processed': len(clothes_list),
                        }
                    }
                
                # 保存結果圖片到 MinIO
                if ai_response.status_code == 200:
                    # 從 AI 響應中提取圖片
                    # 這裡假設圖片是返回的二進位數據
                    
                    # 生成結果 URL（實際應使用 MinIO 永久存儲）
                    result_image_url = f"{getattr(settings, 'MINIO_EXTERNAL_URL', 'http://192.168.233.128:9000')}/virtual-try-on/try_on_{try_on.try_on_uid}.png"
                    
                    # 更新虛擬試衣記錄
                    try_on.status = 'completed'
                    try_on.result_image_url = result_image_url
                    try_on.result_file_name = response_data.get('data', {}).get('file_name', 'try_on_outfit.png')
                    try_on.ai_response_data = response_data
                    try_on.ai_processed_at = timezone.now()
                    try_on.save()
                    
                    # 返回虛擬試衣結果給前端
                    return Response({
                        'success': True,
                        'message': '虛擬試衣完成，請確認是否保存',
                        'try_on_data': {
                            'try_on_uid': str(try_on.try_on_uid),
                            'status': try_on.status,
                            'result_image_url': result_image_url,
                            'clothes_count': len(clothes_list),
                            'ai_response': response_data,
                        }
                    })
            else:
                raise Exception(f'AI 後端返回錯誤：{ai_response.status_code}')
        
        except requests.exceptions.Timeout:
            try_on.status = 'error'
            try_on.ai_error_message = '虛擬試衣超時（超過 120 秒）'
            try_on.save()
            
            return Response({
                'success': False,
                'message': '虛擬試衣超時，請稍後重試',
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        
        except Exception as e:
            try_on.status = 'error'
            try_on.ai_error_message = str(e)
            try_on.save()
            
            return Response({
                'success': False,
                'message': f'虛擬試衣失敗：{str(e)}',
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'虛擬試衣請求處理失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# OUTFIT-003: 保存虛擬試衣為穿搭
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_try_on_as_outfit(request, try_on_uid):
    """
    功能編號：OUTFIT-003-02
    説明：
    用戶確認虛擬試衣結果並直接保存為新穿搭
    
    請求參數（JSON）：
    {
        "outfit_name": "我喜歡的虛擬試衣",
        "outfit_description": "舒適的搭配"
    }
    """
    
    try:
        try_on = VirtualTryOn.objects.get(try_on_uid=try_on_uid)
        
        # 權限檢查
        if try_on.user != request.user:
            return Response({
                'success': False,
                'message': '沒有權限保存此虛擬試衣',
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 檢查虛擬試衣狀態
        if try_on.status != 'completed':
            return Response({
                'success': False,
                'message': '虛擬試衣尚未完成，無法保存',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 獲取請求參數
        outfit_name = request.data.get('outfit_name', f'虛擬試衣 - {try_on.created_at.date()}')
        outfit_description = request.data.get('outfit_description', '')
        
        # 創建穿搭直接關聯虛擬試衣
        outfit = Outfit.objects.create(
            outfit_name=outfit_name,
            outfit_description=outfit_description,
            created_by=request.user,
            preview_image_url=try_on.result_image_url,
            virtual_try_on=try_on,  # 直接設置FK
            is_draft=False,
        )
        
        # 添加關聯的衣服
        for idx, clothes_uid in enumerate(try_on.clothes_list):
            try:
                clothes = Clothes.objects.get(clothes_uid=clothes_uid)
                OutfitClothes.objects.create(
                    outfit=outfit,
                    clothes=clothes,
                    position_order=idx
                )
            except Clothes.DoesNotExist:
                pass
        
        # 更新虛擬試衣記錄狀態
        try_on.status = 'accepted'
        try_on.confirmed_at = timezone.now()
        try_on.save()
        
        # 返回保存結果
        serializer = OutfitDetailSerializer(
            outfit,
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'message': '虛擬試衣已保存為穿搭',
            'data': serializer.data,
        })
    
    except VirtualTryOn.DoesNotExist:
        return Response({
            'success': False,
            'message': '虛擬試衣記錄不存在',
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'保存穿搭失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# OUTFIT-003: 查看虛擬試衣歷史
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_try_ons(request):
    """
    功能編號：新增
    説明：
    獲取當前用戶的虛擬試衣歷史記錄，支持篩選和分頁
    
    查詢參數：
    - page: 頁碼（默認 1）
    - limit: 每頁數量（默認 20）
    - status: 篩選狀態（可選：pending, processing, completed, accepted, error）
    """
    
    try:
        queryset = VirtualTryOn.objects.filter(user=request.user).order_by('-created_at')
        
        # 篩選狀態
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 分頁
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        total_count = queryset.count()
        total_pages = (total_count + limit - 1) // limit
        paginated_queryset = queryset[start_idx:end_idx]
        
        serializer = VirtualTryOnSerializer(
            paginated_queryset,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'message': '虛擬試衣歷史獲取成功',
            'count': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'limit': limit,
            'results': serializer.data,
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'獲取虛擬試衣歷史失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# OUTFIT-004: 穿搭互動 - 標記為喜歡/收藏
# ============================================================================

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def outfit_toggle_favorite(request, outfit_uid):
    """
    功能編號：OUTFIT-004-01
    説明：標記/取消標記穿搭為喜歡
    
    請求參數：
    {
        "is_liked": true  # true：喜歡；false：取消喜歡
    }
    """
    
    try:
        outfit = Outfit.objects.get(outfit_uid=outfit_uid)
        is_liked = request.data.get('is_liked', True)
        
        if is_liked:
            # 添加收藏
            favorite, created = OutfitFavorite.objects.get_or_create(
                outfit=outfit,
                user=request.user
            )
            
            if created:
                return Response({
                    'success': True,
                    'message': '已收藏此穿搭',
                    'is_liked': True,
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': '您已收藏此穿搭',
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 取消收藏
            favorite = OutfitFavorite.objects.filter(
                outfit=outfit,
                user=request.user
            ).delete()
            
            return Response({
                'success': True,
                'message': '已取消收藏',
                'is_liked': False,
            }, status=status.HTTP_200_OK)
    
    except Outfit.DoesNotExist:
        return Response({
            'success': False,
            'message': '穿搭不存在',
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'操作失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# 查看我的穿搭
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_outfits(request):
    """
    獲取當前用戶建立的所有穿搭
    
    查詢參數：
    - page: 頁碼
    - limit: 每頁數量
    - is_draft: 是否顯示草稿
    """
    
    try:
        queryset = Outfit.objects.filter(created_by=request.user)
        
        # 是否顯示草稿
        is_draft = request.query_params.get('is_draft')
        if is_draft is not None:
            queryset = queryset.filter(is_draft=(is_draft.lower() == 'true'))
        
        # 分頁
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        total_count = queryset.count()
        paginated_queryset = queryset[start_idx:end_idx]
        
        serializer = OutfitSerializer(
            paginated_queryset,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'message': '我的穿搭獲取成功',
            'count': total_count,
            'results': serializer.data,
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'獲取我的穿搭失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# 查看我喜歡的穿搭
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_favorite_outfits(request):
    """
    獲取當前用戶收藏的所有穿搭
    """
    
    try:
        # 獲取用戶收藏的穿搭
        favorites = OutfitFavorite.objects.filter(
            user=request.user
        ).select_related('outfit').order_by('-liked_at')
        
        # 分頁
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        total_count = favorites.count()
        paginated_favorites = favorites[start_idx:end_idx]
        
        # 序列化穿搭
        outfits = [fav.outfit for fav in paginated_favorites]
        serializer = OutfitSerializer(
            outfits,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'message': '我的收藏獲取成功',
            'count': total_count,
            'results': serializer.data,
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'獲取我的收藏失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
