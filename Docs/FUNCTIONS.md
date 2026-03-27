# 系統功能文檔

> 更新時間: 2026-03-27  
> 說明: test_project 系統完整功能一覽及詳細說明
> 最新更新: Feature 2.1 擴展 - 添加衣服尺寸參數支持（袖長、褲長、肩寬、腰圍）

---

## 📋 功能總覽

系統共規劃 **15 個主要功能**，分為以下 **5 個功能模塊**：

| 模塊 | 功能數 | 優先級 |
|------|--------|--------|
| 🔐 **用戶賬戶管理** | 5 | ⭐⭐⭐ 核心功能 |
| � **照片管理** | 5 | ⭐⭐⭐ 核心功能 |
| 👗 **穿搭管理** | 4 | ⭐⭐⭐ 核心功能 |
| 🖼️ **圖片和媒體** | 3 | ⭐⭐⭐ 核心功能 |
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

用戶照片和衣服資料的上傳、查看和管理（包括：衣服圖片、用戶個人照片）

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

### 2.3 用戶個人照片管理（CRUD）
- **功能編號**: `PHOTO-001`
- **模組**: `picture`
- **Actor**: `user` (已認證用戶)
- **API 路徑**: `/picture/user/photo` ⭐ (統一端點)
- **驗證方式**: `JWT Bearer Token`
- **狀態**:  - 所有5個 CRUD 操作均已測試驗證
- **功能說明**:
  - 用戶上傳自己的個人照片（全身照、頭像等）
  - 支持 JPG、PNG、GIF、WebP 格式
  - 最大檔案 10MB
  - 自動存儲到 MinIO
  - 更新用戶的個人照片 URL
  - 用於虛擬試衣、個人檔案等場景

**流程說明**:
```
① 用戶選擇並上傳照片檔案
    ↓
② 後端驗證檔案格式和大小
    ↓
③ 上傳到 MinIO 存儲
    ↓
④ 生成 MinIO URL
    ↓
⑤ 更新用戶 user_image_url 字段
    ↓
⑥ 返回照片 URL 和用戶信息
```

#### 2.3.1 上傳個人照片
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

- **成功回應 (201 Created)**:
  ```json
  {
    "success": true,
    "message": "個人照片上傳成功",
    "photo_id": 1,
    "photo_url": "http://minio.example.com/bucket/user_uuid_photo_uuid.png",
    "user": {
      "user_uid": "550e8400-e29b-41d4-a716-446655440000",
      "user_name": "john_doe",
      "user_image_url": "http://minio.example.com/bucket/user_uuid_photo_uuid.png"
    }
  }
  ```

- **失敗回應**:
  - `400 Bad Request`: 缺少檔案參數或檔案過大
  - `401 Unauthorized`: Token 無效或過期
  - `415 Unsupported Media Type`: 不支持的檔案類型
  - `503 Service Unavailable`: MinIO 存儲服務不可用
  - `500 Internal Server Error`: 伺服器內部錯誤

#### 2.3.2 查看我的照片列表
**HTTP 方法**: `GET`
**API 路徑**: `/picture/user/photo`

- **查詢參數**:
  ```
  page: 1 (分頁頁數)
  limit: 20 (每頁數量)
  ```

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "count": 5,
    "total_pages": 1,
    "results": [
      {
        "photo_id": 1,
        "photo_url": "http://minio.example.com/bucket/photo_1.png",
        "uploaded_at": "2026-03-27T16:00:00Z"
      }
    ]
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期
  - `500 Internal Server Error`: 伺服器內部錯誤

#### 2.3.3 查看單張照片詳情
**HTTP 方法**: `GET`
**API 路徑**: `/picture/user/photo/<user_uid>/`

- **路徑參數**:
  ```
  user_uid: "550e8400-e29b-41d4-a716-446655440000"
  ```

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "photo_id": 1,
    "photo_url": "http://minio.example.com/bucket/photo_1.png",
    "uploaded_at": "2026-03-27T16:00:00Z"
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期
  - `404 Not Found`: 照片不存在
  - `500 Internal Server Error`: 伺服器內部錯誤

#### 2.3.4 更新照片信息
**HTTP 方法**: `PUT`
**API 路徑**: `/picture/user/photo/<user_uid>/`

- **路徑參數**:
  ```
  user_uid: "550e8400-e29b-41d4-a716-446655440000"
  ```

- **輸入參數** (JSON):
  ```json
  {
    "photo_file": "<二進位圖片檔案>" 
  }
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
    "message": "照片已更新",
    "photo_id": 1,
    "photo_url": "http://minio.example.com/bucket/photo_1_updated.png",
    "updated_at": "2026-03-27T17:30:00Z"
  }
  ```

