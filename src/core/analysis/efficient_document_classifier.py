#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高效文档分类器

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
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import Counter
import numpy as np
import yaml


@dataclass
class DocumentSignature:
    pass
    
    def __init__(self):
        # 加载置信度阈值配置
        config_path = 'config/config.yaml'
        config = {}  # 保证类型为dict
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    config = loaded
        except Exception:
            config = {}
        self.intent_confidence_thresholds = config.get('intent_confidence_thresholds', {})
        # 文档类型的快速识别规则
        self.quick_rules = {
            "empty_form": {
                "conditions": [
                    lambda sig: sig.word_count < 100,
                    lambda sig: sig.has_forms or sig.has_tables,
                    lambda sig: sig.structure_complexity > 0.3
                ],
                "confidence_threshold": self.intent_confidence_thresholds.get("fill_form", 0.8)
            },
            "format_messy": {
                "conditions": [
                    lambda sig: sig.format_consistency < 0.4,
                    lambda sig: sig.word_count > 100,
                    lambda sig: not sig.has_headers or sig.structure_complexity < 0.3
                ],
                "confidence_threshold": self.intent_confidence_thresholds.get("format_cleanup", 0.7)
            },
            "content_incomplete": {
                "conditions": [
                    lambda sig: 100 < sig.word_count < 800,
                    lambda sig: sig.structure_complexity > 0.5,
                    lambda sig: sig.format_consistency > 0.6
                ],
                "confidence_threshold": self.intent_confidence_thresholds.get("content_completion", 0.6)
            },
            "aigc_heavy": {
                "conditions": [
                    lambda sig: sig.word_count > 200,
                    lambda sig: sig.avg_sentence_length > 20,
                    lambda sig: sig.formality_score > 0.7
                ],
                "confidence_threshold": self.intent_confidence_thresholds.get("style_rewrite", 0.5)
            },
            "contract_template": {
                "conditions": [
                    lambda sig: sig.word_count > 300,
                    lambda sig: sig.technical_density < 0.2,
                    lambda sig: sig.has_headers and sig.has_tables,
                ],
                "confidence_threshold": self.intent_confidence_thresholds.get("contract_template", 0.85)
            },
            "paper_draft": {
                "conditions": [
                    lambda sig: sig.word_count > 500,
                    lambda sig: sig.technical_density > 0.3,
                    lambda sig: sig.has_headers and sig.has_tables,
                ],
                "confidence_threshold": self.intent_confidence_thresholds.get("paper_draft", 0.75)
            },
            "aigc_incomplete": {
                "conditions": [
                    lambda sig: sig.word_count > 100,
                    lambda sig: sig.formality_score > 0.7,
                    lambda sig: sig.structure_complexity < 0.4
                ],
                "confidence_threshold": self.intent_confidence_thresholds.get("aigc_incomplete", 0.7)
            }
        }
        
        # 文档类型的精确特征模板
        self.precise_templates = self._load_precise_templates()
    
    def classify_document(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        # 1. 提取文档签名（最核心的特征）
        signature = self._extract_document_signature(content)
        if metadata is None:
            metadata = {}
        
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
    
    def _extract_document_signature(self, content: str) -> 'DocumentSignature':
        # mock 实现
        return DocumentSignature()

    def _detect_headers(self, lines: List[str]) -> bool:
        table_indicators = ['|', '\t', '┌', '├', '│']
        return any(indicator in content for indicator in table_indicators)
    
    def _detect_lists(self, lines: List[str]) -> bool:
        form_indicators = ['___', '____', '□', '☐', '填写', '姓名：', '日期：']
        return any(indicator in content for indicator in form_indicators)
    
    def _calculate_formality(self, content: str) -> float:
        technical_words = ['系统', '方法', '技术', '算法', '模型', '数据', '分析', '实现']
        technical_count = sum(1 for word in technical_words if word in content)
        total_words = len(content.split())
        return min(1, technical_count / max(total_words / 50, 1))
    
    def _calculate_structure_complexity(self, lines: List[str]) -> float:
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
    
    def _quick_classification(self, signature: 'DocumentSignature', content: str) -> Dict[str, Any]:
        # mock 实现
        return {"document_type": "mock", "confidence": 0.5, "processing_intent": "mock", "evidence": []}
    
    def _detect_aigc_precise(self, content: str) -> float:
        quick_result = {"document_type": "mock", "confidence": 0.5, "processing_intent": "mock", "evidence": []}
        precise_result = {"document_type": "mock", "confidence": 0.5, "processing_intent": "mock", "evidence": []}
        if quick_result["document_type"] == precise_result["document_type"]:
            combined_confidence = min(1.0, (quick_result["confidence"] + precise_result["confidence"]) / 2 + 0.2)
            return {
                "document_type": quick_result["document_type"],
                "confidence": combined_confidence,
                "processing_intent": quick_result["processing_intent"],
                "evidence": quick_result["evidence"] + precise_result["evidence"]
            }
        if quick_result["confidence"] >= precise_result["confidence"]:
            return quick_result
        else:
            return precise_result
    
    def _map_type_to_intent(self, doc_type: str) -> str:
        # MVP: 加载精确识别模板
        # 当前实现范围:
        # - 返回空字典, 表示暂无预训练模板
        # - 不依赖外部模型或复杂规则
        # - 作为占位符保持接口完整性
        # 后续扩展点:
        # - 加载预训练的机器学习模型
        # - 支持自定义模板规则配置
        # - 支持模板的动态更新和版本管理
        # - 集成外部AI服务进行文档分类
        # - 支持多语言模板识别
        return {}
    
    def _has_table(self, content: str = "") -> bool:
        table_indicators = ["表格", "table", "|", ","]
        return any(indicator in content for indicator in table_indicators)

    def _has_form(self, content: str = "") -> bool:
        form_indicators = ["表单", "form", "填写"]
        return any(indicator in content for indicator in form_indicators)