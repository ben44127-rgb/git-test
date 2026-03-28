# 系統功能文檔

> 更新時間: 2026-03-28  
> 說明: test_project 系統完整功能一覽及詳細說明
> 最新更新: 數據庫優化 - 刪除 outfit/outfit_clothes/virtual_try_on/outfit_favorite 冗餘表，保留虛擬試穿核心功能（Feature 3.1）

---

## 📋 功能總覽

系統共規劃 **9 個主要功能**，分為以下 **4 個功能模塊**：

| 模塊 | 功能數 | 優先級 |
|------|--------|--------|
| 🔐 **用戶賬戶管理** | 5 | ⭐⭐⭐ 核心功能 |
| � **照片管理** | 5 | ⭐⭐⭐ 核心功能 |
| **虛擬試穿** | 4 | ⭐⭐⭐ 核心功能 |
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

## 📸 二、照片管理模塊

用戶照片和衣伺資料的上傳、查看和管理（包括：衣伺圖片、用戶模特照片）

### 2.1 用戶新增衣伺（上傳圖片 + AI 處理）
- **功能編號**: `CLOTHES-001`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/picture/clothes/` ⭐ (統一端點)
- **請求格式**: `multipart/form-data`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 用戶上傳衣伺**圖片** + **衣伺尺寸信息**
  - 支持可選的衣伺尺寸參數：袖長、褲長、肩寬、腰圍
  - 後端自動轉發給 AI 進行去背處理，包含尺寸參數
  - AI 自動分析並提取：衣伺分類、顏色、風格
  - 處理後的圖片存儲到 MinIO，返回 URL
  - 將完整信息（包括衣伺尺寸）存儲到數據庫
  - 用戶無需手動輸入顏色和風格（由 AI 自動提取）

**流程說明**:
```
① 用戶上傳圖片 + 衣伺尺寸 (袖長、褲長、肩寬、腰圍)
    ↓
② 後端驗證衣伺尺寸參數範圍
    ↓
③ 後端轉發給 AI 後端進行去背處理（包含尺寸）
    ↓
④ AI 返回：
   - 去背後的圖片
   - 衣伺分類（clothes_category）
   - 風格列表（style_name x 3）
   - 顏色列表（color_name x 3）
    ↓
⑤ 後端將圖片存儲到 MinIO
    ↓
⑥ 將完整數據存儲到 DB：
   - Clothes 表：基本信息 + 圖片 URL + 衣伺尺寸
   - Style 表：3 筆風格
   - Color 表：3 筆顏色
    ↓
⑦ 返回完整的衣伺詳情給前端（包含尺寸數據）
```

- **輸入參數** (form-data):
  ```json
  {
    "image_data": {
      "type": "file (binary)",
      "required": true,
      "description": "衣伺圖片檔案（二進位數據）",
      "accepted_formats": ["JPG", "PNG", "GIF", "WebP"],
      "max_size": "10MB"
    },
    "clothes_arm_length": {
      "type": "integer",
      "required": false,
      "default": 0,
      "range": [0, 200],
      "unit": "cm",
      "description": "衣伺袖長（衣伺的胳膊長度）"
    },
    "clothes_leg_length": {
      "type": "integer",
      "required": false,
      "default": 0,
      "range": [0, 150],
      "unit": "cm",
      "description": "衣伺褲長（衣伺的褲子長度）"
    },
    "clothes_shoulder_width": {
      "type": "integer",
      "required": false,
      "default": 0,
      "range": [0, 200],
      "unit": "cm",
      "description": "衣伺肩寬（衣伺肩膀的寬度）"
    },
    "clothes_waistline": {
      "type": "integer",
      "required": false,
      "default": 0,
      "range": [0, 300],
      "unit": "cm",
      "description": "衣伺腰圍（衣伺腰部的圓周）"
    }
  }
  ```

  **📝 參數說明**:
  - **必填參數**: `image_data` (衣伺圖片檔案)
  - **可選參數**: `clothes_arm_length`, `clothes_leg_length`, `clothes_shoulder_width`, `clothes_waistline` (所有尺寸參數不提供時預認為 0)
  - 衣伺尺寸參數必須是 **非負整數**，超出範圍將返回 400 Bad Request
  - 衣伺尺寸數據會被發送給 AI 後端進行智能處理
  - 衣伺尺寸數據會被持久化存儲在數據庫中

- **Headers** 🔐:
  ```
  Authorization: Bearer <access_token>          // ⭐ JWT Token - 必填，用於識別用戶身份
  Content-Type: multipart/form-data
  ```
  
  **認證說明**: 使用 JWT Bearer Token 進行身份驗證
  - 從登入端點獲得的 `access_token`
  - 後端自動從 Token 中提取用戶信息（user_uid、user_id 等）
  - **不需要** 在表單參數中提供 `user_uid`

- **成功回應 (201 Created / 200 OK)**:
  ```json
  {
    "success": true,
    "message": "圖片處理和儲存成功",
    "processed_url": "http://192.168.233.128:9000/processed-images/unique_id_cleaned.png",
    "ai_status": {
      "status_code": 200,
      "message": "Processing Success",
      "tools_status": {
        "rembg_engine": "success",
        "opencv_masking": "success",
        "gemini_consultant": "success"
      }
    },
    "storage_status": {
      "success": true,
      "filename": "unique_id_cleaned_garment.png",
      "file_name": "cleaned_garment.png",
      "file_format": "PNG",
      "storage": "minio",
      "bucket": "processed-images",
      "public_url": "http://192.168.233.128:9000/processed-images/...",
      "signed_url": "http://192.168.233.128:9000/processed-images/...?X-Amz..."
    },
    "clothes_data": {
      "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
      "clothes_category": "T-shirt",
      "styles": ["Casual", "Formal", "Streetwear"],
      "colors": ["red", "blue", "green"],
      "image_url": "http://192.168.233.128:9000/processed-images/...",
      "clothes_measurements": {
        "arm_length": 65,           // 衣伺袖長（cm）
        "leg_length": 92,           // 衣伺褲長（cm）
        "shoulder_width": 45,       // 衣伺肩寬（cm）
        "waistline": 80             // 衣伺腰圍（cm）
      }
    }
  }
  ```

- **失敗回應**:
  - `400 Bad Request`: 缺少圖片、檔案驗證失敗或衣伺尺寸參數無效
    ```json
    {
      "success": false,
      "message": "請上傳圖片檔案（欄位名稱：image_data）"
    }
    ```
    或
    ```json
    {
      "success": false,
      "message": "衣伺尺寸參數必須為整數"
    }
    ```
    或
    ```json
    {
      "success": false,
      "message": "衣伺袖長必須在 0 到 200 cm 之間"
    }
    ```
  - `401 Unauthorized`: 未認證或 Token 過期
  - `415 Unsupported Media Type`: 上傳非圖片檔案
  - `422 Unprocessable Entity`: 圖片過於模糊
  - `503 Service Unavailable`: AI 伺務或存儲伺務不可用
  - `504 Gateway Timeout`: AI 處理逾時（超過 120 秒）

**📊 統一端點 CRUD 操作表** ⭐ 所有衣伺操作都經由同一端點：

| HTTP 方法 | API 路徑 | 操作 | 身份要求 | 返回狀態碼 |
|----------|---------|------|---------|----------|
| **POST** | `/picture/clothes/` | ✏️ 新增衣伺 | 認證用戶 | 201 |
| **GET** | `/picture/clothes/my` | 📋 查看我的衣伺 | 認證用戶 | 200 |
| **GET** | `/picture/clothes/<id>/` | 👁️ 查看衣伺詳情 | 認證用戶 | 200 |
| **PUT** | `/picture/clothes/<id>/` | ✏️ 更新衣伺 | 擁有者/管理員 | 200 |
| **DELETE** | `/picture/clothes/<id>/` | 🗑️ 刪除衣伺 | 擁有者/管理員 | 200 |

**✅ 確認：統一端點 `/picture/clothes/` 可以完整支持衣伺的 CRUD 操作**

**📏 衣伺尺寸參數驗證規則**:

| 參數名 | 範圍 | 預認值 | 說明 |
|-------|------|--------|------|
| `clothes_arm_length` | 0-200 cm | 0 | 衣伺袖長，不能為負數 |
| `clothes_leg_length` | 0-150 cm | 0 | 衣伺褲長，不能為負數 |
| `clothes_shoulder_width` | 0-200 cm | 0 | 衣伺肩寬，不能為負數 |
| `clothes_waistline` | 0-300 cm | 0 | 衣伺腰圍，不能為負數 |

**✅ 驗證流程**:
1. 將參數轉換為整數，若非整數格式則返回 400 Bad Request
2. 檢查是否在允許的範圍內，若超出範圍則返回 400 Bad Request
3. 所有參數都是可選的，可完全不提供或只提供部分參數
4. 不提供時預認為 0，系統仍然正常處理

---

### 2.2 用戶查看喜歡的衣伺/穿搭列表
- **功能編號**: `CLOTHES-003`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `GET`
- **API 路徑**: `/picture/clothes/favorites`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 獲取用戶標註喜歡的所有衣伺和穿搭
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
  - `500 Internal Server Error`: 伺伺器內部錯誤

#### 2.2.1 標記衣伺為喜歡
**功能編號**: `CLOTHES-003-MARK`  
**HTTP 方法**: `PATCH`  
**API 路徑**: `/picture/clothes/<clothes_uid>/favorite`

- **輸入參數** (JSON):
  ```json
  {
    "favorite": true  // true 表示喜歡，false 表示取消喜歡
  }
  ```

- **Headers**:
  ```
  Authorization: Bearer <JWT_TOKEN>
  Content-Type: application/json
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "message": "已標記為喜歡",
    "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
    "clothes_favorite": true
  }
  ```
  或取消喜歡時：
  ```json
  {
    "success": true,
    "message": "已取消喜歡",
    "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
    "clothes_favorite": false
  }
  ```

- **失敗回應**:
  - `400 Bad Request`: 缺少 favorite 參數
  - `401 Unauthorized`: Token 無效或過期
  - `404 Not Found`: 衣伺不存在
  - `500 Internal Server Error`: 伺伺器內部錯誤

**📊 快速參考表** ⭐ 衣伺收藏相關操作：

| 操作 | HTTP 方法 | API 路徑 | 身份要求 | 返回狀態碼 |
|------|----------|---------|---------|----------|
| 查看喜歡的衣伺 | GET | `/picture/clothes/favorites` | 認證用戶 | 200 |
| 標記為喜歡 | PATCH | `/picture/clothes/<id>/favorite` | 認證用戶 | 200 |
| 取消喜歡 | PATCH | `/picture/clothes/<id>/favorite` | 認證用戶 | 200 |

**🔄 工作流程**：

```
1. 用戶查看衣伺詳情
   ├─ GET /picture/clothes/<id>/
   └─ 獲得完整的衣伺信息（包含 clothes_favorite 當前狀態）

2. 標記為喜歡
   ├─ PATCH /picture/clothes/<id>/favorite
   ├─ Body: {"favorite": true}
   └─ 返回成功狀態

3. 查看所有喜歡的衣伺
   ├─ GET /picture/clothes/favorites
   ├─ 支持分頁 (?page=1&limit=20)
   └─ 返回標記為喜歡的衣伺列表

4. 取消喜歡
   ├─ PATCH /picture/clothes/<id>/favorite
   ├─ Body: {"favorite": false}
   └─ 返回成功狀態
```

---

### 2.3 用戶模特照片管理
- **功能編號**: `PHOTO-001`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **API 路徑**: `/picture/user/photo` ⭐ (統一端點)
- **驗證方式**: `JWT Bearer Token`
- **狀態**: ✅ 已實現
- **功能說明**:
  - 用戶上傳和管理虛擬試穿用的模特照片
  - 自動更新用戶的 `user_image_url` 字段（虛擬試穿的必須數據）
  - 支持 JPG、PNG、GIF、WebP 格式
  - 最大檔案 10MB
  - 自動存儲到 MinIO
  - 一個用戶同時只有一張活跃的模特照片，上傳新照片會覆蓋舊照片

**流程說明**:
```
① 用戶選擇並上傳模特照片檔案
    ↓
② 後端驗證檔案格式和大小
    ↓
③ 上傳到 MinIO 存儲
    ↓
④ 生成 MinIO URL
    ↓
⑤ 更新用戶 user_image_url 字段（用於虛擬試穿）
    ↓
⑥ 返回照片 URL 和用戶信息
```

**⚠️ 重要說明**:
- 這個照片是虛擬試穿的必須數據，存儲在 User 表的 `user_image_url` 字段
- 虛擬試穿會自動讀取用戶的 `user_image_url`，如未設定則返回400錯誤
- 一個用戶只能有一張當前活跃的模特照片

#### 2.3.1 上傳模特照片
**HTTP 方法**: `POST`
**API 路徑**: `/picture/user/photo`

- **輸入參數** (form-data):
  ```
  photo_file: <二進位圖片檔案> (JPG, PNG, GIF, WebP，最大 10MB)
  ```

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  Content-Type: multipart/form-data
  ```

