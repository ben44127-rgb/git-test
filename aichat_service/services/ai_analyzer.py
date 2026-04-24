import google.generativeai as genai
import json
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """使用 Gemini API 分析用户输入和提取关键词的服务类"""
    
    def __init__(self):
        """初始化 AI 分析器"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY 环境变量未设置")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def analyze_and_select_clothes(self, user_input: str, user_clothes: List[Dict]) -> Optional[Dict]:
        """
        分析用户输入并直接从提供的衣伺列表中挑选合适的上下装
        
        Args:
            user_input: 用户输入的文本
            user_clothes: 用户的衣伺列表
            
        Returns:
            包含挑选结果和推荐理由的字典
        """
        clothes_text = "\n".join([
            f"- UID: {c['clothes_uid']}, 类别: {c['clothes_category']}, 颜色: {c.get('colors', [])}, 风格: {c.get('styles', [])}"
            for c in user_clothes
        ])

        prompt = f"""
你是一位专业的穿搭顾问。用户的需求如下：
"{user_input}"

以下是用户目前拥有的所有衣伺：
{clothes_text}

请根据用户的需求，从上述衣伺中挑选出一件合适的上装（top）和一件合适的下装（bottom）。
请务必返回 JSON 格式的信息，包含你选择的衣服 UID，以及你提取的风格关键词和推荐理由：
{{
    "recommended_styles": ["Casual", "Sporty", ...],
    "top_clothes_uid": "...",
    "bottom_clothes_uid": "...",
    "reasoning": "搭配理由..."
}}

注意：如果找不到合适的，请尽可能挑出最接近的一套。确保返回的 top_clothes_uid 和 bottom_clothes_uid 真实存在于上面的列表中。
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = text[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                logger.warning(f"无法从 Gemini 响应中提取 JSON：{text}")
                return None
                
        except Exception as e:
            logger.error(f"Gemini API 调用失败：{e}")
            return None

    def analyze_user_input(self, user_input: str) -> Optional[Dict]:
        """
        分析用户输入，提取结构化关键词
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            包含关键词的字典，或 None 如果失败
        """
        prompt = f"""
请分析以下用户的穿搭需求，提取关键词并以 JSON 格式返回。

用户输入："{user_input}"

请返回以下 JSON 格式的信息（确保返回有效的 JSON）：
{{
    "occasion": ["..."],     
    "weather": ["..."],      
    "style": ["..."],        
    "emotion": ["..."],      
    "recommended_categories": ["T-shirt", "Shirt", "Pants", "Skirt"],
    "recommended_colors": ["白色", "黑色", "蓝色"],
    "recommended_styles": ["Casual", "Formal", "Sporty"],
    "intent": "recommendation|advice"
}}

注意：
- occasion: 场景或机会（逛街、上班、约会、参加活动等）
- weather: 天气或季节（晴天、雨天、冬季等）
- style: 用户希望呈现的风格（舒适、时尚、简约、性感等）
- emotion: 用户的情感状态（开心、冷静、自信等）
- recommended_categories: 推荐的衣伺分类
- recommended_colors: 推荐的颜色
- recommended_styles: 推荐的风格
- intent: 用户的意图（recommendation=需要推荐，advice=需要建议）
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # 尝试提取 JSON（Gemini 可能返回额外文本）
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = text[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                logger.warning(f"无法从 Gemini 响应中提取 JSON：{text}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败：{e}")
            return None
        except Exception as e:
            logger.error(f"Gemini API 调用失败：{e}")
            return None
    
    def verify_color_harmony(self, top_colors: List[str], bottom_colors: List[str]) -> Dict:
        """
        验证颜色搭配的和谐性
        
        Args:
            top_colors: 上衣颜色列表
            bottom_colors: 下衣颜色列表
            
        Returns:
            包含和谐性评分的字典
        """
        prompt = f"""
请评估以下颜色搭配的和谐性：

上衣颜色：{', '.join(top_colors)}
下衣颜色：{', '.join(bottom_colors)}

请返回 JSON 格式：
{{
    "harmony_score": 0.0-1.0,
    "explanation": "搭配说明",
    "suggestions": ["建议1", "建议2"]
}}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = text[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                return {
                    "harmony_score": 0.8,
                    "explanation": "颜色搭配不错",
                    "suggestions": []
                }
                
        except Exception as e:
            logger.error(f"颜色和谐性验证失败：{e}")
            return {
                "harmony_score": 0.5,
                "explanation": "无法评估",
                "suggestions": []
            }
    
    def generate_chat_response(self, user_message: str, conversation_context: str, 
                              user_info: Dict, clothes_list: List[Dict]) -> Optional[Dict]:
        """
        为用户消息生成 AI 聊天回应
        
        Args:
            user_message: 用户消息
            conversation_context: 对话上下文
            user_info: 用户信息（身高、体重等）
            clothes_list: 用户的衣伺列表
            
        Returns:
            包含回应和推荐的字典
        """
        clothes_text = "\n".join([
            f"- {c['category']}: {', '.join(c.get('colors', []))} ({', '.join(c.get('styles', []))})"
            for c in clothes_list[:10]  # 只列出前 10 件
        ])
        
        prompt = f"""
你是一位专业的穿搭顾问。

用户信息：
- 身高：{user_info.get('height', 'N/A')} cm
- 体重：{user_info.get('weight', 'N/A')} kg
- 体型：{user_info.get('body_type', 'N/A')}

用户的衣伺列表：
{clothes_text}

对话历史：{conversation_context if conversation_context else '(新对话)'}

用户问题：{user_message}

请提供：
1. 详细的穿搭建议
2. 推荐的衣伺（如果适用，提供衣伺 ID）
3. 搭配理由
4. 后续引导问题

请返回 JSON 格式：
{{
    "response": "你的回答文本",
    "recommended_clothes_ids": ["id1", "id2"],
    "suggestions": ["问题1", "问题2"],
    "tokens_estimate": 300
}}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = text[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                return {
                    "response": text,
                    "recommended_clothes_ids": [],
                    "suggestions": [],
                    "tokens_estimate": 200
                }
                
        except Exception as e:
            logger.error(f"生成聊天回应失败：{e}")
            return None
