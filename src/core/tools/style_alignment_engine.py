#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Style Alignment Engine - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import json
import os
import math
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Some features will be limited.")


class StyleSimilarityCalculator:
    """文风相似度计算器"""
    
    def __init__(self):
        self.similarity_methods = ["cosine", "euclidean", "manhattan", "weighted"]
    
    def calculate_similarity(self, features1: List[float], features2: List[float], 
                           method: str = "cosine", weights: List[float] = None) -> Dict[str, Any]:
        """
        计算两个特征向量的相似度
        
        Args:
            features1: 第一个特征向量
            features2: 第二个特征向量
            method: 相似度计算方法
            weights: 特征权重（用于加权计算）
        """
        result = {
            "calculation_time": datetime.now().isoformat(),
            "method": method,
            "similarity_score": 0.0,
            "distance": 0.0,
            "feature_comparison": {},
            "success": False
        }
        
        try:
            if not features1 or not features2:
                raise ValueError("Empty feature vectors")
            
            if len(features1) != len(features2):
                raise ValueError("Feature vectors must have the same length")
            
            # 转换为numpy数组
            vec1 = np.array(features1)
            vec2 = np.array(features2)
            
            if method == "cosine":
                similarity = self._cosine_similarity(vec1, vec2)
                distance = 1 - similarity
            elif method == "euclidean":
                distance = self._euclidean_distance(vec1, vec2)
                similarity = 1 / (1 + distance)  # 转换为相似度
            elif method == "manhattan":
                distance = self._manhattan_distance(vec1, vec2)
                similarity = 1 / (1 + distance)
            elif method == "weighted":
                if weights is None:
                    weights = [1.0] * len(features1)
                similarity, distance = self._weighted_similarity(vec1, vec2, weights)
            else:
                raise ValueError(f"Unknown similarity method: {method}")
            
            result.update({
                "similarity_score": float(similarity),
                "distance": float(distance),
                "feature_comparison": self._compare_features(vec1, vec2),
                "success": True
            })
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        if SKLEARN_AVAILABLE:
            return cosine_similarity([vec1], [vec2])[0][0]
        else:
            # 手动计算余弦相似度
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot_product / (norm1 * norm2)
    
    def _euclidean_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算欧氏距离"""
        if SKLEARN_AVAILABLE:
            return euclidean_distances([vec1], [vec2])[0][0]
        else:
            return np.sqrt(np.sum((vec1 - vec2) ** 2))
    
    def _manhattan_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算曼哈顿距离"""
        return np.sum(np.abs(vec1 - vec2))
    
    def _weighted_similarity(self, vec1: np.ndarray, vec2: np.ndarray, 
                           weights: List[float]) -> Tuple[float, float]:
        """计算加权相似度"""
        weights = np.array(weights)
        
        # 加权欧氏距离
        weighted_diff = weights * (vec1 - vec2) ** 2
        weighted_distance = np.sqrt(np.sum(weighted_diff))
        
        # 转换为相似度
        similarity = 1 / (1 + weighted_distance)
        
        return similarity, weighted_distance
    
    def _compare_features(self, vec1: np.ndarray, vec2: np.ndarray) -> Dict[str, Any]:
        """比较特征向量的详细信息"""
        return {
            "mean_difference": float(np.mean(np.abs(vec1 - vec2))),
            "max_difference": float(np.max(np.abs(vec1 - vec2))),
            "correlation": float(np.corrcoef(vec1, vec2)[0, 1]) if len(vec1) > 1 else 0.0,
            "feature_count": len(vec1)
        }


