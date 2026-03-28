# API 文檔

> 更新時間: 2026-03-27  
> 說明: test_project Main Backend 的完整 API 文檔，包含所有端點、參數、響應示例
> 最新更新: 照片管理模塊重組 - 整合衣伺管理和用戶個人照片上傳功能

---

## 📋 API 概覽

| 模組 | 基礎路徑 | 說明 |
|------|--------|------|
| **認證** | `/account/user/` | 用戶註冊、登錄、登出等認證功能 |
| **照片管理** | `/picture/` | 衣伺、穿搭列表管理、用戶個人照片 |
| **健康檢查** | `/health` | 伺務狀態檢查 |

---

## 🔐 認證 API

### 📍 POST `/account/user/register`
**描述**: 新用戶註冊

**請求頭**:
```
Content-Type: application/json
```

**請求體**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**成功響應 (200 OK)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "created_at": "2026-03-23T12:00:00Z"
}
```

**錯誤響應 (400 Bad Request)**:
```json
{
  "error": "username_already_exists",
  "message": "用戶名已存在"
}
```

---

### 📍 POST `/account/user/login`
**描述**: 用戶登錄，獲取認證令牌

**請求頭**:
```
Content-Type: application/json
```

**請求體**:
```json
{
  "username": "john_doe",
  "password": "secure_password_123"
}
```

**成功響應 (200 OK)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2026-03-24T12:00:00Z",
  "token_type": "Bearer"
}
```

**錯誤響應 (401 Unauthorized)**:
```json
{
  "error": "invalid_credentials",
  "message": "用戶名或密碼錯誤"
}
```

---

### 📍 POST `/account/user/logout`
**描述**: 用戶登出，使令牌失效

**請求頭**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**請求體**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**成功響應 (200 OK)**:
```json
{
  "status": "success",
  "message": "已成功登出"
}
```

**錯誤響應 (401 Unauthorized)**:
```json
{
  "error": "invalid_token",
  "message": "令牌無效或已過期"
}
```

---

### 📍 GET `/account/user/list`
**描述**: 獲取用戶列表（僅管理員可用）

**請求頭**:
```
Authorization: Bearer <admin_token>
```

**查詢參數**:
```
?page=1&limit=10
```

**成功響應 (200 OK)**:
```json
{
  "users": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2026-03-23T12:00:00Z"
    },
    {
      "id": 2,
      "username": "jane_smith",
      "email": "jane@example.com",
      "created_at": "2026-03-23T14:30:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "limit": 10
}
```

**錯誤響應 (403 Forbidden)**:
```json
{
  "error": "permission_denied",
  "message": "只有管理員可以訪問此端點"
}
```

---

### 📍 POST `/account/user/delete`
**描述**: 刪除用戶賬戶

**請求頭**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**請求體**:
```json
{
  "user_id": 1,
  "password": "confirm_password"
}
```

**成功響應 (200 OK)**:
```json
{
  "status": "success",
  "message": "用戶已刪除",
  "deleted_at": "2026-03-23T15:45:00Z"
}
```

**錯誤響應 (401 Unauthorized)**:
```json
{
  "error": "invalid_password",
  "message": "密碼錯誤"
}
```

---

## 📸 照片管理 API

### 📕 衣伺管理端點

### 📍 POST `/picture/clothes/` ⭐ 新增衣伺
**描述**: 用戶上傳衣伺圖片，系統進行 AI 去背並自動提取衣伺信息

**請求頭**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**請求體 (form-data)**:
```
image_data: <二進位圖片檔案> (必需)
user_uid: <用戶UID> (可選，若使用JWT可不提供)
```

**完整流程**:
```
1. 用戶上傳圖片 + 基本尺寸信息
   ↓
2. 後端轉發給 AI 進行去背處理
   ↓
3. AI 分析並返回：衣伺分類、顏色、風格
   ↓
4. 圖片存儲到 MinIO
   ↓
5. 完整數據存儲到 DB
   ↓
6. 返回衣伺詳情給前端
```

