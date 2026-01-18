# 1. 選擇基底映像檔 (就像選擇車子的底盤)
# 我們選用 python 3.9 的輕量版 (slim)，檔案比較小，下載比較快
FROM python:3.9-slim

# 2. 設定工作目錄 (在車子裡劃出一個工作區)
# 之後的指令都會在這個資料夾內執行
WORKDIR /app

# 3. 複製採購清單進去
COPY requirements.txt .

# 4. 安裝依賴套件 (根據清單把東西買齊)
# --no-cache-dir 可以減少映像檔大小
RUN pip install --no-cache-dir -r requirements.txt

# 5. 把你的程式碼 (app.py) 複製進去
COPY app.py .

# 6. 告訴 Docker 這個容器會用到的 Port (僅作為宣告用)
EXPOSE 5000

# 7. 設定容器啟動時要執行的指令 (發動引擎！)
CMD ["python", "app.py"]