class StyleTransferEngine:
    """文风迁移引擎"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.transfer_strategies = ["direct", "gradual", "selective"]
    
    def generate_style_transfer_prompt(self, source_text: str, target_style_features: Dict[str, Any], 
                                     content_to_rewrite: str, strategy: str = "direct") -> str:
        """生成文风迁移提示词"""
        
        # 解析目标风格特征
        style_description = self._features_to_description(target_style_features)
        
        if strategy == "direct":
            return self._direct_transfer_prompt(source_text, style_description, content_to_rewrite)
        elif strategy == "gradual":
            return self._gradual_transfer_prompt(source_text, style_description, content_to_rewrite)
        elif strategy == "selective":
            return self._selective_transfer_prompt(source_text, style_description, content_to_rewrite)
        else:
            raise ValueError(f"Unknown transfer strategy: {strategy}")
    
    def _features_to_description(self, features: Dict[str, Any]) -> str:
        """将特征转换为文字描述"""
        descriptions = []
        
        # 处理LLM特征
        if "llm_features" in features:
            evaluations = features["llm_features"].get("evaluations", {})
            for dimension, eval_data in evaluations.items():
                if isinstance(eval_data, dict) and "score" in eval_data:
                    score = eval_data["score"]
                    reason = eval_data.get("reason", "")
                    if score >= 4:
                        descriptions.append(f"高{dimension}（{reason}）")
                    elif score <= 2:
                        descriptions.append(f"低{dimension}（{reason}）")
        
        # 处理量化特征
        if "quantitative_features" in features:
            quant = features["quantitative_features"]
            lexical = quant.get("lexical_features", {})
            syntactic = quant.get("syntactic_features", {})
            
            if lexical.get("ttr", 0) > 0.7:
                descriptions.append("词汇丰富多样")
            if syntactic.get("avg_sentence_length", 0) > 20:
                descriptions.append("句子较长，结构复杂")
            elif syntactic.get("avg_sentence_length", 0) < 10:
                descriptions.append("句子简短，表达简洁")
        
        return "；".join(descriptions) if descriptions else "标准文风"
    
    def _direct_transfer_prompt(self, source_text: str, style_description: str, content: str) -> str:
        """直接迁移提示词"""
        return f"""请将以下内容改写为指定的文风风格。

参考文本（目标风格）：
{source_text[:500]}...

目标风格特征：
{style_description}

需要改写的内容：
{content}

改写要求：
1. 保持原文的核心信息和逻辑结构不变
2. 调整词汇选择，使其符合目标风格的用词习惯
3. 调整句式结构，保持与目标风格的一致性
4. 调整语气和表达方式，匹配目标风格的情感色彩
5. 确保改写后的文本自然流畅，符合中文表达习惯

请提供改写结果："""
    
    def _gradual_transfer_prompt(self, source_text: str, style_description: str, content: str) -> str:
        """渐进式迁移提示词"""
        return f"""请分步骤将以下内容逐步调整为目标文风。

参考文本：{source_text[:300]}...
目标风格：{style_description}
原始内容：{content}

请按以下步骤进行调整：

步骤1 - 词汇调整：
[调整用词，替换不符合目标风格的词汇]

步骤2 - 句式调整：
[调整句子结构，使其符合目标风格]

步骤3 - 语气调整：
[调整语气和表达方式]

最终结果：
[提供最终的完整改写文本]"""
    
    def _selective_transfer_prompt(self, source_text: str, style_description: str, content: str) -> str:
        """选择性迁移提示词"""
        return f"""请选择性地调整以下内容的文风，重点关注最需要改进的方面。

参考文本：{source_text[:300]}...
目标风格：{style_description}
原始内容：{content}

请分析并选择性调整：

需要重点调整的方面：
[识别最需要调整的1-2个方面，如词汇正式度、句式复杂度等]

调整策略：
[说明具体的调整策略]

改写结果：
[提供改写后的文本]

保持不变的方面：
[说明哪些方面保持原样，以及原因]"""
    
    def perform_style_transfer(self, source_features: Dict[str, Any], 
                             target_features: Dict[str, Any],
                             content_to_rewrite: str,
                             strategy: str = "direct") -> Dict[str, Any]:
        """执行文风迁移"""
        if not self.llm_client:
            return {"error": "LLM client not available"}
        
        result = {
            "transfer_time": datetime.now().isoformat(),
            "strategy": strategy,
            "original_content": content_to_rewrite,
            "rewritten_content": "",
            "transfer_analysis": {},
            "success": False
        }
        
        try:
            # 生成迁移提示词
            source_text = source_features.get("text_preview", "")
            prompt = self.generate_style_transfer_prompt(
                source_text, target_features, content_to_rewrite, strategy
            )
            
            # 调用LLM进行文风迁移
            response = self.llm_client.generate(prompt)
            
            # 解析响应
            rewritten_content = self._extract_rewritten_content(response)
            
            result.update({
                "rewritten_content": rewritten_content,
                "raw_llm_response": response,
                "transfer_analysis": self._analyze_transfer_result(
                    content_to_rewrite, rewritten_content
                ),
                "success": True
            })
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _extract_rewritten_content(self, llm_response: str) -> str:
        """从LLM响应中提取改写内容"""
        # 寻找改写结果的标识
        markers = ["改写结果：", "最终结果：", "重写结果：", "改写后："]
        
        for marker in markers:
            if marker in llm_response:
                parts = llm_response.split(marker, 1)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # 如果没有找到标识，返回整个响应
        return llm_response.strip()
    
    def _analyze_transfer_result(self, original: str, rewritten: str) -> Dict[str, Any]:
        """分析迁移结果"""
        return {
            "original_length": len(original),
            "rewritten_length": len(rewritten),
            "length_change_ratio": len(rewritten) / len(original) if len(original) > 0 else 0,
            "word_overlap": self._calculate_word_overlap(original, rewritten),
            "structure_similarity": self._estimate_structure_similarity(original, rewritten)
        }
    
    def _calculate_word_overlap(self, text1: str, text2: str) -> float:
        """计算词汇重叠度"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _estimate_structure_similarity(self, text1: str, text2: str) -> float:
        """估算结构相似度"""
        # 简单的结构相似度估算（基于句子数量和长度分布）
        sentences1 = text1.split('。')
        sentences2 = text2.split('。')
        
        if len(sentences1) == 0 and len(sentences2) == 0:
            return 1.0
        
        # 句子数量相似度
        count_similarity = 1 - abs(len(sentences1) - len(sentences2)) / max(len(sentences1), len(sentences2))
        
        return count_similarity