- **失敗回應**:
  - `400 Bad Request`: 檔案驗證失敗
  - `401 Unauthorized`: Token 無效或過期
  - `403 Forbidden`: 無權限更新此照片
  - `404 Not Found`: 照片不存在
  - `415 Unsupported Media Type`: 不支持的檔案類型

#### 2.3.5 刪除照片
**HTTP 方法**: `DELETE`
**API 路徑**: `/picture/user/photo/<user_uid>/`

- **路徑參數**:
  ```
  user_uid: "550e8400-e29b-41d4-a716-446655440000"
  ```

- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```

- **成功回應 (200 OK)**:
  ```json
  {
    "success": true,
    "message": "照片已刪除"
  }
  ```

- **失敗回應**:
  - `401 Unauthorized`: Token 無效或過期
  - `403 Forbidden`: 無權限刪除此照片
  - `404 Not Found`: 照片不存在
  - `500 Internal Server Error`: 伺服器內部錯誤

**📊 統一端點 CRUD 操作表** ⭐ 所有個人照片操作都經由同一端點：

| HTTP 方法 | API 路徑 | 操作 | 身份要求 | 返回狀態碼 |
|----------|---------|------|---------|----------|
| **POST** | `/picture/user/photo` | ⬆️ 上傳照片 | 認證用戶 | 201 |
| **GET** | `/picture/user/photo` | 📋 查看我的照片 | 認證用戶 | 200 |
| **GET** | `/picture/user/photo/<user_uid>/` | 👁️ 查看照片詳情 | 認證用戶 | 200 |
| **PUT** | `/picture/user/photo/<user_uid>/` | ✏️ 更新照片 | 照片擁有者 | 200 |
| **DELETE** | `/picture/user/photo/<user_uid>/` | 🗑️ 刪除照片 | 照片擁有者 | 200 |

**✅ 確認：統一端點 `/picture/user/photo` 可以完整支持個人照片的 CRUD 操作**

---

## 👗 三、穿搭管理模塊

穿搭組合的創建、管理、虛擬試衣和收藏

**📌 重要說明**：穿搭管理模塊採用新的 `combine` 應用，支持虛擬試衣和 AI 合成功能。每個穿搭恰好包含 2 件衣服

---

### 3.1 使用者查看穿搭總覽列表
- **功能編號**: `OUTFIT-001`
- **模組**: `combine`
- **Actor**: `user` (任何用戶，認證可選)
- **HTTP 方法**: `GET`
- **API 路徑**: `/combine/outfit/`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token` (可選)
- **功能說明**:
  - 顯示系統中所有已發布的穿搭組合（不含草稿）
  - 完整的分頁支持
  - 認證用戶可查看自己的點讚狀態

#### 3.1.1 查詢參數說明

| 參數 | 類型 | 範例 | 說明 |
|------|------|------|------|
| `page` | integer | 1 | 頁碼（默認 1） |
| `limit` | integer | 20 | 每頁數量（默認 20，最多 100） |

#### 3.1.2 查詢示例

```
GET /combine/outfit/?page=1&limit=20
```

#### 3.1.3 成功回應 (200 OK)

```json
{
  "success": true,
  "message": "穿搭列表獲取成功",
  "count": 45,
  "total_pages": 3,
  "current_page": 1,
  "limit": 20,
  "results": [
    {
      "outfit_uid": "550e8400-e29b-41d4-a716-446655440000",
      "outfit_name": "春日甜美風",
      "outfit_description": "清新舒適的春季搭配",
      "preview_image_url": "http://192.168.233.128:9000/outfits/preview_1.png",
      "created_by_name": "fashion_expert",
      "clothes_count": 2,
      "is_liked": false,
      "is_draft": false,
      "created_at": "2026-03-20T10:30:45Z",
      "updated_at": "2026-03-25T14:20:00Z"
    }
  ]
}
```

#### 3.1.4 失敗回應

- `400 Bad Request`: 查詢參數無效
- `500 Internal Server Error`: 伺服器內部錯誤

---

### 3.2 使用者新增穿搭組合
- **功能編號**: `OUTFIT-002`
- **模組**: `combine`
- **Actor**: `user` (已認證用戶)
- **HTTP 方法**: `POST`
- **API 路徑**: `/combine/outfit/`
- **請求格式**: `application/json`
- **驗證方式**: `JWT Bearer Token`
- **功能說明**:
  - 用戶建立新的穿搭組合（選擇系統中已存在的 2 件衣服）
  - 添加穿搭名稱（必填）、描述（可選）
  - 一個穿搭必須恰好包含 2 件衣服
  - 支持保存為草稿或直接發布

#### 3.2.1 請求參數 (JSON)

