# Django 圖片處理 API

這是一個 Django 應用程式，作為前端與 AI 後端之間的中間層，用於處理圖片去背功能，並將處理後的圖片存儲到 MinIO 對象存儲。

## 📋 功能描述

- 接收前端上傳的圖片檔案
- 轉發給 AI 後端進行去背處理
- 將處理後的圖片存儲到 MinIO
- 生成預簽名 URL 供前端下載
- 完整的錯誤處理和日誌記錄

## 🛠️ 技術棧

- **Python 3.11**
- **Django 4.x** - Web 框架
- **Gunicorn** - WSGI HTTP 服務器（生產環境）
- **MinIO** - 對象存儲服務
- **Docker & Docker Compose** - 容器化部署
- **Requests** - HTTP 客戶端

## 📁 專案結構

```
test_project/
├── api/                    # API 應用
│   ├── views.py           # 視圖函數（主要業務邏輯）
│   ├── urls.py            # URL 路由配置
│   └── models.py          # 數據模型
├── config/                 # Django 配置
│   ├── settings.py        # 應用設定
│   ├── urls.py            # 主 URL 路由
│   └── wsgi.py            # WSGI 配置
├── start.sh               # 統一啟動腳本
├── stop.sh                # 統一停止腳本
├── Dockerfile             # Docker 映像配置
├── docker-compose.yml     # Docker Compose 配置
├── requirements.txt       # Python 依賴
├── .env                   # 環境變數配置
├── .env.example           # 環境變數範本
├── ENV_CONFIG.md          # 環境變數配置說明
├── SCRIPT_INTEGRATION.md  # 腳本整合說明
└── README.md              # 專案說明文件
```

## 🚀 快速開始

### 前置要求

- Docker 和 Docker Compose（推薦）
- 或 Python 3.11+（本地開發）

### 方法一：使用 Docker Compose（推薦）

1. **複製環境變數範本**
   ```bash
   cp .env.example .env
   ```

2. **編輯 .env 檔案，設定 AI 後端位址**
   ```bash
   nano .env
   # 修改 AI_BACKEND_URL 為您的 AI 服務位址
   ```

3. **啟動服務**
   ```bash
   chmod +x start.sh
   ./start.sh --docker
   ```

4. **服務將運行在**
   - Django API: http://localhost:30000
   - MinIO 控制台: http://localhost:9001
   - MinIO API: http://localhost:9000

### 方法二：本地開發

1. **複製環境變數範本**
   ```bash
   cp .env.example .env
   nano .env  # 編輯配置
   ```

2. **啟動 MinIO（使用 Docker）**
   ```bash
   docker compose up -d minio
   ```

3. **安裝 Python 依賴**
   ```bash
   pip install -r requirements.txt
   ```

4. **啟動應用**
   ```bash
   chmod +x start.sh
   ./start.sh --local
   ```

### 方法三：自動偵測模式

```bash
./start.sh
```
腳本會自動偵測環境並選擇最適合的啟動方式。

## 📡 API 端點

### GET `/health`

健康檢查端點。

**回應：**
```json
{
  "status": "healthy",
  "message": "服務運行正常"
}
```

### POST `/api/upload-image`

接收前端上傳的圖片並處理。

**請求格式（multipart/form-data）：**
- `image_data`: 圖片檔案
- `filename`: 檔案名稱

**成功回應：**
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
    "filename": "processed_xxx.png",
    "url": "http://localhost:9000/processed-images/...",
    "storage": "minio"
  }
}
```

**錯誤回應：**
```json
{
  "success": false,
  "message": "錯誤訊息",
  "ai_status": {
    "status_code": 422,
    "message": "圖片過於模糊"
  }
}
```

詳細 API 文件請參考：[API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## ⚙️ 環境變數配置

主要環境變數（在 `.env` 中配置）：

```bash
# Django 配置
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key

# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=processed-images

# AI 後端配置
AI_BACKEND_URL=http://your-ai-service:8001/api/remove_bg
```

詳細配置說明請參考：[ENV_CONFIG.md](ENV_CONFIG.md)

## 🎯 啟動腳本說明

### start.sh - 統一啟動腳本

支援三種模式：
- **自動偵測**：`./start.sh`
- **Docker Compose**：`./start.sh --docker`
- **本地開發**：`./start.sh --local`

### stop.sh - 統一停止腳本

支援停止不同模式的服務：
- **停止所有**：`./stop.sh`
- **只停止 Docker**：`./stop.sh --docker`
- **只停止本地**：`./stop.sh --local`

詳細說明請參考：[SCRIPT_INTEGRATION.md](SCRIPT_INTEGRATION.md)

根據你的 Docker 網路配置或 AI 服務地址進行調整。

## 🐳 Docker 指令

```bash
# 構建映像檔
docker build -t test-flask-app .

# 運行容器
docker run -d --name flask-container -p 5000:5000 test-flask-app

# 查看容器日誌
docker logs -f flask-container

# 停止容器
docker stop flask-container

# 刪除容器
docker rm flask-container
```

## 📝 注意事項

1. **網路配置**：確保前端、此中間層、AI 後端三者之間網路互通
2. **CORS 設定**：已啟用 CORS，允許跨域請求
3. **端口配置**：預設使用 5000 端口，可在 `run.sh` 中修改
4. **AI 後端**：需要先啟動 AI 去背服務

## 🔧 常見問題

**Q: 無法連線到 AI 伺服器？**  
A: 檢查 `AI_BACKEND_URL` 是否正確，確認 AI 服務已啟動且網路可達。

**Q: Docker 容器啟動失敗？**  
A: 檢查 5000 端口是否被佔用，使用 `docker logs flask-container` 查看錯誤日誌。

**Q: 圖片處理失敗？**  
A: 確認上傳的 Base64 格式正確，檢查 AI 後端是否正常運作。

## 📄 授權

本專案僅供學習和開發使用。
