# test_project 系統架構圖

> 更新時間: 2026-03-23  
> 說明: 根據實際代碼檢查的 test_project 微伺務系統架構，包含前端頁面、兩個後端伺務和存儲層

## 📊 完整系統架構圖（含流程順序）

```
                         👤 User Browser
                              │
                              │ HTTP :8080
                              │
                         ┌────▼──────┐
                         │ Frontend  │
                         │ :8080     │
                         └────┬──────┘
                              │
                              │ HTTP :30000
                              │ POST /picture/clothes/upload_image
                              │
                    ┌─────────▼──────────┐
                    │  Main Backend     │
                    │  test_project     │
                    │  Django :30000    │
                    └─┬────┬──────────┬─┘
                      │    │          │
        ┌─────TCP─────┘    │ S3 API  │ HTTP :8002
        │ :9090       │ :9000  │ /virtual_try_on/
        │             │        │ clothes/remove_bg
        ▼             ▼        ▼
    ┌────────┐  ┌────────┐  ┌─────────┐
    │PostgreSQL  │ MinIO  │  │AI       │
    │:9090   │  │:9000   │  │Backend  │
    │(DB)    │  │(Files) │  │:8002    │
    └────────┘  └────────┘  └────┬────┘
                                  │ HTTP
                                  │ Gemini API
                                  │ (External)
                                  ▼
                            [Gemini AI]
                          (remove_bg)
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

## 📋 系統組件詳解

| 組件 | Port | 類型 | 主要功能 |
|------|------|------|---------|
| **Frontend** | 8080 | React/Vite | 用戶界面、圖片上傳、結果展示 |
| **Main Backend** | 30000 | Django | 用戶認證、圖片管理、API 路由 |
| **AI Backend** | 8002 | Django | Gemini API 調用、去背處理 |
| **PostgreSQL** | 9090※ | 數據庫 | 用戶數據、認證信息、記錄|
| **MinIO** | 9000 | 對象存儲 | 圖片存儲、URL 生成 |

※ Container 內部 Port 5432，主機外部 Port 9090

---

📌 **詳細 API 文檔請參見 [API.md](API.md)**

## 🚀 Docker 容器設定

| 伺務 | 容器名 | 鏡像 | 映射 Port |
|------|--------|------|----------|
| Frontend | frontend | Node.js/Nginx | 8080:8080 |
| Main Backend | django-backend | Python/Django | 30000:30000 |
| PostgreSQL | auth_postgres | postgres:15 | 9090:5432 |
| MinIO | minio | minio/minio | 9000:9000, 9001:9001 |

---

## 📝 連接設定

```bash
# .env 中的關鍵設定:

# 主後端連接 AI 伺務
AI_BACKEND_URL=http://host.docker.internal:8002/virtual_try_on/clothes/remove_bg

# MinIO 內部連接 (Docker 中)
MINIO_ENDPOINT=minio:9000

# MinIO 外部 URL (前端瀏覽器)
MINIO_EXTERNAL_URL=http://192.168.233.128:9000

# PostgreSQL 外部連接
DB_HOST=db
DB_PORT=5432

