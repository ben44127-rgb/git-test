# 🚀 三人協作快速參考卡

## 💡 核心記住這 3 點

```
✅ 環境變數統一在 .env
✅ AI 後端只改 1 個變數：AI_BACKEND_URL
✅ 改完 .env 後重啟 Django
```

---

## 🎯 三種場景一句話配置

### 1️⃣ 本地開發（最簡單）

```bash
# .env 中：
AI_BACKEND_URL=http://localhost:8002
DB_HOST=localhost

# 啟動：
python test_file/mock_ai_backend.py --port 8002 &
python manage.py runserver
```

### 2️⃣ Docker 本地（改 2 行）

```bash
# .env 中：
AI_BACKEND_URL=http://172.17.0.1:8002
DB_HOST=postgres

# 啟動：
docker-compose up
```

### 3️⃣ 與 AI 團隊（改 1 行）

```bash
# .env 中：
AI_BACKEND_URL=http://192.168.1.50:8002  # ← 只改這行

# 啟動：
python manage.py runserver
```

---

## ⚡ 最常用命令

```bash
# 驗證所有連接
python verify_connections.py

# 重新啟動後端
python manage.py runserver 0.0.0.0:30000

# 測試 AI 後端
curl http://localhost:8002/health

# 測試 MinIO
curl http://localhost:9001

# 查看 .env 中的 AI 配置
grep "AI_BACKEND_URL" .env
```

---

## 🔍 快速故障排除

| 問題 | 解決 |
|------|------|
| AI 連接失敗 | `curl http://[AI_URL]/health` |
| 圖片上傳失敗 | `docker-compose logs minio` |
| 前端 CORS 錯誤 | 檢查 `CORS_ALLOWED_ORIGINS` |
| Docker MinIO 連接失敗 | 用 `MINIO_CONTAINER_ENDPOINT=minio:9000` |

---

## 📋 環境變量速查表

```env
# 【前端】
FRONTEND_URL                # 前端地址（CORS白名單）
CORS_ALLOWED_ORIGINS       # CORS允許的來源列表

# 【AI後端】⭐ 最重要
AI_BACKEND_URL             # 單一變數，根據環境改
  → http://localhost:8002         # 本地
  → http://172.17.0.1:8002        # Docker
  → http://[IP]:8002              # 真實 AI

# 【數據庫】
DB_HOST                    # localhost 或 postgres

# 【MinIO】
MINIO_ENDPOINT             # localhost:9000
MINIO_CONTAINER_ENDPOINT   # minio:9000（僅Docker）
```

---

## 🎓 什麼時候改什麼

### 早上啟動前

```bash
grep "DB_HOST\|AI_BACKEND_URL" .env  # 確認配置正確
python verify_connections.py          # 驗證連接
```

### 與團隊同步後

```bash
git pull
grep "AI_BACKEND_URL" .env  # 檢查是否有變更
python manage.py runserver  # 重啟
```

### 要切換 AI 後端時

```bash
# 1. 編輯 .env
nano .env
# 改：AI_BACKEND_URL=新地址

# 2. 重啟 Django
python manage.py runserver

# 3. 驗證
python verify_connections.py
```

---

## 📚 一鍵導航

| 需求 | 看這個文檔 |
|------|----------|
| 詳細配置說明 | [COLLABORATION_GUIDE.md](./docs/COLLABORATION_GUIDE.md) |
| 環境變量詳解 | [ENV_REFERENCE.md](./docs/ENV_REFERENCE.md) |
| 改動總結 | [CONFIG_SUMMARY.md](./CONFIG_SUMMARY.md) |
| API 文檔 | [FUNCTIONS.md](./docs/FUNCTIONS.md) |

---

## 🎉 大功告成

```
✅ .env 配置完整（6 個區塊）
✅ AI 後端簡化為 1 個變數
✅ 支持 3 種部署方式
✅ 連接驗證工具已就緒
✅ 文檔齊全（3 份）

→ 可以開始開發了！🚀
```

---

## 💬 常見問題 1 分鐘速答

**Q: 怎麼連 AI 團隊的後端?**
A: 改 `.env` 的 `AI_BACKEND_URL=http://[AI_IP]:8002`，重啟 Django

**Q: Docker 裡圖片上傳失敗?**
A: 設置 `MINIO_CONTAINER_ENDPOINT=minio:9000`

**Q: 前端無法訪問?**
A: 檢查 `CORS_ALLOWED_ORIGINS` 白名單

**Q: 容器連接不到本機 AI?**
A: 用 `AI_BACKEND_URL=http://172.17.0.1:8002`

---

**最後一個貼士：** 把這個文件夾加到書籤，經常回來查看 📌
