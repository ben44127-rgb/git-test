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
#   ./start.sh              # 自動偵測環境（預設 Docker 模式）
#   ./start.sh --docker     # 強制使用 Docker Compose
#   ./start.sh --local      # 強制使用本地開發模式
#   ./start.sh --test       # 啟動後自動運行認證系統測試
#   ./start.sh --help       # 顯示幫助

set -e  # 遇到錯誤立即退出

# ==========================================
# 解析命令列參數
# ==========================================
FORCE_MODE=""
RUN_TEST=false
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
        --test)
            RUN_TEST=true
            shift
            ;;
        --help|-h)
            echo "使用方式: $0 [選項]"
            echo ""
            echo "選項："
            echo "  --docker    強制使用 Docker Compose 模式"
            echo "  --local     強制使用本地開發模式"
            echo "  --test      啟動後自動運行認證系統測試"
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
echo "   運行模式: $RUN_MODE"
echo "=========================================="
echo ""

# ==========================================
# 確保 .env 檔案存在
# ==========================================
ensure_env_file() {
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            echo "⚠️  未找到 .env 檔案，從 .env.example 自動複製..."
            cp .env.example .env
            echo "✅ 已建立 .env 檔案（使用預設值）"
            echo "   如需自訂配置，請編輯 .env 檔案後重新啟動"
        else
            echo "❌ 錯誤：未找到 .env 或 .env.example 檔案"
            exit 1
        fi
    else
        echo "✅ .env 檔案已存在"
    fi
}

# ==========================================
# 檢查 Docker 環境
# ==========================================
check_docker() {
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
    if docker compose version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo "❌ 錯誤：未找到 docker-compose，請先安裝 Docker Compose"
        exit 1
    fi
    echo "✅ Docker 環境檢查完成，使用命令：$COMPOSE_CMD"
}

# ==========================================
# 模式一：Docker Compose 啟動（宿主機）
# ==========================================
start_docker() {
    echo "🐳 使用 Docker Compose 模式啟動..."
    echo ""
    
    ensure_env_file
    echo ""
    check_docker
    echo ""
    
    # 創建必要的目錄
    mkdir -p output logs

    # 檢查容器是否已在運行
    echo "🔍 檢查容器服務狀態..."
    DB_RUNNING=$(docker ps 2>/dev/null | grep -q auth_postgres && echo "true" || echo "false")
    MINIO_RUNNING=$(docker ps 2>/dev/null | grep -q minio && echo "true" || echo "false")
    BACKEND_RUNNING=$(docker ps 2>/dev/null | grep -q django-backend && echo "true" || echo "false")

    if [ "$DB_RUNNING" = "true" ] && [ "$MINIO_RUNNING" = "true" ] && [ "$BACKEND_RUNNING" = "true" ]; then
        echo "✅ 所有服務都已在運行"
    else
        echo "⚠️  檢測到服務未運行，正在啟動所有容器..."
        echo "📦 構建並啟動所有服務（PostgreSQL + MinIO + Django Backend）..."
        $COMPOSE_CMD up --build -d

        if [ $? -eq 0 ]; then
            echo "⏳ 等待容器啟動..."
            sleep 10

            # 驗證容器狀態
            echo ""
            echo "🔍 驗證服務狀態..."
            if docker ps | grep -q auth_postgres; then
                echo "   ✅ PostgreSQL 數據庫: 運行中 (port 9090)"
            else
                echo "   ❌ PostgreSQL 數據庫: 啟動失敗"
            fi
            if docker ps | grep -q minio; then
                echo "   ✅ MinIO 物件存儲: 運行中 (API: 9000, 控制台: 9001)"
            else
                echo "   ❌ MinIO 物件存儲: 啟動失敗"
            fi
            if docker ps | grep -q django-backend; then
                echo "   ✅ Django Backend: 運行中 (port 30000)"
            else
                echo "   ❌ Django Backend: 啟動失敗"
                echo ""
                echo "查看日誌以排查問題："
                $COMPOSE_CMD logs backend
                exit 1
            fi
        else
            echo "❌ 容器啟動失敗"
            exit 1
        fi
    fi

    # 等待後端健康檢查
    echo ""
    echo "🏥 等待 Django 服務就緒..."
    for i in $(seq 1 30); do
        if curl -sf http://localhost:30000/health > /dev/null 2>&1; then
            echo "✅ 健康檢查通過！"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "⚠️  健康檢查超時，服務可能仍在啟動中"
            echo "   請稍後手動檢查: curl http://localhost:30000/health"
        fi
        sleep 2
    done

    echo ""
    echo "=========================================="
    echo "   🎉 所有服務已啟動！"
    echo "=========================================="
    echo ""
    echo "   📡 服務地址："
    echo "   Django 後端:   http://localhost:30000"
    echo "   圖片上傳:     http://localhost:30000/picture/clothes/upload_image"
    echo "   MinIO API:     http://localhost:9000"
    echo "   MinIO 控制台:  http://localhost:9001"
    echo "   PostgreSQL:    localhost:9090"
    echo ""
    echo "   📝 常用命令："
    echo "   查看日誌:      $COMPOSE_CMD logs -f"
    echo "   查看後端日誌:  $COMPOSE_CMD logs -f backend"
    echo "   停止服務:      ./stop.sh"
    echo "   重啟服務:      ./stop.sh && ./start.sh"
    echo "   查看容器狀態:  $COMPOSE_CMD ps"
    echo "   進入數據庫:    docker exec -it auth_postgres psql -U auth_user -d auth_db"
    echo ""
    echo "=========================================="
}

