# API 完整文檔

> 更新時間: 2026-03-29  
> 說明: test_project Main Backend 的完整 API 文檔，包含所有端點、參數、響應示例  
> 版本: 1.0 (完整實現版)

---

## 📋 API 概覽

| 模組 | 基礎路徑 | 說明 |
|------|--------|------|
| **認證系統** | `/account/user/` | 用戶註冊、登入、登出、刪除帳號、身體測量資料 |
| **照片管理** | `/picture/` | 衣伺上傳/管理、用戶模特照片管理 |
| **虛擬試穿** | `/combine/` | 虛擬試穿、試穿歷史、試穿詳情 |
| **系統檢查** | `/health` | 伺務狀態檢查 |

---

## 🔐 認證 API

### 📍 POST `/account/user/register`
**描述**: 使用者註冊新帳號

**請求頭**:
```
Content-Type: application/json
```

**請求體**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securePass123"
}
```

**參數說明**:
- `username` (必填): 使用者名稱，最大 150 字元
- `email` (必填): 有效的電子郵件地址
- `password` (必填): 密碼，至少 8 個字元

**成功響應 (201 Created)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "date_joined": "2026-03-29T10:00:00Z"
}
```

**錯誤響應**:
- `400 Bad Request`: 驗證失敗（密碼過短、格式錯誤等）
  ```json
  {
    "password": ["這個密碼太短了。至少需要包含 8 個字元。"],
    "email": ["輸入有效的電子郵件地址。"]
  }
  ```
- `409 Conflict`: 帳號或 Email 已存在
  ```json
  {
    "username": ["此使用者名稱已存在。"]
  }
  ```

---

### 📍 POST `/account/user/login`
**描述**: 使用者登入，取得 JWT Token

**請求頭**:
```
Content-Type: application/json
```

**請求體**:
```json
{
  "username": "john_doe",
  "password": "securePass123"
}
```

**參數說明**:
- `username` (必填): 使用者名稱或 Email
- `password` (必填): 密碼

**成功響應 (200 OK)**:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

**錯誤響應**:
- `401 Unauthorized`: 帳密錯誤或帳號不存在
  ```json
  {
    "detail": "找不到符合條件的有效使用者。"
  }
  ```

---

### 📍 POST `/account/user/logout`
**描述**: 使用者登出

**請求頭**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**請求體**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**參數說明**:
- `refresh` (必填): 登入時取得的 Refresh Token

**成功響應 (200 OK)**:
```json
{
  "detail": "登出成功。"
}
```

**錯誤響應**:
- `400 Bad Request`: 缺少 refresh token
  ```json
  {
    "detail": "請提供 refresh token。"
  }
  ```
- `401 Unauthorized`: Token 無效或過期
  ```json
  {
    "detail": "Token 無效或已過期。"
  }
  ```

---

### 📍 POST `/account/user/user_info` ⭐ 上傳身體測量資料
**描述**: 使用者上傳或更新身體測量資料（用於虛擬試穿參考）

**請求頭**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**請求體** (所有參數可選，提供的字段會被更新):
```json
{
  "user_height": 180,           
  "user_weight": 70,             
  "user_arm_length": 65,         
  "user_shoulder_width": 45,     
  "user_waistline": 80,          
  "user_leg_length": 105         
}
```

**參數說明**:
| 欄位 | 範圍 | 單位 | 說明 |
|------|------|------|------|
| `user_height` | 50-250 | cm | 身高 |
| `user_weight` | 20-300 | kg | 體重 |
| `user_arm_length` | 30-100 | cm | 臂長（手臂長度） |
| `user_shoulder_width` | 20-100 | cm | 肩寬 |
| `user_waistline` | 40-200 | cm | 腰圍 |
| `user_leg_length` | 50-150 | cm | 腿長 |

