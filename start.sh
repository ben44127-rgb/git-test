#!/bin/bash

# ==========================================
# Django 圖片處理服務統一啟動腳本
# ==========================================
# 這個腳本可以自動偵測環境並選擇適當的啟動方式：
# 1. Docker 容器內部 - 使用 Gunicorn 啟動
# 2. 宿主機 + Docker - 使用 Docker Compose 啟動
# 3. 宿主機本地開發 - 使用 Django 開發伺服器啟動
#
# 使用方式：
#   ./start.sh              # 自動偵測環境
#   ./start.sh --docker     # 強制使用 Docker Compose
#   ./start.sh --local      # 強制使用本地開發模式
#   ./start.sh --help       # 顯示幫助

set -e  # 遇到錯誤立即退出

# ==========================================
# 解析命令列參數
# ==========================================
FORCE_MODE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            FORCE_MODE="docker"
            shift
            ;;
        --local)
            FORCE_MODE="local"
            shift
            ;;
        --help|-h)
            echo "使用方式: $0 [選項]"
            echo ""
            echo "選項："
            echo "  --docker    強制使用 Docker Compose 模式"
            echo "  --local     強制使用本地開發模式"
            echo "  --help      顯示此幫助訊息"
            echo ""
            echo "不指定選項時，會自動偵測環境："
            echo "  - 在 Docker 容器內：使用 Gunicorn"
            echo "  - 宿主機有 Docker：使用 Docker Compose"
            echo "  - 宿主機無 Docker：使用本地開發伺服器"
            exit 0
            ;;
        *)
            echo "❌ 未知選項: $1"
            echo "使用 --help 查看幫助"
            exit 1
            ;;
    esac
done

# ==========================================
# 函數：等待服務就緒
# ==========================================
wait_for_service() {
    local service_name=$1
    local host=$2
    local port=$3
    local max_attempts=30
    local attempt=1

    echo "⏳ 等待 $service_name 服務就緒 ($host:$port)..."
    
    while [ $attempt -le $max_attempts ]; do
        if timeout 1 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
            echo "✅ $service_name 服務已就緒"
            return 0
        fi
        echo "   嘗試 $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name 服務啟動超時"
    return 1
}

# ==========================================
# 偵測運行環境
# ==========================================
detect_environment() {
    # 檢查是否在 Docker 容器內
    if [ -f /.dockerenv ]; then
        echo "container"
        return
    fi
    
    # 檢查是否有 Docker
    if command -v docker &> /dev/null; then
        # 檢查 Docker 是否可用
        if docker ps &> /dev/null; then
            echo "docker"
            return
        fi
    fi
    
    # 預設為本地模式
    echo "local"
}

# 決定運行模式
if [ -n "$FORCE_MODE" ]; then
    RUN_MODE=$FORCE_MODE
else
    RUN_MODE=$(detect_environment)
fi

echo "=========================================="
echo "   Django 圖片處理服務啟動腳本"
echo "=========================================="
echo ""

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤：未找到 python3，請先安裝 Python 3"
    exit 1
fi

# 檢查 pip 是否安裝
if ! command -v pip3 &> /dev/null; then
    echo "❌ 錯誤：未找到 pip3，請先安裝 pip"
    exit 1
fi

# 檢查虛擬環境
if [ -d "venv" ]; then
    echo "🔍 發現虛擬環境，正在啟動..."
    source venv/bin/activate
    echo "✅ 虛擬環境已啟動"
fi

# 檢查必要的依賴是否安裝
echo ""
echo "📦 檢查 Python 依賴..."
if ! python3 -c "import django" 2>/dev/null; then
    echo "⚠️  未找到 Django，正在安裝依賴..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依賴安裝失敗"
        exit 1
    fi
else
    echo "✅ Django 已安裝"
fi

# 檢查 Docker 和 Docker Compose 服務
echo ""
echo "🔍 檢查 Docker 和 Docker Compose..."
if ! command -v docker &> /dev/null; then
    echo "❌ 錯誤：未找到 Docker，請先安裝 Docker"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ 錯誤：Docker 未運行，請啟動 Docker 服務"
    exit 1
fi

COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ 錯誤：未找到 docker-compose，請先安裝 Docker Compose"
    exit 1
fi

echo "✅ Docker 環境檢查完成，使用命令：$COMPOSE_CMD"

