#!/bin/bash

# ==========================================
# Django 應用啟動腳本
# ==========================================
# 這個腳本會自動檢查並啟動所有必要的服務

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

# 檢查必要的依賴是否安裝
echo "📦 檢查 Python 依賴..."
if ! python3 -c "import django" 2>/dev/null; then
    echo "⚠️  未找到 Django，正在安裝依賴..."
    pip3 install -r requirements.txt
else
    echo "✅ Django 已安裝"
fi

# 檢查 MinIO 容器是否運行
echo ""
echo "🔍 檢查 MinIO 服務..."
if docker ps | grep -q minio; then
    echo "✅ MinIO 服務正在運行"
else
    echo "⚠️  MinIO 服務未運行"
    echo "   可以使用以下命令啟動："
    echo "   docker-compose up -d minio"
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
OLD_PID=$(pgrep -f "manage.py runserver")
if [ ! -z "$OLD_PID" ]; then
    echo "⚠️  發現舊進程（PID: $OLD_PID），正在停止..."
    kill $OLD_PID
    sleep 2
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

# 啟動 Django 應用
echo ""
echo "🚀 啟動 Django 應用..."
nohup python3 manage.py runserver 0.0.0.0:30000 > logs/app.log 2>&1 &
APP_PID=$!

echo "✅ 應用已啟動！"
echo "   進程 ID: $APP_PID"
echo "   日誌檔案: logs/app.log"
echo "   API 地址: http://localhost:30000"
echo ""
echo "📝 常用命令："
echo "   查看日誌: tail -f logs/app.log"
echo "   停止服務: ./stop.sh"
echo "   健康檢查: curl http://localhost:30000/health"
echo ""
echo "=========================================="
