import base64
import io
import requests # 用來呼叫 AI 後端
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- 設定 AI 後端的地址 ---
# 注意：如果是 Docker 之間互連，這裡要用 service name 或內網 IP
# 例如：http://ai-service:5000/api/remove_bg
AI_BACKEND_URL = "http://172.17.0.3:5000/api/remove_bg" 

@app.route('/api/upload-image', methods=['POST'])
def process_image():
    # ==========================================
    # 1. 接收前端送來的 Base64 JSON (需求 1 & 2)
    # ==========================================
    try:
        # 檢查是不是 JSON 格式
        data = request.get_json()
        if not data:
            return jsonify({'error': '格式錯誤，請傳送 JSON'}), 400
        
        # 檢查是否有必要的欄位 (前端應該要傳 image_data 和 filename)
        # 假設前端傳來的 JSON 長這樣： { "image_data": "base64字串...", "filename": "photo.png" }
        if 'image_data' not in data or 'filename' not in data:
            return jsonify({'error': '缺少 image_data 或 filename 欄位'}), 400

        image_b64_string = data['image_data']
        filename = data['filename']
        
        # 簡單檢查：如果字串是空的，代表沒資料 (需求 2)
        if not image_b64_string:
            return jsonify({'error': '圖片資料是空的'}), 400

        print(f"收到圖片：{filename}，準備進行解碼...")

    except Exception as e:
        return jsonify({'error': f'資料接收失敗: {str(e)}'}), 400

    # ==========================================
    # 2. 解碼與格式轉換 (中間人處理)
    # ==========================================
    try:
        # 前端傳來的 Base64 有時候會包含 "data:image/png;base64," 這種檔頭，要拿掉才能解碼
        if "," in image_b64_string:
            image_b64_string = image_b64_string.split(",")[1]

        # 將 Base64 字串變回 二進位圖片 (Bytes)
        image_bytes = base64.b64decode(image_b64_string)
        
        # 為了要傳給 AI，我們要把這些 Bytes 偽裝成一個檔案物件
        # io.BytesIO 可以讓變數在記憶體中看起來像個檔案
        image_file = io.BytesIO(image_bytes)

    except Exception as e:
        print(f"解碼失敗: {e}")
        return jsonify({'error': 'Base64 解碼失敗，請確認格式'}), 400

    # ==========================================
    # 3. 轉發給 AI 後端 (需求 3 & 4)
    # ==========================================
    print(f"正在將圖片傳送給 AI 後端 ({AI_BACKEND_URL})...")
    
    try:
        # 準備要寄給 AI 的包裹
        # 格式：'欄位名': ('檔名', 檔案物件, 'MIME類型')
        files_to_send = {
            'file': (filename, image_file, 'image/png')
        }
        
        # 發送 POST 請求給 AI (這裡我們變成 Client)
        ai_response = requests.post(AI_BACKEND_URL, files=files_to_send, timeout=30)
        
        # 檢查 AI 是否成功回應
        if ai_response.status_code == 200:
            print("AI 處理成功！")
            
            # ==========================================
            # 4. 處理 AI 回傳的結果並給前端 (需求 5)
            # ==========================================
            # 假設 AI 回傳的是一張直接的圖片檔案 (Binary)
            # 我們要把它轉成 Base64 回傳給前端顯示，或是直接儲存回傳網址
            
            # 這裡示範：存下來並回傳網址 (比較適合你的前端架構)
            output_filename = f"processed_{filename}"
            with open(output_filename, "wb") as f:
                f.write(ai_response.content)
            
            return jsonify({
                "message": "去背成功",
                "processed_url": f"http://你的IP:5000/download/{output_filename}", 
                "original_filename": filename
            })
            
        else:
            print(f"AI 處理失敗: {ai_response.text}")
            return jsonify({'error': 'AI 伺服器處理失敗'}), 500

    except requests.exceptions.ConnectionError:
        return jsonify({'error': '無法連線到 AI 伺服器，請檢查 Docker 網路'}), 503
    except Exception as e:
        return jsonify({'error': f'轉發過程發生錯誤: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)