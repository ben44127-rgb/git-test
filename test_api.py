#!/usr/bin/env python3
"""
API 测试脚本
用于测试图片上传和处理功能

测试流程：
1. 创建一个测试图片
2. 上传到 API 端点
3. 查看返回结果
"""

import requests
from PIL import Image
import io
import json

# API 端点
API_URL = "http://localhost:30000/api/upload-image"

# 创建测试图片
print("📷 创建测试图片...")
img = Image.new('RGB', (200, 200), color='red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# 准备请求数据
print("📤 准备上传数据...")
files = {
    'image_data': ('test_image.png', img_bytes, 'image/png')
}
data = {
    'filename': 'test_image.png'
}

print(f"🚀 发送请求到: {API_URL}")
print(f"   文件名: test_image.png")
print(f"   文件大小: {len(img_bytes.getvalue())} bytes")

try:
    # 发送请求
    response = requests.post(API_URL, files=files, data=data, timeout=120)
    
    print(f"\n✅ 收到响应")
    print(f"   状态码: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")
    
    # 解析响应
    if response.status_code == 200:
        result = response.json()
        print(f"\n📊 响应内容:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ 请求失败")
        print(f"   错误内容: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ 无法连接到 API 服务")
    print("   请确认服务是否启动: python3 manage.py runserver 0.0.0.0:30000")
except requests.exceptions.Timeout:
    print("\n❌ 请求超时")
except Exception as e:
    print(f"\n❌ 发生错误: {e}")
