# test_project 系統架構圖

> 更新時間: 2026-04-19  
> 說明: AI 虛擬試衣系統的完整微伺務架構，三人協作分工（前端開發者、後端開發者、AI後端開發者）
> 部署方式: Docker & Docker Compose 容器化

## 📊 完整系統架構圖（三人協作）

```
                          👤 User Browser
                               │
                 ┌─────────────┴─────────────┐
                 │ HTTP :8080                │
                 ▼                           ▼
          ┌──────────────┐         ┌──────────────────┐
          │ 👨‍💻 Frontend  │         │  📚 Documentation│
          │ React/Vite   │         │   & UI 設計      │
          │ :8080        │         └──────────────────┘
          │              │
          │ (前端開發者)  │
          └──────┬───────┘
                 │
                 │ HTTP REST API :30000
                 │ (多個端點)
                 ▼
      ┌──────────────────────────┐
      │  👨‍💼 Main Backend         │
      │  Django :30000           │
      │  (業務邏輯 & 系統整合)    │
      │                          │
      │  - 用戶認證 (JWT)        │
      │  - 圖片管理              │
      │  - 虛擬試穿              │
      │  - API 路由              │
      │                          │
      │  (你的責任)              │
      └──┬─────────┬────────┬───┘
         │         │        │
         │ TCP     │ S3     │ HTTP :8002
         │ :9090   │ API    │ /virtual_try_on/
         │         │ :9000  │ clothes/remove_bg
         ▼         ▼        ▼
    ┌────────┐ ┌────────┐ ┌──────────┐
    │PostgreSQL│ MinIO  │ │👨‍🔬 AI   │
    │:9090    │ :9000  │ │ Backend  │
    │(DB)     │(Files) │ │ :8002    │
    │         │        │ │          │
    │- 用戶  │ ├─ Bucket
    │- 衣服  │ └─ URL生成
    │- 穿搭  │         │(AI開發者)│
    └────────┘ └────────┘ └────┬────┘
                               │ HTTP
                               │ Gemini API
                               │ (外部服務)
                               ▼
                         [Gemini AI]
                      (圖片去背處理)
```

### 🔄 流程說明

```
上傳圖片流程:
═════════════════════════════════════════════════
1. User → Frontend (:8080)              [瀏覽器打開頁面]
   └─ HTTP :8080
   
2. Frontend → Main Backend (:30000)     [上傳圖片]
   └─ HTTP POST /picture/clothes/upload_image
   
3. Main Backend → PostgreSQL (:9090)    [驗證用戶]
   └─ TCP :9090 (Django ORM)
   
4. Main Backend → MinIO (:9000)         [保存圖片]
   └─ S3 API :9000 (PUT Object)
   
5. Main Backend ← MinIO                 [返回圖片URL]
   └─ S3 API :9000 (返回預簽URL)
   
6. Frontend ← Main Backend              [返回結果]
   └─ HTTP 200 { image_url, ... }


去背流程:
═════════════════════════════════════════════════
1. Main Backend → AI Backend (:8002)    [請求去背]
   └─ HTTP POST
      /virtual_try_on/clothes/remove_bg
   
2. AI Backend → Gemini API              [調用外部API]
   └─ HTTP POST (Gemini credentials)
   
3. Gemini API ← AI Backend              [返回去背圖]
   └─ HTTP 200 { image/png binary }
   
4. Main Backend ← AI Backend (:8002)    [返回結果]
   └─ HTTP 200 { image/png binary }
   
5. Main Backend → MinIO (:9000)         [保存去背結果]
   └─ S3 API :9000 (PUT Object)
   
6. Main Backend → PostgreSQL (:9090)    [記錄結果]
   └─ TCP :9090 (Update record)
   
7. Frontend ← Main Backend              [返回最終結果]
   └─ HTTP 200 { result_url, ... }
```

---

## 📋 系統組件詳解（三人分工）

