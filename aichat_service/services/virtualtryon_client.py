import requests
import logging
import os
from typing import Dict, Optional, List
from io import BytesIO

logger = logging.getLogger(__name__)


class VirtualTryOnClient:
    """与虚拟试穿 AI 后端通信的客户端"""
    
    def __init__(self):
        """初始化虚拟试穿客户端"""
        self.api_url = os.getenv('VIRTUALTRYON_API_URL', 'http://172.17.0.1:8002')
        self.timeout = int(os.getenv('VIRTUALTRYON_TIMEOUT', 60))
        self.endpoint = f"{self.api_url}/virtual_try_on/clothes/combine"
    
    def generate_tryon_image(self, model_image_url: str, garment_urls: List[str],
                            model_info: Dict, garments_info: List[Dict]) -> Optional[Dict]:
        """
        调用虚拟试穿 AI 生成合成图
        
        Args:
            model_image_url: 模特照片 URL
            garment_urls: 衣伺图片 URL 列表（2 件）
            model_info: 用户身体测量信息
            garments_info: 衣伺尺寸信息
            
        Returns:
            包含合成图片 URL 和风格分析的字典，或 None
        """
        try:
            if len(garment_urls) != 2:
                logger.error(f"衣伺数量错误：期望 2 件，收到 {len(garment_urls)} 件")
                return None
            
            # 准备请求数据
            files = {}
            data = {
                'model_info': model_info,
                'garments': garments_info
            }
            
            # 下载图片并添加到 files
            try:
                model_image_data = self._download_image(model_image_url)
                files['model_image'] = ('model.png', model_image_data, 'image/png')
                
                for idx, garment_url in enumerate(garment_urls):
                    garment_image_data = self._download_image(garment_url)
                    files[f'garment_{idx}'] = (f'garment_{idx}.png', garment_image_data, 'image/png')
            except Exception as e:
                logger.error(f"下载图片失败：{e}")
                return None
            
            # 发送请求
            logger.info(f"调用虚拟试穿 API：{self.endpoint}")
            response = requests.post(
                self.endpoint,
                files=files,
                data=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                # 解析 multipart/mixed 响应
                result = self._parse_multipart_response(response)
                logger.info("虚拟试穿成功")
                return result
            else:
                logger.error(f"虚拟试穿 API 返回错误：{response.status_code}")
                logger.error(f"错误详情：{response.text}")
                return None
                
        except requests.Timeout:
            logger.error("虚拟试穿 API 请求超时")
            return None
        except Exception as e:
            logger.error(f"虚拟试穿生成失败：{e}")
            return None
    
    def _download_image(self, image_url: str) -> BytesIO:
        """
        从 URL 下载图片
        
        Args:
            image_url: 图片 URL
            
        Returns:
            图片二进制数据
        """
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        return BytesIO(response.content)
    
    def _parse_multipart_response(self, response: requests.Response) -> Optional[Dict]:
        """
        解析 multipart/mixed 响应
        
        Args:
            response: 响应对象
            
        Returns:
            解析后的数据字典
        """
        try:
            # 简化处理：假设响应为 JSON + 二进制图片
            # 实际需要根据真实的 API 响应格式调整
            
            content_type = response.headers.get('content-type', '')
            
            if 'multipart' in content_type:
                # 处理 multipart 响应（这里简化处理）
                # 实际需要使用 multipart 解析库
                parts = response.text.split('\r\n\r\n')
                if len(parts) >= 2:
                    import json
                    json_part = parts[0]
                    # 尝试提取 JSON
                    try:
                        ai_response = json.loads(json_part)
                    except:
                        ai_response = {'message': '200'}
                    
                    return {
                        'image_url': 'placeholder_url',  # 实际需要保存二进制图片到 MinIO
                        'style_names': ai_response.get('data', {}).get('style_name', []),
                        'ai_response': ai_response
                    }
            else:
                # 假设响应为 JSON
                result = response.json()
                return {
                    'image_url': result.get('image_url'),
                    'style_names': result.get('data', {}).get('style_name', []),
                    'ai_response': result
                }
        except Exception as e:
            logger.error(f"解析虚拟试穿响应失败：{e}")
            return None
