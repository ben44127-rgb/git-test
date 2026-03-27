"""
Outfit/Combine Models
穿搭組合和虛擬試衣管理的資料模型

主要包含：
1. Outfit - 穿搭組合表（最多包含 2 件衣服）
2. OutfitClothes - 穿搭包含的衣服（最多 2 件）
3. VirtualTryOn - 虛擬試衣記錄表
4. OutfitFavorite - 用戶收藏的穿搭
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Clothes, User as CustomUser


class Outfit(models.Model):
    """
    穿搭組合主表
    
    用於記錄使用者建立的穿搭組合，包含：
    - 基本信息（名稱、描述）
    - 季節和風格分類
    - 建立者和時間戳
    - 是否為草稿
    """
    
    # 主鍵和唯一標識
    outfit_id = models.AutoField(primary_key=True)
    outfit_uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # 穿搭基本信息
    outfit_name = models.CharField(
        max_length=100,
        verbose_name='穿搭名稱',
        help_text='使用者自訂的穿搭名稱'
    )
    outfit_description = models.TextField(
        blank=True,
        null=True,
        verbose_name='穿搭描述',
        help_text='穿搭的詳細說明'
    )
    
    # 關聯信息
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='outfits',
        verbose_name='建立者',
        help_text='建立此穿搭的用戶'
    )
    
    # 虛擬試衣來源（可選：若由虛擬試衣生成，則記錄其來源）
    virtual_try_on = models.ForeignKey(
        'VirtualTryOn',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='saved_outfits',
        verbose_name='虛擬試衣來源',
        help_text='此穿搭來自哪個虛擬試衣結果（若為空則是手動建立）'
    )
    
    # 預覽圖
    preview_image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='穿搭預覽圖 URL',
        help_text='穿搭組合的預覽圖片（由虛擬試衣生成）'
    )
    
    # 狀態
    is_draft = models.BooleanField(
        default=False,
        verbose_name='是否為草稿',
        help_text='True：草稿；False：已發佈'
    )
    
    # 時間戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='建立時間'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新時間'
    )
    
    class Meta:
        db_table = 'outfit'
        verbose_name = '穿搭組合'
        verbose_name_plural = '穿搭組合'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['outfit_uid']),
            models.Index(fields=['created_by']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.outfit_name} (by {self.created_by.user_name})"


class OutfitClothes(models.Model):
    """
    穿搭-衣服關聯表
    
    用於記錄一個穿搭包含的所有衣服
    一對多關係：一個穿搭可以有多件衣服
    """
    
    id = models.AutoField(primary_key=True)
    outfit = models.ForeignKey(
        Outfit,
        on_delete=models.CASCADE,
        related_name='outfit_clothes',
        verbose_name='穿搭'
    )
    clothes = models.ForeignKey(
        Clothes,
        on_delete=models.CASCADE,
        related_name='outfit_references',
        verbose_name='衣服',
        help_text='此穿搭包含的衣服'
    )
    
    # 順序（用於展示衣服的順序）
    position_order = models.PositiveIntegerField(
        default=0,
        verbose_name='順序',
        help_text='衣服在穿搭中的顯示順序'
    )
    
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='添加時間'
    )
    
    class Meta:
        db_table = 'outfit_clothes'
        verbose_name = '穿搭衣服'
        verbose_name_plural = '穿搭衣服'
        unique_together = [['outfit', 'clothes']]
        ordering = ['position_order']
        indexes = [
            models.Index(fields=['outfit']),
            models.Index(fields=['clothes']),
        ]
    
    def __str__(self):
        return f"{self.outfit.outfit_name} - {self.clothes.clothes_category}"


class VirtualTryOn(models.Model):
    """
    虛擬試衣記錄表
    
    用於記錄用戶進行虛擬試衣的流程和結果：
    1. 用戶選擇模特照片和衣服組合
    2. 傳送至 AI 後端進行合成
    3. AI 返回虛擬試衣結果圖片
    4. 用戶確認後保存為 Outfit，或直接刪除
    """
    
    # 主鍵和唯一標識
    try_on_id = models.AutoField(primary_key=True)
    try_on_uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # 關聯用戶
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='virtual_try_ons',
        verbose_name='用戶',
        help_text='進行虛擬試衣的用戶'
    )
    
    # 選擇的穿搭（一開始是從某個 Outfit 或臨時選擇）
    outfit = models.ForeignKey(
        Outfit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='try_ons',
        verbose_name='參考穿搭',
        help_text='用戶選擇的參考穿搭（可選）'
    )
    
    # 虛擬試衣流程狀態
    STATUS_CHOICES = [
        ('pending', '待處理'),          # 剛提交，等待 AI 處理
        ('processing', '處理中'),        # 正在 AI 後端處理
        ('completed', '已完成'),         # AI 處理完成
        ('accepted', '已保存'),          # 用戶確認並保存為 Outfit
        ('rejected', '已拒絕'),          # 用戶不滿意，拒絕保存
        ('error', '處理失敗'),           # AI 處理失敗
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='狀態',
        help_text='虛擬試衣的處理狀態'
    )
    
    # 使用的模特照片（可能來自 Photo 表或用戶身體數據）
    user_photo = models.ForeignKey(
        'picture.Photo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='virtual_try_ons',
        verbose_name='模特照片',
        help_text='虛擬試衣使用的模特照片'
    )
    
    # 使用的衣服列表（JSON 陣列存儲多件衣服的 UID）
    clothes_list = models.JSONField(
        default=list,
        verbose_name='衣服列表',
        help_text='虛擬試衣包含的衣服 UID 陣列'
    )
    
    # AI 後端返回的結果
    result_image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='虛擬試衣結果圖',
        help_text='AI 後端返回的虛擬試衣合成圖片 URL'
    )
    
    result_file_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='結果文件名',
        help_text='AI 返回的結果文件名稱'
    )
    
    # AI 處理的詳細信息
    ai_response_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='AI 回應數據',
        help_text='AI 後端返回的完整 JSON 數據'
    )
    
    ai_error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='錯誤信息',
        help_text='如果 AI 處理失敗，記錄錯誤詳情'
    )
    
    # 時間戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='建立時間'
    )
    ai_processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='AI 完成時間',
        help_text='AI 處理完成的時間'
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='確認時間',
        help_text='用戶確認保存的時間'
    )
    
    class Meta:
        db_table = 'virtual_try_on'
        verbose_name = '虛擬試衣記錄'
        verbose_name_plural = '虛擬試衣記錄'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['try_on_uid']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"VirtualTryOn {self.try_on_uid} - {self.user.user_name} ({self.status})"


class OutfitFavorite(models.Model):
    """
    穿搭收藏表
    
    用於記錄用戶收藏（點讚）的穿搭
    """
    
    id = models.AutoField(primary_key=True)
    
    outfit = models.ForeignKey(
        Outfit,
        on_delete=models.CASCADE,
        related_name='liked_by',
        verbose_name='穿搭',
        help_text='被收藏的穿搭'
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorite_outfits',
        verbose_name='用戶',
        help_text='收藏此穿搭的用戶'
    )
    
    liked_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='收藏時間'
    )
    
    class Meta:
        db_table = 'outfit_favorite'
        verbose_name = '穿搭收藏'
        verbose_name_plural = '穿搭收藏'
        unique_together = [['outfit', 'user']]
        indexes = [
            models.Index(fields=['outfit']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.user_name} liked {self.outfit.outfit_name}"
