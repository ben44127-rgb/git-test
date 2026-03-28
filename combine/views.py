"""
Views for Virtual Try-On API
虛擬試衣管理的視圖

主要功能：
1. Feature 3.1：發起虛擬試衣
2. 查看我的試穿歷史
3. 查看試穿詳情
"""

import json
import re
import logging
import requests
from io import BytesIO
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from minio import Minio
from minio.error import S3Error

from .models import Model
from .serializers import VirtualTryOnCreateSerializer, ModelSerializer
from accounts.models import Clothes, User

logger = logging.getLogger(__name__)


def _extract_filename(content_disposition, default_name='try_on_outfit.png'):
    """從 Content-Disposition 取出檔名。"""
    if not content_disposition:
        return default_name
    match = re.search(r'filename="?([^";]+)"?', content_disposition)
    if match:
        return match.group(1)
    return default_name


def _parse_multipart_mixed_response(ai_response):
    """
    解析 AI 回傳的 multipart/mixed 響應。
    返回：json_data, image_bytes, image_filename
    """
    content_type = ai_response.headers.get('Content-Type', '')
    match = re.search(r'boundary="?([^";]+)"?', content_type)
    if not match:
        raise ValueError('AI 回應缺少 multipart boundary')

    boundary = match.group(1).encode('utf-8')
    delimiter = b'--' + boundary
    parts = ai_response.content.split(delimiter)

    json_data = None
    image_bytes = None
    image_filename = 'try_on_outfit.png'

    for raw_part in parts:
        part = raw_part.strip()
        if not part or part == b'--':
            continue
        if part.endswith(b'--'):
            part = part[:-2].strip()

        if b'\r\n\r\n' in part:
            headers_blob, body_blob = part.split(b'\r\n\r\n', 1)
        elif b'\n\n' in part:
            headers_blob, body_blob = part.split(b'\n\n', 1)
        else:
            continue

        headers_text = headers_blob.decode('utf-8', errors='ignore')
        headers_lower = headers_text.lower()
        body = body_blob.strip(b'\r\n')

        if 'application/json' in headers_lower:
            json_data = json.loads(body.decode('utf-8', errors='ignore'))
        elif 'image/png' in headers_lower or 'application/octet-stream' in headers_lower:
            image_bytes = body
            content_disposition = ''
            for line in headers_text.splitlines():
                if line.lower().startswith('content-disposition:'):
                    content_disposition = line
                    break
            image_filename = _extract_filename(content_disposition, image_filename)

    if json_data is None:
        raise ValueError('AI multipart 回應缺少 JSON metadata')

    return json_data, image_bytes, image_filename