**成功響應 (200 OK)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "height": 180,
  "weight": 70,
  "arm_length": 65,
  "shoulder_width": 45,
  "waistline": 80,
  "leg_length": 105,
  "updated_time": "2026-03-29T10:30:45.123456Z"
}
```

**驗證規則**:
- 所有參數都是選擇性的，可以提供部分或全部
- 腿長不應超過身高
- 參數必須在指定的範圍內

**錯誤響應**:
- `400 Bad Request`: 驗證失敗（超出範圍或不合理）
  ```json
  {
    "user_height": ["確保此值大於或等於 50。"]
  }
  ```
- `401 Unauthorized`: 未登入或 Token 過期

---

### 📍 POST `/account/user/delete`
**描述**: 刪除使用者帳號（需要確認密碼）

**請求頭**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**請求體**:
```json
{
  "password": "securePass123"
}
```

**參數說明**:
- `password` (必填): 使用者密碼（用於確認身份）

**成功響應 (200 OK)**:
```json
{
  "message": "帳號已刪除"
}
```

**錯誤響應**:
- `401 Unauthorized`: 未登入
- `403 Forbidden`: 密碼錯誤
  ```json
  {
    "password": ["密碼不正確。"]
  }
  ```

---

### 📍 GET `/account/user/list`
**描述**: 查看所有使用者列表（測試用）

**請求頭**:
```
(無認證要求)
```

**成功響應 (200 OK)**:
```json
{
  "count": 2,
  "users": [
    {
      "id": 1,
      "uid": "550e8400-e29b-41d4-a716-446655440001",
      "username": "john_doe",
      "email": "john@example.com",
      "weight": 70,
      "height": 180,
      "is_active": true,
      "created_time": "2026-03-29T10:00:00Z"
    },
    {
      "id": 2,
      "uid": "550e8400-e29b-41d4-a716-446655440002",
      "username": "jane_smith",
      "email": "jane@example.com",
      "weight": 55,
      "height": 165,
      "is_active": true,
      "created_time": "2026-03-29T10:15:00Z"
    }
  ]
}
```

---

## 📸 照片管理 API

### 📕 衣伺管理端點

### 📍 POST `/picture/clothes/` ⭐ 新增衣伺（上傳圖片 + AI 去背）
**描述**: 使用者上傳衣伺圖片，系統自動轉發給 AI 進行去背、分類、顏色和風格分析

**請求頭**:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**請求體 (form-data)**:
```
image_data: <二進位圖片檔案> (必需，JPG/PNG/GIF/WebP，最大 10MB)
clothes_arm_length: 65 (可選，衣伺袖長，0-200cm)
clothes_leg_length: 92 (可選，衣伺褲長，0-150cm)
clothes_shoulder_width: 45 (可選，衣伺肩寬，0-200cm)
clothes_waistline: 80 (可選，衣伺腰圍，0-300cm)
```

**完整流程**:
```
1. 使用者上傳圖片 + 衣伺尺寸
   ↓
2. 後端驗證衣伺尺寸參數
   ↓
3. 後端轉發給 AI 進行去背處理（包含尺寸）
   ↓
4. AI 返回：
   - 去背後的圖片
   - 衣伺分類（clothes_category）
   - 風格列表（style_name x 3）
   - 顏色列表（color_name x 3）
   ↓
5. 後端將圖片存儲到 MinIO
   ↓
6. 將完整數據存儲到 DB
   ↓