- **成功回應 (201 Created / 200 OK)**:
  ```json
  {
    "success": true,
    "message": "模特照片上傳成功，已自動更新為虛擬試穿用的模特照片",
    "photo_data": {
      "photo_url": "http://minio.example.com/bucket/user_uuid_photo_timestamp.png",
      "uploaded_at": "2026-03-28T10:00:00Z",
      "note": "此照片已保存為用戶的虛擬試穿模特照片"
    },
    "user": {
      "user_uid": "550e8400-e29b-41d4-a716-446655440000",
      "user_name": "john_doe",
      "user_image_url": "http://minio.example.com/bucket/user_uuid_photo_timestamp.png",
      "updated_at": "2026-03-28T10:00:00Z"
    }
  }
  ```

- **失敗回應**:
  - `400 Bad Request`: 缺少檔案參數或檔案過大
  - `401 Unauthorized`: Token 無效或過期
  - `415 Unsupported Media Type`: 不支持的檔案類型 (僅接受 JPG、PNG、GIF、WebP)
  - `503 Service Unavailable`: MinIO 存儲伺務不可用
  - `500 Internal Server Error`: 伺伺器內部錯誤

**📝 操作說明**:
- 用於**首次上傳**模特照片
- 上傳照片會保存為用戶的虛擬試穿模特照片
- 新的 `user_image_url` 會立即用於虛擬試穿功能
- 推薦上傳全身照以獲得最佳虛擬試穿效果
- 如需更新已上傳的照片，請使用 PUT 方法（見 2.3.2.1）

---

#### 2.3.2 更新或查看模特照片

##### 2.3.2.1 更新模特照片
**HTTP 方法**: `PUT`
**API 路徑**: `/picture/user/photo`

- **輸入參數** (form-data):
  ```
  photo_file: <二進位圖片檔案> (JPG, PNG, GIF, WebP，最大 10MB)
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
    "message": "模特照片更新成功，已自動更新為虛擬試穿用的模特照片",
    "photo_data": {
      "photo_url": "http://minio.example.com/bucket/user_uuid_photo_timestamp.png",
      "uploaded_at": "2026-03-28T10:00:00Z",
      "note": "此照片已保存為用戶的虛擬試穿模特照片"
    },
    "user": {
      "user_uid": "550e8400-e29b-41d4-a716-446655440000",
      "user_name": "john_doe",
      "user_image_url": "http://minio.example.com/bucket/user_uuid_photo_timestamp.png",
      "updated_at": "2026-03-28T10:00:00Z"
    }
  }
  ```

- **失敗回應**:
  - `400 Bad Request`: 缺少檔案參數或檔案過大
  - `401 Unauthorized`: Token 無效或過期
  - `415 Unsupported Media Type`: 不支持的檔案類型 (僅接受 JPG、PNG、GIF、WebP)
  - `503 Service Unavailable`: MinIO 存儲伺務不可用
  - `500 Internal Server Error`: 伺伺器內部錯誤

**📝 操作說明**:
- 更新照片會自動覆蓋舊照片（替換 `user_image_url`）
- 新的 `user_image_url` 會立即用於虛擬試穿功能
- 推薦上傳全身照以獲得最佳虛擬試穿效果

---

##### 2.3.2.2 查看當前模特照片
**HTTP 方法**: `GET`
**API 路徑**: `/picture/user/photo`

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "message": "模特照片獲取成功",
    "photo_data": {
      "photo_url": "http://minio.example.com/bucket/user_uuid_photo_timestamp.png",
      "uploaded_at": "2026-03-27T16:00:00Z"
    },
    "user": {
      "user_uid": "550e8400-e29b-41d4-a716-446655440000",
      "user_name": "john_doe",
      "user_image_url": "http://minio.example.com/bucket/user_uuid_photo_timestamp.png"
    }
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期
  - `404 Not Found`: 用戶未上傳模特照片（user_image_url 為空）
  - `500 Internal Server Error`: 伺伺器內部錯誤

**📝 說明**:
- 如果用戶未上傳照片，返回 404 且提示「未設定模特照片」
- 前端應該在虛擬試穿前檢查此端點，確認照片已設定

---

**📊 操作表** ⭐ 用戶模特照片管理：

| HTTP 方法 | API 路徑 | 操作 | 說明 | 返回狀態碼 |
|----------|---------|------|------|----------|
| **POST** | `/picture/user/photo` | ⬆️ 上傳照片 | 首次上傳模特照片並保存 user_image_url | 201/200 |
| **PUT** | `/picture/user/photo` | 🔄 更新照片 | 更新現有的模特照片，覆蓋舊照片 | 200 |
| **GET** | `/picture/user/photo` | 👁️ 查看當前照片 | 查看當前的模特照片 URL | 200 |

**✅ 確認設計**:
- 支持 3 種操作：上傳、更新和查看
- 一個用戶同時只有 1 張活跃的模特照片
- POST 用於初次上傳，PUT 用於後續更新
- 上傳或更新照片會覆蓋舊照片（實現自動更新）
- 虛擬試穿會自動讀取 user_image_url，無須額外操作

---

##  三、虛擬試穿模塊

使用者透過自己衣櫃內既有衣伺，挑選 2 件衣伺進行虛擬試穿。後端接收請求後，從資料庫讀取衣伺與模特資料，組裝成 AI 後端要求的格式，取得合併結果後直接保存到 Model 表。

**📌 重要說明**：虛擬試穿為核心功能（Feature 3.1），重點在請求組裝、AI 整合、結果保存（Model 表）與歷史查詢。

### 3.1 使用者發起虛擬試穿（選取 2 件衣伺）
- **功能編號**: `TRYON-001`
- **模組**: `combine`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/combine/user/virtual-try-on`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 使用者從自己資料庫既有衣伺中選取 2 件進行試穿
  - 後端查詢 2 件衣伺圖片與尺寸資料
  - 後端使用使用者個人檔案中的模特照片（`user_image_url`）與身體測量資料
  - 後端打包並轉發給 AI 後端進行合併試穿
  - 後端解析 AI 回傳並保存試穿結果

**流程說明**:
```
① 前端送出試穿請求（2 件衣伺）
    ↓
② 後端驗證衣伺數量與歸屬權限
    ↓
③ 後端查詢衣伺資料 + 使用者模特照片（user_image_url） + 身體測量
    ↓
④ 後端組裝 multipart/form-data 並呼叫 AI
    ↓
⑤ AI 回傳 multipart/mixed（JSON + PNG）
    ↓
⑥ 後端解析回應，保存圖片與 metadata
    ↓
⑦ 回傳試穿結果給前端
```

- **輸入參數** (JSON):
  ```json
  {
    "clothes_ids": [
      "550e8400-e29b-41d4-a716-446655440010",
      "550e8400-e29b-41d4-a716-446655440011"
    ]
  }
  ```

  **📝 參數說明**:
  - **必填參數**: `clothes_ids`（必須恰好 2 件）
  - `clothes_ids` 中衣伺必須存在，且必須屬於當前使用者
  - **模特照片來源**: 直接使用用戶個人檔案的 `user_image_url`（需要先在用戶資料中設定）
  - 如果未設定 `user_image_url`，虛擬試穿請求會失敗，需引導用戶先上傳模特照片

- **Headers** 🔐:
  ```
  Authorization: Bearer <access_token>
  Content-Type: application/json
  ```

#### 3.1.1 模特照片設定說明

使用者必須先上傳模特照片（設定 `user_image_url`），虛擬試穿功能才能正常運作：

- **相關 API**: `PHOTO-001` - 功能 2.3 用戶模特照片管理（API 路徑：`/picture/user/photo`）
- **設定方式**: 透過 POST `/picture/user/photo` 上傳模特照片，自動設定 `user_image_url` 字段
- **確認方式**: 用 GET `/picture/user/photo` 查看當前模特照片是否已設定
- **如未設定**: 虛擬試穿請求會返回 `400 Bad Request`，提示「用戶未設定模特照片」

#### 3.1.2 後端送給 AI 的資料格式

後端會組裝以下格式的請求轉發給 AI 後端：

- **請求格式**: `multipart/form-data`
- **Files 參數**:
  ```json
  {
    "model_image": "<二進位模特照片檔案>",
    "garment_0": "<二進位衣伺圖片1>",
    "garment_1": "<二進位衣伺圖片2>"
  }
  ```

- **Data 參數** (JSON):
  ```json
  {
    "model_info": {
      "user_height": 175.0,
      "user_weight": 70,
      "user_shoulder_width": 42.5,
      "user_arm_length": 60,
      "user_waistline": 80,
      "user_leg_length": 100
    },
    "garments": [
      {
        "clothes_category": "clothing",
        "garment_info": {
          "clothes_arm_length": 68.0,
          "clothes_shoulder_width": 48.0
        }
      },
      {
        "clothes_category": "bottom",
        "garment_info": {
          "clothes_leg_length": 100.0,
          "clothes_waistline": 100.0
        }
      }
    ]
  }
  ```

---

#### 3.1.3 AI 回傳資料格式

- **回傳格式**: `multipart/mixed`
- **回傳內容**: 
  - 第 1 段：JSON metadata（AI 處理結果）
  - 第 2 段：PNG 圖片二進位數據

**JSON Metadata 回應** (200 OK):
```json
{
  "code": 200,
  "message": "200",
  "data": {
    "file_name": "try_on_outfit_20260328.png",
    "file_format": "PNG",
    "style_name": [
      "Japanese Style",
      "Elegant",
      "Traditional"
    ]
  }
}
```

**message 可能值**:
- `200` - 成功處理
- `2200` - 模特檢測失敗
- `2400` - 衣伺檢測失敗
- `2422` - 圖片品質過低
- `2500` - 內部處理錯誤
- `2501` - 超時

#### 3.1.3 試穿結果寫入 model 資料表

AI 回傳的圖片與風格資料需保存到 `model` 資料表，欄位對應如下：

| model 欄位 | 資料來源 | 說明 |
|-----------|---------|------|
| `model_id` | DB 自動生成 | 主鍵流水號 |
| `f_user_uid` | JWT 使用者資訊 | 關聯當前使用者 |
| `model_uid` | 後端生成 UUID | 試穿記錄唯一識別碼 |
| `model_picture` | AI 回傳 PNG 上傳後 URL/Key | 合併試穿結果圖 |
| `model_style` | `ai_response.data.style_name` | 風格陣列（JSON 或字串化） |

**✅ 確認：AI 後端回傳資料會保存到 `model` 資料表（包含 model_picture 與 model_style）**

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "message": "虛擬試穿完成",
    "model_data": {
      "model_uid": "550e8400-e29b-41d4-a716-446655440200",
      "f_user_uid": "550e8400-e29b-41d4-a716-446655440001",
      "status": "completed",
      "model_picture": "http://192.168.233.128:9000/virtual-try-on/try_on_550e8400.png",
      "model_style": ["Japanese Style", "Elegant", "Traditional"],
      "clothes_count": 2,
      "ai_response": {
        "code": 200,
        "message": "200",
        "data": {
          "file_name": "try_on_outfit_20260328.png",
          "style_name": ["Japanese Style", "Elegant", "Traditional"],
          "file_format": "PNG"
        }
      }
    }
  }
  ```

- **失敗回應**:
  - `400 Bad Request`: 衣伺數量錯誤、參數格式錯誤、未設定用戶模特照片
  - `401 Unauthorized`: 未登入或 Token 無效
  - `403 Forbidden`: 衣伺不屬於當前使用者
  - `404 Not Found`: 衣伺不存在
  - `503 Service Unavailable`: AI 伺務不可用
  - `504 Gateway Timeout`: AI 合併逾時
  - `500 Internal Server Error`: 伺伺器內部錯誤

---

### 3.2 使用者查看我的試穿歷史
- **功能編號**: `TRYON-002`
- **模組**: `combine`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `GET`
- **API 路徑**: `/combine/user/virtual-try-on-history`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 取得當前使用者的試穿歷史
  - 支持分頁與狀態過濾
  - 可查看每筆試穿的結果圖與 AI 摘要

- **查詢參數**:
  ```
  GET /combine/user/virtual-try-on-history?page=1&limit=20&status=completed
  ```

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "count": 12,
    "total_pages": 1,
    "current_page": 1,
    "results": [
      {
        "model_uid": "550e8400-e29b-41d4-a716-446655440200",
        "status": "completed",
        "model_picture": "http://192.168.233.128:9000/virtual-try-on/try_on_550e8400.png",
        "model_style": ["Japanese Style", "Elegant", "Traditional"],
        "created_at": "2026-03-28T10:30:00Z"
      }
    ]
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: 未認證或 Token 過期
  - `500 Internal Server Error`: 伺伺器內部錯誤

---

### 3.3 使用者查看單筆試穿詳情
- **功能編號**: `TRYON-003`
- **模組**: `combine`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `GET`
- **API 路徑**: `/combine/user/virtual-try-on-detail/<model_uid>`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 查看單筆試穿詳情
  - 返回衣伺清單、結果圖片、AI metadata

