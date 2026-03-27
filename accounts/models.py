from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    """自定義用戶管理器"""
    
    def create_user(self, user_name, user_email, user_password=None, **extra_fields):
        """創建普通用戶"""
        if not user_name:
            raise ValueError('用戶名不能為空')
        if not user_email:
            raise ValueError('郵箱不能為空')
        
        email = self.normalize_email(user_email)
        user = self.model(
            user_name=user_name,
            user_email=email,
            user_uid=str(uuid.uuid4()),
            **extra_fields
        )
        user.set_password(user_password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, user_name, user_email, user_password=None, **extra_fields):
        """創建超級用戶"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(user_name, user_email, user_password, **extra_fields)


class User(AbstractBaseUser):
    """
    用戶表模型
    對應圖片中的 user 表結構
    """
    user_id = models.AutoField(primary_key=True, db_column='user_id')
    user_uid = models.CharField(max_length=255, unique=True, db_column='user_uid', default=uuid.uuid4)
    user_name = models.CharField(max_length=150, unique=True, db_column='user_name')
    user_email = models.EmailField(unique=True, db_column='user_email')
    user_password = models.CharField(max_length=255, db_column='user_password')
    user_weight = models.IntegerField(default=0, db_column='user_weight')
    user_height = models.IntegerField(default=0, db_column='user_height')
    user_arm_length = models.IntegerField(default=0, db_column='user_arm_length', help_text='手臂長度(cm)')
    user_shoulder_width = models.IntegerField(default=0, db_column='user_shoulder_width', help_text='肩寬(cm)')
    user_waistline = models.IntegerField(default=0, db_column='user_waistline', help_text='腰圍(cm)')
    user_leg_length = models.IntegerField(default=0, db_column='user_leg_length', help_text='腿長(cm)')
    user_image_url = models.CharField(max_length=500, default='', db_column='user_image_url')
    user_created_time = models.DateTimeField(auto_now_add=True, db_column='user_created_time')
    user_updated_time = models.DateTimeField(auto_now=True, db_column='user_updated_time')
    
    # Django 必需的額外字段
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Django 權限系統需要的字段（不存儲到數據庫表中）
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
        db_table='user_groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
        db_table='user_permissions'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['user_email']
    
    class Meta:
        db_table = 'user'
        verbose_name = '用戶'
        verbose_name_plural = '用戶'
    
    def __str__(self):
        return self.user_name
    
    def has_perm(self, perm, obj=None):
        """用戶是否擁有特定權限"""
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        """用戶是否有訪問指定應用的權限"""
        return self.is_superuser


class Clothes(models.Model):
    """
    衣服表模型
    對應圖片中的 clothes 表結構
    """
    clothes_id = models.AutoField(primary_key=True, db_column='clothes_id')
    f_user_uid = models.CharField(max_length=255, db_column='f_user_uid')
    clothes_uid = models.CharField(max_length=255, unique=True, db_column='clothes_uid', default=uuid.uuid4)
    clothes_category = models.CharField(max_length=100, db_column='clothes_category')
    clothes_arm_length = models.IntegerField(default=0, db_column='clothes_arm_length', help_text='袖長(cm)')
    clothes_shoulder_width = models.IntegerField(default=0, db_column='clothes_shoulder_width', help_text='肩寬(cm)')
    clothes_waistline = models.IntegerField(default=0, db_column='clothes_waistline', help_text='腰圍(cm)')
    clothes_leg_length = models.IntegerField(default=0, db_column='clothes_leg_length', help_text='褲長(cm)')
    clothes_image_url = models.CharField(max_length=500, db_column='clothes_image_url')
    clothes_favorite = models.BooleanField(default=False, db_column='clothes_favorite')
    clothes_created_time = models.DateTimeField(auto_now_add=True, db_column='clothes_created_time')
    clothes_updated_time = models.DateTimeField(auto_now=True, db_column='clothes_updated_time')
    
    class Meta:
        db_table = 'clothes'
        verbose_name = '衣服'
        verbose_name_plural = '衣服'
    
    def __str__(self):
        return f"{self.clothes_category} - {self.clothes_uid}"


class Style(models.Model):
    """
    風格表模型
    對應圖片中的 style 表結構
    一件衣服可對應多個風格（多筆 style 連接同一個 clothes_uid）
    """
    style_id = models.AutoField(primary_key=True, db_column='style_id')
    f_clothes_uid = models.CharField(max_length=255, db_column='f_clothes_uid')
    style_uid = models.CharField(max_length=255, unique=True, db_column='style_uid', default=uuid.uuid4)
    style_name = models.CharField(max_length=100, db_column='style_name')

    class Meta:
        db_table = 'style'
        verbose_name = '風格'
        verbose_name_plural = '風格'

    def __str__(self):
        return f"{self.style_name} - {self.style_uid}"


class Color(models.Model):
    """
    顏色表模型
    對應圖片中的 color 表結構
    一件衣服可對應多個顏色
    """
    color_id = models.AutoField(primary_key=True, db_column='color_id')
    f_clothes_uid = models.CharField(max_length=255, db_column='f_clothes_uid')
    color_uid = models.CharField(max_length=255, unique=True, db_column='color_uid', default=uuid.uuid4)
    color_name = models.CharField(max_length=100, db_column='color_name')

    class Meta:
        db_table = 'color'
        verbose_name = '顏色'
        verbose_name_plural = '顏色'

    def __str__(self):
        return f"{self.color_name} - {self.color_uid}"


class Photo(models.Model):
    """
    用戶個人照片表模型
    存儲用戶上傳的個人照片（全身照、頭像等）
    支持多張照片，自動關聯到用戶
    """
    photo_id = models.AutoField(primary_key=True, db_column='photo_id')
    photo_uid = models.CharField(max_length=255, unique=True, db_column='photo_uid', default=uuid.uuid4)
    f_user_uid = models.CharField(max_length=255, db_column='f_user_uid')  # 外鍵關聯用戶
    photo_url = models.CharField(max_length=500, db_column='photo_url')  # MinIO 圖片 URL
    photo_filename = models.CharField(max_length=255, db_column='photo_filename')  # 原始檔名
    photo_file_size = models.IntegerField(default=0, db_column='photo_file_size', help_text='檔案大小(bytes)')
    photo_content_type = models.CharField(max_length=50, default='image/jpeg', db_column='photo_content_type')
    photo_uploaded_time = models.DateTimeField(auto_now_add=True, db_column='photo_uploaded_time')
    photo_updated_time = models.DateTimeField(auto_now=True, db_column='photo_updated_time')
    
    class Meta:
        db_table = 'photo'
        verbose_name = '用戶照片'
        verbose_name_plural = '用戶照片'
    
    def __str__(self):
        return f"Photo {self.photo_id} - {self.f_user_uid}"
