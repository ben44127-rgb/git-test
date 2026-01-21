# 用戶認證系統說明

本系統已整合完整的用戶認證功能，包含登入、登出、註冊、刪除用戶等功能。

## 系統架構

### 服務配置
- **Django 後端**: `http://localhost:30000` (圖片處理 API)
- **認證系統 API**: `http://localhost:30000/api/auth/` (用戶認證)
- **PostgreSQL 數據庫**: `localhost:9090` (用戶數據存儲)
- **MinIO 對象存儲**: `localhost:9000` (圖片存儲)

### 已安裝的應用
- `api` - 圖片處理 API
- `accounts` - 用戶認證系統
- Django REST Framework
- PostgreSQL 數據庫支持

## 認證 API 端點

### 基礎 URL
所有認證 API 的基礎 URL: `http://localhost:30000/api/auth/`

### 1. 用戶註冊
**POST** `/api/auth/register/`

請求範例：
```json
{
  "username": "testuser",
  "password": "securepass123",
  "email": "test@example.com"
}
```

成功響應 (201):
```json
{
  "success": true,
  "message": "註冊成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

### 2. 用戶登入
**POST** `/api/auth/login/`

請求範例：
```json
{
  "username": "testuser",
  "password": "securepass123"
}
```

成功響應 (200):
```json
{
  "success": true,
  "message": "登入成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_staff": false,
    "is_active": true
  }
}
```

### 3. 用戶登出
**POST** `/api/auth/logout/`

成功響應 (200):
```json
{
  "success": true,
  "message": "用戶 testuser 已登出"
}
```

### 4. 刪除用戶
**DELETE** `/api/auth/delete/`

請求範例：
```json
{
  "password": "securepass123"
}
```

成功響應 (200):
```json
{
  "success": true,
  "message": "用戶 testuser 已刪除"
}
```

### 5. 檢查登入狀態
**GET** `/api/auth/check/`

成功響應 (200):
```json
{
  "success": true,
  "authenticated": true,
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_staff": false
  }
}
```

## 前端整合範例

### Fetch API 範例

```javascript
const API_BASE = 'http://localhost:30000/api/auth';

// 註冊
async function register(username, password, email) {
  const response = await fetch(`${API_BASE}/register/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // 重要：包含 cookies
    body: JSON.stringify({ username, password, email })
  });
  return await response.json();
}

// 登入
async function login(username, password) {
  const response = await fetch(`${API_BASE}/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ username, password })
  });
  return await response.json();
}

// 登出
async function logout() {
  const response = await fetch(`${API_BASE}/logout/`, {
    method: 'POST',
    credentials: 'include'
  });
  return await response.json();
}

// 刪除帳戶
async function deleteAccount(password) {
  const response = await fetch(`${API_BASE}/delete/`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ password })
  });
  return await response.json();
}

// 檢查登入狀態
async function checkAuth() {
  const response = await fetch(`${API_BASE}/check/`, {
    method: 'GET',
    credentials: 'include'
  });
  return await response.json();
}
```

### Axios 範例

```javascript
import axios from 'axios';

const authAPI = axios.create({
  baseURL: 'http://localhost:30000/api/auth',
  withCredentials: true // 重要：自動發送 cookies
});

export const authService = {
  register: (username, password, email) => 
    authAPI.post('/register/', { username, password, email }),
  
  login: (username, password) => 
    authAPI.post('/login/', { username, password }),
  
  logout: () => 
    authAPI.post('/logout/'),
  
  deleteAccount: (password) => 
    authAPI.delete('/delete/', { data: { password } }),
  
  checkAuth: () => 
    authAPI.get('/check/'),
};
```

### React Hook 範例

```javascript
import { useState, useEffect } from 'react';

function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('http://localhost:30000/api/auth/check/', {
        credentials: 'include'
      });
      const data = await response.json();
      if (data.authenticated) {
        setUser(data.data);
      }
    } catch (error) {
      console.error('檢查登入狀態失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    const response = await fetch('http://localhost:30000/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    if (data.success) {
      setUser(data.data);
    }
    return data;
  };

  const logout = async () => {
    await fetch('http://localhost:30000/api/auth/logout/', {
      method: 'POST',
      credentials: 'include'
    });
    setUser(null);
  };

  return { user, loading, login, logout, checkAuthStatus };
}

export default useAuth;
```

## 數據庫管理

### 訪問 PostgreSQL

```bash
# 進入數據庫容器
docker exec -it auth_postgres psql -U auth_user -d auth_db

