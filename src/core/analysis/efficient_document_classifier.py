"""
高效文档类型识别器 - 基于第一性原理的分层识别架构

核心思想：
1. 快速筛选 - 用最少计算排除不可能的类型
2. 特征聚焦 - 针对每种类型提取最具区分度的特征
3. 渐进精确 - 从粗粒度到细粒度逐步确认
"""

import re
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import Counter
import numpy as np


@dataclass
class DocumentSignature:
    """文档特征签名 - 用于快速识别的核心特征"""
    # 结构特征
    has_title: bool
    has_headers: bool
    has_tables: bool
    has_lists: bool
    has_forms: bool
    
    # 统计特征
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_sentence_length: float
    
    # 语言特征
    formality_score: float
    technical_density: float
    
    # 格式特征
    structure_complexity: float
    format_consistency: float


class EfficientDocumentClassifier:
    """高效文档分类器"""
    
    def __init__(self):
        # 文档类型的快速识别规则
        self.quick_rules = {
            "empty_form": {
                "conditions": [
                    lambda sig: sig.word_count < 100,
                    lambda sig: sig.has_forms or sig.has_tables,
                    lambda sig: sig.structure_complexity > 0.3
                ],
                "confidence_threshold": 0.8
            },
            "format_messy": {
                "conditions": [
                    lambda sig: sig.format_consistency < 0.4,
                    lambda sig: sig.word_count > 100,
                    lambda sig: not sig.has_headers or sig.structure_complexity < 0.3
                ],
                "confidence_threshold": 0.7
            },
            "content_incomplete": {
                "conditions": [
                    lambda sig: 100 < sig.word_count < 800,
                    lambda sig: sig.structure_complexity > 0.5,
                    lambda sig: sig.format_consistency > 0.6
                ],
                "confidence_threshold": 0.6
            },
            "aigc_heavy": {
                "conditions": [
                    lambda sig: sig.word_count > 200,
                    lambda sig: sig.avg_sentence_length > 20,
                    lambda sig: sig.formality_score > 0.7
                ],
                "confidence_threshold": 0.5
            }
        }
        
        # 文档类型的精确特征模板
        self.precise_templates = self._load_precise_templates()
    
    def classify_document(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        高效文档分类主流程
        
        Returns:
            {
                "document_type": str,
                "confidence": float,
                "processing_intent": str,
                "evidence": List[str],
                "signature": DocumentSignature
            }
        """
        # 1. 提取文档签名（最核心的特征）
        signature = self._extract_document_signature(content)
        
        # 2. 快速筛选阶段
        quick_results = self._quick_classification(signature, content)
        
        # 3. 如果快速筛选置信度足够，直接返回
        if quick_results["confidence"] >= 0.8:
            return {
                **quick_results,
                "signature": signature,
                "classification_method": "quick_rules"
            }
        
        # 4. 精确识别阶段
        precise_results = self._precise_classification(signature, content)
        
        # 5. 结合快速和精确结果
        final_result = self._combine_results(quick_results, precise_results)
        
        return {
            **final_result,
            "signature": signature,
            "classification_method": "combined"
        }
    
    def _extract_document_signature(self, content: str) -> DocumentSignature:
        """提取文档特征签名 - 核心特征提取"""
        if not content or not content.strip():
            return DocumentSignature(
                has_title=False, has_headers=False, has_tables=False,
                has_lists=False, has_forms=False, word_count=0,
                sentence_count=0, paragraph_count=0, avg_sentence_length=0,
                formality_score=0, technical_density=0,
                structure_complexity=0, format_consistency=0
            )
        
        lines = content.split('\n')
        words = content.split()
        sentences = re.split(r'[.!?。！？]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 结构特征检测
        has_title = self._detect_title(lines)
        has_headers = self._detect_headers(lines)
        has_tables = self._detect_tables(content)
        has_lists = self._detect_lists(lines)
        has_forms = self._detect_forms(content)
        
        # 统计特征
        word_count = len(words)
        sentence_count = len(sentences)
        paragraph_count = len([line for line in lines if line.strip()])
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # 语言特征
        formality_score = self._calculate_formality(content)
        technical_density = self._calculate_technical_density(content)
        
        # 格式特征
        structure_complexity = self._calculate_structure_complexity(lines)
        format_consistency = self._calculate_format_consistency(lines)
        
        return DocumentSignature(
            has_title=has_title, has_headers=has_headers, has_tables=has_tables,
            has_lists=has_lists, has_forms=has_forms, word_count=word_count,
            sentence_count=sentence_count, paragraph_count=paragraph_count,
            avg_sentence_length=avg_sentence_length, formality_score=formality_score,
            technical_density=technical_density, structure_complexity=structure_complexity,
            format_consistency=format_consistency
        )
    
    def _detect_title(self, lines: List[str]) -> bool:
        """检测标题"""
        if not lines:
            return False
        first_line = lines[0].strip()
        return len(first_line) < 50 and len(first_line) > 5 and not first_line.endswith('：')
    
    def _detect_headers(self, lines: List[str]) -> bool:
        """检测标题层级"""
        header_patterns = [r'^[一二三四五六七八九十]+[、.]', r'^\d+[、.]', r'^[（(]\d+[）)]', r'^#+\s']
        return any(any(re.match(pattern, line.strip()) for pattern in header_patterns) for line in lines)
    
    def _detect_tables(self, content: str) -> bool:
        """检测表格"""
        table_indicators = ['|', '\t', '┌', '├', '│']
        return any(indicator in content for indicator in table_indicators)
    
    def _detect_lists(self, lines: List[str]) -> bool:
        """检测列表"""
        list_patterns = [r'^\s*[-*+]\s', r'^\s*\d+\.\s', r'^\s*[a-zA-Z]\.\s']
        return any(any(re.match(pattern, line) for pattern in list_patterns) for line in lines)
    
    def _detect_forms(self, content: str) -> bool:
        """检测表单"""
        form_indicators = ['___', '____', '□', '☐', '填写', '姓名：', '日期：']
        return any(indicator in content for indicator in form_indicators)
    
    def _calculate_formality(self, content: str) -> float:
        """计算正式程度"""
        formal_words = ['根据', '依据', '按照', '鉴于', '综合', '分析', '评估', '建议']
        informal_words = ['很', '非常', '特别', '挺', '蛮', '超级']
        
        formal_count = sum(1 for word in formal_words if word in content)
        informal_count = sum(1 for word in informal_words if word in content)
        
        total_words = len(content.split())
        formal_ratio = formal_count / max(total_words / 100, 1)  # 每100词的正式词汇数
        informal_ratio = informal_count / max(total_words / 100, 1)
        
        return max(0, min(1, formal_ratio - informal_ratio + 0.5))
    
    def _calculate_technical_density(self, content: str) -> float:
        """计算技术密度"""
        technical_words = ['系统', '方法', '技术', '算法', '模型', '数据', '分析', '实现']
        technical_count = sum(1 for word in technical_words if word in content)
        total_words = len(content.split())
        return min(1, technical_count / max(total_words / 50, 1))
    
    def _calculate_structure_complexity(self, lines: List[str]) -> float:
        """计算结构复杂度"""
        structure_indicators = 0
        
        # 检测不同层级的标题
        header_levels = set()
        for line in lines:
            if re.match(r'^[一二三四五六七八九十]+[、.]', line.strip()):
                header_levels.add(1)
            elif re.match(r'^\d+[、.]', line.strip()):
                header_levels.add(2)
            elif re.match(r'^[（(]\d+[）)]', line.strip()):
                header_levels.add(3)
        
        structure_indicators += len(header_levels) * 0.2
        
        # 检测段落结构
        empty_lines = sum(1 for line in lines if not line.strip())
        if empty_lines > 0:
            structure_indicators += 0.3
        
        return min(1, structure_indicators)
    
    def _calculate_format_consistency(self, lines: List[str]) -> float:
        """计算格式一致性"""
        if not lines:
            return 0
        
        # 检测行长度的一致性
        line_lengths = [len(line) for line in lines if line.strip()]
        if not line_lengths:
            return 0
        
        avg_length = sum(line_lengths) / len(line_lengths)
        variance = sum((length - avg_length) ** 2 for length in line_lengths) / len(line_lengths)
        consistency = 1 / (1 + variance / max(avg_length, 1))
        
        return min(1, consistency)
    
    def _quick_classification(self, signature: DocumentSignature, content: str) -> Dict[str, Any]:
        """快速分类阶段"""
        results = []
        
        for doc_type, rule_set in self.quick_rules.items():
            # 检查所有条件
            conditions_met = sum(1 for condition in rule_set["conditions"] if condition(signature))
            confidence = conditions_met / len(rule_set["conditions"])
            
            if confidence >= rule_set["confidence_threshold"]:
                results.append({
                    "document_type": doc_type,
                    "confidence": confidence,
                    "evidence": [f"满足{conditions_met}/{len(rule_set['conditions'])}个快速识别条件"]
                })
        
        if results:
            # 返回置信度最高的结果
            best_result = max(results, key=lambda x: x["confidence"])
            return {
                **best_result,
                "processing_intent": self._map_type_to_intent(best_result["document_type"])
            }
        
        return {
            "document_type": "unknown",
            "confidence": 0.0,
            "processing_intent": "general_processing",
            "evidence": ["快速识别阶段未找到匹配类型"]
        }
    
    def _precise_classification(self, signature: DocumentSignature, content: str) -> Dict[str, Any]:
        """精确分类阶段"""
        # 这里可以使用更复杂的算法，如机器学习模型
        # 目前使用基于规则的精确匹配
        
        scores = {}
        
        # 空表单检测
        if signature.has_forms or (signature.has_tables and signature.word_count < 200):
            scores["empty_form"] = 0.8
        
        # 格式混乱检测
        if signature.format_consistency < 0.5 and signature.word_count > 100:
            scores["format_messy"] = 0.7
        
        # 内容不完整检测
        if 100 < signature.word_count < 1000 and signature.structure_complexity > 0.4:
            scores["content_incomplete"] = 0.6
        
        # AIGC检测
        aigc_score = self._detect_aigc_precise(content)
        if aigc_score > 0.5:
            scores["aigc_heavy"] = aigc_score
        
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])
            return {
                "document_type": best_type[0],
                "confidence": best_type[1],
                "processing_intent": self._map_type_to_intent(best_type[0]),
                "evidence": [f"精确分析得分: {best_type[1]:.2f}"]
            }
        
        return {
            "document_type": "general_document",
            "confidence": 0.5,
            "processing_intent": "general_processing",
            "evidence": ["使用默认分类"]
        }
    
    def _detect_aigc_precise(self, content: str) -> float:
        """精确AIGC检测"""
        aigc_indicators = [
            "总的来说", "综上所述", "需要注意的是", "值得一提的是",
            "首先", "其次", "最后", "另外", "此外"
        ]
        
        indicator_count = sum(1 for indicator in aigc_indicators if indicator in content)
        sentences = re.split(r'[.!?。！？]', content)
        
        if len(sentences) == 0:
            return 0.0
        
        # 计算AIGC指标密度
        density = indicator_count / len(sentences)
        return min(1.0, density * 10)  # 放大密度作为得分
    
    def _combine_results(self, quick_result: Dict[str, Any], precise_result: Dict[str, Any]) -> Dict[str, Any]:
        """结合快速和精确结果"""
        # 如果两个结果一致，提高置信度
        if quick_result["document_type"] == precise_result["document_type"]:
            combined_confidence = min(1.0, (quick_result["confidence"] + precise_result["confidence"]) / 2 + 0.2)
            return {
                "document_type": quick_result["document_type"],
                "confidence": combined_confidence,
                "processing_intent": quick_result["processing_intent"],
                "evidence": quick_result["evidence"] + precise_result["evidence"]
            }
        
        # 如果结果不一致，选择置信度更高的
        if quick_result["confidence"] >= precise_result["confidence"]:
            return quick_result
        else:
            return precise_result
    
    def _map_type_to_intent(self, doc_type: str) -> str:
        """映射文档类型到处理意图"""
        mapping = {
            "empty_form": "intelligent_filling",
            "format_messy": "format_cleanup", 
            "content_incomplete": "content_completion",
            "aigc_heavy": "style_rewrite",
            "general_document": "general_processing"
        }
        return mapping.get(doc_type, "general_processing")
    
    def _load_precise_templates(self) -> Dict[str, Any]:
        """加载精确识别模板"""
        # 这里可以加载预训练的模板或模型
        return {}
