# 图片处理 API 完整文档

## 📡 API 概览

这个 Django 后端服务作为中间件，负责接收前端上传的图片，转发给 AI 服务进行去背处理，然后将处理后的图片存储到 MinIO，并返回访问链接。

---

## 🔗 端点列表

### 1. 健康检查

**端点**: `GET /health`

**描述**: 检查服务是否正常运行

**请求示例**:
```bash
curl http://localhost:30000/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "message": "服务运行正常"
}
```

---

### 2. 图片上传和处理

**端点**: `POST /api/upload-image`

**描述**: 上传图片到 AI 服务进行去背处理，并存储到 MinIO

**Content-Type**: `multipart/form-data`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `image_data` | File | ✅ 是 | 图片文件（multipart/form-data） |
| `filename` | String | ✅ 是 | 文件名（例如："photo.jpg"） |

**请求示例 (curl)**:
```bash
curl -X POST http://localhost:30000/api/upload-image \
  -F "image_data=@/path/to/image.jpg" \
  -F "filename=image.jpg"
```

**请求示例 (Python)**:
```python
import requests

files = {
    'image_data': ('photo.jpg', open('photo.jpg', 'rb'), 'image/jpeg')
}
data = {
    'filename': 'photo.jpg'
}

response = requests.post(
    'http://localhost:30000/api/upload-image',
    files=files,
    data=data
)

result = response.json()
print(result)
```

**请求示例 (JavaScript/Fetch)**:
```javascript
const formData = new FormData();
formData.append('image_data', fileInput.files[0]);
formData.append('filename', fileInput.files[0].name);

fetch('http://localhost:30000/api/upload-image', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

---

## 📤 响应格式

### 成功响应 (200 OK)

```json
{
  "success": true,
  "message": "图片处理和存储成功",
  "ai_status": {
    "status_code": 200,
    "message": "去背成功"
  },
  "storage_status": {
    "success": true,
    "filename": "processed_abc12345_photo.png",
    "original_filename": "photo.png",
    "url": "http://localhost:9000/processed-images/processed_abc12345_photo.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&...",
    "storage": "minio",
    "bucket": "processed-images"
  }
}
```

**字段说明**:
- `success`: 整体操作是否成功
- `message`: 操作描述信息
- `ai_status`: AI 处理状态
  - `status_code`: AI 服务返回的状态码
  - `message`: AI 处理结果描述
- `storage_status`: 存储状态
  - `success`: 是否成功存储
  - `filename`: 在 MinIO 中的唯一文件名
  - `original_filename`: 原始文件名
  - `url`: 可访问的预签名 URL（7天有效期）
  - `storage`: 存储类型（minio）
  - `bucket`: 存储桶名称

---

## ❌ 错误响应

### 400 Bad Request - 缺少参数

```json
{
  "success": false,
  "message": "请上传图片文件（字段名：image_data）"
}
```

或

```json
{
  "success": false,
  "message": "请提供文件名（字段名：filename）"
}
```

---

### 415 Unsupported Media Type - AI: 非图片文件

```json
{
  "success": false,
  "message": "AI 处理失败",
  "ai_status": {
    "status_code": 415,
    "message": "上传非图片文件"
  }
}
```

---

### 422 Unprocessable Entity - AI: 图片模糊

```json
{
  "success": false,
  "message": "AI 处理失败",
  "ai_status": {
    "status_code": 422,
    "message": "图片过于模糊"
  }
}
```

---

### 500 Internal Server Error - AI: 模型失败

```json
{
  "success": false,
  "message": "AI 处理失败",
  "ai_status": {
    "status_code": 500,
    "message": "AI 模型运算失败"
  }
}
```

---

### 503 Service Unavailable - 服务不可用

```json
{
  "success": false,
  "message": "无法连接到 AI 服务",
  "ai_status": {
    "status_code": 503,
    "message": "服务不可用"
  }
}
```

或 MinIO 不可用:

```json
{
  "success": false,
  "message": "存储服务不可用",
  "ai_status": {
    "status_code": 200,
    "message": "去背成功"
  },
  "storage_status": {
    "success": false,
    "message": "MinIO 服务不可用"
  }
}
```

---

### 504 Gateway Timeout - 请求超时

```json
{
  "success": false,
  "message": "AI 处理超时",
  "ai_status": {
    "status_code": 504,
    "message": "请求超时"
  }
}
```

---

## 🔄 完整工作流程

```
前端 → Django 后端 → AI 服务 (port 8001) → Django 后端 → MinIO → 前端
  │          │              │                    │           │         │
  │          │              │                    │           │         │
  └─ 上传     └─ 转发        └─ 去背处理          └─ 存储     └─ 生成URL └─ 返回结果
     图片        图片+文件名    返回处理结果         到MinIO      (7天有效)   给前端