**成功響應 (200 OK)**:
```json
{
  "success": true,
  "message": "圖片處理和儲存成功",
  "processed_url": "http://minio.example.com/bucket/processed_image.png",
  "ai_status": {
    "status_code": 200,
    "message": "去背成功",
    "tools_status": {
      "rembg_engine": "success",
      "opencv_masking": "success",
      "gemini_consultant": "success"
    }
  },
  "storage_status": {
    "success": true,
    "filename": "unique_id_cleaned_garment.png",
    "file_format": "PNG",
    "storage": "minio",
    "bucket": "clothes-bucket"
  },
  "clothes_data": {
    "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
    "clothes_category": "T-shirt",
    "styles": ["Casual", "Formal", "Streetwear"],
    "colors": ["red", "blue", "green"],
    "image_url": "http://minio.example.com/..."
  }
}
```

**錯誤響應**:
- `400 Bad Request`: 缺少圖片或檔案驗證失敗
- `401 Unauthorized`: 未認證或令牌過期
- `415 Unsupported Media Type`: 上傳非圖片檔案
- `422 Unprocessable Entity`: 圖片過於模糊或無法處理
- `503 Service Unavailable`: AI 或 MinIO 伺務不可用
- `504 Gateway Timeout`: AI 處理逾時

---

### 📍 GET `/picture/clothes/my` ⭐ 我的衣伺列表
**描述**: 獲取當前用戶的衣伺列表（管理員可查看所有）

**請求頭**:
```
Authorization: Bearer <token>
```

**查詢參數**:
```
page: 1 (分頁頁數，預設1)
limit: 20 (每頁數量，預設20)
category: "上衣" (按分類篩選，可選)
```

**示例**:
```
GET /picture/clothes/my?page=1&limit=20&category=T-shirt
```

**成功響應 (200 OK)**:
```json
{
  "count": 15,
  "total_pages": 1,
  "current_page": 1,
  "results": [
    {
      "clothes_id": 1,
      "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
      "clothes_category": "T-shirt",
      "clothes_arm_length": 60,
      "clothes_shoulder_width": 45,
      "clothes_waistline": 80,
      "clothes_leg_length": 0,
      "clothes_image_url": "http://minio.example.com/...",
      "clothes_favorite": false,
      "clothes_created_time": "2026-03-27T16:00:00Z",
      "clothes_updated_time": "2026-03-27T16:00:00Z",
      "colors": [
        {"color_id": 1, "color_uid": "...", "color_name": "red"},
        {"color_id": 2, "color_uid": "...", "color_name": "blue"}
      ],
      "styles": [
        {"style_id": 1, "style_uid": "...", "style_name": "Casual"},
        {"style_id": 2, "style_uid": "...", "style_name": "Formal"}
      ]
    }
  ]
}
```

**錯誤響應**:
- `401 Unauthorized`: 未認證或令牌過期
- `500 Internal Server Error`: 伺務器內部錯誤

---

### 📍 GET `/picture/clothes/<id>/` ✅ 衣伺詳情
**描述**: 獲取單個衣伺的詳細信息

**請求頭**:
```
Authorization: Bearer <token>
```

**路徑參數**:
```
id: 1 (衣伺 ID)
```

**成功響應 (200 OK)**:
```json
{
  "clothes_id": 1,
  "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
  "clothes_category": "T-shirt",
  "clothes_arm_length": 60,
  "clothes_shoulder_width": 45,
  "clothes_waistline": 80,
  "clothes_leg_length": 0,
  "clothes_image_url": "http://minio.example.com/...",
  "clothes_favorite": false,
  "clothes_created_time": "2026-03-27T16:00:00Z",
  "clothes_updated_time": "2026-03-27T16:00:00Z",
  "colors": [
    {"color_id": 1, "color_uid": "...", "color_name": "red"},
    {"color_id": 2, "color_uid": "...", "color_name": "blue"}
  ],
  "styles": [
    {"style_id": 1, "style_uid": "...", "style_name": "Casual"},
    {"style_id": 2, "style_uid": "...", "style_name": "Formal"}
  ]
}
```

