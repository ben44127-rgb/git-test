"""
Django Admin Configuration for Combine App
虛擬試衣管理的管理後台設定
"""

from django.contrib import admin
from .models import Model


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    """模特試穿結果管理"""
    
    list_display = (
        'model_uid',
        'f_user_uid',
        'model_created_time',
    )
    
    list_filter = (
        'model_created_time',
    )
    
    search_fields = (
        'model_uid',
        'f_user_uid',
        'model_style',
    )
    
    readonly_fields = (
        'model_uid',
        'model_created_time',
        'model_updated_time',
    )
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'model_uid',
                'f_user_uid',
            )
        }),
        ('試穿結果', {
            'fields': (
                'model_picture',
                'model_style',
                'clothes_list',
            )
        }),
        ('AI 回應', {
            'fields': (
                'ai_response_data',
            ),
            'classes': ('collapse',),
        }),
        ('時間戳', {
            'fields': (
                'model_created_time',
                'model_updated_time',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def has_add_permission(self, request):
        # 模特試穿結果只能通過虛擬試衣 API 創建
        return False
    
    def has_delete_permission(self, request, obj=None):
        # 管理員可以刪除
        return request.user.is_superuser
