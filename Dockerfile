# 使用官方 Python 3.11 作為基礎映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 安裝系統依賴（如果需要）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY manage.py .
COPY config/ config/
COPY api/ api/
COPY .env .

# 創建輸出目錄（用於備援存儲）
RUN mkdir -p /app/output /app/logs

# 暴露端口
EXPOSE 30000

# 運行數據庫遷移（即使不使用數據庫也要運行，避免警告）
RUN python manage.py migrate --noinput

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:30000/health || exit 1

# 啟動 Django 應用
# 使用 gunicorn 作為生產級 WSGI 服務器
CMD ["gunicorn", "--bind", "0.0.0.0:30000", "--workers", "2", "--timeout", "120", "config.wsgi:application"]
