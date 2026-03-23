# 系統功能文檔

> 更新時間: 2026-03-23  
> 說明: test_project 系統完整功能清單及詳細說明

---

## 📋 功能總覽

系統共規劃 **15 個主要功能**，分為以下 **5 個功能模塊**：

| 模塊 | 功能數 | 優先級 |
|------|--------|--------|
| 🔐 **用戶賬戶管理** | 5 | ⭐⭐⭐ 核心功能 |
| 👕 **衣服管理** | 4 | ⭐⭐⭐ 核心功能 |
| 👗 **穿搭管理** | 4 | ⭐⭐⭐ 核心功能 |
| 📸 **圖片和媒體** | 3 | ⭐⭐⭐ 核心功能 |
| 🤖 **AI 功能** | 1 | ⭐⭐ 進階功能 |

---

## 🔐 一、用戶賬戶管理模塊

用戶身份驗證和賬戶相關功能

### 1.1 使用者註冊
- **功能編號**: `ACCOUNT-001`
- **模組**: `accounts`
- **Actor**: `user` (未認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/account/user/register`
- **請求格式**: `application/json`
- **驗證方式**: 無
- **功能說明**: 
  - 允許新用戶建立賬號
  - 需要 email、username、password
  - 密碼需至少 8 個字元
  - Email 需為有效格式且不重複
- **輸入參數**:
  ```json
  {
    "email": "user@example.com",
    "username": "user",
    "password": "mypassword123"
  }
  ```
- **成功回應 (201 Created)**:
  ```json
  {
    "id": 12345,
    "username": "user",
    "email": "user@example.com",
    "date_joined": "2026-01-21T10:00:00Z"
  }
  ```
- **失敗回應**:
  - `400 Bad Request`: 格式錯誤或驗證失敗
  - `409 Conflict`: 帳號已存在

---

### 1.2 使用者登入
- **功能編號**: `ACCOUNT-002`
- **模組**: `accounts`
- **Actor**: `user` (未認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/account/user/login`
- **請求格式**: `application/json`
- **驗證方式**: 無
- **功能說明**:
  - 用戶使用 email/username 和密碼登錄
  - 返回 JWT access token 和 refresh token
  - 用於後續 API 請求的身份驗證
- **輸入參數**:
  ```json
  {
    "username": "user@example.com",
    "password": "mypassword123"
  }
  ```
- **成功回應 (200 OK)**:
  ```json
  {
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": 12345,
      "username": "user",
      "email": "user@example.com"
    }
  }
  ```
- **失敗回應**:
  - `401 Unauthorized`: 帳密錯誤
  - `404 Not Found`: 用戶不存在

---

### 1.3 使用者登出
- **功能編號**: `ACCOUNT-003`
- **模組**: `accounts`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/account/user/logout`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 用戶登出系統
  - 需要提供 refresh token
  - 用於黑名單管理 (可選)
- **輸入參數**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
  }
  ```
- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```
- **成功回應 (200 OK)**:
  ```json
  {
    "detail": "登出成功。"
  }
  ```
- **失敗回應**:
  - `401 Unauthorized`: 驗證失敗或 Token 無效

---

### 1.4 使用者刪除帳號
- **功能編號**: `ACCOUNT-004`
- **模組**: `accounts`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/account/user/delete`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 永久刪除用戶賬號和相關數據
  - 需要用戶確認密碼
  - 刪除後無法恢復
- **輸入參數**:
  ```json
  {
    "password": "mypassword123"
  }
  ```
- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```
- **成功回應 (200 OK)**:
  ```json
  {
    "message": "帳號已刪除"
  }
  ```
- **失敗回應**:
  - `401 Unauthorized`: 未登入
  - `403 Forbidden`: 密碼錯誤

---

### 1.5 使用者上傳模特基本資料
- **功能編號**: `ACCOUNT-005`
- **模組**: `accounts`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/account/user/user_info`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 上傳或更新用戶的身體測量數據
  - 包含身高、體重、臂長、肩寬、腰圍、腿長
  - 用於虛擬試衣參考數據
- **輸入參數**:
  ```json
  {
    "user_height": 180,           // cm
    "user_weight": 70,             // kg
    "user_arm_length": 65,         // cm
    "user_shoulder_width": 45,     // cm
    "user_waistline": 80,          // cm
    "user_leg_length": 105         // cm
  }
  ```
- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```
- **成功回應 (200 OK)**:
  ```json
  {
    "id": 12345,
    "username": "model_user",
    "height": 175,
    "weight": 70,
    "arm_length": 65,
    "shoulder_width": 40,
    "waistline": 80,
    "leg_length": 92,
    "updated_time": "2026-01-22T10:30:45.123456Z"
  }
  ```
- **失敗回應**:
  - `400 Bad Request`: 驗證失敗（超出合理範圍）
  - `401 Unauthorized`: 未授權

---

## 👕 二、衣服管理模塊

衣服資料的設定、查看和管理

### 2.1 設定衣服資料
- **功能編號**: `CLOTHES-001`
- **模組**: `picture`
- **Actor**: `admin` (管理員)
- **HTTP 方法**: `POST` (新增) / `PUT` (更新)
- **API 路徑**: `/picture/clothes/` (新增) 或 `/picture/clothes/{id}/` (更新)
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 管理員添加或編輯衣服資料
  - 包含衣服分類、尺寸數據、圖片 URL、顏色和風格標籤
  - 支持新增多個顏色和風格

**POST 新增衣服 (201 Created)**:
- **輸入參數**:
  ```json
  {
    "clothes_category": "上衣",
    "clothes_arm_length": 60,
    "clothes_shoulder_width": 45,
    "clothes_waistline": 80,
    "clothes_leg_length": 0,
    "clothes_image_url": "http://minio.example.com/clothes.jpg",
    "colors": ["藍色", "紅色"],
    "styles": ["休閒", "正式"]
  }
  ```
- **成功回應**:
  ```json
  {
    "clothes_id": 1,
    "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
    "clothes_category": "上衣",
    "clothes_arm_length": 60,
    "clothes_shoulder_width": 45,
    "clothes_waistline": 80,
    "clothes_leg_length": 0,
    "clothes_image_url": "http://minio.example.com/clothes.jpg",
    "clothes_favorite": false,
    "clothes_created_time": "2026-03-23T16:00:00Z",
    "colors": [{"color_id": 1, "color_name": "藍色"}, {"color_id": 2, "color_name": "紅色"}],
    "styles": [{"style_id": 1, "style_name": "休閒"}, {"style_id": 2, "style_name": "正式"}]
  }
  ```

**PUT 更新衣服 (200 OK)**:
- **路徑**: `/picture/clothes/{id}/`
- **輸入參數**: 同上
- **回應**: 同上

- **失敗回應**:
  - `400 Bad Request`: 數據驗證失敗
  - `403 Forbidden`: 無管理員權限
  - `404 Not Found`: 衣服不存在 (PUT 時)

---

### 2.2 使用者查看衣服總覽列表
- **功能編號**: `CLOTHES-002`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `GET`
- **API 路徑**: `/picture/clothes/`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token` (可選)
- **功能說明**:
  - 顯示系統中所有可用的衣服
  - 支持分頁、篩選
  - 可按分類篩選
- **查詢參數**:
  ```
  GET /picture/clothes/?page=1&category=上衣&limit=20
  ```
- **成功回應 (200 OK)**:
  ```json
  {
    "count": 150,
    "total_pages": 8,
    "current_page": 1,
    "results": [
      {
        "id": 1,
        "name": "藍色短袖T恤",
        "category": "上衣",
        "color": "藍色",
        "thumbnail_url": "http://minio:9000/bucket/clothes_1.png"
      },
      {
        "id": 2,
        "name": "黑色牛仔褲",
        "category": "褲子",
        "color": "黑色",
        "thumbnail_url": "http://minio:9000/bucket/clothes_2.png"
      }
    ]
  }
  ```

---

### 2.3 使用者新增衣服照片
- **功能編號**: `CLOTHES-003`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/picture/clothes/upload_image`
- **請求格式**: `multipart/form-data`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 用戶上傳衣服照片
  - 自動調用 AI 進行背景移除
  - 處理後的圖片存儲到 MinIO
  - 返回去背後的圖片 URL
- **輸入參數**:
  ```
  image_data: <二進位圖片文件>
  filename: "clothes_photo.jpg"
  ```
- **Headers**:
  ```
  Authorization: Bearer <access_token>
  Content-Type: multipart/form-data
  ```
- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "message": "圖片處理和儲存成功",
    "processed_url": "http://192.168.233.128:9000/bucket/processed_image.png",
    "ai_status": {
      "status_code": 200,
      "message": "去背成功"
    }
  }
  ```
- **失敗回應**:
  - `400 Bad Request`: 檔案驗證失敗
  - `503 Service Unavailable`: AI 服務不可用

---

### 2.4 使用者查看喜歡的衣服/穿搭列表
- **功能編號**: `CLOTHES-004`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `GET`
- **API 路徑**: `/picture/clothes/favorites`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 獲取用戶標註喜歡的所有衣服和穿搭
  - 支持分頁
  - 顯示喜歡的時間
- **查詢參數**:
  ```
  GET /picture/clothes/favorites?page=1&type=clothes
  ```
- **Headers**:
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **成功回應 (200 OK)**:
  ```json
  {
    "count": 5,
    "results": [
      {
        "clothes_id": 1,
        "clothes_category": "上衣",
        "clothes_image_url": "http://minio:9000/bucket/image.png",
        "favorited_at": "2026-01-22T10:30:45Z"
      }
    ]
  }
  ```
- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期
  - `500 Internal Server Error`: 伺服器內部錯誤

---

## 👗 三、穿搭管理模塊

穿搭組合的創建、管理和查看

### 3.1 使用者查看穿搭總覽列表
- **功能編號**: `OUTFIT-001`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `GET`
- **API 路徑**: `/picture/outfit/`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token` (可選)
- **功能說明**:
  - 顯示系統中所有穿搭組合
  - 支持按季節、風格、評分篩選
  - 支持搜索和排序
- **查詢參數**:
  ```
  GET /picture/outfit/?page=1&season=春季&style=休閒&limit=20
  ```
- **成功回應 (200 OK)**:
  ```json
  {
    "count": 45,
    "results": [
      {
        "id": 1,
        "name": "春日休閒風格",
        "season": "春季",
        "style": "休閒",
        "clothes_count": 3,
        "outfit_image": "http://minio:9000/bucket/outfit_1.png",
        "rating": 4.5,
        "creator": "fashion_expert"
      }
    ]
  }
  ```

---

### 3.2 使用者新增穿搭組合
- **功能編號**: `OUTFIT-002`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/picture/outfit/`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 用戶創建新的穿搭組合
  - 選擇多件衣服進行組合
  - 添加穿搭名稱、描述、標籤
- **輸入參數**:
  ```json
  {
    "name": "我的春日穿搭",
    "description": "舒適又時尚的春季搭配",
    "season": "春季",
    "style": "休閒",
    "clothes_ids": [1, 5, 12],
    "tags": ["春季", "休閒", "甜美"]
  }
  ```
- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```
- **成功回應 (201 Created)**:
  ```json
  {
    "id": 100,
    "name": "我的春日穿搭",
    "season": "春季",
    "created_by": "user_id",
    "created_at": "2026-01-22T10:30:45Z",
    "clothes": [
      {"id": 1, "name": "藍色短袖T恤"},
      {"id": 5, "name": "白色長褲"},
      {"id": 12, "name": "米色外套"}
    ]
  }
  ```

---

### 3.3 使用者儲存當前穿搭
- **功能編號**: `OUTFIT-003`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/picture/outfit/{outfit_id}/save` 或 `/picture/outfit/save_current`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 保存用戶當前正在編輯/試穿的穿搭
  - 支持將虛擬試衣結果保存為穿搭
  - 生成穿搭預覽圖
- **輸入參數**:
  ```json
  {
    "name": "正在試穿的搭配",
    "clothes_ids": [1, 5, 12],
    "preview_image": "base64_encoded_image_data or url",
    "is_draft": false
  }
  ```
- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```
- **成功回應 (201 Created)**:
  ```json
  {
    "id": 101,
    "name": "正在試穿的搭配",
    "status": "saved",
    "preview_url": "http://minio:9000/bucket/outfit_preview.png",
    "saved_at": "2026-01-22T10:35:20Z"
  }
  ```

---

### 3.4 使用者與各穿搭互動
- **功能編號**: `OUTFIT-004`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST / DELETE`
- **API 路徑**: `/picture/outfit/{outfit_id}/like` 或 `/picture/outfit/{outfit_id}/unlike`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 用戶可以喜歡或取消喜歡穿搭
  - 喜歡的穿搭會顯示在收藏列表
  - 支持評分和評論
- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```
- **成功回應 (200 OK)**:
  ```json
  {
    "id": 100,
    "name": "春日休閒風格",
    "is_liked": true,
    "like_count": 256,
    "current_rating": 4.5
  }
  ```

---

## 📸 四、圖片和媒體模塊

用戶照片上傳和圖片管理

### 4.1 使用者上傳模特照片
- **功能編號**: `MEDIA-001`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/picture/user/user_picture`
- **請求格式**: `multipart/form-data`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 用戶上傳自己的照片
  - 自動調用 AI 進行背景移除
  - 用於虛擬試衣的模特圖片
  - 可以設定為頭像或背景
- **輸入參數**:
  ```
  photo_file: <二進位圖片檔案> (max 10MB)
  photo_type: "avatar" | "background" | "full_body"
  ```
- **Headers**:
  ```
  Authorization: Bearer <token>
  Content-Type: multipart/form-data
  ```
- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "message": "照片上傳和去背完成",
    "photo": {
      "id": 123,
      "status": "completed",
      "original_url": "http://minio:9000/bucket/original.jpg",
      "removed_bg_url": "http://minio:9000/bucket/removed_bg.png",
      "uploaded_at": "2026-01-22T10:30:45Z"
    }
  }
  ```
- **失敗回應**:
  - `400 Bad Request`: 檔案驗證失敗或檔案過大 (>10MB)
  - `401 Unauthorized`: Token 無效
  - `503 Service Unavailable`: AI 服務不可用

---

### 4.2 使用者上傳圖片 (通用)
- **功能編號**: `MEDIA-002`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/picture/upload/` (通用上傳端點)
- **請求格式**: `multipart/form-data`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 通用圖片上傳功能
  - 支持多種圖片格式 (JPG, PNG, GIF, WebP)
  - 自動生成縮略圖
  - 可用於穿搭、收藏等多種場景
