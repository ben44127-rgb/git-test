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
    1. 接收前端上傳的圖片（multipart/form-data）
    2. 將圖片轉發給 AI 後端（virtual_try_on/clothes/remove_bg）
    3. 解析 AI 返回的 multipart 回應（JSON 元數據 + 去背圖片）
    4. 使用 AI 回傳的 file_name / file_format 將圖片儲存到 MinIO
    5. 將 clothes_category、style_name（3筆）、color_name（3筆）存入資料庫
    6. 返回完整的狀態資訊給前端

    請求方式：POST
    Content-Type: multipart/form-data
    存取位址：http://localhost:30000/picture/clothes/upload_image

    請求參數：
    - image_data: 圖片檔案（multipart/form-data 格式）
    - user_uid: 用戶 UID（字串，若有 JWT Token 則可省略）

    AI 後端位址：http://192.168.233.128:8002/virtual_try_on/clothes/remove_bg
    AI 請求格式：
    - clothes_image: 圖片檔案流

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
        # 只需要 clothes_image（根據新 API 規格）
        files = {
            'clothes_image': (image_file.name, file_bytes, image_file.content_type)
        }

        # 發送 POST 請求給 AI 後端
        ai_response = requests.post(
            settings.AI_BACKEND_URL,
            files=files,
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
    unique_filename = f"{unique_id}_{base_name}{format_info['ext']}"
    logger.info(f"   MinIO 檔案名稱：{unique_filename}")

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

        # 建立 Clothes 記錄
        clothes = Clothes.objects.create(
            f_user_uid=user_uid,
            clothes_uid=clothes_uid,
            clothes_category=clothes_category,
            clothes_image_url=image_url,
        )
        logger.info(f"✅ 建立衣服記錄：clothes_uid={clothes_uid}, category={clothes_category}")

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
        }
    }

    return JsonResponse(response_data)