| 組件 | Port | 開發者 | 主要功能 |
|------|------|--------|---------|
| **Frontend** | 8080 | 👨‍💻 前端開發者 | React/Vite、用戶界面、圖片上傳、結果展示 |
| **Main Backend** | 30000 | 👨‍💼 你（後端開發者） | 用戶認證、圖片管理、API 路由、業務邏輯、系統整合 |
| **AI Backend** | 8002 | 👨‍🔬 AI後端開發者 | Gemini API 調用、去背處理、AI 算法實現 |
| **PostgreSQL** | 9090※ | 你（後端開發者） | 用戶數據、認證信息、衣服、穿搭、虛擬試穿記錄 |
| **MinIO** | 9000 | 你（後端開發者） | 圖片存儲、預簽 URL 生成、文件管理 |
| **Gemini API** | - | AI後端開發者 | 外部 AI 服務、圖片去背 |

※ Container 內部 Port 5432，主機外部 Port 9090  
※ GCP 部署時用 IP `35.201.135.229` 訪問所有服務

---

📌 **詳細 API 文檔請參見 [API.md](API.md)**

## 🚀 Docker 容器設定（docker-compose.yml）

| 伺務 | 容器名 | 鏡像 | 映射 Port | 開發者 |
|------|--------|------|----------|--------|
| Frontend | frontend | Node.js/Nginx | 8080:8080 | 👨‍💻 前端 |
| Main Backend | django-backend | Python/Django | 30000:30000 | 👨‍💼 你（後端） |
| PostgreSQL | postgres | postgres:15 | 9090:5432 | 👨‍💼 你（後端） |
| MinIO | minio | minio/minio | 9000:9000, 9001:9001 | 👨‍💼 你（後端） |
| MinIO Console | - | (同 MinIO) | 9001:9001 | 👨‍💼 你（後端） |

**注**：AI Backend (:8002) 可單獨部署或本地運行，由 👨‍🔬 AI開發者 負責

---

## 🌐 GCP 部署配置（實際環境）

> 部署環境：Google Cloud Platform (GCP)  
> 外部 IP：**35.201.135.229**  
> 部署日期：2026-04-19

### GCP 外部訪問地址

```
┌──────────────────────────────────────────────────┐
│    GCP VM 外部 IP: 35.201.135.229              │
├──────────────────────────────────────────────────┤
│ 服務              │ 外部地址             │
├──────────────────────────────────────────────────┤
│ Django API       │ http://:30000        │
│ MinIO API        │ http://:9000         │
│ MinIO 管理台     │ http://:9001         │
│ PostgreSQL       │ :9090                │
│ AI Backend       │ http://:8002         │
│ Django Admin     │ http://:30000/admin  │
└──────────────────────────────────────────────────┘
```

### 容器內部訪問地址（Docker 容器間通信）

```
Django → PostgreSQL:  postgres:5432
Django → MinIO:       minio:9000
Django → AI Backend:  35.201.135.229:8002  （GCP 外部 IP）
```

### 關鍵配置要點

| 配置項 | 值 | 說明 |
|--------|-----|------|
| **MINIO_EXTERNAL_URL** | http://35.201.135.229:9000 | 前端瀏覽器訪問 MinIO |
| **AI_BACKEND_URL** | http://35.201.135.229:8002 | Django 調用 AI Backend |
| **DJANGO_ALLOWED_HOSTS** | ...35.201.135.229 | Django 認可的主機 |
| **CORS_ALLOWED_ORIGINS** | 包含 35.201.135.229 | 允許跨域訪問的源 |
| **PostgreSQL Port** | 容器內 5432 → 外部 9090 | 正確的 port 映射 |

---

## � Docker 通信完整路徑圖

> **核心原則**：  
> - **容器內部通信** → 使用容器名稱 + 內部 port (postgres:5432, minio:9000)  
> - **訪問宿主機服務** → 使用外部 IP + 映射 port (35.201.135.229:port)  
> - **所有配置集中在 .env** → 改一個地方，本地開發 ↔ GCP 部署無縫切換

