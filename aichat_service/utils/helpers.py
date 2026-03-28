import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    估计文本的 token 数量
    
    Args:
        text: 文本内容
        
    Returns:
        估计的 token 数量
    """
    from .constants import TOKEN_ESTIMATE
    
    # 简单估计：中文约 0.25 token/字符
    return int(len(text) * TOKEN_ESTIMATE['char_to_token_ratio']) + 10


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    安全的 JSON 解析
    
    Args:
        json_str: JSON 字符串
        default: 解析失败时的默认值
        
    Returns:
        解析后的对象，或默认值
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败：{e}")
        return default


def extract_json_from_text(text: str) -> Dict:
    """
    从文本中提取 JSON（Gemini API 可能返回额外文本）
    
    Args:
        text: 包含 JSON 的文本
        
    Returns:
        提取的 JSON 对象，失败返回空字典
    """
    try:
        # 查找第一个 { 和最后一个 }
        json_start = text.find('{')
        json_end = text.rfind('}')
        
        if json_start != -1 and json_end > json_start:
            json_str = text[json_start:json_end + 1]
            return json.loads(json_str)
        else:
            logger.warning("无法从文本中提取 JSON")
            return {}
    except Exception as e:
        logger.error(f"JSON 提取失败：{e}")
        return {}


def normalize_color(color: str) -> str:
    """
    规范化颜色名称
    
    Args:
        color: 颜色名称
        
    Returns:
        规范化后的颜色名称
    """
    from .constants import COLOR_MAPPING
    
    color_lower = color.lower().strip()
    
    # 查找匹配的颜色映射
    for key, values in COLOR_MAPPING.items():
        if color_lower in [v.lower() for v in values]:
            return key
    
    return color  # 如果没有匹配，返回原始值


def normalize_category(category: str) -> str:
    """
    规范化衣伺分类
    
    Args:
        category: 衣伺分类名称
        
    Returns:
        规范化后的分类
    """
    from .constants import CLOTHES_CATEGORIES
    
    category_lower = category.lower().strip()
    
    for key, values in CLOTHES_CATEGORIES.items():
        if any(category_lower in v.lower() or v.lower() in category_lower 
               for v in values):
            return key
    
    return category


def format_error_response(message: str, code: str = 'ERROR') -> Dict:
    """
    格式化错误响应
    
    Args:
        message: 错误消息
        code: 错误代码
        
    Returns:
        格式化的错误响应字典
    """
    return {
        'success': False,
        'error': {
            'code': code,
            'message': message
        }
    }


def format_success_response(data: Any, message: str = 'Success') -> Dict:
    """
    格式化成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
        
    Returns:
        格式化的成功响应字典
    """
    return {
        'success': True,
        'message': message,
        'data': data
    }


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    截断文本到最大长度
    
    Args:
        text: 原文本
        max_length: 最大长度
        
    Returns:
        截断后的文本
    """
    if len(text) > max_length:
        return text[:max_length] + '...'
    return text


def validate_user_input(text: str, min_length: int = 1, max_length: int = 500) -> bool:
    """
    验证用户输入
    
    Args:
        text: 用户输入的文本
        min_length: 最小长度
        max_length: 最大长度
        
    Returns:
        是否有效
    """
    if not text or not isinstance(text, str):
        return False
    
    text = text.strip()
    
    if len(text) < min_length or len(text) > max_length:
        return False
    
    return True


def merge_dicts(*dicts) -> Dict:
    """
    合并多个字典
    
    Args:
        *dicts: 字典列表
        
    Returns:
        合并后的字典
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result