7. 返回完整的衣伺詳情給前端
```

**衣伺尺寸參數驗證規則**:
| 參數名 | 範圍 | 預設值 | 說明 |
|-------|------|--------|------|
| `clothes_arm_length` | 0-200 cm | 0 | 衣伺袖長，不能為負數 |
| `clothes_leg_length` | 0-150 cm | 0 | 衣伺褲長，不能為負數 |
| `clothes_shoulder_width` | 0-200 cm | 0 | 衣伺肩寬，不能為負數 |
| `clothes_waistline` | 0-300 cm | 0 | 衣伺腰圍，不能為負數 |

**成功響應 (201 Created / 200 OK)**:
```json
{
  "success": true,
  "message": "圖片處理和儲存成功",
  "processed_url": "http://192.168.233.128:9000/clothes-bucket/unique_id_cleaned.png",
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
    "bucket": "clothes-bucket",
    "public_url": "http://192.168.233.128:9000/clothes-bucket/...",
    "signed_url": "http://192.168.233.128:9000/clothes-bucket/...?X-Amz..."
  },
  "clothes_data": {
    "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
    "clothes_category": "T-shirt",
    "styles": ["Casual", "Formal", "Streetwear"],
    "colors": ["red", "blue", "green"],
    "image_url": "http://192.168.233.128:9000/clothes-bucket/...",
    "clothes_measurements": {
      "arm_length": 65,
      "leg_length": 92,
      "shoulder_width": 45,
      "waistline": 80
    }
  }
}
```

**錯誤響應**:
- `400 Bad Request`: 缺少圖片、驗證失敗或尺寸參數無效
  ```json
  {
    "success": false,
    "message": "請上傳圖片檔案（欄位名稱：image_data）"
  }
  ```
- `401 Unauthorized`: 未認證或 Token 過期
- `415 Unsupported Media Type`: 不支持的檔案類型
- `422 Unprocessable Entity`: 圖片過於模糊或無法處理
- `503 Service Unavailable`: AI 或 MinIO 伺務不可用
- `504 Gateway Timeout`: AI 處理逾時

---

### 📍 GET `/picture/clothes/my` ⭐ 我的衣伺列表
**描述**: 取得當前使用者的衣伺列表

**請求頭**:
```
Authorization: Bearer <access_token>
```

**查詢參數**:
```
page: 1 (分頁頁數，預設1)
limit: 20 (每頁數量，預設20)
```

**成功響應 (200 OK)**:
```json
{
  "count": 5,
  "total_pages": 1,
  "current_page": 1,
  "results": [
    {
      "clothes_id": 1,
      "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
      "clothes_category": "T-shirt",
      "clothes_arm_length": 65,
      "clothes_shoulder_width": 45,
      "clothes_waistline": 80,
      "clothes_leg_length": 0,
      "clothes_image_url": "http://192.168.233.128:9000/clothes-bucket/...",
      "clothes_favorite": false,
      "clothes_created_time": "2026-03-29T10:00:00Z",
      "clothes_updated_time": "2026-03-29T10:00:00Z",
      "colors": [
        {
          "color_id": 1,
          "color_uid": "...",
          "color_name": "red"
        }
      ],
      "styles": [
        {
          "style_id": 1,
          "style_uid": "...",
          "style_name": "Casual"
        }
      ]
    }
  ]
}
```

**錯誤響應**:
- `401 Unauthorized`: 未認證或 Token 過期
- `500 Internal Server Error`: 伺務器內部錯誤

---

### 📍 GET `/picture/clothes/<clothes_uid>/` ✅ 衣伺詳情
**描述**: 取得單個衣伺的詳細信息

**請求頭**:
```
Authorization: Bearer <access_token>
```

**路徑參數**:
```
clothes_uid: "550e8400-e29b-41d4-a716-446655440000" (衣伺 UID)
```

**成功響應 (200 OK)**:
```json
{
  "clothes_id": 1,
  "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
  "clothes_category": "T-shirt",
  "clothes_arm_length": 65,
  "clothes_shoulder_width": 45,
  "clothes_waistline": 80,
  "clothes_leg_length": 0,
  "clothes_image_url": "http://192.168.233.128:9000/clothes-bucket/...",
  "clothes_favorite": false,
  "clothes_created_time": "2026-03-29T10:00:00Z",
  "clothes_updated_time": "2026-03-29T10:00:00Z",
  "colors": [
    {
      "color_id": 1,
      "color_uid": "...",
      "color_name": "red"
    }
  ],
  "styles": [
    {
      "style_id": 1,
      "style_uid": "...",
      "style_name": "Casual"
    }
  ]
}
```

**錯誤響應**:
- `401 Unauthorized`: 未認證或 Token 過期
- `404 Not Found`: 衣伺不存在

---

### 📍 PUT `/picture/clothes/<clothes_uid>/` ✅ 更新衣伺
**描述**: 更新衣伺信息（衣伺擁有者或管理員）

**請求頭**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**路徑參數**:
```
clothes_uid: "550e8400-e29b-41d4-a716-446655440000" (衣伺 UID)
```

**請求體** (任意字段都可選):
```json
{
  "clothes_category": "Pants",
  "clothes_arm_length": 0,
  "clothes_shoulder_width": 0,
  "clothes_waistline": 85,
  "clothes_leg_length": 100,
  "colors": ["black", "blue"],
  "styles": ["Formal", "Business"]
}
```

**成功響應 (200 OK)**:
```json
{
  "clothes_id": 1,
  "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
  "clothes_category": "Pants",
  "clothes_arm_length": 0,
  "clothes_shoulder_width": 0,
  "clothes_waistline": 85,
  "clothes_leg_length": 100,
  "clothes_image_url": "http://192.168.233.128:9000/clothes-bucket/...",
  "clothes_favorite": false,
  "clothes_created_time": "2026-03-29T10:00:00Z",
  "clothes_updated_time": "2026-03-29T10:30:00Z",
  "colors": [
    {
      "color_id": 1,
      "color_uid": "...",
      "color_name": "black"
    }
  ],
  "styles": [
    {
      "style_id": 1,
      "style_uid": "...",
      "style_name": "Formal"
    }
  ]
}
```

**錯誤響應**:
- `400 Bad Request`: 數據驗證失敗
- `401 Unauthorized`: 未認證或 Token 過期
- `403 Forbidden`: 無權限修改（只有擁有者或管理員可修改）
- `404 Not Found`: 衣伺不存在

---

### 📍 DELETE `/picture/clothes/<clothes_uid>/` ✅ 刪除衣伺
**描述**: 刪除衣伺（衣伺擁有者或管理員）

**請求頭**:
```
Authorization: Bearer <access_token>
```

**路徑參數**:
```
clothes_uid: "550e8400-e29b-41d4-a716-446655440000" (衣伺 UID)
```

**成功響應 (200 OK)**:
```json
{
  "detail": "衣伺已刪除"
}
```

**錯誤響應**:
- `401 Unauthorized`: 未認證或 Token 過期
- `403 Forbidden`: 無權限刪除
- `404 Not Found`: 衣伺不存在

---

### 📍 PATCH `/picture/clothes/<clothes_uid>/favorite` ⭐ 標記/取消標記衣伺為喜歡
**描述**: 標記或取消標記衣伺為喜歡

**請求頭**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**路徑參數**:
```
clothes_uid: "550e8400-e29b-41d4-a716-446655440000" (衣伺 UID)
```

**請求體**:
```json
{
  "favorite": true
}
```

**參數說明**:
- `favorite` (必填): `true` 表示喜歡，`false` 表示取消喜歡

**成功響應 (200 OK)**:
```json
{
  "success": true,
  "message": "已標記為喜歡",
  "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
  "clothes_favorite": true
}
```

**錯誤響應**:
- `400 Bad Request`: 缺少 favorite 參數
- `401 Unauthorized`: Token 無效或過期
- `404 Not Found`: 衣伺不存在
- `500 Internal Server Error`: 伺務器內部錯誤

---

### 📍 GET `/picture/clothes/favorites` ⭐ 我的收藏衣伺
**描述**: 取得使用者收藏（喜歡）的所有衣伺列表

**請求頭**:
```
Authorization: Bearer <access_token>
```

**查詢參數**:
```
page: 1 (分頁頁數，預設1)
limit: 20 (每頁數量，預設20)
```

**成功響應 (200 OK)**:
```json
{
  "count": 3,
  "total_pages": 1,
  "current_page": 1,
  "results": [
    {
      "clothes_id": 1,
      "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
      "clothes_category": "T-shirt",
      "clothes_image_url": "http://192.168.233.128:9000/clothes-bucket/...",
      "favorited_at": "2026-03-29T10:00:00Z"
    }
  ]
}
```

**錯誤響應**:
- `401 Unauthorized`: 未認證或 Token 過期
- `500 Internal Server Error`: 伺務器內部錯誤

---

### 📸 用戶模特照片管理端點

### 📍 POST `/picture/user/photo` ⭐ 上傳模特照片
**描述**: 使用者上傳模特照片，自動保存為虛擬試穿用的模特照片

**請求頭**:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**請求體 (form-data)**:
```
photo_file: <二進位圖片檔案> (JPG, PNG, GIF, WebP，最大 10MB)
```

**成功響應 (201 Created / 200 OK)**:
```json
{
  "success": true,
  "message": "模特照片上傳成功，已自動更新為虛擬試穿用的模特照片",
  "photo_data": {
    "photo_url": "http://192.168.233.128:9000/user-photos/user_uuid_photo_timestamp.png",
    "uploaded_at": "2026-03-29T10:00:00Z",
    "note": "此照片已保存為用戶的虛擬試穿模特照片"
  },
  "user": {
    "user_uid": "550e8400-e29b-41d4-a716-446655440001",
    "user_name": "john_doe",
    "user_image_url": "http://192.168.233.128:9000/user-photos/user_uuid_photo_timestamp.png",
    "updated_at": "2026-03-29T10:00:00Z"
  }
}
```

**重要說明**:
- 此照片自動保存為用戶的 `user_image_url` 字段（用於虛擬試穿）
- 虛擬試穿會自動讀取此 URL，無須額外操作
- 推薦上傳全身照以獲得最佳虛擬試穿效果
- 新的 `user_image_url` 會立即用於虛擬試穿功能
- 一個使用者同時只有一張活跃的模特照片，上傳新照片會自動覆蓋舊照片

**錯誤響應**:
- `400 Bad Request`: 缺少檔案參數或檔案過大 (>10MB)
- `401 Unauthorized`: Token 無效或過期
- `415 Unsupported Media Type`: 不支持的檔案類型 (僅接受 JPG、PNG、GIF、WebP)
- `503 Service Unavailable`: MinIO 存儲伺務不可用

---

### 📍 PUT `/picture/user/photo` ⭐ 更新模特照片
**描述**: 更新已上傳的模特照片，自動覆蓋舊照片

**請求頭**:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**請求體 (form-data)**:
```
photo_file: <二進位圖片檔案> (JPG, PNG, GIF, WebP，最大 10MB)
```

**成功響應 (200 OK)**:
```json
{
  "success": true,
  "message": "模特照片更新成功，已自動更新為虛擬試穿用的模特照片",
  "photo_data": {
    "photo_url": "http://192.168.233.128:9000/user-photos/user_uuid_photo_timestamp.png",
    "uploaded_at": "2026-03-29T10:05:00Z",
    "note": "此照片已保存為用戶的虛擬試穿模特照片"
  },
  "user": {
    "user_uid": "550e8400-e29b-41d4-a716-446655440001",
    "user_name": "john_doe",
    "user_image_url": "http://192.168.233.128:9000/user-photos/user_uuid_photo_timestamp.png",
    "updated_at": "2026-03-29T10:05:00Z"
  }
}
```

**錯誤響應**:
- `400 Bad Request`: 缺少檔案參數或檔案過大
- `401 Unauthorized`: Token 無效或過期
- `415 Unsupported Media Type`: 不支持的檔案類型
- `503 Service Unavailable`: MinIO 存儲伺務不可用

---

### 📍 GET `/picture/user/photo` ⭐ 查看當前模特照片
**描述**: 查看當前的模特照片 URL 和使用者信息

**請求頭**:
```
Authorization: Bearer <access_token>
```

**成功響應 (200 OK)**:
```json
{
  "success": true,
  "message": "模特照片獲取成功",
  "photo_data": {
    "photo_url": "http://192.168.233.128:9000/user-photos/user_uuid_photo_timestamp.png",
    "uploaded_at": "2026-03-29T10:00:00Z"
  },
  "user": {
    "user_uid": "550e8400-e29b-41d4-a716-446655440001",
    "user_name": "john_doe",
    "user_image_url": "http://192.168.233.128:9000/user-photos/user_uuid_photo_timestamp.png"
  }
}
```

**說明**:
- 如果使用者未上傳照片，返回 404 且提示「未設定模特照片」
- 前端應在虛擬試穿前檢查此端點，確認照片已設定
- 虛擬試穿會自動讀取 `user_image_url`，如未設定則返回 400 錯誤

**錯誤響應**:
- `401 Unauthorized`: Token 無效或過期
- `404 Not Found`: 使用者未上傳模特照片
  ```json
  {
    "success": false,
    "message": "未設定模特照片"
  }
  ```

---

## 👕 虛擬試穿 API (Feature 3.1)

### 📍 POST `/combine/user/virtual-try-on` ⭐ 發起虛擬試穿
**描述**: 使用者從自己衣櫃選擇 2 件衣伺進行虛擬試穿

**請求頭**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**請求體**:
```json
{
  "clothes_ids": [
    "550e8400-e29b-41d4-a716-446655440010",
    "550e8400-e29b-41d4-a716-446655440011"
  ]
}
```

**參數說明**:
- `clothes_ids` (必填): 衣伺 UID 陣列，恰好 2 件
  - 衣伺必須存在且屬於當前使用者
  - 如果衣伺數量不是 2 件，返回 400 錯誤

**前置條件**:
- 使用者必須先上傳模特照片（使用 POST `/picture/user/photo`）
- 使用者的 `user_image_url` 必須已設定
- 如果未設定，返回 400 Bad Request，提示「用戶未設定模特照片」

**完整流程**:
```
① 前端送出試穿請求（2 件衣伺）
   ↓
