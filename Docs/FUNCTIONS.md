# 系統功能文檔

> 更新時間: 2026-03-28  
> 說明: test_project 系統完整功能一覽及詳細說明
> 最新更新: 數據庫優化 - 刪除 outfit/outfit_clothes/virtual_try_on/outfit_favorite 冗余表，保留虛擬試穿核心功能（Feature 3.1）

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

用戶照片和衣服資料的上傳、查看和管理（包括：衣服圖片、用戶模特照片）

### 2.1 用戶新增衣服（上傳圖片 + AI 處理）
- **功能編號**: `CLOTHES-001`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/picture/clothes/` ⭐ (統一端點)
- **請求格式**: `multipart/form-data`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 用戶上傳衣服**圖片** + **衣服尺寸信息**
  - 支持可選的衣服尺寸參數：袖長、褲長、肩寬、腰圍
  - 後端自動轉發給 AI 進行去背處理，包含尺寸參數
  - AI 自動分析並提取：衣服分類、顏色、風格
  - 處理後的圖片存儲到 MinIO，返回 URL
  - 將完整信息（包括衣服尺寸）存儲到數據庫
  - 用戶無需手動輸入顏色和風格（由 AI 自動提取）

**流程說明**:
```
① 用戶上傳圖片 + 衣服尺寸 (袖長、褲長、肩寬、腰圍)
    ↓
② 後端驗證衣服尺寸參數範圍
    ↓
③ 後端轉發給 AI 後端進行去背處理（包含尺寸）
    ↓
④ AI 返回：
   - 去背後的圖片
   - 衣服分類（clothes_category）
   - 風格列表（style_name x 3）
   - 顏色列表（color_name x 3）
    ↓
⑤ 後端將圖片存儲到 MinIO
    ↓
⑥ 將完整數據存儲到 DB：
   - Clothes 表：基本信息 + 圖片 URL + 衣服尺寸
   - Style 表：3 筆風格
   - Color 表：3 筆顏色
    ↓
⑦ 返回完整的衣服詳情給前端（包含尺寸數據）
```

- **輸入參數** (form-data):
  ```json
  {
    "image_data": {
      "type": "file (binary)",
      "required": true,
      "description": "衣服圖片文件（二進位數據）",
      "accepted_formats": ["JPG", "PNG", "GIF", "WebP"],
      "max_size": "10MB"
    },
    "clothes_arm_length": {
      "type": "integer",
      "required": false,
      "default": 0,
      "range": [0, 200],
      "unit": "cm",
      "description": "衣服袖長（衣服的胳膊長度）"
    },
    "clothes_leg_length": {
      "type": "integer",
      "required": false,
      "default": 0,
      "range": [0, 150],
      "unit": "cm",
      "description": "衣服褲長（衣服的褲子長度）"
    },
    "clothes_shoulder_width": {
      "type": "integer",
      "required": false,
      "default": 0,
      "range": [0, 200],
      "unit": "cm",
      "description": "衣服肩寬（衣服肩膀的寬度）"
    },
    "clothes_waistline": {
      "type": "integer",
      "required": false,
      "default": 0,
      "range": [0, 300],
      "unit": "cm",
      "description": "衣服腰圍（衣服腰部的圓周）"
    }
  }
  ```

  **📝 參數說明**:
  - **必填參數**: `image_data` (衣服圖片文件)
  - **可選參數**: `clothes_arm_length`, `clothes_leg_length`, `clothes_shoulder_width`, `clothes_waistline` (所有尺寸參數不提供時默認為 0)
  - 衣服尺寸參數必須是 **非負整數**，超出範圍將返回 400 Bad Request
  - 衣服尺寸數據會被發送給 AI 後端進行智能處理
  - 衣服尺寸數據會被持久化存儲在數據庫中

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
        "arm_length": 65,           // 衣服袖長（cm）
        "leg_length": 92,           // 衣服褲長（cm）
        "shoulder_width": 45,       // 衣服肩寬（cm）
        "waistline": 80             // 衣服腰圍（cm）
      }
    }
  }
  ```

