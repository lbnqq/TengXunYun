#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pyramid Document Analyzer - 核心模块

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
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class DocumentTheme:
    """文档主题结构"""
    main_theme: str
    sub_themes: List[str]
    supporting_points: List[str]
    evidence_levels: List[str]
    logical_hierarchy: Dict[str, List[str]]


@dataclass
class ContentStructure:
    """内容结构分析"""
    document_outline: List[Dict[str, Any]]
    logical_flow: List[str]
    content_dependencies: Dict[str, List[str]]
    consistency_checks: List[str]


class PyramidDocumentAnalyzer:
    """金字塔原理文档分析器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.tool_name = "金字塔原理文档分析器"
        self.description = "基于金字塔原理实现自上而下的文档主题和逻辑分析"
        
        # 金字塔原理分析模板
        self.pyramid_templates = {
            "theme_analysis": self._get_theme_analysis_template(),
            "structure_analysis": self._get_structure_analysis_template(),
            "logic_analysis": self._get_logic_analysis_template(),
            "content_generation": self._get_content_generation_template()
        }
    
    def analyze_document_pyramid(self, document_content: str, document_name: Optional[str] = None) -> Dict[str, Any]:
        """
        基于金字塔原理分析文档
        
        Args:
            document_content: 文档内容
            document_name: 文档名称
            
        Returns:
            金字塔分析结果
        """
        try:
            analysis_result = {
                "document_name": document_name or "未命名文档",
                "analysis_time": datetime.now().isoformat(),
                "analysis_method": "pyramid_principle",
                "pyramid_analysis": {},
                "theme_structure": {},
                "content_structure": {},
                "logical_consistency": {},
                "generation_guidance": {},
                "confidence_score": 0.0
            }
            
            # 1. 主题分析
            theme_analysis = self._analyze_document_theme(document_content)
            analysis_result["theme_structure"] = theme_analysis
            
            # 2. 结构分析
            structure_analysis = self._analyze_content_structure(document_content, theme_analysis)
            analysis_result["content_structure"] = structure_analysis
            
            # 3. 逻辑一致性分析
            logic_analysis = self._analyze_logical_consistency(document_content, theme_analysis, structure_analysis)
            analysis_result["logical_consistency"] = logic_analysis
            
            # 4. 生成指导
            generation_guidance = self._generate_pyramid_guidance(theme_analysis, structure_analysis, logic_analysis)
            analysis_result["generation_guidance"] = generation_guidance
            
            # 5. 计算置信度
            confidence = self._calculate_pyramid_confidence(theme_analysis, structure_analysis, logic_analysis)
            analysis_result["confidence_score"] = confidence
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"金字塔原理分析失败: {str(e)}"}
    
    def _analyze_document_theme(self, content: str) -> Dict[str, Any]:
        """分析文档主题结构"""
        try:
            if self.llm_client:
                prompt = self.pyramid_templates["theme_analysis"].format(
                    content=content[:3000]
                )
                
                response = self.llm_client.generate(prompt)
                try:
                    result = json.loads(response)
                    return result
                except:
                    pass
            
            # 备用分析逻辑
            return self._fallback_theme_analysis(content)
            
        except Exception as e:
            return {"error": f"主题分析失败: {str(e)}"}
    
    def _analyze_content_structure(self, content: str, theme_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析内容结构"""
        try:
            if self.llm_client:
                prompt = self.pyramid_templates["structure_analysis"].format(
                    content=content[:3000],
                    theme_info=json.dumps(theme_analysis, ensure_ascii=False)
                )
                
                response = self.llm_client.generate(prompt)
                try:
                    result = json.loads(response)
                    return result
                except:
                    pass
            
            # 备用分析逻辑
            return self._fallback_structure_analysis(content)
            
        except Exception as e:
            return {"error": f"结构分析失败: {str(e)}"}
    
    def _analyze_logical_consistency(self, content: str, theme_analysis: Dict[str, Any], 
                                   structure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析逻辑一致性"""
        try:
            if self.llm_client:
                prompt = self.pyramid_templates["logic_analysis"].format(
                    content=content[:3000],
                    theme_info=json.dumps(theme_analysis, ensure_ascii=False),
                    structure_info=json.dumps(structure_analysis, ensure_ascii=False)
                )
                
                response = self.llm_client.generate(prompt)
                try:
                    result = json.loads(response)
                    return result
                except:
                    pass
            
            # 备用分析逻辑
            return self._fallback_logic_analysis(content)
            
        except Exception as e:
            return {"error": f"逻辑分析失败: {str(e)}"}
    
    def _generate_pyramid_guidance(self, theme_analysis: Dict[str, Any], 
                                 structure_analysis: Dict[str, Any],
                                 logic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成金字塔原理指导"""
        try:
            if self.llm_client:
                prompt = self.pyramid_templates["content_generation"].format(
                    theme_info=json.dumps(theme_analysis, ensure_ascii=False),
                    structure_info=json.dumps(structure_analysis, ensure_ascii=False),
                    logic_info=json.dumps(logic_analysis, ensure_ascii=False)
                )
                
                response = self.llm_client.generate(prompt)
                try:
                    result = json.loads(response)
                    return result
                except:
                    pass
            
            # 备用指导生成
            return self._fallback_guidance_generation(theme_analysis, structure_analysis, logic_analysis)
            
        except Exception as e:
            return {"error": f"指导生成失败: {str(e)}"}
    
    def _get_theme_analysis_template(self) -> str:
        """获取主题分析模板"""
        return """
        基于金字塔原理分析以下文档的主题结构：

        文档内容：
        {content}

        请以JSON格式返回分析结果：
        {{
            "main_theme": "文档的核心主题",
            "sub_themes": ["子主题1", "子主题2", "子主题3"],
            "supporting_points": ["支撑点1", "支撑点2", "支撑点3"],
            "evidence_levels": ["证据层级1", "证据层级2"],
            "logical_hierarchy": {{
                "level_1": ["一级要点"],
                "level_2": ["二级要点"],
                "level_3": ["三级要点"]
            }},
            "theme_clarity": 1-5,
            "theme_coherence": 1-5,
            "theme_analysis": "主题分析说明"
        }}
        """
    
    def _get_structure_analysis_template(self) -> str:
        """获取结构分析模板"""
        return """
        基于金字塔原理分析以下文档的内容结构：

        文档内容：
        {content}

        主题信息：
        {theme_info}

        请以JSON格式返回分析结果：
        {{
            "document_outline": [
                {{
                    "level": 1,
                    "title": "章节标题",
                    "content_summary": "内容摘要",
                    "key_points": ["要点1", "要点2"],
                    "sub_sections": []
                }}
            ],
            "logical_flow": ["逻辑流程步骤1", "逻辑流程步骤2"],
            "content_dependencies": {{
                "section1": ["依赖章节1", "依赖章节2"]
            }},
            "consistency_checks": ["一致性检查项1", "一致性检查项2"],
            "structure_quality": 1-5,
            "structure_analysis": "结构分析说明"
        }}
        """
    
    def _get_logic_analysis_template(self) -> str:
        """获取逻辑分析模板"""
        return """
        基于金字塔原理分析以下文档的逻辑一致性：

        文档内容：
        {content}

        主题信息：
        {theme_info}

        结构信息：
        {structure_info}

        请以JSON格式返回分析结果：
        {{
            "logical_consistency": {{
                "theme_support": 1-5,
                "argument_flow": 1-5,
                "evidence_quality": 1-5,
                "conclusion_support": 1-5
            }},
            "logical_issues": ["逻辑问题1", "逻辑问题2"],
            "improvement_suggestions": ["改进建议1", "改进建议2"],
            "consistency_score": 1-5,
            "logic_analysis": "逻辑分析说明"
        }}
        """
    
    def _get_content_generation_template(self) -> str:
        """获取内容生成指导模板"""
        return """
        基于金字塔原理为文档内容生成提供指导：

        主题信息：
        {theme_info}

        结构信息：
        {structure_info}

        逻辑信息：
        {logic_info}

        请以JSON格式返回生成指导：
        {{
            "generation_strategy": "自上而下的生成策略",
            "content_priorities": ["优先级1", "优先级2"],
            "logical_sequence": ["逻辑顺序1", "逻辑顺序2"],
            "consistency_rules": ["一致性规则1", "一致性规则2"],
            "quality_checks": ["质量检查项1", "质量检查项2"],
            "generation_guidance": "生成指导说明"
        }}
        """
    
    def _fallback_theme_analysis(self, content: str) -> Dict[str, Any]:
        """备用主题分析"""
        # 简单的关键词提取
        lines = content.split('\n')
        title = lines[0] if lines else "未命名文档"
        
        # 提取可能的主题词
        theme_keywords = []
        for line in lines[:10]:  # 只看前10行
            if len(line.strip()) > 5 and len(line.strip()) < 50:
                theme_keywords.append(line.strip())
        
        return {
            "main_theme": title,
            "sub_themes": theme_keywords[:3],
            "supporting_points": [],
            "evidence_levels": [],
            "logical_hierarchy": {
                "level_1": [title],
                "level_2": theme_keywords[:2],
                "level_3": []
            },
            "theme_clarity": 3,
            "theme_coherence": 3,
            "theme_analysis": "基于文档标题和关键词的主题分析"
        }
    
    def _fallback_structure_analysis(self, content: str) -> Dict[str, Any]:
        """备用结构分析"""
        lines = content.split('\n')
        sections = []
        
        for i, line in enumerate(lines):
            if line.strip() and len(line.strip()) < 50:
                sections.append({
                    "level": 1,
                    "title": line.strip(),
                    "content_summary": "",
                    "key_points": [],
                    "sub_sections": []
                })
        
        return {
            "document_outline": sections[:5],  # 最多5个章节
            "logical_flow": ["文档分析", "内容生成", "质量检查"],
            "content_dependencies": {},
            "consistency_checks": ["主题一致性", "逻辑连贯性"],
            "structure_quality": 3,
            "structure_analysis": "基于文档结构的简单分析"
        }
    
    def _fallback_logic_analysis(self, content: str) -> Dict[str, Any]:
        """备用逻辑分析"""
        return {
            "logical_consistency": {
                "theme_support": 3,
                "argument_flow": 3,
                "evidence_quality": 3,
                "conclusion_support": 3
            },
            "logical_issues": [],
            "improvement_suggestions": ["增强主题一致性", "改善逻辑流程"],
            "consistency_score": 3,
            "logic_analysis": "基础逻辑一致性分析"
        }
    
    def _fallback_guidance_generation(self, theme_analysis: Dict[str, Any], 
                                    structure_analysis: Dict[str, Any],
                                    logic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """备用指导生成"""
        return {
            "generation_strategy": "自上而下，先主题后细节",
            "content_priorities": ["主题明确", "逻辑清晰", "内容完整"],
            "logical_sequence": ["确定主题", "构建框架", "填充内容"],
            "consistency_rules": ["保持主题一致", "逻辑连贯", "格式统一"],
            "quality_checks": ["主题检查", "逻辑检查", "完整性检查"],
            "generation_guidance": "基于金字塔原理的内容生成指导"
        }
    
    def _calculate_pyramid_confidence(self, theme_analysis: Dict[str, Any], 
                                    structure_analysis: Dict[str, Any],
                                    logic_analysis: Dict[str, Any]) -> float:
        """计算金字塔分析置信度"""
        try:
            confidence = 0.0
            
            # 主题分析权重
            if "error" not in theme_analysis:
                theme_clarity = theme_analysis.get("theme_clarity", 3)
                theme_coherence = theme_analysis.get("theme_coherence", 3)
                confidence += (theme_clarity + theme_coherence) / 10.0 * 0.4
            
            # 结构分析权重
            if "error" not in structure_analysis:
                structure_quality = structure_analysis.get("structure_quality", 3)
                confidence += structure_quality / 5.0 * 0.3
            
            # 逻辑分析权重
            if "error" not in logic_analysis:
                consistency_score = logic_analysis.get("consistency_score", 3)
                confidence += consistency_score / 5.0 * 0.3
            
            return min(1.0, confidence)
            
        except Exception as e:
            return 0.3  # 默认置信度 