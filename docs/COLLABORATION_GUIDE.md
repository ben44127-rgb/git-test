# 🔗 三人協作 - 連接配置指南

## 📋 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                    前端 (Frontend)                           │
│                    localhost:5173                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ HTTP API + CORS
                 │
┌────────────────▼────────────────────────────────────────────┐
│                 Django 後端 (Backend)                        │
│                 localhost:30000                             │
│  - 用戶認證 (JWT)                                           │
│  - 圖片上傳/下載                                           │
│  - 虛擬試穿業務邏輯                                         │
└────────────────┬─────────────────┬──────────────────────────┘
                 │                 │
         HTTP API        MinIO S3  │ Postgres
                 │        Storage  │ Database
                 │        (9000)   │ (9090)
┌────────────────▼─────┐  ┌───────▼────┐
│  AI 後端 (AI Team)    │  │  PostgreSQL │
│  [手動設置]          │  │  MinIO      │
│  localhost:8002      │  └─────────────┘
│  或                   │
│  [真實AI伺服器IP]     │
└───────────────────────┘
```

---

## 🎯 三種環境配置

### 環境 1️⃣：本地個別開發（開發階段）

**適用情況：** 初期開發，各自獨立測試功能

```env
# .env 配置
FRONTEND_URL=http://localhost:5173
AI_BACKEND_URL=http://localhost:8002
MINIO_ENDPOINT=localhost:9000
DB_HOST=localhost
```

**啟動步驟：**

```bash
# 終端 1：前端
cd frontend && npm run dev

# 終端 2：後端
python manage.py runserver 0.0.0.0:30000

# 終端 3：AI 後端（模擬）
python test_file/mock_ai_backend.py --port 8002

# 終端 4：Docker 服務（數據庫 + MinIO）
docker-compose up postgres minio
```

**驗證：**
- 前端：http://localhost:5173
- 後端：http://localhost:30000/api/docs
- AI 後端：http://localhost:8002/health
- MinIO：http://localhost:9001（Console）

---

### 環境 2️⃣：Docker 容器環境（集成測試）

**適用情況：** 本地測試，所有服務在 Docker 中運行

```env
# .env 配置
FRONTEND_URL=http://localhost:5173
AI_BACKEND_URL=http://172.17.0.1:8002
MINIO_ENDPOINT=localhost:9000
MINIO_CONTAINER_ENDPOINT=minio:9000
DB_HOST=postgres
```

**啟動步驟：**

```bash
# 使用 docker-compose 啟動所有後端服務
docker-compose up

# 前端仍在本地
cd frontend && npm run dev
```

**重點：**
- 容器內訪問 MinIO：使用 `MINIO_CONTAINER_ENDPOINT=minio:9000`
- 容器外訪問 MinIO：使用 `MINIO_ENDPOINT=localhost:9000`
- 訪問主機服務（AI 後端）：使用 `172.17.0.1`

---

### 環境 3️⃣：協作集成測試（與 AI 團隊協作）

**適用情況：** 與其他組員進行完整集成測試

```env
# .env 配置
FRONTEND_URL=http://[前端團隊地址]
AI_BACKEND_URL=http://[AI團隊IP]:8002
MINIO_ENDPOINT=[MinIO伺服器IP]:9000
DB_HOST=[數據庫伺服器IP]
```

**配置步驟：**

1. **決定一個物理主機作為中樞**
   - 例如：192.168.1.100（你的電腦或伺服器）

2. **前端團隊**
   ```env
   BACKEND_URL=http://192.168.1.100:30000
   ```

3. **你的後端**
   ```env
   FRONTEND_URL=http://[前端IP]:[前端端口]
   AI_BACKEND_URL=http://[AI團隊IP]:8002
   MINIO_ENDPOINT=localhost:9000
   DB_HOST=localhost
   ```

4. **AI 後端團隊**
   ```
   監聽 8002 端口，接收 POST /virtual_try_on/clothes/combine
   ```

---

## 🔑 關鍵環境變量說明

| 變量 | 說明 | 本地 | Docker | 生產 |
|------|------|------|--------|------|
| `FRONTEND_URL` | 前端地址（用於 CORS） | `localhost:5173` | `localhost:5173` | `https://your-domain.com` |
| `AI_BACKEND_URL` | **AI 後端地址（手動切換）** | `localhost:8002` | `172.17.0.1:8002` | `http://ai-team-ip:8002` |
| `MINIO_ENDPOINT` | MinIO 外部訪問 | `localhost:9000` | `localhost:9000` | `minio.your-domain:9000` |
| `MINIO_CONTAINER_ENDPOINT` | MinIO 容器內訪問 | - | `minio:9000` | - |
| `DB_HOST` | 數據庫地址 | `localhost` | `postgres` | `db.your-domain` |
| `AI_VIRTUAL_TRY_ON_ENDPOINT` | AI 虛擬試穿端點 | `/virtual_try_on/clothes/combine` | 同 | 同 |

---

## 🚀 快速切換指南

### 從本地開發 → Docker 環境

```bash
# 1. 更新 .env
AI_BACKEND_URL=http://172.17.0.1:8002
MINIO_CONTAINER_ENDPOINT=minio:9000
DB_HOST=postgres

# 2. 重啟後端
docker-compose restart backend
```