- **失敗回應**:
  - `400 Bad Request`: 缺少圖片、檔案驗證失敗或衣服尺寸參數無效
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
      "message": "衣服尺寸參數必須為整數"
    }
    ```
    或
    ```json
    {
      "success": false,
      "message": "衣服袖長必須在 0 到 200 cm 之間"
    }
    ```
  - `401 Unauthorized`: 未認證或 Token 過期
  - `415 Unsupported Media Type`: 上傳非圖片檔案
  - `422 Unprocessable Entity`: 圖片過於模糊
  - `503 Service Unavailable`: AI 服務或存儲服務不可用
  - `504 Gateway Timeout`: AI 處理逾時（超過 120 秒）

**📊 統一端點 CRUD 操作表** ⭐ 所有衣服操作都經由同一端點：

| HTTP 方法 | API 路徑 | 操作 | 身份要求 | 返回狀態碼 |
|----------|---------|------|---------|----------|
| **POST** | `/picture/clothes/` | ✏️ 新增衣服 | 認證用戶 | 201 |
| **GET** | `/picture/clothes/my` | 📋 查看我的衣服 | 認證用戶 | 200 |
| **GET** | `/picture/clothes/<id>/` | 👁️ 查看衣服詳情 | 認證用戶 | 200 |
| **PUT** | `/picture/clothes/<id>/` | ✏️ 更新衣服 | 擁有者/管理員 | 200 |
| **DELETE** | `/picture/clothes/<id>/` | 🗑️ 刪除衣服 | 擁有者/管理員 | 200 |

**✅ 確認：統一端點 `/picture/clothes/` 可以完整支持衣服的 CRUD 操作**

**📏 衣服尺寸參數驗證規則**:

| 參數名 | 範圍 | 默認值 | 說明 |
|-------|------|--------|------|
| `clothes_arm_length` | 0-200 cm | 0 | 衣服袖長，不能為負數 |
| `clothes_leg_length` | 0-150 cm | 0 | 衣服褲長，不能為負數 |
| `clothes_shoulder_width` | 0-200 cm | 0 | 衣服肩寬，不能為負數 |
| `clothes_waistline` | 0-300 cm | 0 | 衣服腰圍，不能為負數 |

**✅ 驗證流程**:
1. 將參數轉換為整數，若非整數格式則返回 400 Bad Request
2. 檢查是否在允許的範圍內，若超出範圍則返回 400 Bad Request
3. 所有參數都是可選的，可完全不提供或只提供部分參數
4. 不提供時默認為 0，系統仍然正常處理

---

### 2.2 用戶查看喜歡的衣服/穿搭列表
- **功能編號**: `CLOTHES-003`
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

#### 2.2.1 標記衣服為喜歡
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
  - `404 Not Found`: 衣服不存在
  - `500 Internal Server Error`: 伺服器內部錯誤

**📊 快速參考表** ⭐ 衣服收藏相關操作：

| 操作 | HTTP 方法 | API 路徑 | 身份要求 | 返回狀態碼 |
|------|----------|---------|---------|----------|
| 查看喜歡的衣服 | GET | `/picture/clothes/favorites` | 認證用戶 | 200 |
| 標記為喜歡 | PATCH | `/picture/clothes/<id>/favorite` | 認證用戶 | 200 |
| 取消喜歡 | PATCH | `/picture/clothes/<id>/favorite` | 認證用戶 | 200 |

**🔄 工作流程**：

```
1. 用戶查看衣服詳情
   ├─ GET /picture/clothes/<id>/
   └─ 獲得完整的衣服信息（包含 clothes_favorite 當前狀態）

2. 標記為喜歡
   ├─ PATCH /picture/clothes/<id>/favorite
   ├─ Body: {"favorite": true}
   └─ 返回成功狀態

3. 查看所有喜歡的衣服
   ├─ GET /picture/clothes/favorites
   ├─ 支持分頁 (?page=1&limit=20)
   └─ 返回標記為喜歡的衣服列表

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

