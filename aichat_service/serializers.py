from rest_framework import serializers
from .models import Conversation, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """聊天信息序列化器"""
    
    class Meta:
        model = ChatMessage
        fields = [
            'message_id',
            'role',
            'content',
            'recommended_clothes',
            'input_tokens',
            'output_tokens',
            'metadata',
            'created_at'
        ]
        read_only_fields = [
            'message_id',
            'input_tokens',
            'output_tokens',
            'created_at'
        ]


class ConversationSerializer(serializers.ModelSerializer):
    """对话序列化器"""
    
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'context',
            'tags',
            'message_count',
            'total_tokens_used',
            'is_active',
            'created_at',
            'updated_at',
            'ended_at',
            'messages'
        ]
        read_only_fields = [
            'conversation_id',
            'message_count',
            'total_tokens_used',
            'created_at',
            'updated_at',
            'ended_at'
        ]


class ConversationListSerializer(serializers.ModelSerializer):
    """对话列表序列化器（不包含所有消息，用于列表视图）"""
    
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'context',
            'tags',
            'message_count',
            'total_tokens_used',
            'is_active',
            'created_at',
            'updated_at',
            'last_message'
        ]
    
    def get_last_message(self, obj):
        """获取最后一条消息的内容"""
        last_msg = obj.messages.last()
        if last_msg:
            return last_msg.content[:100]  # 只返回前 100 个字符
        return None
