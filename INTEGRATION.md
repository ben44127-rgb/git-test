# 系統整合說明

本文檔說明如何將用戶認證系統整合到 test_project 中。

## 整合概述

已成功將獨立的認證系統整合到 test_project，實現了以下整合：

### ✅ 已完成的整合

1. **應用整合**
   - ✅ 複製 `accounts` 應用到 test_project
   - ✅ 在 `settings.py` 中添加 `accounts` 和 `rest_framework` 到 `INSTALLED_APPS`
   - ✅ 在主 `urls.py` 中添加認證路由 `/api/auth/`

2. **數據庫整合**
   - ✅ 將 SQLite 更改為 PostgreSQL
   - ✅ 配置數據庫連接參數
   - ✅ 在 docker-compose.yml 中添加 PostgreSQL 服務
   - ✅ 配置端口映射（9090:5432）

3. **Docker 配置整合**
   - ✅ 添加 PostgreSQL 服務到 docker-compose.yml
   - ✅ 配置服務依賴關係
   - ✅ 添加健康檢查
   - ✅ 配置數據卷持久化

4. **環境變數整合**
   - ✅ 在 `.env` 中添加數據庫配置
   - ✅ 在 `.env.example` 中添加配置示例
   - ✅ 更新 Docker 環境變數傳遞

5. **依賴整合**
   - ✅ 添加 `djangorestframework` 到 requirements.txt
   - ✅ 添加 `psycopg2-binary` 到 requirements.txt

6. **文檔整合**
   - ✅ 創建 AUTH_SYSTEM.md 詳細說明
   - ✅ 更新主 README.md
   - ✅ 創建測試腳本 test_auth.sh

## 文件變更清單

### 新增文件
```
test_project/
├── accounts/              # 新增：認證應用
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── AUTH_SYSTEM.md         # 新增：認證系統文檔
└── test_auth.sh           # 新增：認證測試腳本
```

### 修改文件
```
test_project/
├── config/
│   ├── settings.py        # 修改：添加認證配置
│   └── urls.py            # 修改：添加認證路由
├── docker-compose.yml     # 修改：添加 PostgreSQL
├── requirements.txt       # 修改：添加依賴
├── .env                   # 修改：添加數據庫配置
├── .env.example           # 修改：添加配置示例
└── README.md              # 修改：更新說明
```

## 服務架構

### 整合前
```
┌─────────────────┐
│   Django App    │  Port 30000
├─────────────────┤
│      MinIO      │  Port 9000/9001
└─────────────────┘
```

### 整合後
```
┌─────────────────┐
│   Django App    │  Port 30000
│  - api          │  (圖片處理)
│  - accounts     │  (用戶認證)
├─────────────────┤
│   PostgreSQL    │  Port 9090
│  (用戶數據)     │
├─────────────────┤
│      MinIO      │  Port 9000/9001
│  (圖片存儲)     │
└─────────────────┘
```

## API 端點映射

### 整合前（auth_system 獨立運行）
- `http://localhost:30001/api/auth/register/`
- `http://localhost:30001/api/auth/login/`
- `http://localhost:30001/api/auth/logout/`
- `http://localhost:30001/api/auth/delete/`
- `http://localhost:30001/api/auth/check/`

### 整合後（test_project）
- `http://localhost:30000/api/auth/register/`
- `http://localhost:30000/api/auth/login/`
- `http://localhost:30000/api/auth/logout/`
- `http://localhost:30000/api/auth/delete/`
- `http://localhost:30000/api/auth/check/`

**變更**: 端口從 30001 改為 30000

## 配置文件變更詳情

### 1. config/settings.py

#### INSTALLED_APPS
```python
INSTALLED_APPS = [
    # ... 原有應用 ...
    'rest_framework',    # 新增
    'api',
    'accounts',          # 新增
]
```

#### DATABASES
```python
# 從 SQLite 改為 PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # 修改
        'NAME': os.getenv('DB_NAME', 'auth_db'),
        'USER': os.getenv('DB_USER', 'auth_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'auth_password_123'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '9090'),
    }
}
```

#### REST Framework 配置（新增）
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### 2. config/urls.py

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
    path('api/auth/', include('accounts.urls')),  # 新增
]
```

### 3. docker-compose.yml

新增 PostgreSQL 服務：
```yaml
services:
  db:
    image: postgres:15
    container_name: auth_postgres
    environment:
      POSTGRES_DB: ${DB_NAME:-auth_db}
      POSTGRES_USER: ${DB_USER:-auth_user}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-auth_password_123}
    ports:
      - "9090:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U auth_user -d auth_db"]
      interval: 10s
      timeout: 5s
      retries: 5
```

更新 backend 服務依賴：
```yaml
backend:
  # ...
  environment:
    # ... 原有配置 ...
    DB_NAME: ${DB_NAME:-auth_db}
    DB_USER: ${DB_USER:-auth_user}
    DB_PASSWORD: ${DB_PASSWORD:-auth_password_123}
    DB_HOST: db
    DB_PORT: 5432
  depends_on:
    minio:
      condition: service_started
    db:
      condition: service_healthy  # 新增