#### 2.3.1 上傳/更新模特照片
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
  - `503 Service Unavailable`: MinIO 存儲服務不可用
  - `500 Internal Server Error`: 伺服器內部錯誤

**📝 操作說明**:
- 上傳新照片會自動覆蓋舊照片（更新 `user_image_url`）
- 新的 `user_image_url` 會立即用於虛擬試穿功能
- 推薦上傳全身照以獲得最佳虛擬試穿效果

---

#### 2.3.2 查看當前模特照片
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
  - `500 Internal Server Error`: 伺服器內部錯誤

**📝 說明**:
- 如果用戶未上傳照片，返回 404 且提示「未設定模特照片」
- 前端應該在虛擬試穿前檢查此端點，確認照片已設定

---

**📊 操作表** ⭐ 用戶模特照片管理（簡化設計）：

| HTTP 方法 | API 路徑 | 操作 | 說明 | 返回狀態碼 |
|----------|---------|------|------|----------|
| **POST** | `/picture/user/photo` | ⬆️ 上傳/更新照片 | 上傳新照片並自動更新 user_image_url | 201/200 |
| **GET** | `/picture/user/photo` | 👁️ 查看當前照片 | 查看當前的模特照片 URL | 200 |

**✅ 確認設計**:
- 簡化為只需 2 個操作：上傳和查看
- 一個用戶同時只有 1 張活跃的模特照片
- 上傳新照片會覆蓋舊照片（實現自動更新）
- 虛擬試穿會自動讀取 user_image_url，無須額外操作

---

##  三、虛擬試穿模塊

使用者透過自己衣櫃內既有衣服，挑選 2 件衣服進行虛擬試穿。後端接收請求後，從資料庫讀取衣服與模特資料，組裝成 AI 後端要求的格式，取得合併結果後直接保存到 Model 表。

**📌 重要說明**：虛擬試穿為核心功能（Feature 3.1），重點在請求組裝、AI 整合、結果保存（Model 表）與歷史查詢。

### 3.1 使用者發起虛擬試穿（選取 2 件衣服）
- **功能編號**: `TRYON-001`
- **模組**: `combine`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/combine/user/virtual-try-on`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 使用者從自己資料庫既有衣服中選取 2 件進行試穿
  - 後端查詢 2 件衣服圖片與尺寸資料
  - 後端使用使用者個人檔案中的模特照片（`user_image_url`）與身體測量資料
  - 後端打包並轉發給 AI 後端進行合併試穿
  - 後端解析 AI 回傳並保存試穿結果

**流程說明**:
```
① 前端送出試穿請求（2 件衣服）
    ↓
② 後端驗證衣服數量與歸屬權限
    ↓
③ 後端查詢衣服資料 + 使用者模特照片（user_image_url） + 身體測量
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
  - `clothes_ids` 中衣服必須存在，且必須屬於當前使用者
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
    "garment_0": "<二進位衣服圖片1>",
    "garment_1": "<二進位衣服圖片2>"
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
- `2400` - 衣服檢測失敗
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
  - `400 Bad Request`: 衣服數量錯誤、參數格式錯誤、未設定用戶模特照片
  - `401 Unauthorized`: 未登入或 Token 無效
  - `403 Forbidden`: 衣服不屬於當前使用者
  - `404 Not Found`: 衣服不存在
  - `503 Service Unavailable`: AI 服務不可用
  - `504 Gateway Timeout`: AI 合併逾時
  - `500 Internal Server Error`: 伺服器內部錯誤

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
  - `500 Internal Server Error`: 伺服器內部錯誤

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
  - 返回衣服清單、結果圖片、AI metadata

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
  - `500 Internal Server Error`: 伺服器內部錯誤

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
  - `500 Internal Server Error`: 伺服器內部錯誤

---

### 3.5 試穿 API 快速參考表

