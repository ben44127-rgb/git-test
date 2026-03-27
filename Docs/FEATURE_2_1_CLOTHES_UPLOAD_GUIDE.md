# Feature 2.1 - 衣服上傳與尺寸參數指南

## 功能說明

功能 2.1 允許用戶上傳衣服圖片，並同時提交衣服的尺寸參數。系統會將圖片和尺寸信息同時發送給 AI 後端進行去背處理，然後將所有數據（包括尺寸）存儲在數據庫中。

## API 端點

**URL:** `POST /picture/clothes/`

**Content-Type:** `multipart/form-data`

## 請求參數

### 必填參數

| 參數名 | 類型 | 描述 | 範例 |
|-------|------|------|------|
| `image_data` | File | 衣服圖片文件 | 任何有效的圖片文件 |

### 可選參數（衣服尺寸）

| 參數名 | 類型 | 範圍 | 默認值 | 描述 |
|-------|------|------|--------|------|
| `clothes_arm_length` | Integer | 0-200 | 0 | 衣服袖長（厘米） |
| `clothes_leg_length` | Integer | 0-150 | 0 | 衣服褲長（厘米） |
| `clothes_shoulder_width` | Integer | 0-200 | 0 | 衣服肩寬（厘米） |
| `clothes_waistline` | Integer | 0-300 | 0 | 衣服腰圍（厘米） |

### 認證參數

可以通過以下兩種方式提供用戶信息：

1. **使用 JWT Token（推薦）**
   - 在 HTTP 頭部添加：`Authorization: Bearer <你的_access_token>`
   - 無需在請求體中提供 `user_uid`

2. **使用 user_uid 參數**
   - 在請求中添加 `user_uid` 參數
   - 格式：UUID 字符串

## 使用示例

### cURL 示例

```bash
# 使用 JWT Token（推薦）
curl -X POST \
  -H "Authorization: Bearer your_access_token_here" \
  -F "image_data=@/path/to/clothes_image.jpg" \
  -F "clothes_arm_length=65" \
  -F "clothes_leg_length=92" \
  -F "clothes_shoulder_width=45" \
  -F "clothes_waistline=80" \
  http://localhost:30000/picture/clothes/

# 使用 user_uid
curl -X POST \
  -F "image_data=@/path/to/clothes_image.jpg" \
  -F "user_uid=f9cac3dc-f80b-48cd-994d-1d8b873671fc" \
  -F "clothes_arm_length=65" \
  -F "clothes_leg_length=92" \
  -F "clothes_shoulder_width=45" \
  -F "clothes_waistline=80" \
  http://localhost:30000/picture/clothes/
```

### Python 示例

```python
import requests

# 準備請求參數
url = "http://localhost:30000/picture/clothes/"
headers = {
    "Authorization": "Bearer your_access_token_here"
}

files = {
    'image_data': open('/path/to/clothes_image.jpg', 'rb')
}

data = {
    'clothes_arm_length': 65,
    'clothes_leg_length': 92,
    'clothes_shoulder_width': 45,
    'clothes_waistline': 80
}

# 發送請求
response = requests.post(url, headers=headers, files=files, data=data)

# 查看響應
print(response.json())
```

### JavaScript/Front-end 示例

```javascript
// 使用 FormData API
const formData = new FormData();
formData.append('image_data', fileInput.files[0]); // <input type="file">
formData.append('clothes_arm_length', '65');
formData.append('clothes_leg_length', '92');
formData.append('clothes_shoulder_width', '45');
formData.append('clothes_waistline', '80');

// 發送請求
const response = await fetch('/picture/clothes/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});

const data = await response.json();
console.log(data);
```

## 成功響應示例

**Status Code:** 200 OK

