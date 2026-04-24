import logging
import json
from typing import Dict, List, Optional
from django.utils import timezone
from django.contrib.auth.models import User

from .ai_analyzer import AIAnalyzer
from .clothes_matcher import ClothesMatcher
from .virtualtryon_client import VirtualTryOnClient
from combine.models import Model
from accounts.models import User as CustomUser
from accounts.models import Clothes

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """推荐穿搭的核心引擎 - 用于 4.1 AI 智能推薦穿搭"""
    
    def __init__(self, user):
        """
        初始化推荐引擎
        
        Args:
            user: Django User 对象
        """
        self.user = user
        self.ai_analyzer = AIAnalyzer()
        self.clothes_matcher = ClothesMatcher(user)
        self.virtualtryon_client = VirtualTryOnClient()
    
    async def generate_recommendations(self, user_input: str, top_k: int = 1) -> Optional[Dict]:
        """
        生成推荐穿搭
        
        Args:
            user_input: 用户输入的文字
            top_k: 返回前 K 个推荐结果
            
        Returns:
            推荐结果字典，包含虚拟试穿图片和分析
        """
        try:
            logger.info("第一层：获取用户的全部衣伺")
            user_clothes = self.clothes_matcher.get_user_clothes_info()
            
            if not user_clothes:
                return {
                    'success': False,
                    'message': '用户没有衣伺，无法进行推荐'
                }
            
            logger.info("第二层：AI 分析用户输入并挑选衣伺")
            ai_result = self.ai_analyzer.analyze_and_select_clothes(user_input, user_clothes)
            
            if not ai_result or not ai_result.get('top_clothes_uid') or not ai_result.get('bottom_clothes_uid'):
                return {
                    'success': False,
                    'message': 'AI 无法为您挑选合适的衣伺，请提供更多信息'
                }
            
            logger.info("第三层：组合推荐")
            top_clothes_obj = Clothes.objects.filter(clothes_uid=ai_result['top_clothes_uid']).first()
            bottom_clothes_obj = Clothes.objects.filter(clothes_uid=ai_result['bottom_clothes_uid']).first()
            
            if not top_clothes_obj or not bottom_clothes_obj:
                return {
                    'success': False,
                    'message': 'AI 挑选的衣伺无效'
                }
            
            # 组装为后续需要的格式
            top_clothes = {
                'clothes_uid': str(top_clothes_obj.clothes_uid),
                'clothes_category': top_clothes_obj.clothes_category,
                'clothes_image_url': top_clothes_obj.clothes_image_url,
                'matching_score': 0.95
            }
            bottom_clothes = {
                'clothes_uid': str(bottom_clothes_obj.clothes_uid),
                'clothes_category': bottom_clothes_obj.clothes_category,
                'clothes_image_url': bottom_clothes_obj.clothes_image_url,
                'matching_score': 0.95
            }
            
            recommendations = []
            
            logger.info("第四层：虚拟试穿")
            # 组装一个假的 keywords 以复用已有方法
            fake_keywords = {
                'recommended_styles': ai_result.get('recommended_styles', []),
                'reasoning': ai_result.get('reasoning', '')
            }
            
            tryon_result = await self._perform_virtual_tryon(
                top_clothes,
                bottom_clothes,
                fake_keywords
            )
            
            if tryon_result:
                logger.info("第五层：保存推荐结果")
                model_record = await self._save_recommendation(
                    top_clothes,
                    bottom_clothes,
                    tryon_result,
                    user_input,
                    fake_keywords,
                    1
                )
                
                if model_record:
                    recommendations.append({
                        'rank': 1,
                        'model_uid': str(model_record.model_uid),
                        'model_picture': model_record.model_picture,
                        'recommendation_score': model_record.recommendation_score,
                        'clothes_info': {
                            'top': top_clothes,
                            'bottom': bottom_clothes
                        },
                        'ai_reasoning': ai_result.get('reasoning', '')
                    })
            
            if not recommendations:
                return {
                    'success': False,
                    'message': '虚拟试穿失败，无法生成推荐'
                }
            
            return {
                'success': True,
                'message': '推荐穿搭生成成功',
                'ai_keywords': ai_result.get('recommended_styles', []),
                'recommendations': recommendations,
                'total_recommendations': len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"生成推荐失败：{e}")
            return {
                'success': False,
                'message': f'生成推荐失败：{str(e)}'
            }
    
    async def _perform_virtual_tryon(self, top_clothes: Dict, bottom_clothes: Dict,
                                     keywords: Dict) -> Optional[Dict]:
        """
        执行虚拟试穿
        
        Args:
            top_clothes: 上衣信息
            bottom_clothes: 下衣信息
            keywords: AI 提取的关键词
            
        Returns:
            虚拟试穿结果
        """
        try:
            # 获取用户信息
            user_profile = self.user.account if hasattr(self.user, 'account') else None
            
            model_image_url = user_profile.user_image_url if user_profile else None
            if not model_image_url:
                logger.error("用户未设置模特照片")
                return None
            
            model_info = {
                'user_height': user_profile.user_height if user_profile else 0,
                'user_weight': user_profile.user_weight if user_profile else 0,
                'user_shoulder_width': user_profile.user_shoulder_width if user_profile else 0,
                'user_arm_length': user_profile.user_arm_length if user_profile else 0,
                'user_waistline': user_profile.user_waistline if user_profile else 0,
                'user_leg_length': user_profile.user_leg_length if user_profile else 0,
            }
            
            garments_info = [
                {
                    'clothes_category': top_clothes['clothes_category'],
                    'garment_info': {
                        'clothes_arm_length': 65.0,
                        'clothes_shoulder_width': 48.0
                    }
                },
                {
                    'clothes_category': bottom_clothes['clothes_category'],
                    'garment_info': {
                        'clothes_leg_length': 100.0,
                        'clothes_waistline': 90.0
                    }
                }
            ]
            
            garment_urls = [
                top_clothes['clothes_image_url'],
                bottom_clothes['clothes_image_url']
            ]
            
            # 调用虚拟试穿 API
            result = self.virtualtryon_client.generate_tryon_image(
                model_image_url,
                garment_urls,
                model_info,
                garments_info
            )
            
            return result
            
        except Exception as e:
            logger.error(f"虚拟试穿失败：{e}")
            return None
    
    async def _save_recommendation(self, top_clothes: Dict, bottom_clothes: Dict,
                                   tryon_result: Dict, user_input: str, keywords: Dict,
                                   rank: int) -> Optional[Model]:
        """
        保存推荐结果到 Model 表
        
        Args:
            top_clothes: 上衣信息
            bottom_clothes: 下衣信息
            tryon_result: 虚拟试穿结果
            user_input: 用户原始输入
            keywords: AI 提取的关键词
            rank: 推荐排名
            
        Returns:
            保存的 Model 对象
        """
        try:
            # 计算推荐分数
            recommendation_score = (
                top_clothes.get('matching_score', 0.8) * 0.5 +
                bottom_clothes.get('matching_score', 0.8) * 0.5
            )
            
            # 创建 Model 记录
            model = Model(
                f_user_uid=self.user,
                model_picture=tryon_result.get('image_url', ''),
                model_style=tryon_result.get('style_names', []),
                source='ai_recommendation',
                recommendation_context=user_input,
                recommendation_keywords=keywords,
                recommendation_score=recommendation_score,
                ai_analysis=keywords.get('reasoning', f"推薦排名：{rank}。搭配舒適和諧。")
            )
            
            model.save()
            logger.info(f"推荐结果已保存，model_uid={model.model_uid}")
            
            return model
            
        except Exception as e:
            logger.error(f"保存推荐失败：{e}")
            return None
