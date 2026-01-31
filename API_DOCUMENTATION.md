# 圖片處理 API 完整文檔

## 📡 API 概覽

這個 Django 後端服務作為中間件，負責接收前端上傳的圖片，轉發給 AI 服務進行去背處理，然後將處理後的圖片儲存到 MinIO，並返回訪問連結。

---

## 🔗 端點列表

### 1. 健康檢查

**端點**: `GET /health`

**描述**: 檢查服務是否正常運行

**請求範例**:
```bash
curl http://localhost:30000/health
```

**回應範例**:
```json
{
  "status": "healthy",
  "message": "服務運行正常"
}
```

---

### 2. 圖片上傳和處理

**端點**: `POST /api/upload-image`

**描述**: 上傳圖片到 AI 服務進行去背處理，並儲存到 MinIO

**Content-Type**: `multipart/form-data`

**請求參數**:

| 參數名 | 類型 | 必填 | 描述 |
|--------|------|------|------|
| `image_data` | File | ✅ 是 | 圖片檔案（multipart/form-data） |
| `filename` | String | ✅ 是 | 檔案名稱（例如："photo.jpg"） |

**請求範例 (curl)**:
```bash
curl -X POST http://localhost:30000/api/upload-image \
  -F "image_data=@/path/to/image.jpg" \
  -F "filename=image.jpg"
```

**請求範例 (Python)**:
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

**請求範例 (JavaScript/Fetch)**:
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

## 📤 回應格式

### 成功回應 (200 OK)

```json
{
  "success": true,
  "message": "圖片處理和儲存成功",
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

**欄位說明**:
- `success`: 整體操作是否成功
- `message`: 操作描述資訊
- `ai_status`: AI 處理狀態
  - `status_code`: AI 服務返回的狀態碼
  - `message`: AI 處理結果描述
- `storage_status`: 儲存狀態
  - `success`: 是否成功儲存
  - `filename`: 在 MinIO 中的唯一檔案名稱
  - `original_filename`: 原始檔案名稱
  - `url`: 可訪問的預簽名 URL（7天有效期）
  - `storage`: 儲存類型（minio）
  - `bucket`: 儲存桶名稱

---

## ❌ 錯誤回應

### 400 Bad Request - 缺少參數

```json
{
  "success": false,
  "message": "請上傳圖片檔案（欄位名稱：image_data）"
}
```

或

```json
{
  "success": false,
  "message": "請提供檔案名稱（欄位名稱：filename）"
}
```

---

### 415 Unsupported Media Type - AI: 非圖片檔案

```json
{
  "success": false,
  "message": "AI 處理失敗",
  "ai_status": {
    "status_code": 415,
    "message": "上傳非圖片檔案"
  }
}
```

---

### 422 Unprocessable Entity - AI: 圖片模糊

```json
{
  "success": false,
  "message": "AI 處理失敗",
  "ai_status": {
    "status_code": 422,
    "message": "圖片過於模糊"
  }
}
```

---

### 500 Internal Server Error - AI: 模型失敗

```json
{
  "success": false,
  "message": "AI 處理失敗",
  "ai_status": {
    "status_code": 500,
    "message": "AI 模型運算失敗"
  }
}
```

---

### 503 Service Unavailable - 服務不可用

```json
{
  "success": false,
  "message": "無法連接到 AI 服務",
  "ai_status": {
    "status_code": 503,
    "message": "服務不可用"
  }
}
```

或 MinIO 不可用:

```json
{
  "success": false,
  "message": "儲存服務不可用",
  "ai_status": {
    "status_code": 200,
    "message": "去背成功"
  },
  "storage_status": {
    "success": false,
    "message": "MinIO 服務不可用"
  }
}
```

---

### 504 Gateway Timeout - 請求逾時

```json
{
  "success": false,
  "message": "AI 處理逾時",
  "ai_status": {
    "status_code": 504,
    "message": "請求逾時"
  }
}
```

---

## 🔄 完整工作流程

```
前端 → Django 後端 → AI 服務 (port 8002) → Django 後端 → MinIO → 前端
  │          │              │                    │           │         │
  │          │              │                    │           │         │
  └─ 上傳     └─ 轉發        └─ 去背處理          └─ 儲存     └─ 生成URL └─ 返回結果
     圖片        圖片+檔案名    返回處理結果         到MinIO      (7天有效)   給前端
