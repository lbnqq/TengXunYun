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
        features = {}
        
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
        
        return features
    
    def _analyze_sentence_structure(self, content: str) -> Dict[str, Any]:
        """分析句式结构"""
        sentences = re.split(r'[。！？；]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {"average_length": 0, "long_short_ratio": 0, "complex_ratio": 0}
        
        # 计算平均句长
        total_chars = sum(len(s) for s in sentences)
        average_length = total_chars / len(sentences)
        
        # 长短句比例（长句定义为超过20字）
        long_sentences = [s for s in sentences if len(s) > 20]
        long_short_ratio = len(long_sentences) / len(sentences)
        
        # 复合句比例（包含逗号、分号等的句子）
        complex_sentences = [s for s in sentences if '，' in s or '；' in s or '：' in s]
        complex_ratio = len(complex_sentences) / len(sentences)
        
        return {
            "average_length": round(average_length, 2),
            "long_short_ratio": round(long_short_ratio, 2),
            "complex_ratio": round(complex_ratio, 2),
            "total_sentences": len(sentences)
        }
    
    def _analyze_vocabulary_choice(self, content: str) -> Dict[str, Any]:
        """分析词汇选择"""
        # 正式词汇模式
        formal_words = ["根据", "按照", "依据", "鉴于", "基于", "关于", "针对", "为了", "通过", "采用"]
        formal_count = sum(content.count(word) for word in formal_words)
        
        # 专业术语模式（简单检测）
        technical_patterns = [r'\w+系统', r'\w+技术', r'\w+方案', r'\w+标准', r'\w+规范']
        technical_count = sum(len(re.findall(pattern, content)) for pattern in technical_patterns)
        
        # 修饰词使用
        modifiers = ["很", "非常", "特别", "极其", "相当", "比较", "较为", "十分"]
        modifier_count = sum(content.count(word) for word in modifiers)
        
        # 动词类型（动作动词 vs 状态动词）
        action_verbs = ["实施", "执行", "开展", "推进", "落实", "完成", "达成", "实现"]
        action_count = sum(content.count(word) for word in action_verbs)
        
        total_chars = len(content)
        
        return {
            "formality_score": round((formal_count / total_chars * 1000), 2) if total_chars > 0 else 0,
            "technical_density": round((technical_count / total_chars * 1000), 2) if total_chars > 0 else 0,
            "modifier_usage": round((modifier_count / total_chars * 1000), 2) if total_chars > 0 else 0,
            "action_verb_ratio": round((action_count / total_chars * 1000), 2) if total_chars > 0 else 0
        }
    
    def _analyze_expression_style(self, content: str) -> Dict[str, Any]:
        """分析表达方式"""
        # 被动语态检测
        passive_patterns = [r'\w+被\w+', r'\w+受到\w+', r'\w+得到\w+', r'\w+获得\w+']
        passive_count = sum(len(re.findall(pattern, content)) for pattern in passive_patterns)
        
        # 主动语态检测
        active_patterns = [r'\w+进行\w+', r'\w+开展\w+', r'\w+实施\w+', r'\w+推进\w+']
        active_count = sum(len(re.findall(pattern, content)) for pattern in active_patterns)
        
        # 人称使用
        first_person = content.count('我') + content.count('我们')
        second_person = content.count('你') + content.count('您') + content.count('你们')
        third_person = content.count('他') + content.count('她') + content.count('它') + content.count('他们')
        
        # 语气强度
        strong_tone = content.count('必须') + content.count('务必') + content.count('严禁') + content.count('绝对')
        mild_tone = content.count('建议') + content.count('希望') + content.count('可以') + content.count('尽量')
        
        total_chars = len(content)
        
        return {
            "passive_active_ratio": round(passive_count / (active_count + 1), 2),
            "person_usage": {
                "first_person": first_person,
                "second_person": second_person, 
                "third_person": third_person
            },
            "tone_strength": round((strong_tone - mild_tone) / total_chars * 1000, 2) if total_chars > 0 else 0
        }
    
    def _analyze_text_organization(self, content: str) -> Dict[str, Any]:
        """分析文本组织"""
        paragraphs = content.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # 逻辑连接词
        connectors = ["首先", "其次", "然后", "最后", "因此", "所以", "但是", "然而", "此外", "另外"]
        connector_count = sum(content.count(word) for word in connectors)
        
        # 总结性表达
        summary_words = ["总之", "综上", "总的来说", "综合以上", "总而言之"]
        summary_count = sum(content.count(word) for word in summary_words)
        
        return {
            "paragraph_count": len(paragraphs),
            "average_paragraph_length": round(sum(len(p) for p in paragraphs) / len(paragraphs), 2) if paragraphs else 0,
            "connector_density": round(connector_count / len(content) * 1000, 2) if content else 0,
            "summary_usage": summary_count
        }
    
    def _analyze_language_habits(self, content: str) -> Dict[str, Any]:
        """分析语言习惯"""
        # 口语化程度
        colloquial_words = ["挺", "蛮", "特别", "超级", "好像", "感觉", "觉得"]
        colloquial_count = sum(content.count(word) for word in colloquial_words)
        
        # 书面语规范
        formal_structures = ["之", "其", "所", "乃", "即", "亦", "且", "而"]
        formal_count = sum(content.count(word) for word in formal_structures)
        
        # "的"字结构使用频率
        de_count = content.count('的')
        
        total_chars = len(content)
        
        return {
            "colloquial_level": round(colloquial_count / total_chars * 1000, 2) if total_chars > 0 else 0,
            "formal_structure_usage": round(formal_count / total_chars * 1000, 2) if total_chars > 0 else 0,
            "de_structure_density": round(de_count / total_chars * 1000, 2) if total_chars > 0 else 0
        }
    
    def _identify_style_type(self, content: str, features: Dict[str, Any]) -> Tuple[str, float]:
        """识别文风类型"""
        scores = {}
        
        for style_id, style_info in self.style_types.items():
            score = 0.0
            
            # 基于特征模式匹配
            for pattern in style_info["typical_patterns"]:
                if pattern in content:
                    score += 0.2
            
            # 基于特征分析结果
            if style_id == "formal_official":
                score += features["vocabulary_choice"]["formality_score"] * 0.1
                score += features["text_organization"]["connector_density"] * 0.05
            elif style_id == "business_professional":
                score += features["vocabulary_choice"]["action_verb_ratio"] * 0.1
                score += (1 - features["expression_style"]["passive_active_ratio"]) * 0.3
            elif style_id == "academic_research":
                score += features["sentence_structure"]["complex_ratio"] * 0.4
                score += features["vocabulary_choice"]["technical_density"] * 0.1
            elif style_id == "narrative_descriptive":
                score += features["vocabulary_choice"]["modifier_usage"] * 0.2
                score += features["language_habits"]["colloquial_level"] * 0.1
            elif style_id == "concise_practical":
                score += (1 - features["sentence_structure"]["long_short_ratio"]) * 0.3
                score += (1 - features["language_habits"]["de_structure_density"] * 0.001) * 0.2
            
            scores[style_id] = min(score, 1.0)
        
        # 找到得分最高的文风类型
        best_style = max(scores.items(), key=lambda x: x[1])
        return best_style[0], best_style[1]
    
    def _generate_style_prompt(self, features: Dict[str, Any], style_type: str) -> str:
        """生成文风提示词"""
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
        
        prompt_parts.append("")
        prompt_parts.append("【句式要求】")
        
        # 根据分析结果生成具体要求
        sentence_features = features.get("sentence_structure", {})
        avg_length = sentence_features.get("average_length", 15)
        
        if avg_length > 25:
            prompt_parts.append("- 适当使用长句，保持表达的完整性和逻辑性")
        elif avg_length < 15:
            prompt_parts.append("- 多使用短句，保持表达的简洁明了")
        else:
            prompt_parts.append("- 长短句结合，保持节奏感和可读性")
        
        # 语态要求
        expression_features = features.get("expression_style", {})
        passive_ratio = expression_features.get("passive_active_ratio", 0)
        
        if passive_ratio > 0.5:
            prompt_parts.append("- 适当使用被动语态，体现客观性")
        else:
            prompt_parts.append("- 优先使用主动语态，让表达更直接有力")
        
        prompt_parts.append("")
        prompt_parts.append("【词汇要求】")
        
        # 词汇选择要求
        vocab_features = features.get("vocabulary_choice", {})
        formality = vocab_features.get("formality_score", 0)
        
        if formality > 10:
            prompt_parts.append("- 使用正式、规范的词汇")
            prompt_parts.append("- 适当使用专业术语和书面语表达")
        else:
            prompt_parts.append("- 使用通俗易懂的词汇")
            prompt_parts.append("- 避免过于正式或生僻的表达")
        
        prompt_parts.append("")
        prompt_parts.append("【组织结构】")
        
        # 文本组织要求
        org_features = features.get("text_organization", {})
        connector_density = org_features.get("connector_density", 0)
        
        if connector_density > 5:
            prompt_parts.append("- 使用适当的逻辑连接词")
            prompt_parts.append("- 保持段落间的逻辑关系清晰")
        else:
            prompt_parts.append("- 减少机械化的过渡词使用")
            prompt_parts.append("- 通过内容逻辑自然过渡")
        
        prompt_parts.append("")
        prompt_parts.append("【特别注意】")
        prompt_parts.append("- 避免AI生成痕迹，让内容自然流畅")
        prompt_parts.append("- 保持与原文档风格的一致性")
        prompt_parts.append("- 确保内容准确、逻辑清晰")
        
        return "\n".join(prompt_parts)
    
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
