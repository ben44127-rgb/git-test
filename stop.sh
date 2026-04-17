#!/bin/bash

# ==========================================
# Django 圖片處理伺務統一停止腳本
# 版本：1.0
# 最後更新：2026-03-23
# ==========================================
# 這個腳本可以停止不同模式下運行的伺務：
# 1. Docker Compose 模式
# 2. 本地開發模式
#
# 使用方式：
#   ./stop.sh              # 自動偵測並停止所有模式
#   ./stop.sh --docker     # 只停止 Docker Compose
#   ./stop.sh --local      # 只停止本地開發伺伺器
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
            echo "  --docker    只停止 Docker Compose 伺務"
            echo "  --local     只停止本地開發伺伺器"
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
echo "   停止 Django 圖片處理伺務"
echo "=========================================="
echo ""

# ==========================================
# 檢查 Docker 環境
# ==========================================
check_docker() {
    echo "🔍 檢查 Docker 和 Docker Compose..."
    if ! command -v docker &> /dev/null; then
        echo "⚠️  警告：未找到 Docker，某些功能可能無法使用"
        return 1
    fi

    if ! docker info &> /dev/null; then
        echo "⚠️  警告：Docker 未運行"
        return 1
    fi

    COMPOSE_CMD=""
    if docker compose version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo "⚠️  警告：未找到 docker-compose"
        return 1
    fi
    echo "✅ Docker 環境檢查完成，使用命令：$COMPOSE_CMD"
    return 0
}

# ==========================================
# 停止本地開發伺伺器
# ==========================================
stop_local() {
    echo "💻 停止本地開發伺務..."
    echo ""
    
    # 查找並停止 Django 進程
    echo "🔍 查找 Django 進程..."
    PID=$(pgrep -f "manage.py runserver" 2>/dev/null)
    
    if [ -z "$PID" ]; then
        echo "⚠️  未找到運行中的 Django 進程"
        
        # 檢查端口是否被佔用
        if command -v lsof &> /dev/null; then
            if lsof -Pi :30000 -sTCP:LISTEN -t >/dev/null 2>&1; then
                PORT_PID=$(lsof -Pi :30000 -sTCP:LISTEN -t)
                echo "⚠️  但端口 30000 被進程 $PORT_PID 佔用"
                echo "   嘗試清理端口..."
                kill $PORT_PID 2>/dev/null || true
                sleep 1
                if lsof -Pi :30000 -sTCP:LISTEN -t >/dev/null 2>&1; then
                    echo "   使用強制停止..."
                    kill -9 $PORT_PID 2>/dev/null || true
                fi
                echo "✅ 端口已清理"
            fi
        else
            echo "   未安裝 lsof，無法檢查端口佔用"
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
# 停止 Docker Compose 伺務
# ==========================================
stop_docker() {
    echo "🐳 停止 Docker Compose 伺務..."
    echo ""
    
    # 檢查是否在 Docker 容器內
    if [ -f /.dockerenv ]; then
        echo "⚠️  此命令應在宿主機上運行，不應在容器內執行"
        return
    fi
    
    # 驗證 .env 檔案是否存在
    if [ ! -f .env ]; then
        echo "⚠️  未找到 .env 檔案"
        echo "   嘗試從 .env.example 複製..."
        if [ -f .env.example ]; then
            cp .env.example .env
            echo "✅ 已建立 .env 檔案"
        else
            echo "❌ 錯誤：.env 和 .env.example 都不存在"
            return
        fi
    else
        echo "✅ .env 檔案已驗證"
    fi
    
    # 確定使用哪個命令
    if docker compose version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo "❌ 未找到 docker-compose，無法停止 Docker 伺務"
        return
    fi
    
    # 檢查是否有容器在運行
    if ! docker ps | grep -q "django-backend\|minio\|auth_postgres"; then
        echo "⚠️  未發現運行中的 Docker 容器"
        return
    fi
    
    echo "📦 使用命令: $COMPOSE_CMD"
    echo ""
    echo "🔍 當前運行的容器："
    docker ps --filter "name=django-backend" --filter "name=minio" --filter "name=auth_postgres" --format "table {{.Names}}\t{{.Status}}"
    
    # 停止伺務
    echo ""
    echo "🛑 停止伺務..."
    $COMPOSE_CMD down
    
    # 確認停止
    echo ""
    if docker ps | grep -q "django-backend\|minio\|auth_postgres"; then
        echo "⚠️  部分容器仍在運行"
    else
        echo "✅ Docker 伺務已全部停止（PostgreSQL + MinIO + Backend）"
    fi
}

# ==========================================
# 執行停止操作
# ==========================================
if [ "$FORCE_MODE" = "local" ]; then
    stop_local
elif [ "$FORCE_MODE" = "docker" ]; then
    check_docker > /dev/null 2>&1 || true  # 不因為 Docker 檢查失敗而退出
    echo ""
    stop_docker
elif [ "$FORCE_MODE" = "all" ]; then
    # 停止所有模式
    echo "🔍 執行環境檢查..."
    check_docker > /dev/null 2>&1 || true  # 不因為 Docker 檢查失敗而退出
    echo ""
    
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