② 後端驗證衣伺數量與歸屬權限
   ↓
③ 後端查詢衣伺資料 + 使用者模特照片（user_image_url） + 身體測量
   ↓
④ 後端組裝 multipart/form-data 並呼叫 AI 後端
   ↓
⑤ AI 回傳 multipart/mixed（JSON metadata + PNG 圖片）
   ↓
⑥ 後端解析回應，將圖片上傳到 MinIO
   ↓
⑦ 將試穿記錄保存到 Model 表
   ↓
⑧ 返回試穿結果給前端
```

**後端送給 AI 的資料格式**:

- **URL**: `http://172.17.0.1:8002/virtual_try_on/clothes/combine`（或根據環境配置）
- **方法**: POST
- **Content-Type**: multipart/form-data

**Files 參數**:
```
model_image: <二進位模特照片>
garment_0: <二進位衣伺圖片1>
garment_1: <二進位衣伺圖片2>
```

**Data 參數**:
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

**成功響應 (200 OK)**:
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
    "created_at": "2026-03-29T10:30:00Z",
    "ai_response": {
      "code": 200,
      "message": "200",
      "data": {
        "file_name": "try_on_outfit_20260329.png",
        "style_name": ["Japanese Style", "Elegant", "Traditional"],
        "file_format": "PNG"
      }
    }
  }
}
```

**AI 回傳狀態碼**:
| message | 說明 |
|---------|------|
| 200 | 成功 |
| 2200 | 模特檢測失敗 |
| 2400 | 衣伺檢測失敗 |
| 2422 | 圖片品質過低 |
| 2500 | 內部處理錯誤 |
| 2501 | 超時 |

**錯誤響應**:
- `400 Bad Request`: 衣伺數量錯誤、參數格式錯誤、未設定使用者模特照片
  ```json
  {
    "success": false,
    "message": "用戶未設定模特照片，請先上傳模特照片"
  }
  ```
- `401 Unauthorized`: 未登入或 Token 無效
- `403 Forbidden`: 衣伺不屬於當前使用者
- `404 Not Found`: 衣伺不存在
- `503 Service Unavailable`: AI 伺務不可用
- `504 Gateway Timeout`: AI 合併逾時
- `500 Internal Server Error`: 伺務器內部錯誤

---

### 📍 GET `/combine/user/virtual-try-on-history` ⭐ 查看試穿歷史
**描述**: 取得當前使用者的虛擬試穿歷史記錄

**請求頭**:
```
Authorization: Bearer <access_token>
```

**查詢參數**:
```
page: 1 (分頁頁數，預設1)
limit: 20 (每頁數量，預設20)
status: "completed" (狀態篩選，可選)
```

**成功響應 (200 OK)**:
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
      "created_at": "2026-03-29T10:30:00Z"
    }
  ]
}
```