### 完整通信拓撲圖

```
┌─────────────────────────────────────────────────────────────────┐
│                   GCP VM (35.201.135.229)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────── Docker Network (app-network) ───────────┐  │
│  │                                                          │  │
│  │  ┌──────────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │ Django       │  │PostgreSQL│  │ MinIO    │          │  │
│  │  │ :30000       │  │ :5432    │  │ :9000    │          │  │
│  │  │ (容器內)     │  │(容器內)  │  │(容器內)  │          │  │
│  │  └──────────────┘  └──────────┘  └──────────┘          │  │
│  │       ▲ (容器名)       ▲ (容器名)       ▲ (容器名)     │  │
│  │       │ postgres:      │ minio:         │              │  │
│  │       │ 5432           │ 9000           │              │  │
│  │       └─────────────────────┬──────────┬────┘          │  │
│  │                             │          │               │  │
│  │                     【容器內部通信】    │               │  │
│  │                                       │               │  │
│  └───────────────────────────────────────┼───────────────┘  │
│       ▲               ▲               ▲  │                  │
│       │ :30000        │ :9090         │  │ :9000 & :9001   │
│       │(port map)     │(port map)     │  │ (port map)      │
│       │ 外部:30000    │ 外部:9090     │  │ 外部:9000-9001 │
│       │               │               │  │                 │
│  ┌────┴───────┬───────┴─────┬────────┴──┴─────────────┐   │
│  │            │             │                         │   │
│  │      ┌─────▼──────┐  ┌───▼────────┐         ┌──────▼──┐│
│  │      │ 瀏覽器/     │  │ AI Backend │         │Django  │ │
│  │      │ 外部客戶端   │  │ (宿主機)   │         │Admin   │  │
│  │      │ :30000     │  │ :8002      │         │:30000  ││
│  │      │ :9000      │  │            │         │/admin  ││
│  │      │ :9001      │  │ 需要用:    │         │        ││
│  │      │            │  │ 35.201...  │         │(內部)  ││
│  │      │(透過VM IP) │  │ :8002      │         │        ││
│  │      └────────────┘  └────────────┘         └────────┘│
│  │                            ▲                            │
│  │                            │ HTTP                       │
│  │                     【透過外部 IP】                      │
│  │                                                         │
│  └─────────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────────┘
```

### 通信路由對照表

| 從 | 到 | 使用 | ❌ 不要用 | 說明 |
|---|---|------|---------|------|
| **Django** | PostgreSQL | `postgres:5432` | `localhost:5432` | 容器內通信用容器名 |
| **Django** | MinIO | `minio:9000` | `localhost:9000` | 容器內通信用容器名 |
| **Django** | AI Backend | `35.201.135.229:8002` | `localhost:8002` | 訪問宿主機用外部IP |
| **前端瀏覽器** | Django API | `35.201.135.229:30000` | `localhost:30000` | 外部訪問用外部IP |
| **前端瀏覽器** | MinIO | `35.201.135.229:9000` | `localhost:9000` | 外部訪問用外部IP |
| **前端瀏覽器** | MinIO Console | `35.201.135.229:9001` | `localhost:9001` | 外部訪問用外部IP |

### Django 程式碼示例（settings.py）

```python
import os

# 【容器內部通信】
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('DB_HOST', 'postgres'),         # ✓ 容器名
        'PORT': int(os.getenv('DB_PORT', 5432)),          # ✓ 容器內部port
    }
}

# MinIO（容器內部）
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000')  # ✓ 容器名

# 【訪問宿主機服務】
AI_BACKEND_URL = os.getenv('AI_BACKEND_URL', 'http://35.201.135.229:8002')  # ✓ 外部IP

# CORS（前端訪問 Django）
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",          # 本地開發
    "http://35.201.135.229:8080",    # GCP 前端
]
```

---

## 📝 連接設定（.env 環境變數）