# 本地外部訪問
PostgreSQL: localhost:9090
MinIO API: localhost:9000
MinIO Console: localhost:9001
```

---

## ✅ 啟動順序

```
1. PostgreSQL (db:5432)
2. MinIO (:9000, :9001)
3. Main Backend (:30000)
4. AI Backend (:8002) - 可並行
5. Frontend (:8080) - 最後
```

---

# 🏗️ Django 項目結構

## 📁 完整項目目錄樹

```
test_project/
│
├── manage.py                      # Django 管理命令
├── requirements.txt               # Python 依賴
├── Pipfile                       # Pipenv 依賴管理
├── db.sqlite3                    # SQLite 數據庫 (開發環境)
├── docker-compose.yml            # Docker 容器編排
├── Dockerfile                    # Django 容器設定
├── start.sh                      # 啟動腳本
├── stop.sh                       # 停止腳本
│
├── config/                       # 專案全局設定
│   ├── __init__.py
│   ├── settings.py              # Django 主要設定
│   ├── urls.py                  # 全局 URL 路由
│   ├── asgi.py                  # ASGI 應用設定
│   ├── wsgi.py                  # WSGI 應用設定
│   └── __pycache__/            # Python 緩存
│
├── modules/                      # 業務模組（模組/Actor/Function 架構）
│   │
│   ├── accounts/                # 模組：用戶賬戶管理
│   │   ├── __init__.py
│   │   ├── admin.py             # Admin 後台設定
│   │   ├── apps.py              # 應用設定
│   │   ├── models.py            # 用戶認證相關模型
│   │   │   └── User, Profile, 認證相關模型
│   │   ├── serializers.py       # DRF 序列化器
│   │   │   └── UserSerializer, 註冊/登入序列化器
│   │   ├── views.py             # API 視圖
│   │   │   ├── register (POST)  # 用戶註冊
│   │   │   ├── login (POST)     # 用戶登入
│   │   │   ├── logout (POST)    # 用戶登出
│   │   │   ├── delete (POST)    # 刪除賬號
│   │   │   └── user_info        # 上傳模特基本資料
│   │   ├── urls.py              # 應用級 URL 路由
│   │   ├── permissions.py       # 自訂權限類
│   │   ├── migrations/          # 數據庫遷移
│   │   │   ├── __init__.py
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_remove_clothes_clothes_size_and_more.py
│   │   │   └── 0003_alter_clothes_clothes_arm_length_and_more.py
│   │   │
│   │   └── Actor 設計 (使用者類型):
│   │       ├── user - 普通用戶（可註冊、登入、管理資料）
│   │       ├── admin - 管理員（完全控制）
│   │
│   └── picture/                 # 模組：圖片和衣伺處理
│       ├── __init__.py
│       ├── admin.py             # Admin 後台設定
│       ├── apps.py              # 應用設定
│       ├── models.py            # 圖片、衣伺相關模型
│       │   └── Clothes, ClothesImage, UserPhoto 等
│       ├── serializers.py       # DRF 序列化器
│       │   └── ClothesSerializer, 圖片上傳序列化器
│       ├── views.py             # API 視圖
│       │   ├── upload_image (POST)    # 上傳衣伺圖片 + 去背
│       │   ├── upload_user_picture    # 上傳模特照片 + 去背
│       │   ├── favorites (GET)        # 查看喜歡的衣伺列表
│       │   └── 虛擬試衣相關 API
│       ├── urls.py              # 應用級 URL 路由
│       ├── permissions.py       # 自訂權限類
│       ├── services/            # 業務邏輯伺務層
│       │   ├── __init__.py
│       │   ├── image_service.py    # 圖片處理邏輯
│       │   │   ├── 圖片驗證
│       │   │   ├── 圖片保存到 MinIO
│       │   │   └── URL 生成
│       │   └── ai_service.py       # AI 相關邏輯
│       │       ├── 調用 Gemini API
│       │       ├── 去背處理
│       │       └── 結果存儲
│       │
│       ├── migrations/          # 數據庫遷移
│       │   └── __init__.py
│       │
│       └── Actor 設計 (使用者類型):
│           ├── user - 普通用戶（可上傳圖片、標記喜歡）
│           ├── admin - 管理員（可管理所有圖片）
│
├── Docs/                        # 文檔
│   ├── api.csv                 # API 規格 (CSV 格式)
│   ├── api.xlsx                # API 規格 (Excel 格式)
│   ├── API.md                  # API 文檔
│   ├── Architecture.md         # 架構文檔
│   └── README.md               # 專案說明
│
├── logs/                        # 日誌檔案
│
└── picture/                    # 媒體檔案存儲
    └── (已上傳的圖片)
```

## 🔗 模組/Actor/Function 映射表

| 模組 | Actor | Function | API 端點 | 方法 |
|------|-------|----------|---------|------|
| **accounts** | user | register | `/account/user/register` | POST |
| **accounts** | user | login | `/account/user/login` | POST |
| **accounts** | user | logout | `/account/user/logout` | POST |
| **accounts** | user | delete | `/account/user/delete` | POST |
| **accounts** | user | user_info | `/account/user/user_info` | POST |
| **picture** | user | upload_image | `/picture/clothes/upload_image` | POST |
| **picture** | user | user_picture | `/picture/user/user_picture` | POST |
| **picture** | user | favorites | `/picture/clothes/favorites` | GET |

## 🔐 認證架構

```
┌────────────────┐
│   User Login   │
└───────┬────────┘
        │ POST /account/user/login
        ▼
┌────────────────────────────────────┐
│  生成 JWT Token                    │
│  - access_token (短期)              │
│  - refresh_token (長期)             │
└────────┬─────────────────────────┬──┘
         │                         │
         ▼ 存儲                    ▼ 返回
    Frontend LocalStorage     JSON Response
         │
         │ Authorization: Bearer <access_token>
         ▼
┌────────────────────┐
│  驗證 JWT Token    │
│  (Account 模組)    │
└────────┬───────────┘
         │
    ✓ 有效 ✗ 無效/過期
         │      │
         ▼      ▼
    允許訪問  403/401 錯誤
         │      │
         └──────┘
```

## 📊 數據流

### 1. 圖片上傳流程

```
User → Frontend
   ↓
POST /picture/clothes/upload_image
   ↓
accounts.permissions (JWT 驗證)
   ↓
picture.views.upload_image()
   ↓
picture.services.image_service
   ├─ 驗證檔案
   ├─ 存儲到 MinIO
   └─ 返回 URL
   ↓
picture.services.ai_service
   ├─ 調用 Gemini API 去背
   ├─ 保存結果到 MinIO
   └─ 存儲地址到 PostgreSQL
   ↓
返回 Response (success: true, processed_url, ai_status)
   ↓
Frontend 顯示結果
```

### 2. 用戶認證流程

```
用戶輸入 email/password
   ↓
POST /account/user/login
   ↓
accounts.serializers (驗證數據)
   ↓
accounts.views.login()
   ├─ 檢查用戶是否存在
   ├─ 驗證密碼
   └─ 生成 JWT Token
   ↓
PostgreSQL (查詢用戶)
   ↓
返回 Response (access, refresh, user_info)
   ↓
Frontend 存儲 Token
```

## 🛠️ 常用命令

```bash
# 創建新資料庫遷移
python manage.py makemigrations

# 應用遷移
python manage.py migrate

# 創建超級用戶 (Admin)
python manage.py createsuperuser

# 運行開發伺伺器
python manage.py runserver

# 訪問 Django Admin
http://localhost:8000/admin/

# 進入 Django Shell
python manage.py shell
```

## 📚 依賴庫

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


