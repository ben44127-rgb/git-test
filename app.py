from flask import Flask, request, jsonify # 1. 多引入 jsonify 用來回傳 JSON
from flask_cors import CORS # 2. 引入 CORS 套件

app = Flask(__name__)

# 3. 開啟 CORS，允許所有來源連線 (解決瀏覽器報錯問題)
CORS(app) 

# 4. 修改這裡！把路由改成跟前端一模一樣 '/api/upload-image'
@app.route('/api/upload-image', methods=['POST'])
def upload_file():
    # --- 接收檢查 ---
    if 'file' not in request.files:
        return jsonify({'error': '沒有上傳檔案'}), 400
    
    file = request.files['file']
    user_id = request.form.get('user_id') # 順便示範怎麼拿 user_id
    
    if file.filename == '':
        return jsonify({'error': '檔名是空的'}), 400

    # --- 處理存檔 ---
    save_path = f"./{file.filename}"
    file.save(save_path)
    print(f"收到使用者 {user_id} 的圖片，已儲存至：{save_path}")

    # --- 回傳結果 (配合前端) ---
    # 前端要的是 JSON，且裡面要有 'processed_url' 這個欄位
    # 因為還沒接 AI，我們先假裝回傳原本的檔名給前端顯示
    response_data = {
        "message": "上傳成功",
        "processed_url": "http://假裝我有回傳圖片.com/test.png" 
        # ↑ 之後這裡要換成真的 AI 處理完的圖片網址
    }

    return jsonify(response_data) # 5. 用 jsonify 回傳標準 JSON 格式

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)