# ==========================================
# 模式二：本地開發啟動（宿主機無 Docker 或 --local）
# ==========================================
start_local() {
    echo "💻 使用本地開發模式啟動..."
    echo ""

    ensure_env_file
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

    # 嘗試用 Docker 啟動資料庫和 MinIO（如果有 Docker）
    if command -v docker &> /dev/null && docker info &> /dev/null 2>&1; then
        echo ""
        echo "🐳 偵測到 Docker，啟動 PostgreSQL 和 MinIO 容器..."
        check_docker
        $COMPOSE_CMD up -d db minio
        echo "⏳ 等待數據庫服務就緒..."
        sleep 5
        wait_for_service "PostgreSQL" "localhost" "9090"
    else
        echo ""
        echo "⚠️  未偵測到 Docker，請確保 PostgreSQL 和 MinIO 已手動啟動"
        echo "   PostgreSQL: localhost:9090"
        echo "   MinIO: localhost:9000"
    fi

    # 創建必要的目錄
    echo ""
    echo "📁 創建必要的目錄..."
    mkdir -p output logs
    echo "✅ 目錄創建完成"

    # 檢查是否有舊的進程在運行
    echo ""
    echo "🔍 檢查舊進程..."
    OLD_PID=$(pgrep -f "manage.py runserver" 2>/dev/null)
    if [ ! -z "$OLD_PID" ]; then
        echo "⚠️  發現舊進程（PID: $OLD_PID），正在停止..."
        kill $OLD_PID 2>/dev/null || true
        sleep 2
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
    echo "🚀 啟動 Django 開發伺服器..."
    nohup python3 manage.py runserver 0.0.0.0:30000 > logs/app.log 2>&1 &
    APP_PID=$!

    # 等待服務啟動
    sleep 3

    # 檢查進程是否還在運行
    if ps -p $APP_PID > /dev/null; then
        echo "✅ 應用已啟動！"
        echo "   進程 ID: $APP_PID"
        echo "   日誌檔案: logs/app.log"
        echo "   服務地址: http://localhost:30000"
        echo "   圖片上傳: http://localhost:30000/picture/clothes/upload_image"

        # 執行健康檢查
        echo ""
        echo "🏥 執行健康檢查..."
        sleep 2
        if curl -f http://localhost:30000/health 2>/dev/null; then
            echo ""
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
    echo "=========================================="
    echo "   🎉 本地開發伺服器已啟動！"
    echo "=========================================="
    echo ""
    echo "   📝 常用命令："
    echo "   查看日誌:     tail -f logs/app.log"
    echo "   停止服務:     ./stop.sh"
    echo "   健康檢查:     curl http://localhost:30000/health"
    echo "   重啟服務:     ./stop.sh && ./start.sh --local"
    echo ""
    echo "   💡 提示：這是開發伺服器，不適合生產環境"
    echo ""
    echo "=========================================="
}

