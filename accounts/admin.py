from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Clothes, Style, Color


class CustomUserAdmin(BaseUserAdmin):
    """自定義用戶管理界面"""
    list_display = ('user_id', 'user_name', 'user_email', 'user_weight', 'user_height', 'is_active', 'user_created_time')
    list_filter = ('is_active', 'is_staff', 'user_created_time')
    search_fields = ('user_name', 'user_email', 'user_uid')
    ordering = ('-user_created_time',)
    
    fieldsets = (
        (None, {'fields': ('user_name', 'user_email', 'user_password')}),
        ('個人資訊', {'fields': ('user_weight', 'user_height', 'user_image_url')}),
        ('權限', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('重要日期', {'fields': ('user_created_time', 'user_updated_time')}),
    )
    
    readonly_fields = ('user_uid', 'user_created_time', 'user_updated_time')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_name', 'user_email', 'user_password', 'user_weight', 'user_height'),
        }),
    )


class ClothesAdmin(admin.ModelAdmin):
    """衣服管理界面"""
    list_display = ('clothes_id', 'f_user_uid', 'clothes_category', 'clothes_size', 'clothes_favorite', 'clothes_created_time')
    list_filter = ('clothes_category', 'clothes_size', 'clothes_favorite', 'clothes_created_time')
    search_fields = ('clothes_uid', 'f_user_uid', 'clothes_category')
    ordering = ('-clothes_created_time',)
    readonly_fields = ('clothes_uid', 'clothes_created_time', 'clothes_updated_time')


class StyleAdmin(admin.ModelAdmin):
    """風格管理界面"""
    list_display = ('style_id', 'f_clothes_uid', 'style_name')
    search_fields = ('style_uid', 'f_clothes_uid', 'style_name')
    readonly_fields = ('style_uid',)


class ColorAdmin(admin.ModelAdmin):
    """顏色管理界面"""
    list_display = ('color_id', 'f_clothes_uid', 'color_name')
    search_fields = ('color_uid', 'f_clothes_uid', 'color_name')
    readonly_fields = ('color_uid',)


# 註冊模型到管理後台
admin.site.register(User, CustomUserAdmin)
admin.site.register(Clothes, ClothesAdmin)
admin.site.register(Style, StyleAdmin)
admin.site.register(Color, ColorAdmin)