- **路徑參數**:
  ```
  model_uid: "550e8400-e29b-41d4-a716-446655440200"
  ```

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "model_uid": "550e8400-e29b-41d4-a716-446655440200",
    "f_user_uid": "550e8400-e29b-41d4-a716-446655440001",
    "status": "completed",
    "model_picture": "http://192.168.233.128:9000/virtual-try-on/try_on_550e8400.png",
    "model_style": ["Japanese Style", "Elegant", "Traditional"],
    "clothes_list": [
      {
        "clothes_uid": "550e8400-e29b-41d4-a716-446655440010",
        "clothes_category": "clothing"
      },
      {
        "clothes_uid": "550e8400-e29b-41d4-a716-446655440011",
        "clothes_category": "bottom"
      }
    ],
    "ai_response": {
      "code": 200,
      "message": "200",
      "data": {
        "file_name": "try_on_outfit_20260328.png",
        "style_name": ["Japanese Style", "Elegant", "Traditional"],
        "file_format": "PNG"
      }
    }
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: 未認證或 Token 過期
  - `404 Not Found`: 試穿紀錄不存在
  - `500 Internal Server Error`: 伺伺器內部錯誤

---

### 3.4 使用者刪除虛擬試穿結果
- **功能編號**: `TRYON-004`
- **模組**: `combine`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `DELETE`
- **API 路徑**: `/combine/user/virtual-try-on-delete/<model_uid>`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 刪除一個虛擬試穿結果
  - 只能刪除自己的試穿記錄
  - 同時刪除 MinIO 中儲存的試穿結果圖片
  - 刪除後無法恢復

- **路徑參數**:
  ```
  model_uid: "550e8400-e29b-41d4-a716-446655440200"
  ```

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "message": "試穿結果已成功刪除",
    "deleted_model_uid": "550e8400-e29b-41d4-a716-446655440200",
    "deleted_model_id": 12345
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: 未認證或 Token 過期
  - `404 Not Found`: 試穿紀錄不存在或沒有權限刪除
    ```json
    {
      "success": false,
      "message": "試穿紀錄不存在或沒有權限刪除"
    }
    ```
  - `500 Internal Server Error`: 伺伺器內部錯誤

---

### 3.5 試穿 API 快速參考表

| 功能 | HTTP 方法 | API 路徑 | 認證 | 返回狀態碼 |
|------|----------|---------|------|----------|
| 發起試穿（選 2 件衣伺） | POST | `/combine/user/virtual-try-on` | 必須 | 200 |
| 查看我的試穿歷史 | GET | `/combine/user/virtual-try-on-history` | 必須 | 200 |
| 查看單筆試穿詳情 | GET | `/combine/user/virtual-try-on-detail/<model_uid>` | 必須 | 200 |
| 刪除試穿結果 | DELETE | `/combine/user/virtual-try-on-delete/<model_uid>` | 必須 | 200 |

---

## 🤖 四、AI 功能模塊

AI 相關的智能功能，包括智能推薦穿搭和文字對話諮詢

---

### 4.1 AI 智能推薦穿搭 ⭐ 新功能

**功能編號**: `AI-001`  
**模組**: `aichat_service` (新模組)  
**優先級**: ⭐⭐ 進階功能  
**核心特性**: 用戶輸入文字描述 → AI 分析 → 自動篩選衣服 → 虛擬試穿合成 → 保存推薦結果

**功能說明**:
用戶輸入一段自然語言文字（包含心情、天氣、場合等資訊），系統通過以下步驟自動生成穿搭推薦：
1. **AI 分析階段**: 使用 Gemini API 分析用戶輸入，提取關鍵詞和風格偏好
2. **衣服篩選階段**: 基於提取的關鍵詞和衣服標籤（color_name、clothes_category、style_name）進行智能篩選
3. **組合推薦階段**: 從篩選結果中自動選擇 2 件衣服進行組合（上衣 + 下衣）
4. **虛擬試穿階段**: 將選定的衣服組合丟入虛擬試穿 AI 進行合成
5. **結果保存階段**: 將合成結果直接保存到 Model 表（並標記 source 為 'ai_recommendation'）

**整體流程圖**:
```
【AI 推薦穿搭完整流程】
════════════════════════════════════════════════════════════════

1️⃣ 前端：用戶輸入文字
   └─ 例："今天天氣很好，我要去逛街，希望穿得舒適又時尚"

2️⃣ 前端：發送推薦請求
   └─ POST /aichat_service/recommend/generate
      Headers: Authorization: Bearer <access_token>
      Body: {
        "user_input": "今天天氣很好，我要去逛街，希望穿得舒適又時尚",
        "top_k": 3  // 可選，返回前 3 個推薦結果
      }

3️⃣ 後端：第一層 - AI 分析
   ├─ 調用 Gemini API 分析用戶輸入文字
   ├─ 提取關鍵詞：
   │  ├─ 場景關鍵詞：逛街、休閒、日常等
   │  ├─ 天氣關鍵詞：晴天、春季等
   │  ├─ 風格關鍵詞：舒適、時尚、簡約等
   │  └─ 情感關鍵詞：開心、輕鬆等
   │
   ├─ 使用 Gemini 提取推薦的：
   │  ├─ clothes_category（衣伺分類）：T-shirt, Shirt, Pants, Skirt 等
   │  ├─ color_name（顏色）：白色、藍色、米色等
   │  └─ style_name（風格）：Casual, Sporty, Elegant 等
   │
   └─ 返回分析結果（JSON 格式）

4️⃣ 後端：第二層 - 衣服篩選
   ├─ 查詢數據庫中所有用戶的衣服
   ├─ 根據 AI 提取的關鍵詞進行多維度篩選：
   │  ├─ 匹配 clothes_category
   │  ├─ 匹配 color_name（支持模糊匹配）
   │  └─ 匹配 style_name
   │
   ├─ 計算衣服匹配分數（matching_score）：
   │  ├─ category 匹配得 0.4 分
   │  ├─ color 匹配得 0.3 分
   │  └─ style 匹配得 0.3 分
   │
   ├─ 按分數排序，過濾出 top 衣伺
   └─ 分離為上衣（top）和下衣（bottom）兩個池子

5️⃣ 後端：第三層 - 組合推薦
   ├─ 從篩選結果中選擇：
   │  ├─ 1 件上衣（clothes_category 為 shirt/top/clothing 等）
   │  └─ 1 件下衣（clothes_category 為 pants/skirt/bottom 等）
   │
   ├─ 選擇邏輯：
   │  ├─ 優先選擇匹配分數最高的組合
   │  ├─ 確保顏色搭配和諧（調用 Gemini 驗證）
   │  └─ 最多生成 top_k 個推薦組合（默認 1，最多 3）
   │
   └─ 返回選定的衣服 IDs

6️⃣ 後端：第四層 - 虛擬試穿合成
   ├─ 對每一個推薦組合，調用虛擬試穿 AI：
   │  └─ POST http://172.17.0.1:8002/virtual_try_on/clothes/combine
   │
   ├─ 發送數據格式（與虛擬試穿相同）：
   │  ├─ model_image: 用戶模特照片
   │  ├─ garment_0, garment_1: 推薦的 2 件衣伺
   │  ├─ model_info: 用戶身體測量數據
   │  └─ garments: 衣伺尺寸信息
   │
   └─ 接收虛擬試穿結果（圖片 + 風格分析）

7️⃣ 後端：第五層 - 結果保存
   ├─ 對每個推薦結果，保存到 Model 表：
   │  ├─ f_user_uid: 當前用戶
   │  ├─ model_uid: UUID
   │  ├─ model_picture: 虛擬試穿合成圖 URL
   │  ├─ model_style: AI 返回的風格分析
   │  ├─ source: 'ai_recommendation'（標記為推薦來源）
   │  ├─ recommendation_context: 用戶輸入的文字
   │  ├─ recommendation_keywords: AI 提取的關鍵詞（JSON）
   │  ├─ recommendation_score: 推薦匹配分數
   │  └─ clothes_list: 使用的 2 件衣伺詳情
   │
   └─ 記錄已保存，可立即在推薦歷史中查看

8️⃣ 後端：返回推薦結果
   └─ HTTP/1.1 200 OK
      {
        "success": true,
        "message": "推薦穿搭生成成功",
        "recommendations": [
          {
            "rank": 1,
            "model_uid": "uuid-1",
            "model_picture": "http://minio:9000/...",
            "recommendation_score": 0.92,
            "clothes_info": {
              "top": {...},
              "bottom": {...}
            },
            "ai_analysis": "這個組合非常適合您的需求..."
          },
          // 如果 top_k > 1，返回多個推薦
        ],
        "ai_keywords": ["逛街", "舒適", "時尚", "Casual", "白色", "T-shirt"],
        "total_recommendations": 1
      }

9️⃣ 前端：展示推薦結果
   └─ 依次展示推薦組合：
      ├─ 虛擬試穿合成圖
      ├─ 推薦理由/分析說明
      ├─ 衣伺詳情（可點擊查看）
      └─ 操作按鈕：
         ├─ 保存到收藏夾
         ├─ 分享
         ├─ 查看其他推薦
         └─ 重新推薦
```

---

#### 4.1.1 生成推薦穿搭

**HTTP 方法**: `POST`  
**API 路徑**: `/aichat_service/recommend/generate`

- **輸入參數** (JSON):
  ```json
  {
    "user_input": "今天天氣很好，我要去逛街，希望穿得舒適又時尚",
    "top_k": 1,
    "exclude_colors": ["黑色"],
    "preferred_styles": ["Casual"],
    "category_filter": null
  }
  ```

  **📝 參數說明**:
  - **user_input** (必填): 用戶輸入的自然語言文字（1-500 字符）
  - **top_k** (可選，默認 1): 返回前 K 個推薦結果（範圍 1-3）
  - **exclude_colors** (可選): 排除的顏色列表
  - **preferred_styles** (可選): 偏好的風格列表（會加權提高匹配分數）
  - **category_filter** (可選): 僅篩選特定衣伺分類

- **Headers** 🔐:
  ```
  Authorization: Bearer <access_token>
  Content-Type: application/json
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "message": "推薦穿搭生成成功",
    "request_id": "req_20260328_001",
    "ai_analysis": {
      "user_intent": "日常休閒街拍",
      "extracted_keywords": {
        "occasion": ["逛街"],
        "weather": ["晴天"],
        "style": ["舒適", "時尚"],
        "emotion": ["開心"]
      },
      "recommended_categories": ["T-shirt", "Pants"],
      "recommended_colors": ["白色", "藍色"],
      "recommended_styles": ["Casual", "Sporty"]
    },
    "recommendations": [
      {
        "rank": 1,
        "model_uid": "550e8400-e29b-41d4-a716-446655440300",
        "model_picture": "http://192.168.233.128:9000/recommendations/model_550e8400.png",
        "recommendation_score": 0.92,
        "score_breakdown": {
          "category_match": 0.95,
          "color_match": 0.90,
          "style_match": 0.90,
          "overall": 0.92
        },
        "clothes_info": {
          "top": {
            "clothes_uid": "550e8400-e29b-41d4-a716-446655440010",
            "clothes_category": "T-shirt",
            "colors": ["白色"],
            "styles": ["Casual", "Sporty"],
            "clothes_image_url": "..."
          },
          "bottom": {
            "clothes_uid": "550e8400-e29b-41d4-a716-446655440011",
            "clothes_category": "Pants",
            "colors": ["藍色"],
            "styles": ["Casual"],
            "clothes_image_url": "..."
          }
        },
        "ai_reasoning": "白色 T 恤搭配藍色牛仔褲是經典的日常搭配。這個組合舒適休閒，非常適合逛街。白色清爽，藍色耐髒，顏色搭配和諧，整體氣質時尚簡約。",
        "model_style": ["Casual", "Sporty", "Elegant"],
        "created_at": "2026-03-28T10:45:00Z"
      },
      // 如果 top_k > 1，返回更多推薦...
    ],
    "total_recommendations": 1,
    "generation_time_ms": 3456
  }
  ```

- **失敗回應**:
  - `400 Bad Request`: 輸入文字過短或過長、參數格式錯誤
    ```json
    {
      "success": false,
      "message": "用戶輸入必須在 1-500 字符之間"
    }
    ```
  - `401 Unauthorized`: Token 無效或過期
  - `403 Forbidden`: 用戶未設定模特照片或身體數據
    ```json
    {
      "success": false,
      "message": "請先上傳模特照片並補充身體測量數據後，才能使用推薦功能"
    }
    ```
  - `404 Not Found`: 用戶沒有衣伺，無法生成推薦
  - `422 Unprocessable Entity`: AI 分析失敗或無法進行虛擬試穿
  - `503 Service Unavailable`: Gemini API 或虛擬試穿 AI 服務不可用
  - `504 Gateway Timeout`: 推薦生成超時（超過 60 秒）

---

#### 4.1.2 查看推薦穿搭歷史

**HTTP 方法**: `GET`  
**API 路徑**: `/aichat_service/recommend/history`

