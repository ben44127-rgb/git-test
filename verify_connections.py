#!/usr/bin/env python3
"""
連接驗證腳本
驗證三人協作環境中所有服務的連接狀態

使用方法：
  python verify_connections.py
  python verify_connections.py --detailed
  python verify_connections.py --verbose
"""

import os
import sys
import json
import subprocess
from urllib.parse import urlparse

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 載入環境變數
import django
django.setup()

from django.conf import settings
import requests
from minio import Minio
from django.db import connection
from django.test.utils import get_unique_databases_and_mirrors


class ConnectionVerifier:
    def __init__(self, verbose=False, detailed=False):
        self.verbose = verbose
        self.detailed = detailed
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def log(self, service, status, message, details=""):
        """記錄驗證結果"""
        symbol = "✅" if status else "❌"
        
        if status:
            self.passed += 1
        else:
            self.failed += 1
        
        print(f"{symbol} {service:20s} {message}")
        
        if details and (self.verbose or self.detailed):
            print(f"   └─ {details}")
        
        self.results.append({
            'service': service,
            'status': status,
            'message': message,
            'details': details
        })
    
    def verify_django(self):
        """驗證 Django 設置"""
        print("\n【1】Django 配置")
        print("─" * 60)
        
        try:
            print(f"  • DEBUG：{settings.DEBUG}")
            print(f"  • ALLOWED_HOSTS：{settings.ALLOWED_HOSTS}")
            self.log("Django", True, "設置加載成功")
        except Exception as e:
            self.log("Django", False, "設置加載失敗", str(e))
    
    def verify_frontend(self):
        """驗證前端配置"""
        print("\n【2】前端配置")
        print("─" * 60)
        
        frontend_url = settings.FRONTEND_URL
        print(f"  • FRONTEND_URL：{frontend_url}")
        
        # 不實際連接前端（可能還沒啟動），只檢查配置
        if frontend_url and frontend_url.startswith('http'):
            self.log("Frontend URL", True, f"配置正確：{frontend_url}")
        else:
            self.log("Frontend URL", False, f"配置不正確：{frontend_url}")
    
    def verify_cors(self):
        """驗證 CORS 配置"""
        print("\n【3】CORS 配置")
        print("─" * 60)
        
        print(f"  • CORS_ALLOW_ALL：{settings.CORS_ALLOW_ALL_ORIGINS}")
        print(f"  • CORS_ORIGINS：{settings.CORS_ALLOWED_ORIGINS}")
        
        if settings.CORS_ALLOW_ALL_ORIGINS:
            self.log("CORS", True, "允許所有來源（開發模式）")
        elif settings.CORS_ALLOWED_ORIGINS:
            self.log("CORS", True, f"白名單配置：{len(settings.CORS_ALLOWED_ORIGINS)} 個來源")
        else:
            self.log("CORS", False, "未配置 CORS")
    
    def verify_database(self):
        """驗證數據庫連接"""
        print("\n【4】PostgreSQL 數據庫")
        print("─" * 60)
        
        db_config = settings.DATABASES['default']
        print(f"  • HOST：{db_config['HOST']}")
        print(f"  • PORT：{db_config['PORT']}")
        print(f"  • NAME：{db_config['NAME']}")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.log("PostgreSQL", True, "連接成功")
        except Exception as e:
            self.log("PostgreSQL", False, "連接失敗", str(e)[:50])
    
    def verify_minio(self):
        """驗證 MinIO 連接"""
        print("\n【5】MinIO 物件存儲")
        print("─" * 60)
        
        endpoint = settings.MINIO_ENDPOINT
        external_url = settings.MINIO_EXTERNAL_URL
        print(f"  • ENDPOINT：{endpoint}")
        print(f"  • EXTERNAL_URL：{external_url}")
        
        try:
            client = Minio(
                endpoint,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            
            # 列出 buckets
            buckets = client.list_buckets()
            bucket_names = [b.name for b in buckets]
            self.log("MinIO", True, "連接成功", f"Buckets：{', '.join(bucket_names)}")
            
            # 檢查目標 bucket
            if settings.MINIO_BUCKET_NAME in bucket_names:
                self.log("MinIO Bucket", True, f"Bucket '{settings.MINIO_BUCKET_NAME}' 存在")
            else:
                self.log("MinIO Bucket", False, f"Bucket '{settings.MINIO_BUCKET_NAME}' 不存在")
        
        except Exception as e:
            self.log("MinIO", False, "連接失敗", str(e)[:50])
    
    def verify_ai_backend(self):
        """驗證 AI 後端連接"""
        print("\n【6】AI 後端")
        print("─" * 60)
        
        ai_url = settings.AI_BACKEND_URL
        health_url = ai_url.replace(
            settings.AI_VIRTUAL_TRY_ON_ENDPOINT, 
            '/health'
        )
        
        print(f"  • AI_BACKEND_URL：{ai_url}")
        print(f"  • ENDPOINT：{settings.AI_VIRTUAL_TRY_ON_ENDPOINT}")
        print(f"  • HEALTH_CHECK：{health_url}")
        
        try:
            response = requests.get(health_url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                self.log(
                    "AI Backend",
                    True,
                    "連接成功",
                    f"狀態：{data.get('status', 'unknown')}"
                )
            else:
                self.log("AI Backend", False, f"狀態碼 {response.status_code}", "")
        
        except requests.exceptions.ConnectionError:
            self.log("AI Backend", False, "連接被拒絕", health_url)
        except requests.exceptions.Timeout:
            self.log("AI Backend", False, "連接超時", "（AI 服務未啟動？）")
        except Exception as e:
            self.log("AI Backend", False, "驗證失敗", str(e)[:50])
    
    def verify_minio_container(self):
        """驗證 MinIO 容器端點"""
        print("\n【7】MinIO 容器內部訪問")
        print("─" * 60)
        
        if hasattr(settings, 'MINIO_CONTAINER_ENDPOINT'):
            container_endpoint = settings.MINIO_CONTAINER_ENDPOINT
            print(f"  • MINIO_CONTAINER_ENDPOINT：{container_endpoint}")
            
            if container_endpoint == "minio:9000":
                self.log(
                    "MinIO Container",
                    True,
                    "配置正確（Docker 環境）"
                )
            else:
                self.log(
                    "MinIO Container",
                    False,
                    f"非預期的容器端點：{container_endpoint}"
                )
        else:
            self.log("MinIO Container", True, "未配置（本地環境）")
    
    def print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 60)
        print("【驗證摘要】")
        print("=" * 60)
        print(f"✅ 通過：{self.passed}")
        print(f"❌ 失敗：{self.failed}")
        print(f"📊 總計：{self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n🎉 所有連接正常！")
            return True
        else:
            print("\n⚠️  有服務連接失敗，請檢查上方詳情")
            return False
    
    def run(self):
        """運行所有驗證"""
        print("╔═════════════════════════════════════════════════════════╗")
        print("║         三人協作 - 連接驗證工具                        ║")
        print("╚═════════════════════════════════════════════════════════╝")
        
        self.verify_django()
        self.verify_frontend()
        self.verify_cors()
        self.verify_database()
        self.verify_minio()
        self.verify_minio_container()
        self.verify_ai_backend()
        
        success = self.print_summary()
        
        # 打印快速修復建議
        if self.failed > 0:
            print("\n【快速修復】")
            print("─" * 60)
            if not self._check_db_connection():
                print("• PostgreSQL：docker-compose up postgres")
            if not self._check_minio_connection():
                print("• MinIO：docker-compose up minio")
            if not self._check_ai_connection():
                print("• AI 後端：python test_file/mock_ai_backend.py --port 8002")
        
        return 0 if success else 1
    
    def _check_db_connection(self):
        """快速檢查數據庫"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except:
            return False
    
    def _check_minio_connection(self):
        """快速檢查 MinIO"""
        try:
            client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            client.list_buckets()
            return True
        except:
            return False
    
    def _check_ai_connection(self):
        """快速檢查 AI 後端"""
        try:
            health_url = settings.AI_BACKEND_URL.replace(
                settings.AI_VIRTUAL_TRY_ON_ENDPOINT,
                '/health'
            )
            response = requests.get(health_url, timeout=2)
            return response.status_code == 200
        except:
            return False


if __name__ == '__main__':
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    detailed = '--detailed' in sys.argv or '-d' in sys.argv
    
    verifier = ConnectionVerifier(verbose=verbose, detailed=detailed)
    exit_code = verifier.run()
    sys.exit(exit_code)