```json
{
  "outfit_name": "我的春日穿搭",
  "outfit_description": "清新舒適的春季搭配",
  "clothes_ids": [
    "550e8400-e29b-41d4-a716-446655440010",
    "550e8400-e29b-41d4-a716-446655440011"
  ],
  "preview_image_url": "http://..." (可選),
  "is_draft": false
}
```

#### 3.2.2 參數驗證規則

| 參數 | 類型 | 必填 | 驗證規則 |
|------|------|------|---------|
| `outfit_name` | string | ✅ | 1-100 字符 |
| `outfit_description` | string | ❌ | 最多 500 字符 |
| `clothes_ids` | array | ✅ | UUID 陣列，**必須恰好 2 件** |
| `preview_image_url` | string | ❌ | 有效的 URL 格式 |
| `is_draft` | boolean | ❌ | 默認 false |

#### 3.2.3 Headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### 3.2.4 成功回應 (201 Created)

```json
{
  "success": true,
  "message": "穿搭建立成功",
  "data": {
    "outfit_uid": "550e8400-e29b-41d4-a716-446655440100",
    "outfit_name": "我的春日穿搭",
    "outfit_description": "清新舒適的春季搭配",
    "preview_image_url": "http://...",
    "outfit_clothes": [
      {
        "id": 1,
        "clothes": {
          "clothes_uid": "550e8400-e29b-41d4-a716-446655440010",
          "clothes_category": "T-shirt",
          "clothes_image_url": "http://192.168.233.128:9000/...",
          "colors": ["pink", "white"],
          "styles": ["casual", "sweet"]
        },
        "position_order": 0
      },
      {
        "id": 2,
        "clothes": {
          "clothes_uid": "550e8400-e29b-41d4-a716-446655440011",
          "clothes_category": "Pants",
          "clothes_image_url": "http://192.168.233.128:9000/...",
          "colors": ["white"],
          "styles": ["casual"]
        },
        "position_order": 1
      }
    ],
    "created_by": {
      "user_uid": "550e8400-e29b-41d4-a716-446655440001",
      "user_name": "john_doe",
      "user_image_url": "http://..."
    },
    "is_liked": false,
    "is_draft": false,
    "created_at": "2026-03-27T12:30:45Z",
    "updated_at": "2026-03-27T12:30:45Z"
  }
}
```

#### 3.2.5 失敗回應

- `400 Bad Request`: 數據驗證失敗
  ```json
  {
    "success": false,
    "message": "穿搭數據驗證失敗",
    "errors": {
      "clothes_ids": ["穿搭必須恰好包含 2 件衣服"]
    }
  }
  ```
- `401 Unauthorized`: 未認證
- `404 Not Found`: 衣服不存在
- `500 Internal Server Error`: 服務器內部錯誤

---

### 3.3 虛擬試衣 - 核心功能（OUTFIT-003）

穿搭管理模塊的核心功能：用戶選擇 2 件衣服或已存在的穿搭，與 AI 後端互動進行虛擬試衣合成

#### 3.3.1 虛擬試衣流程説明

⭐ **新工作流（v2.0）**：立即試衣，按需保存

