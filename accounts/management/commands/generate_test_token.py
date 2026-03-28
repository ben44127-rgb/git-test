"""
生成測試用 JWT Token 的 Django Management Command

使用方式：
    python manage.py generate_test_token                    # 為 admin 用戶生成 365 天有效期的 token
    python manage.py generate_test_token --username john    # 為特定用戶生成 token
    python manage.py generate_test_token --days 730         # 自定義有效期（730 天）
    python manage.py generate_test_token --create           # 如果用戶不存在，自動創建用戶

示例：
    python manage.py generate_test_token --username testuser --days 365 --create
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = '生成長期有效的 JWT Token 用於測試'

    def add_arguments(self, parser):
        # 用戶名
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='用戶名 (預認: admin)'
        )
        
        # token 有效天數
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Token 有效天數 (預認: 365 天，約 1 年)'
        )
        
        # 是否自動創建用戶
        parser.add_argument(
            '--create',
            action='store_true',
            help='如果用戶不存在，自動創建用戶'
        )

    def handle(self, *args, **options):
        username = options['username']
        days = options['days']
        auto_create = options['create']
        
        self.stdout.write(f"🔍 查找用戶: {username}")
        
        try:
            user = User.objects.get(user_name=username)
            self.stdout.write(self.style.SUCCESS(f"✅ 找到用戶: {username}"))
        except User.DoesNotExist:
            if auto_create:
                # 自動創建用戶
                self.stdout.write(f"⚠️  用戶 {username} 不存在，正在創建...")
                try:
                    user = User.objects.create_user(
                        user_name=username,
                        email=f"{username}@test.local",
                        password='testpass123'
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ 成功創建用戶: {username}"))
                except Exception as e:
                    raise CommandError(f"❌ 創建用戶失敗: {str(e)}")
            else:
                raise CommandError(
                    f"❌ 用戶 {username} 不存在。\n"
                    f"   請使用 --create 標誌自動創建，或指定現有用戶。\n"
                    f"   可用用戶:\n"
                    f"   {', '.join([u.user_name for u in User.objects.all()])}"
                )
        
        # 生成 Token
        self.stdout.write(f"🔑 正在為用戶 {username} 生成 Token...")
        
        try:
            # 創建 Refresh Token
            refresh = RefreshToken.for_user(user)
            
            # 修改 Token 過期時間為指定的天數
            # 修改 access token 的過期時間
            refresh.access_token.set_exp(
                lifetime=timedelta(days=days)
            )
            
            # 修改 refresh token 的過期時間（可選）
            refresh.set_exp(
                lifetime=timedelta(days=days * 2)  # Refresh token 有效期更長
            )
            
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # 計算過期時間
            exp_time = timezone.now() + timedelta(days=days)
            
            self.stdout.write("\n" + "="*80)
            self.stdout.write(self.style.SUCCESS("✅ Token 生成成功！"))
            self.stdout.write("="*80)
            
            self.stdout.write(f"\n📋 Token 信息:")
            self.stdout.write(f"   用戶名: {username}")
            self.stdout.write(f"   有效期: {days} 天")
            self.stdout.write(f"   過期時間: {exp_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC)")
            
            self.stdout.write(f"\n🎫 Access Token (用於 API 請求):")
            self.stdout.write(f"\n{access_token}\n")
            
            self.stdout.write(f"🔄 Refresh Token (用於更新 Access Token):")
            self.stdout.write(f"\n{refresh_token}\n")
            
            self.stdout.write("="*80)
            
            self.stdout.write(f"\n📌 使用方法:")
            self.stdout.write(f"   在 HTTP 請求的 Authorization header 中使用:")
            self.stdout.write(f"   Authorization: Bearer {access_token[:50]}...")
            
            self.stdout.write(f"\n📝 示例 (curl):")
            example_cmd = f'curl -H "Authorization: Bearer {access_token[:30]}..." http://localhost:8000/api/v1/path'
            self.stdout.write(f"   {example_cmd}")
            
            self.stdout.write(f"\n⚠️  注意:")
            self.stdout.write(f"   • 這個 Token 用於開發和測試")
            self.stdout.write(f"   • 不要在生產環境中使用")
            self.stdout.write(f"   • 保管好 Token，不要洩露")
            self.stdout.write(f"   • Token 有效期為 {days} 天")
            
            self.stdout.write("\n" + "="*80 + "\n")
            
        except Exception as e:
            raise CommandError(f"❌ 生成 Token 失敗: {str(e)}")
