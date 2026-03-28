# 颜色定义和分类
COLOR_MAPPING = {
    '白色': ['white', '米色'],
    '黑色': ['black', '深灰'],
    '蓝色': ['blue', '深蓝', '浅蓝'],
    '红色': ['red', '深红', '浅红'],
    '绿色': ['green', '深绿', '浅绿'],
    '黄色': ['yellow', '金色', '米黄'],
    '粉色': ['pink', '浅粉'],
    '紫色': ['purple', '深紫'],
    '灰色': ['gray', '浅灰', '深灰'],
    '棕色': ['brown', '咖啡'],
}

# 衣伺分类
CLOTHES_CATEGORIES = {
    'TOP': ['T-shirt', 'Shirt', 'Blouse', 'Sweater', 'Hoodie', 'Jacket', 'Blazer', 'Cardigan'],
    'BOTTOM': ['Pants', 'Jeans', 'Skirt', 'Shorts', 'Trousers', 'Leggings'],
    'DRESS': ['Dress', 'Jumpsuit'],
    'OUTER': ['Coat', 'Jacket', 'Denim Jacket', 'Leather Jacket'],
}

# 风格定义
STYLES = {
    'CASUAL': ['Casual', 'Relaxed', 'Comfortable', 'Sporty'],
    'FORMAL': ['Formal', 'Business', 'Professional', 'Elegant'],
    'TRENDY': ['Trendy', 'Fashion-forward', 'Modern', 'Contemporary'],
    'CLASSIC': ['Classic', 'Timeless', 'Traditional', 'Conservative'],
    'BOHEMIAN': ['Bohemian', 'Boho', 'Artistic', 'Free-spirited'],
}

# 场景分类
OCCASIONS = {
    'CASUAL': ['逛街', '朋友聚餐', '看电影', '休闲'],
    'WORK': ['上班', '工作', '会议', '办公'],
    'DATE': ['约会', '独处', '拍照', '休闲时尚'],
    'PARTY': ['派对', '聚会', '活动', '宴会'],
    'SPORT': ['运动', '健身', '户外', '瑜伽'],
}

# 天气/季节分类
WEATHER_SEASONS = {
    'SPRING': ['春天', '春季', '温暖'],
    'SUMMER': ['夏天', '夏季', '炎热', '高温'],
    'AUTUMN': ['秋天', '秋季', '凉爽'],
    'WINTER': ['冬天', '冬季', '寒冷', '低温'],
    'RAINY': ['下雨', '阴雨', '潮湿'],
}

# 情感状态
EMOTIONS = {
    'CONFIDENT': ['自信', '霸气', '气场'],
    'COMFORTABLE': ['舒适', '舒服', '放松'],
    'ELEGANT': ['优雅', '高级', '气质'],
    'SEXY': ['性感', '魅力', '撩'],
    'CUTE': ['可爱', '甜美', '俏皮'],
}

# 默认配置
DEFAULT_RECOMMENDATION_TOP_K = 3
DEFAULT_CONVERSATION_CONTEXT = 'general'
DEFAULT_MATCHING_SCORE_THRESHOLD = 0.3

# Token 估计
TOKEN_ESTIMATE = {
    'user_message': 10,  # 每条用户消息的基础 token
    'ai_response': 200,  # 每条 AI 响应的基础 token
    'char_to_token_ratio': 0.25,  # 字符转 token 比率
}