- **輸入參數**:
  ```
  image: <二進位圖片檔案>
  image_type: "clothes" | "outfit" | "inspiration" | "user_photo"
  title: "圖片標題"
  description: "詳細描述"
  ```
- **成功回應 (201 Created)**:
  ```json
  {
    "id": 456,
    "image_type": "inspiration",
    "original_url": "http://minio:9000/bucket/inspiration.jpg",
    "thumbnail_url": "http://minio:9000/bucket/inspiration_thumb.jpg",
    "uploaded_at": "2026-01-22T10:40:00Z"
  }
  ```

---

### 4.3 圖片管理 (其他操作)
- **功能編號**: `MEDIA-003`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `GET / DELETE / PUT`
- **API 路徑**: `/picture/media/{media_id}/`
- **功能說明**:
  - 查看、編輯、刪除已上傳的圖片
  - 設定公開/私密
  - 移動到不同分類
  - 管理圖片元數據

---

## 🤖 五、AI 功能模塊

AI 相關的智能功能

### 5.1 使用者與 AI 文字對話
- **功能編號**: `AI-001`
- **模組**: `picture` 或 `ai_service` (新模組)
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/ai/chat` 或 `/picture/ai/chat`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 用戶可以與 AI 進行文字對話
  - AI 提供穿搭建議、風格諮詢
  - 基於用戶的身體數據和偏好進行推薦
  - 使用 Gemini API 進行自然語言處理
- **輸入參數**:
  ```json
  {
    "message": "我想要春季休閒風的穿搭建議，我的身高 180cm，體重 70kg",
    "context": "outfit_recommendation" | "style_advice" | "general",
    "previous_messages": []
  }
  ```
- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```
- **成功回應 (200 OK)**:
  ```json
  {
    "conversation_id": "conv_123456",
    "ai_response": "根據您的身材數據和風格偏好，我建議：1. 選擇寬鬆版型的T恤，可以凸顯肩線... 2. 搭配九分褲或直筒褲可以拉長腿型... 3. 建議色系：米色、淺藍、白色...",
    "suggested_clothes": [
      {"id": 1, "name": "藍色短袖T恤", "match_score": 0.95},
      {"id": 5, "name": "白色長褲", "match_score": 0.92}
    ],
    "timestamp": "2026-01-22T10:45:00Z"
  }
  ```
