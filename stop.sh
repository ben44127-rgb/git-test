#!/bin/bash

# ==========================================
# Django 應用停止腳本
# ==========================================

echo "🛑 正在停止 Django 應用..."

# 查找並停止 Django 進程
PID=$(pgrep -f "manage.py runserver")

if [ -z "$PID" ]; then
    echo "⚠️  未找到運行中的 Django 進程"
else
    echo "找到進程 PID: $PID"
    kill $PID
    sleep 2
    
    # 確認是否已停止
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo "⚠️  進程未停止，嘗試強制停止..."
        kill -9 $PID
    fi
    
    echo "✅ Django 應用已停止"
fi
