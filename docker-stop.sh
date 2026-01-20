#!/bin/bash

# ==========================================
# Docker 環境停止腳本
# ==========================================

echo "=========================================="
echo "   停止 Docker 服務"
echo "=========================================="
echo ""

# 檢查是否在 Docker 容器內
if [ -f /.dockerenv ]; then
    echo "⚠️  此腳本應在宿主機上運行，不應在容器內執行"
    exit 1
fi

# 確定使用哪個命令
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ 錯誤：未找到 docker-compose"
    exit 1
fi

echo "📦 使用命令: $COMPOSE_CMD"
echo ""

# 顯示當前運行的容器
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
    docker ps --filter "name=django-backend" --filter "name=minio"
else
    echo "✅ 所有服務已停止"
fi

echo ""
echo "📝 其他可用命令："
echo "   停止但保留容器:    $COMPOSE_CMD stop"
echo "   刪除所有數據:      $COMPOSE_CMD down -v"
echo "   查看所有容器:      docker ps -a"
echo ""
echo "=========================================="