- **失敗回應**:
  - `401 Unauthorized`: Token 無效
  - `429 Too Many Requests`: 請求過於頻繁
  - `503 Service Unavailable`: AI 服務不可用

---

## 📊 功能矩陣表

| # | 功能名稱 | 模組 | Actor | HTTP 方法 | 優先級 | 狀態 | API 端點 |
|---|---------|------|-------|----------|--------|------|---------|
| 1 | 使用者註冊 | accounts | user | POST | ⭐⭐⭐ | ✅ | `/account/user/register` |
| 2 | 使用者登入 | accounts | user | POST | ⭐⭐⭐ | ✅ | `/account/user/login` |
| 3 | 使用者登出 | accounts | user | POST | ⭐⭐⭐ | ✅ | `/account/user/logout` |
| 4 | 使用者刪除帳號 | accounts | user | POST | ⭐⭐ | ✅ | `/account/user/delete` |
| 5 | 上傳模特基本資料 | accounts | user | POST | ⭐⭐⭐ | 🔄 | `/account/user/user_info` |
| 6 | 設定衣服資料 | picture | admin | POST/PUT | ⭐⭐⭐ | ✅ | `/picture/clothes/` |
| 7 | 查看衣服總覽列表 | picture | user | GET | ⭐⭐⭐ | ⏳ | `/picture/clothes/` |
| 8 | 新增衣服照片 | picture | user | POST | ⭐⭐⭐ | ✅ | `/picture/clothes/upload_image` |
| 9 | 查看喜歡的衣服 | picture | user | GET | ⭐⭐ | ✅ | `/picture/clothes/favorites` |
| 10 | 查看穿搭總覽列表 | picture | user | GET | ⭐⭐⭐ | ⏳ | `/picture/outfit/` |
| 11 | 新增穿搭組合 | picture | user | POST | ⭐⭐⭐ | ⏳ | `/picture/outfit/` |
| 12 | 儲存當前穿搭 | picture | user | POST | ⭐⭐⭐ | ⏳ | `/picture/outfit/save_current` |
| 13 | 上傳模特照片 | picture | user | POST | ⭐⭐⭐ | ✅ | `/picture/user/user_picture` |
| 14 | 上傳圖片 (通用) | picture | user | POST | ⭐⭐ | ⏳ | `/picture/upload/` |
| 15 | AI 文字對話 | picture/ai | user | POST | ⭐⭐ | 🔄 | `/ai/chat` |

