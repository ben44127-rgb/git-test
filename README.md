# Flask 圖片處理 API

這是一個 Flask 應用程式，作為前端與 AI 後端之間的中間層，用於處理圖片去背功能。

## 📋 功能描述

- 接收前端上傳的 Base64 格式圖片
- 解碼並轉換圖片格式
- 轉發給 AI 後端進行去背處理
- 回傳處理後的結果給前端

## 🛠️ 技術棧

- **Python 3.9**
- **Flask** - Web 框架
- **Flask-CORS** - 處理跨域請求
- **Requests** - HTTP 客戶端
- **Docker** - 容器化部署

## 📁 專案結構

```
test_project/
├── app.py              # Flask 主應用程式
├── dockerfile          # Docker 映像檔配置
├── requirements.txt    # Python 依賴套件
├── run.sh             # 快速部署腳本
└── README.md          # 專案說明文件
```

## 🚀 快速開始

### 方法一：使用 Docker（推薦）

1. **確保已安裝 Docker**
   ```bash
   docker --version
   ```

2. **執行部署腳本**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

3. **應用將運行在**
   ```
   http://localhost:5000
   ```

### 方法二：本地開發

1. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

2. **運行應用**
   ```bash
   python app.py
   ```

## 📡 API 端點

### POST `/api/upload-image`

接收前端上傳的圖片並轉發給 AI 後端處理。

**請求格式：**
```json
{
  "image_data": "base64編碼的圖片資料",
  "filename": "photo.png"
}
```

**成功回應：**
```json
{
  "message": "去背成功",
  "processed_url": "http://你的IP:5000/download/processed_photo.png",
  "original_filename": "photo.png"
}
```

**錯誤回應：**
```json
{
  "error": "錯誤訊息"
}
```

## ⚙️ 配置說明

在 `app.py` 中修改 AI 後端地址：

```python
AI_BACKEND_URL = "http://172.17.0.3:5000/api/remove_bg"
```

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
