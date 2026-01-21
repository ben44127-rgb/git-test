from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    使用者註冊序列化器
    
    Request:  {"email", "username", "password"}
    Response: {"id", "username", "email", "date_joined"}
    """
    # 輸入欄位對應（前端用 username/email/password，Model 用 user_name/user_email/user_password）
    username = serializers.CharField(source='user_name', max_length=150)
    email = serializers.EmailField(source='user_email')
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],  # 套用 Django 內建密碼驗證規則
    )

    # 輸出欄位
    id = serializers.IntegerField(source='user_id', read_only=True)
    date_joined = serializers.DateTimeField(source='user_created_time', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'date_joined')
        read_only_fields = ('id', 'date_joined')

    def validate_email(self, value):
        """檢查 email 是否已被註冊"""
        if User.objects.filter(user_email=value).exists():
            raise serializers.ValidationError("此 Email 已被註冊。")
        return value

    def validate_username(self, value):
        """檢查使用者名稱是否已存在"""
        if User.objects.filter(user_name=value).exists():
            raise serializers.ValidationError("此使用者名稱已存在。")
        return value

    def create(self, validated_data):
        """建立新使用者"""
        user = User.objects.create_user(
            user_name=validated_data['user_name'],
            user_email=validated_data['user_email'],
            user_password=validated_data.pop('password'),
        )
        return user


class UserInfoSerializer(serializers.ModelSerializer):
    """
    使用者資訊序列化器（用於登入回應中的 user 物件）
    
    Response: {"id", "username", "email"}
    """
    id = serializers.IntegerField(source='user_id', read_only=True)
    username = serializers.CharField(source='user_name', read_only=True)
    email = serializers.EmailField(source='user_email', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserLoginSerializer(serializers.Serializer):
    """
    使用者登入序列化器
    
    Request: {"username", "password"}
    username 欄位同時支援帳號名稱或 email 登入
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get('username')
        password = attrs.get('password')

        # 支援 email 或 username 登入
        user = None

        # 先嘗試用 email 查詢
        try:
            user_obj = User.objects.get(user_email=username_or_email)
            user = authenticate(
                username=user_obj.user_name,
                password=password,
            )
        except User.DoesNotExist:
            # 再嘗試用 username 查詢
            user = authenticate(
                username=username_or_email,
                password=password,
            )

        if user is None or not user.is_active:
            raise serializers.ValidationError(
                {"detail": "找不到符合條件的有效使用者。"}
            )

        attrs['user'] = user
        return attrs


class UserDeleteSerializer(serializers.Serializer):
    """
    使用者刪除帳號序列化器
    
    Request: {"password"}
    需要驗證密碼才能刪除帳號
    """
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("密碼不正確。")
        return value
