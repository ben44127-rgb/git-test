# Feature 2.1 衣服上傳功能更新總結

## 更新概述

Feature 2.1（衣服上傳與 AI 處理）已擴展支持衣服尺寸參數。前端現在可以在上傳衣服圖片時同時提交衣服的尺寸信息，這些數據會：

1. **發送給 AI 後端** - 幫助 AI 進行更準確的衣服分析和虛擬試衣
2. **存儲在數據庫** - 衣服記錄會包含完整的尺寸信息
3. **返回給前端** - API 響應會包含所有尺寸數據

## 主要改動

### 1. API 請求參數擴展

**新增可選參數：**

| 參數名 | 類型 | 範圍 | 默認值 |
|-------|------|------|--------|
| `clothes_arm_length` | Integer | 0-200 | 0 |
| `clothes_leg_length` | Integer | 0-150 | 0 |
| `clothes_shoulder_width` | Integer | 0-200 | 0 |
| `clothes_waistline` | Integer | 0-300 | 0 |

**參數說明：**
- 所有參數都是可選的，默認值為 0
- 參數必須是整數，代表厘米數
- 系統會自動驗證參數是否在允許的範圍內

### 2. 數據流程

```
前端上傳
    ↓
[圖片 + 尺寸參數]
    ↓
Django 後端驗證參數
    ↓
發送給 AI 後端（包含尺寸參數）
    ↓
AI 後端處理
    ↓
Django 後端儲存（包含尺寸數據）
    ↓
返回完整的衣服信息（包括尺寸）
    ↓
前端接收
```

### 3. 數據庫變更

衣服信息現在已經包含在 `clothes` 表中（這些欄位已經存在，現在被充分利用）：

```sql
ALTER TABLE clothes
ADD COLUMN IF NOT EXISTS clothes_arm_length INTEGER DEFAULT 0;
ADD COLUMN IF NOT EXISTS clothes_leg_length INTEGER DEFAULT 0;
ADD COLUMN IF NOT EXISTS clothes_shoulder_width INTEGER DEFAULT 0;
ADD COLUMN IF NOT EXISTS clothes_waistline INTEGER DEFAULT 0;
```

### 4. API 響應更新

成功的響應現在包含 `clothes_measurements` 對象：

```json
{
  "clothes_data": {
    "clothes_uid": "550e8400-e29b-41d4-a716-446655440000",
    "clothes_category": "T-shirt",
    "styles": ["Casual", "Formal", "Streetwear"],
    "colors": ["red", "blue", "green"],
    "image_url": "http://192.168.233.128:9000/processed-images/...",
    "clothes_measurements": {
      "arm_length": 65,
      "leg_length": 92,
      "shoulder_width": 45,
      "waistline": 80
    }
  }
}
```

## 修改的文件

### picture/views.py

**修改部分：**

1. **步驟 1.6 - 提取衣服尺寸參數**
   - 從 POST 請求中提取 4 個衣服尺寸參數
   - 執行類型轉換（字符串 → 整數）
   - 驗證參數範圍（0 到最大值之間）

2. **步驟 3 - 發送給 AI 後端**
   - 修改 multipart 請求的 `data` 字典
   - 添加衣服尺寸參數和用戶 UID
   - 記錄詳細的日誌信息

3. **步驟 8 - 儲存到數據庫**
   - 修改 `Clothes.objects.create()` 調用
   - 添加 4 個衣服尺寸欄位
   - 記錄衣服尺寸信息到日誌

4. **步驟 9 - 返回響應**
   - 在 `clothes_data` 中添加 `clothes_measurements` 對象
   - 返回所有衣服尺寸信息給前端

5. **文檔更新**
   - 更新函數文檔注釋
   - 添加新參數說明
   - 更新 AI 後端請求格式說明

## 使用示例

### 使用 cURL 上傳衣服

```bash
curl -X POST \
  -H "Authorization: Bearer your_access_token" \
  -F "image_data=@clothes_image.jpg" \
  -F "clothes_arm_length=65" \
  -F "clothes_leg_length=92" \
  -F "clothes_shoulder_width=45" \
  -F "clothes_waistline=80" \
  http://localhost:30000/picture/clothes/
```