# ============================================================================
# Feature 3.1: 虛擬試衣核心功能
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def virtual_try_on(request):
    """
    功能編號：Feature 3.1 - 虛擬試衣
    
    流程説明：
    1️⃣ 前端用戶選擇衣服組合（必須恰好 2 件）
    2️⃣ 發送請求至後端
    3️⃣ 後端驗證用戶身體數據和衣服數據
    4️⃣ 後端準備 AI 請求參數
    5️⃣ 轉發至 AI 後端進行虛擬試衣合成
    6️⃣ AI 返回試衣結果圖片
    7️⃣ 直接保存結果到 Model 表
    8️⃣ 返回試穿結果給前端
    
    請求參數（JSON）：
    {
        "clothes_ids": ["uuid1", "uuid2"]
    }
    
    返回示例：
    {
        "success": true,
        "message": "虛擬試穿完成",
        "model_data": {
            "model_uid": "xxx",
            "f_user_uid": "xxx",
            "status": "completed",
            "model_picture": "http://minio:9000/...",
            "model_style": ["Japanese Style", "Elegant"],
            "clothes_count": 2,
            "ai_response": {...}
        }
    }
    """
    
    try:
        serializer = VirtualTryOnCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '請求參數驗證失敗',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        clothes_ids = [str(uid) for uid in validated_data.get('clothes_ids', [])]

        # 用戶身體測量資訊（若未填則給預設值）
        model_info = {
            'user_height': float(request.user.user_height or 170),
            'user_weight': int(request.user.user_weight or 65),
            'user_shoulder_width': float(request.user.user_shoulder_width or 40),
            'user_arm_length': float(request.user.user_arm_length or 60),
            'user_waistline': float(request.user.user_waistline or 75),
            'user_leg_length': float(request.user.user_leg_length or 95),
        }

        # 依照輸入順序載入衣服資料
        clothes_qs = Clothes.objects.filter(
            clothes_uid__in=clothes_ids,
            f_user_uid=str(request.user.user_uid)
        )
        clothes_map = {str(item.clothes_uid): item for item in clothes_qs}
        ordered_clothes = [clothes_map.get(cid) for cid in clothes_ids]

        if any(item is None for item in ordered_clothes):
            return Response({
                'success': False,
                'message': '衣服不存在或不屬於當前使用者',
            }, status=status.HTTP_403_FORBIDDEN)

        # 獲取用戶模特照片（直接從 User.user_image_url）
        if not request.user.user_image_url:
            return Response({
                'success': False,
                'message': '用戶未設定模特照片',
                'error_code': 'USER_MODEL_IMAGE_NOT_SET',
                'hint': '請先設定 user_image_url',
            }, status=status.HTTP_400_BAD_REQUEST)

        model_image_url = request.user.user_image_url
        
        # ⚠️ 檢測 localhost URL（Docker 容器內無法訪問）
        if 'localhost:9000' in model_image_url or 'localhost:9001' in model_image_url:
            model_image_url = model_image_url.replace('localhost:9000', 'minio:9000').replace('localhost:9001', 'minio:9001')
            logger.warning(f'檢測到 localhost URL，已轉換為容器內 URL: {model_image_url}')
        
        # 嘗試下載模特照片
        try:
            model_img_resp = requests.get(model_image_url, timeout=30)
            model_img_resp.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            return Response({
                'success': False,
                'message': '無法訪問模特照片 URL',
                'error_code': 'MODEL_IMAGE_CONNECTION_ERROR',
                'hint': 'user_image_url 可能使用了 localhost:9000，請改用 http://minio:9000',
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except requests.exceptions.Timeout:
            return Response({
                'success': False,
                'message': '下載模特照片超時',
                'error_code': 'MODEL_IMAGE_TIMEOUT',
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        
        model_content_type = model_img_resp.headers.get('Content-Type', 'image/png')

        # 準備衣服資料
        garments = []
        for idx, clothes in enumerate(ordered_clothes):
            try:
                garment_resp = requests.get(clothes.clothes_image_url, timeout=30)
                garment_resp.raise_for_status()
            except requests.exceptions.RequestException as e:
                return Response({
                    'success': False,
                    'message': f'無法下載衣服圖片：{clothes.clothes_uid}',
                    'error_detail': str(e),
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            garment_type = 'bottom' if idx == 1 else 'top'
            garments.append({
                'type': garment_type,
                'image': ('garment.png', garment_resp.content, 'image/png'),
            })

        # 準備 AI 請求
        ai_url = getattr(settings, 'AI_BACKEND_VIRTUAL_TRY_ON_URL', 'http://172.17.0.1:8002/virtual_try_on/clothes/combine')
        
        ai_files = {
            'model_image': ('model.png', model_img_resp.content, model_content_type),
        }
        for i, (gtype, gimg) in enumerate([(g['type'], g['image']) for g in garments]):
            ai_files[f'garment_{i}'] = gimg

        ai_payload = {
            'model_info': json.dumps(model_info, ensure_ascii=False),
            'garments': json.dumps([{'type': g['type']} for g in garments], ensure_ascii=False),
        }

        # 調用 AI 後端
        ai_response = requests.post(
            ai_url,
            files=ai_files,
            data=ai_payload,
            timeout=120,
        )

        if ai_response.status_code != 200:
            try:
                error_data = ai_response.json()
            except:
                error_data = {'message': ai_response.text}
            
            return Response({
                'success': False,
                'message': f'AI 後端返回錯誤：{ai_response.status_code}',
                'ai_error': error_data,
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        response_data = None
        image_bytes = None
        image_file_name = 'try_on_outfit.png'

        content_type = ai_response.headers.get('Content-Type', '').lower()
        if 'multipart/mixed' in content_type:
            response_data, image_bytes, image_file_name = _parse_multipart_mixed_response(ai_response)
        else:
            response_data = ai_response.json()

        ai_message = str(response_data.get('message', ''))
        if ai_message != '200':
            return Response({
                'success': False,
                'message': f'AI 回傳失敗代碼：{ai_message}',
                'ai_response': response_data,
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        file_name_from_ai = response_data.get('data', {}).get('file_name') or image_file_name
        safe_file_name = f"try_on_{request.user.user_uid}_{timezone.now().timestamp()}.png"

        # ✅ 上傳到 MinIO
        result_image_url = None
        if image_bytes:
            try:
                minio_client = Minio(
                    settings.MINIO_ENDPOINT,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=settings.MINIO_SECURE
                )
                
                bucket_name = settings.MINIO_BUCKET_NAME
                if not minio_client.bucket_exists(bucket_name):
                    minio_client.make_bucket(bucket_name)
                
                minio_object_name = f"virtual-try-on/{safe_file_name}"
                minio_client.put_object(
                    bucket_name,
                    minio_object_name,
                    BytesIO(image_bytes),
                    len(image_bytes),
                    content_type='image/png'
                )
                
                minio_external_url = getattr(settings, 'MINIO_EXTERNAL_URL', 'http://minio:9000')
                result_image_url = f"{minio_external_url}/{bucket_name}/{minio_object_name}"
                
            except S3Error as minio_error:
                logger.error(f"MinIO 上傳失敗：{minio_error}，使用備用 URL")
                result_image_url = None
            except Exception as e:
                logger.error(f"MinIO 初始化失敗：{e}，使用備用 URL")
                result_image_url = None

        # 若 MinIO 上傳失敗，使用備用 URL
        if not result_image_url:
            result_image_url = (
                f"{getattr(settings, 'MINIO_EXTERNAL_URL', 'http://minio:9000')}"
                f"/{settings.MINIO_BUCKET_NAME}/virtual-try-on/{safe_file_name}"
            )

        # 構建衣服清單
        clothes_list = []
        for idx, clothes in enumerate(ordered_clothes):
            clothes_list.append({
                'position': idx + 1,
                'clothes_uid': str(clothes.clothes_uid),
                'clothes_category': clothes.clothes_category,
                'clothes_image_url': clothes.clothes_image_url,
            })
        
        # 直接保存到 Model 表
        model_style = response_data.get('data', {}).get('style_name', [])
        model_result = Model.objects.create(
            f_user_uid=str(request.user.user_uid),
            model_uid=f"{request.user.user_uid}_{timezone.now().timestamp()}",
            model_picture=result_image_url,
            model_style=model_style,
            clothes_list=clothes_list,
            ai_response_data=response_data,
        )

        return Response({
            'success': True,
            'message': '虛擬試穿完成',
            'model_data': {
                'model_uid': str(model_result.model_uid),
                'f_user_uid': str(request.user.user_uid),
                'status': 'completed',
                'model_picture': result_image_url,
                'model_style': model_style,
                'clothes_count': len(ordered_clothes),
                'ai_response': response_data,
            }
        }, status=status.HTTP_200_OK)

    except requests.exceptions.Timeout:
        return Response({
            'success': False,
            'message': '虛擬試穿超時，請稍後重試',
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)

    except requests.exceptions.RequestException as e:
        return Response({
            'success': False,
            'message': f'無法連接 AI 後端：{str(e)}',
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    except Exception as e:
        logger.error(f'虛擬試穿處理失敗：{str(e)}')
        return Response({
            'success': False,
            'message': f'虛擬試穿請求處理失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# 查看我的試穿歷史
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_try_ons(request):
    """
    查看當前用戶的虛擬試穿歷史
    
    查詢參數：
    - page: 頁碼（默認 1）
    - limit: 每頁數量（默認 20）
    """
    
    try:
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        queryset = Model.objects.filter(
            f_user_uid=str(request.user.user_uid)
        ).order_by('-model_created_time')
        
        total_count = queryset.count()
        total_pages = (total_count + limit - 1) // limit
        
        paginated_queryset = queryset[start_idx:end_idx]
        serializer = ModelSerializer(paginated_queryset, many=True)
        
        return Response({
            'success': True,
            'message': '試穿歷史獲取成功',
            'count': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'limit': limit,
            'results': serializer.data,
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'獲取試穿歷史失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# 查看單筆試穿詳情
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_try_on_detail(request, model_uid):
    """
    查看單個試穿結果的詳細信息
    
    路徑參數：
    - model_uid: 試穿結果 UUID
    """
    
    try:
        model = Model.objects.get(model_uid=model_uid, f_user_uid=str(request.user.user_uid))
        serializer = ModelSerializer(model)
        
        return Response({
            'success': True,
            'message': '試穿詳情獲取成功',
            'data': serializer.data,
        })
    
    except Model.DoesNotExist:
        return Response({
            'success': False,
            'message': '試穿紀錄不存在或沒有權限訪問',
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'獲取試穿詳情失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