> **🎯 關鍵原則**：
> 
> **改 .env，不改程式碼！**  
> 本地開發和 GCP 部署使用 **完全相同的 Django 程式碼**，只需改 `.env` 檔案。

```bash
# ═══════════════════════════════════════════════════════════
# 你（後端開發者）需要配置的連接設定:
# ═══════════════════════════════════════════════════════════

# 【Django 應用】
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,django-backend,35.201.135.229

# ═══════════════════════════════════════════════════════════
# ⭐ 容器內部通信 → 使用容器名稱（Docker DNS 自動解析）
# ═══════════════════════════════════════════════════════════

# 【PostgreSQL 數據庫連接】(你負責)
# - Django 在容器內部訪問 PostgreSQL
# - 使用容器名稱 'postgres' (不用改)
# - 使用容器內部 port 5432 (不用改)
# - 無論本地還是 GCP 部署都是這個值!
DB_HOST=postgres              # ✓ 容器名稱（本地&GCP都一樣）
DB_PORT=5432                  # ✓ 容器內部標準port（不要改！）
DB_NAME=auth_db
DB_USER=auth_user
DB_PASSWORD=auth_password_123

# 【MinIO 對象存儲配置】(你負責)
# - Django 在容器內部訪問 MinIO
# - 使用容器名稱 'minio' (不用改)
# - 使用容器內部 port 9000 (不用改)
# - 無論本地還是 GCP 部署都是這個值!
MINIO_ENDPOINT=minio:9000     # ✓ 容器名:內部port（本地&GCP都一樣）
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=processed-images

# ═══════════════════════════════════════════════════════════
# ⭐ 外部訪問 → 使用外部 IP（讓前端瀏覽器能訪問）
# ═══════════════════════════════════════════════════════════

# 【MinIO 外部 URL】(前端使用)
# - 前端在瀏覽器中訪問 MinIO（下載圖片）
# - 本地開發：http://localhost:9000
# - GCP 部署：http://35.201.135.229:9000
# 【改這裡根據環境】
MINIO_EXTERNAL_URL=http://35.201.135.229:9000  # ← 改為你的環境IP

# ═══════════════════════════════════════════════════════════
# ⭐ Django 調用外部服務 → 使用外部 IP
# ═══════════════════════════════════════════════════════════

# 【AI 後端連接】(你調用)
# - Django 在容器內調用 AI Backend（在宿主機上）
# - 因為 AI Backend 不在同一個 Docker network
# - 需要用宿主機的外部 IP
# 【改這裡根據 AI Backend 位置】
# 選項 1: 同一 GCP VM
AI_BACKEND_URL=http://35.201.135.229:8002
# 選項 2: 本地機器（開發環境）
# AI_BACKEND_URL=http://192.168.x.x:8002  # 改為你的本地IP
# 選項 3: 不同 GCP VM
# AI_BACKEND_URL=http://[其他VM的IP]:8002

# ═══════════════════════════════════════════════════════════
# ⭐ CORS 配置（前端能訪問 API）
# ═══════════════════════════════════════════════════════════
CORS_ALLOWED_ORIGINS=http://localhost:8080,http://localhost:5173,http://35.201.135.229:8080,http://35.201.135.229:5173

# ═══════════════════════════════════════════════════════════
# 📋 訪問端點速查表
# ═══════════════════════════════════════════════════════════

# 🟢 容器內部通信（自動通過 Docker DNS）
#    PostgreSQL:    postgres:5432
#    MinIO API:     minio:9000
#    Django:        django-backend:30000

# 🔵 外部訪問（透過 GCP 外部 IP 35.201.135.229）
#    Main Backend:      http://35.201.135.229:30000
#    MinIO API:         http://35.201.135.229:9000
#    MinIO Console:     http://35.201.135.229:9001
#    PostgreSQL 外部:   35.201.135.229:9090
#    AI Backend:        http://35.201.135.229:8002
#    Django Admin:      http://35.201.135.229:30000/admin

# 🟣 本地開發環境（localhost）
#    Main Backend:      http://localhost:30000
#    MinIO API:         http://localhost:9000
#    MinIO Console:     http://localhost:9001
#    PostgreSQL 外部:   localhost:9090
```