**錯誤響應**:
- `401 Unauthorized`: 未認證或 Token 過期
- `500 Internal Server Error`: 伺務器內部錯誤

---

### 📍 GET `/combine/user/virtual-try-on-detail/<model_uid>` ⭐ 查看試穿詳情
**描述**: 查看單筆虛擬試穿的完整詳情

**請求頭**:
```
Authorization: Bearer <access_token>
```

**路徑參數**:
```
model_uid: "550e8400-e29b-41d4-a716-446655440200" (試穿記錄 UID)
```

**成功響應 (200 OK)**:
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
      "clothes_category": "clothing",
      "clothes_image_url": "http://192.168.233.128:9000/clothes-bucket/...",
      "clothes_arm_length": 68,
      "clothes_shoulder_width": 48
    },
    {
      "clothes_uid": "550e8400-e29b-41d4-a716-446655440011",
      "clothes_category": "bottom",
      "clothes_image_url": "http://192.168.233.128:9000/clothes-bucket/...",
      "clothes_leg_length": 100,
      "clothes_waistline": 100
    }
  ],
  "created_at": "2026-03-29T10:30:00Z",
  "ai_response": {
    "code": 200,
    "message": "200",
    "data": {
      "file_name": "try_on_outfit_20260329.png",
      "style_name": ["Japanese Style", "Elegant", "Traditional"],
      "file_format": "PNG"
    }
  }
}
```

**錯誤響應**:
- `401 Unauthorized`: 未認證或 Token 過期
- `404 Not Found`: 試穿紀錄不存在
- `500 Internal Server Error`: 伺務器內部錯誤

---

### 📍 DELETE `/combine/user/virtual-try-on-delete/<model_uid>` ⭐ 刪除試穿結果
**描述**: 刪除一個虛擬試穿結果記錄（只能刪除自己的）

**請求頭**:
```
Authorization: Bearer <access_token>
```

**路徑參數**:
```
model_uid: "550e8400-e29b-41d4-a716-446655440200" (試穿記錄 UID)
```

**成功響應 (200 OK)**:
```json
{
  "success": true,
  "message": "試穿結果已成功刪除",
  "deleted_model_uid": "550e8400-e29b-41d4-a716-446655440200",
  "deleted_model_id": 12345
}
```

**錯誤響應**:
- `401 Unauthorized`: 未認證或 Token 過期
- `404 Not Found`: 試穿紀錄不存在或沒有權限刪除
  ```json
  {
    "success": false,
    "message": "試穿紀錄不存在或沒有權限刪除"
  }
  ```
- `500 Internal Server Error`: 伺務器內部錯誤

---

## ✅ 系統檢查 API

### 📍 GET `/health`
**描述**: 檢查後端伺務是否正常運行

**成功響應 (200 OK)**:
```json
{
  "status": "healthy",
  "message": "伺務運行正常"
}
```

---

## 📊 完整 API 路由表

| HTTP 方法 | 路徑 | 描述 | 認證 | 狀態 |
|----------|------|------|------|------|
| **POST** | `/account/user/register` | 用戶註冊 | ❌ | ✅ |
| **POST** | `/account/user/login` | 用戶登入 | ❌ | ✅ |
| **POST** | `/account/user/logout` | 用戶登出 | ✅ | ✅ |
| **POST** | `/account/user/user_info` | 上傳身體測量資料 | ✅ | ✅ |
| **POST** | `/account/user/delete` | 刪除帳號 | ✅ | ✅ |
| **GET** | `/account/user/list` | 查看用戶列表 | ❌ | ✅ |
| **POST** | `/picture/clothes/` | 新增衣伺（AI 去背） | ✅ | ✅ |
| **GET** | `/picture/clothes/my` | 我的衣伺列表 | ✅ | ✅ |
| **GET** | `/picture/clothes/favorites` | 我的收藏衣伺 | ✅ | ✅ |
| **GET** | `/picture/clothes/<clothes_uid>/` | 衣伺詳情 | ✅ | ✅ |
| **PUT** | `/picture/clothes/<clothes_uid>/` | 更新衣伺 | ✅ | ✅ |
| **DELETE** | `/picture/clothes/<clothes_uid>/` | 刪除衣伺 | ✅ | ✅ |
| **PATCH** | `/picture/clothes/<clothes_uid>/favorite` | 標記衣伺為喜歡 | ✅ | ✅ |
| **POST** | `/picture/user/photo` | 上傳模特照片 | ✅ | ✅ |
| **PUT** | `/picture/user/photo` | 更新模特照片 | ✅ | ✅ |
| **GET** | `/picture/user/photo` | 查看模特照片 | ✅ | ✅ |
| **POST** | `/combine/user/virtual-try-on` | 發起虛擬試穿 | ✅ | ✅ |
| **GET** | `/combine/user/virtual-try-on-history` | 試穿歷史 | ✅ | ✅ |
| **GET** | `/combine/user/virtual-try-on-detail/<model_uid>` | 試穿詳情 | ✅ | ✅ |
| **DELETE** | `/combine/user/virtual-try-on-delete/<model_uid>` | 刪除試穿結果 | ✅ | ✅ |
| **GET** | `/health` | 系統健康檢查 | ❌ | ✅ |

---

## 🔐 認證方式

所有需要認證的 API 都使用 **JWT Bearer Token** 模式：

```
Authorization: Bearer <jwt_access_token>
```

**取得方式**:
1. 使用者先呼叫 POST `/account/user/login` 登入
2. 後端返回 `access` 和 `refresh` token
3. 將 `access` token 添加到後續 API 請求的 Authorization 頭

**Token 刷新**:
- `access` token 有有效期限
- 過期後可使用 `refresh` token 重新取得新的 `access` token
- 實作方式：呼叫 POST `/account/user/logout` 並提供 `refresh` token

---

## 🛡️ 錯誤代碼總覽

| HTTP Code | 錯誤類型 | 說明 |
|-----------|--------|------|
| 200 | OK | 請求成功 |
| 201 | Created | 資源建立成功 |
| 400 | Bad Request | 請求參數錯誤或格式不正確 |
| 401 | Unauthorized | 認證失敗或令牌過期 |
| 403 | Forbidden | 無權限訪問此資源 |
| 404 | Not Found | 資源不存在 |
| 415 | Unsupported Media Type | 不支持的媒體類型 |
| 422 | Unprocessable Entity | 無法處理的實體 |
| 500 | Internal Server Error | 伺務器內部錯誤 |
| 503 | Service Unavailable | 伺務不可用 |
| 504 | Gateway Timeout | 請求超時 |

---

## 💡 使用示例

### Bash / cURL

#### 1. 用戶註冊
```bash
curl -X POST http://localhost:30000/account/user/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

