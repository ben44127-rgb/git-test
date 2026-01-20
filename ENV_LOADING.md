# .env 檔案載入機制說明

## ✅ 已完成的優化

為了確保所有程式檔案都能正確讀取 `.env` 檔案的變數，已對以下檔案進行優化：

### 1. **manage.py** - Django 管理命令入口
- ✅ 在執行任何 Django 命令前先載入 .env
- ✅ 確保 `python manage.py` 相關命令都能讀取環境變數
- ✅ 添加了明確的 .env 檔案路徑

### 2. **config/settings.py** - Django 設定檔
- ✅ 使用明確的路徑載入 .env 檔案
- ✅ 添加了載入狀態的日誌輸出
- ✅ 支援 Docker 環境中的環境變數

### 3. **config/wsgi.py** - WSGI 應用入口
- ✅ 在 WSGI 應用啟動前載入 .env
- ✅ 確保 Gunicorn 等 WSGI 服務器能讀取環境變數
- ✅ 添加了容錯處理

### 4. **config/asgi.py** - ASGI 應用入口
- ✅ 在 ASGI 應用啟動前載入 .env
- ✅ 支援異步應用的環境變數讀取
- ✅ 添加了容錯處理

### 5. **Dockerfile** - Docker 映像配置
- ✅ 複製 .env 檔案到容器中
- ✅ 支援 Docker 環境變數覆蓋

### 6. **docker-compose.yml** - Docker Compose 配置
- ✅ 使用 `env_file` 載入 .env
- ✅ 支援環境變數優先順序覆蓋

## 🔄 環境變數載入順序

### 本地開發環境
```
1. .env 檔案 → python-dotenv 載入
2. manage.py/wsgi.py 中的 load_dotenv()
3. config/settings.py 讀取 os.getenv()
4. 應用程式使用 settings 中的配置
```

### Docker 環境
```
1. docker-compose.yml 的 env_file
2. docker-compose.yml 的 environment（會覆蓋 .env）
3. 容器中的 .env 檔案
4. manage.py/wsgi.py 中的 load_dotenv()
5. config/settings.py 讀取 os.getenv()
6. 應用程式使用 settings 中的配置
```

## 🎯 環境變數優先順序

從高到低：
1. **Docker Compose environment 區段** - 直接賦值（最高優先）
2. **系統環境變數** - export 設定的變數
3. **Docker Compose env_file** - .env 檔案透過 docker-compose
4. **.env 檔案** - python-dotenv 載入
5. **程式碼預設值** - os.getenv('VAR', 'default')

## 📝 支援的所有環境變數

### Django 配置
- `DEBUG` - 是否啟用除錯模式
- `DJANGO_SECRET_KEY` - Django 安全金鑰

### MinIO 配置
- `MINIO_ENDPOINT` - MinIO 服務位址
- `MINIO_ACCESS_KEY` - MinIO 存取金鑰
- `MINIO_SECRET_KEY` - MinIO 秘密金鑰
- `MINIO_BUCKET_NAME` - 儲存桶名稱
- `MINIO_SECURE` - 是否使用 HTTPS

### AI 後端配置
- `AI_BACKEND_URL` - AI 服務 URL

### 其他配置
- `MAX_UPLOAD_SIZE` - 檔案上傳大小限制
- `CORS_ALLOW_ALL_ORIGINS` - CORS 設定

## 🧪 驗證方法

### 1. 使用檢查腳本
```bash
python3 check_env.py
```

### 2. 手動驗證
```bash
# 本地環境
python3 manage.py shell
>>> from django.conf import settings
>>> print(settings.MINIO_ENDPOINT)
>>> print(settings.AI_BACKEND_URL)
```

```bash
# Docker 環境
docker exec -it django-backend python manage.py shell
>>> from django.conf import settings
>>> print(settings.MINIO_ENDPOINT)
```

### 3. 查看啟動日誌
啟動服務時會看到：
```
✅ 已載入環境變數檔案: /path/to/.env
```

## 🔧 故障排除

### 問題：環境變數未載入

**檢查清單：**
1. ✅ 確認 `.env` 檔案存在於專案根目錄
2. ✅ 確認 `python-dotenv` 已安裝
3. ✅ 確認 `.env` 檔案格式正確（無 BOM、正確的格式）
4. ✅ 檢查啟動日誌是否顯示載入成功

**解決方案：**
```bash
# 重新安裝 python-dotenv
pip install python-dotenv

# 檢查 .env 檔案
cat .env

# 執行驗證腳本
python3 check_env.py
```

### 問題：Docker 環境中變數不正確

**原因：**
Docker Compose 的 `environment` 區段會覆蓋 `.env` 檔案

**解決方案：**
1. 檢查 `docker-compose.yml` 中的 `environment` 設定
2. 確認是否使用了 `${VAR:-default}` 語法
3. 重新建立容器：`docker-compose up --build`

### 問題：某些命令讀不到環境變數

**原因：**
環境變數在命令執行前未載入

**解決方案：**
- 使用 `python3 manage.py` 而不是直接執行 Python 腳本
- 確保從專案根目錄執行命令
- 使用 `./start.sh` 腳本啟動

## 📚 相關檔案

- `.env` - 環境變數配置檔案
- `.env.example` - 環境變數範本
- `check_env.py` - 環境變數檢查腳本
- `ENV_CONFIG.md` - 環境變數詳細說明
- `SCRIPT_INTEGRATION.md` - 啟動腳本說明

## 🎓 最佳實踐

1. **開發環境**：使用 `.env` 檔案存放配置
2. **生產環境**：使用系統環境變數或 Docker secrets
3. **敏感資訊**：永遠不要將 `.env` 提交到版本控制
4. **預設值**：在程式碼中提供合理的預設值
5. **驗證**：定期執行 `check_env.py` 驗證配置

## ✨ 總結

現在所有程式檔案都能正確讀取 `.env` 檔案的變數：

✅ **Django 管理命令** - manage.py
✅ **WSGI 應用** - Gunicorn/uWSGI
✅ **ASGI 應用** - Daphne/Uvicorn  
✅ **Django Settings** - 配置模組
✅ **Docker 環境** - 容器中的應用
✅ **本地開發** - 直接執行的應用

所有入口點都已優化，確保環境變數在應用啟動的最早期就被載入！