### 📌 .env 快速修改檢查清單

**部署環境切換時，只需修改這三項**：

- [ ] `MINIO_EXTERNAL_URL` → 改為該環境的 IP（或 localhost）
- [ ] `AI_BACKEND_URL` → 改為 AI Backend 實際位置的 IP
- [ ] `DJANGO_ALLOWED_HOSTS` → 加入該環境的 IP（非必須，但建議）

**不要改的項目**（本地 ↔ GCP 都一樣）：

- ✓ `DB_HOST=postgres` 
- ✓ `DB_PORT=5432`
- ✓ `MINIO_ENDPOINT=minio:9000`

---

## 🎯 三種常見環境配置

### 1️⃣ 本地開發環境（localhost）

```bash
DB_HOST=postgres              # ✓ 不變
DB_PORT=5432                  # ✓ 不變
MINIO_ENDPOINT=minio:9000     # ✓ 不變
MINIO_EXTERNAL_URL=http://localhost:9000      # ← 改這裡
AI_BACKEND_URL=http://localhost:8002          # ← 改這裡
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,django-backend
```

### 2️⃣ GCP 部署（同一 VM，IP: 35.201.135.229）

```bash
DB_HOST=postgres              # ✓ 不變
DB_PORT=5432                  # ✓ 不變
MINIO_ENDPOINT=minio:9000     # ✓ 不變
MINIO_EXTERNAL_URL=http://35.201.135.229:9000  # ← 改這裡
AI_BACKEND_URL=http://35.201.135.229:8002      # ← 改這裡
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,django-backend,35.201.135.229
```

### 3️⃣ 生產環境（不同 VM）

```bash
DB_HOST=postgres              # ✓ 不變
DB_PORT=5432                  # ✓ 不變
MINIO_ENDPOINT=minio:9000     # ✓ 不變
MINIO_EXTERNAL_URL=http://[MinIO_VM_IP]:9000   # ← 改為 MinIO VM IP
AI_BACKEND_URL=http://[AI_VM_IP]:8002          # ← 改為 AI VM IP
DJANGO_ALLOWED_HOSTS=...,django-prod-vm,[MinIO_VM_IP]
```

---

## ✅ Docker Compose 啟動順序

```
1. PostgreSQL (:9090)           [你負責 - 後端開發者]
2. MinIO (:9000, :9001)        [你負責 - 後端開發者]
3. Main Backend (:30000)        [你負責 - 後端開發者]
4. AI Backend (:8002) ─ 可並行  [AI開發者負責]
5. Frontend (:8080) ─ 最後      [前端開發者負責]

# 啟動命令：
docker-compose up -d

# 停止命令：
docker-compose down

# 查看運行狀態：
docker-compose ps

# 檢查特定服務日誌：
docker-compose logs django-backend   # 你的後端服務日誌
docker-compose logs postgres          # 數據庫日誌
docker-compose logs minio            # MinIO 日誌
```

# 🏗️ Django 後端項目結構（你的責任）

## 📁 完整項目目錄樹

