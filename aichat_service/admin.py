from django.contrib import admin
from .models import Conversation, ChatMessage


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """对话管理后台"""
    
    list_display = ('conversation_id', 'f_user_uid', 'context', 'message_count', 
                    'is_active', 'created_at', 'updated_at')
    list_filter = ('context', 'is_active', 'created_at')
    search_fields = ('conversation_id', 'f_user_uid__username', 'tags')
    readonly_fields = ('conversation_id', 'created_at', 'updated_at', 'ended_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('conversation_id', 'f_user_uid', 'context')
        }),
        ('内容', {
            'fields': ('message_count', 'total_tokens_used', 'tags')
        }),
        ('状态', {
            'fields': ('is_active', 'created_at', 'updated_at', 'ended_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # 后台不允许直接创建


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """聊天消息管理后台"""
    
    list_display = ('message_id', 'conversation', 'role', 'content_preview', 
                    'input_tokens', 'output_tokens', 'created_at')
    list_filter = ('role', 'conversation__context', 'created_at')
    search_fields = ('message_id', 'content', 'conversation__conversation_id')
    readonly_fields = ('message_id', 'created_at', 'conversation')
    
    fieldsets = (
        ('对话', {
            'fields': ('message_id', 'conversation')
        }),
        ('消息内容', {
            'fields': ('role', 'content')
        }),
        ('推荐', {
            'fields': ('recommended_clothes', 'metadata')
        }),
        ('Token 计数', {
            'fields': ('input_tokens', 'output_tokens')
        }),
        ('时间戳', {
            'fields': ('created_at',)
        }),
    )
    
    def content_preview(self, obj):
        """显示内容预览"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'
    
    def has_add_permission(self, request):
        return False  # 后台不允许直接创建
    
    def has_delete_permission(self, request, obj=None):
        return False  # 后台不允许删除