```json
{
  "success": true,
  "message": "圖片處理和儲存成功",
  "processed_url": "http://192.168.233.128:9000/processed-images/a1b2c3d4_cleaned_garment.png",
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
    "filename": "a1b2c3d4_cleaned_garment.png",
    "file_name": "cleaned_garment.png",
    "file_format": "PNG",
    "storage": "minio",
    "bucket": "processed-images",
    "public_url": "http://192.168.233.128:9000/processed-images/a1b2c3d4_cleaned_garment.png",
    "signed_url": "http://192.168.233.128:9000/processed-images/a1b2c3d4_cleaned_garment.png?X-Amz-Algorithm=..."
  },
  "clothes_data": {
    "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
    "clothes_category": "T-shirt",
    "styles": ["Casual", "Formal", "Streetwear"],
    "colors": ["red", "blue", "green"],
    "image_url": "http://192.168.233.128:9000/processed-images/a1b2c3d4_cleaned_garment.png",
    "clothes_measurements": {
      "arm_length": 65,
      "leg_length": 92,
      "shoulder_width": 45,
      "waistline": 80
    }
  }
}
```

## 錯誤響應示例

### 缺少必填參數

**Status Code:** 400 Bad Request

```json
{
  "success": false,
  "message": "請上傳圖片檔案（欄位名稱：image_data）"
}
```

### 衣服尺寸參數格式錯誤

**Status Code:** 400 Bad Request

```json
{
  "success": false,
  "message": "衣服尺寸參數必須為整數"
}
```

### 衣服尺寸超出有效範圍

**Status Code:** 400 Bad Request

```json
{
  "success": false,
  "message": "衣服袖長必須在 0 到 200 cm 之間"
}
```

### 無效的認證

**Status Code:** 401 Unauthorized

```json
{
  "success": false,
  "message": "請提供 user_uid 或使用 JWT 認證"
}
```

### AI 後端處理失敗

**Status Code:** 422 Unprocessable Entity

```json
{
  "success": false,
  "message": "AI 處理失敗",
  "ai_status": {
    "status_code": 422,
    "message": "圖片過於模糊"
  }
}
```

### MinIO 儲存失敗

**Status Code:** 503 Service Unavailable

```json
{
  "success": false,
  "message": "儲存服務不可用",
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
    "success": false,
    "message": "MinIO 服務不可用"
  }
}
```

## 數據流程

```
前端
 ↓
 ├─ image_data (圖片文件)
 ├─ clothes_arm_length
 ├─ clothes_leg_length
 ├─ clothes_shoulder_width
 ├─ clothes_waistline
 └─ [Authorization: Bearer token 或 user_uid]
 ↓
Django 後端（驗證和提取參數）
 ↓
 ├─ 驗證衣服尺寸參數範圍
 ├─ 提取用戶信息（JWT 或 user_uid）
 └─ 準備 multipart 請求數據
 ↓
AI 後端
 ├─ 接收圖片和衣服尺寸參數
 ├─ 進行去背處理
 └─ 識別衣服類別、風格、顏色
 ↓
Django 後端（解析和儲存）
 ├─ 解析 AI 回應（JSON + 圖片）
 ├─ 上傳圖片到 MinIO
 ├─ 在數據庫中建立記錄：
 │  ├─ Clothes（包含衣服尺寸和類別）
 │  ├─ Style（風格名稱）
 │  └─ Color（顏色名稱）
 └─ 生成公開 URL
 ↓
前端（接收完整的衣服信息）
```

## 數據庫存儲

衣服尺寸數據會被存儲在 `clothes` 表的以下欄位中：

| 欄位名 | 類型 | 存儲值 |
|-------|------|--------|
| `clothes_arm_length` | INTEGER | 袖長（厘米） |
| `clothes_leg_length` | INTEGER | 褲長（厘米） |
| `clothes_shoulder_width` | INTEGER | 肩寬（厘米） |
| `clothes_waistline` | INTEGER | 腰圍（厘米） |

## 獲取衣服列表（包括尺寸信息）