| 功能 | HTTP 方法 | API 路徑 | 認證 | 返回狀態碼 |
|------|----------|---------|------|----------|
| 發起試穿（選 2 件衣服） | POST | `/combine/user/virtual-try-on` | 必須 | 200 |
| 查看我的試穿歷史 | GET | `/combine/user/virtual-try-on-history` | 必須 | 200 |
| 查看單筆試穿詳情 | GET | `/combine/user/virtual-try-on-detail/<model_uid>` | 必須 | 200 |
| 刪除試穿結果 | DELETE | `/combine/user/virtual-try-on-delete/<model_uid>` | 必須 | 200 |

---

## 🤖 四、AI 功能模塊

AI 相關的智能功能

### 4.1 使用者與 AI 文字對話
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

### 第一部分：用戶賬戶和衣服管理

| # | 功能名稱 | 模組 | Actor | HTTP 方法 | 優先級 | 狀態 | API 端點 |
|---|---------|------|-------|----------|--------|------|---------|
| 1 | 使用者註冊 | accounts | user | POST | ⭐⭐⭐ | ✅ | `/account/user/register` |
| 2 | 使用者登入 | accounts | user | POST | ⭐⭐⭐ | ✅ | `/account/user/login` |
| 3 | 使用者登出 | accounts | user | POST | ⭐⭐⭐ | ✅ | `/account/user/logout` |
| 4 | 使用者刪除帳號 | accounts | user | POST | ⭐⭐ | ✅ | `/account/user/delete` |
| 5 | 上傳模特基本資料 | accounts | user | POST | ⭐⭐⭐ | 🔄 | `/account/user/user_info` |
| 6 | 設定衣服資料 | picture | admin | POST/PUT | ⭐⭐⭐ | ✅ | `/picture/clothes/` |
| 7 | 新增衣服（上傳圖片 + AI 處理） | picture | user | POST | ⭐⭐⭐ | ✅ | `/picture/clothes/` |
| 8 | 查看喜歡的衣服 | picture | user | GET | ⭐⭐ | ✅ | `/picture/clothes/favorites` |
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
| 14 | AI 文字對話 | picture/ai | user | POST | ⭐⭐ | 🔄 | `/ai/chat` |

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

3. 瀏覽和上傳衣服
   ├─ 查看衣服列表 (clothes list) ⏳
   ├─ 上傳衣服圖片 (upload_image) ✅
   │  └─ 調用 AI 去背和分類
   └─ 標記喜歡的衣服 (favorites) ✅

4. 虛擬試衣 ✨ 核心功能（Feature 3.1）
   ├─ 發起試穿 (TRYON-001) ✅
   │  ├─ 選擇 2 件衣服
   │  ├─ AI 合成試衣結果圖
   │  └─ 直接保存到 Model 表
   │
   ├─ 查看試穿歷史 (TRYON-002) ✅
   │  └─ 查看之前的試穿記錄
   │
   └─ 查看試穿詳情 (TRYON-003) ✅
      └─ 查看單筆試穿的完整信息

5. AI 諮詢
   ├─ 文字對話 (AI chat) 🔄
   └─ 獲得穿搭建議

6. 登出
   └─ 登出系統 (logout) ✅
```

### 虛擬試衣簡化流程圖 ✨ Feature 3.1 流程

```
【使用者虛擬試衣流程】
════════════════════════════════════════════════════════════════

1️⃣ 前端：選擇衣服
   └─ 手動從衣櫃選擇 2 件衣服（上衣 + 下衣）

2️⃣ 前端：發送虛擬試衣請求
   └─ POST /combine/user/virtual-try-on
      Headers: Authorization: Bearer <access_token>
      Body: {
        "clothes_ids": ["uuid1", "uuid2"]
      }

3️⃣ 後端：驗證並準備 AI 請求
   ├─ 驗證用戶、衣服數據（必須 2 件且屬於用戶）
   ├─ 從數據庫獲取：
   │  ├─ 用戶身體測量數據（user_height, user_weight 等）
   │  ├─ 用戶模特照片（user_image_url）
   │  ├─ 衣服圖片和尺寸數據
   │  └─ user_image_url 必須已設定，否則返回 400
   │
   └─ 組裝 AI 請求所需的 multipart/form-data