**錯誤響應**:
- `401 Unauthorized`: 未認證或令牌過期
- `404 Not Found`: 衣伺不存在

---

### 📍 PUT `/picture/clothes/<id>/` ✅ 更新衣伺
**描述**: 更新衣伺信息（衣伺擁有者或管理員）

**請求頭**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**路徑參數**:
```
id: 1 (衣伺 ID)
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
  "clothes_image_url": "http://minio.example.com/...",
  "clothes_favorite": false,
  "clothes_created_time": "2026-03-27T16:00:00Z",
  "clothes_updated_time": "2026-03-27T16:30:00Z",
  "colors": [
    {"color_id": 1, "color_uid": "...", "color_name": "black"},
    {"color_id": 2, "color_uid": "...", "color_name": "blue"}
  ],
  "styles": [
    {"style_id": 1, "style_uid": "...", "style_name": "Formal"},
    {"style_id": 2, "style_uid": "...", "style_name": "Business"}
  ]
}
```

**錯誤響應**:
- `400 Bad Request`: 數據驗證失敗
- `401 Unauthorized`: 未認證或令牌過期
- `403 Forbidden`: 無權限修改（只有擁有者或管理員可修改）
- `404 Not Found`: 衣伺不存在

---

### 📍 DELETE `/picture/clothes/<id>/` ✅ 刪除衣伺
**描述**: 刪除衣伺（衣伺擁有者或管理員）

**請求頭**:
```
Authorization: Bearer <token>
```

**路徑參數**:
```
id: 1 (衣伺 ID)
```

**成功響應 (200 OK)**:
```json
{
  "detail": "衣伺已刪除"
}
```

**錯誤響應**:
- `401 Unauthorized`: 未認證或令牌過期
- `403 Forbidden`: 無權限刪除（只有擁有者或管理員可刪除）
- `404 Not Found`: 衣伺不存在

---

### 📸 用戶照片管理端點

### 📍 POST `/picture/user/photo` ⭐ 上傳個人照片
**描述**: 用戶上傳個人照片（全身照、頭像等），存儲到 MinIO 並更新用戶檔案

**請求頭**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**請求體 (form-data)**:
```
photo_file: <二進位圖片檔案> (JPG, PNG, GIF, WebP，最大 10MB)
```

**成功響應 (201 Created)**:
```json
{
  "success": true,
  "message": "個人照片上傳成功",
  "photo_url": "http://minio.example.com/bucket/user_uuid_photo_uuid.png",
  "user": {
    "user_uid": "550e8400-e29b-41d4-a716-446655440000",
    "user_name": "john_doe",
    "user_image_url": "http://minio.example.com/bucket/user_uuid_photo_uuid.png"
  }
}
```

**錯誤響應**:
- `400 Bad Request`: 缺少檔案參數或檔案過大 (>10MB)
- `401 Unauthorized`: Token 無效或過期
- `415 Unsupported Media Type`: 不支持的檔案類型
- `503 Service Unavailable`: MinIO 存儲伺務不可用

---

## ✅ 系統檢查 API

### 📍 GET `/health`
**描述**: 檢查後端伺務是否正常運行

**請求頭**: 無

**成功響應 (200 OK)**:
```json
{
  "status": "healthy",
  "message": "伺務運行正常"
}
```

---

## 📊 API 路由總表

| 方法 | 路徑 | 描述 | 認證 | 備註 |
|------|------|------|------|------|
| POST | `/account/user/register` | 用戶註冊 | ❌ | - |
| POST | `/account/user/login` | 用戶登錄 | ❌ | - |
| POST | `/account/user/logout` | 用戶登出 | ✅ | - |
| GET | `/account/user/list` | 列出用戶 | ✅ | 管理員 |
| POST | `/account/user/delete` | 刪除用戶 | ✅ | - |
| **POST** | **`/picture/clothes/`** | **新增衣伺** | ✅ | **⭐ 統一端點** |
| **GET** | **`/picture/clothes/my`** | **我的衣伺** | ✅ | **用戶查看** |
| GET | `/picture/clothes/<id>/` | 衣伺詳情 | ✅ | - |
| PUT | `/picture/clothes/<id>/` | 更新衣伺 | ✅ | 擁有者/管理員 |
| DELETE | `/picture/clothes/<id>/` | 刪除衣伺 | ✅ | 擁有者/管理員 |
| GET | `/health` | 健康檢查 | ❌ | - |

