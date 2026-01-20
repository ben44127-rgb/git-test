#!/bin/bash

# ==========================================
# Django 圖片處理服務統一停止腳本
# ==========================================
# 這個腳本可以停止不同模式下運行的服務：
# 1. Docker Compose 模式
# 2. 本地開發模式
#
# 使用方式：
#   ./stop.sh              # 自動偵測並停止所有模式
#   ./stop.sh --docker     # 只停止 Docker Compose
#   ./stop.sh --local      # 只停止本地開發伺服器
#   ./stop.sh --help       # 顯示幫助

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
        --all)
            FORCE_MODE="all"
            shift
            ;;
        --help|-h)
            echo "使用方式: $0 [選項]"
            echo ""
            echo "選項："
            echo "  --docker    只停止 Docker Compose 服務"
            echo "  --local     只停止本地開發伺服器"
            echo "  --all       停止所有模式（預設）"
            echo "  --help      顯示此幫助訊息"
            exit 0
            ;;
        *)
            echo "❌ 未知選項: $1"
            echo "使用 --help 查看幫助"
            exit 1
            ;;
    esac
done

# 預設停止所有
if [ -z "$FORCE_MODE" ]; then
    FORCE_MODE="all"
fi

echo "=========================================="
echo "   停止 Django 圖片處理服務"
echo "=========================================="
echo ""

# ==========================================
# 停止本地開發伺服器
# ==========================================
stop_local() {
    echo "💻 停止本地開發服務..."
    echo ""
    
    # 查找並停止 Django 進程
    echo "🔍 查找 Django 進程..."
    PID=$(pgrep -f "manage.py runserver" 2>/dev/null)
    
    if [ -z "$PID" ]; then
        echo "⚠️  未找到運行中的 Django 進程"
        
        # 檢查端口是否被佔用
        if command -v lsof &> /dev/null && lsof -Pi :30000 -sTCP:LISTEN -t >/dev/null 2>&1; then
            PORT_PID=$(lsof -Pi :30000 -sTCP:LISTEN -t)
            echo "⚠️  但端口 30000 被進程 $PORT_PID 佔用"
            kill $PORT_PID 2>/dev/null || true
            sleep 1
            if lsof -Pi :30000 -sTCP:LISTEN -t >/dev/null 2>&1; then
                kill -9 $PORT_PID 2>/dev/null || true
            fi
            echo "✅ 進程已停止"
        fi
    else
        echo "🛑 正在停止 Django 應用..."
        echo "   進程 PID: $PID"
        
        # 嘗試優雅停止
        kill $PID 2>/dev/null || true
        sleep 2
        
        # 確認是否已停止
        if pgrep -f "manage.py runserver" > /dev/null 2>&1; then
            echo "⚠️  進程未停止，嘗試強制停止..."
            kill -9 $PID 2>/dev/null || true
            sleep 1
        fi
        
        echo "✅ Django 應用已停止"
    fi
    
    # 檢查 Gunicorn 進程（如果存在）
    GUNICORN_PID=$(pgrep -f "gunicorn.*config.wsgi" 2>/dev/null)
    if [ ! -z "$GUNICORN_PID" ]; then
        echo ""
        echo "🔍 發現 Gunicorn 進程: $GUNICORN_PID，正在停止..."
        kill $GUNICORN_PID 2>/dev/null || true
        sleep 1
        if pgrep -f "gunicorn.*config.wsgi" > /dev/null 2>&1; then
            kill -9 $GUNICORN_PID 2>/dev/null || true
        fi
        echo "✅ Gunicorn 已停止"
    fi
}

# ==========================================
# 停止 Docker Compose 服務
# ==========================================
stop_docker() {
    echo "🐳 停止 Docker Compose 服務..."
    echo ""
    
    # 檢查是否在 Docker 容器內
    if [ -f /.dockerenv ]; then
        echo "⚠️  此命令應在宿主機上運行，不應在容器內執行"
        return
    fi
    
    # 確定使用哪個命令
    if docker compose version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo "⚠️  未找到 docker-compose，跳過"
        return
    fi
    
    # 檢查是否有容器在運行
    if ! docker ps | grep -q "django-backend\|minio"; then
        echo "⚠️  未發現運行中的 Docker 容器"
        return
    fi
    
    echo "📦 使用命令: $COMPOSE_CMD"
    echo ""
    echo "🔍 當前運行的容器："
    docker ps --filter "name=django-backend" --filter "name=minio" --format "table {{.Names}}\t{{.Status}}"
    
    # 停止服務
    echo ""
    echo "🛑 停止服務..."
    $COMPOSE_CMD down
    
    # 確認停止
    echo ""
    if docker ps | grep -q "django-backend\|minio"; then
        echo "⚠️  部分容器仍在運行"
    else
        echo "✅ Docker 服務已停止"
    fi
}

# ==========================================
# 執行停止操作
# ==========================================
if [ "$FORCE_MODE" = "local" ]; then
    stop_local
elif [ "$FORCE_MODE" = "docker" ]; then
    stop_docker
elif [ "$FORCE_MODE" = "all" ]; then
    # 停止所有模式
    stop_docker
    echo ""
    stop_local
fi

echo ""
echo "📝 其他可用命令："
echo "   查看運行進程:      ps aux | grep manage.py"
echo "   查看 Docker:       docker ps"
echo "   查看端口佔用:      lsof -i :30000"
echo ""
echo "=========================================="