- **查詢參數**:
  ```
  GET /aichat_service/recommend/history?page=1&limit=20&sort=newest
  ```
  - **page** (可選，默認 1): 分頁號
  - **limit** (可選，默認 20): 每頁數量（範圍 1-50）
  - **sort** (可選，默認 newest): 排序方式
    - `newest`: 最新優先
    - `score_high`: 推薦分數最高優先
    - `oldest`: 最舊優先

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "count": 15,
    "total_pages": 1,
    "current_page": 1,
    "results": [
      {
        "model_uid": "550e8400-e29b-41d4-a716-446655440300",
        "recommendation_score": 0.92,
        "model_picture": "http://192.168.233.128:9000/recommendations/model_550e8400.png",
        "model_style": ["Casual", "Sporty"],
        "recommendation_context": "今天天氣很好，我要去逛街，希望穿得舒適又時尚",
        "clothes_count": 2,
        "created_at": "2026-03-28T10:45:00Z",
        "source": "ai_recommendation"
      },
      // ... 更多推薦記錄
    ]
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期

---

#### 4.1.3 查看推薦詳情

**HTTP 方法**: `GET`  
**API 路徑**: `/aichat_service/recommend/<model_uid>`

- **路徑參數**:
  ```
  model_uid: "550e8400-e29b-41d4-a716-446655440300"
  ```

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "model_uid": "550e8400-e29b-41d4-a716-446655440300",
    "f_user_uid": "550e8400-e29b-41d4-a716-446655440001",
    "recommendation_score": 0.92,
    "recommendation_context": "今天天氣很好，我要去逛街，希望穿得舒適又時尚",
    "recommendation_keywords": {
      "occasion": ["逛街"],
      "weather": ["晴天"],
      "style": ["舒適", "時尚"],
      "emotion": ["開心"]
    },
    "model_picture": "http://192.168.233.128:9000/recommendations/model_550e8400.png",
    "model_style": ["Casual", "Sporty", "Elegant"],
    "clothes_list": [
      {
        "clothes_uid": "550e8400-e29b-41d4-a716-446655440010",
        "clothes_category": "T-shirt",
        "colors": ["白色"],
        "styles": ["Casual"],
        "clothes_image_url": "...",
        "clothes_measurements": {
          "arm_length": 65,
          "shoulder_width": 45
        }
      },
      {
        "clothes_uid": "550e8400-e29b-41d4-a716-446655440011",
        "clothes_category": "Pants",
        "colors": ["藍色"],
        "styles": ["Casual"],
        "clothes_image_url": "...",
        "clothes_measurements": {
          "leg_length": 100,
          "waistline": 90
        }
      }
    ],
    "ai_reasoning": "白色 T 恤搭配藍色牛仔褲是經典的日常搭配。這個組合舒適休閒，非常適合逛街。白色清爽，藍色耐髒，顏色搭配和諧，整體氣質時尚簡約。",
    "ai_response": {
      "code": 200,
      "message": "200",
      "data": {
        "file_name": "recommend_outfit_20260328.png",
        "style_name": ["Casual", "Sporty", "Elegant"],
        "file_format": "PNG"
      }
    },
    "created_at": "2026-03-28T10:45:00Z",
    "source": "ai_recommendation"
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期
  - `404 Not Found`: 推薦記錄不存在

---

#### 4.1.4 刪除推薦穿搭

**HTTP 方法**: `DELETE`  
**API 路徑**: `/aichat_service/recommend/<model_uid>`

- **路徑參數**:
  ```
  model_uid: "550e8400-e29b-41d4-a716-446655440300"
  ```

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "message": "推薦穿搭已成功刪除",
    "deleted_model_uid": "550e8400-e29b-41d4-a716-446655440300"
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期
  - `404 Not Found`: 推薦記錄不存在或沒有權限刪除

---

#### 4.1.5 AI 推薦 API 快速參考表

| 功能 | HTTP 方法 | API 路徑 | 認證 | 返回狀態碼 |
|------|----------|---------|------|----------|
| 生成推薦穿搭 | POST | `/aichat_service/recommend/generate` | 必須 | 200 |
| 查看推薦歷史 | GET | `/aichat_service/recommend/history` | 必須 | 200 |
| 查看推薦詳情 | GET | `/aichat_service/recommend/<model_uid>` | 必須 | 200 |
| 刪除推薦穿搭 | DELETE | `/aichat_service/recommend/<model_uid>` | 必須 | 200 |

---

### 4.2 使用者與 AI 文字對話 ⭐ 未來擴展功能

**功能編號**: `AI-002`  
**模組**: `aichat_service` (共用模組)  
**優先級**: ⭐⭐ 進階功能  
**核心特性**: 與 AI 進行多輪對話 → 獲得穿搭建議、風格諮詢、搭配指導等

**功能說明**:
用戶可以與 AI 進行自由形式的文字對話，提問關於穿搭、風格、搭配等各類問題。AI 基於用戶的身體數據、已有衣伺、風格偏好等信息進行智能回答，並可在對話過程中提供衣伺推薦。

**使用場景**:
- 場景 1: "我想要一套適合職場的穿搭，但預算有限，請幫我分析一下如何搭配"
- 場景 2: "我的皮膚偏黃，應該穿什麼顏色的衣服？"
- 場景 3: "這套衣服該怎麼搭配鞋子和配飾？"
- 場景 4: "我想參加一個正式活動，身高170cm，體型偏瘦，怎樣才能顯得更有氣質？"
- 場景 5: "根據我的衣櫃，幫我提出5套完整的穿搭方案"

**整體流程圖**:
```
【AI 文字對話完整流程】
════════════════════════════════════════════════════════════════

1️⃣ 前端：用戶發起對話
   └─ 輸入第一條信息（問題或需求）

2️⃣ 前端：建立聊天會話
   └─ POST /aichat_service/chat/start
      Headers: Authorization: Bearer <access_token>
      Body: {
        "initial_message": "我想要一套職場穿搭方案"
      }
      
      返回 conversation_id（後續對話使用）

3️⃣ 後端：初始化會話
   ├─ 建立新的 Conversation 記錄
   ├─ 生成 conversation_id（UUID）
   └─ 初始化上下文：
      ├─ 用戶身體數據
      ├─ 用戶衣伺列表
      ├─ 用戶的對話歷史（可選，支持續聊）
      └─ 風格偏好信息

4️⃣ 後端：AI 分析層
   ├─ 調用 Gemini API：
   │  ├─ 輸入：用戶信息、衣伺列表、用戶提問
   │  ├─ 提示詞：
   │  │  ├─ 系統提示詞（定義 AI 的角色和能力）
   │  │  ├─ 用戶數據上下文（身高、體型、膚色等）
   │  │  ├─ 衣伺列表上下文（用戶已有的衣服）
   │  │  └─ 對話歷史（前面的對話內容）
   │  │
   │  └─ 輸出：
   │     ├─ AI 回答文字
   │     ├─ 推薦的衣伺 IDs（可選）
   │     ├─ 搭配建議
   │     └─ 後續問題提示（引導對話）
   │
   └─ 解析 AI 回應

5️⃣ 後端：衣伺推薦層（可選）
   ├─ 如果 AI 推薦了衣伺：
   │  ├─ 從推薦中提取衣伺 ID
   │  ├─ 查詢衣伺詳情
   │  └─ 生成衣伺 URL 和信息
   │
   └─ 組裝推薦信息到回應中

6️⃣ 後端：保存對話記錄
   ├─ 保存用戶信息到 ChatMessage 表：
   │  ├─ conversation_id
   │  ├─ user_id
   │  ├─ role: 'user'
   │  ├─ content: 用戶信息原文
   │  ├─ created_at
   │  └─ token_count: 信息 token 數
   │
   ├─ 保存 AI 回應到 ChatMessage 表：
   │  ├─ conversation_id
   │  ├─ user_id (AI 用戶或系統用戶)
   │  ├─ role: 'assistant'
   │  ├─ content: AI 回答
   │  ├─ metadata: 推薦的衣伺、搭配建議等
   │  ├─ created_at
   │  └─ token_count: AI 回應 token 數
   │
   └─ 更新 Conversation 表統計信息

7️⃣ 後端：返回對話回應
   └─ HTTP/1.1 200 OK
      {
        "success": true,
        "conversation_id": "conv_20260328_001",
        "message_id": "msg_001",
        "ai_response": "根據您的身高和體型...",
        "recommended_clothes": [
          {
            "clothes_uid": "uuid",
            "clothes_image_url": "...",
            "clothes_category": "Blazer",
            "colors": ["黑色"],
            "styles": ["Elegant"],
            "reason": "這件西裝..."
          },
          // 更多推薦...
        ],
        "suggestions": "您還可以詢問...",
        "tokens_used": {
          "input": 1200,
          "output": 450,
          "total": 1650
        }
      }

8️⃣ 前端：顯示 AI 回答
   ├─ 展示 AI 回答文本
   ├─ 如果有衣伺推薦，展示推薦卡片
   ├─ 顯示搭配建議
   └─ 顯示後續提示（引導用戶繼續對話）

9️⃣ 用戶後續操作選項
   ├─ 追問相關問題（多輪對話）
   │  └─ POST /aichat_service/chat/<conversation_id>/message
   │     Body: { "message": "還有其他搭配方案嗎？" }
   │
   ├─ 查看對話歷史
   │  └─ GET /aichat_service/chat/<conversation_id>/history
   │
   ├─ 保存推薦衣伺到收藏
   │  └─ PATCH /picture/clothes/<clothes_uid>/favorite
   │
   ├─ 基於推薦進行虛擬試穿
   │  └─ POST /combine/user/virtual-try-on
   │
   ├─ 結束對話
   │  └─ POST /aichat_service/chat/<conversation_id>/end
   │
   └─ 開始新對話
      └─ POST /aichat_service/chat/start

【核心特性】
✅ 多輪對話 - 支持完整的對話流程，AI 可以記住上下文
✅ 用戶上下文 - 基於用戶身體數據和衣伺庫進行個性化建議
✅ 衣伺推薦 - 在對話過程中推薦具體的衣伺及搭配建議
✅ 對話歷史 - 完整保存對話記錄，支持回顧和續聊
✅ Token 計數 - 記錄 API 使用情況，為後續計費提供數據
✅ 搭配指導 - 提供詳細的穿搭建議和搭配理由
✅ 靈活擴展 - 易於添加新的功能，如搭配評分、分享等
```

---

#### 4.2.1 開始新對話

**HTTP 方法**: `POST`  
**API 路徑**: `/aichat_service/chat/start`

- **輸入參數** (JSON):
  ```json
  {
    "initial_message": "我想要一套職場穿搭方案",
    "context": "outfit_recommendation|style_advice|general",
    "tags": ["professional", "business"]
  }
  ```

  **📝 參數說明**:
  - **initial_message** (必填): 用戶的初始提問或需求（1-500 字符）
  - **context** (可選，默認 'general'): 對話上下文
    - `outfit_recommendation`: 穿搭推薦
    - `style_advice`: 風格諮詢
    - `general`: 一般問答
  - **tags** (可選): 對話標籤，便於後續分類和搜索

- **Headers** 🔐:
  ```
  Authorization: Bearer <access_token>
  Content-Type: application/json
  ```

- **成功回應 (201 Created / 200 OK)**:
  ```json
  {
    "success": true,
    "message": "對話已開始",
    "conversation": {
      "conversation_id": "conv_20260328_550e8400",
      "context": "outfit_recommendation",
      "created_at": "2026-03-28T10:00:00Z",
      "tags": ["professional", "business"]
    },
    "ai_response": {
      "message_id": "msg_20260328_001",
      "content": "您好！我是您的穿搭顧問。根據您的需求，我建議...",
      "recommended_clothes": [
        {
          "clothes_uid": "550e8400-e29b-41d4-a716-446655440010",
          "clothes_category": "Blazer",
          "colors": ["黑色", "深藍"],
          "styles": ["Elegant", "Professional"],
          "clothes_image_url": "http://...",
          "reason": "這件黑色西裝是職場穿搭的經典選擇，能提升整體氣質。建議搭配白色或淺藍色襯衫。"
        },
        // 更多推薦...
      ],
      "suggestions": "您還可以詢問：1. 搭配什麼褲子比較好？2. 有沒有更休閒的選擇？",
      "created_at": "2026-03-28T10:00:05Z"
    },
    "tokens_used": {
      "input": 1200,
      "output": 450,
      "total": 1650
    }
  }
  ```

- **失敗回應**:
  - `400 Bad Request`: 輸入文字過短或過長、參數格式錯誤
  - `401 Unauthorized`: Token 無效或過期
  - `403 Forbidden`: 用戶未完善個人資料
  - `503 Service Unavailable`: Gemini API 不可用
  - `504 Gateway Timeout`: AI 回應超時（超過 30 秒）

---

#### 4.2.2 發送聊天信息（多輪對話）

**HTTP 方法**: `POST`  
**API 路徑**: `/aichat_service/chat/<conversation_id>/message`

- **路徑參數**:
  ```
  conversation_id: "conv_20260328_550e8400"
  ```