# 查看所有表
\dt

# 查看用戶數據
SELECT id, username, email, is_staff, is_active, date_joined FROM auth_user;

# 退出
\q
```

### 使用外部工具連接

使用 pgAdmin、DBeaver 等工具：
- **Host**: localhost
- **Port**: 9090
- **Database**: auth_db
- **Username**: auth_user
- **Password**: auth_password_123

## 啟動系統

### 使用 Docker (推薦)

```bash
cd /home/ben/test_project

# 啟動所有服務（包含認證系統）
./start.sh --docker

# 或直接使用 docker-compose
docker-compose up -d --build

# 查看日誌
docker-compose logs -f backend
```

### 系統初始化

首次啟動後，Django 會自動執行數據庫遷移，創建用戶表。

創建管理員帳號（可選）：
```bash
docker exec -it django-backend python manage.py createsuperuser
```

訪問 Django Admin: `http://localhost:30000/admin/`

## 測試 API

### 使用 curl

```bash
# 註冊用戶
curl -X POST http://localhost:30000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123","email":"test@test.com"}'

# 登入（保存 cookie）
curl -X POST http://localhost:30000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"test","password":"test123"}'

# 檢查登入狀態
curl -X GET http://localhost:30000/api/auth/check/ \
  -b cookies.txt

# 登出
curl -X POST http://localhost:30000/api/auth/logout/ \
  -b cookies.txt

# 刪除用戶
curl -X DELETE http://localhost:30000/api/auth/delete/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"password":"test123"}'
```

### 使用 Python requests

```python
import requests

API_BASE = 'http://localhost:30000/api/auth'
session = requests.Session()

# 註冊
response = session.post(f'{API_BASE}/register/', json={
    'username': 'testuser',
    'password': 'test123',
    'email': 'test@test.com'
})
print(response.json())

# 登入
response = session.post(f'{API_BASE}/login/', json={
    'username': 'testuser',
    'password': 'test123'
})
print(response.json())

# 檢查狀態
response = session.get(f'{API_BASE}/check/')
print(response.json())

# 登出
response = session.post(f'{API_BASE}/logout/')
print(response.json())
```

## 安全注意事項

### 開發環境
- ✅ CORS 已設置為允許所有來源
- ✅ Session 認證已配置
- ✅ CSRF 保護已啟用

### 生產環境建議
1. 修改 `DJANGO_SECRET_KEY` 為隨機字符串
2. 設置 `DEBUG=False`
3. 配置 `ALLOWED_HOSTS` 為具體域名
4. 修改數據庫密碼
5. 使用 HTTPS
6. 配置具體的 CORS 白名單
7. 啟用更嚴格的 Session 安全設置

## 錯誤處理

### 常見錯誤響應

**用戶已存在 (400)**
```json
{
  "success": false,
  "message": "用戶名已存在"
}
```

**登入失敗 (401)**
```json
{
  "success": false,
  "message": "用戶名或密碼錯誤"
}
```

**未登入 (401)**
```json
{
  "success": false,
  "message": "請先登入"
}
```

**密碼錯誤 (401)**
```json
{
  "success": false,
  "message": "密碼錯誤"
}
```

## 停止系統

```bash
# 使用腳本停止
./stop.sh --docker

# 或直接使用 docker-compose
docker-compose down

# 刪除所有數據（包含數據庫）
docker-compose down -v
```

## 目錄結構

```
test_project/
├── accounts/              # 用戶認證應用
│   ├── views.py          # 認證 API 視圖
│   ├── urls.py           # 認證路由
│   └── models.py         # 數據模型
├── api/                  # 圖片處理 API
├── config/               # Django 配置
│   ├── settings.py      # 主配置（已整合認證）
│   └── urls.py          # URL 路由（已整合認證）
├── docker-compose.yml   # Docker 配置（已整合 PostgreSQL）
├── .env                 # 環境變數（已添加數據庫配置）
├── requirements.txt     # Python 依賴（已添加認證相關）
└── AUTH_SYSTEM.md       # 本文件
```

## 技術棧

- **Django 5.1.5**: Web 框架
- **Django REST Framework 3.14.0**: REST API 框架
- **PostgreSQL 15**: 關係型數據庫（用戶數據）
- **MinIO**: 對象存儲（圖片文件）
- **psycopg2-binary**: PostgreSQL 適配器
- **django-cors-headers**: CORS 支持
- **Docker & Docker Compose**: 容器化部署