#### 2. 用戶登入
```bash
curl -X POST http://localhost:30000/account/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

**取得 Token** (從響應中複製):
```bash
export ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIs..."
export REFRESH_TOKEN="eyJhbGciOiJIUzI1NiIs..."
```

#### 3. 上傳身體測量資料
```bash
curl -X POST http://localhost:30000/account/user/user_info \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_height": 180,
    "user_weight": 70,
    "user_arm_length": 65,
    "user_shoulder_width": 45,
    "user_waistline": 80,
    "user_leg_length": 105
  }'
```

#### 4. 上傳衣伺圖片
```bash
curl -X POST http://localhost:30000/picture/clothes/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "image_data=@/path/to/clothes.jpg" \
  -F "clothes_arm_length=65" \
  -F "clothes_shoulder_width=45"
```

#### 5. 上傳模特照片
```bash
curl -X POST http://localhost:30000/picture/user/photo \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "photo_file=@/path/to/model_photo.jpg"
```

#### 6. 發起虛擬試穿
```bash
curl -X POST http://localhost:30000/combine/user/virtual-try-on \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clothes_ids": [
      "550e8400-e29b-41d4-a716-446655440010",
      "550e8400-e29b-41d4-a716-446655440011"
    ]
  }'
```

#### 7. 查看試穿歷史
```bash
curl -X GET "http://localhost:30000/combine/user/virtual-try-on-history?page=1&limit=20" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### JavaScript/Fetch