```
前端用戶流程圖
══════════════════════════════════════════════════════

Step 1: 選擇穿搭或衣服組合
   ├─ 方式 A：選擇系統中已存在的穿搭（包含 2 件衣服）
   └─ 方式 B：手動選擇 2 件衣服組合

Step 2: 發送虛擬試衣請求到後端
   ├─ POST /combine/virtual-try-on/
   ├─ 提供：
   │  ├─ outfit_uid（如果是穿搭）或 clothes_ids（如果是衣服組合，恰好 2 件）
   │  ├─ photo_uid（可選，用戶照片）
   │  └─ 如果不提供照片，使用用戶身體測量數據
   └─ 系統開始 AI 合成處理（後端異步處理）

Step 3: 後端驗證並準備 AI 請求
   ├─ 驗證衣服數量恰好為 2 件
   ├─ 驗證用戶信息完整性
   ├─ 從數據庫獲取用戶身體測量和衣服尺寸數據
   └─ 標記虛擬試衣狀態為 "processing"

Step 4: 轉發至 AI 後端進行虛擬試衣合成
   ├─ 後端調用：POST (AI_BACKEND_VIRTUAL_TRY_ON_URL 從 .env 讀取)
   ├─ 發送 multipart/form-data：
   │  ├─ files[model_image]：模特照片（單張）
   │  ├─ files[garment_images]：2 件衣服圖片
   │  ├─ data[model_info]：JSON（用戶身體測量數據）
   │  └─ data[garments]：JSON（衣服信息）
   └─ 超時時間：120 秒

Step 5: AI 後端返回虛擬試衣結果
   ├─ 返回格式：multipart/mixed
   ├─ 成功 (200 OK)：JSON 元數據 + PNG 二進位圖片
   └─ 失敗：返回錯誤代碼

Step 6: 後端處理 AI 結果並返回
   ├─ 解析 AI multipart 響應
   ├─ 將合成圖片保存到 MinIO
   ├─ 生成公開訪問 URL
   ├─ 更新虛擬試衣記錄（狀態 → "completed"）✅ 虛擬試衣立即完成
   └─ 返回試衣結果給前端

Step 7: 前端展示結果
   ├─ 展示合成後的虛擬試衣圖片
   ├─ 用戶可以：
   │  ├─ ✅ 保存為穿搭：調用 save-as-outfit endpoint
   │  ├─ ❌ 不保存：忽略此結果
   │  └─ 📚 查看歷史：GET /combine/virtual-try-on/my
   └─ 虛擬試衣記錄永久保存供用戶參考

Step 8: 用戶決定保存時
   ├─ 如果喜歡，調用：
   │  ├─ POST /combine/virtual-try-on/{try_on_uid}/save-as-outfit
   │  ├─ 提供：outfit_name（必填） 和 outfit_description（可選）
   │  ├─ 後端建立 Outfit 記錄，FK 指向此 VirtualTryOn
   │  ├─ 複製衣服組合到 OutfitClothes
   │  └─ 返回完整的穿搭詳情
   └─ 如無需保存：虛擬試衣記錄仍保留在歷史中

**📊 關鍵變化**：
- VirtualTryOn = 虛擬試衣歷史記錄（永久保存）
- Outfit = 用戶的穿搭設計（可選，來自滿意的虛擬試衣）
- Outfit.virtual_try_on FK = 追溯此穿搭來自哪個虛擬試衣
- 一次虛擬試衣可生成 0 或 1 個 Outfit
- 用戶可瀏覽所有試衣歷史，按需保存喜歡的設計
```

#### 3.3.2 發起虛擬試衣請求

**功能編號**: `OUTFIT-003-01`  
**HTTP 方法**: `POST`  
**API 路徑**: `/combine/virtual-try-on/`

**請求參數 (JSON)**：

```json
{
  "outfit_uid": "550e8400-e29b-41d4-a716-446655440000",  // 可選：要試穿的穿搭 UUID
  "clothes_ids": [
    "550e8400-e29b-41d4-a716-446655440010",
    "550e8400-e29b-41d4-a716-446655440011"
  ],  // 或者直接提供衣服 UUID 列表（恰好 2 件）
  "photo_uid": "550e8400-e29b-41d4-a716-446655440050"  // 可選：模特照片 UUID
}
```

**參數說明**：
- `outfit_uid` 和 `clothes_ids` 至少提供一個
  - 如果提供 `outfit_uid`，系統會使用該穿搭的 2 件衣服
  - 如果提供 `clothes_ids`，必須恰好包含 2 件衣服 UUID
- `photo_uid` 可選：使用指定照片作為模特照片

**Headers**：
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**成功回應 (200 OK)**：

```json
{
  "success": true,
  "message": "虛擬試衣完成，請確認是否保存",
  "try_on_data": {
    "try_on_uid": "550e8400-e29b-41d4-a716-446655440200",
    "status": "completed",
    "result_image_url": "http://192.168.233.128:9000/virtual-try-on/try_on_550e8400.png",
    "clothes_count": 2,
    "ai_response": {
      "code": 200,
      "message": "200",
      "data": {
        "file_name": "try_on_outfit_20260328.png",
        "file_format": "PNG",
        "items_processed": 2
      }
    }
  }
}
```

**失敗回應**：

- `400 Bad Request`: 請求參數驗證失敗（如衣服數量不是 2 件）
- `401 Unauthorized`: 未認證
- `404 Not Found`: 衣服或照片不存在
- `503 Service Unavailable`: AI 後端服務不可用
- `504 Gateway Timeout`: AI 處理逾時（超過 120 秒）
- `500 Internal Server Error`: 服務器內部錯誤

#### 3.3.3 將虛擬試衣結果保存為穿搭

**功能編號**: `OUTFIT-003-02`  
**HTTP 方法**: `POST`  
**API 路徑**: `/combine/virtual-try-on/<try_on_uid>/save-as-outfit`

**請求參數 (JSON)**：

```json
{
  "outfit_name": "我喜歡的虛擬試衣結果無敵組合",
  "outfit_description": "通過虛擬試衣確認的完美搭配"
}
```

**參數說明**：
- `outfit_name`（必填）：穿搭名稱，1-100 字符
- `outfit_description`（可選）：穿搭描述，最多 500 字符

**Headers**：
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**成功回應 (201 Created)**：

