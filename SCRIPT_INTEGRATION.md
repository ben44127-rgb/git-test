# 啟動腳本整合說明

## 📝 更新內容

已將 `docker-start.sh` 和 `start.sh` 整合為單一的 **統一啟動腳本** `start.sh`，同時也整合了停止腳本。

### 刪除的檔案
- ❌ `docker-start.sh` - 已整合到 `start.sh`
- ❌ `docker-stop.sh` - 已整合到 `stop.sh`

### 保留的檔案
- ✅ `start.sh` - 統一啟動腳本（支援多種模式）
- ✅ `stop.sh` - 統一停止腳本（支援多種模式）

## 🚀 使用方式

### 啟動服務

#### 1. 自動偵測模式（推薦）
```bash
./start.sh
```
腳本會自動偵測環境：
- 在 Docker 容器內 → 使用 Gunicorn 啟動
- 宿主機有 Docker → 使用 Docker Compose 啟動
- 宿主機無 Docker → 使用 Django 開發伺服器啟動

#### 2. 強制使用 Docker Compose
```bash
./start.sh --docker
```

#### 3. 強制使用本地開發模式
```bash
./start.sh --local
```

#### 4. 顯示幫助
```bash
./start.sh --help
```

### 停止服務

#### 1. 停止所有服務（推薦）
```bash
./stop.sh
```
會自動停止所有正在運行的服務（Docker 和本地）

#### 2. 只停止 Docker 服務
```bash
./stop.sh --docker
```

#### 3. 只停止本地開發服務
```bash
./stop.sh --local
```

#### 4. 顯示幫助
```bash
./stop.sh --help
```

## 🔧 環境偵測邏輯

### start.sh 偵測流程
```
檢查 /.dockerenv
    ↓ 是
    使用容器模式（Gunicorn）
    ↓ 否
檢查 docker 命令可用
    ↓ 是
    使用 Docker Compose 模式
    ↓ 否
    使用本地開發模式
```

### stop.sh 行為
- 預設模式：停止所有服務
- `--docker`：只停止 Docker Compose 服務
- `--local`：只停止本地 Python 進程

## 📋 各模式功能對照

| 功能 | 容器模式 | Docker Compose | 本地開發 |
|------|---------|----------------|----------|
| 自動啟動 | ✅ | ✅ | ✅ |
| 數據庫遷移 | ✅ | ✅ | ✅ |
| 等待 MinIO | ✅ | ✅ | ⚠️ 檢查但不等待 |
| 健康檢查 | ✅ | ✅ | ✅ |
| 日誌輸出 | Gunicorn | Docker logs | app.log |
| 適用環境 | 生產 | 開發/生產 | 僅開發 |

## 💡 使用場景

### 開發環境
```bash
# 方式 1: 使用 Docker Compose（推薦）
./start.sh --docker

# 方式 2: 純本地開發
./start.sh --local
```

### 生產環境
```bash
# 使用 Docker Compose
docker compose up -d
# 或
./start.sh --docker
```

### CI/CD 環境
```bash
# 在 Dockerfile 中會自動使用容器模式
# 不需要指定參數
```

## 🔄 遷移指南

### 從舊腳本遷移

#### 之前使用 docker-start.sh
```bash
# 舊命令
./docker-start.sh

# 新命令（等效）
./start.sh --docker
# 或讓腳本自動偵測
./start.sh
```

#### 之前使用 start.sh（本地模式）
```bash
# 舊命令
./start.sh

# 新命令（本地模式）
./start.sh --local
# 或讓腳本自動偵測
./start.sh
```

#### 之前使用 docker-stop.sh
```bash
# 舊命令
./docker-stop.sh

# 新命令（等效）
./stop.sh --docker
# 或停止所有
./stop.sh
```

## ⚙️ 更新的檔案

### Dockerfile
- 更新 `CMD` 指令使用 `/app/start.sh`
- 保持其他配置不變

### docker-compose.yml
- 無需修改，自動使用新的 start.sh
- 容器內會自動偵測為容器模式

### 環境變數配置
- 完全相容 `.env` 檔案
- 無需修改現有配置

## 🧪 測試建議

### 測試 Docker 模式
```bash
./stop.sh
./start.sh --docker
curl http://localhost:30000/health
```

### 測試本地模式
```bash
./stop.sh
./start.sh --local
curl http://localhost:30000/health
```

### 測試自動偵測
```bash
./stop.sh
./start.sh
# 檢查輸出確認使用了哪種模式
```

## 📚 相關文件

- [ENV_CONFIG.md](ENV_CONFIG.md) - 環境變數配置說明
- [README.md](README.md) - 專案整體說明
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API 文件

## ❓ 常見問題

**Q: 為什麼要整合腳本？**
A: 簡化使用，減少混淆，一個腳本解決所有啟動需求。

**Q: 舊的命令還能用嗎？**
A: 舊的腳本檔案已刪除，請使用新的參數方式。

**Q: 如何確定使用了哪種模式？**
A: 執行腳本時會在開頭顯示「偵測到的環境」訊息。

**Q: 可以同時運行多種模式嗎？**
A: 不建議，會造成端口衝突。請先停止現有服務。

**Q: 在容器內執行會怎樣？**
A: 自動切換到容器模式，使用 Gunicorn 啟動。
