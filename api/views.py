"""
Django Views for Image Processing API
圖像處理 API 的 Django 視圖函數

這個檔案包含了所有的視圖函數（View Functions）
在 Django 中，視圖函數負責處理 HTTP 請求並返回 HTTP 響應

主要功能：
1. 接收前端上傳的圖片和檔案名稱
2. 轉發給 AI 後端進行去背處理
3. 接收 AI 返回的結果（圖片 + 狀態碼）
4. 驗證圖片格式為 PNG
5. 將處理後的圖片儲存到 MinIO
6. 返回完整的狀態資訊給前端
"""

# ==========================================
# 【第一部分】匯入所需的函式庫
# ==========================================
import io                    # 用來處理二進位資料流
import os                    # 用來操作檔案系統
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
    1. 接收前端上傳的圖片和檔案名稱（multipart/form-data）
    2. 將圖片和檔案名稱轉發給 AI 後端進行去背處理
    3. 接收 AI 返回的處理結果（圖片 + 檔案名稱 + 狀態碼）
    4. 驗證返回的圖片是 PNG 格式
    5. 將處理後的圖片儲存到 MinIO
    6. 返回完整的狀態資訊給前端
    
    請求方式：POST
    Content-Type: multipart/form-data
    存取位址：http://localhost:30000/api/upload-image
    
    請求參數：
    - image_data: 圖片檔案（multipart/form-data 格式）
    - filename: 檔案名稱（字串）
    
    AI 後端位址：http://192.168.233.128:8002/api/remove_bg
    AI 請求格式：
    - clothes_image: 圖片檔案流
    - clothes_filename: 檔案名稱
    
    AI 響應狀態碼：
    - 200 OK: 去背成功
    - 415 Unsupported Media Type: 上傳非圖片檔案
    - 422 Unprocessable Entity: 圖片過於模糊
    - 500 Internal Server Error: AI 模型運算失敗
    
    返回範例（成功）：
    {
        "success": true,
        "message": "圖片處理和儲存成功",
        "ai_status": {
            "status_code": 200,
            "message": "去背成功"
        },
        "storage_status": {
            "success": true,
            "filename": "processed_xxx.png",
            "url": "http://localhost:9000/processed-images/processed_xxx.png?X-Amz-...",
            "storage": "minio"
        }
    }
    
    返回範例（AI 失敗）：
    {
        "success": false,
        "message": "AI 處理失敗",
        "ai_status": {
            "status_code": 422,
            "message": "圖片過於模糊"
        }
    }
    """
    
    # ==========================================
    # 【步驟 1】接收前端上傳的圖片和檔案名稱
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
    
    # 檢查是否包含檔案名稱
    filename = request.POST.get('filename', '')
    if not filename:
        logger.error("❌ 請求中未找到 'filename' 欄位")
        return JsonResponse(
            {
                "success": False,
                "message": "請提供檔案名稱（欄位名稱：filename）"
            },
            status=400
        )
    
    # 取得上傳的檔案物件
    image_file = request.FILES['image_data']
    
    logger.info(f"📷 接收到圖片")
    logger.info(f"   檔案名稱：{filename}")
    logger.info(f"   檔案大小：{image_file.size} bytes")
    logger.info(f"   內容類型：{image_file.content_type}")
    
    # ==========================================
    # 【步驟 2】讀取圖片資料準備發送給 AI 後端
    # ==========================================
    try:
        # 重置檔案指標到開頭（重要！）
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
    # 【步驟 3】將圖片和檔案名稱發送給 AI 後端進行去背處理
    # ==========================================
    logger.info(f"🤖 開始呼叫 AI 後端：{settings.AI_BACKEND_URL}")
    logger.info(f"   發送檔案名稱：{filename}")
    
    try:
        # 準備發送給 AI 後端的資料
        # multipart/form-data 格式
        files = {
            'clothes_image': (filename, file_bytes, image_file.content_type)
        }
        data = {
            'clothes_filename': filename
        }
        
        # 發送 POST 請求給 AI 後端
        ai_response = requests.post(
            settings.AI_BACKEND_URL,
            files=files,
            data=data,
            timeout=60  # 60秒逾時
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
            except:
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
        # 【步驟 5】解析 AI 返回的處理結果
        # ==========================================
        logger.info("🔍 開始解析 AI 返回的資料...")
        
        # AI 後端返回 multipart/form-data 格式的圖片二進位資料
        content_type = ai_response.headers.get('Content-Type', '')
        logger.info(f"   AI 響應的 Content-Type: {content_type}")
        
        # 直接取得圖片二進位資料
        processed_image = ai_response.content
        processed_filename = filename  # 使用原檔案名稱
        
        logger.info(f"✅ 取得二進位圖片資料，大小：{len(processed_image)} bytes")
        
        # 驗證是否成功取得圖片資料
        if not processed_image or len(processed_image) == 0:
            logger.error("❌ AI 返回的圖片資料為空")
            return JsonResponse(
                {
                    "success": False,
                    "message": "AI 返回的圖片資料為空",
                    "ai_status": {
                        "status_code": 500,
                        "message": "返回資料為空"
                    }
                },
                status=500
            )
        
        logger.info(f"✅ 圖片處理完成，處理後大小：{len(processed_image)} bytes")
        logger.info(f"   處理後檔案名稱：{processed_filename}")
        
    except requests.exceptions.Timeout:
        logger.error("❌ AI 後端請求逾時（超過60秒）")
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
    # 【步驟 6】驗證圖片格式是否為 PNG
    # ==========================================
    logger.info("🔍 驗證圖片格式...")
    
    # 檢查檔案副檔名
    if not processed_filename.lower().endswith('.png'):
        logger.warning(f"⚠️  檔案名稱不是 .png 結尾，自動新增 .png 副檔名")
        # 移除其他副檔名
        base_name = processed_filename.rsplit('.', 1)[0] if '.' in processed_filename else processed_filename
        processed_filename = f"{base_name}.png"
    
    # 檢查圖片魔術數字（PNG 檔案標頭：89 50 4E 47）
    if len(processed_image) >= 8:
        png_signature = processed_image[:8]
        expected_signature = b'\x89PNG\r\n\x1a\n'
        if png_signature != expected_signature:
            logger.warning(f"⚠️  圖片不是標準 PNG 格式（檔案標頭不匹配）")
            # 但仍然繼續處理，因為可能是特殊編碼
    
    logger.info(f"✅ 圖片格式驗證通過：{processed_filename}")
    
    # ==========================================
    # 【步驟 7】將處理後的圖片儲存到 MinIO
    # ==========================================
    logger.info("💾 開始上傳圖片到 MinIO...")
    
    # 產生唯一的檔案名稱，避免重複
    unique_id = uuid.uuid4().hex[:8]
    base_name = processed_filename.rsplit('.', 1)[0] if '.' in processed_filename else processed_filename
    unique_filename = f"processed_{unique_id}_{base_name}.png"
    logger.info(f"   產生唯一檔案名稱：{unique_filename}")
    
    # 取得 MinIO 客戶端（每次都重新取得，確保連接有效）
    minio_client = get_minio_client()
    
    # 檢查 MinIO 客戶端是否可用
    if minio_client is None:
        logger.error("❌ MinIO 客戶端不可用")
        return JsonResponse(
            {
                "success": False,
                "message": "儲存服務不可用",
                "ai_status": {
                    "status_code": 200,
                    "message": "去背成功"
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
        # 將二進位資料轉換為類似檔案的物件
        file_data = io.BytesIO(processed_image)
        file_length = len(processed_image)
        
        # 上傳到 MinIO
        minio_client.put_object(
            settings.MINIO_BUCKET_NAME,
            unique_filename,
            file_data,
            file_length,
            content_type='image/png'
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
                    "message": "去背成功"
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
                    "message": "去背成功"
                },
                "storage_status": {
                    "success": False,
                    "message": str(e)
                }
            },
            status=500
        )
    
    # ==========================================
    # 【步驟 8】產生預簽名 URL
    # ==========================================
    try:
        presigned_url = minio_client.presigned_get_object(
            settings.MINIO_BUCKET_NAME,
            unique_filename,
            expires=timedelta(days=7)  # 7天後過期
        )
        
        logger.info(f"✅ 原始預簽名 URL：{presigned_url[:100]}...")
        
        # 修正：將內部地址轉換為外部地址（讓前端瀏覽器可以存取）
        # MinIO 可能返回多種格式的 URL，都需要替換
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
        
        logger.info(f"✅ 轉換後的預簽名 URL：{presigned_url[:100]}...")
        
        # 同時產生不需要簽名的公開 URL
        # 因為 Bucket 已設定為公開讀取，可以直接訪問
        public_url = f"{settings.MINIO_EXTERNAL_URL}/{settings.MINIO_BUCKET_NAME}/{unique_filename}"
        logger.info(f"✅ 公開 URL：{public_url[:100]}...")
        
    except Exception as e:
        logger.error(f"❌ 產生 URL 失敗：{e}")
        # 即使 URL 產生失敗，也返回成功（因為檔案已上傳）
        presigned_url = None
        public_url = None
    
    # ==========================================
    # 【步驟 9】返回完整的狀態資訊給前端
    # ==========================================
    logger.info("=" * 50)
    logger.info("✅ 圖片處理流程全部完成")
    logger.info("=" * 50)
    
    response_data = {
        "success": True,
        "message": "圖片處理和儲存成功",
        "processed_url": public_url or presigned_url,  # 優先使用公開 URL
        "ai_status": {
            "status_code": 200,
            "message": "去背成功"
        },
        "storage_status": {
            "success": True,
            "filename": unique_filename,
            "original_filename": processed_filename,
            "storage": "minio",
            "bucket": settings.MINIO_BUCKET_NAME,
            "public_url": public_url,  # 新增公開 URL
            "signed_url": presigned_url  # 新增預簽名 URL（備用）
        }
    }
    
    # 如果有 URL，新增到響應中
    if public_url or presigned_url:
        response_data["storage_status"]["url"] = public_url or presigned_url
    
    return JsonResponse(response_data)
