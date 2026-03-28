# 🎯 三人協作系統配置完成總結

## ✅ 已完成的改動

### 1️⃣ `.env` 環境配置（完全重構）

**變更內容：**
- ✅ 添加前端配置：`FRONTEND_URL`
- ✅ 簡化 AI 後端：單一 `AI_BACKEND_URL` 變數（用戶手動切換）
- ✅ 分離 MinIO 端點：`MINIO_ENDPOINT` + `MINIO_CONTAINER_ENDPOINT`
- ✅ 完整的 CORS 配置：`CORS_ALLOWED_ORIGINS`
- ✅ Django 主機配置：`DJANGO_ALLOWED_HOSTS`
- ✅ 新增 AI 虛擬試穿端點：`AI_VIRTUAL_TRY_ON_ENDPOINT`
- ✅ 組織配置結構：區分開發、Docker、協作三種場景

**新配置清單：**
```env
# 【1】Django 應用
DEBUG, DJANGO_SECRET_KEY, DJANGO_DEV_MODE, DJANGO_ALLOWED_HOSTS

# 【2】PostgreSQL 數據庫
DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# 【3】MinIO 物件儲存
MINIO_ENDPOINT, MINIO_CONTAINER_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
MINIO_BUCKET_NAME, MINIO_SECURE, MINIO_EXTERNAL_URL

# 【4】前端配置
FRONTEND_URL, CORS_ALLOWED_ORIGINS, CORS_ALLOW_ALL_ORIGINS

# 【5】AI 後端（核心改進）
AI_BACKEND_URL          # ⭐ 單一變數，用戶手動切換
AI_VIRTUAL_TRY_ON_ENDPOINT

# 【6】檔案上傳
MAX_UPLOAD_SIZE
```

---

### 2️⃣ `config/settings.py` （簡化配置邏輯）

**改動：**
- ✅ 添加 `FRONTEND_URL` 讀取
- ✅ 改進 CORS 配置邏輯：支持環境變數控制
- ✅ 簡化 Django ALLOWED_HOSTS：支持環境變數擴展
- ✅ 添加 `MINIO_CONTAINER_ENDPOINT`
- ✅ **重構 AI 後端配置**：移除 `AI_ADAPTER_MODE` 邏輯，使用單一 `AI_BACKEND_URL`
- ✅ 自動組合虛擬試穿完整 URL

**核心改進（AI 後端）：**
```python
# 之前（複雜）：
# AI_ADAPTER_MODE = 'mock' or 'production'
# if mode == 'mock': AI_BACKEND_BASE_URL = ...
# ...

# 之後（簡單）：
AI_BACKEND_URL = os.getenv('AI_BACKEND_URL', 'http://localhost:8002')
AI_VIRTUAL_TRY_ON_ENDPOINT = os.getenv('AI_VIRTUAL_TRY_ON_ENDPOINT', '...')
AI_BACKEND_VIRTUAL_TRY_ON_URL = AI_BACKEND_URL + AI_VIRTUAL_TRY_ON_ENDPOINT
```

---

### 3️⃣ `combine/views.py` （簡化 AI 連接）

**改動：**
- ✅ 移除硬編碼的預設 AI URL
- ✅ 使用 `settings.AI_BACKEND_VIRTUAL_TRY_ON_URL`
- ✅ 添加備用 `settings.AI_BACKEND_URL`

---

### 4️⃣ 新增文檔和工具

| 檔案 | 說明 |
|------|------|
| **docs/COLLABORATION_GUIDE.md** | 📚 三人協作完整指南（最重要） |
| **docs/ENV_REFERENCE.md** | 📋 環境變量快速參考 |
| **verify_connections.py** | 🔍 連接驗證腳本 |

---

## 🎯 三種場景快速配置

### 場景 1️⃣：本地開發（各自獨立）

```env
FRONTEND_URL=http://localhost:5173
AI_BACKEND_URL=http://localhost:8002
MINIO_ENDPOINT=localhost:9000
DB_HOST=localhost
```

**啟動：**
```bash
# Terminal 1
python test_file/mock_ai_backend.py --port 8002

# Terminal 2
python manage.py runserver 0.0.0.0:30000

# Terminal 3（前端）
npm run dev
```

---

### 場景 2️⃣：Docker 本地集成

```env
FRONTEND_URL=http://localhost:5173
AI_BACKEND_URL=http://172.17.0.1:8002           # ← 改這行
MINIO_CONTAINER_ENDPOINT=minio:9000             # ← 添加此行
DB_HOST=postgres                                 # ← 改這行
```

**啟動：**
```bash
docker-compose up
npm run dev
```

---

### 場景 3️⃣：與 AI 團隊協作

```env
FRONTEND_URL=http://[前端IP]:[端口]
AI_BACKEND_URL=http://[AI團隊IP]:8002           # ← 手動切換
MINIO_ENDPOINT=[MinIO服務器IP]:9000
DB_HOST=[共用數據庫IP]
```

**特點：**
- ✅ 只需改 **1 個變數** → `AI_BACKEND_URL`
- ✅ 無需改動代碼
- ✅ 自動適應不同的後端地址

---

## 🔍 驗證配置正確性

### 方式 1️⃣：運行驗證腳本

```bash
python verify_connections.py

# 輸出：
# ✅ Django         設置加載成功
# ✅ Frontend URL   配置正確
# ✅ CORS           白名單配置
# ✅ PostgreSQL     連接成功
# ✅ MinIO          連接成功
# ✅ AI Backend     連接成功（如果已啟動）
```

### 方式 2️⃣：手動驗證