使用以下 API 端點獲取用戶的衣服列表，返回結果會包含尺寸數據：

**URL:** `GET /picture/clothes/my`

**Headers:**
```
Authorization: Bearer <access_token>
```

**響應示例：**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "clothes_id": 1,
      "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
      "clothes_category": "T-shirt",
      "clothes_arm_length": 65,
      "clothes_shoulder_width": 45,
      "clothes_waistline": 80,
      "clothes_leg_length": 92,
      "clothes_image_url": "http://192.168.233.128:9000/processed-images/a1b2c3d4_cleaned_garment.png",
      "clothes_favorite": false,
      "clothes_created_time": "2026-03-27T10:30:45.123456Z",
      "clothes_updated_time": "2026-03-27T10:30:45.123456Z",
      "colors": [
        {
          "color_id": 1,
          "color_uid": "660f9511-f40c-52e5-b827-557766551111",
          "color_name": "red"
        },
        {
          "color_id": 2,
          "color_uid": "770g0622-g51d-63f6-c938-668877662222",
          "color_name": "blue"
        },
        {
          "color_id": 3,
          "color_uid": "880h1733-h62e-74g7-d049-779988773333",
          "color_name": "green"
        }
      ],
      "styles": [
        {
          "style_id": 1,
          "style_uid": "aa0i2844-i73f-85h8-e150-88aa99884444",
          "style_name": "Casual"
        },
        {
          "style_id": 2,
          "style_uid": "bb1j3955-j84g-96i9-f261-99bb00aa5555",
          "style_name": "Formal"
        },
        {
          "style_id": 3,
          "style_uid": "cc2k4a66-k95h-a7j0-g372-00cc11bb6666",
          "style_name": "Streetwear"
        }
      ]
    }
  ]
}
```

## 驗證規則

所有衣服尺寸參數都會按以下規則進行驗證：

| 參數 | 最小值 | 最大值 | 說明 |
|------|--------|--------|------|
| `clothes_arm_length` | 0 | 200 | 袖長不能為負數，不能超過 200 cm |
| `clothes_leg_length` | 0 | 150 | 褲長不能為負數，不能超過 150 cm |
| `clothes_shoulder_width` | 0 | 200 | 肩寬不能為負數，不能超過 200 cm |
| `clothes_waistline` | 0 | 300 | 腰圍不能為負數，不能超過 300 cm |

## 常見問題

### Q: 如果不提供衣服尺寸參數會怎樣？
A: 在 `clothes_measurements` 中會顯示默認值 0。API 會正常處理，數據庫中會存儲 0。

### Q: 衣服尺寸參數是否必須全部提供？
A: 不是。所有衣服尺寸參數都是可選的。您可以只提供其中的某些參數，其他參數會默認為 0。

### Q: AI 後端如何使用衣服尺寸參數？
A: AI 後端會在進行尺寸識別、衣服類別分類或虛擬試衣時考慮這些參數。具體的使用方式取決於 AI 後端的實現。

### Q: 上傳後是否可以修改衣服尺寸？
A: 可以。使用 `PUT /picture/clothes/{clothes_id}/` 端點更新衣服信息，包括尺寸參數。

### Q: 衣服尺寸數據是否會影響虛擬試衣的準確性？
A: 是的。提供準確的衣服尺寸會幫助 AI 後端進行更準確的虛擬試衣和尺寸匹配。

## 相關 API 端點

- **上傳衣服：** `POST /picture/clothes/`（本指南）
- **獲取衣服列表：** `GET /picture/clothes/my`
- **獲取衣服詳情：** `GET /picture/clothes/{clothes_id}/`
- **更新衣服信息：** `PUT /picture/clothes/{clothes_id}/`
- **刪除衣服：** `DELETE /picture/clothes/{clothes_id}/`
- **獲取最愛衣服：** `GET /picture/clothes/favorites`

## 更新日期

- 2026-03-27: 添加衣服尺寸參數支持
