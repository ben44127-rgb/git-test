import logging
from typing import Dict, List, Tuple, Optional
from accounts.models import Clothes

logger = logging.getLogger(__name__)


class ClothesMatcher:
    """根据关键词篛选和匹配衣服的服务类"""
    
    def __init__(self, user):
        """
        初始化衣服匹配器
        
        Args:
            user: Django User 对象
        """
        self.user = user
    
    def filter_clothes_by_keywords(self, keywords: Dict) -> Dict[str, List]:
        """
        根据 AI 提取的关键词过滤衣服
        
        Args:
            keywords: 包含推荐类别、颜色、风格的字典
            
        Returns:
            包含 top_candidates 和 bottom_candidates 的字典
        """
        try:
            # 获取用户的所有衣伺
            user_clothes = Clothes.objects.filter(f_user_uid=self.user)
            
            if not user_clothes.exists():
                logger.warning(f"用户 {self.user.username} 没有衣伺")
                return {
                    "top_candidates": [],
                    "bottom_candidates": [],
                    "message": "用户没有衣伺，无法进行推荐"
                }
            
            recommended_categories = keywords.get('recommended_categories', [])
            recommended_colors = keywords.get('recommended_colors', [])
            recommended_styles = keywords.get('recommended_styles', [])
            
            # 匹配衣伺
            matches = []
            
            for clothes in user_clothes:
                score = self._calculate_matching_score(
                    clothes,
                    recommended_categories,
                    recommended_colors,
                    recommended_styles
                )
                
                if score > 0.3:  # 最低匹配分数阈值
                    matches.append({
                        'clothes': clothes,
                        'score': score
                    })
            
            # 按分数排序
            matches.sort(key=lambda x: x['score'], reverse=True)
            
            # 分离为上衣和下衣
            top_candidates = []
            bottom_candidates = []
            
            for match in matches:
                clothes = match['clothes']
                score = match['score']
                
                candidate = {
                    'clothes_uid': str(clothes.clothes_uid),
                    'clothes_category': clothes.clothes_category,
                    'colors': clothes.colors if isinstance(clothes.colors, list) else [clothes.colors],
                    'styles': clothes.styles if isinstance(clothes.styles, list) else [clothes.styles],
                    'clothes_image_url': clothes.clothes_image_url,
                    'matching_score': score
                }
                
                # 分类
                category_lower = clothes.clothes_category.lower()
                if any(t in category_lower for t in ['shirt', 'top', 'clothing', 't-shirt', 'blazer', 'jacket']):
                    top_candidates.append(candidate)
                elif any(b in category_lower for b in ['pants', 'skirt', 'bottom', 'trousers', 'shorts']):
                    bottom_candidates.append(candidate)
            
            return {
                "top_candidates": top_candidates[:10],  # 最多返回 10 件
                "bottom_candidates": bottom_candidates[:10]
            }
            
        except Exception as e:
            logger.error(f"衣服过滤失败：{e}")
            return {
                "top_candidates": [],
                "bottom_candidates": [],
                "error": str(e)
            }
    
    def _calculate_matching_score(self, clothes: Clothes, categories: List[str],
                                  colors: List[str], styles: List[str]) -> float:
        """
        计算单件衣服与关键词的匹配分数
        
        Args:
            clothes: Clothes 对象
            categories: 推荐分类列表
            colors: 推荐颜色列表
            styles: 推荐风格列表
            
        Returns:
            匹配分数（0.0-1.0）
        """
        score = 0.0
        
        # 分类匹配（权重 40%）
        if clothes.clothes_category.lower() in [c.lower() for c in categories]:
            score += 0.4
        else:
            # 模糊匹配
            for category in categories:
                if category.lower() in clothes.clothes_category.lower() or \
                   clothes.clothes_category.lower() in category.lower():
                    score += 0.2
                    break
        
        # 颜色匹配（权重 30%）
        clothes_colors = clothes.colors if isinstance(clothes.colors, list) else [clothes.colors]
        color_match_count = 0
        for color in colors:
            if any(color.lower() in c.lower() or c.lower() in color.lower() 
                   for c in clothes_colors):
                color_match_count += 1
        
        if color_match_count > 0:
            score += min(0.3, color_match_count * 0.15)
        
        # 风格匹配（权重 30%）
        clothes_styles = clothes.styles if isinstance(clothes.styles, list) else [clothes.styles]
        style_match_count = 0
        for style in styles:
            if any(style.lower() in s.lower() or s.lower() in style.lower() 
                   for s in clothes_styles):
                style_match_count += 1
        
        if style_match_count > 0:
            score += min(0.3, style_match_count * 0.15)
        
        return min(1.0, score)
    
    def find_best_combination(self, top_candidates: List[Dict], 
                             bottom_candidates: List[Dict]) -> Optional[Tuple]:
        """
        从候选衣伺中选择最佳搭配
        
        Args:
            top_candidates: 上衣候选列表
            bottom_candidates: 下衣候选列表
            
        Returns:
            最佳搭配的元组 (top, bottom)，或 None
        """
        if not top_candidates or not bottom_candidates:
            logger.warning("候选衣伺不足")
            return None
        
        # 简单策略：选择分数最高的组合
        best_top = top_candidates[0]
        best_bottom = bottom_candidates[0]
        
        return (best_top, best_bottom)
    
    def get_user_clothes_info(self) -> List[Dict]:
        """
        获取用户的衣伺简化信息
        
        Args:
            user: Django User 对象
            
        Returns:
            衣伺信息列表
        """
        try:
            user_clothes = Clothes.objects.filter(f_user_uid=self.user).values(
                'clothes_uid',
                'clothes_category',
                'colors',
                'styles'
            )[:20]  # 限制返回 20 件
            
            return list(user_clothes)
        except Exception as e:
            logger.error(f"获取用户衣伺信息失败：{e}")
            return []
