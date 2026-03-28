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


def _convert_url_for_container(url):
    """
    將容器外部的 URL 轉換為容器內部可訪問的 URL。
    
    在 Docker 容器內部：
    - localhost:9000 不可訪問，需要改用 minio:9000
    - 192.168.x.x 可能不可訪問，需要改用 minio:9000 
    """
    if not url:
        return url
    
    url_lower = url.lower()
    
    # 轉換 localhost/127.0.0.1
    if 'localhost:' in url_lower or '127.0.0.1:' in url_lower:
        # 替換所有可能的 localhost/127.0.0.1 引用
        url = url.replace('localhost:', 'minio:').replace('localhost/', 'minio/')
        url = url.replace('127.0.0.1:', 'minio:').replace('127.0.0.1/', 'minio/')
        logger.warning(f'轉換 localhost/127.0.0.1 為 minio: {url}')
        return url
    
    # 轉換 IP 地址（192.168.x.x 或其他內網/外網 IP）到 minio
    if 'minio' not in url_lower:
        # 檢查是否是 IP 地址引用
        import re
        ip_pattern = r'http[s]?://(?:\d+\.\d+\.\d+\.\d+|[^:/]+):\d+/.*minio'
        if not re.match(ip_pattern, url, re.IGNORECASE):
            # 如果包含特定的 IP 地址，轉換為 minio
            url_temp = re.sub(
                r'http[s]?://(?:\d+\.\d+\.\d+\.\d+|[^:]+):(\d+)',
                lambda m: f'http://minio:{m.group(1)}',
                url
            )
            if url_temp != url:
                logger.warning(f'轉換外部 URL 為內部 URL: {url} -> {url_temp}')
                return url_temp
    
    return url


