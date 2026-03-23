from django.contrib import admin
from accounts.models import Clothes, Style, Color


@admin.register(Clothes)
class ClothesAdmin(admin.ModelAdmin):
    """衣服模型的管理後台"""
    list_display = [
        'clothes_id',
        'clothes_category',
        'clothes_image_url',
        'clothes_favorite',
        'clothes_created_time'
    ]
    list_filter = [
        'clothes_category',
        'clothes_favorite',
        'clothes_created_time'
    ]
    search_fields = ['clothes_uid', 'clothes_category']
    readonly_fields = ['clothes_id', 'clothes_uid', 'clothes_created_time', 'clothes_updated_time']
    ordering = ['-clothes_created_time']


@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    """風格模型的管理後台"""
    list_display = [
        'style_id',
        'style_name',
        'f_clothes_uid'
    ]
    search_fields = ['style_uid', 'style_name', 'f_clothes_uid']
    readonly_fields = ['style_id', 'style_uid']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    """顏色模型的管理後台"""
    list_display = [
        'color_id',
        'color_name',
        'f_clothes_uid'
    ]
    search_fields = ['color_uid', 'color_name', 'f_clothes_uid']
    readonly_fields = ['color_id', 'color_uid']
