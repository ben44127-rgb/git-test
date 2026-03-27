"""
Serializers for Outfit/Combine Management API
穿搭組合和虛擬試衣管理的序列化器

主要包含：
1. OutfitSerializer - 基礎穿搭序列化器
2. OutfitDetailSerializer - 穿搭詳情序列化器（含衣服列表）
3. OutfitCreateSerializer - 創建穿搭時的驗證
4. VirtualTryOnSerializer - 虛擬試衣記錄序列化器
5. OutfitFavoriteSerializer - 收藏序列化器
"""

from rest_framework import serializers
from .models import (
    Outfit,
    OutfitClothes,
    VirtualTryOn,
    OutfitFavorite,
)
from accounts.models import Clothes
from picture.serializers import ClothesSerializer


class OutfitClothesSerializer(serializers.ModelSerializer):
    """穿搭-衣服關聯序列化器"""
    clothes = ClothesSerializer(read_only=True)
    
    class Meta:
        model = OutfitClothes
        fields = ['id', 'clothes', 'position_order', 'added_at']
        read_only_fields = ['id', 'added_at', 'clothes']


class OutfitSerializer(serializers.ModelSerializer):
    """
    穿搭基礎序列化器
    
    用於列表展示，包含基本信息
    """
    created_by_name = serializers.CharField(
        source='created_by.user_name',
        read_only=True
    )
    clothes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Outfit
        fields = [
            'outfit_uid',
            'outfit_name',
            'outfit_description',
            'preview_image_url',
            'created_by_name',
            'clothes_count',
            'is_liked',
            'is_draft',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'outfit_uid',
            'created_at',
            'updated_at',
            'clothes_count',
        ]
    
    def get_clothes_count(self, obj):
        """統計穿搭包含的衣服數量"""
        return obj.outfit_clothes.count()
    
    def get_is_liked(self, obj):
        """檢查當前用戶是否點讚了此穿搭"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return OutfitFavorite.objects.filter(
                outfit=obj,
                user=request.user
            ).exists()
        return False


class OutfitDetailSerializer(serializers.ModelSerializer):
    """
    穿搭詳情序列化器
    
    包含完整信息：
    - 穿搭基本信息
    - 包含的衣服列表
    - 用戶互動狀態
    """
    created_by = serializers.SerializerMethodField()
    outfit_clothes = OutfitClothesSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Outfit
        fields = [
            'outfit_uid',
            'outfit_name',
            'outfit_description',
            'preview_image_url',
            'outfit_clothes',
            'created_by',
            'is_liked',
            'is_draft',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'outfit_uid',
            'created_at',
            'updated_at',
            'outfit_clothes',
        ]
    
    def get_created_by(self, obj):
        """創建者信息"""
        return {
            'user_uid': str(obj.created_by.user_uid),
            'user_name': obj.created_by.user_name,
            'user_image_url': obj.created_by.user_image_url,
        }
    
    def get_is_liked(self, obj):
        """檢查當前用戶是否點讚"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return OutfitFavorite.objects.filter(
                outfit=obj,
                user=request.user
            ).exists()
        return False


