"""
Django Views for Image Processing API
圖像處理 API 的 Django 視圖函數

這個檔案包含了所有的視圖函數（View Functions）
在 Django 中，視圖函數負責處理 HTTP 請求並返回 HTTP 響應

主要功能：
1. 接收前端上傳的圖片
2. 轉發給 AI 後端進行去背處理（virtual_try_on/clothes/remove_bg）
3. 解析 AI 返回的 multipart 回應（JSON 元數據 + 去背圖片）
4. 使用 AI 回傳的 file_name / file_format 儲存圖片到 MinIO
5. 將 clothes_category、style_name（3筆）、color_name（3筆）存入資料庫
6. 返回完整的狀態資訊給前端
"""

# ==========================================
# 【第一部分】匯入所需的函式庫
# ==========================================
import io                    # 用來處理二進位資料流
import os                    # 用來操作檔案系統
import json                  # 用來解析 JSON 資料
import requests              # 用來發送 HTTP 請求給 AI 後端
import uuid                  # 用來產生唯一的 ID
import logging               # 用來記錄日誌
from datetime import timedelta   # 用來設定時間差

# Django 相關匯入
from django.http import JsonResponse, HttpResponse  # Django 的響應物件
from django.views.decorators.csrf import csrf_exempt  # 用來停用 CSRF 保護
from django.views.decorators.http import require_http_methods  # 用來限制 HTTP 方法
from django.conf import settings  # 用來存取 Django 設定

# MinIO 相關匯入
from minio import Minio      # MinIO 的 Python 客戶端
from minio.error import S3Error  # MinIO 的錯誤類型

# Multipart 回應解析
from requests_toolbelt.multipart import decoder as multipart_decoder

# 資料庫模型匯入
from accounts.models import Clothes, Style, Color

# JWT 認證匯入
from rest_framework_simplejwt.authentication import JWTAuthentication

# 取得日誌記錄器
logger = logging.getLogger(__name__)

