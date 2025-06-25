import re
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import hashlib

class WritingStyleAnalyzer:
    """
    文风分析器
    分析文档的写作风格特征，生成文风模板，支持文风对齐功能
    """
    
    def __init__(self, storage_path: str = "src/core/knowledge_base/writing_style_templates"):
        self.tool_name = "文风分析器"
        self.description = "分析文档写作风格，生成文风模板，支持文风对齐和润色功能"
        self.storage_path = storage_path
        
        # 确保存储目录存在
        os.makedirs(storage_path, exist_ok=True)
        
        # 文风特征分析维度
        self.style_dimensions = {
            "sentence_structure": {
                "name": "句式结构",
                "features": ["平均句长", "长短句比例", "复合句使用", "并列句使用"]
            },
            "vocabulary_choice": {
                "name": "词汇选择", 
                "features": ["正式程度", "专业术语", "修饰词使用", "动词类型偏好"]
            },
            "expression_style": {
                "name": "表达方式",
                "features": ["主被动语态", "人称使用", "语气强度", "情感色彩"]
            },
            "text_organization": {
                "name": "文本组织",
                "features": ["段落结构", "逻辑连接", "过渡方式", "总结习惯"]
            },
            "language_habits": {
                "name": "语言习惯",
                "features": ["口语化程度", "书面语规范", "地域特色", "行业特色"]
            }
        }
        
        # 常见文风类型
        self.style_types = {
            "formal_official": {
                "name": "正式公文风格",
                "characteristics": ["严谨规范", "用词准确", "逻辑清晰", "格式标准"],
                "typical_patterns": ["根据", "按照", "现将", "特此", "务必"]
            },
            "business_professional": {
                "name": "商务专业风格", 
                "characteristics": ["简洁明了", "重点突出", "数据导向", "结果导向"],
                "typical_patterns": ["提升", "优化", "实现", "达成", "推进"]
            },
            "academic_research": {
                "name": "学术研究风格",
                "characteristics": ["客观严谨", "逻辑严密", "论证充分", "引用规范"],
                "typical_patterns": ["研究表明", "分析发现", "综合考虑", "深入探讨"]
            },
            "narrative_descriptive": {
                "name": "叙述描述风格",
                "characteristics": ["生动形象", "细节丰富", "情感真实", "故事性强"],
                "typical_patterns": ["生动地", "详细地", "深刻地", "真实地"]
            },
            "concise_practical": {
                "name": "简洁实用风格",
                "characteristics": ["言简意赅", "直接有效", "操作性强", "易于理解"],
                "typical_patterns": ["直接", "立即", "马上", "简单", "快速"]
            }
        }
    
    def analyze_writing_style(self, document_content: str, document_name: str = None) -> Dict[str, Any]:
        """
        分析文档的写作风格
        
        Args:
            document_content: 文档内容
            document_name: 文档名称
            
        Returns:
            文风分析结果
        """
        try:
            analysis_result = {
                "document_name": document_name or "未命名文档",
                "analysis_time": datetime.now().isoformat(),
                "style_features": {},
                "style_type": None,
                "confidence_score": 0.0,
                "style_prompt": "",
                "template_id": None
            }
            
            # 分析各个维度的文风特征
            style_features = self._analyze_style_features(document_content)
            analysis_result["style_features"] = style_features
            
            # 识别文风类型
            style_type, confidence = self._identify_style_type(document_content, style_features)
            analysis_result["style_type"] = style_type
            analysis_result["confidence_score"] = confidence
            
            # 生成文风提示词
            style_prompt = self._generate_style_prompt(style_features, style_type)
            analysis_result["style_prompt"] = style_prompt
            
            # 生成模板ID
            template_id = self._generate_template_id(document_name, style_features)
            analysis_result["template_id"] = template_id
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"文风分析失败: {str(e)}"}
    
    def _analyze_style_features(self, content: str) -> Dict[str, Any]:
        """分析文风特征"""
        if not content or not content.strip():
            return self._get_empty_features()

        features = {}

        try:
            # 句式结构分析
            features["sentence_structure"] = self._analyze_sentence_structure(content)

            # 词汇选择分析
            features["vocabulary_choice"] = self._analyze_vocabulary_choice(content)

            # 表达方式分析
            features["expression_style"] = self._analyze_expression_style(content)

            # 文本组织分析
            features["text_organization"] = self._analyze_text_organization(content)

            # 语言习惯分析
            features["language_habits"] = self._analyze_language_habits(content)

            # 新增：情感色彩分析
            features["emotional_tone"] = self._analyze_emotional_tone(content)

            # 新增：专业性分析
            features["professionalism"] = self._analyze_professionalism(content)

            # 新增：修辞手法分析
            features["rhetorical_devices"] = self._analyze_rhetorical_devices(content)

        except Exception as e:
            print(f"文风特征分析出错: {str(e)}")
            features = self._get_empty_features()

        return features

    def _get_empty_features(self) -> Dict[str, Any]:
        """获取空的特征结构"""
        return {
            "sentence_structure": {"average_length": 0, "long_short_ratio": 0, "complex_ratio": 0, "total_sentences": 0},
            "vocabulary_choice": {"formality_score": 0, "technical_density": 0, "modifier_usage": 0, "action_verb_ratio": 0},
            "expression_style": {"passive_active_ratio": 0, "person_usage": {"first_person": 0, "second_person": 0, "third_person": 0}, "tone_strength": 0},
            "text_organization": {"paragraph_count": 0, "average_paragraph_length": 0, "connector_density": 0, "summary_usage": 0},
            "language_habits": {"colloquial_level": 0, "formal_structure_usage": 0, "de_structure_density": 0},
            "emotional_tone": {"positive_ratio": 0, "negative_ratio": 0, "neutral_ratio": 1.0, "intensity": 0},
            "professionalism": {"domain_specificity": 0, "authority_indicators": 0, "precision_level": 0},
            "rhetorical_devices": {"metaphor_usage": 0, "parallel_structure": 0, "question_usage": 0}
        }
    
    def _analyze_sentence_structure(self, content: str) -> Dict[str, Any]:
        """分析句式结构"""
        # 清理内容，移除多余的空白字符
        content = re.sub(r'\s+', ' ', content.strip())

        # 更精确的句子分割
        sentences = re.split(r'[。！？；\.!?;]', content)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]

        if not sentences:
            return {
                "average_length": 0,
                "long_short_ratio": 0,
                "complex_ratio": 0,
                "total_sentences": 0
            }

        # 计算平均句长
        total_chars = sum(len(s) for s in sentences)
        average_length = total_chars / len(sentences)

        # 长短句比例（长句定义为超过25字）
        long_sentences = [s for s in sentences if len(s) > 25]
        short_sentences = [s for s in sentences if len(s) <= 15]
        long_short_ratio = len(long_sentences) / len(sentences) if sentences else 0

        # 复合句比例（包含逗号、分号、连词等的句子）
        complex_patterns = [r'，', r'；', r'：', r'而且', r'但是', r'然而', r'因为', r'所以', r'如果', r'虽然']
        complex_sentences = []
        for sentence in sentences:
            if any(re.search(pattern, sentence) for pattern in complex_patterns):
                complex_sentences.append(sentence)
        complex_ratio = len(complex_sentences) / len(sentences) if sentences else 0

        return {
            "average_length": round(average_length, 1),
            "long_short_ratio": round(long_short_ratio, 3),
            "complex_ratio": round(complex_ratio, 3),
            "total_sentences": len(sentences),
            "long_sentences": len(long_sentences),
            "short_sentences": len(short_sentences)
        }
    
    def _analyze_vocabulary_choice(self, content: str) -> Dict[str, Any]:
        """分析词汇选择"""
        # 清理内容
        content_clean = re.sub(r'\s+', '', content)
        total_chars = len(content_clean)

        if total_chars == 0:
            return {
                "formality_score": 0,
                "technical_density": 0,
                "modifier_usage": 0,
                "action_verb_ratio": 0
            }

        # 正式词汇模式
        formal_words = ["根据", "按照", "依据", "鉴于", "基于", "关于", "针对", "为了", "通过", "采用",
                       "进行", "实施", "开展", "落实", "确保", "保证", "维护", "促进", "推动", "加强"]
        formal_count = sum(content.count(word) for word in formal_words)

        # 专业术语模式
        technical_patterns = [
            r'[\u4e00-\u9fff]+系统', r'[\u4e00-\u9fff]+技术', r'[\u4e00-\u9fff]+方案',
            r'[\u4e00-\u9fff]+标准', r'[\u4e00-\u9fff]+规范', r'[\u4e00-\u9fff]+平台',
            r'[\u4e00-\u9fff]+模式', r'[\u4e00-\u9fff]+机制', r'[\u4e00-\u9fff]+流程'
        ]
        technical_count = sum(len(re.findall(pattern, content)) for pattern in technical_patterns)

        # 修饰词使用
        modifiers = ["很", "非常", "特别", "极其", "相当", "比较", "较为", "十分", "更加", "进一步"]
        modifier_count = sum(content.count(word) for word in modifiers)

        # 动词类型（动作动词）
        action_verbs = ["实施", "执行", "开展", "推进", "落实", "完成", "达成", "实现", "提升", "优化",
                       "改进", "建设", "构建", "发展", "创新", "突破", "解决", "处理", "管理", "运营"]
        action_count = sum(content.count(word) for word in action_verbs)

        # 计算密度（每千字）
        multiplier = 1000 / total_chars if total_chars > 0 else 0

        return {
            "formality_score": round(formal_count * multiplier, 2),
            "technical_density": round(technical_count * multiplier, 2),
            "modifier_usage": round(modifier_count * multiplier, 2),
            "action_verb_ratio": round(action_count * multiplier, 2)
        }
    
    def _analyze_expression_style(self, content: str) -> Dict[str, Any]:
        """分析表达方式"""
        total_chars = len(content)

        if total_chars == 0:
            return {
                "passive_active_ratio": 0,
                "person_usage": {"first_person": 0, "second_person": 0, "third_person": 0},
                "tone_strength": 0
            }

        # 被动语态检测（更精确的模式）
        passive_patterns = [
            r'[\u4e00-\u9fff]+被[\u4e00-\u9fff]+', r'[\u4e00-\u9fff]+受到[\u4e00-\u9fff]+',
            r'[\u4e00-\u9fff]+得到[\u4e00-\u9fff]+', r'[\u4e00-\u9fff]+获得[\u4e00-\u9fff]+',
            r'[\u4e00-\u9fff]+遭到[\u4e00-\u9fff]+', r'[\u4e00-\u9fff]+受[\u4e00-\u9fff]+影响'
        ]
        passive_count = sum(len(re.findall(pattern, content)) for pattern in passive_patterns)

        # 主动语态检测
        active_patterns = [
            r'[\u4e00-\u9fff]+进行[\u4e00-\u9fff]+', r'[\u4e00-\u9fff]+开展[\u4e00-\u9fff]+',
            r'[\u4e00-\u9fff]+实施[\u4e00-\u9fff]+', r'[\u4e00-\u9fff]+推进[\u4e00-\u9fff]+',
            r'[\u4e00-\u9fff]+完成[\u4e00-\u9fff]+', r'[\u4e00-\u9fff]+建设[\u4e00-\u9fff]+'
        ]
        active_count = sum(len(re.findall(pattern, content)) for pattern in active_patterns)

        # 人称使用统计
        first_person = content.count('我') + content.count('我们') + content.count('本人') + content.count('笔者')
        second_person = content.count('你') + content.count('您') + content.count('你们') + content.count('各位')
        third_person = content.count('他') + content.count('她') + content.count('它') + content.count('他们') + content.count('她们')

        # 语气强度分析
        strong_words = ['必须', '务必', '严禁', '绝对', '一定', '坚决', '严格', '切实']
        mild_words = ['建议', '希望', '可以', '尽量', '适当', '酌情', '可能', '或许']

        strong_tone = sum(content.count(word) for word in strong_words)
        mild_tone = sum(content.count(word) for word in mild_words)

        # 计算比例
        total_voice_patterns = passive_count + active_count
        passive_ratio = passive_count / total_voice_patterns if total_voice_patterns > 0 else 0

        return {
            "passive_active_ratio": round(passive_ratio, 3),
            "person_usage": {
                "first_person": first_person,
                "second_person": second_person,
                "third_person": third_person
            },
            "tone_strength": round((strong_tone - mild_tone) / total_chars * 1000, 2) if total_chars > 0 else 0,
            "passive_count": passive_count,
            "active_count": active_count
        }
    
    def _analyze_text_organization(self, content: str) -> Dict[str, Any]:
        """分析文本组织"""
        # 段落分析（按换行符分割）
        paragraphs = re.split(r'\n\s*\n', content)
        paragraphs = [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 10]

        total_chars = len(content)

        if total_chars == 0:
            return {
                "paragraph_count": 0,
                "average_paragraph_length": 0,
                "connector_density": 0,
                "summary_usage": 0
            }

        # 逻辑连接词（更全面）
        connectors = [
            "首先", "其次", "然后", "最后", "因此", "所以", "但是", "然而", "此外", "另外",
            "同时", "而且", "并且", "不过", "虽然", "尽管", "由于", "鉴于", "基于", "根据",
            "总之", "综上", "另一方面", "与此同时", "相比之下", "换言之", "也就是说"
        ]
        connector_count = sum(content.count(word) for word in connectors)

        # 总结性表达
        summary_words = ["总之", "综上", "总的来说", "综合以上", "总而言之", "综上所述", "由此可见", "可以看出"]
        summary_count = sum(content.count(word) for word in summary_words)

        # 列举标识
        enumeration_patterns = [r'[一二三四五六七八九十]、', r'\d+[\.、]', r'[（(]\d+[）)]']
        enumeration_count = sum(len(re.findall(pattern, content)) for pattern in enumeration_patterns)

        return {
            "paragraph_count": len(paragraphs),
            "average_paragraph_length": round(sum(len(p) for p in paragraphs) / len(paragraphs), 1) if paragraphs else 0,
            "connector_density": round(connector_count / total_chars * 1000, 2),
            "summary_usage": summary_count,
            "enumeration_usage": enumeration_count
        }
    
    def _analyze_language_habits(self, content: str) -> Dict[str, Any]:
        """分析语言习惯"""
        total_chars = len(content)

        if total_chars == 0:
            return {
                "colloquial_level": 0,
                "formal_structure_usage": 0,
                "de_structure_density": 0
            }

        # 口语化词汇
        colloquial_words = [
            "挺", "蛮", "特别", "超级", "好像", "感觉", "觉得", "应该", "可能", "大概",
            "差不多", "基本上", "一般来说", "说实话", "老实说", "坦白说", "真的", "确实"
        ]
        colloquial_count = sum(content.count(word) for word in colloquial_words)

        # 书面语结构词
        formal_structures = [
            "之", "其", "所", "乃", "即", "亦", "且", "而", "于", "以", "为", "与",
            "及", "或", "若", "则", "故", "因", "由", "自", "从", "向", "至", "及其"
        ]
        formal_count = sum(content.count(word) for word in formal_structures)

        # "的"字结构密度
        de_count = content.count('的')

        # 书面语句式
        formal_patterns = [r'[\u4e00-\u9fff]+之[\u4e00-\u9fff]+', r'所[\u4e00-\u9fff]+', r'其[\u4e00-\u9fff]+']
        formal_pattern_count = sum(len(re.findall(pattern, content)) for pattern in formal_patterns)

        return {
            "colloquial_level": round(colloquial_count / total_chars * 1000, 2),
            "formal_structure_usage": round((formal_count + formal_pattern_count) / total_chars * 1000, 2),
            "de_structure_density": round(de_count / total_chars * 1000, 2)
        }

    def _analyze_emotional_tone(self, content: str) -> Dict[str, Any]:
        """分析情感色彩"""
        total_chars = len(content)
        if total_chars == 0:
            return {"positive_ratio": 0, "negative_ratio": 0, "neutral_ratio": 1.0, "intensity": 0}

        # 积极词汇
        positive_words = ["优秀", "卓越", "成功", "进步", "提升", "改善", "创新", "突破", "发展", "增长",
                         "满意", "高兴", "喜悦", "赞扬", "表彰", "肯定", "支持", "鼓励", "希望", "信心"]

        # 消极词汇
        negative_words = ["问题", "困难", "挑战", "不足", "缺陷", "错误", "失败", "下降", "减少", "损失",
                         "担心", "忧虑", "批评", "质疑", "反对", "拒绝", "否定", "警告", "风险", "危机"]

        # 强度词汇
        intensity_words = ["非常", "极其", "特别", "十分", "相当", "很", "最", "更", "进一步", "大幅"]

        positive_count = sum(content.count(word) for word in positive_words)
        negative_count = sum(content.count(word) for word in negative_words)
        intensity_count = sum(content.count(word) for word in intensity_words)

        total_emotional = positive_count + negative_count
        if total_emotional == 0:
            return {"positive_ratio": 0, "negative_ratio": 0, "neutral_ratio": 1.0, "intensity": 0}

        return {
            "positive_ratio": round(positive_count / total_emotional, 2),
            "negative_ratio": round(negative_count / total_emotional, 2),
            "neutral_ratio": round(1 - (positive_count + negative_count) / total_emotional, 2),
            "intensity": round(intensity_count / total_chars * 1000, 2)
        }

    def _analyze_professionalism(self, content: str) -> Dict[str, Any]:
        """分析专业性特征"""
        total_chars = len(content)
        if total_chars == 0:
            return {"domain_specificity": 0, "authority_indicators": 0, "precision_level": 0}

        # 权威性指标词汇
        authority_words = ["根据", "依据", "按照", "研究表明", "数据显示", "统计", "调查", "分析",
                          "专家", "学者", "权威", "官方", "正式", "法规", "标准", "规范"]

        # 精确性指标
        precision_patterns = [r'\d+%', r'\d+\.\d+', r'第\d+', r'\d+年\d+月', r'\d+万', r'\d+亿']

        # 领域特定词汇（示例）
        domain_words = ["技术", "系统", "平台", "方案", "策略", "机制", "模式", "框架", "体系", "流程"]

        authority_count = sum(content.count(word) for word in authority_words)
        domain_count = sum(content.count(word) for word in domain_words)
        precision_count = sum(len(re.findall(pattern, content)) for pattern in precision_patterns)

        return {
            "domain_specificity": round(domain_count / total_chars * 1000, 2),
            "authority_indicators": round(authority_count / total_chars * 1000, 2),
            "precision_level": round(precision_count / total_chars * 1000, 2)
        }

    def _analyze_rhetorical_devices(self, content: str) -> Dict[str, Any]:
        """分析修辞手法"""
        total_chars = len(content)
        if total_chars == 0:
            return {"metaphor_usage": 0, "parallel_structure": 0, "question_usage": 0}

        # 比喻词汇
        metaphor_words = ["如同", "好比", "犹如", "仿佛", "像", "似", "宛如", "恰似"]

        # 排比结构模式
        parallel_patterns = [r'[\u4e00-\u9fff]+，[\u4e00-\u9fff]+，[\u4e00-\u9fff]+',
                           r'不仅[\u4e00-\u9fff]+，而且[\u4e00-\u9fff]+',
                           r'既[\u4e00-\u9fff]+，又[\u4e00-\u9fff]+']

        # 疑问句
        question_count = content.count('？') + content.count('?')

        metaphor_count = sum(content.count(word) for word in metaphor_words)
        parallel_count = sum(len(re.findall(pattern, content)) for pattern in parallel_patterns)

        return {
            "metaphor_usage": round(metaphor_count / total_chars * 1000, 2),
            "parallel_structure": round(parallel_count / total_chars * 1000, 2),
            "question_usage": round(question_count / total_chars * 1000, 2)
        }
    
    def _identify_style_type(self, content: str, features: Dict[str, Any]) -> Tuple[str, float]:
        """识别文风类型"""
        scores = {}

        # 安全获取特征值的辅助函数
        def safe_get(feature_dict: Dict, key: str, default: float = 0.0) -> float:
            return feature_dict.get(key, default) if feature_dict else default

        for style_id, style_info in self.style_types.items():
            try:
                score = 0.0

                # 基于特征模式匹配 (权重: 0.2)
                pattern_score = 0.0
                for pattern in style_info.get("typical_patterns", []):
                    if pattern in content:
                        pattern_score += 0.04  # 每个模式0.04分，最多5个模式
                score += min(pattern_score, 0.2)

                # 基于特征分析结果 (权重: 0.8)
                sentence_features = features.get("sentence_structure", {})
                vocab_features = features.get("vocabulary_choice", {})
                expression_features = features.get("expression_style", {})
                org_features = features.get("text_organization", {})
                habit_features = features.get("language_habits", {})
                emotional_features = features.get("emotional_tone", {})
                professional_features = features.get("professionalism", {})

                if style_id == "formal_official":
                    # 正式公文风格
                    score += min(safe_get(vocab_features, "formality_score") * 0.02, 0.2)  # 正式度
                    score += min(safe_get(org_features, "connector_density") * 0.01, 0.1)  # 连接词密度
                    score += min(safe_get(professional_features, "authority_indicators") * 0.02, 0.2)  # 权威性
                    score += min((1 - safe_get(habit_features, "colloquial_level") * 0.01), 0.1)  # 非口语化
                    score += min(safe_get(expression_features, "passive_active_ratio") * 0.2, 0.2)  # 被动语态

                elif style_id == "business_professional":
                    # 商务专业风格
                    score += min(safe_get(vocab_features, "action_verb_ratio") * 0.02, 0.2)  # 动作动词
                    score += min((1 - safe_get(expression_features, "passive_active_ratio")) * 0.3, 0.3)  # 主动语态
                    score += min(safe_get(professional_features, "precision_level") * 0.02, 0.1)  # 精确性
                    score += min(safe_get(emotional_features, "neutral_ratio") * 0.2, 0.2)  # 中性语调

                elif style_id == "academic_research":
                    # 学术研究风格
                    score += min(safe_get(sentence_features, "complex_ratio") * 0.4, 0.4)  # 复杂句比例
                    score += min(safe_get(vocab_features, "technical_density") * 0.05, 0.2)  # 技术密度
                    score += min(safe_get(professional_features, "authority_indicators") * 0.02, 0.2)  # 权威性

                elif style_id == "narrative_descriptive":
                    # 叙述描述风格
                    score += min(safe_get(vocab_features, "modifier_usage") * 0.02, 0.2)  # 修饰词使用
                    score += min(safe_get(habit_features, "colloquial_level") * 0.02, 0.2)  # 口语化程度
                    score += min(safe_get(emotional_features, "intensity") * 0.02, 0.2)  # 情感强度
                    score += min((safe_get(emotional_features, "positive_ratio") +
                                safe_get(emotional_features, "negative_ratio")) * 0.2, 0.2)  # 情感色彩

                elif style_id == "concise_practical":
                    # 简洁实用风格
                    avg_length = safe_get(sentence_features, "average_length", 20)
                    if avg_length < 20:
                        score += 0.3  # 短句偏好
                    else:
                        score += max(0, 0.3 - (avg_length - 20) * 0.01)

                    score += min((1 - safe_get(habit_features, "de_structure_density") * 0.001) * 0.2, 0.2)
                    score += min((1 - safe_get(vocab_features, "modifier_usage") * 0.01) * 0.2, 0.2)
                    score += min(safe_get(vocab_features, "action_verb_ratio") * 0.01, 0.1)

                scores[style_id] = min(max(score, 0.0), 1.0)  # 确保分数在0-1之间

            except Exception as e:
                print(f"计算风格 {style_id} 分数时出错: {str(e)}")
                scores[style_id] = 0.0

        # 找到得分最高的文风类型
        if not scores:
            return "business_professional", 0.5

        best_style = max(scores.items(), key=lambda x: x[1])

        # 如果最高分太低，返回默认风格
        if best_style[1] < 0.3:
            return "business_professional", best_style[1]

        return best_style[0], best_style[1]
    
    def _generate_style_prompt(self, features: Dict[str, Any], style_type: str) -> str:
        """生成文风提示词"""
        try:
            style_info = self.style_types.get(style_type, {})
            style_name = style_info.get("name", "通用风格")
            characteristics = style_info.get("characteristics", [])

            # 基础文风描述
            prompt_parts = [
                f"请按照{style_name}进行内容生成，具体要求如下：",
                "",
                "【文风特征】"
            ]

            for char in characteristics:
                prompt_parts.append(f"- {char}")

            # 根据具体特征数据生成个性化要求
            prompt_parts.extend(self._generate_sentence_requirements(features))
            prompt_parts.extend(self._generate_vocabulary_requirements(features))
            prompt_parts.extend(self._generate_expression_requirements(features))
            prompt_parts.extend(self._generate_organization_requirements(features))
            prompt_parts.extend(self._generate_tone_requirements(features))

            prompt_parts.append("")
            prompt_parts.append("【特别注意】")
            prompt_parts.append("- 避免AI生成痕迹，让内容自然流畅")
            prompt_parts.append("- 保持与原文档风格的一致性")
            prompt_parts.append("- 确保内容准确、逻辑清晰")

            # 添加负面示例和避免事项
            prompt_parts.extend(self._generate_avoidance_guidelines(features, style_type))

            return "\n".join(prompt_parts)

        except Exception as e:
            # 如果生成失败，返回基础提示词
            return f"请按照{style_info.get('name', '专业')}风格进行内容生成，保持语言规范、逻辑清晰、表达准确。"

    def _generate_sentence_requirements(self, features: Dict[str, Any]) -> List[str]:
        """生成句式要求"""
        requirements = ["", "【句式要求】"]

        sentence_features = features.get("sentence_structure", {})
        avg_length = sentence_features.get("average_length", 15)
        complex_ratio = sentence_features.get("complex_ratio", 0.5)

        # 句长要求
        if avg_length > 30:
            requirements.append("- 保持长句的使用，注重表达的完整性和逻辑层次")
            requirements.append("- 适当使用分号和破折号来组织复杂句式")
        elif avg_length > 20:
            requirements.append("- 适当使用长句，保持表达的完整性和逻辑性")
            requirements.append("- 长短句结合，避免句式过于单调")
        elif avg_length < 12:
            requirements.append("- 多使用短句，保持表达的简洁明了")
            requirements.append("- 避免冗长复杂的句式结构")
        else:
            requirements.append("- 长短句结合，保持节奏感和可读性")

        # 复杂度要求
        if complex_ratio > 0.7:
            requirements.append("- 保持句式的复杂性和层次感")
        elif complex_ratio < 0.3:
            requirements.append("- 使用简单直接的句式结构")

        return requirements

    def _generate_vocabulary_requirements(self, features: Dict[str, Any]) -> List[str]:
        """生成词汇要求"""
        requirements = ["", "【词汇要求】"]

        vocab_features = features.get("vocabulary_choice", {})
        formality = vocab_features.get("formality_score", 0)
        technical_density = vocab_features.get("technical_density", 0)
        modifier_usage = vocab_features.get("modifier_usage", 0)
        action_verb_ratio = vocab_features.get("action_verb_ratio", 0)

        # 正式度要求
        if formality > 15:
            requirements.append("- 使用正式、规范的书面语词汇")
            requirements.append("- 适当使用专业术语和学术表达")
        elif formality > 8:
            requirements.append("- 使用标准的书面语表达")
            requirements.append("- 避免过于口语化的词汇")
        else:
            requirements.append("- 使用通俗易懂的词汇")
            requirements.append("- 避免过于正式或生僻的表达")

        # 技术性要求
        if technical_density > 5:
            requirements.append("- 保持专业术语的准确使用")

        # 修饰词要求
        if modifier_usage > 10:
            requirements.append("- 适当使用形容词和副词进行修饰")
        elif modifier_usage < 3:
            requirements.append("- 减少不必要的修饰词，保持表达简洁")

        # 动词使用要求
        if action_verb_ratio > 20:
            requirements.append("- 多使用动作性强的动词")
            requirements.append("- 让表达更加生动有力")

        return requirements

    def _generate_expression_requirements(self, features: Dict[str, Any]) -> List[str]:
        """生成表达方式要求"""
        requirements = ["", "【表达方式】"]

        expression_features = features.get("expression_style", {})
        passive_ratio = expression_features.get("passive_active_ratio", 0)
        person_usage = expression_features.get("person_usage", {})

        # 语态要求
        if passive_ratio > 0.6:
            requirements.append("- 适当使用被动语态，体现客观性和正式性")
        elif passive_ratio > 0.3:
            requirements.append("- 主被动语态结合使用，保持表达的灵活性")
        else:
            requirements.append("- 优先使用主动语态，让表达更直接有力")

        # 人称使用要求
        first_person = person_usage.get("first_person", 0)
        if first_person > 5:
            requirements.append("- 可以适当使用第一人称，体现主观态度")
        elif first_person == 0:
            requirements.append("- 避免使用第一人称，保持客观中立")

        return requirements

    def _generate_organization_requirements(self, features: Dict[str, Any]) -> List[str]:
        """生成组织结构要求"""
        requirements = ["", "【组织结构】"]

        org_features = features.get("text_organization", {})
        connector_density = org_features.get("connector_density", 0)
        summary_usage = org_features.get("summary_usage", 0)

        # 连接词要求
        if connector_density > 8:
            requirements.append("- 使用丰富的逻辑连接词")
            requirements.append("- 保持段落间的逻辑关系清晰")
        elif connector_density > 3:
            requirements.append("- 适当使用逻辑连接词")
            requirements.append("- 注意段落间的过渡自然")
        else:
            requirements.append("- 减少机械化的过渡词使用")
            requirements.append("- 通过内容逻辑自然过渡")

        # 总结性表达
        if summary_usage > 2:
            requirements.append("- 适当使用总结性表达")
            requirements.append("- 注重内容的归纳和提炼")

        return requirements

    def _generate_tone_requirements(self, features: Dict[str, Any]) -> List[str]:
        """生成语调要求"""
        requirements = ["", "【语调风格】"]

        emotional_features = features.get("emotional_tone", {})
        professional_features = features.get("professionalism", {})

        positive_ratio = emotional_features.get("positive_ratio", 0)
        negative_ratio = emotional_features.get("negative_ratio", 0)
        intensity = emotional_features.get("intensity", 0)
        authority_indicators = professional_features.get("authority_indicators", 0)

        # 情感色彩要求
        if positive_ratio > 0.6:
            requirements.append("- 保持积极正面的语调")
        elif negative_ratio > 0.4:
            requirements.append("- 可以适当表达关切和问题意识")
        else:
            requirements.append("- 保持中性客观的语调")

        # 强度要求
        if intensity > 15:
            requirements.append("- 适当使用强调词汇，体现重要性")
        elif intensity < 5:
            requirements.append("- 保持平和的表达强度")

        # 权威性要求
        if authority_indicators > 10:
            requirements.append("- 体现专业权威性，使用准确的数据和引用")

        return requirements

    def _generate_avoidance_guidelines(self, features: Dict[str, Any], style_type: str) -> List[str]:
        """生成避免事项指导"""
        guidelines = ["", "【避免事项】"]

        # 根据风格类型添加特定避免事项
        if style_type == "business_professional":
            guidelines.extend([
                "- 避免过于感性或主观的表达",
                "- 避免使用网络流行语或俚语",
                "- 避免冗长的修饰和华丽的辞藻"
            ])
        elif style_type == "academic_research":
            guidelines.extend([
                "- 避免口语化表达和非正式用词",
                "- 避免主观臆断，确保论证严谨",
                "- 避免过于绝对的表述"
            ])
        elif style_type == "concise_practical":
            guidelines.extend([
                "- 避免冗余和重复表达",
                "- 避免过于复杂的句式结构",
                "- 避免不必要的修饰词汇"
            ])

        # 通用避免事项
        guidelines.extend([
            "- 避免明显的AI生成痕迹",
            "- 避免逻辑不清或前后矛盾",
            "- 避免语法错误和用词不当"
        ])

        return guidelines
    
    def _generate_template_id(self, document_name: str, features: Dict[str, Any]) -> str:
        """生成文风模板ID"""
        content = f"{document_name}_{json.dumps(features, sort_keys=True)}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
    
    def save_style_template(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """保存文风模板"""
        try:
            template_id = analysis_result.get("template_id")
            if not template_id:
                return {"error": "缺少模板ID"}
            
            # 保存到JSON文件
            template_file = os.path.join(self.storage_path, f"{template_id}.json")
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            
            # 更新模板索引
            self._update_style_template_index(template_id, analysis_result)
            
            return {
                "success": True,
                "template_id": template_id,
                "template_name": analysis_result.get("document_name", "未命名模板"),
                "style_type": analysis_result.get("style_type", "未知风格"),
                "saved_path": template_file
            }
            
        except Exception as e:
            return {"error": f"保存文风模板失败: {str(e)}"}
    
    def load_style_template(self, template_id: str) -> Dict[str, Any]:
        """加载文风模板"""
        try:
            template_file = os.path.join(self.storage_path, f"{template_id}.json")
            if not os.path.exists(template_file):
                return {"error": f"文风模板不存在: {template_id}"}
            
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            return template_data
            
        except Exception as e:
            return {"error": f"加载文风模板失败: {str(e)}"}
    
    def list_style_templates(self) -> List[Dict[str, Any]]:
        """列出所有文风模板"""
        try:
            index_file = os.path.join(self.storage_path, "style_template_index.json")
            if not os.path.exists(index_file):
                return []
            
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            return index_data.get("templates", [])
            
        except Exception as e:
            print(f"加载文风模板索引失败: {str(e)}")
            return []
    
    def _update_style_template_index(self, template_id: str, template_data: Dict[str, Any]):
        """更新文风模板索引"""
        index_file = os.path.join(self.storage_path, "style_template_index.json")
        
        # 读取现有索引
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        else:
            index_data = {"templates": []}
        
        # 更新或添加模板信息
        template_info = {
            "template_id": template_id,
            "name": template_data.get("document_name", "未命名模板"),
            "style_type": template_data.get("style_type", "未知风格"),
            "style_name": self.style_types.get(template_data.get("style_type", ""), {}).get("name", "未知风格"),
            "confidence_score": template_data.get("confidence_score", 0.0),
            "created_time": template_data.get("analysis_time", datetime.now().isoformat()),
            "description": f"文风模板：{template_data.get('document_name', '未命名文档')}"
        }
        
        # 检查是否已存在
        existing_index = -1
        for i, template in enumerate(index_data["templates"]):
            if template["template_id"] == template_id:
                existing_index = i
                break
        
        if existing_index >= 0:
            index_data["templates"][existing_index] = template_info
        else:
            index_data["templates"].append(template_info)
        
        # 保存索引
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

    def validate_style_application(self, original_content: str, generated_content: str,
                                 target_style: str, style_features: Dict[str, Any]) -> Dict[str, Any]:
        """验证风格应用效果"""
        try:
            # 分析生成内容的风格特征
            generated_features = self._analyze_style_features(generated_content)

            # 识别生成内容的风格类型
            identified_style, confidence = self._identify_style_type(generated_content, generated_features)

            # 计算风格一致性分数
            consistency_score = self._calculate_style_consistency(
                style_features, generated_features, target_style
            )

            # 计算质量指标
            quality_metrics = self._calculate_quality_metrics(
                original_content, generated_content, generated_features
            )

            # 生成改进建议
            improvement_suggestions = self._generate_improvement_suggestions(
                target_style, generated_features, consistency_score
            )

            return {
                "success": True,
                "target_style": target_style,
                "identified_style": identified_style,
                "style_confidence": confidence,
                "consistency_score": consistency_score,
                "quality_metrics": quality_metrics,
                "generated_features": generated_features,
                "improvement_suggestions": improvement_suggestions,
                "validation_time": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"风格验证失败: {str(e)}"}

    def _calculate_style_consistency(self, target_features: Dict[str, Any],
                                   generated_features: Dict[str, Any],
                                   target_style: str) -> float:
        """计算风格一致性分数"""
        try:
            total_score = 0.0
            total_weight = 0.0

            # 句式结构一致性 (权重: 0.25)
            sentence_score = self._compare_sentence_features(
                target_features.get("sentence_structure", {}),
                generated_features.get("sentence_structure", {})
            )
            total_score += sentence_score * 0.25
            total_weight += 0.25

            # 词汇选择一致性 (权重: 0.3)
            vocab_score = self._compare_vocabulary_features(
                target_features.get("vocabulary_choice", {}),
                generated_features.get("vocabulary_choice", {})
            )
            total_score += vocab_score * 0.3
            total_weight += 0.3

            # 表达方式一致性 (权重: 0.2)
            expression_score = self._compare_expression_features(
                target_features.get("expression_style", {}),
                generated_features.get("expression_style", {})
            )
            total_score += expression_score * 0.2
            total_weight += 0.2

            # 组织结构一致性 (权重: 0.15)
            org_score = self._compare_organization_features(
                target_features.get("text_organization", {}),
                generated_features.get("text_organization", {})
            )
            total_score += org_score * 0.15
            total_weight += 0.15

            # 语言习惯一致性 (权重: 0.1)
            habit_score = self._compare_habit_features(
                target_features.get("language_habits", {}),
                generated_features.get("language_habits", {})
            )
            total_score += habit_score * 0.1
            total_weight += 0.1

            return total_score / total_weight if total_weight > 0 else 0.0

        except Exception as e:
            print(f"计算风格一致性时出错: {str(e)}")
            return 0.0

    def _compare_sentence_features(self, target: Dict, generated: Dict) -> float:
        """比较句式特征"""
        score = 0.0
        comparisons = 0

        # 平均句长比较
        target_length = target.get("average_length", 15)
        generated_length = generated.get("average_length", 15)
        length_diff = abs(target_length - generated_length) / max(target_length, 1)
        score += max(0, 1 - length_diff)
        comparisons += 1

        # 复杂句比例比较
        target_complex = target.get("complex_ratio", 0.5)
        generated_complex = generated.get("complex_ratio", 0.5)
        complex_diff = abs(target_complex - generated_complex)
        score += max(0, 1 - complex_diff * 2)
        comparisons += 1

        return score / comparisons if comparisons > 0 else 0.0

    def _compare_vocabulary_features(self, target: Dict, generated: Dict) -> float:
        """比较词汇特征"""
        score = 0.0
        comparisons = 0

        # 正式度比较
        target_formality = target.get("formality_score", 0)
        generated_formality = generated.get("formality_score", 0)
        if target_formality > 0:
            formality_ratio = min(generated_formality / target_formality, target_formality / generated_formality)
            score += formality_ratio
            comparisons += 1

        # 动作动词比例比较
        target_action = target.get("action_verb_ratio", 0)
        generated_action = generated.get("action_verb_ratio", 0)
        if target_action > 0:
            action_ratio = min(generated_action / target_action, target_action / generated_action)
            score += action_ratio
            comparisons += 1

        return score / comparisons if comparisons > 0 else 0.5

    def _compare_expression_features(self, target: Dict, generated: Dict) -> float:
        """比较表达方式特征"""
        score = 0.0
        comparisons = 0

        # 被动语态比例比较
        target_passive = target.get("passive_active_ratio", 0)
        generated_passive = generated.get("passive_active_ratio", 0)
        passive_diff = abs(target_passive - generated_passive)
        score += max(0, 1 - passive_diff * 2)
        comparisons += 1

        return score / comparisons if comparisons > 0 else 0.0

    def _compare_organization_features(self, target: Dict, generated: Dict) -> float:
        """比较组织结构特征"""
        score = 0.0
        comparisons = 0

        # 连接词密度比较
        target_connector = target.get("connector_density", 0)
        generated_connector = generated.get("connector_density", 0)
        if target_connector > 0:
            connector_ratio = min(generated_connector / target_connector, target_connector / generated_connector)
            score += connector_ratio
            comparisons += 1

        return score / comparisons if comparisons > 0 else 0.5

    def _compare_habit_features(self, target: Dict, generated: Dict) -> float:
        """比较语言习惯特征"""
        score = 0.0
        comparisons = 0

        # 口语化程度比较
        target_colloquial = target.get("colloquial_level", 0)
        generated_colloquial = generated.get("colloquial_level", 0)
        colloquial_diff = abs(target_colloquial - generated_colloquial)
        score += max(0, 1 - colloquial_diff * 0.1)
        comparisons += 1

        return score / comparisons if comparisons > 0 else 0.0

    def _calculate_quality_metrics(self, original_content: str, generated_content: str,
                                 generated_features: Dict[str, Any]) -> Dict[str, Any]:
        """计算质量指标"""
        try:
            metrics = {}

            # 长度比较
            original_length = len(original_content)
            generated_length = len(generated_content)
            metrics["length_ratio"] = generated_length / original_length if original_length > 0 else 0

            # 句子数量比较
            original_sentences = generated_features.get("sentence_structure", {}).get("total_sentences", 0)
            metrics["sentence_count"] = original_sentences

            # 可读性评估（基于平均句长）
            avg_length = generated_features.get("sentence_structure", {}).get("average_length", 15)
            if 15 <= avg_length <= 25:
                metrics["readability_score"] = 1.0
            elif 10 <= avg_length < 15 or 25 < avg_length <= 35:
                metrics["readability_score"] = 0.8
            else:
                metrics["readability_score"] = 0.6

            # 词汇丰富度（基于修饰词使用）
            modifier_usage = generated_features.get("vocabulary_choice", {}).get("modifier_usage", 0)
            metrics["vocabulary_richness"] = min(modifier_usage / 10, 1.0)

            # 专业性评估
            professionalism = generated_features.get("professionalism", {})
            authority_score = professionalism.get("authority_indicators", 0)
            precision_score = professionalism.get("precision_level", 0)
            metrics["professionalism_score"] = min((authority_score + precision_score) / 20, 1.0)

            return metrics

        except Exception as e:
            print(f"计算质量指标时出错: {str(e)}")
            return {"error": str(e)}

    def _generate_improvement_suggestions(self, target_style: str, generated_features: Dict[str, Any],
                                        consistency_score: float) -> List[str]:
        """生成改进建议"""
        suggestions = []

        try:
            # 基于一致性分数给出总体建议
            if consistency_score < 0.6:
                suggestions.append("整体风格一致性较低，建议重新调整生成策略")
            elif consistency_score < 0.8:
                suggestions.append("风格基本符合要求，但仍有改进空间")
            else:
                suggestions.append("风格一致性良好，符合目标要求")

            # 基于具体特征给出建议
            sentence_features = generated_features.get("sentence_structure", {})
            vocab_features = generated_features.get("vocabulary_choice", {})
            expression_features = generated_features.get("expression_style", {})

            # 句式建议
            avg_length = sentence_features.get("average_length", 15)
            if target_style == "concise_practical" and avg_length > 20:
                suggestions.append("句子偏长，建议使用更简洁的表达")
            elif target_style == "academic_research" and avg_length < 20:
                suggestions.append("句子偏短，建议增加句式的复杂性和完整性")

            # 词汇建议
            formality = vocab_features.get("formality_score", 0)
            if target_style == "formal_official" and formality < 10:
                suggestions.append("正式度不够，建议使用更规范的书面语")
            elif target_style == "narrative_descriptive" and formality > 15:
                suggestions.append("过于正式，建议使用更生动自然的表达")

            # 语态建议
            passive_ratio = expression_features.get("passive_active_ratio", 0)
            if target_style == "business_professional" and passive_ratio > 0.4:
                suggestions.append("被动语态使用过多，建议多用主动语态")

            # 如果没有具体建议，给出通用建议
            if len(suggestions) <= 1:
                suggestions.append("继续保持当前的写作风格")
                suggestions.append("注意语言的准确性和逻辑性")

        except Exception as e:
            suggestions = [f"生成改进建议时出错: {str(e)}"]

        return suggestions