class OutfitCreateSerializer(serializers.ModelSerializer):
    """
    穿搭創建序列化器
    
    用於驗證創建穿搭時的數據
    """
    clothes_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True,
        help_text='穿搭包含的衣服 UID 列表（必須恰好 2 件）'
    )
    
    class Meta:
        model = Outfit
        fields = [
            'outfit_name',
            'outfit_description',
            'clothes_ids',
            'preview_image_url',
            'is_draft',
        ]
    
    def validate(self, data):
        """驗證穿搭數據"""
        # 驗證衣服ID - 必須恰好 2 件衣服
        clothes_ids = data.get('clothes_ids', [])
        if len(clothes_ids) != 2:
            raise serializers.ValidationError({
                'clothes_ids': '穿搭必須恰好包含 2 件衣服'
            })
        
        # 檢查衣服是否存在
        valid_clothes = Clothes.objects.filter(
            clothes_uid__in=clothes_ids
        )
        if len(valid_clothes) != len(clothes_ids):
            raise serializers.ValidationError({
                'clothes_ids': '包含不存在的衣服 UUID'
            })
        
        # 驗證穿搭名稱
        if len(data.get('outfit_name', '')) == 0:
            raise serializers.ValidationError({
                'outfit_name': '穿搭名稱不能為空'
            })
        
        if len(data.get('outfit_name', '')) > 100:
            raise serializers.ValidationError({
                'outfit_name': '穿搭名稱最多 100 個字符'
            })
        
        return data
    
    def create(self, validated_data):
        """創建穿搭和關聯的衣服"""
        clothes_ids = validated_data.pop('clothes_ids')
        
        # 創建穿搭
        outfit = Outfit.objects.create(**validated_data)
        
        # 添加衣服
        valid_clothes = Clothes.objects.filter(clothes_uid__in=clothes_ids)
        for idx, clothes in enumerate(valid_clothes):
            OutfitClothes.objects.create(
                outfit=outfit,
                clothes=clothes,
                position_order=idx
            )
        
        return outfit


class VirtualTryOnSerializer(serializers.ModelSerializer):
    """
    虛擬試衣記錄序列化器
    
    用於展示和管理虛擬試衣流程
    """
    user_name = serializers.CharField(
        source='user.user_name',
        read_only=True
    )
    outfit_info = serializers.SerializerMethodField()
    
    class Meta:
        model = VirtualTryOn
        fields = [
            'try_on_uid',
            'user_name',
            'outfit',
            'outfit_info',
            'status',
            'clothes_list',
            'result_image_url',
            'result_file_name',
            'is_confirmed',
            'saved_outfit',
            'created_at',
            'ai_processed_at',
            'confirmed_at',
        ]
        read_only_fields = [
            'try_on_uid',
            'result_image_url',
            'result_file_name',
            'is_confirmed',
            'saved_outfit',
            'created_at',
            'ai_processed_at',
            'confirmed_at',
        ]
    
    def get_outfit_info(self, obj):
        """獲取關聯穿搭的基本信息"""
        if obj.outfit:
            return {
                'outfit_uid': str(obj.outfit.outfit_uid),
                'outfit_name': obj.outfit.outfit_name,
            }
        return None


class VirtualTryOnCreateSerializer(serializers.Serializer):
    """
    虛擬試衣創建序列化器
    
    用於驗證虛擬試衣請求
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
    photo_uid = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text='模特照片 UUID（如果不提供，使用用戶身體測量數據）'
    )
    
    def validate(self, data):
        """驗證虛擬試衣請求"""
        clothes_ids = data.get('clothes_ids', [])
        
        if len(clothes_ids) == 0:
            raise serializers.ValidationError({
                'clothes_ids': '虛擬試衣必須包含至少一件衣服'
            })
        
        if len(clothes_ids) > 10:
            raise serializers.ValidationError({
                'clothes_ids': '虛擬試衣最多包含 10 件衣服'
            })
        
        # 檢查衣服是否存在
        valid_clothes = Clothes.objects.filter(
            clothes_uid__in=clothes_ids,
            f_user_uid__user_name='系統'  # 確保是系統化的衣服
        )
        if len(valid_clothes) != len(clothes_ids):
            raise serializers.ValidationError({
                'clothes_ids': '包含不存在的衣服 UUID'
            })
        
        return data


class OutfitFavoriteSerializer(serializers.ModelSerializer):
    """穿搭收藏序列化器"""
    outfit_info = serializers.SerializerMethodField()
    
    class Meta:
        model = OutfitFavorite
        fields = ['outfit', 'outfit_info', 'liked_at']
        read_only_fields = ['outfit', 'liked_at']
    
    def get_outfit_info(self, obj):
        """獲取穿搭基本信息"""
        return {
            'outfit_uid': str(obj.outfit.outfit_uid),
            'outfit_name': obj.outfit.outfit_name,
            'preview_image_url': obj.outfit.preview_image_url,
        }