```json
{
  "success": true,
  "message": "虛擬試衣已保存為穿搭",
  "data": {
    "outfit_uid": "550e8400-e29b-41d4-a716-446655440100",
    "outfit_name": "我喜歡的虛擬試衣結果無敵組合",
    "outfit_description": "通過虛擬試衣確認的完美搭配",
    "preview_image_url": "http://192.168.233.128:9000/virtual-try-on/try_on_550e8400.png",
    "virtual_try_on_uid": "550e8400-e29b-41d4-a716-446655440200",
    "outfit_clothes": [
      {
        "id": 1,
        "clothes": {
          "clothes_uid": "550e8400-e29b-41d4-a716-446655440010",
          "clothes_category": "Shirt",
          "clothes_image_url": "http://192.168.233.128:9000/...",
          "colors": ["pink", "white"],
          "styles": ["casual", "sweet"]
        },
        "position_order": 0
      },
      {
        "id": 2,
        "clothes": {
          "clothes_uid": "550e8400-e29b-41d4-a716-446655440011",
          "clothes_category": "Pants",
          "clothes_image_url": "http://192.168.233.128:9000/...",
          "colors": ["white"],
          "styles": ["casual"]
        },
        "position_order": 1
      }
    ],
    "created_by": {
      "user_uid": "550e8400-e29b-41d4-a716-446655440001",
      "user_name": "john_doe",
      "user_image_url": "http://..."
    },
    "is_liked": false,
    "is_draft": false,
    "created_at": "2026-03-28T10:35:00Z",
    "updated_at": "2026-03-28T10:35:00Z"
  }
}
```

**失敗回應**：
- `400 Bad Request`: 參數驗證失敗
- `401 Unauthorized`: 未認證
- `404 Not Found`: 虛擬試衣不存在
- `500 Internal Server Error`: 伺服器內部錯誤

#### 3.3.4 查看虛擬試衣歷史

**功能編號**: `OUTFIT-003-03`  
**HTTP 方法**: `GET`  
**API 路徑**: `/combine/virtual-try-on/my`

**查詢參數**：
```
page: 1 (分頁頁數)
limit: 20 (每頁數量)
status: "completed" | "processing" (可選過濾)
```

**Headers**：
```
Authorization: Bearer <access_token>
```

**成功回應 (200 OK)**：

```json
{
  "success": true,
  "message": "虛擬試衣歷史獲取成功",
  "count": 12,
  "total_pages": 1,
  "current_page": 1,
  "limit": 20,
  "results": [
    {
      "try_on_uid": "550e8400-e29b-41d4-a716-446655440200",
      "status": "completed",
      "result_image_url": "http://192.168.233.128:9000/virtual-try-on/try_on_550e8400.png",
      "clothes_count": 2,
      "clothes_list": [
        {
          "clothes_uid": "550e8400-e29b-41d4-a716-446655440010",
          "clothes_category": "Shirt",
          "colors": ["pink"]
        },
        {
          "clothes_uid": "550e8400-e29b-41d4-a716-446655440011",
          "clothes_category": "Pants",
          "colors": ["white"]
        }
      ],
      "saved_as_outfit": {
        "outfit_uid": "550e8400-e29b-41d4-a716-446655440100",
        "outfit_name": "我的無敵組合"
      },
      "created_at": "2026-03-28T10:30:00Z",
      "ai_processed_at": "2026-03-28T10:31:30Z",
      "confirmed_at": "2026-03-28T10:35:00Z"
    }
  ]
}
```

**失敗回應**：
- `401 Unauthorized`: 未認證
- `500 Internal Server Error`: 伺服器內部錯誤

---

### 3.4 穿搭詳情和基本 CRUD 操作

#### 3.4.1 查看穿搭詳情

**HTTP 方法**: `GET`  
**API 路徑**: `/combine/outfit/<outfit_uid>/`

**成功回應 (200 OK)**：

```json
{
  "success": true,
  "message": "穿搭詳情獲取成功",
  "data": {
    "outfit_uid": "550e8400-e29b-41d4-a716-446655440000",
    "outfit_name": "春日甜美風",
    "outfit_description": "清新舒適的春季搭配",
    "preview_image_url": "http://...",
    "outfit_clothes": [
      {
        "id": 1,
        "clothes": {...},
        "position_order": 0
      },
      {
        "id": 2,
        "clothes": {...},
        "position_order": 1
      }
    ],
    "created_by": {
      "user_uid": "550e8400-e29b-41d4-a716-446655440001",
      "user_name": "fashion_expert",
      "user_image_url": "..."
    },
    "is_liked": false,
    "is_draft": false,
    "created_at": "2026-03-20T10:30:45Z",
    "updated_at": "2026-03-25T14:20:00Z"
  }
}
```

#### 3.4.2 刪除穿搭

**HTTP 方法**: `DELETE`  
**API 路徑**: `/combine/outfit/<outfit_uid>/`  
**權限**: 穿搭擁有者或管理員