- **輸入參數** (JSON):
  ```json
  {
    "message": "還有其他搭配方案嗎？",
    "include_recommendations": true
  }
  ```

  **📝 參數說明**:
  - **message** (必填): 用戶的對話信息（1-500 字符）
  - **include_recommendations** (可選，默認 true): 是否在回應中包含衣伺推薦

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  Content-Type: application/json
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "conversation_id": "conv_20260328_550e8400",
    "ai_response": {
      "message_id": "msg_20260328_002",
      "content": "當然可以！除了黑色西裝，我還建議...",
      "recommended_clothes": [
        // 新的衣伺推薦...
      ],
      "suggestions": "您可以繼續詢問：1. 鞋子怎樣搭配？2. 配飾選擇？",
      "created_at": "2026-03-28T10:05:00Z"
    },
    "message_history_count": 4,
    "tokens_used": {
      "input": 2000,
      "output": 380,
      "total": 2380,
      "cumulative_total": 4030
    }
  }
  ```

- **失敗回應**:
  - `400 Bad Request`: 輸入格式錯誤
  - `401 Unauthorized`: Token 無效或過期
  - `404 Not Found`: 對話不存在
  - `410 Gone`: 對話已結束
  - `503 Service Unavailable`: Gemini API 不可用

---

#### 4.2.3 查看對話歷史

**HTTP 方法**: `GET`  
**API 路徑**: `/aichat_service/chat/<conversation_id>/history`

- **路徑參數**:
  ```
  conversation_id: "conv_20260328_550e8400"
  ```

- **查詢參數**:
  ```
  GET /aichat_service/chat/<conversation_id>/history?page=1&limit=20
  ```

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "conversation_id": "conv_20260328_550e8400",
    "conversation_info": {
      "context": "outfit_recommendation",
      "created_at": "2026-03-28T10:00:00Z",
      "updated_at": "2026-03-28T10:15:00Z",
      "message_count": 4,
      "total_tokens_used": 4030
    },
    "messages": [
      {
        "message_id": "msg_20260328_001",
        "role": "user",
        "content": "我想要一套職場穿搭方案",
        "created_at": "2026-03-28T10:00:00Z"
      },
      {
        "message_id": "msg_20260328_001",
        "role": "assistant",
        "content": "您好！我是您的穿搭顧問。根據您的需求，我建議...",
        "recommended_clothes": [
          // 推薦的衣伺...
        ],
        "created_at": "2026-03-28T10:00:05Z",
        "tokens": {
          "input": 1200,
          "output": 450
        }
      },
      {
        "message_id": "msg_20260328_002",
        "role": "user",
        "content": "還有其他搭配方案嗎？",
        "created_at": "2026-03-28T10:05:00Z"
      },
      {
        "message_id": "msg_20260328_003",
        "role": "assistant",
        "content": "當然可以！除了黑色西裝，我還建議...",
        "recommended_clothes": [...],
        "created_at": "2026-03-28T10:05:05Z",
        "tokens": {
          "input": 2000,
          "output": 380
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total_count": 4,
      "total_pages": 1
    }
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期
  - `404 Not Found`: 對話不存在或沒有權限查看

---

#### 4.2.4 查看我的所有對話

**HTTP 方法**: `GET`  
**API 路徑**: `/aichat_service/chat/my-conversations`

- **查詢參數**:
  ```
  GET /aichat_service/chat/my-conversations?page=1&limit=20&sort=newest&context=outfit_recommendation
  ```
  - **page** (可選，默認 1): 分頁號
  - **limit** (可選，默認 20): 每頁數量（範圍 1-50）
  - **sort** (可選，默認 newest): 排序方式
    - `newest`: 最新優先
    - `oldest`: 最舊優先
    - `most_messages`: 信息最多優先
  - **context** (可選): 篩選對話類型

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "count": 15,
    "total_pages": 1,
    "current_page": 1,
    "results": [
      {
        "conversation_id": "conv_20260328_550e8400",
        "context": "outfit_recommendation",
        "initial_message": "我想要一套職場穿搭方案",
        "message_count": 4,
        "total_tokens_used": 4030,
        "created_at": "2026-03-28T10:00:00Z",
        "updated_at": "2026-03-28T10:15:00Z",
        "last_message": "當然可以！除了黑色西裝，我還建議..."
      },
      // ... 更多對話...
    ]
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期

---

#### 4.2.5 結束對話

**HTTP 方法**: `POST`  
**API 路徑**: `/aichat_service/chat/<conversation_id>/end`

- **路徑參數**:
  ```
  conversation_id: "conv_20260328_550e8400"
  ```

- **輸入參數** (JSON，可選):
  ```json
  {
    "summary": "非常有幫助的對話",
    "rating": 5
  }
  ```

  **📝 參數說明**:
  - **summary** (可選): 對話總結或評論
  - **rating** (可選): 對對話的評分（1-5 星）

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  Content-Type: application/json
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "message": "對話已結束",
    "conversation_id": "conv_20260328_550e8400",
    "conversation_stats": {
      "message_count": 4,
      "total_tokens_used": 4030,
      "duration_seconds": 900,
      "created_at": "2026-03-28T10:00:00Z",
      "ended_at": "2026-03-28T10:15:00Z"
    }
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期
  - `404 Not Found`: 對話不存在
  - `410 Gone`: 對話已結束

---

#### 4.2.6 刪除對話記錄

**HTTP 方法**: `DELETE`  
**API 路徑**: `/aichat_service/chat/<conversation_id>`

- **路徑參數**:
  ```
  conversation_id: "conv_20260328_550e8400"
  ```

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "message": "對話記錄已刪除",
    "deleted_conversation_id": "conv_20260328_550e8400"
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期
  - `404 Not Found`: 對話不存在或沒有權限刪除

---

#### 4.2.7 AI 文字對話 API 快速參考表

| 功能 | HTTP 方法 | API 路徑 | 認證 | 返回狀態碼 |
|------|----------|---------|------|----------|
| 開始新對話 | POST | `/aichat_service/chat/start` | 必須 | 201/200 |
| 發送聊天信息 | POST | `/aichat_service/chat/<conversation_id>/message` | 必須 | 200 |
| 查看對話歷史 | GET | `/aichat_service/chat/<conversation_id>/history` | 必須 | 200 |
| 查看所有對話 | GET | `/aichat_service/chat/my-conversations` | 必須 | 200 |
| 結束對話 | POST | `/aichat_service/chat/<conversation_id>/end` | 必須 | 200 |
| 刪除對話 | DELETE | `/aichat_service/chat/<conversation_id>` | 必須 | 200 |

---

#### 4.2.8 系統提示詞設計

為了提高 AI 回答的質量，需要為 Gemini API 設計結構化的系統提示詞：

```
【系統提示詞框架】

你是一位專業的穿搭顧問，具備以下能力：
1. 根據用戶的身體測量數據（身高、體重、體型等）提供個性化建議
2. 根據用戶已有的衣伺庫提出搭配方案
3. 考慮用戶的風格偏好和身體特點
4. 提供顏色搭配、風格搭配等專業建議
5. 在對話中推薦具體的衣伺並解釋推薦理由

用戶信息：
- 身高：{user_height}cm
- 體重：{user_weight}kg
- 體型：{body_type}
- 膚色：{skin_tone}
- 風格偏好：{style_preferences}

已有衣伺列表：
{clothes_list}

對話規則：
1. 回答應該以第一人稱提出建議，避免過於正式
2. 如果推薦衣伺，請附上推薦理由
3. 在每次回答最後提出 2-3 個後續問題，引導用戶繼續對話
4. 如果用戶沒有相關衣伺，請提出購買建議
5. 考慮搭配的完整性（上衣、下裝、鞋、配飾等）

回答格式要求：
- 前 50 個字：核心建議
- 中間部分：詳細解釋和推薦衣伺
- 最後：後續引導問題
```

---

#### 4.2.9 對話管理的數據模型

```python
# models.py

from django.db import models

class Conversation(models.Model):
    """對話會話模型"""
    
    CONTEXT_CHOICES = [
        ('outfit_recommendation', 'Outfit Recommendation'),
        ('style_advice', 'Style Advice'),
        ('general', 'General Question'),
    ]
    
    conversation_id = models.CharField(max_length=36, unique=True, primary_key=True)
    f_user_uid = models.ForeignKey(User, on_delete=models.CASCADE)
    context = models.CharField(max_length=20, choices=CONTEXT_CHOICES, default='general')
    tags = models.JSONField(default=list, blank=True)
    
    message_count = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)  # 對話是否進行中
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['f_user_uid', '-created_at']),
            models.Index(fields=['is_active']),
        ]


class ChatMessage(models.Model):
    """對話信息模型"""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    message_id = models.CharField(max_length=36, unique=True, primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    
    # AI 推薦的衣伺
    recommended_clothes = models.JSONField(default=list, blank=True)
    
    # Token 計數
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    
    # 額外元數據
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]
```

---

## 🎯 4.1 vs 4.2 功能對比與前端指南

### 4.1 vs 4.2 核心差異表

| 特性 | **4.1 AI 智能推薦穿搭** (AI-001) | **4.2 AI 文字對話** (AI-002) |
|------|--------------------------------|---------------------------|
| **核心用途** | 🚀 一鍵自動推薦穿搭 | 💬 多輪互動式諮詢 |
| **交互方式** | 👉 用戶輸入 → 系統自動推薦 | 👉 用戶提問 → AI 回答 → 用戶再提問 |
| **應用場景** | 💭 用戶沒想法，需要靈感 | 🤔 用戶有想法，需要詳細指導 |
| **主要 API** | POST `/aichat_service/recommend/generate` | POST `/aichat_service/chat/start` |
| **推薦邏輯** | 自動化：AI分析 → 篩選 → 組合 → 試穿合成 | 智能化：基於對話上下文逐步回答 |
| **返回內容** | ✅ 直接返回虛擬試穿圖片 + 推薦理由 | ✅ 返回文字建議 + 可選衣伺推薦 |
| **會話管理** | ❌ 無（單次請求） | ✅ 有（支持多輪對話，需要 conversation_id） |
| **用戶思考負擔** | 低（只需簡短描述場景） | 高（需要提出具體問題） |
| **平均響應時間** | 5-10 秒（涉及虛擬試穿） | 2-3 秒（僅文字回答） |
| **結果重用性** | ✅ 高（可直接穿搭） | 📚 中（需要參考和進一步詢問） |

---

### 前端決策邏輯

#### 🎬 用戶操作流程

**用戶場景 A: 急於上班，需要快速推薦**
```
用戶輸入: "我5分鐘後要上班，快幫我推薦一套！"
         ↓
前端判斷: 簡短、急迫 → 調用 4.1 (AI-001)
         ↓
API: POST /aichat_service/recommend/generate
     Body: { 
       "user_input": "我5分鐘後要上班，快幫我推薦一套！",
       "top_k": 1 
     }
         ↓
返回: 虛擬試穿圖片 + "這套白襯衫配黑色直筒褲..."
         ↓
用戶: 看到圖片，快速確認，出門！
```

**用戶場景 B: 有時間慢慢諮詢**
```
用戶輸入: "我的膚色偏冷色調，什麼顏色更適合我？"
         ↓
前端判斷: 具體問題、想討論 → 調用 4.2 (AI-002)
         ↓
API: POST /aichat_service/chat/start
     Body: { 
       "initial_message": "我的膚色偏冷色調，什麼顏色更適合我？",
       "context": "style_advice"
     }
         ↓
返回: "根據冷色調膚色，建議..." + conversation_id
         ↓
用戶: "那米色呢？會不會顯膚色暗沉？"
         ↓
API: POST /aichat_service/chat/{conversation_id}/message
     Body: { "message": "那米色呢？會不會顯膚色暗沉？" }
         ↓
返回: "米色搭配冷色調膚色..." (保持對話上下文)
         ↓
用戶: 逐步獲得詳細建議...
```

---

#### 💡 前端判斷規則

```javascript
【決策樹邏輯】

用戶打開 AI 推薦/諮詢頁面
    ↓
根據用戶輸入特點判斷：

1️⃣ 輸入特點分析
   ├─ 字數少 (< 20字) + 包含場景 (天氣、場合、活動)
   │  └─→ 傾向 4.1 (快速推薦)
   │
   ├─ 字數多 (> 30字) + 包含具體問題 (如何、怎樣、應該)
   │  └─→ 傾向 4.2 (詳細諮詢)
   │
   ├─ 提到「怎麼」「應該」「為什麼」等疑問詞
   │  └─→ 傾向 4.2 (用戶有疑問)
   │
   └─ 提到「幫我」「推薦」「推薦一套」等指令詞
      └─→ 傾向 4.1 (用戶要求推薦)

2️⃣ 上下文判斷
   ├─ 首次進入頁面 → 預設建議 4.1
   ├─ 用戶已經進行過對話 → 記住 conversation_id，繼續用 4.2
   └─ 用戶查看歷史記錄 → 4.1/4.2 分別顯示

3️⃣ UI 切換
   ├─ 有兩個標籤頁或獨立按鈕「快速推薦」和「AI 諮詢」
   └─ 用戶可以手動切換，無需自動判斷
