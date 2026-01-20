"""
Django Views for Image Processing API
图像处理 API 的 Django 视图函数

这个文件包含了所有的视图函数（View Functions）
在 Django 中，视图函数负责处理 HTTP 请求并返回 HTTP 响应

主要功能：
1. 接收前端上传的图片和文件名
2. 转发给 AI 后端进行去背处理
3. 接收 AI 返回的结果（图片 + 状态码）
4. 验证图片格式为 PNG
5. 将处理后的图片存储到 MinIO
6. 返回完整的状态信息给前端
"""

# ==========================================
# 【第一部分】导入所需的库
# ==========================================
import io                    # 用来处理二进制数据流
import os                    # 用来操作文件系统
import requests              # 用来发送 HTTP 请求给 AI 后端
import uuid                  # 用来生成唯一的 ID
import logging               # 用来记录日志
from datetime import timedelta   # 用来设定时间差

# Django 相关导入
from django.http import JsonResponse, HttpResponse  # Django 的响应对象
from django.views.decorators.csrf import csrf_exempt  # 用来禁用 CSRF 保护
from django.views.decorators.http import require_http_methods  # 用来限制 HTTP 方法
from django.conf import settings  # 用来访问 Django 设置

# MinIO 相关导入
from minio import Minio      # MinIO 的 Python 客户端
from minio.error import S3Error  # MinIO 的错误类型

# 获取日志记录器
logger = logging.getLogger(__name__)

# ==========================================
# 【第二部分】初始化 MinIO 客户端
# ==========================================
def get_minio_client():
    """
    获取 MinIO 客户端实例
    这个函数负责创建和返回 MinIO 客户端对象
    如果连接失败，会返回 None
    """
    try:
        # 创建 MinIO 客户端对象
        client = Minio(
            settings.MINIO_ENDPOINT,           # MinIO 服务器地址
            access_key=settings.MINIO_ACCESS_KEY,  # 访问密钥
            secret_key=settings.MINIO_SECRET_KEY,  # 秘密密钥
            secure=settings.MINIO_SECURE       # 是否使用 HTTPS
        )
        
        # 检查 Bucket 是否存在
        # Bucket 就像是 MinIO 里的一个文件夹
        if not client.bucket_exists(settings.MINIO_BUCKET_NAME):
            # 如果不存在，就创建一个新的 Bucket
            client.make_bucket(settings.MINIO_BUCKET_NAME)
            logger.info(f"✅ 已创建 Bucket：{settings.MINIO_BUCKET_NAME}")
        else:
            logger.info(f"✅ Bucket 已存在：{settings.MINIO_BUCKET_NAME}")
        
        return client
        
    except Exception as e:
        # 如果连接失败，记录错误日志并返回 None
        logger.error(f"❌ MinIO 初始化失败：{e}")
        logger.error(f"   提示：请确认 MinIO 服务是否启动，以及账号密码是否正确")
        return None

# 在模块加载时初始化 MinIO 客户端
minio_client = get_minio_client()

# ==========================================
# 【第三部分】健康检查视图
# ==========================================
@require_http_methods(["GET"])  # 只允许 GET 请求
def health_check(request):
    """
    健康检查端点
    用来检查服务是否正常运行
    
    请求方式：GET
    访问地址：http://localhost:30000/health
    
    返回示例：
    {
        "status": "healthy",
        "message": "服务运行正常"
    }
    """
    # 创建响应数据
    response_data = {
        "status": "healthy",
        "message": "服务运行正常"
    }
    
    # 返回 JSON 响应
    # JsonResponse 是 Django 提供的便捷函数，会自动设置 Content-Type 为 application/json
    return JsonResponse(response_data)

