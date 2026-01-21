from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserInfoSerializer,
    UserDeleteSerializer,
)
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    使用者註冊
    POST account/user/register

    Request:
        {"email": "user@example.com", "username": "user", "password": "mypassword123"}

    Success 201:
        {"id": 12345, "username": "user", "email": "user@example.com", "date_joined": "2026-01-21T10:00:00Z"}

    Error 400 (驗證失敗):
        {"email": ["輸入有效的電子郵件地址。"], "password": ["這個密碼太短了。至少需要包含 8 個字元。"]}

    Error 409 (帳號已存在):
        {"username": ["此使用者名稱已存在。"]} 或 {"email": ["此 Email 已被註冊。"]}
    """
    serializer = UserRegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        logger.info(f"✅ 新使用者註冊成功: {user.user_name} (id: {user.user_id})")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 判斷是欄位重複（409）還是驗證錯誤（400）
    conflict_fields = {'username', 'email'}
    errors = serializer.errors
    if any(
        field in conflict_fields
        and any('已' in str(msg) for msg in msgs)
        for field, msgs in errors.items()
    ):
        return Response(errors, status=status.HTTP_409_CONFLICT)

    return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    使用者登入
    POST account/user/login

    Request:
        {"username": "user@example.com", "password": "mypassword123"}
        username 欄位同時支援帳號名稱或 email

    Success 200:
        {
            "access": "eyJhb...",
            "refresh": "eyJhb...",
            "user": {"id": 12345, "username": "user", "email": "user@example.com"}
        }

    Error 401:
        {"detail": "找不到符合條件的有效使用者。"}
    """
    serializer = UserLoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']

        # 產生 JWT Token
        refresh = RefreshToken.for_user(user)

        logger.info(f"✅ 使用者登入成功: {user.user_name}")
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserInfoSerializer(user).data,
        }, status=status.HTTP_200_OK)

    # LoginSerializer 的 validate 會回傳 {"detail": "..."} 格式錯誤
    errors = serializer.errors
    if 'detail' in errors.get('non_field_errors', [{}])[0] if errors.get('non_field_errors') else False:
        detail_msg = errors['non_field_errors'][0].get('detail', '找不到符合條件的有效使用者。')
        return Response({'detail': detail_msg}, status=status.HTTP_401_UNAUTHORIZED)

    # 處理 serializer validate 回傳的 dict 格式錯誤
    if 'non_field_errors' in errors:
        for err in errors['non_field_errors']:
            if isinstance(err, dict) and 'detail' in err:
                return Response(
                    {'detail': err['detail']},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

    return Response(
        {'detail': '找不到符合條件的有效使用者。'},
        status=status.HTTP_401_UNAUTHORIZED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    使用者登出
    POST account/user/logout

    Headers:
        Authorization: Bearer <access_token>

    Request:
        {"refresh": "eyJhbGciOiJIUzI1NiIs..."}

    Success 200:
        {"detail": "登出成功。"}

    Error 401:
        {"detail": "身分認證資訊未提供。"}
    """
    refresh_token = request.data.get('refresh')

    if not refresh_token:
        return Response(
            {'detail': '請提供 refresh token。'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()  # 將 token 加入黑名單使其失效
        logger.info(f"✅ 使用者登出成功: {request.user.user_name}")
        return Response({'detail': '登出成功。'}, status=status.HTTP_200_OK)
    except TokenError:
        return Response(
            {'detail': 'Token 無效或已過期。'},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    """
    使用者刪除帳號
    POST account/user/delete

    Headers:
        Authorization: Bearer <access_token>

    Request:
        {"password": "mypassword123"}

    Success 200:
        {"message": "帳號已刪除"}

    Error 401:
        {"detail": "身分認證資訊未提供。"}

    Error 403:
        {"password": ["密碼不正確。"]}
    """
    serializer = UserDeleteSerializer(
        data=request.data,
        context={'request': request},
    )

    if serializer.is_valid():
        user = request.user
        user_name = user.user_name
        user.delete()
        logger.info(f"✅ 使用者刪除帳號成功: {user_name}")
        return Response({'message': '帳號已刪除'}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