---

## 🔐 認證方式

所有需要認證的 API 都使用 **Bearer Token** 模式：

```
Authorization: Bearer <jwt_token>
```

---

## 🛡️ 錯誤代碼總覽

| HTTP Code | 錯誤類型 | 說明 |
|-----------|--------|------|
| 200 | OK | 請求成功 |
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

### JavaScript/Fetch

```javascript
// 1. 用戶註冊
const registerUser = async () => {
  const response = await fetch('http://localhost:30000/account/user/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: 'john_doe',
      email: 'john@example.com',
      password: 'secure_password_123'
    })
  });
  
  const data = await response.json();
  return data.token; // 保存 token
};

// 2. 用戶登錄
const loginUser = async () => {
  const response = await fetch('http://localhost:30000/account/user/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: 'john_doe',
      password: 'secure_password_123'
    })
  });
  
  const data = await response.json();
  localStorage.setItem('token', data.token); // 保存 token
  return data;
};

// 3. 上傳圖片
const uploadImage = async (file, category, userId) => {
  const token = localStorage.getItem('token');
  const formData = new FormData();
  formData.append('file', file);
  formData.append('category', category);
  formData.append('user_id', userId);
  
  const response = await fetch('http://localhost:30000/picture/clothes/upload_image', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  return await response.json();
};

// 4. 健康檢查
const checkHealth = async () => {
  const response = await fetch('http://localhost:30000/health');
  return await response.json();
};

// 5. 用戶登出
const logoutUser = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:30000/account/user/logout', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ token })
  });
  
  localStorage.removeItem('token');
  return await response.json();
};
```

### Python/Requests

```python
import requests

BASE_URL = 'http://localhost:30000'

# 1. 用戶註冊
def register_user(username, email, password):
    response = requests.post(
        f'{BASE_URL}/account/user/register',
        json={
            'username': username,
            'email': email,
            'password': password
        }
    )
    return response.json()

# 2. 用戶登錄
def login_user(username, password):
    response = requests.post(
        f'{BASE_URL}/account/user/login',
        json={
            'username': username,
            'password': password
        }
    )
    data = response.json()
    token = data.get('token')
    return token

# 3. 上傳圖片
def upload_image(token, file_path, category, user_id):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    with open(file_path, 'rb') as f:
        files = {
            'file': f,
            'category': (None, category),
            'user_id': (None, str(user_id))
        }
        response = requests.post(
            f'{BASE_URL}/picture/clothes/upload_image',
            headers=headers,
            files=files
        )
    
    return response.json()

# 4. 健康檢查
def check_health():
    response = requests.get(f'{BASE_URL}/health')
    return response.json()

# 5. 用戶登出
def logout_user(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(
        f'{BASE_URL}/account/user/logout',
        json={'token': token},
        headers=headers
    )
    return response.json()
```

---

## 🚀 最佳實踐

1. **始終包含認證令牌**
   ```
   Authorization: Bearer <token>
   ```

2. **處理錯誤響應**
   ```javascript
   fetch(url, options)
     .then(res => {
       if (!res.ok) {
         throw new Error(`HTTP ${res.status}`);
       }
       return res.json();
     })
     .catch(err => console.error(err));
   ```

3. **定期檢查健康狀態**
   ```javascript
   setInterval(() => {
     fetch('http://localhost:30000/health')
       .then(res => res.json())
       .then(data => {
         if (data.status !== 'ok') {
           console.warn('伺務異常:', data.message);
         }
       });
   }, 30000); // 每 30 秒檢查一次
   ```

4. **保存和更新 Token**
   - 登錄後立即保存 token
   - 在每個需要認證的請求中使用
   - 關閉應用前登出，清除 token

---

**版本**: 1.0.0  
**最後更新**: 2026-03-23