**成功回應 (200 OK)**：

```json
{
  "success": true,
  "message": "穿搭「春日甜美風」已刪除"
}
```

---

### 3.5 穿搭互動功能（OUTFIT-004）

#### 3.5.1 標記/取消標記為喜歡（收藏）

**功能編號**: `OUTFIT-004-01`  
**HTTP 方法**: `PATCH`  
**API 路徑**: `/combine/outfit/<outfit_uid>/favorite`  
**認證**: 必須

**請求參數 (JSON)**：

```json
{
  "is_liked": true  // true：喜歡；false：取消喜歡
}
```

**成功回應 (200 OK)**：

```json
{
  "success": true,
  "message": "已收藏此穿搭",
  "is_liked": true
}
```

或取消喜歡時：

```json
{
  "success": true,
  "message": "已取消收藏",
  "is_liked": false
}
```

---

### 3.6 穿搭管理模塊 API 快速參考表

| 功能 | HTTP 方法 | API 路徑 | 認證 | 返回狀態碼 |
|------|----------|---------|------|----------|
| **OUTFIT-001** 查看穿搭列表 | GET | `/combine/outfit/` | 可選 | 200 |
| **OUTFIT-002** 新增穿搭（2 件衣服） | POST | `/combine/outfit/` | 必須 | 201 |
| 查看穿搭詳情 | GET | `/combine/outfit/<uid>/` | 可選 | 200 |
| 刪除穿搭 | DELETE | `/combine/outfit/<uid>/` | 必須 | 200 |
| **OUTFIT-003-01** 發起虛擬試衣 | POST | `/combine/virtual-try-on/` | 必須 | 200 |
| **OUTFIT-003-02** 保存為穿搭 | POST | `/combine/virtual-try-on/<uid>/save-as-outfit` | 必須 | 201 |
| **OUTFIT-003-03** 查看試衣歷史 | GET | `/combine/virtual-try-on/my` | 必須 | 200 |
| **OUTFIT-004-01** 標記喜歡 | PATCH | `/combine/outfit/<uid>/favorite` | 必須 | 200 |
| 查看我的穿搭 | GET | `/combine/outfit/my` | 必須 | 200 |
| 查看我的收藏 | GET | `/combine/outfit/my/favorites` | 必須 | 200 |

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
| 9 | 上傳個人照片 | picture | user | POST | ⭐⭐⭐ | ✅ | `/picture/user/photo` |

### 第二部分：穿搭管理和虛擬試衣（新增 combine 應用）

| # | 功能名稱 | 模組 | Actor | HTTP 方法 | 優先級 | 狀態 | API 端點 |
|---|---------|------|-------|----------|--------|------|---------|
| 10 | **OUTFIT-001** 查看穿搭列表 | combine | user | GET | ⭐⭐⭐ | ✅ 新增 | `/combine/outfit/` |
| 11 | **OUTFIT-002** 新增穿搭組合 | combine | user | POST | ⭐⭐⭐ | ✅ 新增 | `/combine/outfit/create` |
| 12 | 查看穿搭詳情 | combine | user | GET | ⭐⭐⭐ | ✅ 新增 | `/combine/outfit/<uid>/` |
| 13 | 編輯穿搭 | combine | user | PUT | ⭐⭐ | ✅ 新增 | `/combine/outfit/<uid>/update` |
| 14 | 刪除穿搭 | combine | user | DELETE | ⭐⭐ | ✅ 新增 | `/combine/outfit/<uid>/delete` |
| 15 | **OUTFIT-003-01** 發起虛擬試衣 | combine | user | POST | ⭐⭐⭐ | ✅ 新增 | `/combine/virtual-try-on/` |
| 16 | **OUTFIT-003-02** 確認保存虛擬試衣 | combine | user | POST | ⭐⭐⭐ | ✅ 新增 | `/combine/virtual-try-on/<uid>/confirm` |
| 17 | **OUTFIT-003-03** 拒絕虛擬試衣 | combine | user | POST | ⭐⭐ | ✅ 新增 | `/combine/virtual-try-on/<uid>/reject` |
| 18 | **OUTFIT-004-01** 標記穿搭為喜歡 | combine | user | PATCH | ⭐⭐⭐ | ✅ 新增 | `/combine/outfit/<uid>/favorite` |
| 19 | **OUTFIT-004-02** 穿搭評分和評論 | combine | user | POST | ⭐⭐⭐ | ✅ 新增 | `/combine/outfit/<uid>/rating` |
| 20 | 查看我的穿搭 | combine | user | GET | ⭐⭐⭐ | ✅ 新增 | `/combine/outfit/my` |
| 21 | 查看我的收藏 | combine | user | GET | ⭐⭐⭐ | ✅ 新增 | `/combine/outfit/my/favorites` |

