#!/bin/bash

# ==========================================
# Django 應用啟動腳本（本地開發版）
# ==========================================
# 這個腳本用於在本地開發環境（非 Docker）中啟動服務
# 如果要在 Docker 中運行，請使用 docker-start.sh

set -e  # 遇到錯誤立即退出

echo "=========================================="
echo "   Django 圖片處理服務啟動腳本 (本地版)"
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

# 檢查 MinIO 容器是否運行
echo ""
echo "🔍 檢查 MinIO 服務..."
if command -v docker &> /dev/null && docker ps 2>/dev/null | grep -q minio; then
    echo "✅ MinIO 服務正在運行"
else
    echo "⚠️  MinIO 服務未運行"
    if command -v docker-compose &> /dev/null; then
        echo "   可以使用以下命令啟動："
        echo "   docker-compose up -d minio"
    elif docker compose version &> /dev/null 2>&1; then
        echo "   可以使用以下命令啟動："
        echo "   docker compose up -d minio"
    else
        echo "   請確保 MinIO 服務正在運行"
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
