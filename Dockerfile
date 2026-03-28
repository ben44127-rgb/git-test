# ==========================================
# Django 圖片處理伺務 Dockerfile
# ==========================================

# 使用官方 Python 3.11 作為基礎映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# 安裝系統依賴
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# 複製啟動腳本
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# 複製應用程式代碼
COPY manage.py .
COPY config/ config/
COPY accounts/ accounts/
COPY picture/ picture/
COPY combine/ combine/
COPY aichat_service/ aichat_service/

# 複製環境變數檔案（如果存在）
COPY .env* ./

# 創建必要的目錄
RUN mkdir -p /app/output /app/logs

# 設定日誌目錄權限
RUN chmod -R 755 /app/logs

# 暴露端口
EXPOSE 30000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:30000/health || exit 1

# 使用啟動腳本
# start.sh 會自動偵測環境（容器內/Docker/本地）並執行對應的啟動流程
CMD ["/app/start.sh"]
