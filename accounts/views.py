from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
def register_user(request):
    """
    注册新用户
    接收: user_name, user_password, user_email, user_weight (可选), user_height (可选)
    """
    user_name = request.data.get('user_name') or request.data.get('username')
    user_password = request.data.get('user_password') or request.data.get('password')
    user_email = request.data.get('user_email') or request.data.get('email', '')
    user_weight = request.data.get('user_weight')
    user_height = request.data.get('user_height')
    
    if not user_name or not user_password:
        return Response({
            'success': False,
            'message': '用户名和密码不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not user_email:
        return Response({
            'success': False,
            'message': '邮箱不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查用户是否已存在
    if User.objects.filter(user_name=user_name).exists():
        return Response({
            'success': False,
            'message': '用户名已存在'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(user_email=user_email).exists():
        return Response({
            'success': False,
            'message': '邮箱已被注册'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 创建新用户
    try:
        user = User.objects.create_user(
            user_name=user_name,
            user_password=user_password,
            user_email=user_email,
            user_weight=user_weight,
            user_height=user_height
        )
        
        logger.info(f"✅ 新用户注册成功: {user_name} (uid: {user.user_uid})")
        
        return Response({
            'success': True,
            'message': '注册成功',
            'data': {
                'user_id': user.user_id,
                'user_uid': user.user_uid,
                'user_name': user.user_name,
                'user_email': user.user_email,
                'user_weight': user.user_weight,
                'user_height': user.user_height
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"❌ 用户注册失败: {str(e)}")
        return Response({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login_user(request):
    """
    用户登录
    接收: user_name/username, user_password/password
    """
    user_name = request.data.get('user_name') or request.data.get('username')
    user_password = request.data.get('user_password') or request.data.get('password')
    
    if not user_name or not user_password:
        return Response({
            'success': False,
            'message': '用户名和密码不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证用户
    user = authenticate(request, username=user_name, password=user_password)
    
    if user is not None:
        login(request, user)
        logger.info(f"✅ 用户登录成功: {user_name}")
        return Response({
            'success': True,
            'message': '登录成功',
            'data': {
                'user_id': user.user_id,
                'user_uid': user.user_uid,
                'user_name': user.user_name,
                'user_email': user.user_email,
                'user_weight': user.user_weight,
                'user_height': user.user_height,
                'user_image_url': user.user_image_url,
                'is_staff': user.is_staff,
                'is_active': user.is_active
            }
        }, status=status.HTTP_200_OK)
    else:
        logger.warning(f"⚠️ 登录失败: {user_name}")
        return Response({
            'success': False,
            'message': '用户名或密码错误'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_user(request):
    """
    用户登出
    """
    if request.user.is_authenticated:
        user_name = request.user.user_name
        logout(request)
        logger.info(f"✅ 用户登出成功: {user_name}")
        return Response({
            'success': True,
            'message': f'用户 {user_name} 已登出'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': '未登录'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_user(request):
    """
    删除当前用户
    接收: password (需要验证密码)
    """
    if not request.user.is_authenticated:
        return Response({
            'success': False,
            'message': '请先登录'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    password = request.data.get('password') or request.data.get('user_password')
    
    if not password:
        return Response({
            'success': False,
            'message': '请提供密码以确认删除'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证密码
    user = authenticate(username=request.user.user_name, password=password)
    
    if user is not None:
        user_name = user.user_name
        user.delete()
        logout(request)
        logger.info(f"✅ 用户删除成功: {user_name}")
        return Response({
            'success': True,
            'message': f'用户 {user_name} 已删除'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': '密码错误'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def check_auth(request):
    """
    检查用户登录状态
    """
    if request.user.is_authenticated:
        return Response({
            'success': True,
            'authenticated': True,
            'data': {
                'user_id': request.user.user_id,
                'user_uid': request.user.user_uid,
                'user_name': request.user.user_name,
                'user_email': request.user.user_email,
                'is_staff': request.user.is_staff
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': True,
            'authenticated': False,
            'message': '未登录'
        }, status=status.HTTP_200_OK)
