#!/bin/bash

# ==========================================
# Django 應用停止腳本（本地開發版）
# ==========================================
# 停止本地運行的 Django 開發伺服器
# 如果要停止 Docker 服務，請使用 docker-stop.sh

echo "=========================================="
echo "   停止 Django 應用 (本地版)"
echo "=========================================="
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
        read -p "是否要停止該進程？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill $PORT_PID 2>/dev/null || true
            sleep 1
            if lsof -Pi :30000 -sTCP:LISTEN -t >/dev/null 2>&1; then
                kill -9 $PORT_PID 2>/dev/null || true
            fi
            echo "✅ 進程已停止"
        fi
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
        
        if pgrep -f "manage.py runserver" > /dev/null 2>&1; then
            echo "❌ 無法停止進程"
            exit 1
        fi
    fi
    
    echo "✅ Django 應用已停止"
fi

# 檢查 Gunicorn 進程（如果存在）
GUNICORN_PID=$(pgrep -f "gunicorn.*config.wsgi" 2>/dev/null)
if [ ! -z "$GUNICORN_PID" ]; then
    echo ""
    echo "🔍 發現 Gunicorn 進程: $GUNICORN_PID"
    read -p "是否要停止 Gunicorn？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $GUNICORN_PID 2>/dev/null || true
        sleep 1
        if pgrep -f "gunicorn.*config.wsgi" > /dev/null 2>&1; then
            kill -9 $GUNICORN_PID 2>/dev/null || true
        fi
        echo "✅ Gunicorn 已停止"
    fi
fi

echo ""
echo "📝 其他命令："
echo "   停止 Docker 服務:  ./docker-stop.sh"
echo "   查看運行進程:      ps aux | grep manage.py"
echo "   查看端口佔用:      lsof -i :30000"
echo ""
echo "=========================================="
