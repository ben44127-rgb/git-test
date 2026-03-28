"""
Model - 模特試穿結果表

用於存儲虛擬試穿合併後的結果圖片和相關信息：
- 試穿結果圖片（衣伺 + 模特合併的照片）
- 風格分析結果
- 使用的衣伺清單
"""

import uuid
from django.db import models
from accounts.models import User as CustomUser


class Model(models.Model):
    """
    模特試穿結果表
    
    用於存儲虛擬試穿合併後的結果圖片和相關信息：
    - 試穿結果圖片（衣伺 + 模特合併的照片）
    - 風格分析結果
    - 使用的衣伺清單
    - 相關的虛擬試衣記錄參考
    """
    
    # 主鍵和唯一標識
    model_id = models.AutoField(primary_key=True, db_column='model_id')
    f_user_uid = models.CharField(
        max_length=255,
        db_column='f_user_uid',
        verbose_name='用戶UID',
        help_text='关聯的用戶唯一識別碼'
    )
    model_uid = models.CharField(
        max_length=255,
        unique=True,
        db_column='model_uid',
        default=uuid.uuid4,
        verbose_name='模特試穿UID',
        help_text='試穿記錄唯一識別碼'
    )
    
    # 試穿結果圖片
    model_picture = models.URLField(
        blank=True,
        null=True,
        db_column='model_picture',
        verbose_name='試穿結果圖',
        help_text='衣伺與模特合併後的試穿結果圖片 URL'
    )
    
    # 風格分析（JSON 陣列，如：["Japanese Style", "Elegant", "Traditional"]）
    model_style = models.JSONField(
        default=list,
        blank=True,
        db_column='model_style',
        verbose_name='風格分析',
        help_text='AI 分析的穿搭風格陣列'
    )
    
    # 使用的衣伺清單（JSON 陣列，存儲 2 件衣伺的 UID 和基本信息）
    clothes_list = models.JSONField(
        default=list,
        blank=True,
        db_column='clothes_list',
        verbose_name='衣伺清單',
        help_text='此試穿包含的 2 件衣伺信息'
    )
    
    # AI 回應數據（完整的 JSON 回應，用於調試和追踪）
    ai_response_data = models.JSONField(
        default=dict,
        blank=True,
        db_column='ai_response_data',
        verbose_name='AI 回應數據',
        help_text='AI 後端返回的完整 JSON 數據'
    )
    
    # 時間戳
    model_created_time = models.DateTimeField(
        auto_now_add=True,
        db_column='model_created_time',
        verbose_name='建立時間'
    )
    model_updated_time = models.DateTimeField(
        auto_now=True,
        db_column='model_updated_time',
        verbose_name='更新時間'
    )
    
    class Meta:
        db_table = 'model'
        verbose_name = '模特試穿結果'
        verbose_name_plural = '模特試穿結果'
        ordering = ['-model_created_time']
        indexes = [
            models.Index(fields=['model_uid']),
            models.Index(fields=['f_user_uid']),
            models.Index(fields=['model_created_time']),
        ]
    
    def __str__(self):
        return f"Model {self.model_uid} - User {self.f_user_uid}"