# ==========================================
# 模式三：容器內部啟動
# ==========================================
start_container() {
    echo "📦 在 Docker 容器內部啟動..."
    echo ""

    # 等待 PostgreSQL 數據庫就緒（使用 Python psycopg2 確認連線）
    echo "⏳ 等待 PostgreSQL 數據庫就緒..."
    MAX_RETRIES=30
    RETRY=0
    until python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        dbname='${DB_NAME:-auth_db}',
        user='${DB_USER:-auth_user}',
        password='${DB_PASSWORD:-auth_password_123}',
        host='${DB_HOST:-db}',
        port='${DB_PORT:-5432}'
    )
    conn.close()
    print('✅ 數據庫連線成功')
except Exception as e:
    print(f'⏳ 數據庫尚未就緒: {e}')
    exit(1)
" 2>/dev/null; do
        RETRY=$((RETRY + 1))
        if [ $RETRY -ge $MAX_RETRIES ]; then
            echo "❌ 數據庫連線超時，請檢查 PostgreSQL 服務"
            exit 1
        fi
        echo "   重試 $RETRY/$MAX_RETRIES..."
        sleep 2
    done

    # 創建必要的目錄
    mkdir -p /app/output /app/logs

    # 運行數據庫遷移
    echo ""
    echo "🔄 運行數據庫遷移..."
    python3 manage.py migrate --noinput
    echo "✅ 數據庫遷移完成"

    # 自動建立管理員帳號
    echo ""
    echo "👤 檢查管理員帳號..."
    python3 manage.py shell <<'PYTHON_SCRIPT'
from accounts.models import User

if not User.objects.filter(user_name='admin').exists():
    User.objects.create_superuser(
        user_name='admin',
        user_email='admin@admin.com',
        user_password='admin123'
    )
    print('✅ 管理員帳號已建立: admin / admin123')
else:
    print('ℹ️  管理員帳號已存在')
PYTHON_SCRIPT

    # 根據 DJANGO_DEV_MODE 選擇啟動模式
    echo ""
    if [ "${DJANGO_DEV_MODE}" = "true" ]; then
        echo "🔧 開發模式：Hot Reload 已啟用"
        echo "🚀 啟動 Django 開發伺服器 (port 30000)..."
        exec python3 manage.py runserver 0.0.0.0:30000
    else
        echo "🚀 生產模式：使用 Gunicorn"
        echo "🚀 啟動 Gunicorn 伺服器 (port 30000)..."
        exec gunicorn config.wsgi:application \
            --bind 0.0.0.0:30000 \
            --workers 4 \
            --timeout 300 \
            --access-logfile /app/logs/access.log \
            --error-logfile /app/logs/error.log
    fi
}

# ==========================================
# 根據模式分支執行
# ==========================================
case "$RUN_MODE" in
    docker)
        start_docker
        ;;
    local)
        start_local
        ;;
    container)
        start_container
        ;;
    *)
        echo "❌ 未知運行模式: $RUN_MODE"
        exit 1
        ;;
esac