```

### 詳細步驟:

1. **前端上傳** (POST /api/upload-image)
   - 欄位: `image_data` (檔案) + `filename` (字串)

2. **Django 後端接收**
   - 驗證參數完整性
   - 讀取圖片二進位資料

3. **轉發給 AI 服務** (POST http://192.168.233.128:8002/api/remove_bg)
   - 欄位: `clothes_image` (檔案流) + `clothes_filename` (檔案名稱)

4. **AI 服務處理**
   - 返回狀態碼: 200/415/422/500
   - 返回格式: JSON (base64) 或 二進位圖片

5. **Django 後端處理 AI 回應**
   - 解析返回資料（支援兩種格式）
   - 驗證 PNG 格式
   - 如果檔案名稱不是 .png，自動添加

6. **儲存到 MinIO**
   - 生成唯一檔案名稱: `processed_{隨機ID}_{原檔案名}.png`
   - 上傳到 bucket: `processed-images`

7. **生成預簽名 URL**
   - 有效期: 7 天
   - 包含簽名參數

8. **返回給前端**
   - 包含: AI 狀態 + 儲存狀態 + 訪問 URL

---

## ⚙️ 配置說明

### 環境變數 (.env)

```bash
# Django 配置
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-here

# AI 後端配置
AI_BACKEND_URL=http://192.168.233.128:8002/api/remove_bg
AI_REQUEST_TIMEOUT=60

# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=processed-images
MINIO_SECURE=False
```

### AI 後端要求

**端口**: 8002  
**路徑**: /api/remove_bg  
**方法**: POST  
**輸入格式**:
- `clothes_image`: 圖片檔案流
- `clothes_filename`: 檔案名稱

**輸出格式**:
- **Content-Type**: multipart/form-data 或 image/png
- **Body**: PNG 圖片二進位資料
- 直接返回處理後的圖片二進位流

**狀態碼**:
- `200`: 去背成功
- `415`: 上傳非圖片檔案
- `422`: 圖片過於模糊
- `500`: AI 模型運算失敗

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

### 3. 查看日誌

```bash
# 即時查看日誌
tail -f logs/django.log

# 或
tail -f logs/django_app.log
```

---

## 🔍 故障排除

### 問題 1: AI 服務連接失敗

**錯誤**: `無法連接到 AI 服務`

**解決方案**:
1. 檢查 AI 服務是否在 8002 端口運行
2. 測試連接: `curl http://192.168.233.128:8002/health` (如果有健康檢查端點)
3. 檢查 .env 中的 `AI_BACKEND_URL` 配置

---

### 問題 2: MinIO 連接失敗

**錯誤**: `MinIO 服務不可用`

**解決方案**:
1. 檢查 MinIO 容器: `docker ps | grep minio`
2. 啟動 MinIO: `docker-compose up -d minio`
3. 檢查連接: `curl http://localhost:9000/minio/health/live`

---

### 問題 3: 檔案名稱編碼問題

**問題**: 中文檔案名稱亂碼

**解決方案**:
- 前端發送時使用 UTF-8 編碼
- 或在前端先將中文檔案名稱轉換為英文

---

## 📊 效能考量

- **逾時設定**: AI 請求逾時 60 秒
- **檔案大小限制**: Django 預設 10MB (可在 settings.py 修改)
- **並行處理**: 使用 gunicorn 多 worker (生產環境)
- **預簽名 URL**: 7天有效期，避免頻繁生成

---

## 🔒 安全建議

1. **生產環境**:
   - 修改 `DJANGO_SECRET_KEY` 為強密鑰
   - 設定 `DEBUG=False`
   - 限制 `ALLOWED_HOSTS`
   - 使用 HTTPS (MinIO `MINIO_SECURE=True`)

2. **CORS 配置**:
   - 限制 `CORS_ALLOWED_ORIGINS` 為具體前端網域名稱
   - 不要在生產環境使用 `CORS_ALLOW_ALL_ORIGINS = True`

3. **檔案驗證**:
   - 後端已驗證 PNG 檔案標頭
   - AI 服務應該也驗證檔案類型

---

## 📞 相關資源

如有問題，請查看：
- 日誌檔案：`logs/django_app.log`
- 環境變數配置：`ENV_CONFIG.md`
- 腳本使用說明：`SCRIPT_INTEGRATION.md`
- 專案說明：`README.md`