```

**代碼實現範例**:
```javascript
// 前端判斷邏輯
function determineAPI(userInput) {
  const wordCount = userInput.length;
  const hasQuestion = /怎麼|應該|為什麼|可以嗎|好不好|對不對/.test(userInput);
  const hasRecommendRequest = /推薦|建議|幫我|給我/.test(userInput);
  const hasScenario = /天氣|場合|活動|上班|上課|約會|聚會/.test(userInput);
  
  // 優先級：如果有明確的疑問詞，傾向對話模式
  if (hasQuestion) {
    return 'CHAT'; // 4.2
  }
  
  // 如果是推薦請求且有場景，用快速推薦
  if (hasRecommendRequest && hasScenario && wordCount < 30) {
    return 'RECOMMEND'; // 4.1
  }
  
  // 基於字數的啟發式判斷
  if (wordCount > 30) {
    return 'CHAT'; // 4.2
  }
  
  // 默認返回推薦
  return 'RECOMMEND'; // 4.1
}

// 調用對應的 API
async function handleUserInput(userInput) {
  const apiType = determineAPI(userInput);
  
  if (apiType === 'RECOMMEND') {
    await callRecommendationAPI(userInput);
  } else if (apiType === 'CHAT') {
    await callChatAPI(userInput);
  }
}

// 4.1 API 調用
async function callRecommendationAPI(userInput) {
  const response = await fetch('/aichat_service/recommend/generate', {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_input: userInput,
      top_k: 1
    })
  });
  
  const data = await response.json();
  if (data.success) {
    displayTryOnImage(data.recommendations[0].model_picture);
    displayReasoning(data.recommendations[0].ai_reasoning);
  }
}

// 4.2 API 調用 - 開始對話
async function callChatAPI(userInput) {
  const response = await fetch('/aichat_service/chat/start', {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      initial_message: userInput,
      context: 'general'
    })
  });
  
  const data = await response.json();
  if (data.success) {
    // 保存 conversation_id 用於後續對話
    window.conversationId = data.conversation.conversation_id;
    displayMessage('assistant', data.ai_response.content);
    
    if (data.ai_response.recommended_clothes.length > 0) {
      displayRecommendedClothes(data.ai_response.recommended_clothes);
    }
  }
}

// 4.2 API 調用 - 繼續對話
async function sendChatMessage(message) {
  const response = await fetch(
    `/aichat_service/chat/${window.conversationId}/message`,
    {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message })
    }
  );
  
  const data = await response.json();
  if (data.success) {
    displayMessage('assistant', data.ai_response.content);
    if (data.ai_response.recommended_clothes.length > 0) {
      displayRecommendedClothes(data.ai_response.recommended_clothes);
    }
  }
}
```

---

### ✅ 快速判斷表（前端參考）

| 用戶說... | 應該用 | 理由 |
|---------|------|------|
| "今天天氣好，幫我推薦穿搭" | 4.1 | 簡單場景描述，需要快速結果 |
| "我的膚色偏黃，該怎麼穿？" | 4.2 | 具體問題，需要詳細討論 |
| "根據我的衣櫃給我5套穿搭方案" | 4.2 | 複雜需求，需要多輪對話 |
| "我要去上班，穿什麼？" | 4.1 | 簡單場景，需要快速推薦 |
| "這件藍色T恤搭配什麼褲子好看？" | 4.2 | 特定問題，需要詳細建議 |
| "春天休閒風，幫我推薦" | 4.1 | 簡短場景描述 |
| "怎樣搭配才能顯得更高？" | 4.2 | 疑問詞「怎樣」，需要詳細解答 |
| "我要去參加正式活動，身高160，體型偏胖" | 4.1 | 場景 + 身體數據，快速推薦 |
| "有沒有比較顯身材的穿搭技巧？" | 4.2 | 疑問詞「有沒有」，需要多輪討論 |

---

### 📱 推薦的 UI 設計方案

#### 方案 1: 獨立雙標籤設計（推薦）
```
【主導航】
┌──────────────────────────────────────────────────┐
│ 👜 衣伺 | 🤖 AI 推薦 | 💬 AI 諮詢 |
└──────────────────────────────────────────────────┘
           
🤖 AI 推薦                💬 AI 諮詢
┌────────────────────┐   ┌────────────────────┐
│ 📝 輸入場景描述    │   │ 💬 開始對話       │
│ ─────────────────  │   │ ─────────────────  │
│ [輸入框]           │   │ [對話框]           │
│ 今天天氣很好...    │   │ 白色和黑色...      │
│                    │   │                    │
│ [生成推薦]         │   │ [發送]             │
│ 按鈕 ▶             │   │ 按鈕 ▶             │
│                    │   │                    │
│ ⬇️ 顯示結果        │   │ ⬇️ 顯示結果        │
│ 試穿圖片 + 理由    │   │ AI 回答 + 建議     │
│                    │   │                    │
│ [保存] [分享]      │   │ [保存] [繼續問]    │
└────────────────────┘   └────────────────────┘
```

**優點**:
- ✅ 用戶清楚知道自己在用哪個功能
- ✅ 減少判斷邏輯複雜度
- ✅ 提升用戶體驗透明度

#### 方案 2: 統一入口自動切換設計
```
【統一 AI 推薦/諮詢頁面】
┌──────────────────────────────────┐
│ 🤖 AI 穿搭助手                    │
├──────────────────────────────────┤
│                                  │
│ 說出你的想法，我來幫你...       │
│ [輸入框]                         │
│ ─────────────────────────────   │
│ 例：「我要去上班」                │
│    「白色和黑色哪個更適合我？」   │
│                                  │
│ [提交]                           │
│                                  │
│ ⬇️ 自動判斷                      │
│ ├─ 簡短場景 → 快速推薦 (4.1)    │
│ └─ 具體問題 → 詳細諮詢 (4.2)    │
│                                  │
│ ⬇️ 顯示結果                      │
└──────────────────────────────────┘
```

**優點**:
- ✅ 用戶體驗更統一
- ✅ 無需用戶選擇
- ⚠️ 需要強大的 NLP 判斷邏輯

**推薦使用：方案 1 (獨立雙標籤)**，更清楚明確，減少歧義。

---

### 🔑 關鍵注意事項

1. **會話保存**
   - 4.1 無需保存會話（單次請求）
   - 4.2 必須保存 `conversation_id`，用於後續對話

2. **Token 計數**
   - 4.1: 根據虛擬試穿的複雜度，token 消耗較高
   - 4.2: 文字回答，token 消耗相對較低（但多輪累積）

3. **錯誤處理**
   - 4.1: 如果無衣伺或虛擬試穿超時，返回 422 或 504
   - 4.2: 如果 Gemini API 超時，返回 504

4. **用戶流轉**
   - 4.1 推薦結果 → 可進行虛擬試穿 (TRYON-001)
   - 4.2 推薦衣伺 → 可點擊查看詳情 → 進行虛擬試穿

---

## 📊 功能矩陣表

### 第一部分：用戶賬戶和衣伺管理

| # | 功能名稱 | 模組 | Actor | HTTP 方法 | 優先級 | 狀態 | API 端點 |
|---|---------|------|-------|----------|--------|------|---------|
| 1 | 使用者註冊 | accounts | user | POST | ⭐⭐⭐ | ✅ | `/account/user/register` |
| 2 | 使用者登入 | accounts | user | POST | ⭐⭐⭐ | ✅ | `/account/user/login` |
| 3 | 使用者登出 | accounts | user | POST | ⭐⭐⭐ | ✅ | `/account/user/logout` |
| 4 | 使用者刪除帳號 | accounts | user | POST | ⭐⭐ | ✅ | `/account/user/delete` |
| 5 | 上傳模特基本資料 | accounts | user | POST | ⭐⭐⭐ | 🔄 | `/account/user/user_info` |
| 6 | 設定衣伺資料 | picture | admin | POST/PUT | ⭐⭐⭐ | ✅ | `/picture/clothes/` |
| 7 | 新增衣伺（上傳圖片 + AI 處理） | picture | user | POST | ⭐⭐⭐ | ✅ | `/picture/clothes/` |
| 8 | 查看喜歡的衣伺 | picture | user | GET | ⭐⭐ | ✅ | `/picture/clothes/favorites` |
| 9 | 上傳/管理模特照片 | picture | user | POST/GET | ⭐⭐⭐ | ✅ | `/picture/user/photo` |

### 第二部分：虛擬試穿功能

| # | 功能名稱 | 模組 | Actor | HTTP 方法 | 優先級 | 狀態 | API 端點 |
|---|---------|------|-------|----------|--------|------|---------|
| 10 | **TRYON-001** 發起虛擬試穿 | combine | user | POST | ⭐⭐⭐ | ✅ | `/combine/user/virtual-try-on` |
| 11 | **TRYON-002** 查看試穿歷史 | combine | user | GET | ⭐⭐⭐ | ✅ | `/combine/user/virtual-try-on-history` |
| 12 | **TRYON-003** 查看試穿詳情 | combine | user | GET | ⭐⭐⭐ | ✅ | `/combine/user/virtual-try-on-detail/<model_uid>` |
| 13 | **TRYON-004** 刪除試穿結果 | combine | user | DELETE | ⭐⭐⭐ | ✅ | `/combine/user/virtual-try-on-delete/<model_uid>` |

### 第三部分：AI 功能

| # | 功能名稱 | 模組 | Actor | HTTP 方法 | 優先級 | 狀態 | API 端點 |
|---|---------|------|-------|----------|--------|------|---------|
| 14 | **AI-002** AI 智能推薦穿搭 | aichat_service | user | POST | ⭐⭐ | 🔄 | `/aichat_service/recommend/generate` |
| 15 | 查看推薦歷史 | aichat_service | user | GET | ⭐⭐ | 🔄 | `/aichat_service/recommend/history` |
| 16 | 查看推薦詳情 | aichat_service | user | GET | ⭐⭐ | 🔄 | `/aichat_service/recommend/<model_uid>` |
| 17 | 刪除推薦穿搭 | aichat_service | user | DELETE | ⭐⭐ | 🔄 | `/aichat_service/recommend/<model_uid>` |
| 18 | AI 文字對話 (未來) | aichat_service | user | POST | ⭐⭐ | ⏳ | `/aichat_service/chat` |

**狀態說明:**
- ✅ 已完成（✅ 新增 = 新建立的功能）
- 🔄 進行中
- ⏳ 計劃中

**優先級說明:**
- ⭐⭐⭐ P0 - 核心功能，需優先完成
- ⭐⭐ P1 - 重要功能，需完成
- ⭐ P2 - 增強功能，可延後

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
   └─ 上傳模特照片 (user/photo) ✅

3. 瀏覽和上傳衣伺
   ├─ 查看衣伺列表 (clothes list) ⏳
   ├─ 上傳衣伺圖片 (upload_image) ✅
   │  └─ 調用 AI 去背和分類
   └─ 標記喜歡的衣伺 (favorites) ✅

4. 虛擬試衣 ✨ 核心功能（Feature 3.1）
   ├─ 發起試穿 (TRYON-001) ✅
   │  ├─ 選擇 2 件衣伺
   │  ├─ AI 合成試衣結果圖
   │  └─ 直接保存到 Model 表
   │
   ├─ 查看試穿歷史 (TRYON-002) ✅
   │  └─ 查看之前的試穿記錄
   │
   └─ 查看試穿詳情 (TRYON-003) ✅
      └─ 查看單筆試穿的完整信息

5. AI 諮詢
   ├─ 智能推薦穿搭 (AI recommendation) 🔄
   │  └─ 通過文字輸入自動生成穿搭推薦
   └─ 文字對話 (AI chat) ⏳
      └─ 獲得穿搭建議和風格諮詢

6. 登出
   └─ 登出系統 (logout) ✅
```

### 虛擬試衣簡化流程圖 ✨ Feature 3.1 流程

```
【使用者虛擬試衣流程】
════════════════════════════════════════════════════════════════

1️⃣ 前端：選擇衣伺
   └─ 手動從衣櫃選擇 2 件衣伺（上衣 + 下衣）

2️⃣ 前端：發送虛擬試衣請求
   └─ POST /combine/user/virtual-try-on
      Headers: Authorization: Bearer <access_token>
      Body: {
        "clothes_ids": ["uuid1", "uuid2"]
      }

3️⃣ 後端：驗證並準備 AI 請求
   ├─ 驗證用戶、衣伺數據（必須 2 件且屬於用戶）
   ├─ 從數據庫獲取：
   │  ├─ 用戶身體測量數據（user_height, user_weight 等）
   │  ├─ 用戶模特照片（user_image_url）
   │  ├─ 衣伺圖片和尺寸數據
   │  └─ user_image_url 必須已設定，否則返回 400
   │
   └─ 組裝 AI 請求所需的 multipart/form-data

4️⃣ 後端：轉發至 AI 後端
   └─ POST http://172.17.0.1:8002/virtual_try_on/clothes/combine
      帶帶上：
      - model_image: 用戶模特照片 (binary)
      - garment_0, garment_1: 2 件衣伺圖片 (binary)
      - model_info: 用戶身體測量數據 (JSON)
      - garments: 衣伺尺寸信息 (JSON)

5️⃣ AI 後端：虛擬試衣合成
   ├─ 接收模特照片和 2 件衣伺
   ├─ 使用深度學習模型進行合成
   └─ 產生合成圖片（PNG 格式）+ 風格分析（JSON）

6️⃣ AI 後端：返回結果
   └─ HTTP/1.1 200 OK
      Content-Type: multipart/mixed
      
      返回內容：
      1️⃣ JSON 元數據
         - message: "200"（表示成功）
         - data.style_name: ["風格1", "風格2", "風格3"]
         - data.file_name: "try_on_outfit_*.png"
      
      2️⃣ PNG 圖片二進位數據

7️⃣ 後端：直接保存到 Model 表
   ├─ 解析 multipart/mixed 回應
   ├─ 上傳合成圖片到 MinIO
   ├─ 創建 Model 記錄：
   │  ├─ f_user_uid: 當前用戶
   │  ├─ model_uid: UUID
   │  ├─ model_picture: MinIO 圖片 URL
   │  ├─ model_style: AI 返回的 style_name 陣列
   │  ├─ clothes_list: 使用衣伺的詳情
   │  └─ ai_response_data: AI 回應完整數據
   │
   └─ 記錄已保存，用戶可立即查看歷史

8️⃣ 後端：返回成功响應
   └─ HTTP/1.1 200 OK
      {
        "success": true,
        "message": "虛擬試穿完成",
        "model_data": {
          "model_uid": "...",
          "model_picture": "http://minio:9000/...",
          "model_style": ["Japanese Style", "Elegant"],
          "clothes_count": 2,
          "ai_response": {...}
        }
      }

9️⃣ 前端：顯示試衣結果
   └─ 顯示合成圖片和分析結果
      用戶可以：
      ├─ 查看虛擬試穿歷史 (GET /combine/user/virtual-try-on-history)
      ├─ 查看詳細信息 (GET /combine/user/virtual-try-on-detail/<model_uid>)
      └─ 再次發起試穿

【狀態說明】
- 試穿結果直接保存到 Model 表
- 虛擬試穿記錄直接對應 Model 表記錄
- 無須額外確認、無須創建 Outfit
- API 簡化為：發起試穿 → 直接保存 → 查看歷史
```

