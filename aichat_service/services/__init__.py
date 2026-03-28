# 导出主要的服务类
from .ai_analyzer import AIAnalyzer
from .clothes_matcher import ClothesMatcher
from .recommender import RecommendationEngine
from .virtualtryon_client import VirtualTryOnClient

__all__ = [
    'AIAnalyzer',
    'ClothesMatcher',
    'RecommendationEngine',
    'VirtualTryOnClient',
]