**狀態說明:**
- ✅ 已完成
- 🔄 進行中
- ⏳ 計劃中

---

## 🔄 功能流程圖

### 用戶完整使用流程

```
1. 用戶註冊和登入
   ├─ 註冊 (register) ✅
   ├─ 登入 (login) ✅
   └─ 獲得 JWT Token

2. 完善用戶資料
   ├─ 上傳身體測量數據 (user_info) 🔄
   └─ 上傳模特照片 (user_picture) ✅

3. 瀏覽衣服
   ├─ 查看衣服列表 (clothes list) ⏳
   ├─ 查看衣服詳情
   └─ 標記喜歡的衣服 (favorites) ✅

4. 虛擬試衣
   ├─ 上傳衣服圖片 (upload_image) ✅
   │  └─ 調用 AI 去背
   ├─ 組合穿搭 (create outfit) ⏳
   └─ 儲存穿搭 (save outfit) ⏳

5. AI 諮詢
   ├─ 文字對話 (AI chat) 🔄
   ├─ 獲得穿搭建議
   └─ 推薦衣服

6. 查看和管理
   ├─ 查看穿搭列表 (outfit list) ⏳
   ├─ 查看收藏列表 (favorites) ✅
   └─ 編輯和刪除

7. 登出
   └─ 登出系統 (logout) ✅
```

