#!/bin/bash

# Feature 2.1 衣服上傳測試腳本
# 使用此腳本測試新的衣服尺寸參數功能

echo "==========================================="
echo "Feature 2.1 衣服上傳與尺寸參數測試"
echo "==========================================="
echo ""

# 配置
API_URL="http://localhost:30000/picture/clothes/"
JWT_TOKEN="${1:-}"  # 從命令行參數讀取 JWT Token

# 檢查是否提供了 JWT Token
if [ -z "$JWT_TOKEN" ]; then
    echo "❌ 需要提供 JWT Token 作為參數"
    echo ""
    echo "使用方法："
    echo "  ./test_feature_2_1.sh <JWT_TOKEN> [IMAGE_PATH]"
    echo ""
    echo "示例："
    echo "  ./test_feature_2_1.sh 'eyJhbGciOiJIUzI1NiIs...' './test_image.jpg'"
    echo ""
    echo "或者使用測試圖片："
    echo "  ./test_feature_2_1.sh 'eyJhbGciOiJIUzI1NiIs...'"
    exit 1
fi

# 圖片路徑（可選，默認使用測試圖片）
IMAGE_PATH="${2:-./test_image.jpg}"

# 如果沒有提供圖片，嘗試使用系統中存在的圖片
if [ ! -f "$IMAGE_PATH" ]; then
    # 嘗試找到系統中的任何 JPEG 或 PNG 圖片
    for dir in ~/Pictures ~/Downloads /tmp; do
        if [ -d "$dir" ]; then
            found_image=$(find "$dir" -maxdepth 1 \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) | head -1)
            if [ ! -z "$found_image" ]; then
                IMAGE_PATH="$found_image"
                break
            fi
        fi
    done
fi

# 如果仍然找不到圖片，建議用戶
if [ ! -f "$IMAGE_PATH" ]; then
    echo "❌ 找不到圖片文件：$IMAGE_PATH"
    echo ""
    echo "請確保："
    echo "  1. 圖片文件存在"
    echo "  2. 您有訪問該文件的權限"
    echo "  3. 圖片格式為 JPG、JPEG 或 PNG"
    exit 1
fi

echo "📋 測試配置："
echo "  API 端點: $API_URL"
echo "  JWT Token: ${JWT_TOKEN:0:50}..."
echo "  圖片路徑: $IMAGE_PATH"
echo ""

# 建立衣服尺寸參數
# 例如：一件 T 恤的尺寸
CLOTHES_ARM_LENGTH="65"      # 袖長 65 cm
CLOTHES_LEG_LENGTH="92"      # 褲長 92 cm（T 恤通常不考慮褲長）
CLOTHES_SHOULDER_WIDTH="45"  # 肩寬 45 cm
CLOTHES_WAISTLINE="80"       # 腰圍 80 cm

echo "👕 衣服尺寸參數："
echo "  袖長 (arm_length): $CLOTHES_ARM_LENGTH cm"
echo "  褲長 (leg_length): $CLOTHES_LEG_LENGTH cm"
echo "  肩寬 (shoulder_width): $CLOTHES_SHOULDER_WIDTH cm"
echo "  腰圍 (waistline): $CLOTHES_WAISTLINE cm"
echo ""

# 發送請求
echo "📤 發送請求到 API..."
echo ""

response=$(curl -X POST \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "image_data=@$IMAGE_PATH" \
  -F "clothes_arm_length=$CLOTHES_ARM_LENGTH" \
  -F "clothes_leg_length=$CLOTHES_LEG_LENGTH" \
  -F "clothes_shoulder_width=$CLOTHES_SHOULDER_WIDTH" \
  -F "clothes_waistline=$CLOTHES_WAISTLINE" \
  "$API_URL" \
  2>/dev/null)

# 檢查回應
if [ -z "$response" ]; then
    echo "❌ API 沒有返回回應"
    echo "   請檢查："
    echo "   1. API 服務是否正在運行"
    echo "   2. JWT Token 是否有效"
    echo "   3. 網絡連接是否正常"
    exit 1
fi

# 檢查是否成功
if echo "$response" | grep -q '"success":\s*true'; then
    echo "✅ 請求成功！"
    echo ""
    echo "📊 API 回應："
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
    
    # 提取衣服 UID
    clothes_uid=$(echo "$response" | grep -o '"clothes_uid":\s*"[^"]*"' | cut -d'"' -f4)
    if [ ! -z "$clothes_uid" ]; then
        echo "✨ 衣服已保存！"
        echo "   衣服 UID: $clothes_uid"
        echo ""
        echo "🔗 後續操作："
        echo "   查看衣服詳情："
        echo "     curl -H 'Authorization: Bearer $JWT_TOKEN' http://localhost:30000/picture/clothes/<clothes_id>/"
        echo ""
        echo "   查看用戶的所有衣服："
        echo "     curl -H 'Authorization: Bearer $JWT_TOKEN' http://localhost:30000/picture/clothes/my"
        echo ""
    fi
else
    echo "❌ API 返回錯誤"
    echo ""
    echo "📊 API 回應："
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
    
    # 嘗試提取錯誤信息
    error_msg=$(echo "$response" | grep -o '"message":\s*"[^"]*"' | cut -d'"' -f4 | head -1)
    if [ ! -z "$error_msg" ]; then
        echo "💡 錯誤信息: $error_msg"
    fi
fi

echo ""
echo "==========================================="