```
/home/test_project/backend/git-test/
│
├── manage.py                      # Django 管理命令（你維護）
├── requirements.txt               # Python 依賴（你維護）
├── Pipfile                       # Pipenv 依賴管理
├── docker-compose.yml            # Docker 容器編排（你配置）
├── Dockerfile                    # Django 容器設定（你維護）
├── start.sh                      # 啟動腳本（你執行）
├── stop.sh                       # 停止腳本（你執行）
│
├── config/                       # 【全局配置】（你維護）
│   ├── __init__.py
│   ├── settings.py              # Django 主要設定
│   ├── urls.py                  # 全局 URL 路由
│   ├── asgi.py                  # ASGI 應用設定
│   └── wsgi.py                  # WSGI 應用設定
│
├── accounts/                    # 【模塊：用戶認證】（你開發）
│   ├── models.py                # User 模型（用戶資料、身體測量）
│   ├── views.py                 # API 視圖
│   │   ├── register (POST)      # 用戶註冊
│   │   ├── login (POST)         # 用戶登入 → JWT Token
│   │   ├── logout (POST)        # 用戶登出
│   │   └── delete (DELETE)      # 刪除賬號
│   ├── serializers.py           # DRF 序列化器（數據驗證）
│   ├── urls.py                  # 應用級 URL 路由
│   ├── permissions.py           # JWT 認證檢查
│   ├── migrations/              # 數據庫遷移
│   │   ├── 0001_initial.py
│   │   ├── 0002_xxx.py
│   │   └── 0003_xxx.py
│   └── admin.py                 # Django Admin 設定
│
├── picture/                     # 【模塊：圖片和衣服管理】（你開發）
│   ├── models.py                # Clothes、Outfit 模型
│   ├── views.py                 # API 視圖
│   │   ├── upload_image (POST)        # 上傳衣服 + 去背
│   │   ├── list_clothes (GET)         # 列出衣服
│   │   ├── delete_clothes (DELETE)    # 刪除衣服
│   │   └── create_outfit (POST)       # 建立穿搭組合
│   ├── serializers.py           # DRF 序列化器
│   ├── urls.py                  # 應用級 URL 路由
│   ├── permissions.py           # 權限檢查（確認所有者）
│   ├── services/                # 業務邏輯層（你實現）
│   │   ├── image_service.py     # 圖片處理邏輯
│   │   │   ├── validate_image
│   │   │   ├── upload_to_minio
│   │   │   └── generate_url
│   │   └── ai_service.py        # 調用 AI 後端
│   │       ├── call_remove_bg
│   │       └── handle_ai_response
│   ├── migrations/              # 數據庫遷移
│   └── admin.py                 # Django Admin 設定
│
├── combine/                     # 【模塊：虛擬試穿】（計畫中）
│   ├── models.py                # VirtualTryOn 模型
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── services/                # 業務邏輯層
│   └── migrations/
│
├── Docs/                        # 【文檔】（你維護）
│   ├── API.md                  # API 詳細文檔
│   ├── FUNCTIONS.md            # 功能清單
│   ├── Architecture.md         # 系統架構文檔
│   └── README.md               # 項目說明
│
├── logs/                        # 日誌檔案
│
└── db.sqlite3                  # SQLite 數據庫（開發用）
```

**說明**：你（後端開發者）負責開發和維護整個 Django 後端，包括所有模塊、數據庫設計和 API 路由。

## 🔗 API 映射表（你開發的 endpoints）

| 模組 | 功能編號 | API 端點 | HTTP 方法 | 說明 |
|------|---------|---------|---------|------|
| **accounts** | ACCOUNT-001 | `/account/user/register` | POST | 用戶註冊 |
| **accounts** | ACCOUNT-002 | `/account/user/login` | POST | 用戶登入 → JWT Token |
| **accounts** | ACCOUNT-003 | `/account/user/logout` | POST | 用戶登出 |
| **accounts** | ACCOUNT-004 | `/account/user/delete` | DELETE | 刪除賬號 |
| **accounts** | ACCOUNT-005 | `/account/user/info` | GET/PUT | 獲取/更新用戶資料 |
| **picture** | PHOTO-001 | `/picture/clothes/upload_image` | POST | 上傳衣服圖片 + 去背 |
| **picture** | PHOTO-002 | `/picture/clothes/list` | GET | 列出所有衣服 |
| **picture** | PHOTO-003 | `/picture/clothes/:id` | DELETE | 刪除衣服 |
| **picture** | PHOTO-004 | `/picture/outfit/create` | POST | 建立穿搭組合 |
| **picture** | PHOTO-005 | `/picture/outfit/list` | GET | 列出穿搭組合 |
| **combine** | TRYION-001 | `/combine/virtual_tryon` | POST | 虛擬試穿（計畫中） |

