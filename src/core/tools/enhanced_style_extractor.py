#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Style Extractor - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import re
import json
import os
import math
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime
from collections import Counter, defaultdict
import numpy as np

try:
    import jieba
    import jieba.posseg as pseg
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.decomposition import PCA
    from sklearn.metrics.pairwise import cosine_similarity
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("Warning: Some dependencies not available. Install jieba, scikit-learn for full functionality.")


class QuantitativeFeatureExtractor:
    """量化特征提取器 - 使用开源库进行精确计算"""
    
    def __init__(self):
        self.punctuation_marks = ['。', '！', '？', '；', '：', '，', '、', '"', '"', ''', ''', '（', '）', '【', '】']
        self.function_words = ['的', '了', '是', '在', '有', '和', '与', '或', '但', '而', '因为', '所以', '如果', '那么']
        self.formal_words = ['根据', '按照', '依据', '鉴于', '基于', '关于', '针对', '就', '对于', '至于']
        self.informal_words = ['挺', '蛮', '特别', '非常', '超级', '巨', '贼', '老', '可', '真']
        
    def extract_lexical_features(self, text: str) -> Dict[str, Any]:
        """提取词汇特征"""
        if not DEPENDENCIES_AVAILABLE:
            return {"error": "Dependencies not available"}
            
        # 分词和词性标注
        words = list(jieba.cut(text))
        pos_tags = list(pseg.cut(text))
        
        # 基础统计
        total_chars = len(text)
        total_words = len(words)
        unique_words = len(set(words))
        
        # 词汇丰富度指标
        ttr = unique_words / total_words if total_words > 0 else 0  # Type-Token Ratio
        
        # 词性分布
        pos_counter = Counter([tag.flag for tag in pos_tags])
        total_pos = sum(pos_counter.values())
        pos_ratios = {pos: count/total_pos for pos, count in pos_counter.items()}
        
        # 词长分布
        word_lengths = [len(word) for word in words if len(word) > 0]
        avg_word_length = np.mean(word_lengths) if word_lengths else 0
        
        # 特定词汇统计
        formal_count = sum(1 for word in words if word in self.formal_words)
        informal_count = sum(1 for word in words if word in self.informal_words)
        function_word_count = sum(1 for word in words if word in self.function_words)
        
        return {
            "total_chars": total_chars,
            "total_words": total_words,
            "unique_words": unique_words,
            "ttr": round(ttr, 4),
            "avg_word_length": round(avg_word_length, 2),
            "pos_ratios": pos_ratios,
            "formal_word_density": round(formal_count / total_words * 1000, 2),
            "informal_word_density": round(informal_count / total_words * 1000, 2),
            "function_word_density": round(function_word_count / total_words * 1000, 2)
        }
    
    def extract_syntactic_features(self, text: str) -> Dict[str, Any]:
        """提取句法特征"""
        # 句子分割
        sentences = re.split(r'[。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {"error": "No sentences found"}
        
        # 句长统计
        sentence_lengths = [len(s) for s in sentences]
        avg_sentence_length = np.mean(sentence_lengths)
        sentence_length_std = np.std(sentence_lengths)
        
        # 长短句比例
        short_sentences = sum(1 for length in sentence_lengths if length <= 10)
        medium_sentences = sum(1 for length in sentence_lengths if 10 < length <= 25)
        long_sentences = sum(1 for length in sentence_lengths if length > 25)
        total_sentences = len(sentences)
        
        # 复合句识别
        compound_patterns = [r'，.*，', r'；.*；', r'：.*：']
        compound_count = 0
        for sentence in sentences:
            for pattern in compound_patterns:
                if re.search(pattern, sentence):
                    compound_count += 1
                    break
        
        # 并列句识别
        parallel_patterns = [r'不仅.*而且', r'既.*又', r'一方面.*另一方面', r'或者.*或者']
        parallel_count = sum(1 for sentence in sentences 
                           for pattern in parallel_patterns 
                           if re.search(pattern, sentence))
        
        return {
            "total_sentences": total_sentences,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "sentence_length_std": round(sentence_length_std, 2),
            "short_sentence_ratio": round(short_sentences / total_sentences, 3),
            "medium_sentence_ratio": round(medium_sentences / total_sentences, 3),
            "long_sentence_ratio": round(long_sentences / total_sentences, 3),
            "compound_sentence_ratio": round(compound_count / total_sentences, 3),
            "parallel_sentence_ratio": round(parallel_count / total_sentences, 3)
        }
    
    def extract_punctuation_features(self, text: str) -> Dict[str, Any]:
        """提取标点符号特征"""
        total_chars = len(text)
        if total_chars == 0:
            return {"error": "Empty text"}
        
        # 标点符号统计
        punct_counter = Counter()
        for char in text:
            if char in self.punctuation_marks:
                punct_counter[char] += 1
        
        total_punct = sum(punct_counter.values())
        punct_density = total_punct / total_chars * 100
        
        # 特定标点使用
        question_marks = punct_counter.get('？', 0)
        exclamation_marks = punct_counter.get('！', 0)
        periods = punct_counter.get('。', 0)
        commas = punct_counter.get('，', 0)
        
        return {
            "total_punctuation": total_punct,
            "punctuation_density": round(punct_density, 2),
            "question_mark_count": question_marks,
            "exclamation_mark_count": exclamation_marks,
            "period_count": periods,
            "comma_count": commas,
            "punctuation_distribution": dict(punct_counter)
        }
    
    def extract_all_quantitative_features(self, text: str) -> Dict[str, Any]:
        """提取所有量化特征"""
        features = {
            "extraction_time": datetime.now().isoformat(),
            "text_length": len(text)
        }
        
        try:
            features["lexical_features"] = self.extract_lexical_features(text)
            features["syntactic_features"] = self.extract_syntactic_features(text)
            features["punctuation_features"] = self.extract_punctuation_features(text)
            features["extraction_success"] = True
        except Exception as e:
            features["extraction_success"] = False
            features["error"] = str(e)
        
        return features


class LLMStyleAnalyzer:
    """LLM文风分析器 - 利用LLM进行深度风格分析"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.style_dimensions = [
            "词汇风格", "句子结构风格", "语气情感风格", "正式程度", "专业性", "创新性"
        ]
        
    def generate_style_evaluation_prompt(self, text: str, dimension: str) -> str:
        """生成风格评估提示词"""
        prompts = {
            "词汇风格": f"""请评估以下文本的词汇使用风格，从1（非常平淡）到5（非常丰富且有特色）进行评分，并简要说明理由：

文本：{text[:500]}...

请按以下格式回答：
评分：[1-5]
理由：[简要说明词汇特点，如是否使用生僻词、成语、网络语等]""",
            
            "句子结构风格": f"""请评估以下文本的句子结构风格，从1（非常简单单调）到5（非常复杂且富有变化）进行评分：

文本：{text[:500]}...

请按以下格式回答：
评分：[1-5]
理由：[说明句式结构特点，如长短句结合、从句使用等]""",
            
            "语气情感风格": f"""请评估以下文本的语气和情感表达风格，从1（非常平淡、客观）到5（非常强烈、主观、富有情感）进行评分：

文本：{text[:500]}...

请按以下格式回答：
评分：[1-5]
理由：[说明语气和情感特点]""",
            
            "正式程度": f"""请评估以下文本的正式程度，从1（非常非正式）到5（非常正式）进行评分：

文本：{text[:500]}...

请按以下格式回答：
评分：[1-5]
理由：[说明正式程度的判断依据]""",
            
            "专业性": f"""请评估以下文本的专业性程度，从1（通俗易懂）到5（高度专业）进行评分：

文本：{text[:500]}...

请按以下格式回答：
评分：[1-5]
理由：[说明专业性判断依据，如专业术语使用等]""",
            
            "创新性": f"""请评估以下文本的表达创新性，从1（传统常见）到5（新颖独特）进行评分：

文本：{text[:500]}...

请按以下格式回答：
评分：[1-5]
理由：[说明创新性体现]"""
        }
        
        return prompts.get(dimension, "")
    
    def parse_llm_evaluation(self, response: str) -> Tuple[float, str]:
        """解析LLM评估结果"""
        try:
            lines = response.strip().split('\n')
            score = 0.0
            reason = ""
            
            for line in lines:
                if line.startswith('评分：') or line.startswith('评分:'):
                    score_text = line.split('：')[-1].split(':')[-1].strip()
                    score = float(re.findall(r'\d+', score_text)[0])
                elif line.startswith('理由：') or line.startswith('理由:'):
                    reason = line.split('：')[-1].split(':')[-1].strip()
            
            return score, reason
        except:
            return 3.0, "解析失败"
    
    def analyze_with_llm(self, text: str) -> Dict[str, Any]:
        """使用LLM进行文风分析"""
        if not self.llm_client:
            return {"error": "LLM client not available"}
        
        results = {
            "analysis_time": datetime.now().isoformat(),
            "evaluations": {},
            "overall_style_profile": {}
        }
        
        # 对每个维度进行评估
        for dimension in self.style_dimensions:
            try:
                prompt = self.generate_style_evaluation_prompt(text, dimension)
                response = self.llm_client.generate(prompt)
                score, reason = self.parse_llm_evaluation(response)
                
                results["evaluations"][dimension] = {
                    "score": score,
                    "reason": reason,
                    "raw_response": response
                }
            except Exception as e:
                results["evaluations"][dimension] = {
                    "score": 3.0,
                    "reason": f"评估失败: {str(e)}",
                    "error": True
                }
        
        # 计算整体风格档案
        scores = [eval_data["score"] for eval_data in results["evaluations"].values() 
                 if not eval_data.get("error", False)]
        
        if scores:
            results["overall_style_profile"] = {
                "average_score": round(np.mean(scores), 2),
                "score_std": round(np.std(scores), 2),
                "dominant_characteristics": self._identify_dominant_characteristics(results["evaluations"])
            }
        
        return results
    
    def _identify_dominant_characteristics(self, evaluations: Dict[str, Any]) -> List[str]:
        """识别主导特征"""
        characteristics = []
        
        for dimension, eval_data in evaluations.items():
            if eval_data.get("error"):
                continue
                
            score = eval_data["score"]
            if score >= 4.0:
                characteristics.append(f"高{dimension}")
            elif score <= 2.0:
                characteristics.append(f"低{dimension}")
        
        return characteristics


class EnhancedStyleExtractor:
    """增强文风特征提取器 - 整合量化和LLM分析"""
    
    def __init__(self, llm_client=None, storage_path: str = "src/core/knowledge_base/style_features"):
        self.quantitative_extractor = QuantitativeFeatureExtractor()
        self.llm_analyzer = LLMStyleAnalyzer(llm_client)
        self.storage_path = storage_path
        
        # 确保存储目录存在
        os.makedirs(storage_path, exist_ok=True)
    
    def extract_comprehensive_features(self, text: str, document_name: str = None) -> Dict[str, Any]:
        """提取综合文风特征"""
        result = {
            "document_name": document_name or "未命名文档",
            "extraction_time": datetime.now().isoformat(),
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "quantitative_features": {},
            "llm_features": {},
            "integrated_features": {},
            "feature_vector": [],
            "extraction_summary": {}
        }
        
        try:
            # 提取量化特征
            print("正在提取量化特征...")
            result["quantitative_features"] = self.quantitative_extractor.extract_all_quantitative_features(text)
            
            # 提取LLM特征
            print("正在进行LLM分析...")
            result["llm_features"] = self.llm_analyzer.analyze_with_llm(text)
            
            # 整合特征
            result["integrated_features"] = self._integrate_features(
                result["quantitative_features"], 
                result["llm_features"]
            )
            
            # 生成特征向量
            result["feature_vector"] = self._generate_feature_vector(result["integrated_features"])
            
            # 生成提取摘要
            result["extraction_summary"] = self._generate_extraction_summary(result)
            
            result["success"] = True
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    def _integrate_features(self, quantitative_features: Dict, llm_features: Dict) -> Dict[str, Any]:
        """整合量化特征和LLM特征"""
        integrated = {
            "integration_time": datetime.now().isoformat(),
            "feature_categories": {}
        }
        
        # 整合词汇特征
        lexical_features = quantitative_features.get("lexical_features", {})
        llm_evaluations = llm_features.get("evaluations", {})
        
        integrated["feature_categories"]["lexical"] = {
            "ttr": lexical_features.get("ttr", 0),
            "avg_word_length": lexical_features.get("avg_word_length", 0),
            "formal_density": lexical_features.get("formal_word_density", 0),
            "llm_vocabulary_score": llm_evaluations.get("词汇风格", {}).get("score", 3.0)
        }
        
        # 整合句法特征
        syntactic_features = quantitative_features.get("syntactic_features", {})
        integrated["feature_categories"]["syntactic"] = {
            "avg_sentence_length": syntactic_features.get("avg_sentence_length", 0),
            "sentence_variety": syntactic_features.get("sentence_length_std", 0),
            "complex_sentence_ratio": syntactic_features.get("compound_sentence_ratio", 0),
            "llm_structure_score": llm_evaluations.get("句子结构风格", {}).get("score", 3.0)
        }
        
        # 整合风格特征
        integrated["feature_categories"]["style"] = {
            "formality_score": llm_evaluations.get("正式程度", {}).get("score", 3.0),
            "professionalism_score": llm_evaluations.get("专业性", {}).get("score", 3.0),
            "emotional_intensity": llm_evaluations.get("语气情感风格", {}).get("score", 3.0),
            "creativity_score": llm_evaluations.get("创新性", {}).get("score", 3.0)
        }
        
        return integrated
    
    def _generate_feature_vector(self, integrated_features: Dict) -> List[float]:
        """生成特征向量"""
        vector = []
        
        for category, features in integrated_features.get("feature_categories", {}).items():
            for feature_name, value in features.items():
                if isinstance(value, (int, float)):
                    vector.append(float(value))
        
        return vector
    
    def _generate_extraction_summary(self, result: Dict) -> Dict[str, Any]:
        """生成提取摘要"""
        summary = {
            "total_features_extracted": 0,
            "quantitative_success": result["quantitative_features"].get("extraction_success", False),
            "llm_analysis_success": "evaluations" in result["llm_features"],
            "feature_vector_length": len(result["feature_vector"]),
            "key_characteristics": []
        }
        
        # 统计特征数量
        if result["quantitative_features"].get("extraction_success"):
            summary["total_features_extracted"] += len(result["quantitative_features"].get("lexical_features", {}))
            summary["total_features_extracted"] += len(result["quantitative_features"].get("syntactic_features", {}))
            summary["total_features_extracted"] += len(result["quantitative_features"].get("punctuation_features", {}))
        
        if "evaluations" in result["llm_features"]:
            summary["total_features_extracted"] += len(result["llm_features"]["evaluations"])
        
        # 识别关键特征
        llm_profile = result["llm_features"].get("overall_style_profile", {})
        if "dominant_characteristics" in llm_profile:
            summary["key_characteristics"] = llm_profile["dominant_characteristics"]
        
        return summary
    
    def save_features(self, features: Dict[str, Any], filename: str = None) -> str:
        """保存特征到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            doc_name = features.get("document_name", "unknown").replace(" ", "_")
            filename = f"style_features_{doc_name}_{timestamp}.json"
        
        filepath = os.path.join(self.storage_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(features, f, ensure_ascii=False, indent=2)
            return filepath
        except Exception as e:
            return f"保存失败: {str(e)}"