```

### 详细步骤:

1. **前端上传** (POST /api/upload-image)
   - 字段: `image_data` (文件) + `filename` (字符串)

2. **Django 后端接收**
   - 验证参数完整性
   - 读取图片二进制数据

3. **转发给 AI 服务** (POST http://localhost:8001/api/remove_bg)
   - 字段: `clothes_image` (文件流) + `clothes_filename` (文件名)

4. **AI 服务处理**
   - 返回状态码: 200/415/422/500
   - 返回格式: JSON (base64) 或 二进制图片

5. **Django 后端处理 AI 响应**
   - 解析返回数据（支持两种格式）
   - 验证 PNG 格式
   - 如果文件名不是 .png，自动添加

6. **存储到 MinIO**
   - 生成唯一文件名: `processed_{随机ID}_{原文件名}.png`
   - 上传到 bucket: `processed-images`

7. **生成预签名 URL**
   - 有效期: 7 天
   - 包含签名参数

8. **返回给前端**
   - 包含: AI 状态 + 存储状态 + 访问 URL

---

## ⚙️ 配置说明

### 环境变量 (.env)

```bash
# Django 配置
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-here

# AI 后端配置
AI_BACKEND_URL=http://localhost:8001/api/remove_bg
AI_REQUEST_TIMEOUT=60

# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=processed-images
MINIO_SECURE=False
```

### AI 后端要求

**端口**: 8001  
**路径**: /api/remove_bg  
**方法**: POST  
**输入格式**:
- `clothes_image`: 图片文件流
- `clothes_filename`: 文件名

**输出格式**:
- **Content-Type**: multipart/form-data 或 image/png
- **Body**: PNG 图片二进制数据
- 直接返回处理后的图片二进制流

**状态码**:
- `200`: 去背成功
- `415`: 上传非图片文件
- `422`: 图片过于模糊
- `500`: AI 模型运算失败

---

## 🧪 測試方法

### 使用 curl 測試

```bash
# 創建測試圖片
python3 -c "from PIL import Image; img = Image.new('RGB', (200,200), 'red'); img.save('test.png')"

# 上傳測試
curl -X POST http://localhost:30000/api/upload-image \
  -F "image_data=@test.png" \
  -F "filename=test.png"
```

### 使用 Python requests 測試

```python
import requests
from PIL import Image
import io

# 創建測試圖片
img = Image.new('RGB', (200, 200), color='red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# 發送請求
files = {'image_data': ('test.png', img_bytes, 'image/png')}
data = {'filename': 'test.png'}
response = requests.post('http://localhost:30000/api/upload-image', 
                        files=files, data=data)
print(response.json())
```

### 3. 查看日志

```bash
# 实时查看日志
tail -f logs/django.log

# 或
tail -f logs/django_app.log
```

---

## 🔍 故障排除

### 问题 1: AI 服务连接失败

**错误**: `无法连接到 AI 服务`

**解决方案**:
1. 检查 AI 服务是否在 8001 端口运行
2. 测试连接: `curl http://localhost:8001/health` (如果有健康检查端点)
3. 检查 .env 中的 `AI_BACKEND_URL` 配置

---

### 问题 2: MinIO 连接失败

**错误**: `MinIO 服务不可用`

**解决方案**:
1. 检查 MinIO 容器: `docker ps | grep minio`
2. 启动 MinIO: `docker-compose up -d minio`
3. 检查连接: `curl http://localhost:9000/minio/health/live`

---

### 问题 3: 文件名编码问题

**问题**: 中文文件名乱码

**解决方案**:
- 前端发送时使用 UTF-8 编码
- 或在前端先将中文文件名转换为英文

---

## 📊 性能考虑

- **超时设置**: AI 请求超时 60 秒
- **文件大小限制**: Django 默认 10MB (可在 settings.py 修改)
- **并发处理**: 使用 gunicorn 多worker (生产环境)
- **预签名 URL**: 7天有效期，避免频繁生成

---

## 🔒 安全建议

1. **生产环境**:
   - 修改 `DJANGO_SECRET_KEY` 为强密钥
   - 设置 `DEBUG=False`
   - 限制 `ALLOWED_HOSTS`
   - 使用 HTTPS (MinIO `MINIO_SECURE=True`)

2. **CORS 配置**:
   - 限制 `CORS_ALLOWED_ORIGINS` 为具体前端域名
   - 不要在生产环境使用 `CORS_ALLOW_ALL_ORIGINS = True`

3. **文件验证**:
   - 后端已验证 PNG 文件头
   - AI 服务应该也验证文件类型

---

## 📞 相關資源

如有問題，請查看：
- 日誌檔案：`logs/django_app.log`
- 環境變數配置：`ENV_CONFIG.md`
- 腳本使用說明：`SCRIPT_INTEGRATION.md`
- 專案說明：`README.md`