### 使用測試腳本

```bash
# 執行測試腳本，傳遞 JWT Token
./test_feature_2_1.sh "your_access_token_here"

# 或指定圖片路徑
./test_feature_2_1.sh "your_access_token_here" "/path/to/image.jpg"
```

### 使用 Python

```python
import requests

response = requests.post(
    "http://localhost:30000/picture/clothes/",
    headers={"Authorization": f"Bearer {access_token}"},
    files={"image_data": open("clothes.jpg", "rb")},
    data={
        "clothes_arm_length": 65,
        "clothes_leg_length": 92,
        "clothes_shoulder_width": 45,
        "clothes_waistline": 80
    }
)

print(response.json())
```

### 使用 JavaScript

```javascript
const formData = new FormData();
formData.append("image_data", fileInput.files[0]);
formData.append("clothes_arm_length", "65");
formData.append("clothes_leg_length", "92");
formData.append("clothes_shoulder_width", "45");
formData.append("clothes_waistline", "80");

const response = await fetch("/picture/clothes/", {
  method: "POST",
  headers: {"Authorization": `Bearer ${token}`},
  body: formData
});

const data = await response.json();
```

## 驗證規則

| 參數 | 說明 | 範圍 |
|------|------|------|
| `clothes_arm_length` | 衣服袖長 | 0-200 cm |
| `clothes_leg_length` | 衣服褲長 | 0-150 cm |
| `clothes_shoulder_width` | 衣服肩寬 | 0-200 cm |
| `clothes_waistline` | 衣服腰圍 | 0-300 cm |

**驗證流程：**
1. 嘗試將參數轉換為整數
2. 檢查是否在允許的範圍內
3. 如果驗證失敗，返回 400 Bad Request 錯誤

## 錯誤處理

### 缺少圖片參數

```json
{
  "success": false,
  "message": "請上傳圖片檔案（欄位名稱：image_data）"
}
```
**HTTP Status:** 400

### 尺寸參數格式錯誤

```json
{
  "success": false,
  "message": "衣服尺寸參數必須為整數"
}
```
**HTTP Status:** 400

### 尺寸超出範圍

```json
{
  "success": false,
  "message": "衣服袖長必須在 0 到 200 cm 之間"
}
```
**HTTP Status:** 400

## 向後兼容性

✅ **完全向後兼容** - 已有的代碼無需修改

- 所有衣服尺寸參數都是可選的
- 如果不提供尺寸參數，系統會使用默認值 0
- 現有的 API 調用會繼續正常工作

## 測試檢查清單

- [ ] 後端服務正常啟動（`docker-compose up -d`）
- [ ] 健康檢查端點正常工作（`GET /health`）
- [ ] 可以獲取訪問令牌（`POST /account/login`）
- [ ] 可以上傳圖片（不含尺寸參數）
- [ ] 可以上傳圖片並提供尺寸參數
- [ ] 返回的響應包含 `clothes_measurements` 信息
- [ ] 數據庫中的衣服記錄包含正確的尺寸值
- [ ] 衣服列表 API 返回衣服尺寸信息
- [ ] 無效的尺寸參數會被正確拒絕

## 相關文檔

- [API 使用詳細指南](./FEATURE_2_1_CLOTHES_UPLOAD_GUIDE.md)
- [測試脚本說明](../test_feature_2_1.sh)

## 後續改進建議

1. **圖片驗證**
   - 驗證上傳的圖片尺寸（寬度、高度）
   - 限制文件大小
   - 檢查圖片格式

2. **尺寸推薦**
   - 基於衣服類別的默認尺寸建議
   - AI 驅動的自動尺寸識別

3. **虛擬試衣**
   - 使用衣服尺寸數據進行更準確的虛擬試衣
   - 與用戶身體尺寸的自動匹配

4. **尺寸比較**
   - 衣服和用戶身體尺寸的對比
   - 提供尺寸是否合身的建議

## 更新日期

- **2026-03-27**: 初始版本 - 添加衣服尺寸參數支持