4️⃣ 後端：轉發至 AI 後端
   └─ POST http://172.17.0.1:8002/virtual_try_on/clothes/combine
      帶帶上：
      - model_image: 用戶模特照片 (binary)
      - garment_0, garment_1: 2 件衣服圖片 (binary)
      - model_info: 用戶身體測量數據 (JSON)
      - garments: 衣服尺寸信息 (JSON)

5️⃣ AI 後端：虛擬試衣合成
   ├─ 接收模特照片和 2 件衣服
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
   │  ├─ clothes_list: 使用衣服的詳情
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

3. 衣服管理 (CRUD)
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

4. 數據檢查
   └─ 確保衣服和穿搭數據完整和正確
```

---

## 📝 開發優先級建議

### 第一階段（核心功能）- ✅ 已完成（包括虛擬試衣）
1. ✅ 使用者註冊
2. ✅ 使用者登入
3. ✅ 使用者登出
4. ✅ 使用者上傳衣服圖片 + AI 去背
5. ✅ 使用者上傳模特照片 + AI 去背
6. ✅ **OUTFIT-001** 查看穿搭列表
7. ✅ **OUTFIT-002** 新增穿搭組合
8. ✅ **OUTFIT-003-01** 發起虛擬試衣
9. ✅ **OUTFIT-003-02** 確認保存虛擬試衣
10. ✅ **OUTFIT-004-01** 標記穿搭為喜歡
11. ✅ **OUTFIT-004-02** 穿搭評分評論

### 第二階段（基礎管理）- 1-2 週
1. 🔄 上傳模特基本資料（身體數據） - `/account/user/user_info`
2. ⏳ 查看衣服總覽列表 (GET `/picture/clothes/`)
3. ✅ 設定衣服資料（後台管理）
4. ✅ 查看收藏列表

### 第三階段（穿搭進階功能）- 1-2 週
1. ✅ 編輯穿搭 (PUT `/combine/outfit/<uid>/update`)
2. ✅ 刪除穿搭 (DELETE `/combine/outfit/<uid>/delete`)
3. ✅ 查看穿搭詳情 (GET `/combine/outfit/<uid>/`)
4. ✅ 拒絕虛擬試衣 (POST `/combine/virtual-try-on/<uid>/reject`)
5. ✅ 查看我的穿搭 (GET `/combine/outfit/my`)
6. ✅ 查看我的收藏 (GET `/combine/outfit/my/favorites`)

### 第四階段（增強功能）- 2-4 週
1. 🔄 AI 文字對話 - `/ai/chat`
2. ⏳ 通用圖片上傳 - `/picture/upload/`
3. ⏳ 圖片管理功能
4. ⏳ 穿搭分享功能
5. ⏳ 虛擬試衣歷史記錄

### 開發框架
- **框架**: Django + Django REST Framework
- **數據庫**: PostgreSQL
- **存儲**: MinIO (兼容 AWS S3 API)
- **認證**: JWT (JSON Web Token)
- **AI 集成**: FastAPI 後端服務
- **虛擬試衣 AI**: 深度學習模型（衣服檢測、姿勢估計、合成）

---

## 🔐 權限管理

### 角色權限對照表

| 功能 | 匿名用戶 | 認證用戶 | 管理員 |
|------|---------|---------|--------|
| 註冊 | ✅ | ❌ | ❌ |
| 登入 | ✅ | ❌ | ✅ |
| 登出 | ❌ | ✅ | ✅ |
| 查看衣服列表 | ✅ | ✅ | ✅ |
| 查看穿搭列表 | ✅ | ✅ | ✅ |
| 上傳圖片 | ❌ | ✅ | ✅ |
| 設定衣服資料 | ❌ | ❌ | ✅ |
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
