# test_project - AI 虛擬試衣系統

> 最後更新：2026-03-23  
> [📚 完整文檔導航](INDEX.md) | [🔌 API 文檔](API.md) | [🎯 功能清單](FUNCTIONS.md) | [🏗️ 系統架構](Architecture.md)

## 📖 是什麼？

一個 **AI 驅動的虛擬試衣系統**，提供：
- ✅ 完整的用戶認證系統 (註冊/登入/登出/刪除賬號)
- ✅ 智能圖片去背處理 (AI + Gemini)
- ✅ 衣伺管理與穿搭組合
- ✅ 用戶數據管理 (身體測量數據)
- 🔄 AI 穿搭諮詢對話

**功能完成度**: 6/15 (40%) ✅

## 🛠️ 技術棧

| 層級 | 技術 |
|------|------|
| **Backend** | Django 5.1.5 + DRF 3.14.0 |
| **認證** | JWT (djangorestframework-simplejwt) |
| **數據庫** | PostgreSQL 15 |
| **存儲** | MinIO (S3 兼容) |
| **AI** | Gemini API |
| **容器** | Docker & Docker Compose |

## 🚀 快速開始 (5 分鐘)

### 前置要求
- ✅ Docker & Docker Compose
- ✅ Git

### 步驟 1: 克隆專案
```bash
git clone <your-repo>
cd test_project
```

### 步驟 2: 設定環境
```bash
cp .env.example .env
# 編輯 .env，設定 AI_BACKEND_URL（如需要）
nano .env
```

### 步驟 3: 啟動伺務
```bash
chmod +x start.sh
./start.sh
```

### 步驟 4: 驗證伺務
```bash
# 檢查所有伺務是否運行
docker-compose ps

# 測試 API
curl -X POST http://localhost:30000/account/user/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

## 🌐 伺務端口

| 伺務 | 地址 | 用途 |
|------|------|------|
| **Django API** | http://localhost:30000 | 核心後端 |
| **MinIO 控制台** | http://localhost:9001 | 檔案管理 |
| **PostgreSQL** | localhost:9090 | 數據庫 |
| **MinIO API** | localhost:9000 | 對象存儲 |

## 📁 專案結構 (簡化版)

```
test_project/
├── accounts/              # 👤 用戶認證
├── picture/               # 📸 圖片和穿搭
├── config/                # ⚙️ Django 設定
├── Docs/                  # 📚 文檔
│   ├── INDEX.md          # 📖 文檔導航中心 ⭐
│   ├── API.md            # 🔌 API 詳細文檔
│   ├── FUNCTIONS.md      # 🎯 功能清單
│   ├── Architecture.md   # 🏗️ 系統架構
│   └── api.xlsx          # 📊 API 快速參考
├── start.sh              # 🚀 啟動腳本
├── stop.sh               # ⛔ 停止腳本
├── docker-compose.yml    # 🐳 Docker 設定
├── Dockerfile            # 📦 Django 鏡像
└── requirements.txt      # 📋 Python 依賴
```

## 📚 完整文檔

| 文檔 | 用途 | 閱讀時間 |
|------|------|---------|
| **[INDEX.md](INDEX.md)** | 📖 文檔導航中心 (從這開始!) | 5 分鐘 |
| **[GUIDE.md](GUIDE.md)** ⭐ NEW | 👥 根據角色選擇文檔 | 5 分鐘 |
| [README.md](README.md) | 🚀 快速開始 (你在這裡) | 5 分鐘 |
| [API_CHEATSHEET.md](API_CHEATSHEET.md) ⭐ NEW | ⚡ 5 分鐘 API 快速參考 | 5 分鐘 |
| [FUNCTIONS.md](FUNCTIONS.md) | 🎯 功能清單和設計 | 20 分鐘 |
| [API.md](API.md) | 🔌 API 端點詳細文檔 | 30 分鐘 |
| [Architecture.md](Architecture.md) | 🏗️ 系統設計和架構 | 25 分鐘 |
| [api.xlsx](api.xlsx) | 📊 API 快速參考表 | 5 分鐘 |

**✨ 新手推薦：先讀 GUIDE.md (根據角色選擇)，然後讀 API_CHEATSHEET.md！**

## 🔗 常用命令

```bash
# 查看所有伺務狀态
docker-compose ps

# 查看日志
docker-compose logs -f django-backend

# 進入 Django Shell
docker-compose exec django-backend python manage.py shell

# 運行迁移
docker-compose exec django-backend python manage.py migrate

# 停止所有伺務
./stop.sh
# 或
docker-compose down
```

## 📝 第一個 API 調用

### 1. 用戶注册
```bash
curl -X POST http://localhost:30000/account/user/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

**回應示例：**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "date_joined": "2026-03-23T12:00:00Z"
}
```

### 2. 用戶登入
```bash
curl -X POST http://localhost:30000/account/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

**回應示例：**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

### 3. 上傳衣伺图片
```bash
curl -X POST http://localhost:30000/picture/clothes/upload_image \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "image_data=@/path/to/image.jpg" \
  -F "filename=clothes.jpg"
```

**更多 API 調用示例詳見 ➞ [API.md](API.md)**

## 📖 文档導航

| 文档 | 內容 | 最佳用戶 |
|------|------|---------|
| **[INDEX.md](INDEX.md)** ⭐ | 📖 文档導航中心 | 所有人 |
| **[FUNCTIONS.md](FUNCTIONS.md)** | 🎯 功能清单詳解 | 產品/開發 |
| **[API.md](API.md)** | 🔌 API 端点文档 | 前後端開發 |
| **[Architecture.md](Architecture.md)** | 🏗️ 系統架构設計 | 架构师/高级開發 |
| **[api.xlsx](api.xlsx)** | 📊 API 快速参考 | API 使用者 |

## 🐛 常見問題

### Q1: 伺務無法啟動
```bash
# 檢查端口占用
lsof -i :30000
lsof -i :9090

# 查看詳細错误
docker-compose logs django-backend
```

### Q2: JWT Token 無效
```
确保在請求头中正确傳递:
Authorization: Bearer <access_token>
```

### Q3: MinIO 連接失败
```
檢查 MINIO_ENDPOINT 和認證信息是否正确
# 訪問 MinIO 控制台
http://localhost:9001 (用戶: minioadmin, 密碼: minioadmin)
```

### Q4: 資料庫連接失败
```
檢查 .env 中的資料庫設定:
DB_HOST=db
DB_PORT=5432
DB_NAME=django_db
DB_USER=postgres
DB_PASSWORD=postgres
```

## 🤝 需要幫助？

- 📚 查看完整文档：[INDEX.md](INDEX.md)
- 🔌 API 問題：[API.md](API.md)
- 🎯 功能問題：[FUNCTIONS.md](FUNCTIONS.md)
- 🏗️ 架构問題：[Architecture.md](Architecture.md)

---

**✨ 下一步：** 打開 [INDEX.md](INDEX.md) 獲取完整的文档導航！