### 第三部分：其他功能

| # | 功能名稱 | 模組 | Actor | HTTP 方法 | 優先級 | 狀態 | API 端點 |
|---|---------|------|-------|----------|--------|------|---------|
| 22 | 上傳圖片 (通用) | picture | user | POST | ⭐⭐ | ⏳ | `/picture/upload/` |
| 23 | AI 文字對話 | picture/ai | user | POST | ⭐⭐ | 🔄 | `/ai/chat` |

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
   └─ 上傳模特照片 (user_picture) ✅

3. 瀏覽和上傳衣服
   ├─ 查看衣服列表 (clothes list) ⏳
   ├─ 上傳衣服圖片 (upload_image) ✅
   │  └─ 調用 AI 去背和分類
   └─ 標記喜歡的衣服 (favorites) ✅

4. 穿搭管理 ✨ 新增（combine 應用）
   ├─ 查看穿搭列表 (OUTFIT-001) ✅
   ├─ 新增穿搭組合 (OUTFIT-002) ✅
   │  ├─ 手動選擇衣服進行組合
   │  └─ 保存為草稿或發布
   │
   ├─ 虛擬試衣 (OUTFIT-003) ✅ 核心功能！
   │  ├─ POST /combine/virtual-try-on/
   │  ├─ 選擇穿搭或衣服組合
   │  ├─ AI 合成試衣結果圖
   │  └─ 流程：選擇 → AI 合成 → 確認/拒絕
   │
   ├─ 確認保存虛擬試衣 (OUTFIT-003-02) ✅
   │  └─ 虛擬試衣結果 → 穿搭數據庫
   │
   ├─ 穿搭互動 (OUTFIT-004) ✅
   │  ├─ 標記喜歡（OUTFIT-004-01）
   │  ├─ 評分評論（OUTFIT-004-02）
   │  └─ 查看收藏列表
   │
   └─ 穿搭 CRUD
      ├─ 查看我的穿搭
      ├─ 編輯穿搭
      └─ 刪除穿搭

5. AI 諮詢
   ├─ 文字對話 (AI chat) 🔄
   ├─ 獲得穿搭建議
   └─ 推薦衣服

6. 查看和管理
   ├─ 查看穿搭列表 (outfit list) ✅
   ├─ 查看收藏列表 (favorites) ✅
   └─ 編輯和刪除

7. 登出
   └─ 登出系統 (logout) ✅
```

### 虛擬試衣完整流程圖 ✨ 新增功能詳解

```
【使用者虛擬試衣流程】
════════════════════════════════════════════════════════════════

1️⃣ 前端：選擇穿搭或衣服
   ├─ 方式 A：從穿搭列表選擇一個穿搭
   ├─ 方式 B：手動選擇多件衣服（T-shirt、褲子等）
   └─ （可選）選擇模特照片，或使用默認身體數據

2️⃣ 前端：發送虛擬試衣請求
   └─ POST /combine/virtual-try-on/
      Headers: Authorization: Bearer <access_token>
      Body: {
        "outfit_uid": "...",  // 或 clothes_ids
        "clothes_ids": ["uuid1", "uuid2"],
        "photo_uid": "..." (可選)
      }

3️⃣ 後端：驗證並準備 AI 請求
   ├─ 驗證用戶、衣服、照片數據
   ├─ 從數據庫獲取：
   │  ├─ 用戶身體測量數據
   │  │  ├─ user_height: 175 cm
   │  │  ├─ user_weight: 70 kg
   │  │  ├─ user_shoulder_width: 42.5 cm
   │  │  ├─ user_arm_length: 60 cm
   │  │  ├─ user_waistline: 80 cm
   │  │  └─ user_leg_length: 100 cm
   │  ├─ 衣服尺寸數據
   │  │  └─ clothes_arm_length, clothes_shoulder_width 等
   │  └─ 衣服圖片和模特照片
   │
   ├─ 創建虛擬試衣記錄（VirtualTryOn）
   └─ 狀態 → "processing"