# ==========================================
# 【第二部分】初始化 MinIO 客戶端
# ==========================================
def get_minio_client():
    """
    取得 MinIO 客戶端實例
    這個函數負責建立和返回 MinIO 客戶端物件
    如果連接失敗，會返回 None
    
    重要：這個函數會在每次上傳時被呼叫，而不是在模組載入時
    這樣可以確保 MinIO 服務可用時能夠正常連接，
    即使在容器啟動時 MinIO 服務還未就緒
    """
    try:
        # 建立 MinIO 客戶端物件
        client = Minio(
            settings.MINIO_ENDPOINT,           # MinIO 伺服器位址
            access_key=settings.MINIO_ACCESS_KEY,  # 存取金鑰
            secret_key=settings.MINIO_SECRET_KEY,  # 秘密金鑰
            secure=settings.MINIO_SECURE       # 是否使用 HTTPS
        )
        
        # 檢查 Bucket 是否存在
        # Bucket 就像是 MinIO 裡的一個資料夾
        if not client.bucket_exists(settings.MINIO_BUCKET_NAME):
            # 如果不存在，就建立一個新的 Bucket
            client.make_bucket(settings.MINIO_BUCKET_NAME)
            logger.info(f"✅ 已建立 Bucket：{settings.MINIO_BUCKET_NAME}")
        else:
            logger.info(f"✅ Bucket 已存在：{settings.MINIO_BUCKET_NAME}")
        
        # 設定 Bucket CORS 配置，允許前端跨域訪問圖片
        try:
            from minio.commonconfig import CORSConfig
            cors_config = CORSConfig(
                [
                    {
                        "AllowedMethods": ["GET", "HEAD", "PUT", "POST"],
                        "AllowedOrigins": ["*"],
                        "AllowedHeaders": ["*"],
                        "ExposeHeaders": ["ETag", "x-amz-version-id"]
                    }
                ]
            )
            client.set_bucket_cors(settings.MINIO_BUCKET_NAME, cors_config)
            logger.info(f"✅ 已設定 Bucket CORS 配置")
        except Exception as cors_error:
            logger.warning(f"⚠️  設定 CORS 失敗（可能已設定）：{cors_error}")
        
        # 設定 Bucket 政策為公開讀取（不需要預簽名）
        try:
            import json
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{settings.MINIO_BUCKET_NAME}/*"
                    }
                ]
            }
            client.set_bucket_policy(settings.MINIO_BUCKET_NAME, json.dumps(policy))
            logger.info(f"✅ 已設定 Bucket 政策為公開讀取")
        except Exception as policy_error:
            logger.warning(f"⚠️  設定 Bucket 政策失敗（可能已設定）：{policy_error}")
        
        return client
        
    except Exception as e:
        # 如果連接失敗，記錄錯誤日誌並返回 None
        logger.error(f"❌ MinIO 初始化失敗：{e}")
        logger.error(f"   提示：請確認 MinIO 服務是否啟動，以及帳號密碼是否正確")
        return None

# ==========================================
# 【第三部分】健康檢查視圖
# ==========================================
@require_http_methods(["GET"])  # 只允許 GET 請求
def health_check(request):
    """
    健康檢查端點
    用來檢查服務是否正常運行
    
    請求方式：GET
    存取位址：http://localhost:30000/health
    
    返回範例：
    {
        "status": "healthy",
        "message": "服務運行正常"
    }
    """
    # 建立響應資料
    response_data = {
        "status": "healthy",
        "message": "服務運行正常"
    }
    
    # 返回 JSON 響應
    # JsonResponse 是 Django 提供的便捷函數，會自動設定 Content-Type 為 application/json
    return JsonResponse(response_data)

# ==========================================
# 【第四部分】圖片上傳和處理視圖
# ==========================================
@csrf_exempt  # 停用 CSRF 保護（因為這是 API 端點，通常透過 token 認證）
@require_http_methods(["POST"])  # 只允許 POST 請求
def upload_and_process(request):
    """
    處理圖片上傳和 AI 去背的主要視圖函數

    完整流程：
    1. 接收前端上傳的圖片和衣服尺寸參數（multipart/form-data）
    2. 將圖片和衣服尺寸參數轉發給 AI 後端（virtual_try_on/clothes/remove_bg）
    3. 解析 AI 返回的 multipart 回應（JSON 元數據 + 去背圖片）
    4. 使用 AI 回傳的 file_name / file_format 將圖片儲存到 MinIO
    5. 將 clothes_category、style_name（3筆）、color_name（3筆）和衣服尺寸存入資料庫
    6. 返回完整的狀態資訊給前端

    請求方式：POST
    Content-Type: multipart/form-data
    存取位址：http://localhost:30000/picture/clothes/

    請求參數：
    - image_data: 圖片檔案（multipart/form-data 格式）必填
    - clothes_arm_length: 衣服袖長（cm，整數，0-200）可選，默認0
    - clothes_leg_length: 衣服褲長（cm，整數，0-150）可選，默認0
    - clothes_shoulder_width: 衣服肩寬（cm，整數，0-200）可選，默認0
    - clothes_waistline: 衣服腰圍（cm，整數，0-300）可選，默認0
    - user_uid: 用戶 UID（字串，若有 JWT Token 則可省略）

    AI 後端位址：http://192.168.233.128:8002/virtual_try_on/clothes/remove_bg
    AI 請求格式：
    - clothes_image: 圖片檔案流
    - clothes_arm_length: 袖長（整數）
    - clothes_leg_length: 褲長（整數）
    - clothes_shoulder_width: 肩寬（整數）
    - clothes_waistline: 腰圍（整數）
    - user_uid: 用戶 UID

    AI 回應格式（multipart，boundary=bg_removal_boundary）：
    Part 1 - JSON 元數據:
    {
        "code": 200,
        "message": "Processing Success",
        "tools_status": {
            "rembg_engine": "success",
            "opencv_masking": "success",
            "gemini_consultant": "success"
        },
        "data": {
            "file_name": "cleaned_garment.png",
            "file_format": "PNG",
            "style_analysis": {
                "clothes_category": "T-shirt",
                "style_name": ["Casual", "Formal", "Streetwear"],
                "color_name": ["red", "blue", "green"]
            }
        }
    }
    Part 2 - 去背後的圖片二進位資料（processed_image）

    AI 響應狀態碼：
    - 200 OK: 去背成功
    - 415 Unsupported Media Type: 上傳非圖片檔案
    - 422 Unprocessable Entity: 圖片過於模糊
    - 500 Internal Server Error: AI 模型運算失敗
    """

    # ==========================================
    # 【步驟 1】接收前端上傳的圖片
    # ==========================================
    logger.info("=" * 50)
    logger.info("📥 收到新的圖片處理請求")

    # 檢查請求中是否包含圖片檔案
    if 'image_data' not in request.FILES:
        logger.error("❌ 請求中未找到 'image_data' 欄位")
        return JsonResponse(
            {
                "success": False,
                "message": "請上傳圖片檔案（欄位名稱：image_data）"
            },
            status=400
        )

    # 取得上傳的檔案物件
    image_file = request.FILES['image_data']

    logger.info(f"📷 接收到圖片")
    logger.info(f"   檔案大小：{image_file.size} bytes")
    logger.info(f"   內容類型：{image_file.content_type}")

    # ==========================================
    # 【步驟 1.5】取得 user_uid（從 JWT 或 POST 參數）
    # ==========================================
    user_uid = None

    # 嘗試從 JWT Token 取得用戶
    try:
        jwt_auth = JWTAuthentication()
        header = jwt_auth.get_header(request)
        if header:
            raw_token = jwt_auth.get_raw_token(header)
            validated_token = jwt_auth.get_validated_token(raw_token)
            user = jwt_auth.get_user(validated_token)
            user_uid = str(user.user_uid)
            logger.info(f"👤 從 JWT 取得用戶 UID：{user_uid}")
    except Exception as jwt_err:
        logger.debug(f"JWT 認證未通過：{jwt_err}")

    # 如果 JWT 沒有取得到，嘗試從 POST 參數取得
    if not user_uid:
        user_uid = request.POST.get('user_uid', '')

    if not user_uid:
        logger.error("❌ 無法取得 user_uid")
        return JsonResponse(
            {
                "success": False,
                "message": "請提供 user_uid 或使用 JWT 認證"
            },
            status=401
        )

    logger.info(f"👤 用戶 UID：{user_uid}")

    # ==========================================
    # 【步驟 1.6】提取衣服尺寸參數
    # ==========================================
    clothes_arm_length = request.POST.get('clothes_arm_length', 0)
    clothes_leg_length = request.POST.get('clothes_leg_length', 0)
    clothes_shoulder_width = request.POST.get('clothes_shoulder_width', 0)
    clothes_waistline = request.POST.get('clothes_waistline', 0)

    # 驗證和轉換為整數
    try:
        clothes_arm_length = int(clothes_arm_length) if clothes_arm_length else 0
        clothes_leg_length = int(clothes_leg_length) if clothes_leg_length else 0
        clothes_shoulder_width = int(clothes_shoulder_width) if clothes_shoulder_width else 0
        clothes_waistline = int(clothes_waistline) if clothes_waistline else 0
    except ValueError as e:
        logger.error(f"❌ 衣服尺寸參數格式錯誤：{e}")
        return JsonResponse(
            {
                "success": False,
                "message": "衣服尺寸參數必須為整數"
            },
            status=400
        )

    # 驗證尺寸範圍
    if clothes_arm_length < 0 or clothes_arm_length > 200:
        return JsonResponse(
            {
                "success": False,
                "message": "衣服袖長必須在 0 到 200 cm 之間"
            },
            status=400
        )
    if clothes_leg_length < 0 or clothes_leg_length > 150:
        return JsonResponse(
            {
                "success": False,
                "message": "衣服褲長必須在 0 到 150 cm 之間"
            },
            status=400
        )
    if clothes_shoulder_width < 0 or clothes_shoulder_width > 200:
        return JsonResponse(
            {
                "success": False,
                "message": "衣服肩寬必須在 0 到 200 cm 之間"
            },
            status=400
        )
    if clothes_waistline < 0 or clothes_waistline > 300:
        return JsonResponse(
            {
                "success": False,
                "message": "衣服腰圍必須在 0 到 300 cm 之間"
            },
            status=400
        )

    logger.info(f"👕 衣服尺寸參數：")
    logger.info(f"   袖長（arm_length）：{clothes_arm_length} cm")
    logger.info(f"   褲長（leg_length）：{clothes_leg_length} cm")
    logger.info(f"   肩寬（shoulder_width）：{clothes_shoulder_width} cm")
    logger.info(f"   腰圍（waistline）：{clothes_waistline} cm")

    # ==========================================
    # 【步驟 2】讀取圖片資料準備發送給 AI 後端
    # ==========================================
    try:
        image_file.seek(0)
        file_bytes = image_file.read()
        logger.info(f"✅ 圖片讀取成功，大小：{len(file_bytes)} bytes")
    except Exception as e:
        logger.error(f"❌ 讀取圖片失敗：{e}")
        return JsonResponse(
            {
                "success": False,
                "message": f"讀取圖片失敗：{str(e)}"
            },
            status=500
        )

    # ==========================================
    # 【步驟 3】將圖片發送給 AI 後端進行去背處理
    # ==========================================
    logger.info(f"🤖 開始呼叫 AI 後端：{settings.AI_BACKEND_URL}")

    try:
        # 準備發送給 AI 後端的資料
        # 包含 clothes_image 和衣服尺寸參數
        files = {
            'clothes_image': (image_file.name, file_bytes, image_file.content_type)
        }

        # 準備 data 字典（衣服尺寸和其他參數）
        data = {
            'clothes_arm_length': clothes_arm_length,
            'clothes_leg_length': clothes_leg_length,
            'clothes_shoulder_width': clothes_shoulder_width,
            'clothes_waistline': clothes_waistline,
            'user_uid': user_uid,
        }

        logger.info(f"📤 發送給 AI 後端的參數：{json.dumps(data, ensure_ascii=False)}")

        # 發送 POST 請求給 AI 後端（衣服去背處理）
        # 完整 URL: http://localhost:8002/virtual_try_on/clothes/remove_bg
        ai_remove_bg_url = f"{settings.AI_BACKEND_URL}/virtual_try_on/clothes/remove_bg"
        logger.info(f"🔗 完整 AI 端點 URL：{ai_remove_bg_url}")
        
        ai_response = requests.post(
            ai_remove_bg_url,
            files=files,
            data=data,
            timeout=120  # 120秒逾時（AI 處理可能較耗時）
        )

        ai_status_code = ai_response.status_code
        logger.info(f"✅ AI 後端響應狀態碼：{ai_status_code}")

        # ==========================================
        # 【步驟 4】根據 AI 返回的狀態碼進行處理
        # ==========================================

        # 狀態碼對應的訊息
        status_messages = {
            200: "去背成功",
            415: "上傳非圖片檔案",
            422: "圖片過於模糊",
            500: "AI 模型運算失敗"
        }

        ai_message = status_messages.get(ai_status_code, f"未知狀態碼：{ai_status_code}")

        # 如果 AI 處理失敗（狀態碼不是 200）
        if ai_status_code != 200:
            logger.error(f"❌ AI 處理失敗：{ai_message}")

            # 嘗試取得詳細錯誤資訊
            try:
                error_detail = ai_response.json()
                logger.error(f"   錯誤詳情：{error_detail}")
            except Exception:
                error_detail = ai_response.text[:200]
                logger.error(f"   原始響應：{error_detail}")

            return JsonResponse(
                {
                    "success": False,
                    "message": "AI 處理失敗",
                    "ai_status": {
                        "status_code": ai_status_code,
                        "message": ai_message
                    }
                },
                status=ai_status_code
            )

        # ==========================================
        # 【步驟 5】解析 AI 返回的 multipart 回應
        # ==========================================
        logger.info("🔍 開始解析 AI 返回的 multipart 回應...")

        content_type = ai_response.headers.get('Content-Type', '')
        logger.info(f"   AI 響應的 Content-Type: {content_type}")

        json_data = None
        processed_image = None

        if 'multipart' in content_type:
            # ---- 解析 multipart 回應 ----
            multipart_data = multipart_decoder.MultipartDecoder(
                ai_response.content, content_type
            )

            for part in multipart_data.parts:
                # 解析每個 part 的 headers
                part_content_type = ''
                part_disposition = ''
                for header_name, header_value in part.headers.items():
                    h_name = header_name.decode() if isinstance(header_name, bytes) else header_name
                    h_value = header_value.decode() if isinstance(header_value, bytes) else header_value
                    if h_name.lower() == 'content-type':
                        part_content_type = h_value
                    elif h_name.lower() == 'content-disposition':
                        part_disposition = h_value

                # 判斷 part 類型
                if 'application/json' in part_content_type:
                    json_data = json.loads(part.content.decode('utf-8'))
                    logger.info("✅ 解析到 JSON 元數據")
                elif 'image' in part_content_type or 'processed_image' in part_disposition:
                    processed_image = part.content
                    logger.info(f"✅ 解析到處理後圖片，大小：{len(processed_image)} bytes")
        else:
            # ---- 非 multipart 回應（向後兼容，嘗試當作純 JSON 或純圖片）----
            logger.warning("⚠️ AI 回應非 multipart 格式，嘗試向後兼容解析")
            try:
                json_data = ai_response.json()
                # 如果是純 JSON，圖片可能在其他地方
            except Exception:
                # 如果不是 JSON，把整個回應當作圖片
                processed_image = ai_response.content

        # 驗證是否成功取得所有資料
        if not json_data:
            logger.error("❌ AI 返回的資料缺少 JSON 元數據")
            return JsonResponse(
                {
                    "success": False,
                    "message": "AI 返回的資料格式錯誤：缺少 JSON 元數據"
                },
                status=500
            )

        if not processed_image or len(processed_image) == 0:
            logger.error("❌ AI 返回的圖片資料為空")
            return JsonResponse(
                {
                    "success": False,
                    "message": "AI 返回的圖片資料為空"
                },
                status=500
            )

        # ==========================================
        # 【步驟 5.5】提取 AI 回傳的元數據
        # ==========================================
        logger.info(f"📋 AI 回傳 JSON：{json.dumps(json_data, ensure_ascii=False)}")

        tools_status = json_data.get('tools_status', {})
        ai_data = json_data.get('data', {})
        file_name = ai_data.get('file_name', 'processed.png')
        file_format = ai_data.get('file_format', 'PNG').upper()

        # 提取風格分析資料
        style_analysis = ai_data.get('style_analysis', {})
        clothes_category = style_analysis.get('clothes_category', '')
        style_names_raw = style_analysis.get('style_name', [])
        color_names_raw = style_analysis.get('color_name', [])

        # 正規化為列表（支援陣列、逗號分隔字串、單一字串）
        def normalize_to_list(value):
            """將值正規化為列表"""
            if isinstance(value, list):
                return [str(v).strip() for v in value if str(v).strip()]
            if isinstance(value, str):
                if ',' in value:
                    return [s.strip() for s in value.split(',') if s.strip()]
                return [value.strip()] if value.strip() else []
            return []

        style_names = normalize_to_list(style_names_raw)
        color_names = normalize_to_list(color_names_raw)

        logger.info(f"   AI 指定檔案名稱：{file_name}")
        logger.info(f"   AI 指定檔案格式：{file_format}")
        logger.info(f"   衣服類別：{clothes_category}")
        logger.info(f"   風格列表（{len(style_names)} 筆）：{style_names}")
        logger.info(f"   顏色列表（{len(color_names)} 筆）：{color_names}")
        logger.info(f"   工具狀態：{tools_status}")

    except requests.exceptions.Timeout:
        logger.error("❌ AI 後端請求逾時（超過120秒）")
        return JsonResponse(
            {
                "success": False,
                "message": "AI 處理逾時",
                "ai_status": {
                    "status_code": 504,
                    "message": "請求逾時"
                }
            },
            status=504
        )
    except requests.exceptions.ConnectionError:
        logger.error("❌ 無法連接到 AI 後端")
        return JsonResponse(
            {
                "success": False,
                "message": "無法連接到 AI 服務",
                "ai_status": {
                    "status_code": 503,
                    "message": "服務不可用"
                }
            },
            status=503
        )
    except Exception as e:
        logger.error(f"❌ 呼叫 AI 後端時發生錯誤：{e}")
        return JsonResponse(
            {
                "success": False,
                "message": f"AI 服務呼叫失敗：{str(e)}",
                "ai_status": {
                    "status_code": 500,
                    "message": str(e)
                }
            },
            status=500
        )

    # ==========================================
    # 【步驟 6】使用 AI 回傳的 file_name / file_format 儲存到 MinIO
    # ==========================================
    logger.info("💾 開始上傳圖片到 MinIO...")

    # 根據 file_format 決定副檔名和 content_type
    format_mapping = {
        'PNG':  {'ext': '.png',  'content_type': 'image/png'},
        'JPEG': {'ext': '.jpg',  'content_type': 'image/jpeg'},
        'JPG':  {'ext': '.jpg',  'content_type': 'image/jpeg'},
        'WEBP': {'ext': '.webp', 'content_type': 'image/webp'},
        'GIF':  {'ext': '.gif',  'content_type': 'image/gif'},
    }
    format_info = format_mapping.get(file_format, {'ext': '.png', 'content_type': 'image/png'})

    # 產生唯一檔案名稱：使用 AI 回傳的 file_name + 唯一前綴
    unique_id = uuid.uuid4().hex[:8]
    base_name = file_name.rsplit('.', 1)[0] if '.' in file_name else file_name
    # ==========================================
    # 修改：衣服圖片放在 clothes/ 資料夾下
    # ==========================================
    unique_filename = f"clothes/{unique_id}_{base_name}{format_info['ext']}"
    logger.info(f"   MinIO 檔案名稱（含資料夾）：{unique_filename}")

    # 取得 MinIO 客戶端
    minio_client = get_minio_client()

    if minio_client is None:
        logger.error("❌ MinIO 客戶端不可用")
        return JsonResponse(
            {
                "success": False,
                "message": "儲存服務不可用",
                "ai_status": {
                    "status_code": 200,
                    "message": "去背成功",
                    "tools_status": tools_status,
                },
                "storage_status": {
                    "success": False,
                    "message": "MinIO 服務不可用"
                }
            },
            status=503
        )

    # 上傳到 MinIO
    try:
        file_data = io.BytesIO(processed_image)
        file_length = len(processed_image)

        minio_client.put_object(
            settings.MINIO_BUCKET_NAME,
            unique_filename,
            file_data,
            file_length,
            content_type=format_info['content_type']
        )

        logger.info(f"✅ 成功上傳到 MinIO：{settings.MINIO_BUCKET_NAME}/{unique_filename}")

    except S3Error as e:
        logger.error(f"❌ 上傳到 MinIO 失敗：{e}")
        return JsonResponse(
            {
                "success": False,
                "message": "圖片儲存失敗",
                "ai_status": {
                    "status_code": 200,
                    "message": "去背成功",
                    "tools_status": tools_status,
                },
                "storage_status": {
                    "success": False,
                    "message": f"MinIO 上傳失敗：{str(e)}"
                }
            },
            status=500
        )
    except Exception as e:
        logger.error(f"❌ 上傳過程發生錯誤：{e}")
        return JsonResponse(
            {
                "success": False,
                "message": "圖片儲存失敗",
                "ai_status": {
                    "status_code": 200,
                    "message": "去背成功",
                    "tools_status": tools_status,
                },
                "storage_status": {
                    "success": False,
                    "message": str(e)
                }
            },
            status=500
        )

    # ==========================================
    # 【步驟 7】產生預簽名 URL
    # ==========================================
    try:
        presigned_url = minio_client.presigned_get_object(
            settings.MINIO_BUCKET_NAME,
            unique_filename,
            expires=timedelta(days=7)
        )

        logger.info(f"✅ 原始預簽名 URL：{presigned_url[:100]}...")

        # 將內部地址轉換為外部地址
        replacements = [
            ('http://minio:9000', settings.MINIO_EXTERNAL_URL),
            ('https://minio:9000', settings.MINIO_EXTERNAL_URL.replace('http://', 'https://')),
            ('http://minio/', settings.MINIO_EXTERNAL_URL + '/'),
        ]

        for old_url, new_url in replacements:
            if old_url in presigned_url:
                presigned_url = presigned_url.replace(old_url, new_url)
                logger.info(f"✅ 已將 '{old_url}' 轉換為 '{new_url}'")
                break

        # 產生公開 URL
        public_url = f"{settings.MINIO_EXTERNAL_URL}/{settings.MINIO_BUCKET_NAME}/{unique_filename}"
        logger.info(f"✅ 公開 URL：{public_url[:100]}...")

    except Exception as e:
        logger.error(f"❌ 產生 URL 失敗：{e}")
        presigned_url = None
        public_url = None

    image_url = public_url or presigned_url or ''

    # ==========================================
    # 【步驟 8】儲存到資料庫（Clothes、Style、Color）
    # ==========================================
    logger.info("💾 開始儲存資料到資料庫...")

    try:
        clothes_uid = str(uuid.uuid4())

        # 建立 Clothes 記錄（包含衣服尺寸）
        clothes = Clothes.objects.create(
            f_user_uid=user_uid,
            clothes_uid=clothes_uid,
            clothes_category=clothes_category,
            clothes_image_url=image_url,
            clothes_arm_length=clothes_arm_length,
            clothes_leg_length=clothes_leg_length,
            clothes_shoulder_width=clothes_shoulder_width,
            clothes_waistline=clothes_waistline,
        )
        logger.info(f"✅ 建立衣服記錄：clothes_uid={clothes_uid}, category={clothes_category}")
        logger.info(f"   尺寸：袖長={clothes_arm_length}cm, 褲長={clothes_leg_length}cm, 肩寬={clothes_shoulder_width}cm, 腰圍={clothes_waistline}cm")

        # 建立 Style 記錄（3筆，每筆鏈結到同一件 clothes）
        created_styles = []
        for style_name in style_names:
            Style.objects.create(
                f_clothes_uid=clothes_uid,
                style_uid=str(uuid.uuid4()),
                style_name=style_name,
            )
            created_styles.append(style_name)
            logger.info(f"✅ 建立風格記錄：{style_name} → clothes_uid={clothes_uid}")

        # 建立 Color 記錄（3筆，每筆鏈結到同一件 clothes）
        created_colors = []
        for color_name in color_names:
            Color.objects.create(
                f_clothes_uid=clothes_uid,
                color_uid=str(uuid.uuid4()),
                color_name=color_name,
            )
            created_colors.append(color_name)
            logger.info(f"✅ 建立顏色記錄：{color_name} → clothes_uid={clothes_uid}")

        logger.info(f"✅ 資料庫儲存完成：1 筆衣服、{len(created_styles)} 筆風格、{len(created_colors)} 筆顏色")

    except Exception as e:
        logger.error(f"❌ 資料庫儲存失敗：{e}")
        return JsonResponse(
            {
                "success": False,
                "message": f"資料庫儲存失敗：{str(e)}",
                "ai_status": {
                    "status_code": 200,
                    "message": "去背成功",
                    "tools_status": tools_status,
                },
                "storage_status": {
                    "success": True,
                    "filename": unique_filename,
                    "url": image_url,
                }
            },
            status=500
        )

    # ==========================================
    # 【步驟 9】返回完整的狀態資訊給前端
    # ==========================================
    logger.info("=" * 50)
    logger.info("✅ 圖片處理流程全部完成")
    logger.info("=" * 50)

    response_data = {
        "success": True,
        "message": "圖片處理和儲存成功",
        "processed_url": image_url,
        "ai_status": {
            "status_code": 200,
            "message": json_data.get('message', 'Processing Success'),
            "tools_status": tools_status,
        },
        "storage_status": {
            "success": True,
            "filename": unique_filename,
            "file_name": file_name,
            "file_format": file_format,
            "storage": "minio",
            "bucket": settings.MINIO_BUCKET_NAME,
            "public_url": public_url,
            "signed_url": presigned_url,
        },
        "clothes_data": {
            "clothes_uid": clothes_uid,
            "clothes_category": clothes_category,
            "styles": created_styles,
            "colors": created_colors,
            "image_url": image_url,
            "clothes_measurements": {
                "arm_length": clothes_arm_length,
                "leg_length": clothes_leg_length,
                "shoulder_width": clothes_shoulder_width,
                "waistline": clothes_waistline,
            }
        }
    }

    return JsonResponse(response_data)


# ==========================================
# 【衣服管理 CRUD API】
# ==========================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from accounts.models import Clothes, Style, Color, User
from .serializers import ClothesSerializer, ClothesCreateSerializer, ClothesDetailSerializer
import uuid


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_clothes_list(request):
    """
    用戶衣服列表端點
    
    GET: 獲取當前用戶的衣服列表
         如果用戶為管理員，可查看所有衣服
    
    Query Parameters:
        - category: 按分類篩選
        - page: 頁碼 (預設 1)
        - limit: 每頁筆數 (預設 20)
    
    Success 200:
    {
        "count": 10,
        "total_pages": 1,
        "current_page": 1,
        "results": [{衣服詳情}, ...]
    }
    """
    try:
        # 獲取查詢參數
        category = request.query_params.get('category', None)
        page = request.query_params.get('page', 1)
        limit = request.query_params.get('limit', 20)
        
        # 構建查詢 - 根據用戶身份決定查詢範圍
        if request.user.is_staff or request.user.is_superuser:
            # 管理員可以查看所有衣服
            queryset = Clothes.objects.all().order_by('-clothes_created_time')
            logger.info(f"✅ 管理員 {request.user.user_name} 查看所有衣服")
        else:
            # 普通用戶只能查看自己的衣服
            queryset = Clothes.objects.filter(
                f_user_uid=str(request.user.user_uid)
            ).order_by('-clothes_created_time')
            logger.info(f"✅ 用戶 {request.user.user_name} 查看自己的衣服")
        
        # 按分類篩選
        if category:
            queryset = queryset.filter(clothes_category__icontains=category)
        
        # 分頁
        paginator = Paginator(queryset, int(limit))
        paginated_clothes = paginator.get_page(int(page))
        
        # 序列化
        serializer = ClothesDetailSerializer(paginated_clothes, many=True)
        
        return Response({
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': int(page),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"❌ 獲取衣服列表失敗: {str(e)}")
        return Response(
            {'detail': f'獲取失敗: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorites_list(request):
    """
    用戶喜歡的衣服列表端點
    
    GET: 獲取當前用戶標註為喜歡的所有衣服
    
    Query Parameters:
        - page: 頁碼 (預設 1)
        - limit: 每頁筆數 (預設 20)
    
    Success 200:
    {
        "count": 5,
        "total_pages": 1,
        "current_page": 1,
        "results": [{衣服詳情}, ...]
    }
    """
    try:
        # 獲取查詢參數
        page = request.query_params.get('page', 1)
        limit = request.query_params.get('limit', 20)
        
        # 查詢當前用戶標註為喜歡的衣服
        queryset = Clothes.objects.filter(
            clothes_favorite=True
        ).order_by('-clothes_updated_time')
        
        logger.info(f"✅ 用戶 {request.user.user_name} 查看喜歡的衣服，共 {queryset.count()} 件")
        
        # 分頁
        paginator = Paginator(queryset, int(limit))
        paginated_clothes = paginator.get_page(int(page))
        
        # 序列化
        serializer = ClothesDetailSerializer(paginated_clothes, many=True)
        
        return Response({
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': int(page),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"❌ 獲取喜歡的衣服列表失敗: {str(e)}")
        return Response(
            {'detail': f'獲取失敗: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, clothes_uid):
    """
    標記/取消標記衣服為喜歡的端點
    
    PATCH: 切換衣服的喜歡狀態（favorite = !favorite）
    
    Body (JSON):
    {
        "favorite": true  // true 表示喜歡，false 表示取消喜歡
    }
    
    Success 200:
    {
        "success": true,
        "message": "已標記為喜歡" 或 "已取消喜歡",
        "clothes_uid": "...",
        "clothes_favorite": true/false
    }
    """
    try:
        # 獲取衣服
        clothes = get_object_or_404(Clothes, clothes_uid=clothes_uid)
        
        # 從請求體獲取喜歡狀態
        favorite_value = request.data.get('favorite')
        
        if favorite_value is None:
            return Response(
                {'detail': '必須提供 favorite 參數 (true/false)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新喜歡狀態
        clothes.clothes_favorite = bool(favorite_value)
        clothes.save()
        
        # 準備回應信息
        message = "已標記為喜歡" if clothes.clothes_favorite else "已取消喜歡"
        
        logger.info(f"✅ 用戶 {request.user.user_name} {message}: {clothes_uid}")
        
        return Response({
            'success': True,
            'message': message,
            'clothes_uid': clothes_uid,
            'clothes_favorite': clothes.clothes_favorite
        }, status=status.HTTP_200_OK)
    
    except Clothes.DoesNotExist:
        logger.warning(f"❌ 衣服不存在: {clothes_uid}")
        return Response(
            {'detail': '衣服不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"❌ 標記喜歡失敗: {str(e)}")
        return Response(
            {'detail': f'操作失敗: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def clothes_detail(request, clothes_uid):
    """
    衣服詳情端點
    
    GET: 獲取衣服詳情 (所有認證用戶皆可)
    PUT: 更新衣服 (只有衣服擁有者或管理員可更新)
    DELETE: 刪除衣服 (只有衣服擁有者或管理員可刪除)
    
    URL: /picture/clothes/<clothes_uid>/
    """
    
    # 獲取衣服
    clothes = get_object_or_404(Clothes, clothes_uid=clothes_uid)
    
    if request.method == 'GET':
        try:
            serializer = ClothesDetailSerializer(clothes)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"❌ 獲取衣服詳情失敗: {str(e)}")
            return Response(
                {'detail': f'獲取失敗: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'PUT':
        # 檢查權限 - 只有衣服擁有者或管理員才能更新
        is_owner = str(clothes.f_user_uid) == str(request.user.user_uid)
        is_admin = request.user.is_staff or request.user.is_superuser
        
        if not (is_owner or is_admin):
            return Response(
                {'detail': '只有衣服擁有者或管理員才能更新此衣服'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 驗證數據
        serializer = ClothesCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 更新衣服基本信息
            clothes.clothes_category = serializer.validated_data.get(
                'clothes_category',
                clothes.clothes_category
            )
            clothes.clothes_arm_length = serializer.validated_data.get(
                'clothes_arm_length',
                clothes.clothes_arm_length
            )
            clothes.clothes_shoulder_width = serializer.validated_data.get(
                'clothes_shoulder_width',
                clothes.clothes_shoulder_width
            )
            clothes.clothes_waistline = serializer.validated_data.get(
                'clothes_waistline',
                clothes.clothes_waistline
            )
            clothes.clothes_leg_length = serializer.validated_data.get(
                'clothes_leg_length',
                clothes.clothes_leg_length
            )
            clothes.clothes_image_url = serializer.validated_data.get(
                'clothes_image_url',
                clothes.clothes_image_url
            )
            clothes.save()
            
            # 更新顏色
            if 'colors' in serializer.validated_data:
                Color.objects.filter(f_clothes_uid=clothes.clothes_uid).delete()
                for color_name in serializer.validated_data['colors']:
                    Color.objects.create(
                        f_clothes_uid=clothes.clothes_uid,
                        color_uid=str(uuid.uuid4()),
                        color_name=color_name
                    )
            
            # 更新風格
            if 'styles' in serializer.validated_data:
                Style.objects.filter(f_clothes_uid=clothes.clothes_uid).delete()
                for style_name in serializer.validated_data['styles']:
                    Style.objects.create(
                        f_clothes_uid=clothes.clothes_uid,
                        style_uid=str(uuid.uuid4()),
                        style_name=style_name
                    )
            
            logger.info(f"✅ 用戶 {request.user.user_name} 更新衣服: {clothes.clothes_uid}")
            
            # 返回更新的衣服
            output_serializer = ClothesDetailSerializer(clothes)
            return Response(
                output_serializer.data,
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"❌ 更新衣服失敗: {str(e)}")
            return Response(
                {'detail': f'更新失敗: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'DELETE':
        # 檢查權限 - 只有衣服擁有者或管理員才能刪除
        is_owner = str(clothes.f_user_uid) == str(request.user.user_uid)
        is_admin = request.user.is_staff or request.user.is_superuser
        
        if not (is_owner or is_admin):
            return Response(
                {'detail': '只有衣服擁有者或管理員才能刪除此衣服'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            clothes_uid = clothes.clothes_uid
            clothes_category = clothes.clothes_category
            
            # 刪除相關的顏色和風格
            Color.objects.filter(f_clothes_uid=clothes_uid).delete()
            Style.objects.filter(f_clothes_uid=clothes_uid).delete()
            
            # 刪除衣服
            clothes.delete()
            
            logger.info(f"✅ 用戶 {request.user.user_name} 刪除衣服: {clothes_uid}")
            
            return Response(
                {'detail': '衣服已刪除'},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"❌ 刪除衣服失敗: {str(e)}")
            return Response(
                {'detail': f'刪除失敗: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==========================================
# 【用戶模型照片管理 API】
# ==========================================
@api_view(['POST', 'GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_photo(request):
    """
    用戶模型照片管理 API
    
    功能 2.3: 用戶模型照片管理
    - 上傳/更新用戶的模型照片
    - 獲取用戶當前的模型照片 URL
    
    POST 請求：上傳用戶模型照片（首次上傳）
    =====================================
    請求位址：POST /picture/user/photo
    認證方式：JWT Token (Authorization: Bearer <token>)
    Content-Type: multipart/form-data
    
    請求參數：
    - photo_file: 圖片檔案（二進位，必填）
    
    允許的格式：JPG, PNG, GIF, WebP
    最大大小：10MB
    功能：上傳用戶的模型照片
    
    成功響應（201 Created）：
    {
        "success": true,
        "message": "模型照片已上傳",
        "data": {
            "user_uid": "user_123",
            "user_image_url": "http://minio:9000/bucket/photo.jpg",
            "upload_time": "2024-01-01T12:00:00Z"
        }
    }
    
    PUT 請求：更新用戶模型照片
    =====================================
    請求位址：PUT /picture/user/photo
    認證方式：JWT Token (Authorization: Bearer <token>)
    Content-Type: multipart/form-data
    
    請求參數：
    - photo_file: 圖片檔案（二進位，必填）
    
    允許的格式：JPG, PNG, GIF, WebP
    最大大小：10MB
    功能：更新用戶的模型照片，會覆蓋舊照片
    
    成功響應（200 OK）：
    {
        "success": true,
        "message": "模型照片已更新",
        "data": {
            "user_uid": "user_123",
            "user_image_url": "http://minio:9000/bucket/photo.jpg",
            "upload_time": "2024-01-01T12:00:00Z"
        }
    }
    
    GET 請求：獲取當前用戶的模型照片 URL
    =====================================
    請求位址：GET /picture/user/photo
    認證方式：JWT Token (Authorization: Bearer <token>)
    
    成功響應（200 OK）：
    {
        "success": true,
        "message": "獲取成功",
        "data": {
            "user_uid": "user_123",
            "user_image_url": "http://minio:9000/bucket/photo.jpg",
            "upload_time": "2024-01-01T12:00:00Z"
        }
    }
    
    未設置照片（404 Not Found）：
    {
        "success": false,
        "message": "用戶未設置模型照片"
    }
    
    錯誤響應：
    - 400 Bad Request: 未提供 photo_file 或格式/大小不符
    - 401 Unauthorized: 未提供 JWT Token 或 Token 無效
    - 403 Forbidden: 無法修改他人的照片
    - 500 Internal Server Error: 伺服器錯誤
    """
    
    # ==========================================
    # 【POST 請求：上傳用戶模型照片】
    # ==========================================
    if request.method == 'POST':
        logger.info("=" * 50)
        logger.info("📥 收到用戶模型照片上傳請求")
        
        # 取得當前用戶
        user = request.user
        user_uid = str(user.user_uid)
        logger.info(f"👤 用戶 UID: {user_uid}")
        
        # 【步驟 1】檢查請求是否包含 photo_file 欄位
        if 'photo_file' not in request.FILES:
            logger.error("❌ 請求中未找到 'photo_file' 欄位")
            return Response(
                {
                    'success': False,
                    'message': '請上傳圖片檔案（欄位名稱：photo_file）'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photo_file = request.FILES['photo_file']
        logger.info(f"📷 接收到圖片")
        logger.info(f"   檔案大小：{photo_file.size} bytes")
        logger.info(f"   內容類型：{photo_file.content_type}")
        
        # 【步驟 2】驗證檔案格式
        allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if photo_file.content_type not in allowed_formats:
            logger.error(f"❌ 不支援的檔案格式：{photo_file.content_type}")
            return Response(
                {
                    'success': False,
                    'message': '不支援的檔案格式。允許的格式：JPG, PNG, GIF, WebP'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        logger.info(f"✅ 檔案格式驗證通過：{photo_file.content_type}")
        
        # 【步驟 3】驗證檔案大小（最大 10MB）
        max_size = 10 * 1024 * 1024  # 10MB
        if photo_file.size > max_size:
            logger.error(f"❌ 檔案大小超過限制：{photo_file.size} > {max_size}")
            return Response(
                {
                    'success': False,
                    'message': f'檔案大小不能超過 10MB（當前大小：{photo_file.size // 1024}KB）'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        logger.info(f"✅ 檔案大小驗證通過：{photo_file.size} bytes")
        
        # 【步驟 4】讀取檔案內容
        try:
            photo_file.seek(0)
            file_bytes = photo_file.read()
            logger.info(f"✅ 圖片讀取成功，大小：{len(file_bytes)} bytes")
        except Exception as e:
            logger.error(f"❌ 讀取圖片失敗：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'讀取圖片失敗：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 【步驟 5】轉發給 AI 後端進行去背處理（模特照片）
        logger.info("🤖 準備轉發給 AI 後端進行去背處理...")
        
        # 重新建立文件對象供 AI 後端使用
        photo_file.seek(0)
        
        # 決定副檔名和 content_type
        format_mapping = {
            'image/jpeg': {'ext': '.jpg', 'content_type': 'image/jpeg'},
            'image/png':  {'ext': '.png', 'content_type': 'image/png'},
            'image/gif':  {'ext': '.gif', 'content_type': 'image/gif'},
            'image/webp': {'ext': '.webp', 'content_type': 'image/webp'},
        }
        format_info = format_mapping.get(
            photo_file.content_type,
            {'ext': '.jpg', 'content_type': 'image/jpeg'}
        )
        
        # 準備發送給 AI 後端的文件
        files = {
            'model_image': (f'model_image{format_info["ext"]}', io.BytesIO(file_bytes), photo_file.content_type)
        }
        
        # 發送 POST 請求給 AI 後端（模特照片去背處理）
        # 路由：/virtual_try_on/fitting/modules
        ai_fitting_url = f"{settings.AI_BACKEND_URL}/virtual_try_on/fitting/modules"
        logger.info(f"🔗 AI 端點 URL：{ai_fitting_url}")
        
        try:
            ai_response = requests.post(
                ai_fitting_url,
                files=files,
                timeout=120  # 120秒逾時
            )
        except requests.exceptions.Timeout:
            logger.error("❌ AI 後端請求超時")
            return Response(
                {
                    'success': False,
                    'message': 'AI 後端處理超時'
                },
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            logger.error("❌ 無法連接到 AI 後端")
            return Response(
                {
                    'success': False,
                    'message': 'AI 後端服務不可用'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"❌ 轉發給 AI 後端失敗：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'轉發給 AI 後端失敗：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        ai_status_code = ai_response.status_code
        logger.info(f"✅ AI 後端響應狀態碼：{ai_status_code}")
        
        # 【步驟 6】檢查 AI 後端響應
        if ai_status_code != 200:
            logger.error(f"❌ AI 後端處理失敗（狀態碼：{ai_status_code}）")
            try:
                error_detail = ai_response.json()
                logger.error(f"   錯誤詳情：{error_detail}")
            except Exception:
                error_detail = ai_response.text[:200]
                logger.error(f"   原始響應：{error_detail}")
            
            return Response(
                {
                    'success': False,
                    'message': 'AI 去背處理失敗',
                    'ai_status': {
                        'status_code': ai_status_code,
                        'message': f'AI 後端返回狀態碼 {ai_status_code}'
                    }
                },
                status=ai_status_code if ai_status_code >= 400 and ai_status_code < 600 else 500
            )
        
        # 【步驟 7】解析 AI 返回的 multipart 回應
        logger.info("🔍 開始解析 AI 返回的 multipart 回應...")
        
        content_type = ai_response.headers.get('Content-Type', '')
        logger.info(f"   AI 響應的 Content-Type: {content_type}")
        
        json_data = None
        processed_image = None
        
        if 'multipart' in content_type:
            # ---- 解析 multipart 回應 ----
            multipart_data = multipart_decoder.MultipartDecoder(
                ai_response.content, content_type
            )
            
            for part in multipart_data.parts:
                # 解析每個 part 的 headers
                part_content_type = ''
                for header_name, header_value in part.headers.items():
                    h_name = header_name.decode() if isinstance(header_name, bytes) else header_name
                    h_value = header_value.decode() if isinstance(header_value, bytes) else header_value
                    if h_name.lower() == 'content-type':
                        part_content_type = h_value
                
                # 判斷 part 類型
                if 'application/json' in part_content_type:
                    json_data = json.loads(part.content.decode('utf-8'))
                    logger.info("✅ 解析到 JSON 元數據")
                elif 'image' in part_content_type:
                    processed_image = part.content
                    logger.info(f"✅ 解析到處理後圖片，大小：{len(processed_image)} bytes")
        else:
            logger.warning("⚠️ AI 回應非 multipart 格式，嘗試向後兼容解析")
            try:
                json_data = ai_response.json()
            except Exception:
                processed_image = ai_response.content
        
        # 驗證是否成功取得所有資料
        if not json_data:
            logger.error("❌ AI 返回的資料缺少 JSON 元數據")
            return Response(
                {
                    'success': False,
                    'message': 'AI 返回的資料格式錯誤：缺少 JSON 元數據'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        if not processed_image or len(processed_image) == 0:
            logger.error("❌ AI 返回的圖片資料為空")
            return Response(
                {
                    'success': False,
                    'message': 'AI 返回的圖片資料為空'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        logger.info(f"✅ 成功解析 AI 回應：JSON 元數據 + 圖片二進制數據")
        
        # 【步驟 8】提取 AI 回傳的文件名和格式
        ai_file_name = json_data.get('data', {}).get('file_name', f'model_photo_{user_uid}.png')
        ai_file_format = json_data.get('data', {}).get('file_format', 'PNG')
        logger.info(f"   AI 返回的文件名：{ai_file_name}")
        logger.info(f"   AI 返回的文件格式：{ai_file_format}")
        
        # 決定最終的副檔名
        if ai_file_format.upper() == 'PNG':
            final_ext = '.png'
            final_content_type = 'image/png'
        elif ai_file_format.upper() in ['JPG', 'JPEG']:
            final_ext = '.jpg'
            final_content_type = 'image/jpeg'
        elif ai_file_format.upper() == 'GIF':
            final_ext = '.gif'
            final_content_type = 'image/gif'
        elif ai_file_format.upper() == 'WEBP':
            final_ext = '.webp'
            final_content_type = 'image/webp'
        else:
            final_ext = '.png'
            final_content_type = 'image/png'
        
        # ==========================================
        # 修改：用戶模特照片放在 user-photos/ 資料夾下
        # ==========================================
        # 產生唯一檔案名稱：user_uid + 時間戳 + 隨機ID
        unique_id = uuid.uuid4().hex[:8]
        unique_filename = f"user-photos/model_photo_{user_uid}_{unique_id}{final_ext}"
        logger.info(f"   MinIO 檔案名稱（含資料夾）：{unique_filename}")
        
        # 取得 MinIO 客戶端
        minio_client = get_minio_client()
        if minio_client is None:
            logger.error("❌ MinIO 客戶端不可用")
            return Response(
                {
                    'success': False,
                    'message': '儲存服務不可用'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 【步驟 9】上傳 AI 處理後的圖片到 MinIO
        logger.info("💾 開始上傳 AI 處理後的圖片到 MinIO...")
        
        try:
            file_data = io.BytesIO(processed_image)
            file_length = len(processed_image)
            
            minio_client.put_object(
                settings.MINIO_BUCKET_NAME,
                unique_filename,
                file_data,
                file_length,
                content_type=final_content_type
            )
            
            logger.info(f"✅ 成功上傳 AI 處理後的圖片到 MinIO：{settings.MINIO_BUCKET_NAME}/{unique_filename}")
            
        except S3Error as e:
            logger.error(f"❌ 上傳到 MinIO 失敗：{e}")
            return Response(
                {
                    'success': False,
                    'message': '圖片儲存失敗（MinIO 上傳出錯）'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"❌ 上傳過程發生錯誤：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'圖片儲存失敗：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 【步驟 10】產生公開 URL
        try:
            public_url = f"{settings.MINIO_EXTERNAL_URL}/{settings.MINIO_BUCKET_NAME}/{unique_filename}"
            logger.info(f"✅ 公開 URL：{public_url[:100]}...")
        except Exception as e:
            logger.error(f"❌ 產生 URL 失敗：{e}")
            public_url = None
        
        # 【步驟 11】更新 User 表中的 user_image_url 欄位
        try:
            user.user_image_url = public_url
            user.save()
            logger.info(f"✅ 已更新用戶的 user_image_url")
        except Exception as e:
            logger.error(f"❌ 更新用戶資訊失敗：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'更新用戶資訊失敗：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        logger.info("=" * 50)
        logger.info("✅ 用戶模型照片上傳成功（經 AI 去背處理）")
        logger.info("=" * 50)
        
        # 【步驟 12】返回成功響應
        return Response(
            {
                'success': True,
                'message': '模型照片已上傳（已進行 AI 去背處理）',
                'photo_data': {
                    'photo_url': public_url,
                    'uploaded_at': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None,
                    'note': '此照片已經過 AI 去背處理，已保存為虛擬試穿用的模特照片'
                },
                'user': {
                    'user_uid': user_uid,
                    'user_name': user.user_name,
                    'user_image_url': public_url,
                    'updated_at': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None
                },
                'ai_status': {
                    'status_code': json_data.get('code', 200),
                    'message': json_data.get('message', 'Processing Success'),
                    'file_name': ai_file_name,
                    'file_format': ai_file_format
                }
            },
            status=status.HTTP_201_CREATED
        )
    
    # ==========================================
    # 【GET 請求：獲取用戶模型照片 URL】
    # ==========================================
    elif request.method == 'GET':
        logger.info("=" * 50)
        logger.info("📤 收到用戶模型照片查詢請求")
        
        # 取得當前用戶
        user = request.user
        user_uid = str(user.user_uid)
        logger.info(f"👤 用戶 UID: {user_uid}")
        
        # 檢查 user_image_url 是否已設置
        if not user.user_image_url:
            logger.info(f"⚠️  用戶 {user_uid} 未設置模型照片")
            return Response(
                {
                    'success': False,
                    'message': '用戶未設置模型照片'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        logger.info(f"✅ 用戶 {user_uid} 的模型照片 URL：{user.user_image_url[:100]}...")
        logger.info("=" * 50)
        
        # 返回用戶的模型照片 URL
        return Response(
            {
                'success': True,
                'message': '獲取成功',
                'data': {
                    'user_uid': user_uid,
                    'user_image_url': user.user_image_url,
                    'upload_time': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None
                }
            },
            status=status.HTTP_200_OK
        )
    
    # ==========================================
    # 【PUT 請求：更新用戶模型照片】
    # ==========================================
    elif request.method == 'PUT':
        logger.info("=" * 50)
        logger.info("🔄 收到用戶模型照片更新請求")
        
        # 取得當前用戶
        user = request.user
        user_uid = str(user.user_uid)
        logger.info(f"👤 用戶 UID: {user_uid}")
        
        # 【步驟 0】保存舊照片 URL（稍後用於刪除）
        old_photo_url = user.user_image_url
        old_filename = None
        if old_photo_url:
            # 從 URL 中提取檔案名稱
            # URL 格式：http://minio.example.com/bucket-name/user-photos/user_photo_xxx.jpg
            try:
                # 提取路徑部分（從 bucket 後開始）
                parts = old_photo_url.split(f"/{settings.MINIO_BUCKET_NAME}/")
                if len(parts) > 1:
                    old_filename = parts[1]  # 例如：user-photos/user_photo_xxx.jpg
                    logger.info(f"📝 舊照片檔案名稱：{old_filename}")
            except Exception as e:
                logger.warning(f"⚠️  無法提取舊照片檔案名稱：{e}")
        
        # 【步驟 1】檢查請求是否包含 photo_file 欄位
        if 'photo_file' not in request.FILES:
            logger.error("❌ 請求中未找到 'photo_file' 欄位")
            return Response(
                {
                    'success': False,
                    'message': '請上傳圖片檔案（欄位名稱：photo_file）'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photo_file = request.FILES['photo_file']
        logger.info(f"📷 接收到圖片")
        logger.info(f"   檔案大小：{photo_file.size} bytes")
        logger.info(f"   內容類型：{photo_file.content_type}")
        
        # 【步驟 2】驗證檔案格式
        allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if photo_file.content_type not in allowed_formats:
            logger.error(f"❌ 不支援的檔案格式：{photo_file.content_type}")
            return Response(
                {
                    'success': False,
                    'message': '不支援的檔案格式。允許的格式：JPG, PNG, GIF, WebP'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        logger.info(f"✅ 檔案格式驗證通過：{photo_file.content_type}")
        
        # 【步驟 3】驗證檔案大小（最大 10MB）
        max_size = 10 * 1024 * 1024  # 10MB
        if photo_file.size > max_size:
            logger.error(f"❌ 檔案大小超過限制：{photo_file.size} > {max_size}")
            return Response(
                {
                    'success': False,
                    'message': f'檔案大小不能超過 10MB（當前大小：{photo_file.size // 1024}KB）'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        logger.info(f"✅ 檔案大小驗證通過：{photo_file.size} bytes")
        
        # 【步驟 4】讀取檔案內容
        try:
            photo_file.seek(0)
            file_bytes = photo_file.read()
            logger.info(f"✅ 圖片讀取成功，大小：{len(file_bytes)} bytes")
        except Exception as e:
            logger.error(f"❌ 讀取圖片失敗：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'讀取圖片失敗：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 【步驟 5】轉發給 AI 後端進行去背處理（模特照片）
        logger.info("🤖 準備轉發給 AI 後端進行去背處理...")
        
        # 重新建立文件對象供 AI 後端使用
        photo_file.seek(0)
        
        # 決定副檔名和 content_type
        format_mapping = {
            'image/jpeg': {'ext': '.jpg', 'content_type': 'image/jpeg'},
            'image/png':  {'ext': '.png', 'content_type': 'image/png'},
            'image/gif':  {'ext': '.gif', 'content_type': 'image/gif'},
            'image/webp': {'ext': '.webp', 'content_type': 'image/webp'},
        }
        format_info = format_mapping.get(
            photo_file.content_type,
            {'ext': '.jpg', 'content_type': 'image/jpeg'}
        )
        
        # 準備發送給 AI 後端的文件
        files = {
            'model_image': (f'model_image{format_info["ext"]}', io.BytesIO(file_bytes), photo_file.content_type)
        }
        
        # 發送 POST 請求給 AI 後端（模特照片去背處理）
        ai_fitting_url = f"{settings.AI_BACKEND_URL}/virtual_try_on/fitting/modules"
        logger.info(f"🔗 AI 端點 URL：{ai_fitting_url}")
        
        try:
            ai_response = requests.post(
                ai_fitting_url,
                files=files,
                timeout=120
            )
        except requests.exceptions.Timeout:
            logger.error("❌ AI 後端請求超時")
            return Response(
                {
                    'success': False,
                    'message': 'AI 後端處理超時'
                },
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            logger.error("❌ 無法連接到 AI 後端")
            return Response(
                {
                    'success': False,
                    'message': 'AI 後端服務不可用'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"❌ 轉發給 AI 後端失敗：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'轉發給 AI 後端失敗：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        ai_status_code = ai_response.status_code
        logger.info(f"✅ AI 後端響應狀態碼：{ai_status_code}")
        
        # 【步驟 6】檢查 AI 後端響應
        if ai_status_code != 200:
            logger.error(f"❌ AI 後端處理失敗（狀態碼：{ai_status_code}）")
            try:
                error_detail = ai_response.json()
                logger.error(f"   錯誤詳情：{error_detail}")
            except Exception:
                error_detail = ai_response.text[:200]
                logger.error(f"   原始響應：{error_detail}")
            
            return Response(
                {
                    'success': False,
                    'message': 'AI 去背處理失敗',
                    'ai_status': {
                        'status_code': ai_status_code,
                        'message': f'AI 後端返回狀態碼 {ai_status_code}'
                    }
                },
                status=ai_status_code if ai_status_code >= 400 and ai_status_code < 600 else 500
            )
        
        # 【步驟 7】解析 AI 返回的 multipart 回應
        logger.info("🔍 開始解析 AI 返回的 multipart 回應...")
        
        content_type = ai_response.headers.get('Content-Type', '')
        logger.info(f"   AI 響應的 Content-Type: {content_type}")
        
        json_data = None
        processed_image = None
        
        if 'multipart' in content_type:
            multipart_data = multipart_decoder.MultipartDecoder(
                ai_response.content, content_type
            )
            
            for part in multipart_data.parts:
                part_content_type = ''
                for header_name, header_value in part.headers.items():
                    h_name = header_name.decode() if isinstance(header_name, bytes) else header_name
                    h_value = header_value.decode() if isinstance(header_value, bytes) else header_value
                    if h_name.lower() == 'content-type':
                        part_content_type = h_value
                
                if 'application/json' in part_content_type:
                    json_data = json.loads(part.content.decode('utf-8'))
                    logger.info("✅ 解析到 JSON 元數據")
                elif 'image' in part_content_type:
                    processed_image = part.content
                    logger.info(f"✅ 解析到處理後圖片，大小：{len(processed_image)} bytes")
        else:
            logger.warning("⚠️ AI 回應非 multipart 格式，嘗試向後兼容解析")
            try:
                json_data = ai_response.json()
            except Exception:
                processed_image = ai_response.content
        
        if not json_data:
            logger.error("❌ AI 返回的資料缺少 JSON 元數據")
            return Response(
                {
                    'success': False,
                    'message': 'AI 返回的資料格式錯誤：缺少 JSON 元數據'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        if not processed_image or len(processed_image) == 0:
            logger.error("❌ AI 返回的圖片資料為空")
            return Response(
                {
                    'success': False,
                    'message': 'AI 返回的圖片資料為空'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        logger.info(f"✅ 成功解析 AI 回應：JSON 元數據 + 圖片二進制數據")
        
        # 【步驟 8】提取 AI 回傳的文件名和格式
        ai_file_name = json_data.get('data', {}).get('file_name', f'model_photo_{user_uid}.png')
        ai_file_format = json_data.get('data', {}).get('file_format', 'PNG')
        logger.info(f"   AI 返回的文件名：{ai_file_name}")
        logger.info(f"   AI 返回的文件格式：{ai_file_format}")
        
        # 決定最終的副檔名
        if ai_file_format.upper() == 'PNG':
            final_ext = '.png'
            final_content_type = 'image/png'
        elif ai_file_format.upper() in ['JPG', 'JPEG']:
            final_ext = '.jpg'
            final_content_type = 'image/jpeg'
        elif ai_file_format.upper() == 'GIF':
            final_ext = '.gif'
            final_content_type = 'image/gif'
        elif ai_file_format.upper() == 'WEBP':
            final_ext = '.webp'
            final_content_type = 'image/webp'
        else:
            final_ext = '.png'
            final_content_type = 'image/png'
        
        # 產生唯一檔案名稱：user_uid + 時間戳 + 隨機ID
        unique_id = uuid.uuid4().hex[:8]
        unique_filename = f"user-photos/model_photo_{user_uid}_{unique_id}{final_ext}"
        logger.info(f"   新照片檔案名稱（含資料夾）：{unique_filename}")
        
        # 取得 MinIO 客戶端
        minio_client = get_minio_client()
        if minio_client is None:
            logger.error("❌ MinIO 客戶端不可用")
            return Response(
                {
                    'success': False,
                    'message': '儲存服務不可用'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 【步驟 9】上傳 AI 處理後的圖片到 MinIO
        logger.info("💾 開始上傳 AI 處理後的圖片到 MinIO...")
        
        try:
            file_data = io.BytesIO(processed_image)
            file_length = len(processed_image)
            
            minio_client.put_object(
                settings.MINIO_BUCKET_NAME,
                unique_filename,
                file_data,
                file_length,
                content_type=final_content_type
            )
            
            logger.info(f"✅ 成功上傳 AI 處理後的圖片到 MinIO：{settings.MINIO_BUCKET_NAME}/{unique_filename}")
            
        except S3Error as e:
            logger.error(f"❌ 上傳到 MinIO 失敗：{e}")
            return Response(
                {
                    'success': False,
                    'message': '圖片儲存失敗（MinIO 上傳出錯）'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"❌ 上傳過程發生錯誤：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'圖片儲存失敗：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 【步驟 10】產生公開 URL
        try:
            public_url = f"{settings.MINIO_EXTERNAL_URL}/{settings.MINIO_BUCKET_NAME}/{unique_filename}"
            logger.info(f"✅ 新照片 URL：{public_url[:100]}...")
        except Exception as e:
            logger.error(f"❌ 產生 URL 失敗：{e}")
            public_url = None
        
        # 【步驟 7】更新 User 表中的 user_image_url 欄位（覆蓋舊照片）
        try:
            user.user_image_url = public_url
            user.save()
            logger.info(f"✅ 已更新用戶的 user_image_url（覆蓋舊照片）")
        except Exception as e:
            logger.error(f"❌ 更新用戶資訊失敗：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'更新用戶資訊失敗：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 【步驟 8】刪除 MinIO 中的舊照片（可選，但推薦）
        if old_filename:
            logger.info(f"🗑️  開始刪除舊照片：{old_filename}")
            try:
                minio_client.remove_object(
                    settings.MINIO_BUCKET_NAME,
                    old_filename
                )
                logger.info(f"✅ 成功刪除舊照片：{old_filename}")
            except S3Error as e:
                # 如果舊照片不存在或刪除失敗，只記錄警告，不影響更新成功
                logger.warning(f"⚠️  刪除舊照片失敗（可能已刪除）：{e}")
            except Exception as e:
                logger.warning(f"⚠️  刪除舊照片過程出錯：{e}")
        
        logger.info("=" * 50)
        logger.info("✅ 用戶模型照片更新成功（經 AI 去背處理，舊照片已刪除）")
        logger.info("=" * 50)
        
        # 【步驟 13】返回成功響應
        return Response(
            {
                'success': True,
                'message': '模型照片已更新（已進行 AI 去背處理，舊照片已刪除）',
                'photo_data': {
                    'photo_url': public_url,
                    'uploaded_at': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None,
                    'note': '此照片已經過 AI 去背處理，已保存為虛擬試穿用的模特照片'
                },
                'user': {
                    'user_uid': user_uid,
                    'user_name': user.user_name,
                    'user_image_url': public_url,
                    'updated_at': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None
                },
                'ai_status': {
                    'status_code': json_data.get('code', 200),
                    'message': json_data.get('message', 'Processing Success'),
                    'file_name': ai_file_name,
                    'file_format': ai_file_format
                }
            },
            status=status.HTTP_200_OK
        )