class StyleAlignmentEngine:
    """文风对齐引擎"""
    
    def __init__(self, llm_client=None, storage_path: str = "src/core/knowledge_base/style_alignments"):
        self.similarity_calculator = StyleSimilarityCalculator()
        self.transfer_engine = StyleTransferEngine(llm_client)
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def align_style(self, source_features: Dict[str, Any], 
                   target_features: Dict[str, Any],
                   content_to_align: str,
                   alignment_strategy: str = "comprehensive") -> Dict[str, Any]:
        """
        执行文风对齐
        
        Args:
            source_features: 源文档特征
            target_features: 目标文档特征
            content_to_align: 需要对齐的内容
            alignment_strategy: 对齐策略
        """
        result = {
            "alignment_time": datetime.now().isoformat(),
            "strategy": alignment_strategy,
            "similarity_analysis": {},
            "transfer_result": {},
            "alignment_quality": {},
            "success": False
        }
        
        try:
            # 1. 计算风格相似度
            source_vector = source_features.get("feature_vector", [])
            target_vector = target_features.get("feature_vector", [])
            
            if source_vector and target_vector and len(source_vector) > 0 and len(target_vector) > 0:
                similarity_result = self.similarity_calculator.calculate_similarity(
                    source_vector, target_vector, method="cosine"
                )
                result["similarity_analysis"] = similarity_result
            
            # 2. 执行文风迁移
            print("🔄 开始文风迁移...")
            transfer_result = self.transfer_engine.perform_style_transfer(
                source_features, target_features, content_to_align, strategy="direct"
            )
            result["transfer_result"] = transfer_result
            
            # 3. 如果LLM迁移失败，尝试使用保存的文风提示词
            if not transfer_result.get("success") and "error" in transfer_result:
                print("⚠️ LLM迁移失败，尝试使用保存的文风提示词...")
                fallback_result = self._perform_fallback_style_transfer(
                    source_features, target_features, content_to_align
                )
                if fallback_result.get("success"):
                    transfer_result = fallback_result
                    result["transfer_result"] = transfer_result
                    result["used_fallback"] = True
            
            # 4. 评估对齐质量
            if transfer_result.get("success"):
                quality_assessment = self._assess_alignment_quality(
                    content_to_align, 
                    transfer_result.get("rewritten_content", ""),
                    source_features,
                    target_features
                )
                result["alignment_quality"] = quality_assessment
            
            result["success"] = transfer_result.get("success", False)
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ 文风对齐失败: {str(e)}")
        
        return result
    
    def _perform_fallback_style_transfer(self, source_features: Dict[str, Any],
                                       target_features: Dict[str, Any],
                                       content_to_align: str) -> Dict[str, Any]:
        """使用保存的文风提示词进行回退迁移"""
        try:
            # 获取目标文风模板中的详细提示词
            target_style_prompt = target_features.get("style_prompt", "")
            target_style_type = target_features.get("style_type", "business_professional")
            
            if not target_style_prompt:
                # 如果没有保存的提示词，生成基础提示词
                target_style_prompt = self._generate_basic_style_prompt(target_features)
            
            # 构建完整的迁移提示词
            full_prompt = self._build_enhanced_style_migration_prompt(
                content_to_align, target_style_prompt, target_style_type, target_features
            )
            
            # 尝试调用LLM
            if self.transfer_engine.llm_client:
                print("🤖 使用LLM进行回退文风迁移...")
                response = self.transfer_engine.llm_client.generate(full_prompt)
                rewritten_content = self.transfer_engine._extract_rewritten_content(response)
                
                return {
                    "success": True,
                    "rewritten_content": rewritten_content,
                    "raw_llm_response": response,
                    "used_fallback": True,
                    "fallback_method": "saved_style_prompt"
                }
            else:
                # 如果LLM不可用，使用规则基础迁移
                print("📝 使用规则基础迁移...")
                rewritten_content = self._rule_based_style_migration(
                    content_to_align, target_style_type, target_features
                )
                
                return {
                    "success": True,
                    "rewritten_content": rewritten_content,
                    "used_fallback": True,
                    "fallback_method": "rule_based"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"回退迁移失败: {str(e)}",
                "used_fallback": True
            }
    
    def _build_enhanced_style_migration_prompt(self, content: str, style_prompt: str,
                                             style_type: str, style_features: Dict[str, Any]) -> str:
        """构建增强的文风迁移提示词"""
        
        # 获取风格特征描述
        style_description = self._extract_style_description(style_features)
        
        prompt = f"""请根据以下详细的文风要求，将内容改写为目标风格。

## 目标文风要求
{style_prompt}

## 风格特征详情
{style_description}

## 需要改写的内容
{content}

## 改写要求
1. 严格按照上述文风要求进行改写
2. 保持原文的核心信息和逻辑结构不变
3. 调整词汇选择、句式结构、语气表达等各个方面
4. 确保改写后的文本自然流畅，符合中文表达习惯
5. 避免明显的AI生成痕迹

## 请提供改写结果
请直接返回改写后的完整文本，不要添加任何解释或标记。"""
        
        return prompt
    
    def _extract_style_description(self, style_features: Dict[str, Any]) -> str:
        """提取风格特征描述"""
        descriptions = []
        
        # 从量化特征中提取描述
        quant_features = style_features.get("quantitative_features", {})
        if quant_features:
            lexical = quant_features.get("lexical_features", {})
            syntactic = quant_features.get("syntactic_features", {})
            
            if lexical.get("ttr", 0) > 0.7:
                descriptions.append("词汇丰富多样")
            if lexical.get("formal_word_density", 0) > 0.1:
                descriptions.append("使用较多正式词汇")
            if syntactic.get("avg_sentence_length", 0) > 20:
                descriptions.append("句子较长，结构复杂")
            elif syntactic.get("avg_sentence_length", 0) < 10:
                descriptions.append("句子简短，表达简洁")
        
        # 从LLM特征中提取描述
        llm_features = style_features.get("llm_features", {})
        if llm_features:
            evaluations = llm_features.get("evaluations", {})
            for dimension, eval_data in evaluations.items():
                if isinstance(eval_data, dict) and "score" in eval_data:
                    score = eval_data["score"]
                    reason = eval_data.get("reason", "")
                    if score >= 4:
                        descriptions.append(f"高{dimension}（{reason}）")
                    elif score <= 2:
                        descriptions.append(f"低{dimension}（{reason}）")
        
        return "；".join(descriptions) if descriptions else "标准文风"
    
    def _generate_basic_style_prompt(self, style_features: Dict[str, Any]) -> str:
        """生成基础文风提示词"""
        style_type = style_features.get("style_type", "business_professional")
        
        style_prompts = {
            "business_professional": "请按照商务专业风格进行改写，要求：正式、简洁、逻辑清晰、重点突出",
            "academic_research": "请按照学术研究风格进行改写，要求：严谨、客观、论证充分、引用规范",
            "formal_official": "请按照正式公文风格进行改写，要求：规范、准确、权威、正式",
            "narrative_descriptive": "请按照叙述描述风格进行改写，要求：生动、形象、情感真实、细节丰富",
            "concise_practical": "请按照简洁实用风格进行改写，要求：言简意赅、直接有效、操作性强"
        }
        
        return style_prompts.get(style_type, "请保持原有的写作风格")
    
    def _rule_based_style_migration(self, content: str, target_style: str, 
                                  style_features: Dict[str, Any]) -> str:
        """基于规则的文风迁移"""
        migrated_content = content
        
        # 根据目标风格应用不同的规则
        if target_style == "business_professional":
            replacements = {
                "我觉得": "我认为",
                "挺好的": "较为理想",
                "应该可以": "能够",
                "解决问题": "解决相关问题",
                "用了": "采用了",
                "算了一下": "进行了分析",
                "总的来说": "综上所述",
                "不错": "良好",
                "应该能用": "具备可行性"
            }
        elif target_style == "academic_research":
            replacements = {
                "我觉得": "研究表明",
                "挺好的": "具有积极效果",
                "应该可以": "能够有效",
                "解决问题": "解决相关问题",
                "用了": "采用了",
                "算了一下": "进行了统计分析",
                "总的来说": "综上所述",
                "不错": "表现良好",
                "应该能用": "具备应用价值"
            }
        elif target_style == "formal_official":
            replacements = {
                "我觉得": "经分析认为",
                "挺好的": "表现良好",
                "应该可以": "具备可行性",
                "解决问题": "解决相关问题",
                "用了": "采用了",
                "算了一下": "进行了分析",
                "总的来说": "综上所述",
                "不错": "表现良好",
                "应该能用": "具备实施条件"
            }
        else:
            replacements = {}
        
        for old, new in replacements.items():
            migrated_content = migrated_content.replace(old, new)
        
        return migrated_content
    
    def _assess_alignment_quality(self, original: str, aligned: str,
                                source_features: Dict[str, Any],
                                target_features: Dict[str, Any]) -> Dict[str, Any]:
        """评估对齐质量"""
        assessment = {
            "content_preservation": 0.0,
            "style_alignment": 0.0,
            "fluency": 0.0,
            "overall_quality": 0.0
        }
        
        try:
            # 内容保持度（基于词汇重叠）
            word_overlap = self.transfer_engine._calculate_word_overlap(original, aligned)
            assessment["content_preservation"] = word_overlap
            
            # 风格对齐度（基于特征相似度）
            source_vector = source_features.get("feature_vector", [])
            target_vector = target_features.get("feature_vector", [])
            
            if source_vector and target_vector:
                similarity = self.similarity_calculator.calculate_similarity(
                    source_vector, target_vector, method="cosine"
                )
                assessment["style_alignment"] = similarity.get("similarity_score", 0.0)
            
            # 流畅度（简单估算）
            assessment["fluency"] = self._estimate_fluency(aligned)
            
            # 整体质量
            assessment["overall_quality"] = (
                assessment["content_preservation"] * 0.4 +
                assessment["style_alignment"] * 0.4 +
                assessment["fluency"] * 0.2
            )
            
        except Exception as e:
            assessment["error"] = str(e)
        
        return assessment
    
    def _estimate_fluency(self, text: str) -> float:
        """估算文本流畅度"""
        # 简单的流畅度估算
        if not text:
            return 0.0
        
        # 基于句子长度分布和标点使用的简单评估
        sentences = text.split('。')
        if not sentences:
            return 0.5
        
        # 句子长度方差（过大或过小都不好）
        lengths = [len(s.strip()) for s in sentences if s.strip()]
        if not lengths:
            return 0.5
        
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        
        # 理想句长在10-25字之间
        length_score = 1.0 - abs(avg_length - 17.5) / 17.5
        variance_score = 1.0 - min(variance / 100, 1.0)  # 方差过大扣分
        
        return max(0.0, min(1.0, (length_score + variance_score) / 2))
    
    def save_alignment_result(self, alignment_result: Dict[str, Any], filename: str = None) -> str:
        """保存对齐结果"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"style_alignment_{timestamp}.json"

        filepath = os.path.join(self.storage_path, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(alignment_result, f, ensure_ascii=False, indent=2)
            return filepath
        except Exception as e:
            return f"保存失败: {str(e)}"

    def batch_style_alignment(self, source_features: Dict[str, Any],
                            target_features: Dict[str, Any],
                            content_list: List[str]) -> Dict[str, Any]:
        """批量文风对齐"""
        results = {
            "batch_time": datetime.now().isoformat(),
            "total_items": len(content_list),
            "successful_alignments": 0,
            "failed_alignments": 0,
            "alignment_results": [],
            "batch_summary": {}
        }

        for i, content in enumerate(content_list):
            try:
                alignment_result = self.align_style(
                    source_features, target_features, content
                )

                if alignment_result.get("success"):
                    results["successful_alignments"] += 1
                else:
                    results["failed_alignments"] += 1

                alignment_result["item_index"] = i
                results["alignment_results"].append(alignment_result)

            except Exception as e:
                results["failed_alignments"] += 1
                results["alignment_results"].append({
                    "item_index": i,
                    "success": False,
                    "error": str(e),
                    "original_content": content
                })

        # 生成批量摘要
        results["batch_summary"] = {
            "success_rate": results["successful_alignments"] / results["total_items"] if results["total_items"] > 0 else 0,
            "average_quality": self._calculate_average_quality(results["alignment_results"]),
            "processing_time": datetime.now().isoformat()
        }

        return results

    def _calculate_average_quality(self, alignment_results: List[Dict[str, Any]]) -> float:
        """计算平均质量分数"""
        quality_scores = []

        for result in alignment_results:
            if result.get("success") and "alignment_quality" in result:
                quality = result["alignment_quality"].get("overall_quality", 0.0)
                quality_scores.append(quality)

        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