```

新增數據卷：
```yaml
volumes:
  minio_data:
    driver: local
  postgres_data:        # 新增
    driver: local
```

### 4. requirements.txt

```txt
Django==5.1.5
django-cors-headers==4.6.0
djangorestframework==3.14.0    # 新增
psycopg2-binary==2.9.9         # 新增
requests==2.32.3
minio==7.2.20
python-dotenv==1.0.0
gunicorn==23.0.0
```

### 5. .env

```env
# ... 原有配置 ...

# 新增數據庫配置
DB_NAME=auth_db
DB_USER=auth_user
DB_PASSWORD=auth_password_123
DB_HOST=localhost
DB_PORT=9090
```

## 啟動順序

### Docker Compose 模式
```bash
cd /home/ben/test_project

# 1. 啟動所有服務
docker-compose up -d --build

# 2. 檢查服務狀態
docker-compose ps

# 3. 查看日誌
docker-compose logs -f backend

# 4. 等待數據庫初始化完成
# Django 會自動執行 migrations
```

### 驗證整合

1. **檢查服務狀態**
```bash
docker-compose ps
# 應該看到：minio, db, backend 三個服務都在運行
```

2. **檢查數據庫連接**
```bash
docker exec -it auth_postgres psql -U auth_user -d auth_db
# 應該能夠連接到數據庫
```

3. **測試認證 API**
```bash
./test_auth.sh
# 應該看到註冊、登入、登出測試都通過
```

4. **測試圖片處理 API**
```bash
# 按照原有的測試流程測試圖片處理功能
```

## 遷移指南

如果您有現有的 auth_system 數據需要遷移：

### 1. 導出現有數據
```bash
cd /home/ben/auth_system
docker exec auth_postgres pg_dump -U auth_user auth_db > backup.sql
```

### 2. 導入到新系統
```bash
cd /home/ben/test_project
docker exec -i auth_postgres psql -U auth_user -d auth_db < /path/to/backup.sql
```

## 清理舊系統

整合完成後，可以選擇刪除獨立的 auth_system：

```bash
# 停止並刪除舊的認證系統
cd /home/ben/auth_system
docker-compose down -v

# 刪除目錄（可選）
# cd /home/ben
# rm -rf auth_system
```

## 故障排除

### 1. 數據庫連接失敗

**症狀**: Django 無法連接到 PostgreSQL

**解決方案**:
```bash
# 檢查數據庫容器狀態
docker-compose ps

# 查看數據庫日誌
docker-compose logs db

# 驗證數據庫配置
docker exec -it auth_postgres psql -U auth_user -d auth_db
```

### 2. 認證 API 404 錯誤

**症狀**: 訪問 `/api/auth/` 返回 404

**解決方案**:
- 檢查 `config/urls.py` 是否包含認證路由
- 檢查 `settings.py` 中 `accounts` 是否在 `INSTALLED_APPS` 中
- 重啟 Django 服務

### 3. Migration 錯誤

**症狀**: 啟動時出現數據庫遷移錯誤

**解決方案**:
```bash
# 進入容器執行遷移
docker exec -it django-backend python manage.py makemigrations
docker exec -it django-backend python manage.py migrate
```

### 4. 端口衝突

**症狀**: PostgreSQL 端口 9090 已被占用

**解決方案**:
- 修改 `docker-compose.yml` 中的端口映射
- 同時修改 `.env` 中的 `DB_PORT`

## 測試清單

- [ ] PostgreSQL 容器正常啟動
- [ ] Django 容器正常啟動並連接數據庫
- [ ] 用戶註冊功能正常
- [ ] 用戶登入功能正常
- [ ] 用戶登出功能正常
- [ ] 刪除用戶功能正常
- [ ] 檢查登入狀態功能正常
- [ ] 圖片處理功能仍然正常（未受影響）
- [ ] MinIO 存儲功能仍然正常（未受影響）

## 後續優化建議

1. **安全性增強**
   - 修改預設數據庫密碼
   - 配置 HTTPS
   - 實現 JWT Token 認證（可選）

2. **功能擴展**
   - 添加密碼重置功能
   - 添加郵箱驗證
   - 實現用戶權限管理

3. **性能優化**
   - 配置 Redis 緩存
   - 優化數據庫查詢
   - 實現連接池

4. **監控和日誌**
   - 添加認證相關的日誌記錄
   - 監控數據庫連接狀態
   - 實現審計日誌

## 相關文檔

- [README.md](README.md) - 項目總體說明
- [AUTH_SYSTEM.md](AUTH_SYSTEM.md) - 認證系統詳細文檔
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API 文檔
- [ENV_CONFIG.md](ENV_CONFIG.md) - 環境配置說明
