import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

from .models import Conversation, ChatMessage
from .serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    ChatMessageSerializer
)
from .services.ai_analyzer import AIAnalyzer
from .services.clothes_matcher import ClothesMatcher
from .services.recommender import RecommendationEngine

logger = logging.getLogger(__name__)


class RecommendationViewSet(viewsets.ViewSet):
    """4.1 AI 智能推荐穿搭相关视图"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        生成推荐穿搭
        
        POST /aichat_service/recommend/generate
        """
        try:
            user_input = request.data.get('user_input', '')
            top_k = int(request.data.get('top_k', 1))
            
            # 参数验证
            if not user_input or len(user_input) < 1 or len(user_input) > 500:
                return Response(
                    {
                        'success': False,
                        'message': '用户输入必须在 1-500 字符之间'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if top_k < 1 or top_k > 3:
                return Response(
                    {
                        'success': False,
                        'message': 'top_k 必须在 1-3 之间'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 检查用户是否有模特照片和身体数据
            user_profile = request.user.account if hasattr(request.user, 'account') else None
            if not user_profile or not user_profile.user_image_url:
                return Response(
                    {
                        'success': False,
                        'message': '请先上传模特照片并补充身体测量数据后，才能使用推荐功能'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 检查用户是否有衣伺
            from accounts.models import Clothes
            if not Clothes.objects.filter(f_user_uid=request.user).exists():
                return Response(
                    {
                        'success': False,
                        'message': '用户没有衣伺，无法进行推荐'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 生成推荐
            engine = RecommendationEngine(request.user)
            
            # 这里需要使用 async，但由于 Django 视图的同步特性，
            # 我们可以使用 sync_to_async 或改用 ASGI
            # 为简化起见，这里注释掉 await
            import asyncio
            try:
                # 尝试获取事件循环
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                engine.generate_recommendations(user_input, top_k)
            )
            
            if result and result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    result or {'success': False, 'message': '推荐生成失败'},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
                
        except Exception as e:
            logger.error(f"推荐生成异常：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'推荐生成失败：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        查看推荐穿搭历史
        
        GET /aichat_service/recommend/history
        """
        try:
            from combine.models import Model
            
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 20))
            sort = request.query_params.get('sort', 'newest')
            
            # 获取用户的推荐记录
            queryset = Model.objects.filter(
                f_user_uid=request.user,
                source='ai_recommendation'
            )
            
            # 排序
            if sort == 'score_high':
                queryset = queryset.order_by('-recommendation_score')
            elif sort == 'oldest':
                queryset = queryset.order_by('created_at')
            else:  # newest
                queryset = queryset.order_by('-created_at')
            
            # 分页
            total = queryset.count()
            start = (page - 1) * limit
            end = start + limit
            results = queryset[start:end]
            
            # 序列化
            data = [
                {
                    'model_uid': str(r.model_uid),
                    'recommendation_score': r.recommendation_score,
                    'model_picture': r.model_picture,
                    'model_style': r.model_style,
                    'recommendation_context': r.recommendation_context,
                    'clothes_count': 2,  # AI 推荐总是 2 件
                    'created_at': r.created_at,
                    'source': r.source
                }
                for r in results
            ]
            
            return Response(
                {
                    'success': True,
                    'count': total,
                    'total_pages': (total + limit - 1) // limit,
                    'current_page': page,
                    'results': data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"获取推荐历史失败：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'获取历史失败：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatViewSet(viewsets.ViewSet):
    """4.2 AI 文字对话相关视图"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """
        开始新对话
        
        POST /aichat_service/chat/start
        """
        try:
            initial_message = request.data.get('initial_message', '')
            context = request.data.get('context', 'general')
            tags = request.data.get('tags', [])
            
            # 参数验证
            if not initial_message or len(initial_message) < 1 or len(initial_message) > 500:
                return Response(
                    {
                        'success': False,
                        'message': '初始消息必须在 1-500 字符之间'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 创建对话
            conversation = Conversation.objects.create(
                f_user_uid=request.user,
                context=context,
                tags=tags
            )
            
            # 保存用户消息
            user_message = ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content=initial_message
            )
            
            conversation.message_count = 1
            
            # 生成 AI 回应
            ai_analyzer = AIAnalyzer()
            
            # 获取用户信息和衣伺
            user_profile = request.user.account if hasattr(request.user, 'account') else None
            from accounts.models import Clothes
            user_clothes = Clothes.objects.filter(f_user_uid=request.user).values(
                'clothes_category', 'colors', 'styles'
            )
            
            user_info = {
                'height': user_profile.user_height if user_profile else 0,
                'weight': user_profile.user_weight if user_profile else 0,
                'body_type': 'normal'
            }
            
            clothes_list = list(user_clothes)
            
            ai_response_data = ai_analyzer.generate_chat_response(
                initial_message,
                '',  # 没有之前的对话
                user_info,
                clothes_list
            )
            
            if ai_response_data:
                ai_message = ChatMessage.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=ai_response_data.get('response', ''),
                    recommended_clothes=ai_response_data.get('recommended_clothes_ids', []),
                    output_tokens=ai_response_data.get('tokens_estimate', 0)
                )
                
                conversation.message_count = 2
                conversation.total_tokens_used = ai_response_data.get('tokens_estimate', 0)
                conversation.save()
                
                return Response(
                    {
                        'success': True,
                        'message': '对话已开始',
                        'conversation': {
                            'conversation_id': str(conversation.conversation_id),
                            'context': conversation.context,
                            'created_at': conversation.created_at,
                            'tags': conversation.tags
                        },
                        'ai_response': {
                            'message_id': str(ai_message.message_id),
                            'content': ai_message.content,
                            'recommended_clothes': ai_message.recommended_clothes,
                            'suggestions': ai_response_data.get('suggestions', []),
                            'created_at': ai_message.created_at
                        },
                        'tokens_used': {
                            'input': 0,
                            'output': ai_response_data.get('tokens_estimate', 0),
                            'total': ai_response_data.get('tokens_estimate', 0)
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {
                        'success': False,
                        'message': 'AI 无法生成回应'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
                
        except Exception as e:
            logger.error(f"开始对话失败：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'开始对话失败：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def my_conversations(self, request):
        """
        查看我的所有对话
        
        GET /aichat_service/chat/my-conversations
        """
        try:
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 20))
            sort = request.query_params.get('sort', 'newest')
            context_filter = request.query_params.get('context', None)
            
            queryset = Conversation.objects.filter(f_user_uid=request.user)
            
            if context_filter:
                queryset = queryset.filter(context=context_filter)
            
            # 排序
            if sort == 'most_messages':
                queryset = queryset.order_by('-message_count')
            elif sort == 'oldest':
                queryset = queryset.order_by('created_at')
            else:  # newest
                queryset = queryset.order_by('-updated_at')
            
            # 分页
            total = queryset.count()
            start = (page - 1) * limit
            end = start + limit
            results = queryset[start:end]
            
            # 序列化
            serializer = ConversationListSerializer(results, many=True)
            
            return Response(
                {
                    'success': True,
                    'count': total,
                    'total_pages': (total + limit - 1) // limit,
                    'current_page': page,
                    'results': serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"获取对话列表失败：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'获取对话列表失败：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='message')
    def send_message(self, request, pk=None):
        """
        发送聊天信息（多轮对话）
        
        POST /aichat_service/chat/{conversation_id}/message
        """
        try:
            conversation_id = pk
            message = request.data.get('message', '')
            include_recommendations = request.data.get('include_recommendations', True)
            
            # 参数验证
            if not message or len(message) < 1 or len(message) > 500:
                return Response(
                    {
                        'success': False,
                        'message': '消息必须在 1-500 字符之间'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 获取对话
            try:
                conversation = Conversation.objects.get(
                    conversation_id=conversation_id,
                    f_user_uid=request.user
                )
            except Conversation.DoesNotExist:
                return Response(
                    {
                        'success': False,
                        'message': '对话不存在'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if not conversation.is_active:
                return Response(
                    {
                        'success': False,
                        'message': '对话已结束'
                    },
                    status=status.HTTP_410_GONE
                )
            
            # 保存用户消息
            user_message = ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content=message
            )
            
            # 获取对话历史
            previous_messages = ChatMessage.objects.filter(
                conversation=conversation
            ).values('role', 'content')
            
            context_text = '\n'.join([
                f"{m['role']}: {m['content']}"
                for m in previous_messages[:10]  # 只保留最近 10 条
            ])
            
            # 生成 AI 回应
            ai_analyzer = AIAnalyzer()
            
            user_profile = request.user.account if hasattr(request.user, 'account') else None
            from accounts.models import Clothes
            user_clothes = Clothes.objects.filter(f_user_uid=request.user).values(
                'clothes_category', 'colors', 'styles'
            )
            
            user_info = {
                'height': user_profile.user_height if user_profile else 0,
                'weight': user_profile.user_weight if user_profile else 0,
                'body_type': 'normal'
            }
            
            clothes_list = list(user_clothes)
            
            ai_response_data = ai_analyzer.generate_chat_response(
                message,
                context_text,
                user_info,
                clothes_list
            )
            
            if ai_response_data:
                ai_message = ChatMessage.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=ai_response_data.get('response', ''),
                    recommended_clothes=ai_response_data.get('recommended_clothes_ids', []),
                    output_tokens=ai_response_data.get('tokens_estimate', 0)
                )
                
                conversation.message_count += 2
                conversation.total_tokens_used += ai_response_data.get('tokens_estimate', 0)
                conversation.save()
                
                return Response(
                    {
                        'success': True,
                        'conversation_id': str(conversation.conversation_id),
                        'ai_response': {
                            'message_id': str(ai_message.message_id),
                            'content': ai_message.content,
                            'recommended_clothes': ai_message.recommended_clothes,
                            'suggestions': ai_response_data.get('suggestions', []),
                            'created_at': ai_message.created_at
                        },
                        'message_history_count': conversation.message_count,
                        'tokens_used': {
                            'input': 0,
                            'output': ai_response_data.get('tokens_estimate', 0),
                            'total': ai_response_data.get('tokens_estimate', 0),
                            'cumulative_total': conversation.total_tokens_used
                        }
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        'success': False,
                        'message': 'AI 无法生成回应'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
                
        except Exception as e:
            logger.error(f"发送消息失败：{e}")
            return Response(
                {
                    'success': False,
                    'message': f'发送消息失败：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
