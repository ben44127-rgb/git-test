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
            # 第一层：AI 分析
            logger.info("第一层：AI 分析用户输入")
            keywords = self.ai_analyzer.analyze_user_input(user_input)
            
            if not keywords:
                return {
                    'success': False,
                    'message': 'AI 分析失败'
                }
            
            # 第二层：衣服篛选
            logger.info("第二层：衣服篛选")
            filter_result = self.clothes_matcher.filter_clothes_by_keywords(keywords)
            
            top_candidates = filter_result.get('top_candidates', [])
            bottom_candidates = filter_result.get('bottom_candidates', [])
            
            if not top_candidates or not bottom_candidates:
                return {
                    'success': False,
                    'message': '用户衣伺不足，无法进行推荐',
                    'ai_keywords': keywords
                }
            
            # 第三层：组合推荐
            logger.info("第三层：组合推荐")
            recommendations = []
            
            # 生成 top_k 个推荐
            for rank in range(min(top_k, len(top_candidates), len(bottom_candidates))):
                if rank >= len(top_candidates) or rank >= len(bottom_candidates):
                    break
                
                top_clothes = top_candidates[rank]
                bottom_clothes = bottom_candidates[rank]
                
                # 第四层：虚拟试穿
                logger.info(f"第四层：虚拟试穿（推荐 {rank + 1}）")
                tryon_result = await self._perform_virtual_tryon(
                    top_clothes,
                    bottom_clothes,
                    keywords
                )
                
                if tryon_result:
                    # 第五层：结果保存
                    logger.info(f"第五层：保存推荐结果（推荐 {rank + 1}）")
                    model_record = await self._save_recommendation(
                        top_clothes,
                        bottom_clothes,
                        tryon_result,
                        user_input,
                        keywords,
                        rank + 1
                    )
                    
                    if model_record:
                        recommendations.append({
                            'rank': rank + 1,
                            'model_uid': str(model_record.model_uid),
                            'model_picture': model_record.model_picture,
                            'recommendation_score': model_record.recommendation_score,
                            'clothes_info': {
                                'top': top_clothes,
                                'bottom': bottom_clothes
                            },
                            'ai_reasoning': model_record.ai_analysis
                        })
            
            if not recommendations:
                return {
                    'success': False,
                    'message': '虚拟试穿失败，无法生成推荐'
                }
            
            return {
                'success': True,
                'message': '推荐穿搭生成成功',
                'ai_keywords': keywords.get('recommended_styles', []),
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
                ai_analysis=f"推荐排名：{rank}。{keywords.get('recommended_styles', [])} 风格的穿搭，搭配舒适和谐。"
            )
            
            model.save()
            logger.info(f"推荐结果已保存，model_uid={model.model_uid}")
            
            return model
            
        except Exception as e:
            logger.error(f"保存推荐失败：{e}")
            return None