4️⃣ 後端：轉發至 AI 後端
   └─ POST http://192.168.233.128:8002/virtual_try_on/clothes/combine
      Content-Type: multipart/form-data
      
      files:
        - model_image: <二進位模特照片>
        - garment_images: [<圖片1>, <圖片2>, ...]
      
      data:
        - model_info: {
            "user_height": 175.0,
            "user_weight": 70,
            "user_shoulder_width": 42.5,
            "user_arm_length": 60,
            "user_waistline": 80,
            "user_leg_length": 100
          }
        - garments: [
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

5️⃣ AI 後端：虛擬試衣合成
   ├─ 接收模特照片和衣服圖片
   ├─ 使用深度學習模型：
   │  ├─ 衣服檢測和分割
   │  ├─ 模特姿勢估計
   │  ├─ 根據身體尺寸調整衣服大小
   │  └─ 將衣服"穿"到模特身上
   ├─ 產生合成圖片（PNG 格式）
   └─ 返回 multipart/mixed 響應

6️⃣ AI 後端：返回結果
   └─ HTTP/1.1 200 OK
      Content-Type: multipart/mixed; boundary=frame_boundary
      
      --frame_boundary
      Content-Type: application/json
      
      {
        "code": 200,
        "message": "200",
        "data": {
          "file_name": "try_on_outfit_20260328.png",
          "file_format": "PNG",
          "items_processed": 2  // 成功處理了 2 件衣服
        }
      }
      --frame_boundary
      Content-Type: image/png
      Content-Disposition: attachment; filename="try_on_outfit_20260328.png"
      
      <PNG 圖片二進位數據>
      --frame_boundary--

7️⃣ 後端：處理 AI 結果
   ├─ 解析 multipart/mixed 響應
   ├─ 提取 JSON 元數據和 PNG 圖片
   ├─ 上傳合成圖片到 MinIO
   ├─ 生成公開 URL：
   │  http://192.168.233.128:9000/virtual-try-on/try_on_<uuid>.png
   │
   ├─ 更新虛擬試衣記錄：
   │  ├─ status → "completed"
   │  ├─ result_image_url → MinIO URL
   │  ├─ result_file_name → "try_on_outfit_20260328.png"
   │  ├─ ai_response_data → JSON 元數據
   │  └─ ai_processed_at → 當前時間
   │
   └─ 立即返回結果給前端

8️⃣ 後端：返回虛擬試衣結果
   └─ HTTP/1.1 200 OK
      {
        "success": true,
        "message": "虛擬試衣完成，請確認是否保存",
        "try_on_data": {
          "try_on_uid": "550e8400-...",
          "status": "completed",
          "result_image_url": "http://192.168.233.128:9000/virtual-try-on/try_on_550e8400.png",
          "clothes_count": 2,
          "ai_response": {
            "code": 200,
            "message": "200",
            "data": {
              "file_name": "try_on_outfit_20260328.png",
              "file_format": "PNG",
              "items_processed": 2
            }
          }
        }
      }

9️⃣ 前端：展示試衣結果
   ├─ 顯示合成後的虛擬試衣圖片
   ├─ 允許用戶：
   │  ├─ ✅ 點擊「喜歡」→ 確認保存
   │  └─ ❌ 點擊「不喜歡」→ 拒絕並結束
   └─ 如喜歡，用戶可輸入：
      ├─ 穿搭名稱
      ├─ 穿搭描述
      ├─ 季節
      └─ 風格

🔟 前端：用戶確認（喜歡）
   └─ POST /combine/virtual-try-on/<try_on_uid>/confirm
      Headers: Authorization: Bearer <access_token>
      Body: {
        "outfit_name": "我的春日試衣結果",
        "outfit_description": "通過虛擬試衣確認的完美搭配",
        "season": "春季",
        "style": "甜美",
        "save_as_new": true
      }

1️⃣1️⃣ 後端：創建新穿搭
   ├─ 從虛擬試衣記錄建立新 Outfit
   │  ├─ outfit_name: 用戶輸入
   │  ├─ outfit_description: 用戶輸入
   │  ├─ season, style: 用戶選擇
   │  ├─ preview_image_url: 試衣結果圖
   │  └─ created_by: 當前用戶
   │
   ├─ 添加 OutfitClothes 記錄（關聯衣服）
   ├─ 更新 VirtualTryOn：
   │  ├─ status → "accepted"
   │  ├─ is_confirmed → true
   │  ├─ saved_outfit → 新建的 Outfit ID
   │  ├─ confirmed_at → 當前時間
   │
   └─ 返回完整穿搭詳情（包含衣服列表）

1️⃣2️⃣ 前端：顯示保存成功
   └─ 穿搭已入庫，用戶可以：
      ├─ 查看該穿搭詳情
      ├─ 分享給其他用戶
      ├─ 添加到我的收藏
      ├─ 進行評分
      └─ 發起新的虛擬試衣

【如果用戶拒絕虛擬試衣結果】
使用者不喜歡 → POST /combine/virtual-try-on/<uid>/reject
後端更新 status → "rejected"，流程結束
虛擬試衣記錄保留用於分析用戶偏好

【狀態轉換圖】
pending
   ↓
processing
   ↓
completed
   ├─ 用戶確認 → accepted → Outfit 已保存
   └─ 用戶拒絕 → rejected → 流程結束
   
error （如果 AI 處理失敗）
   └─ ai_error_message 記錄詳細錯誤
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
