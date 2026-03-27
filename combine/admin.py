"""
Django Admin Configuration for Combine App
穿搭組合和虛擬試衣管理的管理後台配置
"""

from django.contrib import admin
from .models import (
    Outfit,
    OutfitClothes,
    VirtualTryOn,
    OutfitFavorite,
)


@admin.register(Outfit)
class OutfitAdmin(admin.ModelAdmin):
    """穿搭組合管理"""
    
    list_display = (
        'outfit_name',
        'created_by',
        'is_draft',
        'created_at',
    )
    
    list_filter = (
        'is_draft',
        'created_at',
    )
    
    search_fields = (
        'outfit_name',
        'outfit_description',
        'created_by__user_name',
    )
    
    readonly_fields = (
        'outfit_uid',
        'created_at',
        'updated_at',
    )
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'outfit_uid',
                'outfit_name',
                'outfit_description',
                'preview_image_url',
            )
        }),
        ('分類信息', {
            'fields': (
                'season',
                'style',
            )
        }),
        ('創建者', {
            'fields': (
                'created_by',
            )
        }),
        ('狀態', {
            'fields': (
                'is_draft',
                'like_count',
                'avg_rating',
            )
        }),
        ('時間戳', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(OutfitClothes)
class OutfitClothesAdmin(admin.ModelAdmin):
    """穿搭-衣服關聯管理"""
    
    list_display = (
        'outfit',
        'clothes',
        'position_order',
        'added_at',
    )
    
    list_filter = (
        'outfit',
        'clothes__clothes_category',
        'added_at',
    )
    
    search_fields = (
        'outfit__outfit_name',
        'clothes__clothes_category',
    )
    
    readonly_fields = (
        'added_at',
    )
    
    ordering = ('outfit', 'position_order')


@admin.register(VirtualTryOn)
class VirtualTryOnAdmin(admin.ModelAdmin):
    """虛擬試衣記錄管理"""
    
    list_display = (
        'try_on_uid',
        'user',
        'status',
        'is_confirmed',
        'ai_processed_at',
        'created_at',
    )
    
    list_filter = (
        'status',
        'is_confirmed',
        'created_at',
    )
    
    search_fields = (
        'user__user_name',
        'try_on_uid',
    )
    
    readonly_fields = (
        'try_on_uid',
        'result_image_url',
        'result_file_name',
        'ai_response_data',
        'created_at',
        'ai_processed_at',
        'confirmed_at',
    )
    
    fieldsets = (
        ('虛擬試衣基本信息', {
            'fields': (
                'try_on_uid',
                'user',
                'outfit',
                'user_photo',
                'status',
            )
        }),
        ('衣服和結果', {
            'fields': (
                'clothes_list',
                'result_image_url',
                'result_file_name',
                'is_confirmed',
                'saved_outfit',
            )
        }),
        ('AI 處理數據', {
            'fields': (
                'ai_response_data',
                'ai_error_message',
            ),
            'classes': ('collapse',)
        }),
        ('時間戳', {
            'fields': (
                'created_at',
                'ai_processed_at',
                'confirmed_at',
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(OutfitFavorite)
class OutfitFavoriteAdmin(admin.ModelAdmin):
    """穿搭收藏管理"""
    
    list_display = (
        'outfit',
        'user',
        'liked_at',
    )
    
    list_filter = (
        'liked_at',
    )
    
    search_fields = (
        'outfit__outfit_name',
        'user__user_name',
    )
    
    readonly_fields = (
        'liked_at',
    )
    
    ordering = ('-liked_at',)
