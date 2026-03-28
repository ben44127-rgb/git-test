from django.db import models
from django.conf import settings
import uuid


class Conversation(models.Model):
    """对话会话模型 - 用于 4.2 AI 文字对话"""
    
    CONTEXT_CHOICES = [
        ('outfit_recommendation', 'Outfit Recommendation'),
        ('style_advice', 'Style Advice'),
        ('general', 'General Question'),
    ]
    
    conversation_id = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
        help_text="对话会话的唯一标识"
    )
    f_user_uid = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_conversations',
        help_text="用户外键"
    )
    context = models.CharField(
        max_length=25,
        choices=CONTEXT_CHOICES,
        default='general',
        help_text="对话类型"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="对话标签"
    )
    
    message_count = models.IntegerField(
        default=0,
        help_text="对话信息数量"
    )
    total_tokens_used = models.IntegerField(
        default=0,
        help_text="总 Token 使用数"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="对话是否进行中"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="更新时间"
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="结束时间"
    )
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['f_user_uid', '-created_at']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = "AI 对话"
        verbose_name_plural = "AI 对话"
    
    def __str__(self):
        return f"Conversation {str(self.conversation_id)[:8]}... - {self.f_user_uid.username}"


class ChatMessage(models.Model):
    """对话信息模型 - 用于 4.2 AI 文字对话"""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    message_id = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
        help_text="信息的唯一标识"
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="所属对话"
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        help_text="角色：用户或助手"
    )
    content = models.TextField(
        help_text="信息内容"
    )
    
    # AI 推荐的衣伺
    recommended_clothes = models.JSONField(
        default=list,
        blank=True,
        help_text="推荐的衣伺列表"
    )
    
    # Token 计数
    input_tokens = models.IntegerField(
        default=0,
        help_text="输入 Token 数"
    )
    output_tokens = models.IntegerField(
        default=0,
        help_text="输出 Token 数"
    )
    
    # 额外元数据
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="额外的元数据"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="创建时间"
    )
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]
        verbose_name = "聊天信息"
        verbose_name_plural = "聊天信息"
    
    def __str__(self):
        return f"{self.role} - {self.message_id[:8]}..."