### AI 智能推薦穿搭流程圖 ⭐ Feature AI-002 流程

```
【AI 推薦穿搭完整流程】
════════════════════════════════════════════════════════════════

1️⃣ 前端：用戶輸入文字描述
   └─ 例："今天天氣很好，我要去逛街，希望穿得舒適又時尚"

2️⃣ 前端：發送推薦請求
   └─ POST /aichat_service/recommend/generate
      Headers: Authorization: Bearer <access_token>
      Body: {
        "user_input": "今天天氣很好，我要去逛街，希望穿得舒適又時尚",
        "top_k": 1
      }

3️⃣ 後端：AI 分析層【layer 1】
   ├─ 調用 Gemini API 分析用戶輸入文字
   ├─ 智能提取關鍵詞（多維度分析）：
   │  ├─ 場景/機會：逛街、約會、運動、工作等
   │  ├─ 天氣/季節：晴天、雨天、春夏秋冬等
   │  ├─ 風格偏好：舒適、時尚、簡約、性感等
   │  ├─ 情感狀態：開心、冷靜、自信等
   │  └─ 用戶描述的衣著需求
   │
   ├─ 使用 Gemini 將關鍵詞映射到衣伺標籤：
   │  ├─ clothes_category：T-shirt, Shirt, Pants, Skirt, Jacket 等
   │  ├─ color_name：白色、黑色、藍色、紅色、米色、綠色等
   │  └─ style_name：Casual, Sporty, Elegant, Sexy, Classic 等
   │
   ├─ 設定篩選權重（可調）：
   │  ├─ category: 40%
   │  ├─ color: 30%
   │  └─ style: 30%
   │
   └─ 返回分析結果（JSON 格式）

4️⃣ 後端：衣服篩選層【layer 2】
   ├─ 查詢數據庫中用戶的所有衣伺
   ├─ 根據 AI 提取的關鍵詞進行多維度匹配：
   │  ├─ 檢查 clothes_category 是否匹配推薦分類
   │  ├─ 檢查 color_name 是否匹配推薦顏色（支持模糊匹配）
   │  ├─ 檢查 style_name 是否匹配推薦風格
   │  └─ 計算綜合匹配分數 = (category匹配*0.4 + color匹配*0.3 + style匹配*0.3)
   │
   ├─ 按匹配分數排序衣伺
   ├─ 過濾出得分 ≥ 0.3 的衣伺作為候選池
   ├─ 分離衣伺為：
   │  ├─ 上衣池（top clothes）：category 為 shirt/clothing/top 等
   │  └─ 下衣池（bottom clothes）：category 為 pants/skirt/bottom 等
   │
   └─ 每個池中至少保留 3-5 件候選衣伺

5️⃣ 後端：組合推薦層【layer 3】
   ├─ 從上衣池和下衣池中選擇最佳搭配：
   │  ├─ 策略 1：優先選擇匹配分數最高的組合
   │  │  └─ top 1 + bottom 1
   │  │
   │  ├─ 策略 2：支持多個推薦組合（top_k）
   │  │  └─ 選擇 top_k 個分數最高的上衣
   │  │  └─ 為每個上衣選擇匹配分數最高的下衣
   │  │
   │  └─ 策略 3：驗證顏色和風格搭配
   │     └─ 調用 Gemini 檢驗組合的和諧性
   │        └─ 返回搭配評分（harmony_score）
   │
   └─ 返回選定的衣伺組合（clothes_ids）

6️⃣ 後端：虛擬試穿層【layer 4】
   ├─ 對每一個推薦的衣伺組合，調用虛擬試穿 AI：
   │  └─ POST http://172.17.0.1:8002/virtual_try_on/clothes/combine
   │
   ├─ 轉發數據格式（multipart/form-data，與虛擬試穿相同）：
   │  ├─ Files:
   │  │  ├─ model_image: 用戶模特照片 (binary)
   │  │  ├─ garment_0: 推薦的上衣圖片 (binary)
   │  │  └─ garment_1: 推薦的下衣圖片 (binary)
   │  │
   │  └─ Data:
   │     ├─ model_info: 用戶身體測量數據 (JSON)
   │     └─ garments: 衣伺尺寸信息 (JSON)
   │
   └─ 接收虛擬試穿結果：
      ├─ PNG 合成圖片二進位數據
      └─ JSON metadata（風格分析）

7️⃣ 後端：結果保存層【layer 5】
   ├─ 對每個推薦結果，直接保存到 Model 表：
   │  ├─ f_user_uid: 當前用戶 UUID
   │  ├─ model_uid: 推薦記錄唯一 ID (UUID)
   │  ├─ model_picture: 虛擬試穿合成圖 URL（MinIO）
   │  ├─ model_style: AI 返回的風格分析 (JSON 陣列)
   │  ├─ source: 'ai_recommendation'（標記推薦來源）
   │  ├─ recommendation_context: 用戶原始輸入文字
   │  ├─ recommendation_keywords: AI 提取的結構化關鍵詞 (JSON)
   │  ├─ recommendation_score: 綜合推薦匹配分數 (0.0-1.0)
   │  ├─ clothes_list: 使用的 2 件衣伺詳情 (JSON)
   │  ├─ ai_analysis: AI 分析和推薦理由 (文字說明)
   │  └─ created_at: 推薦生成時間戳
   │
   └─ 記錄已保存到 DB，用戶可立即查看推薦歷史

8️⃣ 後端：返回推薦結果
   └─ HTTP/1.1 200 OK
      {
        "success": true,
        "message": "推薦穿搭生成成功",
        "ai_keywords": ["逛街", "舒適", "時尚", "Casual", "白色", "T-shirt"],
        "recommendations": [
          {
            "rank": 1,
            "model_uid": "550e8400-e29b-41d4-a716-446655440300",
            "model_picture": "http://minio:9000/recommendations/model_uuid.png",
            "recommendation_score": 0.92,
            "score_breakdown": {
              "category_match": 0.95,
              "color_match": 0.90,
              "style_match": 0.90,
              "harmony_score": 0.93
            },
            "clothes_info": {
              "top": {...},
              "bottom": {...}
            },
            "ai_reasoning": "白色 T 恤搭配藍色牛仔褲..."
          },
          // 如果 top_k > 1，返回更多推薦...
        ],
        "total_recommendations": 1
      }

9️⃣ 前端：展示推薦結果
   └─ 依次展示推薦穿搭：
      ├─ 虛擬試穿合成圖片（居中展示）
      ├─ AI 推薦理由/分析說明（下方說明）
      ├─ 衣伺詳情卡片：
      │  ├─ 上衣圖片、分類、顏色、風格
      │  └─ 下衣圖片、分類、顏色、風格
      │
      └─ 用戶操作按鈕：
         ├─ ❤️ 保存推薦到收藏夾
         ├─ 🔄 重新推薦（新的用戶輸入）
         ├─ 📊 查看其他推薦（如果 top_k > 1）
         └─ 🗑️ 刪除推薦

1️⃣0️⃣ 用戶可進行的後續操作
   ├─ 查看推薦歷史 (GET /aichat_service/recommend/history)
   │  └─ 分頁、排序、篩選推薦記錄
   │
   ├─ 查看推薦詳情 (GET /aichat_service/recommend/<model_uid>)
   │  └─ 查看完整的推薦分析和衣伺信息
   │
   ├─ 再次推薦 (POST /aichat_service/recommend/generate)
   │  └─ 輸入新的文字描述，生成新推薦
   │
   └─ 刪除推薦 (DELETE /aichat_service/recommend/<model_uid>)
      └─ 刪除不喜歡的推薦記錄

【核心優勢與特性】
✅ 零手動操作 - 用戶只需輸入文字，系統全自動完成推薦生成
✅ 多維度分析 - 考慮場景、天氣、風格、情感等多個因素
✅ 智能篩選 - 基於衣伺標籤的精準匹配和評分
✅ 搭配驗證 - AI 驗證顏色和風格搭配的和諧性
✅ 虛擬展示 - 自動生成試穿效果圖，讓用戶看到實際效果
✅ 完整保存 - 推薦結果直接保存到 Model 表，用戶隨時可查看
✅ 可追溯 - 保存用戶輸入、AI 關鍵詞、推薦理由等詳細信息
✅ 易擴展 - 可支持多個推薦結果、額外篩選條件等功能擴展

【與虛擬試穿的區別】
┌─────────────────────┬──────────────────┬──────────────────┐
│ 特性                │ 虛擬試穿(TRYON)  │ AI推薦(AI-002)   │
├─────────────────────┼──────────────────┼──────────────────┤
│ 衣伺選擇            │ 用戶手動選擇      │ AI 自動推薦       │
│ 驅動方式            │ 手動選擇          │ 自然語言輸入      │
│ 衣伺篩選            │ 無（直接使用）    │ 多維度智能篩選    │
│ 搭配驗證            │ 無                │ AI 驗證和諧性    │
│ 結果保存            │ Model 表          │ Model 表          │
│ 源標記              │ source=vitual_tryon │ source=ai_recommendation │
│ 推薦理由            │ 無                │ 詳細的 AI 分析文本 │
│ 使用場景            │ 用戶有想法，驗證效果 │ 用戶無想法，需要靈感 │
└─────────────────────┴──────────────────┴──────────────────┘
```

### 管理員穿搭管理流程 ✨ 新增

```
【後台管理員流程】
1. 管理員登入
   └─ 使用管理員帳號登入 ✅

2. 穿搭管理（combine 應用）
   ├─ 查看所有穿搭列表
   │  └─ GET /combine/outfit/?limit=100
   ├─ 查看虛擬試衣記錄
   │  └─ 分析用戶試衣行為
   ├─ 刪除不當穿搭
   │  └─ DELETE /combine/outfit/<uid>/delete
   └─ 數據管理
      └─ 統計穿搭、虛擬試衣等使用數據

3. 衣伺管理 (CRUD)
   ├─ 新增衣伺 (POST /picture/clothes/) ✅
   │  ├─ 設定衣伺分類 (category)
   │  ├─ 設定尺寸數據 (arm_length, shoulder_width 等)
   │  ├─ 上傳衣伺圖片 URL
   │  ├─ 添加顏色標籤 (colors)
   │  └─ 添加風格標籤 (styles)
   ├─ 查看衣伺列表 (GET /picture/clothes/) ✅
   │  └─ 支持分頁和分類篩選
   ├─ 查看衣伺詳情 (GET /picture/clothes/{id}/) ✅
   │  └─ 包含所有顏色和風格信息
   ├─ 更新衣伺 (PUT /picture/clothes/{id}/) ✅
   │  └─ 修改分類、尺寸、顏色、風格等
   └─ 刪除衣伺 (DELETE /picture/clothes/{id}/) ✅
      └─ 自動刪除相關顏色和風格

4. 數據檢查
   └─ 確保衣伺和穿搭數據完整和正確
```

---

## � 數據庫模型更新

### Model 表欄位擴展（支持 AI 推薦功能）

為了支持 AI 推薦穿搭功能，需要在 `combine.models.Model` 表中添加以下新欄位：

