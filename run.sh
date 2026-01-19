#!/bin/bash

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 配置
IMAGE_NAME="test-flask-app"
CONTAINER_NAME="flask-container"
PORT=5000

echo -e "${BLUE}=== Flask 應用部署腳本 ===${NC}"

# 停止並刪除舊的容器
echo -e "${BLUE}1. 清理舊容器...${NC}"
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    docker stop $CONTAINER_NAME 2>/dev/null
    docker rm $CONTAINER_NAME 2>/dev/null
    echo -e "${GREEN}✓ 舊容器已清理${NC}"
fi

# 構建 Docker 映像檔
echo -e "${BLUE}2. 構建 Docker 映像檔...${NC}"
docker build -t $IMAGE_NAME .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 映像檔構建成功${NC}"
else
    echo -e "${RED}✗ 映像檔構建失敗${NC}"
    exit 1
fi

# 運行容器
echo -e "${BLUE}3. 啟動容器...${NC}"
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:5000 \
    $IMAGE_NAME

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 容器啟動成功${NC}"
    echo -e "${GREEN}應用運行於: http://localhost:$PORT${NC}"
    echo -e "${BLUE}查看日誌: docker logs -f $CONTAINER_NAME${NC}"
else
    echo -e "${RED}✗ 容器啟動失敗${NC}"
    exit 1
fi