def _download_image_with_fallback(url, timeout=30):
    """
    嘗試下載圖片，如果失敗則嘗試轉換 URL 後重新下載。
    
    返回：response 物件
    拋出：requests.exceptions.RequestException
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.ConnectionError:
        # 嘗試轉換 URL 後重新下載
        converted_url = _convert_url_for_container(url)
        if converted_url != url:
            logger.info(f'原始 URL 連接失敗，嘗試轉換 URL：{url} -> {converted_url}')
            response = requests.get(converted_url, timeout=timeout)
            response.raise_for_status()
            return response
        else:
            raise


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
    
    自動使用原始圖片給 AI 後端：
    - 模特圖片：優先使用 user_original_image_url（原始模特照片）
    - 衣服圖片：優先使用 clothes_original_image_url（原始衣服照片）
    
    返回給前端的預覽圖片：
    - 模特圖片：user_image_url（處理後）
    - 衣服圖片：clothes_image_url（去背圖）
    
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
        
        # AI 後端合成使用原始圖片
        logger.info(f"🎨 虛擬試穿配置：")
        logger.info(f"   AI 後端使用：原始模特照片 + 原始衣服照片")
        logger.info(f"   前端預覽：處理後模特照片 + 去背衣服圖片")

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

        # 獲取用戶模特照片
        # 🔑 優先使用原始照片給 AI 後端合成
        if request.user.user_original_image_url:
            model_image_url = _convert_url_for_container(request.user.user_original_image_url)
            logger.info(f"📸 使用原始模特照片進行 AI 後端合成")
        elif request.user.user_image_url:
            model_image_url = _convert_url_for_container(request.user.user_image_url)
            logger.warning(f"⚠️  原始模特照片不存在，使用現有照片")
        else:
            return Response({
                'success': False,
                'message': '用戶未設定模特照片',
                'error_code': 'USER_MODEL_IMAGE_NOT_SET',
                'hint': '請先設定 user_original_image_url 或 user_image_url',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 嘗試下載模特照片
        try:
            model_img_resp = _download_image_with_fallback(model_image_url, timeout=30)
        except requests.exceptions.ConnectionError as e:
            logger.error(f'❌ 無法連接到模特照片 URL：{model_image_url}，錯誤：{e}')
            return Response({
                'success': False,
                'message': '無法訪問模特照片 URL',
                'error_code': 'MODEL_IMAGE_CONNECTION_ERROR',
                'hint': 'user_image_url 可能配置不正確。在 Docker 容器內，必須使用 minio:9000 而不是 localhost:9000',
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except requests.exceptions.Timeout as e:
            logger.error(f'❌ 下載模特照片超時：{model_image_url}')
            return Response({
                'success': False,
                'message': '下載模特照片超時',
                'error_code': 'MODEL_IMAGE_TIMEOUT',
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.exceptions.RequestException as e:
            logger.error(f'❌ 下載模特照片失敗：{e}')
            return Response({
                'success': False,
                'message': f'下載模特照片失敗：{str(e)}',
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        model_content_type = model_img_resp.headers.get('Content-Type', 'image/png')

        # 準備衣服資料
        garments = []
        for idx, clothes in enumerate(ordered_clothes):
            try:
                # 🔑 優先使用原始圖片給 AI 後端合成
                # 如果原始圖不存在，才回退到去背圖
                if clothes.clothes_original_image_url:
                    clothes_image_to_use = clothes.clothes_original_image_url
                    image_type = "原始圖"
                    logger.info(f"   衣服 {idx+1}：使用 {image_type}（AI 後端合成用）")
                else:
                    clothes_image_to_use = clothes.clothes_image_url
                    image_type = "去背圖"
                    logger.warning(f"   衣服 {idx+1}：原始圖不存在，回退到 {image_type}")
                
                # 轉換衣服圖片 URL（如果需要）
                clothes_url = _convert_url_for_container(clothes_image_to_use)
                # 下載衣服圖片，並在失敗時重試
                garment_resp = _download_image_with_fallback(clothes_url, timeout=30)
            except requests.exceptions.ConnectionError as e:
                logger.error(f'❌ 無法連接到衣服圖片 URL：{clothes_image_to_use}')
                return Response({
                    'success': False,
                    'message': f'無法訪問衣服圖片：{clothes.clothes_uid}',
                    'error_code': 'CLOTHES_IMAGE_CONNECTION_ERROR',
                    'error_detail': str(e),
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except requests.exceptions.RequestException as e:
                logger.error(f'❌ 下載衣服圖片失敗：{clothes.clothes_uid}，錯誤：{e}')
                return Response({
                    'success': False,
                    'message': f'無法下載衣服圖片：{clothes.clothes_uid}',
                    'error_detail': str(e),
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            garment_type = 'bottom' if idx == 1 else 'top'
            garments.append({
                'type': garment_type,
                'image': ('garment.png', garment_resp.content, 'image/png'),
                'clothes': clothes,  # 保存衣服物件以便提取詳細信息
            })

        # 準備 AI 請求
        # 使用 settings 中定義的虛擬試穿完整 URL（自動拼接 AI_BACKEND_URL + AI_VIRTUAL_TRY_ON_FITTING_ENDPOINT）
        ai_url = settings.AI_VIRTUAL_TRY_ON_FITTING_URL
        
        # 準備 multipart files
        # 注意：requests 庫支持將 files 參數設為列表，以發送多個同名的 file fields
        ai_files_list = [
            ('model_image', ('model.png', model_img_resp.content, model_content_type)),
        ]
        
        # 添加衣服圖片到請求
        # 使用列表格式，重複使用 'garment_images' 作為鍵名
        for i, garment in enumerate(garments):
            gimg = garment['image']
            # 添加到列表（Flask 的 getlist('garment_images') 會接收所有這些值）
            ai_files_list.append(('garment_images', gimg))
            logger.info(f"📦 添加衣服圖片 {i}：{gimg[0]}，大小：{len(gimg[1])} bytes，類型：{garment['type']}")

        # 準備 garments 的詳細信息（根據 FUNCTIONS.md 規範）
        garments_data = []
        for idx, garment in enumerate(garments):
            clothes_obj = garment['clothes']
            garment_info = {
                'clothes_category': clothes_obj.clothes_category or 'clothing',
                'garment_info': {}
            }
            
            # 根據衣服類型添加相應的尺寸信息
            if idx == 0:  # top
                garment_info['garment_info']['clothes_arm_length'] = float(clothes_obj.clothes_arm_length or 0)
                garment_info['garment_info']['clothes_shoulder_width'] = float(clothes_obj.clothes_shoulder_width or 0)
            else:  # bottom
                garment_info['garment_info']['clothes_leg_length'] = float(clothes_obj.clothes_leg_length or 0)
                garment_info['garment_info']['clothes_waistline'] = float(clothes_obj.clothes_waistline or 0)
            
            garments_data.append(garment_info)

        ai_payload = {
            'model_info': json.dumps(model_info, ensure_ascii=False),
            'garments': json.dumps(garments_data, ensure_ascii=False),
        }

        logger.info(f"🤖 發送至 AI 後端：{ai_url}")
        logger.info(f"   Model image：{len(model_img_resp.content)} bytes")
        logger.info(f"   Garment images：{len(garments)} 件")
        logger.info(f"   AI files format：List with {len(ai_files_list)} multipart fields")
        logger.info(f"   Garments data：{json.dumps(garments_data, ensure_ascii=False)}")

        # 調用 AI 後端
        try:
            ai_response = requests.post(
                ai_url,
                files=ai_files_list,
                data=ai_payload,
                timeout=120,
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 調用 AI 後端失敗：{e}")
            return Response({
                'success': False,
                'message': f'AI 服務連接失敗：{str(e)}',
                'error_code': 'AI_CONNECTION_ERROR',
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

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
    查看當前用戶的虛擬試穿歷史 (功能編號: TRYON-002)
    
    query parameters:
    - page: 页数（默认 1）
    - limit: 每页数量（默认 20）
    
    示例：
    GET /combine/user/virtual-try-on-history?page=1&limit=20
    
    返回：
    {
        "success": true,
        "message": "试穿历史获取成功",
        "count": 12,
        "total_pages": 1,
        "current_page": 1,
        "limit": 20,
        "results": [
            {
                "model_uid": "...",
                "model_picture": "http://...",
                "model_style": ["Japanese Style", "Elegant"],
                "created_at": "2026-03-28T10:30:00Z"
            }
        ]
    }
    """
    
    try:
        # 分頁參數
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        
        # 驗證分頁參數
        if page < 1 or limit < 1:
            return Response({
                'success': False,
                'message': '頁碼和每頁數量必須大於 0',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # 構建查詢集（按創建時間倒序）
        queryset = Model.objects.filter(
            f_user_uid=str(request.user.user_uid)
        ).order_by('-model_created_time')
        
        # 計算分頁信息
        total_count = queryset.count()
        total_pages = (total_count + limit - 1) // limit
        
        # 驗證頁碼
        if page > total_pages and total_count > 0:
            return Response({
                'success': False,
                'message': f'頁碼超出範圍（總頁數：{total_pages}）',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 執行分頁查詢
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
        }, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response({
            'success': False,
            'message': f'參數格式錯誤：{str(e)}',
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"❌ 獲取試穿歷史失敗：{str(e)}")
        return Response({
            'success': False,
            'message': '獲取試穿歷史失敗',
            'error_detail': str(e),
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


# ============================================================================
# 刪除虛擬試穿結果
# ============================================================================

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_virtual_try_on(request, model_uid):
    """
    刪除一個虛擬試穿結果 (功能編號: TRYON-004)
    
    路徑參數：
    - model_uid: 試穿結果 UUID
    
    返回：
    - 成功: 200 OK
    - 失敗:
      - 404 Not Found: 試穿紀錄不存在或沒有權限
      - 500 Internal Server Error: 伺服器錯誤
    
    範例：
    DELETE /combine/user/virtual-try-on/<model_uid>
    """
    
    try:
        # 獲取試穿結果，確保用戶有權限（只能刪除自己的）
        try:
            model = Model.objects.get(
                model_uid=model_uid,
                f_user_uid=str(request.user.user_uid)
            )
        except Model.DoesNotExist:
            return Response({
                'success': False,
                'message': '試穿紀錄不存在或沒有權限刪除',
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 記錄刪除前的信息
        model_picture = model.model_picture
        model_id = model.model_id
        
        # 刪除試穿結果
        model.delete()
        
        logger.info(f"✅ 成功刪除試穿結果: model_uid={model_uid}, user_uid={request.user.user_uid}")
        
        # 嘗試刪除 MinIO 中的圖片（可選，防止儲存空間浪費）
        if model_picture:
            try:
                _delete_minio_file(model_picture)
                logger.info(f"✅ 已刪除 MinIO 中的圖片: {model_picture}")
            except Exception as e:
                # 圖片刪除失敗不影響整體刪除操作
                logger.warning(f"⚠️ 刪除 MinIO 圖片失敗，但試穿紀錄已刪除: {str(e)}")
        
        return Response({
            'success': True,
            'message': '試穿結果已成功刪除',
            'deleted_model_uid': model_uid,
            'deleted_model_id': model_id,
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"❌ 刪除試穿結果失敗：{str(e)}")
        return Response({
            'success': False,
            'message': f'刪除試穿結果失敗：{str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _delete_minio_file(file_url):
    """
    從 MinIO 中删除文件。
    
    參數：
    - file_url: MinIO 檔案 URL（完整 URL 或路徑）
    
    說明：
    - 如果文件已被刪除或不存在，不拋出錯誤
    - 在 try-except 中調用，不影響主操作
    """
    try:
        # 解析 MinIO URL 獲取 bucket 和 object name
        # 典型 URL: http://minio:9000/bucket-name/path/to/file.png
        # 或: http://192.168.233.128:9000/bucket-name/path/to/file.png
        
        if not file_url:
            return
        
        # 提取 bucket 和 object name
        # 移除協議
        url_without_protocol = file_url.split('://', 1)[1] if '://' in file_url else file_url
        # 分割 host 和 path
        parts = url_without_protocol.split('/', 1)
        if len(parts) < 2:
            return
        
        path_part = parts[1]
        # 分割 bucket 和 object name
        path_parts = path_part.split('/', 1)
        if len(path_parts) < 2:
            return
        
        bucket_name = path_parts[0]
        object_name = path_parts[1]
        
        # 創建 MinIO 客戶端並刪除
        minio_client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        
        try:
            minio_client.remove_object(bucket_name, object_name)
            logger.info(f"✅ MinIO 檔案已刪除: {bucket_name}/{object_name}")
        except S3Error as e:
            # 如果檔案不存在（errCode=NoSuchKey），不視為錯誤
            if e.code != 'NoSuchKey':
                raise
            logger.info(f"ℹ️ MinIO 檔案不存在，已忽略: {bucket_name}/{object_name}")
    
    except Exception as e:
        logger.warning(f"⚠️ 無法從 MinIO 刪除檔案: {str(e)}")
        # 不拋出異常，讓調用者決定是否處理