| 欄位名 | 類型 | 必填 | 說明 | 預設值 | 備註 |
|--------|------|------|------|--------|------|
| `source` | CharField | 是 | 推薦來源標記 | `virtual_try_on` | 取值：`virtual_try_on` (虛擬試穿) 或 `ai_recommendation` (AI推薦) |
| `recommendation_context` | TextField | 否 | 用戶輸入文字 | NULL | 記錄 AI 推薦時用戶輸入的原始文字 |
| `recommendation_keywords` | JSONField | 否 | 提取的關鍵詞 | NULL | JSON 格式，包含 occasion/weather/style/emotion 等結構化關鍵詞 |
| `recommendation_score` | FloatField | 否 | 推薦匹配分數 | 0.0 | 範圍 0.0-1.0，表示推薦的匹配度 |
| `ai_analysis` | TextField | 否 | AI 推薦理由 | NULL | AI 生成的推薦分析文本說明 |

**🔧 數據庫遷移範例**:
```python
from django.db import models

class Model(models.Model):
    # ... 現有欄位 ...
    
    # 新增欄位
    SOURCE_CHOICES = [
        ('virtual_try_on', 'Virtual Try-On'),
        ('ai_recommendation', 'AI Recommendation'),
    ]
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='virtual_try_on',
        help_text="推薦來源：虛擬試穿或 AI 推薦"
    )
    
    recommendation_context = models.TextField(
        null=True,
        blank=True,
        help_text="AI 推薦時用戶輸入的文字"
    )
    
    recommendation_keywords = models.JSONField(
        null=True,
        blank=True,
        help_text="AI 提取的結構化關鍵詞（JSON 格式）"
    )
    
    recommendation_score = models.FloatField(
        default=0.0,
        help_text="推薦匹配分數（0.0-1.0）"
    )
    
    ai_analysis = models.TextField(
        null=True,
        blank=True,
        help_text="AI 推薦的分析和理由"
    )
    
    class Meta:
        # 添加索引以加快查詢
        indexes = [
            models.Index(fields=['source', 'created_at']),
            models.Index(fields=['recommendation_score']),
        ]
```

**✅ 向後兼容**:
- 虛擬試穿功能保持不變，`source` 默認為 `virtual_try_on`
- 現有的虛擬試穿數據不受影響
- AI 推薦數據使用 `source='ai_recommendation'` 區分
- 查詢時可以按 source 欄位過濾，分別獲取虛擬試穿或推薦記錄

---

## �📝 開發優先級建議

### 第一階段（核心功能）- ✅ 已完成（包括虛擬試衣）
1. ✅ 使用者註冊
2. ✅ 使用者登入
3. ✅ 使用者登出
4. ✅ 使用者上傳衣伺圖片 + AI 去背
5. ✅ 使用者上傳模特照片 + AI 去背
6. ✅ **OUTFIT-001** 查看穿搭列表
7. ✅ **OUTFIT-002** 新增穿搭組合
8. ✅ **OUTFIT-003-01** 發起虛擬試衣
9. ✅ **OUTFIT-003-02** 確認保存虛擬試衣
10. ✅ **OUTFIT-004-01** 標記穿搭為喜歡
11. ✅ **OUTFIT-004-02** 穿搭評分評論

### 第二階段（基礎管理）- 1-2 週
1. 🔄 上傳模特基本資料（身體數據） - `/account/user/user_info`
2. ⏳ 查看衣伺總覽列表 (GET `/picture/clothes/`)
3. ✅ 設定衣伺資料（後台管理）
4. ✅ 查看收藏列表

### 第三階段（穿搭進階功能）- 1-2 週
1. ✅ 編輯穿搭 (PUT `/combine/outfit/<uid>/update`)
2. ✅ 刪除穿搭 (DELETE `/combine/outfit/<uid>/delete`)
3. ✅ 查看穿搭詳情 (GET `/combine/outfit/<uid>/`)
4. ✅ 拒絕虛擬試衣 (POST `/combine/virtual-try-on/<uid>/reject`)
5. ✅ 查看我的穿搭 (GET `/combine/outfit/my`)
6. ✅ 查看我的收藏 (GET `/combine/outfit/my/favorites`)

### 第四階段（增強功能）- 2-4 週
1. 🔄 **AI 智能推薦穿搭** - `/aichat_service/recommend/generate` ⭐ 新增
   - 用戶輸入文字 → AI 分析 → 自動篩選衣服 → 虛擬試穿合成 → 保存結果
   - 依賴虛擬試穿功能和 Gemini API
2. ⏳ AI 文字對話 - `/aichat_service/chat`
3. ⏳ 通用圖片上傳 - `/picture/upload/`
4. ⏳ 圖片管理功能
5. ⏳ 穿搭分享功能
6. ⏳ 虛擬試衣歷史記錄

### 開發框架
- **框架**: Django + Django REST Framework
- **數據庫**: PostgreSQL
- **存儲**: MinIO (兼容 AWS S3 API)
- **認證**: JWT (JSON Web Token)
- **AI 集成**: FastAPI 後端伺務
- **虛擬試衣 AI**: 深度學習模型（衣伺檢測、姿勢估計、合成）

---

## 🏗️ 新模組實現建議（aichat_service）

### 模組結構

```
aichat_service/
├── __init__.py
├── admin.py
├── apps.py
├── models.py              # 推薦相關數據模型（可選）
├── serializers.py         # 序列化器
├── views.py              # API 視圖
├── urls.py               # URL 路由
├── services/
│   ├── __init__.py
│   ├── ai_analyzer.py    # AI 分析和關鍵詞提取
│   ├── clothes_matcher.py # 衣服篩選和匹配
│   ├── recommender.py    # 推薦邏輯
│   └── virtualtryon_client.py # 虛擬試穿 AI 客戶端
├── utils/
│   ├── __init__.py
│   ├── constants.py      # 常數定義（關鍵詞映射等）
│   └── helpers.py        # 輔助函數
├── tests/
│   ├── __init__.py
│   ├── test_views.py
│   ├── test_services.py
│   └── test_models.py
└── management/
    └── commands/
        └── generate_sample_recommendations.py  # 測試命令
```

### 核心組件說明

#### 1. AI 分析器（ai_analyzer.py）
```python
class AIAnalyzer:
    """使用 Gemini API 分析用戶輸入和提取關鍵詞"""
    
    def analyze_user_input(self, user_input: str) -> dict:
        """
        分析用戶輸入，提取結構化關鍵詞
        
        返回格式：
        {
            "occasion": ["逛街"],
            "weather": ["晴天"],
            "style": ["舒適", "時尚"],
            "emotion": ["開心"],
            "recommended_categories": ["T-shirt", "Pants"],
            "recommended_colors": ["白色", "藍色"],
            "recommended_styles": ["Casual"]
        }
        """
    
    def verify_color_harmony(self, top_colors: list, bottom_colors: list) -> float:
        """驗證顏色搭配的和諧性，返回評分 0.0-1.0"""
```

#### 2. 衣服匹配器（clothes_matcher.py）
```python
class ClothesMatcher:
    """根據關鍵詞篩選和匹配衣服"""
    
    def filter_clothes_by_keywords(self, user, keywords: dict) -> dict:
        """
        根據 AI 提取的關鍵詞過濾衣服
        
        返回：
        {
            "top_candidates": [衣服列表，按分數排序],
            "bottom_candidates": [衣服列表，按分數排序]
        }
        """
    
    def calculate_matching_score(self, clothes, keywords) -> float:
        """計算衣服與關鍵詞的匹配分數"""
    
    def find_best_combination(self, top_candidates, bottom_candidates) -> tuple:
        """從候選衣服中選擇最佳搭配"""
```

#### 3. 推薦器（recommender.py）
```python
class RecommendationEngine:
    """推薦穿搭的核心引擎"""
    
    async def generate_recommendations(self, user, user_input: str, top_k: int = 1) -> list:
        """
        生成推薦穿搭
        
        流程：
        1. AI 分析 → 提取關鍵詞
        2. 衣服篩選 → 根據關鍵詞過濾
        3. 組合推薦 → 選擇最佳搭配
        4. 虛擬試穿 → 生成合成圖
        5. 結果保存 → 保存到 Model 表
        
        返回：推薦結果列表（Model 對象）
        """
    
    async def save_recommendation(self, user, top_clothes, bottom_clothes, 
                                   context, keywords, score, reasoning) -> Model:
        """將推薦結果保存到 Model 表"""
```

#### 4. 虛擬試穿客戶端（virtualtryon_client.py）
```python
class VirtualTryOnClient:
    """與虛擬試穿 AI 後端通信"""
    
    async def generate_tryon_image(self, model_image_url: str, 
                                    garment_images: list, 
                                    model_info: dict, 
                                    garments_info: list) -> dict:
        """
        調用虛擬試穿 AI，生成合成圖
        
        返回：
        {
            "image_url": "MinIO URL",
            "style_names": ["Casual", "Sporty"],
            "ai_response": {...}
        }
        """
```

### API 實現檢查清單

- [ ] POST `/aichat_service/recommend/generate` - 生成推薦
  - [ ] 參數驗證（user_input 長度、top_k 範圍）
  - [ ] 用戶狀態檢查（是否有模特照片、身體數據）
  - [ ] AI 分析模塊集成
  - [ ] 衣服篩選邏輯
  - [ ] 虛擬試穿調用
  - [ ] 結果保存到 Model 表
  - [ ] 錯誤處理（AI 超時、無衣服等）

- [ ] GET `/aichat_service/recommend/history` - 查看歷史
  - [ ] 分頁支持
  - [ ] 排序選項（newest/oldest/score_high）
  - [ ] 過濾選項（source='ai_recommendation'）
  - [ ] 授權檢查

- [ ] GET `/aichat_service/recommend/<model_uid>` - 查看詳情
  - [ ] 授權檢查（只能查看自己的推薦）
  - [ ] 完整數據返回

- [ ] DELETE `/aichat_service/recommend/<model_uid>` - 刪除推薦
  - [ ] 授權檢查
  - [ ] 級聯刪除相關數據（如需要）

### 環境變數配置

```bash
# Gemini API
GEMINI_API_KEY=your_api_key
GEMINI_API_ENDPOINT=https://generativelanguage.googleapis.com/v1beta/models

# 虛擬試穿 AI 服務
VIRTUALTRYON_API_URL=http://172.17.0.1:8002
VIRTUALTRYON_TIMEOUT=60  # 秒

# 推薦配置
RECOMMENDATION_MIN_SCORE=0.3  # 最低匹配分數
RECOMMENDATION_SEARCH_TOP_K=5  # 每個分類保留候選數
```

---

## 🔐 權限管理

### 角色權限對照表

| 功能 | 匿名用戶 | 認證用戶 | 管理員 |
|------|---------|---------|--------|
| 註冊 | ✅ | ❌ | ❌ |
| 登入 | ✅ | ❌ | ✅ |
| 登出 | ❌ | ✅ | ✅ |
| 查看衣伺列表 | ✅ | ✅ | ✅ |
| 查看穿搭列表 | ✅ | ✅ | ✅ |
| 上傳圖片 | ❌ | ✅ | ✅ |
| 設定衣伺資料 | ❌ | ❌ | ✅ |
| 新增穿搭 | ❌ | ✅ | ✅ |
| 編輯/刪除穿搭 | ❌ | ⚠️ (自己) | ✅ |
| 發起虛擬試衣 | ❌ | ✅ | ✅ |
| 標記喜歡 | ❌ | ✅ | ✅ |
| 評分評論 | ❌ | ✅ | ✅ |
| 刪除用戶 | ❌ | ⚠️ (自己) | ✅ |
| AI 對話 | ❌ | ✅ | ✅ |

### 穿搭模組權限詳解

| 操作 | 權限要求 | 說明 |
|------|---------|------|
| GET /combine/outfit/ | 任何人 | 查看所有公開穿搭 |
| POST /combine/outfit/create | 認證用戶 | 建立新穿搭 |
| GET /combine/outfit/<uid>/ | 任何人 | 查看穿搭詳情（包含讚數和評分） |
| PUT /combine/outfit/<uid>/update | 擁有者\|管理員 | 編輯穿搭（只有創建者或管理員） |
| DELETE /combine/outfit/<uid>/delete | 擁有者\|管理員 | 刪除穿搭 |
| POST /combine/virtual-try-on/ | 認證用戶 | 發起虛擬試衣 |
| POST /combine/virtual-try-on/<uid>/confirm | 試衣者 | 確認並保存虛擬試衣結果 |
| POST /combine/virtual-try-on/<uid>/reject | 試衣者 | 拒絕虛擬試衣結果 |
| PATCH /combine/outfit/<uid>/favorite | 認證用戶 | 標記喜歡或取消喜歡 |
| POST /combine/outfit/<uid>/rating | 認證用戶 | 對穿搭進行評分和評論 |
| GET /combine/outfit/my | 認證用戶 | 查看我建立的穿搭 |
| GET /combine/outfit/my/favorites | 認證用戶 | 查看我的收藏列表 |

---

## 📞 API 版本

- **當前版本**: v1
- **API 基礎 URL**: `http://localhost:30000/api/v1/`
- **WebSocket 支持**: 計劃在 v2
- **向後兼容**: v1 API 不會中斷

### combine 應用 API 前綴
- **API 路徑**: `/combine/`
- **主要功能**: 穿搭管理和虛擬試衣
- **新增日期**: 2026-03-27

---

> 最後更新：2026-03-27  
> 包含內容：虛擬試衣完整功能、穿搭管理模塊、combine 應用架構
> 下次審查：2026-04-27