**認證方式**：所有 API（除 register/login）均需 JWT Authorization Header
```
Authorization: Bearer <access_token>
```

## 🔐 JWT 認證架構（你實現）

```
┌────────────────────────┐
│ 用戶輸入帳密            │
│ (email + password)     │
└──────────┬─────────────┘
           │
    POST /account/user/login
           ▼
┌──────────────────────────────────────┐
│ accounts.views.login()               │
│ - 檢查用戶是否存在 (PostgreSQL)       │
│ - 驗證密碼                           │
│ - 生成 JWT Token                    │
│   ├─ access_token (15分鐘)          │
│   └─ refresh_token (7天)             │
└──────┬──────────────────────┬────────┘
       │                      │
返回 JSON                 Frontend
{access, refresh, user_info}  │
                             ▼
                    LocalStorage 存儲
                             │
      ┌──────────────────────┘
      │
┌─────▼───────────────────────────────┐
│ 後續請求 Headers:                   │
│ Authorization: Bearer <access_token>│
└──────┬────────────────────────────┬─┘
       │                            │
       │ accounts.permissions       │
       │ (JWT 驗證中間件)           │
       ▼                            ▼
  ✓ 有效且未過期            ✗ 無效/過期
       │                            │
       ▼                            ▼
  允許訪問                    401 Unauthorized
  取得 user.id               返回錯誤
       │                      (需重新登入)
       └──────────┬───────────┘
```

## 📊 數據流（你負責的流程）

### 1️⃣ 圖片上傳 + 去背流程

```
使用者上傳衣服圖片
(Frontend :8080)
        │
POST /picture/clothes/upload_image
(multipart/form-data)
        │
        ▼
accounts.permissions
│檢查 JWT Token 有效性
│查詢用戶 ID
        │
        ▼
picture.views.upload_image()
│接收檔案、用戶 ID
│驗證檔案格式 (JPG/PNG)
│驗證檔案大小 (< 10MB)
        │
        ▼
picture.services.image_service.upload_to_minio()
│將原圖上傳到 MinIO
│生成預簽 URL
│保存記錄到 PostgreSQL
        │
        ▼
picture.services.ai_service.call_remove_bg()
│調用 AI Backend HTTP API
│POST http://AI:8002/virtual_try_on/clothes/remove_bg
│傳送原圖 URL
        │
        ▼
👨‍🔬 AI Backend (Gemini API)
│執行去背處理
│返回 Binary PNG
        │
        ▼
picture.services.ai_service.handle_response()
│將去背結果上傳到 MinIO
│生成預簽 URL
│更新 PostgreSQL 記錄
        │
        ▼
返回 Frontend
{
  success: true,
  original_url: "http://minio:9000/...",
  processed_url: "http://minio:9000/...",
  status: "completed"
}
        │
        ▼
Frontend 顯示結果圖片
```

### 2️⃣ 用戶登入流程

```
使用者輸入帳號密碼
(Frontend :8080)
        │
POST /account/user/login
{username, password}
        │
        ▼
accounts.serializers
│驗證輸入格式
        │
        ▼
accounts.views.login()
│查詢 PostgreSQL 檢查用戶
│驗證密碼 Hash
│生成 access_token (15分鐘)
│生成 refresh_token (7天)
        │
        ▼
返回 Frontend
{
  access: "eyJhbGc...",
  refresh: "eyJhbGc...",
  user: {id, username, email}
}
        │
        ▼
Frontend 存儲到 LocalStorage
        │
        ▼
後續所有請求加入:
Authorization: Bearer <access_token>
```

### 3️⃣ 穿搭管理流程