```javascript
// 1. 用戶登入並保存 Token
const loginUser = async () => {
  const response = await fetch('http://localhost:30000/account/user/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: 'john_doe',
      password: 'SecurePass123'
    })
  });
  
  const data = await response.json();
  localStorage.setItem('accessToken', data.access);
  localStorage.setItem('refreshToken', data.refresh);
  return data.access;
};

// 2. 上傳衣伺圖片
const uploadClothes = async (imageFile, accessToken) => {
  const formData = new FormData();
  formData.append('image_data', imageFile);
  formData.append('clothes_arm_length', 65);
  formData.append('clothes_shoulder_width', 45);
  
  const response = await fetch('http://localhost:30000/picture/clothes/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    },
    body: formData
  });
  
  return response.json();
};

// 3. 發起虛擬試穿
const startVirtualTryOn = async (clothesIds, accessToken) => {
  const response = await fetch('http://localhost:30000/combine/user/virtual-try-on', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      clothes_ids: clothesIds
    })
  });
  
  return response.json();
};
```

---

## 📋 常見問題

### Q1: 如何處理 Token 過期？
**A**: 當收到 401 Unauthorized 錯誤時，使用 refresh token 重新取得新的 access token。實作方式見上面的例子。

### Q2: 虛擬試穿前需要先上傳什麼？
**A**: 
1. 上傳身體測量資料（user_info）
2. 上傳模特照片（user/photo）
3. 上傳至少 2 件衣伺圖片（clothes/）
4. 才能發起虛擬試穿

### Q3: 衣伺圖片有什麼格式限制？
**A**: 支持 JPG、PNG、GIF、WebP 格式，最大 10MB。系統會自動轉發給 AI 進行去背處理。

### Q4: 虛擬試穿結果會儲存多久？
**A**: 試穿結果會永久儲存在資料庫和 MinIO 中，直到使用者手動刪除。

### Q5: 模特照片可以重複上傳嗎？
**A**: 可以。使用 POST 上傳新照片，或使用 PUT 更新現有照片。新照片會自動覆蓋舊照片。

---

## 🚀 測試端點

系統提供 `/health` 端點用於快速測試：

```bash
curl http://localhost:30000/health
```

**成功響應**:
```json
{
  "status": "healthy",
  "message": "伺務運行正常"
}
```

---

**最後更新**: 2026-03-29  
**版本**: 1.0 完整實現版  
**聯絡**: 查看 Architecture.md 了解系統架構詳情
