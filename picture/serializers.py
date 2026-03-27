"""
Serializers for Picture/Clothes Management API
圖片/衣服管理 API 的序列化器

這個檔案定義了所有的數據序列化器，用於
驗證和轉換請求/回應數據
"""

from rest_framework import serializers
from accounts.models import Clothes, Style, Color, Photo


class ColorSerializer(serializers.ModelSerializer):
    """顏色序列化器"""
    
    class Meta:
        model = Color
        fields = ['color_id', 'color_uid', 'color_name']
        read_only_fields = ['color_id', 'color_uid']


class StyleSerializer(serializers.ModelSerializer):
    """風格序列化器"""
    
    class Meta:
        model = Style
        fields = ['style_id', 'style_uid', 'style_name']
        read_only_fields = ['style_id', 'style_uid']


class ClothesSerializer(serializers.ModelSerializer):
    """
    衣服序列化器
    包含完整的衣服信息及其相關的風格和顏色
    """
    # 將相關的 Color 和 Style 作為嵌套序列化器
    colors = serializers.SerializerMethodField()
    styles = serializers.SerializerMethodField()
    
    class Meta:
        model = Clothes
        fields = [
            'clothes_id',
            'clothes_uid',
            'clothes_category',
            'clothes_arm_length',
            'clothes_shoulder_width',
            'clothes_waistline',
            'clothes_leg_length',
            'clothes_image_url',
            'clothes_favorite',
            'clothes_created_time',
            'clothes_updated_time',
            'colors',
            'styles'
        ]
        read_only_fields = [
            'clothes_id', 
            'clothes_uid',
            'clothes_created_time',
            'clothes_updated_time'
        ]
    
    def get_colors(self, obj):
        """獲取該衣服的所有顏色"""
        colors = Color.objects.filter(f_clothes_uid=obj.clothes_uid)
        return ColorSerializer(colors, many=True).data
    
    def get_styles(self, obj):
        """獲取該衣服的所有風格"""
        styles = Style.objects.filter(f_clothes_uid=obj.clothes_uid)
        return StyleSerializer(styles, many=True).data


class ClothesCreateSerializer(serializers.Serializer):
    """
    衣服創建序列化器 (用於 POST 和 PUT)
    包含衣服信息及相關的顏色和風格列表
    """
    clothes_category = serializers.CharField(
        max_length=100,
        help_text="衣服分類 (例如: 上衣, 褲子, 連身裙)"
    )
    clothes_arm_length = serializers.IntegerField(
        default=0,
        help_text="袖長 (cm)"
    )
    clothes_shoulder_width = serializers.IntegerField(
        default=0,
        help_text="肩寬 (cm)"
    )
    clothes_waistline = serializers.IntegerField(
        default=0,
        help_text="腰圍 (cm)"
    )
    clothes_leg_length = serializers.IntegerField(
        default=0,
        help_text="褲長 (cm)"
    )
    clothes_image_url = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="衣服圖片 URL"
    )
    colors = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=[],
        help_text="衣服顏色列表 (例如: ['藍色', '紅色', '黑色'])"
    )
    styles = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=[],
        help_text="衣服風格列表 (例如: ['休閒', '正式', '運動'])"
    )
    
    def validate_clothes_arm_length(self, value):
        """驗證袖長是否在合理範圍"""
        if value < 0 or value > 200:
            raise serializers.ValidationError("袖長必須在 0 到 200 cm 之間")
        return value
    
    def validate_clothes_shoulder_width(self, value):
        """驗證肩寬是否在合理範圍"""
        if value < 0 or value > 200:
            raise serializers.ValidationError("肩寬必須在 0 到 200 cm 之間")
        return value
    
    def validate_clothes_waistline(self, value):
        """驗證腰圍是否在合理範圍"""
        if value < 0 or value > 300:
            raise serializers.ValidationError("腰圍必須在 0 到 300 cm 之間")
        return value
    
    def validate_clothes_leg_length(self, value):
        """驗證褲長是否在合理範圍"""
        if value < 0 or value > 150:
            raise serializers.ValidationError("褲長必須在 0 到 150 cm 之間")
        return value


class ClothesDetailSerializer(serializers.ModelSerializer):
    """
    衣服詳情序列化器 (用於 GET 單個衣服)
    包含完整的衣服信息及其相關的風格和顏色
    """
    colors = serializers.SerializerMethodField()
    styles = serializers.SerializerMethodField()
    
    class Meta:
        model = Clothes
        fields = [
            'clothes_id',
            'clothes_uid',
            'clothes_category',
            'clothes_arm_length',
            'clothes_shoulder_width',
            'clothes_waistline',
            'clothes_leg_length',
            'clothes_image_url',
            'clothes_favorite',
            'clothes_created_time',
            'clothes_updated_time',
            'colors',
            'styles'
        ]
        read_only_fields = [
            'clothes_id',
            'clothes_uid',
            'clothes_created_time',
            'clothes_updated_time'
        ]
    
    def get_colors(self, obj):
        """獲取該衣服的所有顏色"""
        colors = Color.objects.filter(f_clothes_uid=obj.clothes_uid)
        return ColorSerializer(colors, many=True).data
    
    def get_styles(self, obj):
        """獲取該衣服的所有風格"""
        styles = Style.objects.filter(f_clothes_uid=obj.clothes_uid)
        return StyleSerializer(styles, many=True).data


class PhotoSerializer(serializers.ModelSerializer):
    """
    用戶照片序列化器
    用於照片的 CRUD 操作
    """
    
    class Meta:
        model = Photo
        fields = [
            'photo_id',
            'photo_uid',
            'photo_url',
            'photo_filename',
            'photo_file_size',
            'photo_content_type',
            'photo_uploaded_time',
            'photo_updated_time'
        ]
        read_only_fields = [
            'photo_id',
            'photo_uid',
            'photo_url',
            'photo_file_size',
            'photo_uploaded_time',
            'photo_updated_time'
        ]
