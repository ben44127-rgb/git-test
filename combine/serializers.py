"""
Serializers for Combine Management API
虛擬試衣管理的序列化器

主要包含：
1. VirtualTryOnCreateSerializer - 虛擬試衣請求驗證
2. ModelSerializer - 模特試穿結果序列化器
"""

from rest_framework import serializers
from .models import Model
from accounts.models import Clothes


class VirtualTryOnCreateSerializer(serializers.Serializer):
    """
    虛擬試衣創建序列化器
    
    用於驗證虛擬試衣請求
    
    模特照片直接來自用戶個人檔案的 user_original_image_url
    衣服圖片直接使用 clothes_original_image_url
    
    返回給前端的預覽圖片：user_image_url（處理後）和 clothes_image_url（去背圖）
    """
    outfit_uid = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text='參考穿搭 UUID（可選，用於預定義搭配）'
    )
    clothes_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text='虛擬試衣使用的衣服 UUID 列表'
    )
    
    def validate(self, data):
        """驗證虛擬試衣請求"""
        clothes_ids = data.get('clothes_ids', [])

        # 3.1 規格：每次試穿必須恰好 2 件衣服
        if len(clothes_ids) != 2:
            raise serializers.ValidationError({
                'clothes_ids': '虛擬試穿必須恰好包含 2 件衣服'
            })

        # 不允許重複選取同一件衣服
        if len(set(clothes_ids)) != 2:
            raise serializers.ValidationError({
                'clothes_ids': '不能重複選擇同一件衣服'
            })

        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError({
                'detail': '未認證使用者，無法驗證衣服歸屬'
            })

        # 檢查衣服是否存在且屬於當前使用者
        valid_clothes = Clothes.objects.filter(
            clothes_uid__in=clothes_ids,
            f_user_uid=str(request.user.user_uid)
        )
        if valid_clothes.count() != 2:
            raise serializers.ValidationError({
                'clothes_ids': '衣服不存在或不屬於當前使用者'
            })
        
        return data


class ModelSerializer(serializers.ModelSerializer):
    """模特試穿結果序列化器"""
    
    class Meta:
        model = Model
        fields = [
            'model_id',
            'f_user_uid',
            'model_uid',
            'model_picture',
            'model_style',
            'clothes_list',
            'ai_response_data',
            'model_created_time',
            'model_updated_time',
        ]
        read_only_fields = [
            'model_id',
            'model_uid',
            'model_created_time',
            'model_updated_time',
        ]
