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
1. **獲取衣櫃資料**: 系統從資料庫讀取該用戶所有擁有的衣服列表（包含款式、顏色、分類等）。
2. **AI 分析與挑選階段**: 將用戶的輸入文字，連同用戶的衣服列表一併發送給 Gemini API。Gemini 會理解用戶需求，並**直接從用戶既有的衣服清單中挑選出最適合的一件上衣和一件下裝**，同時給出搭配理由。
3. **虛擬試穿階段**: 將選定的衣服組合丟入虛擬試穿 AI 進行合成。
4. **結果保存階段**: 將合成結果直接保存到 Model 表（並標記 source 為 'ai_recommendation'）。

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
        "top_k": 1  // 目前系統返回 1 個最佳推薦組合
      }

3️⃣ 後端：第一層 - 獲取用戶所有衣伺
   ├─ 從資料庫讀取該用戶上傳的所有衣服
   └─ 提取每件衣服的：ID、分類、顏色和風格標籤

4️⃣ 後端：第二層 - AI 分析與挑選 (Gemini)
   ├─ 構建 Prompt，包含「用戶輸入要求」與「用戶衣櫃清單」
   ├─ 調用 Gemini API，讓 AI 在清單中直接選擇：
   │  ├─ 一件最合適的上衣 (top)
   │  └─ 一件最合適的下衣 (bottom)
   ├─ AI 同時輸出搭配理由（例如：「白色 T 恤搭配藍色牛仔褲非常休閒舒適...」）
   └─ 解析 Gemini 返回的衣服 ID 與理由 (JSON 格式)

5️⃣ 後端：第三層 - 組合與數據準備
   ├─ 使用 AI 選出的衣服 ID，從資料庫讀取完整的衣服詳情與圖片
   └─ 準備虛擬試穿所需要的數據格式

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
    "top_k": 1
  }
  ```

  **📝 參數說明**:
  - **user_input** (必填): 用戶輸入的自然語言文字（1-500 字符）
  - **top_k** (可選，默認 1): 系統目前專注於返回最佳的 1 個推薦結果

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
    "ai_keywords": ["Casual", "Sporty"],
    "recommendations": [
      {
        "rank": 1,
        "model_uid": "550e8400-e29b-41d4-a716-446655440300",
        "model_picture": "http://192.168.233.128:9000/recommendations/model_550e8400.png",
        "recommendation_score": 0.95,
        "clothes_info": {
          "top": {
            "clothes_uid": "550e8400-e29b-41d4-a716-446655440010",
            "clothes_category": "T-shirt",
            "clothes_image_url": "..."
          },
          "bottom": {
            "clothes_uid": "550e8400-e29b-41d4-a716-446655440011",
            "clothes_category": "Pants",
            "clothes_image_url": "..."
          }
        },
        "ai_reasoning": "白色 T 恤搭配藍色牛仔褲非常休閒舒適，適合逛街行程。"
      }
    ],
    "total_recommendations": 1
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
    "recommendation_score": 0.95,
    "recommendation_context": "今天天氣很好，我要去逛街，希望穿得舒適又時尚",
    "recommendation_keywords": {
      "recommended_styles": ["Casual", "Sporty"],
      "reasoning": "白色 T 恤搭配藍色牛仔褲非常休閒舒適，適合逛街行程。"
    },
    "model_picture": "http://192.168.233.128:9000/recommendations/model_550e8400.png",
    "model_style": ["Casual", "Sporty", "Elegant"],
    "clothes_list": [
      {
        "clothes_uid": "550e8400-e29b-41d4-a716-446655440010",
        "clothes_category": "T-shirt",
        "clothes_image_url": "..."
      },
      {
        "clothes_uid": "550e8400-e29b-41d4-a716-446655440011",
        "clothes_category": "Pants",
        "clothes_image_url": "..."
      }
    ],
    "ai_reasoning": "白色 T 恤搭配藍色牛仔褲非常休閒舒適，適合逛街行程。",
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


---