# 檢查容器是否運行
echo ""
echo "🔍 檢查容器服務狀態..."
MINIO_RUNNING=$(docker ps 2>/dev/null | grep -q minio && echo "true" || echo "false")
BACKEND_RUNNING=$(docker ps 2>/dev/null | grep -q django-backend && echo "true" || echo "false")

if [ "$MINIO_RUNNING" = "true" ] && [ "$BACKEND_RUNNING" = "true" ]; then
    echo "✅ MinIO 和 Django Backend 都已在運行"
else
    echo "⚠️  檢測到服務未運行，正在啟動所有容器..."
    echo "📦 啟動 MinIO 和 Django Backend..."
    $COMPOSE_CMD up -d
    
    if [ $? -eq 0 ]; then
        echo "⏳ 等待容器啟動..."
        sleep 5
        
        # 驗證容器狀態
        if docker ps | grep -q minio && docker ps | grep -q django-backend; then
            echo "✅ MinIO 和 Django Backend 啟動成功"
            echo "   MinIO API: http://localhost:9000"
            echo "   MinIO 控制台: http://localhost:9001"
            echo "   Django Backend: http://localhost:30000"
        else
            echo "❌ 部分容器啟動失敗，請檢查日誌"
            $COMPOSE_CMD logs
            exit 1
        fi
    else
        echo "❌ 容器啟動失敗"
        exit 1
    fi
fi

# 創建必要的目錄
echo ""
echo "📁 創建必要的目錄..."
mkdir -p output
mkdir -p logs
echo "✅ 目錄創建完成"

# 檢查是否有舊的進程在運行
echo ""
echo "🔍 檢查舊進程..."
OLD_PID=$(pgrep -f "manage.py runserver" 2>/dev/null)
if [ ! -z "$OLD_PID" ]; then
    echo "⚠️  發現舊進程（PID: $OLD_PID），正在停止..."
    kill $OLD_PID 2>/dev/null || true
    sleep 2
    # 確認是否已停止
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo "⚠️  進程未停止，嘗試強制停止..."
        kill -9 $OLD_PID 2>/dev/null || true
    fi
fi

# 檢查端口是否被佔用
echo ""
echo "🔍 檢查端口 30000..."
if lsof -Pi :30000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 30000 已被佔用"
    PORT_PID=$(lsof -Pi :30000 -sTCP:LISTEN -t)
    echo "   佔用進程 PID: $PORT_PID"
    echo "   可以使用以下命令停止: kill $PORT_PID"
    exit 1
else
    echo "✅ 端口 30000 可用"
fi

# 運行數據庫遷移
echo ""
echo "🔄 運行數據庫遷移..."
python3 manage.py migrate --noinput
if [ $? -eq 0 ]; then
    echo "✅ 數據庫遷移完成"
else
    echo "❌ 數據庫遷移失敗"
    exit 1
fi

# 執行 Django 系統檢查
echo ""
echo "🔍 執行系統檢查..."
python3 manage.py check
if [ $? -ne 0 ]; then
    echo "❌ 系統檢查失敗"
    exit 1
fi

# 啟動 Django 應用
echo ""
echo "🚀 啟動 Django 應用..."
echo "   使用開發伺服器（不適合生產環境）"
nohup python3 manage.py runserver 0.0.0.0:30000 > logs/app.log 2>&1 &
APP_PID=$!

# 等待服務啟動
sleep 3

# 檢查進程是否還在運行
if ps -p $APP_PID > /dev/null; then
    echo "✅ 應用已啟動！"
    echo "   進程 ID: $APP_PID"
    echo "   日誌檔案: logs/app.log"
    echo "   API 地址: http://localhost:30000"
    
    # 執行健康檢查
    echo ""
    echo "🏥 執行健康檢查..."
    sleep 2
    if curl -f http://localhost:30000/health 2>/dev/null; then
        echo "✅ 健康檢查通過！"
    else
        echo "⚠️  健康檢查失敗，請查看日誌"
    fi
else
    echo "❌ 應用啟動失敗，請查看日誌："
    echo "   tail -f logs/app.log"
    exit 1
fi

echo ""
echo "📝 常用命令："
echo "   查看日誌:     tail -f logs/app.log"
echo "   停止服務:     ./stop.sh"
echo "   健康檢查:     curl http://localhost:30000/health"
echo "   重啟服務:     ./stop.sh && ./start.sh"
echo ""
echo "💡 提示："
echo "   這是開發伺服器，不適合生產環境"
echo "   生產環境請使用 Docker: ./docker-start.sh"
echo ""
echo "=========================================="
