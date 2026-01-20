#!/bin/bash

# ==========================================
# Docker 環境啟動腳本
# ==========================================
# 這個腳本用於在 Docker 容器內部或通過 Docker Compose 啟動服務

set -e  # 遇到錯誤立即退出

echo "=========================================="
echo "   Django 圖片處理服務 (Docker 版本)"
echo "=========================================="
echo ""

# 檢查是否在 Docker 容器內
if [ -f /.dockerenv ]; then
    echo "✅ 運行在 Docker 容器內"
    IN_DOCKER=true
else
    echo "📦 運行在宿主機上，將使用 Docker Compose"
    IN_DOCKER=false
fi

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
# 如果在容器內運行
# ==========================================
if [ "$IN_DOCKER" = true ]; then
    echo ""
    echo "🔧 容器內部初始化..."
    
    # 創建必要的目錄
    mkdir -p /app/output
    mkdir -p /app/logs
    echo "✅ 目錄創建完成"
    
    # 等待 MinIO 服務
    if [ ! -z "$MINIO_ENDPOINT" ]; then
        MINIO_HOST=$(echo $MINIO_ENDPOINT | cut -d':' -f1)
        MINIO_PORT=$(echo $MINIO_ENDPOINT | cut -d':' -f2)
        wait_for_service "MinIO" "$MINIO_HOST" "$MINIO_PORT" || echo "⚠️  無法連接到 MinIO"
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
    
    # 收集靜態文件（如果需要）
    # python3 manage.py collectstatic --noinput
    
    # 啟動 Django 應用
    echo ""
    echo "🚀 啟動 Django 應用 (Gunicorn)..."
    echo "   監聽地址: 0.0.0.0:30000"
    echo "   Workers: 2"
    echo "   Timeout: 120s"
    echo ""
    
    # 使用 gunicorn 啟動（生產級 WSGI 服務器）
    exec gunicorn \
        --bind 0.0.0.0:30000 \
        --workers 2 \
        --threads 4 \
        --timeout 120 \
        --access-logfile /app/logs/access.log \
        --error-logfile /app/logs/error.log \
        --log-level info \
        config.wsgi:application

# ==========================================
# 如果在宿主機上運行（使用 Docker Compose）
# ==========================================
else
    echo ""
    echo "📦 檢查 Docker 環境..."
    
    # 檢查 docker 是否安裝
    if ! command -v docker &> /dev/null; then
        echo "❌ 錯誤：未找到 docker，請先安裝 Docker"
        exit 1
    fi
    
    # 檢查 docker-compose 是否安裝
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo "❌ 錯誤：未找到 docker-compose，請先安裝 Docker Compose"
        exit 1
    fi
    
    # 確定使用哪個命令
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    echo "✅ Docker 環境檢查通過"
    echo "   使用命令: $COMPOSE_CMD"
    
    # 檢查是否有舊容器運行
    echo ""
    echo "🔍 檢查舊容器..."
    if docker ps -a | grep -q django-backend; then
        echo "⚠️  發現舊容器，正在清理..."
        $COMPOSE_CMD down
        sleep 2
    fi
    
    # 構建並啟動服務
    echo ""
    echo "🔨 構建 Docker 映像..."
    $COMPOSE_CMD build
    
    echo ""
    echo "🚀 啟動服務..."
    $COMPOSE_CMD up -d
    
    # 等待服務啟動
    echo ""
    echo "⏳ 等待服務啟動..."
    sleep 5
    
    # 檢查容器狀態
    echo ""
    echo "📊 容器狀態："
    docker ps --filter "name=django-backend" --filter "name=minio" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    # 顯示日誌
    echo ""
    echo "📝 最近的日誌輸出："
    $COMPOSE_CMD logs --tail=20 backend
    
    # 健康檢查
    echo ""
    echo "🏥 執行健康檢查..."
    sleep 3
    
    if curl -f http://localhost:30000/health 2>/dev/null; then
        echo "✅ 健康檢查通過！"
    else
        echo "⚠️  健康檢查失敗，請查看日誌"
    fi
    
    # 顯示訪問信息
    echo ""
    echo "=========================================="
    echo "✅ 服務啟動完成！"
    echo ""
    echo "📍 服務地址："
    echo "   Django API:        http://localhost:30000"
    echo "   健康檢查:          http://localhost:30000/health"
    echo "   MinIO 控制台:      http://localhost:9001"
    echo "   MinIO API:         http://localhost:9000"
    echo ""
    echo "🔐 MinIO 登錄信息："
    echo "   用戶名: minioadmin"
    echo "   密碼:   minioadmin"
    echo ""
    echo "📝 常用命令："
    echo "   查看日誌:         $COMPOSE_CMD logs -f backend"
    echo "   查看所有容器:     docker ps"
    echo "   停止服務:         $COMPOSE_CMD down"
    echo "   重啟服務:         $COMPOSE_CMD restart"
    echo "   進入容器:         docker exec -it django-backend bash"
    echo ""
    echo "🧪 測試命令："
    echo "   curl http://localhost:30000/health"
    echo "=========================================="
fi
