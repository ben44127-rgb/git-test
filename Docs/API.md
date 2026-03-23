# API 文檔

> 更新時間: 2026-03-23  
> 說明: test_project Main Backend 的完整 API 文檔，包含所有端點、參數、響應示例

---

## 📋 API 概覽

| 模組 | 基礎路徑 | 說明 |
|------|--------|------|
| **認證** | `/account/user/` | 用戶註冊、登錄、登出等認證功能 |
| **圖片管理** | `/picture/clothes/` | 服裝圖片上傳、管理功能 |
| **健康檢查** | `/health` | 服務狀態檢查 |

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

## 📸 圖片管理 API

### 📍 POST `/picture/clothes/upload_image`
**描述**: 上傳服裝圖片到 MinIO 存儲

**請求頭**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**請求體 (form-data)**:
```
file: <binary image data>
category: "shirt" | "pants" | "dress" | "shoes"
user_id: 1
```

**成功響應 (200 OK)**:
```json
{
  "image_id": 123,
  "user_id": 1,
  "filename": "shoes_001.jpg",
  "file_size": 2048576,
  "category": "shirt",
  "minIO_url": "http://192.168.233.128:9000/bucket/user_1/shoes_001.jpg",
  "presigned_url": "http://192.168.233.128:9000/bucket/user_1/shoes_001.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&...",
  "presigned_url_expires": 900,
  "uploaded_at": "2026-03-23T16:00:00Z"
}
```

**錯誤響應 (400 Bad Request)**:
```json
{
  "error": "invalid_file_format",
  "message": "只支持 JPG, PNG, GIF 格式"
}
```

**錯誤響應 (413 Payload Too Large)**:
```json
{
  "error": "file_too_large",
  "message": "文件大小超過 50MB 限制"
}
```

---

### 📍 POST `/picture/clothes/` ✅ 新增功能
**描述**: 創建新衣服（需要管理員權限）

**請求頭**:
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**請求體**:
```json
{
  "clothes_category": "上衣",
  "clothes_arm_length": 60,
  "clothes_shoulder_width": 45,
  "clothes_waistline": 80,
  "clothes_leg_length": 0,
  "clothes_image_url": "http://minio.example.com/bucket/clothes_001.jpg",
  "colors": ["藍色", "紅色", "黑色"],
  "styles": ["休閒", "正式", "運動"]
}
```

**成功響應 (201 Created)**:
```json
{
  "clothes_id": 1,
  "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
  "clothes_category": "上衣",
  "clothes_arm_length": 60,
  "clothes_shoulder_width": 45,
  "clothes_waistline": 80,
  "clothes_leg_length": 0,
  "clothes_image_url": "http://minio.example.com/bucket/clothes_001.jpg",
  "clothes_favorite": false,
  "clothes_created_time": "2026-03-23T16:00:00Z",
  "clothes_updated_time": "2026-03-23T16:00:00Z",
  "colors": [
    {"color_id": 1, "color_uid": "...", "color_name": "藍色"},
    {"color_id": 2, "color_uid": "...", "color_name": "紅色"},
    {"color_id": 3, "color_uid": "...", "color_name": "黑色"}
  ],
  "styles": [
    {"style_id": 1, "style_uid": "...", "style_name": "休閒"},
    {"style_id": 2, "style_uid": "...", "style_name": "正式"},
    {"style_id": 3, "style_uid": "...", "style_name": "運動"}
  ]
}
```

**錯誤響應**:
- `400 Bad Request`: 數據驗證失敗
- `403 Forbidden`: 無管理員權限

---

### 📍 GET `/picture/clothes/` ✅ 新增功能
**描述**: 獲取衣服列表（支持分頁和篩選）

**請求頭**:
```
Authorization: Bearer <token>
```

**查詢參數**:
```
page: 1 (分頁頁數)
limit: 20 (每頁數量)
category: "上衣" (按分類篩選，可選)
```

**示例**:
```
GET /picture/clothes/?page=1&limit=20&category=上衣
```

**成功響應 (200 OK)**:
```json
{
  "count": 150,
  "total_pages": 8,
  "current_page": 1,
  "results": [
    {
      "clothes_id": 1,
      "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
      "clothes_category": "上衣",
      "clothes_arm_length": 60,
      "clothes_shoulder_width": 45,
      "clothes_waistline": 80,
      "clothes_leg_length": 0,
      "clothes_image_url": "http://minio.example.com/...",
      "clothes_favorite": false,
      "clothes_created_time": "2026-03-23T16:00:00Z",
      "clothes_updated_time": "2026-03-23T16:00:00Z",
      "colors": [
        {"color_id": 1, "color_uid": "...", "color_name": "藍色"}
      ],
      "styles": [
        {"style_id": 1, "style_uid": "...", "style_name": "休閒"}
      ]
    }
  ]
}
```

---

### 📍 GET `/picture/clothes/{id}/` ✅ 新增功能
**描述**: 獲取衣服詳情

**請求頭**:
```
Authorization: Bearer <token>
```

**路徑參數**:
```
id: 1 (衣服 ID)
```

