#!/usr/bin/env python3
"""
環境變數檢查腳本
用於驗證 .env 檔案是否正確載入
"""

import os
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 載入環境變數
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ 成功載入 .env 檔案: {env_path}")
    else:
        print(f"⚠️  .env 檔案不存在: {env_path}")
except ImportError:
    print("❌ 未安裝 python-dotenv")
    sys.exit(1)

print("\n" + "="*60)
print("環境變數檢查結果")
print("="*60 + "\n")

# 檢查的環境變數列表
env_vars = {
    'Django 配置': [
        ('DEBUG', 'False'),
        ('DJANGO_SECRET_KEY', 'change-this-secret-key-in-production-please-use-random-string'),
    ],
    'MinIO 配置': [
        ('MINIO_ENDPOINT', 'localhost:9000'),
        ('MINIO_ACCESS_KEY', 'minioadmin'),
        ('MINIO_SECRET_KEY', 'minioadmin'),
        ('MINIO_BUCKET_NAME', 'processed-images'),
        ('MINIO_SECURE', 'False'),
    ],
    'AI 後端配置': [
        ('AI_BACKEND_URL', 'http://192.168.233.128:8002/api/remove_bg'),
    ],
    '其他配置': [
        ('MAX_UPLOAD_SIZE', '10485760'),
        ('CORS_ALLOW_ALL_ORIGINS', 'True'),
    ]
}

all_ok = True

for category, vars_list in env_vars.items():
    print(f"📋 {category}")
    print("-" * 60)
    
    for var_name, default_value in vars_list:
        value = os.getenv(var_name)
        
        if value is None:
            print(f"  ❌ {var_name:25} = 未設定")
            all_ok = False
        elif value == default_value:
            print(f"  ⚠️  {var_name:25} = {value[:50]} (使用預設值)")
        else:
            # 隱藏敏感資訊
            if 'SECRET' in var_name or 'PASSWORD' in var_name:
                display_value = value[:10] + '...' if len(value) > 10 else value
            else:
                display_value = value[:50]
            print(f"  ✅ {var_name:25} = {display_value}")
    
    print()

print("="*60)

if all_ok:
    print("✅ 所有環境變數都已正確設定！")
else:
    print("⚠️  部分環境變數未設定，將使用預設值")

print("="*60)

# 測試 Django settings 是否能正確載入
print("\n🔧 測試 Django Settings 載入...")
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()
    from django.conf import settings
    
    print(f"  ✅ DEBUG = {settings.DEBUG}")
    print(f"  ✅ MINIO_ENDPOINT = {settings.MINIO_ENDPOINT}")
    print(f"  ✅ AI_BACKEND_URL = {settings.AI_BACKEND_URL}")
    print("\n✅ Django Settings 載入成功！")
except Exception as e:
    print(f"\n❌ Django Settings 載入失敗: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✨ 環境變數檢查完成")
print("="*60)