# ==========================================
# 【第四部分】图片上传和处理视图
# ==========================================
@csrf_exempt  # 禁用 CSRF 保护（因为这是 API 端点，通常通过 token 认证）
@require_http_methods(["POST"])  # 只允许 POST 请求
def upload_and_process(request):
    """
    处理图片上传和 AI 去背的主要视图函数
    
    完整流程：
    1. 接收前端上传的图片和文件名（multipart/form-data）
    2. 将图片和文件名转发给 AI 后端进行去背处理
    3. 接收 AI 返回的处理结果（图片 + 文件名 + 状态码）
    4. 验证返回的图片是 PNG 格式
    5. 将处理后的图片存储到 MinIO
    6. 返回完整的状态信息给前端
    
    请求方式：POST
    Content-Type: multipart/form-data
    访问地址：http://localhost:30000/api/upload-image
    
    请求参数：
    - image_data: 图片文件（multipart/form-data 格式）
    - filename: 文件名（字符串）
    
    AI 后端地址：http://localhost:8001/api/remove_bg
    AI 请求格式：
    - clothes_image: 图片文件流
    - clothes_filename: 文件名
    
    AI 响应状态码：
    - 200 OK: 去背成功
    - 415 Unsupported Media Type: 上传非图片文件
    - 422 Unprocessable Entity: 图片过于模糊
    - 500 Internal Server Error: AI 模型运算失败
    
    返回示例（成功）：
    {
        "success": true,
        "message": "图片处理和存储成功",
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
    
    返回示例（AI 失败）：
    {
        "success": false,
        "message": "AI 处理失败",
        "ai_status": {
            "status_code": 422,
            "message": "图片过于模糊"
        }
    }
    """
    
    # ==========================================
    # 【步骤 1】接收前端上传的图片和文件名
    # ==========================================
    logger.info("=" * 50)
    logger.info("📥 收到新的图片处理请求")
    
    # 检查请求中是否包含图片文件
    if 'image_data' not in request.FILES:
        logger.error("❌ 请求中未找到 'image_data' 字段")
        return JsonResponse(
            {
                "success": False,
                "message": "请上传图片文件（字段名：image_data）"
            },
            status=400
        )
    
    # 检查是否包含文件名
    filename = request.POST.get('filename', '')
    if not filename:
        logger.error("❌ 请求中未找到 'filename' 字段")
        return JsonResponse(
            {
                "success": False,
                "message": "请提供文件名（字段名：filename）"
            },
            status=400
        )
    
    # 获取上传的文件对象
    image_file = request.FILES['image_data']
    
    logger.info(f"📷 接收到图片")
    logger.info(f"   文件名：{filename}")
    logger.info(f"   文件大小：{image_file.size} bytes")
    logger.info(f"   内容类型：{image_file.content_type}")
    
    # ==========================================
    # 【步骤 2】读取图片数据准备发送给 AI 后端
    # ==========================================
    try:
        # 重置文件指针到开头（重要！）
        image_file.seek(0)
        file_bytes = image_file.read()
        logger.info(f"✅ 图片读取成功，大小：{len(file_bytes)} bytes")
    except Exception as e:
        logger.error(f"❌ 读取图片失败：{e}")
        return JsonResponse(
            {
                "success": False,
                "message": f"读取图片失败：{str(e)}"
            },
            status=500
        )
    
    # ==========================================
    # 【步骤 3】将图片和文件名发送给 AI 后端进行去背处理
    # ==========================================
    logger.info(f"🤖 开始调用 AI 后端：{settings.AI_BACKEND_URL}")
    logger.info(f"   发送文件名：{filename}")
    
    try:
        # 准备发送给 AI 后端的数据
        # multipart/form-data 格式
        files = {
            'clothes_image': (filename, file_bytes, image_file.content_type)
        }
        data = {
            'clothes_filename': filename
        }
        
        # 发送 POST 请求给 AI 后端
        ai_response = requests.post(
            settings.AI_BACKEND_URL,
            files=files,
            data=data,
            timeout=60  # 60秒超时
        )
        
        ai_status_code = ai_response.status_code
        logger.info(f"✅ AI 后端响应状态码：{ai_status_code}")
        
        # ==========================================
        # 【步骤 4】根据 AI 返回的状态码进行处理
        # ==========================================
        
        # 状态码对应的消息
        status_messages = {
            200: "去背成功",
            415: "上传非图片文件",
            422: "图片过于模糊",
            500: "AI 模型运算失败"
        }
        
        ai_message = status_messages.get(ai_status_code, f"未知状态码：{ai_status_code}")
        
        # 如果 AI 处理失败（状态码不是 200）
        if ai_status_code != 200:
            logger.error(f"❌ AI 处理失败：{ai_message}")
            
            # 尝试获取详细错误信息
            try:
                error_detail = ai_response.json()
                logger.error(f"   错误详情：{error_detail}")
            except:
                error_detail = ai_response.text[:200]
                logger.error(f"   原始响应：{error_detail}")
            
            return JsonResponse(
                {
                    "success": False,
                    "message": "AI 处理失败",
                    "ai_status": {
                        "status_code": ai_status_code,
                        "message": ai_message
                    }
                },
                status=ai_status_code
            )
        
        # ==========================================
        # 【步骤 5】解析 AI 返回的处理结果
        # ==========================================
        logger.info("🔍 开始解析 AI 返回的数据...")
        
        # AI 后端返回 multipart/form-data 格式的图片二进制数据
        content_type = ai_response.headers.get('Content-Type', '')
        logger.info(f"   AI 响应的 Content-Type: {content_type}")
        
        # 直接获取图片二进制数据
        processed_image = ai_response.content
        processed_filename = filename  # 使用原文件名
        
        logger.info(f"✅ 获取到二进制图片数据，大小：{len(processed_image)} bytes")
        
        # 验证是否成功获取图片数据
        if not processed_image or len(processed_image) == 0:
            logger.error("❌ AI 返回的图片数据为空")
            return JsonResponse(
                {
                    "success": False,
                    "message": "AI 返回的图片数据为空",
                    "ai_status": {
                        "status_code": 500,
                        "message": "返回数据为空"
                    }
                },
                status=500
            )
        
        logger.info(f"✅ 图片处理完成，处理后大小：{len(processed_image)} bytes")
        logger.info(f"   处理后文件名：{processed_filename}")
        
    except requests.exceptions.Timeout:
        logger.error("❌ AI 后端请求超时（超过60秒）")
        return JsonResponse(
            {
                "success": False,
                "message": "AI 处理超时",
                "ai_status": {
                    "status_code": 504,
                    "message": "请求超时"
                }
            },
            status=504
        )
    except requests.exceptions.ConnectionError:
        logger.error("❌ 无法连接到 AI 后端")
        return JsonResponse(
            {
                "success": False,
                "message": "无法连接到 AI 服务",
                "ai_status": {
                    "status_code": 503,
                    "message": "服务不可用"
                }
            },
            status=503
        )
    except Exception as e:
        logger.error(f"❌ 调用 AI 后端时发生错误：{e}")
        return JsonResponse(
            {
                "success": False,
                "message": f"AI 服务调用失败：{str(e)}",
                "ai_status": {
                    "status_code": 500,
                    "message": str(e)
                }
            },
            status=500
        )
    
    # ==========================================
    # 【步骤 6】验证图片格式是否为 PNG
    # ==========================================
    logger.info("🔍 验证图片格式...")
    
    # 检查文件扩展名
    if not processed_filename.lower().endswith('.png'):
        logger.warning(f"⚠️  文件名不是 .png 结尾，自动添加 .png 后缀")
        # 移除其他扩展名
        base_name = processed_filename.rsplit('.', 1)[0] if '.' in processed_filename else processed_filename
        processed_filename = f"{base_name}.png"
    
    # 检查图片魔术数字（PNG 文件头：89 50 4E 47）
    if len(processed_image) >= 8:
        png_signature = processed_image[:8]
        expected_signature = b'\x89PNG\r\n\x1a\n'
        if png_signature != expected_signature:
            logger.warning(f"⚠️  图片不是标准 PNG 格式（文件头不匹配）")
            # 但仍然继续处理，因为可能是特殊编码
    
    logger.info(f"✅ 图片格式验证通过：{processed_filename}")
    
    # ==========================================
    # 【步骤 7】将处理后的图片存储到 MinIO
    # ==========================================
    logger.info("💾 开始上传图片到 MinIO...")
    
    # 生成唯一的文件名，避免重复
    unique_id = uuid.uuid4().hex[:8]
    base_name = processed_filename.rsplit('.', 1)[0] if '.' in processed_filename else processed_filename
    unique_filename = f"processed_{unique_id}_{base_name}.png"
    logger.info(f"   生成唯一文件名：{unique_filename}")
    
    # 检查 MinIO 客户端是否可用
    if minio_client is None:
        logger.error("❌ MinIO 客户端不可用")
        return JsonResponse(
            {
                "success": False,
                "message": "存储服务不可用",
                "ai_status": {
                    "status_code": 200,
                    "message": "去背成功"
                },
                "storage_status": {
                    "success": False,
                    "message": "MinIO 服务不可用"
                }
            },
            status=503
        )
    
    # 上传到 MinIO
    try:
        # 将二进制数据转换为类似文件的对象
        file_data = io.BytesIO(processed_image)
        file_length = len(processed_image)
        
        # 上传到 MinIO
        minio_client.put_object(
            settings.MINIO_BUCKET_NAME,
            unique_filename,
            file_data,
            file_length,
            content_type='image/png'
        )
        
        logger.info(f"✅ 成功上传到 MinIO：{settings.MINIO_BUCKET_NAME}/{unique_filename}")
        
    except S3Error as e:
        logger.error(f"❌ 上传到 MinIO 失败：{e}")
        return JsonResponse(
            {
                "success": False,
                "message": "图片存储失败",
                "ai_status": {
                    "status_code": 200,
                    "message": "去背成功"
                },
                "storage_status": {
                    "success": False,
                    "message": f"MinIO 上传失败：{str(e)}"
                }
            },
            status=500
        )
    except Exception as e:
        logger.error(f"❌ 上传过程发生错误：{e}")
        return JsonResponse(
            {
                "success": False,
                "message": "图片存储失败",
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
    # 【步骤 8】生成预签名 URL
    # ==========================================
    try:
        presigned_url = minio_client.presigned_get_object(
            settings.MINIO_BUCKET_NAME,
            unique_filename,
            expires=timedelta(days=7)  # 7天后过期
        )
        
        logger.info(f"✅ 生成预签名 URL 成功")
        logger.info(f"   URL（前100字符）：{presigned_url[:100]}...")
        
    except Exception as e:
        logger.error(f"❌ 生成预签名 URL 失败：{e}")
        # 即使 URL 生成失败，也返回成功（因为文件已上传）
        presigned_url = None
    
    # ==========================================
    # 【步骤 9】返回完整的状态信息给前端
    # ==========================================
    logger.info("=" * 50)
    logger.info("✅ 图片处理流程全部完成")
    logger.info("=" * 50)
    
    response_data = {
        "success": True,
        "message": "图片处理和存储成功",
        "ai_status": {
            "status_code": 200,
            "message": "去背成功"
        },
        "storage_status": {
            "success": True,
            "filename": unique_filename,
            "original_filename": processed_filename,
            "storage": "minio",
            "bucket": settings.MINIO_BUCKET_NAME
        }
    }
    
    # 如果有 URL，添加到响应中
    if presigned_url:
        response_data["storage_status"]["url"] = presigned_url
    
    return JsonResponse(response_data)