# ==========================================
# 認證系統測試（如果指定 --test 選項）
# ==========================================
if [ "$RUN_TEST" = true ]; then
    echo ""
    echo "=========================================="
    echo "   開始測試用戶認證系統"
    echo "=========================================="
    echo ""
    
    # 等待服務完全啟動
    echo "⏳ 等待服務完全啟動..."
    sleep 3
    
    BASE_URL="http://localhost:30000/account/user"
    
    # 顏色定義
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
    
    # 測試註冊
    echo -e "${BLUE}📝 測試用戶註冊...${NC}"
    REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST ${BASE_URL}/register \
      -H "Content-Type: application/json" \
      -d '{"username":"testuser","password":"testPass123!","email":"test@test.com"}')
    
    REGISTER_BODY=$(echo "$REGISTER_RESPONSE" | head -n -1)
    REGISTER_CODE=$(echo "$REGISTER_RESPONSE" | tail -n 1)
    
    if [ "$REGISTER_CODE" = "201" ]; then
      echo -e "${GREEN}✅ 註冊成功 (201 Created)${NC}"
      echo "響應: $REGISTER_BODY"
    elif [ "$REGISTER_CODE" = "409" ]; then
      echo -e "${YELLOW}⚠️  用戶已存在 (409 Conflict)${NC}"
      echo "響應: $REGISTER_BODY"
    else
      echo -e "${RED}❌ 註冊失敗 ($REGISTER_CODE)${NC}"
      echo "響應: $REGISTER_BODY"
    fi
    echo ""
    
    # 測試登入（取得 JWT Token）
    echo -e "${BLUE}🔐 測試用戶登入...${NC}"
    LOGIN_RESPONSE=$(curl -s -X POST ${BASE_URL}/login \
      -H "Content-Type: application/json" \
      -d '{"username":"testuser","password":"testPass123!"}')
    
    ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access',''))" 2>/dev/null)
    REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('refresh',''))" 2>/dev/null)
    
    if [ -n "$ACCESS_TOKEN" ] && [ "$ACCESS_TOKEN" != "" ]; then
      echo -e "${GREEN}✅ 登入成功 (200 OK)${NC}"
      echo "Access Token: ${ACCESS_TOKEN:0:50}..."
      echo "Refresh Token: ${REFRESH_TOKEN:0:50}..."
      echo "User: $(echo $LOGIN_RESPONSE | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin).get('user',{})))" 2>/dev/null)"
    else
      echo -e "${RED}❌ 登入失敗${NC}"
      echo "響應: $LOGIN_RESPONSE"
    fi
    echo ""
    
    # 測試使用 Token 存取受保護的資源（登出需要認證）
    echo -e "${BLUE}🚪 測試用戶登出 (使用 JWT Token)...${NC}"
    if [ -n "$ACCESS_TOKEN" ] && [ -n "$REFRESH_TOKEN" ]; then
      LOGOUT_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST ${BASE_URL}/logout \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -d "{\"refresh\":\"${REFRESH_TOKEN}\"}")
      
      LOGOUT_BODY=$(echo "$LOGOUT_RESPONSE" | head -n -1)
      LOGOUT_CODE=$(echo "$LOGOUT_RESPONSE" | tail -n 1)
      
      if [ "$LOGOUT_CODE" = "200" ]; then
        echo -e "${GREEN}✅ 登出成功 (200 OK)${NC}"
        echo "響應: $LOGOUT_BODY"
      else
        echo -e "${RED}❌ 登出失敗 ($LOGOUT_CODE)${NC}"
        echo "響應: $LOGOUT_BODY"
      fi
    else
      echo -e "${YELLOW}⚠️  跳過登出測試（無有效 Token）${NC}"
    fi
    echo ""
    
    # 測試 Token 失效後的存取（應該返回 401）
    echo -e "${BLUE}🔎 測試已登出後使用舊 Token 存取...${NC}"
    if [ -n "$REFRESH_TOKEN" ]; then
      REUSE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST ${BASE_URL}/logout \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -d "{\"refresh\":\"${REFRESH_TOKEN}\"}")
      
      REUSE_CODE=$(echo "$REUSE_RESPONSE" | tail -n 1)
      
      if [ "$REUSE_CODE" = "401" ]; then
        echo -e "${GREEN}✅ Token 已正確失效 (401 Unauthorized)${NC}"
      else
        echo -e "${YELLOW}⚠️  Token 狀態異常 ($REUSE_CODE)${NC}"
      fi
    fi
    echo ""
    
    echo "=========================================="
    echo "   認證系統測試完成！"
    echo "=========================================="
    echo ""
    echo "💡 提示："
    echo "- 查看 Docker 容器狀態: docker-compose ps"
    echo "- 查看後端日誌: docker-compose logs backend"
    echo "- 查看數據庫: docker exec -it auth_postgres psql -U auth_user -d auth_db"
    echo ""
fi