```bash
# 驗證配置讀取
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings
print('Frontend:', settings.FRONTEND_URL)
print('AI Backend:', settings.AI_BACKEND_URL)
print('MinIO:', settings.MINIO_ENDPOINT)
"

# 驗證 AI 後端
curl http://localhost:8002/health

# 驗證 MinIO
curl http://localhost:9001  # 進入 console
```

---

## 📋 配置檢查清單

### 🟢 必須設置

- [ ] `FRONTEND_URL` - 前端應用地址
- [ ] `AI_BACKEND_URL` - AI 後端地址（每次環境變更時檢查）
- [ ] `DB_HOST` - 數據庫地址
- [ ] `MINIO_ENDPOINT` - MinIO 地址

### 🟡 根據環境設置

- [ ] `DB_HOST` - 本地：`localhost`，Docker：`postgres`
- [ ] `MINIO_CONTAINER_ENDPOINT` - 僅在 Docker 中設置為 `minio:9000`
- [ ] `DJANGO_ALLOWED_HOSTS` - 添加實際的域名

### 🔵 通常無需改動

- [ ] `MINIO_ACCESS_KEY / SECRET_KEY`
- [ ] `AI_VIRTUAL_TRY_ON_ENDPOINT`
- [ ] `DJANGO_SECRET_KEY`（除非將代碼部署到生產）

---

## 🚀 日常開發流程

```bash
# 1️⃣ 早上開啟
docker-compose up postgres minio
sleep 2
python test_file/mock_ai_backend.py --port 8002 &
python manage.py runserver &

# 2️⃣ 驗證連接
python verify_connections.py

# 3️⃣ 開始開發
# ... 編寫代碼 ...

# 4️⃣ 與組員同步
git pull
# 檢查 .env 是否有變更
grep "AI_BACKEND_URL" .env

# 5️⃣ 下班關閉
killall python
docker-compose down
```

---

## 🔄 切換 AI 後端示例

### 本地模擬 → AI 團隊（真實）

```bash
# 1. 檢查 AI 團隊的設置文檔
# （AI 團隊：請告訴我們 AI 後端 IP 和端口）

# 2. 更新 .env
# AI_BACKEND_URL=http://localhost:8002
#               ↓ 改成 ↓
# AI_BACKEND_URL=http://192.168.1.50:8002

# 3. 驗證連接
curl http://192.168.1.50:8002/health

# 4. 重啟後端
python manage.py runserver 0.0.0.0:30000

# 5. 運行驗證
python verify_connections.py
```

---

## 📚 相關文檔

按推薦閱讀順序：

1. **[COLLABORATION_GUIDE.md](./docs/COLLABORATION_GUIDE.md)** ⭐ 最重要
   - 三種環境詳細配置
   - 快速切換指南
   - 故障排除
   
2. **[ENV_REFERENCE.md](./docs/ENV_REFERENCE.md)**
   - 環境變量完整說明
   - 決策樹
   
3. **[FUNCTIONS.md](./docs/FUNCTIONS.md)**
   - API 端點文檔
   - 數據格式說明

4. **此文件** - 當前文件（總結）

---

## 🎯 核心改進點

| 項目 | 之前 | 之後 |
|------|------|------|
| AI 後端配置 | 複雜的 `AI_ADAPTER_MODE` | 簡單的單一變數 |
| 硬編碼 URL | 多處硬編碼 | 全部環境變數 |
| 前端支持 | 無 | 完整的 CORS + URL 配置 |
| Docker 支持 | 需要手動處理 | `MINIO_CONTAINER_ENDPOINT` 自動適應 |
| 協作支持 | 困難（需要改代碼） | 簡單（只改 `.env`） |
| 驗證工具 | 無 | `verify_connections.py` |

---

## ✨ 使用心得

### 代碼改動最少化 ✅

- ❌ 之前需要修改 `settings.py` 邏輯
- ✅ 現在只需修改 `.env`

### 三人協作更便利 ✅

- 前端團隊看 `FRONTEND_URL`
- AI 團隊看 `AI_BACKEND_URL`
- 你的後端看其他配置
- 彼此不干擾

### 環境切換自動化 ✅

- 本地 → Docker：修改 2 個變數
- 本地 → 真實 AI：修改 1 個變數
- Docker → 生產：修改 4 個變數

---

## 📞 快速問題解答

**Q：AI 後端切換不了怎麼辦？**
A：
1. 檢查 `.env` 中的 `AI_BACKEND_URL`
2. 重啟 Django：`python manage.py runserver`
3. 運行驗證：`python verify_connections.py`

**Q：為什麼容器內 MinIO 連接失敗？**
A：
1. 檢查 `MINIO_CONTAINER_ENDPOINT` 是否設置
2. 確認 MinIO 容器名稱是否為 `minio`
3. 在 Docker 網絡中用容器名訪問

**Q：前端無法訪問後端？**
A：
1. 檢查 `CORS_ALLOWED_ORIGINS` 配置
2. 確認前端地址在白名單中
3. 改用 `CORS_ALLOW_ALL_ORIGINS=True`（開發環境臨時用）

**Q：如何快速切換到 AI 團隊的後端？**
A：
```bash
# 只需改這一行
AI_BACKEND_URL=http://[AI團隊IP]:8002
# 然后重启Django
python manage.py runserver 0.0.0.0:30000
```

---

## 🎉 大功告成！

所有配置已準備就緒。你現在可以：

✅ 獨立開發和測試
✅ 快速切換 AI 後端
✅ 與前端和 AI 團隊無縫協作
✅ 通過環境變量靈活適應不同環境

祝開發順利！🚀