```
使用者建立穿搭組合
        │
POST /picture/outfit/create
{outfit_name, clothes_ids}
        │
        ▼
accounts.permissions (驗證 JWT)
        │
        ▼
picture.views.create_outfit()
│檢查所有衣服所有者
│建立 Outfit 記錄
│關聯 Clothes
        │
        ▼
PostgreSQL 存儲:
┌──────────────────────┐
│ Outfit 表            │
├──────────────────────┤
│ outfit_id            │
│ user_id (FK)         │
│ outfit_name          │
│ created_at           │
└──────────────────────┘
        │
        ▼
返回 Frontend
{
  outfit_id: 123,
  outfit_name: "Summer Look",
  clothes: [...]
}
```

## � 數據庫設計（PostgreSQL :9090）

### User 表 - 用戶資料

```
user_id (PK)
├─ user_uid (UUID)
├─ user_name (unique)
├─ user_email (unique)
├─ user_password (hashed)
├─ user_weight (kg)
├─ user_height (cm)
├─ user_arm_length (cm) - 手臂長度
├─ user_shoulder_width (cm) - 肩寬
├─ user_waistline (cm) - 腰圍
├─ user_leg_length (cm) - 腿長
└─ timestamp (created_at, updated_at)
```

### Clothes 表 - 衣服資料

```
clothes_id (PK)
├─ user_id (FK → User)
├─ clothes_name
├─ clothes_size
├─ original_image_url (MinIO)
├─ processed_image_url (去背後)
├─ clothes_type (shirt/pants/dress)
├─ color
└─ timestamp
```

### Outfit 表 - 穿搭組合

```
outfit_id (PK)
├─ user_id (FK → User)
├─ outfit_name
├─ clothes_ids (JSON 陣列或多對多)
└─ timestamp
```

**你需要維護的**：
- 所有表的遷移 (`python manage.py makemigrations`)
- 所有表的結構設計
- 外鍵約束和索引優化
- 數據一致性

## �️ 你常用的 Django 命令

```bash
# ═══════════════════════════════════════════════════════════
# 數據庫操作（你的責任）
# ═══════════════════════════════════════════════════════════

# 創建數據庫遷移（修改 models.py 後執行）
python manage.py makemigrations

# 應用遷移到數據庫
python manage.py migrate

# 創建超級用戶（Admin 後台管理員）
python manage.py createsuperuser

# ═══════════════════════════════════════════════════════════
# 開發伺務
# ═══════════════════════════════════════════════════════════

# 運行開發伺務器（本地測試）
python manage.py runserver 0.0.0.0:30000

# ═══════════════════════════════════════════════════════════
# Django Admin 後台
# ═══════════════════════════════════════════════════════════

# 訪問管理後台（需先創建超級用戶）
http://localhost:30000/admin/

# ═══════════════════════════════════════════════════════════
# 調試工具
# ═══════════════════════════════════════════════════════════

# 進入 Django Shell（測試模型、查詢）
python manage.py shell

# 檢查 Django 項目設定
python manage.py check

# ═══════════════════════════════════════════════════════════
# Docker 部署
# ═══════════════════════════════════════════════════════════

# 啟動所有服務（在 docker-compose.yml 目錄）
docker-compose up -d

# 查看服務日誌
docker-compose logs -f django-backend

# 停止所有服務
docker-compose down
```

根據 `requirements.txt`：
- **Django==5.1.5** - Web 框架
- **djangorestframework==3.14.0** - REST API 框架
- **djangorestframework-simplejwt==5.3.1** - JWT 認證
- **psycopg2-binary==2.9.9** - PostgreSQL 驅動
- **minio==7.2.20** - MinIO S3 SDK
- **django-cors-headers==4.6.0** - CORS 支持
- **requests==2.32.3** - HTTP 請求庫
- **python-dotenv==1.0.0** - 環境變數管理

## ✨ 將來擴展

```
modules/
├── accounts/           # ✓ 已實現
├── picture/           # ✓ 已實現
├── try_on/            # 🔄 虛擬試衣計算
├── recommendations/   # 📋 推薦系統
├── notifications/     # 🔔 通知系統
└── analytics/         # 📊 分析統計
```