### 從本地開發 → 與 AI 團隊協作

```bash
# 1. 檢查 AI 團隊的伺服器 IP
AI_TEAM_IP=192.168.1.50

# 2. 更新 .env
AI_BACKEND_URL=http://192.168.1.50:8002

# 3. 告訴前端團隊
BACKEND_IP=192.168.1.100  # 你的 IP

# 4. 重啟後端
python manage.py runserver 0.0.0.0:30000
```

---

## ✅ 連接驗證清單

### 後端自檢

```bash
# 1. 驗證所有環境變量
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings
print('✓ Frontend:', settings.FRONTEND_URL)
print('✓ AI Backend:', settings.AI_BACKEND_URL)
print('✓ MinIO Endpoint:', settings.MINIO_ENDPOINT)
print('✓ DB Host:', settings.DATABASES['default']['HOST'])
"

# 2. 驗證 AI 後端連接
curl http://localhost:8002/health

# 3. 驗證 MinIO 連接
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from picture.views import get_minio_client
client = get_minio_client()
if client:
    print('✓ MinIO 連接成功')
    buckets = client.list_buckets()
    for bucket in buckets:
        print(f'  - Bucket: {bucket.name}')
else:
    print('✗ MinIO 連接失敗')
"

# 4. 驗證數據庫連接
python manage.py migrate --check
```

### 前端連接檢查

```javascript
// 檢查 CORS 是否正常
fetch('http://localhost:30000/api/health', {
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' }
})
.then(r => r.json())
.then(d => console.log('✓ Backend:', d))
.catch(e => console.error('✗ Backend:', e))

// 檢查 MinIO 是否可訪問
fetch('http://localhost:9000/')
.then(() => console.log('✓ MinIO'))
.catch(() => console.error('✗ MinIO'))
```

### AI 後端連接檢查

```bash
# 檢查健康狀態
curl http://localhost:8002/health

# 測試虛擬試穿端點
curl -X POST http://localhost:8002/virtual_try_on/clothes/combine \
  -F "model_image=@model.png" \
  -F "garment_images=@garment1.png" \
  -F "garment_images=@garment2.png" \
  -F "model_info={...}" \
  -F "garments=[...]"
```

---

## 🐛 常見問題

### 問題 1：前端無法連接後端

**症狀：** CORS 錯誤或 404

**檢查：**
```bash
# 1. 後端是否運行
curl http://localhost:30000/api/docs

# 2. CORS 配置是否正確
grep "CORS" .env

# 3. 前端配置的後端 URL 是否正確
# 檢查前端代碼中的 API_BASE_URL
```

### 問題 2：無法上傳圖片

**症狀：** 上傳失敗或 500 錯誤

**檢查：**
```bash
# 1. MinIO 是否運行
docker-compose logs minio

# 2. MinIO 連接是否正確
python manage.py shell
>>> from picture.views import get_minio_client
>>> client = get_minio_client()
>>> print(client)  # 應該返回 client 物件

# 3. Bucket 是否存在
curl http://localhost:9001  # 進入 MinIO console 檢查
```

### 問題 3：虛擬試穿失敗

**症狀：** 503 或連接超時

**檢查：**
```bash
# 1. AI 後端是否運行
curl http://localhost:8002/health

# 2. AI_BACKEND_URL 是否正確
grep "AI_BACKEND_URL" .env

# 3. 檢查後端日誌
docker-compose logs backend | grep -i "ai\|error"

# 4. 測試 AI 後端連接
curl -X POST http://localhost:8002/virtual_try_on/clothes/combine
```

---

## 📚 相關檔案

- **`.env`** - 主配置檔案
- **`config/settings.py`** - Django 設置
- **`combine/views.py`** - 虛擬試穿 API
- **`picture/views.py`** - 圖片上傳 API
- **`docker-compose.yml`** - 容器編排

---

## 🎯 三人協作最佳實踐

### 前端團隊

```javascript
// 環境配置
const API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost:30000';

// 請求攔截器（自動附加 JWT）
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 你的後端（Django）

```python
# 記錄所有 AI 後端通信
logger.info(f"連接 AI 後端：{settings.AI_BACKEND_URL}")
logger.info(f"接收 AI 響應：{ai_response.status_code}")

# 確保返回前端的 URL 可訪問
response_data = {
    'model_picture': settings.MINIO_EXTERNAL_URL + '/path/to/image.png'
}
```

### AI 後端團隊

```python
# 預期請求格式
def virtual_try_on():
    model_image = request.files['model_image']
    garment_images = request.files.getlist('garment_images')
    model_info = json.loads(request.form['model_info'])
    garments = json.loads(request.form['garments'])
    
    # 返回 multipart 響應
    return multipart_response
```

---

## 🔄 日常開發流程

```bash
# 1. 早上啟動服務
docker-compose up postgres minio
python test_file/mock_ai_backend.py &
python manage.py runserver &

# 2. 與團隊同步最新 .env 設置
git pull
source .env

# 3. 測試三方連接
curl http://localhost:8002/health          # AI
curl http://localhost:9001                 # MinIO
python manage.py migrate --check           # DB

# 4. 提交代碼
git add .
git commit -m "Feature: ..."
git push

# 5. 晚上關閉服務
killall python
docker-compose down
```

---

祝開發順利！🚀
