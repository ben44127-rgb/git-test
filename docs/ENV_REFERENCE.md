# 📋 .env 快速參考

## 🎯 一句話總結

```env
# 核心配置：
FRONTEND_URL=http://localhost:5173        # 前端地址（CORS）
AI_BACKEND_URL=http://localhost:8002      # AI 後端（手動切換）
MINIO_ENDPOINT=localhost:9000             # MinIO 外部訪問
DB_HOST=localhost                         # 數據庫
```

---

## 📝 完整配置模板

### 🖥️ 本地開發

```env
# Django
DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# 前端
FRONTEND_URL=http://localhost:5173
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOW_ALL_ORIGINS=False

# AI 後端（模擬）
AI_BACKEND_URL=http://localhost:8002
AI_VIRTUAL_TRY_ON_ENDPOINT=/virtual_try_on/clothes/combine

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_EXTERNAL_URL=http://localhost:9000

# 數據庫
DB_HOST=localhost
DB_PORT=9090
```

### 🐳 Docker 環境

```env
# Django
DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,django-backend

# 前端
FRONTEND_URL=http://localhost:5173
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# AI 後端（主機上的模擬 AI）
AI_BACKEND_URL=http://172.17.0.1:8002

# MinIO（容器間通信）
MINIO_ENDPOINT=localhost:9000
MINIO_CONTAINER_ENDPOINT=minio:9000
MINIO_EXTERNAL_URL=http://localhost:9000

# 數據庫（容器名）
DB_HOST=postgres
DB_PORT=5432
```

### 🌍 與 AI 團隊協作

```env
# Django
DEBUG=False
DJANGO_ALLOWED_HOSTS=[你的IP或域名]

# 前端
FRONTEND_URL=http://[前端團隊IP]:[前端端口]
CORS_ALLOWED_ORIGINS=http://[前端團隊IP]:[前端端口]

# AI 後端（真實 AI 伺服器）
# ⚠️  這是唯一需要改動的地方
AI_BACKEND_URL=http://[AI團隊IP]:8002

# MinIO
MINIO_ENDPOINT=[MinIO伺服器IP]:9000
MINIO_EXTERNAL_URL=http://[MinIO伺服器IP]:9000

# 數據庫
DB_HOST=[數據庫伺服器IP]
DB_PORT=5432
```

---

## 🔄 常用切換情景

### 切換 1️⃣：本地開發 → AI 團隊（真實 AI）

```bash
# 只需改一行
AI_BACKEND_URL=http://ai-team-ip:8002

# 查看是否成功
curl http://ai-team-ip:8002/health
```

### 切換 2️⃣：本地開發 → Docker 環境

```bash
# 改這些
AI_BACKEND_URL=http://172.17.0.1:8002
MINIO_CONTAINER_ENDPOINT=minio:9000
DB_HOST=postgres

# 啟動
docker-compose up
```

### 切換 3️⃣：Docker 環境 → 本地開發

```bash
# 改回這些
AI_BACKEND_URL=http://localhost:8002
DB_HOST=localhost

# 啟動
python manage.py runserver
```

---

## 🔍 環境變量詳解

### 服務連接相關

```env
# 前端地址（Django CORS 白名單用）
# 開發：http://localhost:5173
# 生產：https://your-domain.com
FRONTEND_URL=http://localhost:5173

# AI 後端地址（⚠️ 唯一需要手動切換的變數）
# 本地模擬：http://localhost:8002
# Docker 容器：http://172.17.0.1:8002
# 真實 AI：http://[AI團隊IP]:8002
AI_BACKEND_URL=http://localhost:8002

# MinIO 外部訪問端點（前端和容器外部訪問）
MINIO_ENDPOINT=localhost:9000
MINIO_EXTERNAL_URL=http://localhost:9000

# MinIO 容器內部訪問端點（只在 Docker 中使用）
MINIO_CONTAINER_ENDPOINT=minio:9000

# 數據庫
DB_HOST=localhost
DB_PORT=9090
DB_NAME=auth_db
DB_USER=auth_user
DB_PASSWORD=auth_password_123
```

### CORS 配置

```env
# 單個來源（推薦生產環境）
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# 允許所有（開發環境快速測試）
CORS_ALLOW_ALL_ORIGINS=True
```

### Django 配置

```env
# 調試模式（開發：False，生產：False）
DEBUG=False

# 允許的主機（域名驗證）
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Django 安全金鑰（生產環境應設置強隨機值）
DJANGO_SECRET_KEY=change-this-secret-key-in-production...
```

### MinIO 配置

```env
# MinIO 認證
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=processed-images
MINIO_SECURE=False  # 本地開發用 HTTP
```

### 文件上傳配置

```env
# 最大上傳大小（10 MB）
MAX_UPLOAD_SIZE=10485760
```

### AI 後端配置

```env
# AI 虛擬試穿端點（相對於 AI_BACKEND_URL）
AI_VIRTUAL_TRY_ON_ENDPOINT=/virtual_try_on/clothes/combine

# 完整 URL = AI_BACKEND_URL + AI_VIRTUAL_TRY_ON_ENDPOINT
# 例：http://localhost:8002 + /virtual_try_on/clothes/combine
```

---

## ⚡ 最小化配置（開發快速啟動）

```env
# 這些是最少需要的配置
DJANGO_SECRET_KEY=dev-key
DEBUG=False

# 關鍵服務地址
FRONTEND_URL=http://localhost:5173
AI_BACKEND_URL=http://localhost:8002
MINIO_ENDPOINT=localhost:9000
DB_HOST=localhost

# 其他自動使用預設值
```

---

## 🚨 重要提醒

### ⚠️ 一定要改的

1. **AI_BACKEND_URL** - 每次切換環境都要檢查
2. **DB_HOST** - 本地 vs Docker，不同的值

### ℹ️ 通常不用改的

- MINIO_BUCKET_NAME
- MINIO_ACCESS_KEY / MINIO_SECRET_KEY
- DB_USER / DB_PASSWORD
- AI_VIRTUAL_TRY_ON_ENDPOINT

### ⚠️ 生產環境必改的

- DEBUG=True → False
- DJANGO_SECRET_KEY=隨機強密鑰
- CORS_ALLOW_ALL_ORIGINS=True → False
- CORS_ALLOWED_ORIGINS=實際前端域名
- FRONTEND_URL=前端實際地址
- 所有 localhost → 實際域名

---

## 🔗 與代碼的對應關係

```
.env 變數              →  settings.py 讀取           →  views.py 使用
─────────────────────────────────────────────────────────────────
FRONTEND_URL           →  settings.FRONTEND_URL        →  CORS 白名單
AI_BACKEND_URL         →  settings.AI_BACKEND_URL      →  combine/views.py
MINIO_ENDPOINT         →  settings.MINIO_ENDPOINT      →  picture/views.py
MINIO_CONTAINER_EP.    →  settings.MINIO_CONTAINER_EP. →  combine/views.py
DB_HOST                →  settings.DATABASES[...]      →  Django ORM
```

---

## 🎯 決策樹

```
我要開發什麼場景？

├─ 單人本地開發
│  └─ AI_BACKEND_URL=http://localhost:8002
│
├─ Docker 本地測試
│  └─ AI_BACKEND_URL=http://172.17.0.1:8002
│     DB_HOST=postgres
│
└─ 與團隊協作
   └─ AI_BACKEND_URL=http://[AI團隊IP]:8002
      FRONTEND_URL=http://[前端團隊IP]:port
      DB_HOST=[共用伺服器]
```

---

更詳細的指南見：[COLLABORATION_GUIDE.md](./COLLABORATION_GUIDE.md)