**成功響應 (200 OK)**:
```json
{
  "clothes_id": 1,
  "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
  "clothes_category": "上衣",
  "clothes_arm_length": 60,
  "clothes_shoulder_width": 45,
  "clothes_waistline": 80,
  "clothes_leg_length": 0,
  "clothes_image_url": "http://minio.example.com/...",
  "clothes_favorite": false,
  "clothes_created_time": "2026-03-23T16:00:00Z",
  "clothes_updated_time": "2026-03-23T16:00:00Z",
  "colors": [
    {"color_id": 1, "color_uid": "...", "color_name": "藍色"},
    {"color_id": 2, "color_uid": "...", "color_name": "紅色"}
  ],
  "styles": [
    {"style_id": 1, "style_uid": "...", "style_name": "休閒"},
    {"style_id": 2, "style_uid": "...", "style_name": "正式"}
  ]
}
```

**錯誤響應 (404 Not Found)**:
```json
{
  "detail": "Not found."
}
```

---

### 📍 PUT `/picture/clothes/{id}/` ✅ 新增功能
**描述**: 更新衣服（需要管理員權限）

**請求頭**:
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**路徑參數**:
```
id: 1 (衣服 ID)
```

**請求體**:
```json
{
  "clothes_category": "褲子",
  "clothes_arm_length": 0,
  "clothes_shoulder_width": 0,
  "clothes_waistline": 85,
  "clothes_leg_length": 100,
  "clothes_image_url": "http://minio.example.com/bucket/pants_001.jpg",
  "colors": ["黑色", "藍色"],
  "styles": ["正式", "商務"]
}
```

**成功響應 (200 OK)**:
```json
{
  "clothes_id": 1,
  "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
  "clothes_category": "褲子",
  "clothes_arm_length": 0,
  "clothes_shoulder_width": 0,
  "clothes_waistline": 85,
  "clothes_leg_length": 100,
  "clothes_image_url": "http://minio.example.com/bucket/pants_001.jpg",
  "clothes_favorite": false,
  "clothes_created_time": "2026-03-23T16:00:00Z",
  "clothes_updated_time": "2026-03-23T16:30:00Z",
  "colors": [
    {"color_id": 1, "color_uid": "...", "color_name": "黑色"},
    {"color_id": 2, "color_uid": "...", "color_name": "藍色"}
  ],
  "styles": [
    {"style_id": 1, "style_uid": "...", "style_name": "正式"},
    {"style_id": 2, "style_uid": "...", "style_name": "商務"}
  ]
}
```

**錯誤響應**:
- `400 Bad Request`: 數據驗證失敗
- `403 Forbidden`: 無管理員權限
- `404 Not Found`: 衣服不存在

---

### 📍 DELETE `/picture/clothes/{id}/` ✅ 新增功能
**描述**: 刪除衣服（需要管理員權限）

**請求頭**:
```
Authorization: Bearer <admin_token>
```

**路徑參數**:
```
id: 1 (衣服 ID)
```

**成功響應 (200 OK)**:
```json
{
  "detail": "衣服已刪除"
}
```

**錯誤響應**:
- `403 Forbidden`: 無管理員權限
- `404 Not Found`: 衣服不存在

---

## ✅ 系統檢查 API

### 📍 GET `/health`
**描述**: 檢查後端服務是否正常運行

**請求頭**: 無

**成功響應 (200 OK)**:
```json
{
  "status": "ok",
  "timestamp": "2026-03-23T16:30:00Z",
  "database": "connected",
  "minio": "connected",
  "version": "1.0.0"
}
```

**服務異常響應 (503 Service Unavailable)**:
```json
{
  "status": "error",
  "timestamp": "2026-03-23T16:35:00Z",
  "database": "disconnected",
  "minio": "connected",
  "message": "PostgreSQL 數據庫連接失敗"
}
```

---

## 📊 API 路由總表

| 方法 | 路徑 | 描述 | 認證 |
|------|------|------|------|
| POST | `/account/user/register` | 用戶註冊 | ❌ |
| POST | `/account/user/login` | 用戶登錄 | ❌ |
| POST | `/account/user/logout` | 用戶登出 | ✅ |
| GET | `/account/user/list` | 列出用戶（管理員） | ✅ |
| POST | `/account/user/delete` | 刪除用戶 | ✅ |
| POST | `/picture/clothes/` | 新增衣服（管理員） | ✅ |
| GET | `/picture/clothes/` | 查看衣服列表 | ✅ |
| GET | `/picture/clothes/{id}/` | 查看衣服詳情 | ✅ |
| PUT | `/picture/clothes/{id}/` | 更新衣服（管理員） | ✅ |
| DELETE | `/picture/clothes/{id}/` | 刪除衣服（管理員） | ✅ |
| POST | `/picture/clothes/upload_image` | 上傳圖片 | ✅ |
| GET | `/health` | 健康檢查 | ❌ |

---

## 🔐 認證方式

所有需要認證的 API 都使用 **Bearer Token** 模式：

```
Authorization: Bearer <jwt_token>
```

**JWT Token 結構**:
```json
Header: {
  "alg": "HS256",
  "typ": "JWT"
}

Payload: {
  "user_id": 1,
  "username": "john_doe",
  "iat": 1679580000,
  "exp": 1679666400
}

Signature: HMAC_SHA256(header.payload, secret_key)
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
| 413 | Payload Too Large | 上傳文件過大 |
| 429 | Too Many Requests | 請求過於頻繁（速率限制） |
| 500 | Internal Server Error | 服務器內部錯誤 |
| 503 | Service Unavailable | 服務不可用（數據庫或 MinIO 連接失敗） |

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
           console.warn('服務異常:', data.message);
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