### 管理員衣服管理流程 ✨ 新增

```
【後台管理員流程】
1. 管理員登入
   └─ 使用管理員帳號登入 ✅

2. 衣服管理 (CRUD)
   ├─ 新增衣服 (POST /picture/clothes/) ✅
   │  ├─ 設定衣服分類 (category)
   │  ├─ 設定尺寸數據 (arm_length, shoulder_width 等)
   │  ├─ 上傳衣服圖片 URL
   │  ├─ 添加顏色標籤 (colors)
   │  └─ 添加風格標籤 (styles)
   ├─ 查看衣服列表 (GET /picture/clothes/) ✅
   │  └─ 支持分頁和分類篩選
   ├─ 查看衣服詳情 (GET /picture/clothes/{id}/) ✅
   │  └─ 包含所有顏色和風格信息
   ├─ 更新衣服 (PUT /picture/clothes/{id}/) ✅
   │  └─ 修改分類、尺寸、顏色、風格等
   └─ 刪除衣服 (DELETE /picture/clothes/{id}/) ✅
      └─ 自動刪除相關顏色和風格

3. 衣服數據檢查
   └─ 確保衣服數據完整和正確
```

---

## 📝 開發優先級建議

### 第一階段（核心功能）- 即時開發
1. ✅ 使用者註冊
2. ✅ 使用者登入
3. ✅ 使用者登出
4. ✅ 使用者上傳衣服圖片 + AI 去背
5. ✅ 使用者上傳模特照片 + AI 去背

### 第二階段（基礎管理）- 1-2 週
6. 🔄 上傳模特基本資料（身體數據）
7. ⏳ 查看衣服總覽列表 (GET `/picture/clothes/`)
8. ✅ 設定衣服資料（後台管理）[剛完成!]
9. ✅ 查看收藏列表

### 第三階段（穿搭功能）- 2-4 週
10. ⏳ 新增穿搭組合
11. ⏳ 儲存穿搭
12. ⏳ 查看穿搭列表

### 第四階段（增強功能）- 4-8 週
13. 🔄 AI 文字對話
14. ⏳ 通用圖片上傳
15. ⏳ 圖片管理功能

---

## 🔐 權限管理

### 角色權限對照表

| 功能 | 匿名用戶 | 認證用戶 | 管理員 |
|------|---------|---------|--------|
| 註冊 | ✅ | ❌ | ❌ |
| 登入 | ✅ | ❌ | ✅ |
| 登出 | ❌ | ✅ | ✅ |
| 查看衣服列表 | ✅ | ✅ | ✅ |
| 上傳圖片 | ❌ | ✅ | ✅ |
| 設定衣服資料 | ❌ | ❌ | ✅ |
| 刪除用戶 | ❌ | ⚠️ (自己) | ✅ |
| AI 對話 | ❌ | ✅ | ✅ |

---

## 📞 API 版本

- **當前版本**: v1
- **API 基礎 URL**: `http://localhost:30000/api/v1/`
- **WebSocket 支持**: 計劃在 v2
- **向後兼容**: v1 API 不會中斷

---

> 最後更新：2026-03-23  
> 下次審查：2026-04-23
