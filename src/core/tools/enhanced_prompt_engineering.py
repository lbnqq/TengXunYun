#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Prompt Engineering - 核心模块

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
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
from dataclasses import dataclass, asdict
from enum import Enum


class PromptType(Enum):
    """提示词类型"""
    ANALYSIS = "analysis"           # 分析类
    GENERATION = "generation"       # 生成类
    REVIEW = "review"               # 审阅类
    OPTIMIZATION = "optimization"   # 优化类
    COMPARISON = "comparison"       # 比较类


class PromptStyle(Enum):
    """提示词风格"""
    PROFESSIONAL = "professional"   # 专业风格
    CONVERSATIONAL = "conversational" # 对话风格
    STRUCTURED = "structured"       # 结构化风格
    CREATIVE = "creative"           # 创意风格


@dataclass
class PromptTemplate:
    """提示词模板数据结构"""
    template_id: str
    prompt_type: PromptType
    prompt_style: PromptStyle
    name: str
    description: str
    version: str
    created_time: str
    updated_time: str
    base_prompt: str
    variables: List[str]
    examples: List[Dict[str, Any]]
    optimization_tips: List[str]
    quality_metrics: Dict[str, Any]


class EnhancedPromptEngineering:
    """增强的提示词工程系统"""
    
    def __init__(self, storage_path: str = "prompt_templates"):
        """
        初始化增强的提示词工程系统
        
        Args:
            storage_path: 模板存储路径
        """
        self.storage_path = storage_path
        self.templates_file = os.path.join(storage_path, "prompt_templates.json")
        
        # 确保存储目录存在
        os.makedirs(storage_path, exist_ok=True)
        
        # 初始化模板数据
        self.templates = self._load_templates()
        
        # 如果没有模板，创建默认模板
        if not self.templates:
            self._create_default_templates()
        
        # 提示词优化策略
        self.optimization_strategies = {
            "clarity": self._optimize_for_clarity,
            "specificity": self._optimize_for_specificity,
            "structure": self._optimize_for_structure,
            "context": self._optimize_for_context,
            "output_format": self._optimize_for_output_format
        }
    
    def create_optimized_prompt(self, prompt_type: PromptType, 
                               prompt_style: PromptStyle,
                               content: str,
                               variables: Dict[str, Any],
                               optimization_focus: List[str] = None) -> Dict[str, Any]:
        """
        创建优化的提示词
        
        Args:
            prompt_type: 提示词类型
            prompt_style: 提示词风格
            content: 主要内容
            variables: 变量字典
            optimization_focus: 优化重点
            
        Returns:
            优化的提示词
        """
        try:
            # 获取基础模板
            template = self._get_template_by_type_and_style(prompt_type, prompt_style)
            if not template:
                return {
                    "success": False,
                    "error": "未找到匹配的模板",
                    "message": f"未找到类型为 {prompt_type.value} 且风格为 {prompt_style.value} 的模板"
                }
            
            # 构建基础提示词
            base_prompt = self._build_base_prompt(template, content, variables)
            
            # 应用优化策略
            optimized_prompt = self._apply_optimization_strategies(
                base_prompt, template, optimization_focus or ["clarity", "specificity"]
            )
            
            # 生成提示词质量评估
            quality_assessment = self._assess_prompt_quality(optimized_prompt, template)
            
            return {
                "success": True,
                "optimized_prompt": optimized_prompt,
                "template_info": {
                    "template_id": template.template_id,
                    "template_name": template.name,
                    "prompt_type": prompt_type.value,
                    "prompt_style": prompt_style.value
                },
                "quality_assessment": quality_assessment,
                "optimization_applied": optimization_focus or ["clarity", "specificity"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "提示词优化失败"
            }
    
    def get_prompt_suggestions(self, content: str, target_output: str = None) -> Dict[str, Any]:
        """
        获取提示词建议
        
        Args:
            content: 输入内容
            target_output: 目标输出（可选）
            
        Returns:
            提示词建议
        """
        try:
            # 分析内容特征
            content_features = self._analyze_content_features(content)
            
            # 推荐提示词类型和风格
            recommended_type = self._recommend_prompt_type(content_features)
            recommended_style = self._recommend_prompt_style(content_features)
            
            # 生成优化建议
            optimization_suggestions = self._generate_optimization_suggestions(
                content_features, target_output
            )
            
            return {
                "success": True,
                "content_features": content_features,
                "recommendations": {
                    "prompt_type": recommended_type.value,
                    "prompt_style": recommended_style.value,
                    "reasoning": self._explain_recommendations(content_features)
                },
                "optimization_suggestions": optimization_suggestions,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "获取提示词建议失败"
            }
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载模板数据"""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载模板数据失败: {e}")
        return {}
    
    def _save_templates(self):
        """保存模板数据"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存模板数据失败: {e}")
    
    def _create_default_templates(self):
        """创建默认模板"""
        default_templates = [
            # 专业分析模板
            PromptTemplate(
                template_id="professional_analysis_v1",
                prompt_type=PromptType.ANALYSIS,
                prompt_style=PromptStyle.PROFESSIONAL,
                name="专业分析提示词模板",
                description="用于专业文档分析的提示词模板",
                version="1.0",
                created_time=datetime.now().isoformat(),
                updated_time=datetime.now().isoformat(),
                base_prompt="""
请作为{role}，对以下{content_type}进行专业分析：

文档内容：
{content}

请从以下维度进行深度分析：
{analysis_dimensions}

【分析要求】
- 分析要深入、准确、专业
- 建议要具体、可操作、有价值
- 语言要清晰、简洁、专业
- 结构要合理、逻辑要严密

【输出格式】
{output_format}

请确保分析结果的质量和专业性。
""",
                variables=["role", "content_type", "content", "analysis_dimensions", "output_format"],
                examples=[
                    {
                        "input": {
                            "role": "技术专家",
                            "content_type": "技术报告",
                            "content": "人工智能技术在自然语言处理领域取得了重大突破...",
                            "analysis_dimensions": "1. 技术指标评估\n2. 创新性分析\n3. 可行性评估",
                            "output_format": "JSON格式输出"
                        },
                        "output": "专业的JSON格式分析结果"
                    }
                ],
                optimization_tips=[
                    "明确指定分析角色和专业领域",
                    "提供具体的分析维度和要求",
                    "强调输出格式的规范性",
                    "要求分析的专业性和可操作性"
                ],
                quality_metrics={
                    "clarity": 0.9,
                    "specificity": 0.85,
                    "structure": 0.9,
                    "professionalism": 0.95
                }
            ),
            
            # 对话风格模板
            PromptTemplate(
                template_id="conversational_analysis_v1",
                prompt_type=PromptType.ANALYSIS,
                prompt_style=PromptStyle.CONVERSATIONAL,
                name="对话风格分析模板",
                description="用于友好对话式分析的提示词模板",
                version="1.0",
                created_time=datetime.now().isoformat(),
                updated_time=datetime.now().isoformat(),
                base_prompt="""
你好！我想请你帮我分析一下这个{content_type}。

内容如下：
{content}

我希望你能从{analysis_focus}的角度来帮我看看，主要关注{key_points}。

你觉得这个{content_type}怎么样？有什么好的地方，还有哪些地方可以改进？

请用{output_style}的方式回答我，让我容易理解。
""",
                variables=["content_type", "content", "analysis_focus", "key_points", "output_style"],
                examples=[
                    {
                        "input": {
                            "content_type": "商业提案",
                            "content": "我们推出了一款创新的智能家居产品...",
                            "analysis_focus": "商业价值",
                            "key_points": "市场机会、竞争优势",
                            "output_style": "通俗易懂"
                        },
                        "output": "友好的分析建议"
                    }
                ],
                optimization_tips=[
                    "使用友好的语气和表达方式",
                    "明确表达分析需求和关注点",
                    "要求输出风格通俗易懂",
                    "鼓励互动和讨论"
                ],
                quality_metrics={
                    "clarity": 0.85,
                    "specificity": 0.8,
                    "structure": 0.8,
                    "friendliness": 0.95
                }
            ),
            
            # 结构化模板
            PromptTemplate(
                template_id="structured_analysis_v1",
                prompt_type=PromptType.ANALYSIS,
                prompt_style=PromptStyle.STRUCTURED,
                name="结构化分析模板",
                description="用于结构化分析的提示词模板",
                version="1.0",
                created_time=datetime.now().isoformat(),
                updated_time=datetime.now().isoformat(),
                base_prompt="""
【分析任务】
对以下{content_type}进行{analysis_type}分析

【输入内容】
{content}

【分析框架】
{analysis_framework}

【具体要求】
{requirements}

【输出规范】
{output_specification}

【质量标准】
{quality_standards}

请严格按照上述框架和要求进行分析。
""",
                variables=["content_type", "analysis_type", "content", "analysis_framework", 
                          "requirements", "output_specification", "quality_standards"],
                examples=[
                    {
                        "input": {
                            "content_type": "合同文档",
                            "analysis_type": "法律风险",
                            "content": "甲方委托乙方提供技术服务...",
                            "analysis_framework": "1. 权利义务分析\n2. 风险识别\n3. 合规性检查",
                            "requirements": "专业、严谨、全面",
                            "output_specification": "结构化JSON格式",
                            "quality_standards": "准确性≥90%，完整性≥95%"
                        },
                        "output": "结构化的分析结果"
                    }
                ],
                optimization_tips=[
                    "使用清晰的结构化框架",
                    "明确每个部分的要求",
                    "提供具体的质量标准",
                    "强调输出格式的规范性"
                ],
                quality_metrics={
                    "clarity": 0.95,
                    "specificity": 0.9,
                    "structure": 0.95,
                    "completeness": 0.9
                }
            )
        ]
        
        # 保存默认模板
        for template in default_templates:
            self.templates[template.template_id] = asdict(template)
        
        self._save_templates()
    
    def _get_template_by_type_and_style(self, prompt_type: PromptType, 
                                       prompt_style: PromptStyle) -> Optional[PromptTemplate]:
        """根据类型和风格获取模板"""
        for template_data in self.templates.values():
            if (template_data.get("prompt_type") == prompt_type.value and 
                template_data.get("prompt_style") == prompt_style.value):
                return PromptTemplate(**template_data)
        return None
    
    def _build_base_prompt(self, template: PromptTemplate, content: str, 
                          variables: Dict[str, Any]) -> str:
        """构建基础提示词"""
        # 准备变量
        prompt_variables = {
            "content": content,
            **variables
        }
        
        # 替换模板中的变量
        base_prompt = template.base_prompt
        for var_name, var_value in prompt_variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in base_prompt:
                base_prompt = base_prompt.replace(placeholder, str(var_value))
        
        return base_prompt
    
    def _apply_optimization_strategies(self, base_prompt: str, template: PromptTemplate,
                                     optimization_focus: List[str]) -> str:
        """应用优化策略"""
        optimized_prompt = base_prompt
        
        for strategy_name in optimization_focus:
            if strategy_name in self.optimization_strategies:
                optimized_prompt = self.optimization_strategies[strategy_name](
                    optimized_prompt, template
                )
        
        return optimized_prompt
    
    def _optimize_for_clarity(self, prompt: str, template: PromptTemplate) -> str:
        """优化清晰度"""
        # 添加清晰度优化
        clarity_enhancements = [
            "\n\n【重要提醒】",
            "请确保回答清晰、准确、易懂。",
            "如果遇到不确定的内容，请明确说明。",
            "使用简洁明了的语言表达复杂概念。"
        ]
        
        return prompt + "\n".join(clarity_enhancements)
    
    def _optimize_for_specificity(self, prompt: str, template: PromptTemplate) -> str:
        """优化具体性"""
        # 添加具体性优化
        specificity_enhancements = [
            "\n\n【具体要求】",
            "请提供具体的例子和数据支持。",
            "避免使用模糊的表述，要给出明确的结论。",
            "每个分析点都要有充分的依据。"
        ]
        
        return prompt + "\n".join(specificity_enhancements)
    
    def _optimize_for_structure(self, prompt: str, template: PromptTemplate) -> str:
        """优化结构"""
        # 添加结构化优化
        structure_enhancements = [
            "\n\n【回答结构】",
            "请按照以下结构组织回答：",
            "1. 总体概述",
            "2. 详细分析",
            "3. 具体建议",
            "4. 总结"
        ]
        
        return prompt + "\n".join(structure_enhancements)
    
    def _optimize_for_context(self, prompt: str, template: PromptTemplate) -> str:
        """优化上下文"""
        # 添加上下文优化
        context_enhancements = [
            "\n\n【上下文考虑】",
            "请考虑文档的整体背景和目的。",
            "分析时要结合行业特点和实际情况。",
            "注意文档的目标读者和使用场景。"
        ]
        
        return prompt + "\n".join(context_enhancements)
    
    def _optimize_for_output_format(self, prompt: str, template: PromptTemplate) -> str:
        """优化输出格式"""
        # 添加输出格式优化
        format_enhancements = [
            "\n\n【输出格式要求】",
            "请严格按照指定的格式输出结果。",
            "确保输出内容的完整性和一致性。",
            "如果格式有特殊要求，请严格遵守。"
        ]
        
        return prompt + "\n".join(format_enhancements)
    
    def _assess_prompt_quality(self, prompt: str, template: PromptTemplate) -> Dict[str, Any]:
        """评估提示词质量"""
        quality_metrics = {
            "clarity": self._assess_clarity(prompt),
            "specificity": self._assess_specificity(prompt),
            "structure": self._assess_structure(prompt),
            "completeness": self._assess_completeness(prompt),
            "professionalism": self._assess_professionalism(prompt, template)
        }
        
        # 计算总体质量分数
        overall_score = sum(quality_metrics.values()) / len(quality_metrics)
        
        return {
            "metrics": quality_metrics,
            "overall_score": overall_score,
            "assessment": self._get_quality_assessment(overall_score)
        }
    
    def _assess_clarity(self, prompt: str) -> float:
        """评估清晰度"""
        clarity_indicators = [
            "请", "要求", "确保", "明确", "具体", "清晰", "准确"
        ]
        
        score = 0.0
        for indicator in clarity_indicators:
            if indicator in prompt:
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_specificity(self, prompt: str) -> float:
        """评估具体性"""
        specificity_indicators = [
            "具体", "详细", "明确", "例如", "包括", "涵盖", "涉及"
        ]
        
        score = 0.0
        for indicator in specificity_indicators:
            if indicator in prompt:
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_structure(self, prompt: str) -> float:
        """评估结构性"""
        structure_indicators = [
            "【", "】", "1.", "2.", "3.", "首先", "其次", "最后", "总结"
        ]
        
        score = 0.0
        for indicator in structure_indicators:
            if indicator in prompt:
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_completeness(self, prompt: str) -> float:
        """评估完整性"""
        completeness_indicators = [
            "分析", "评估", "建议", "总结", "输出", "格式", "要求"
        ]
        
        score = 0.0
        for indicator in completeness_indicators:
            if indicator in prompt:
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_professionalism(self, prompt: str, template: PromptTemplate) -> float:
        """评估专业性"""
        professionalism_indicators = [
            "专业", "专家", "深度", "严谨", "准确", "权威", "标准"
        ]
        
        score = 0.0
        for indicator in professionalism_indicators:
            if indicator in prompt:
                score += 0.1
        
        # 根据模板类型调整分数
        if template.prompt_style == PromptStyle.PROFESSIONAL:
            score += 0.2
        
        return min(score, 1.0)
    
    def _get_quality_assessment(self, overall_score: float) -> str:
        """获取质量评估描述"""
        if overall_score >= 0.9:
            return "优秀 - 提示词质量很高，适合专业应用"
        elif overall_score >= 0.8:
            return "良好 - 提示词质量较好，可以正常使用"
        elif overall_score >= 0.7:
            return "一般 - 提示词质量中等，建议进一步优化"
        else:
            return "需要改进 - 提示词质量较低，建议重新设计"
    
    def _analyze_content_features(self, content: str) -> Dict[str, Any]:
        """分析内容特征"""
        features = {
            "length": len(content),
            "word_count": len(content.split()),
            "sentence_count": len([s for s in content.split('。') if s.strip()]),
            "has_numbers": any(char.isdigit() for char in content),
            "has_technical_terms": self._detect_technical_terms(content),
            "has_business_terms": self._detect_business_terms(content),
            "has_legal_terms": self._detect_legal_terms(content),
            "complexity_level": self._assess_complexity(content)
        }
        
        return features
    
    def _detect_technical_terms(self, content: str) -> bool:
        """检测技术术语"""
        technical_terms = ["技术", "算法", "系统", "平台", "开发", "实现", "架构"]
        return any(term in content for term in technical_terms)
    
    def _detect_business_terms(self, content: str) -> bool:
        """检测商业术语"""
        business_terms = ["商业", "市场", "产品", "服务", "客户", "销售", "盈利"]
        return any(term in content for term in business_terms)
    
    def _detect_legal_terms(self, content: str) -> bool:
        """检测法律术语"""
        legal_terms = ["合同", "条款", "义务", "权利", "责任", "法律", "合规"]
        return any(term in content for term in legal_terms)
    
    def _assess_complexity(self, content: str) -> str:
        """评估复杂度"""
        word_count = len(content.split())
        if word_count < 100:
            return "简单"
        elif word_count < 500:
            return "中等"
        else:
            return "复杂"
    
    def _recommend_prompt_type(self, content_features: Dict[str, Any]) -> PromptType:
        """推荐提示词类型"""
        if content_features.get("has_technical_terms"):
            return PromptType.ANALYSIS
        elif content_features.get("has_business_terms"):
            return PromptType.ANALYSIS
        elif content_features.get("has_legal_terms"):
            return PromptType.REVIEW
        else:
            return PromptType.ANALYSIS
    
    def _recommend_prompt_style(self, content_features: Dict[str, Any]) -> PromptStyle:
        """推荐提示词风格"""
        complexity = content_features.get("complexity_level", "中等")
        
        if complexity == "复杂":
            return PromptStyle.STRUCTURED
        elif complexity == "中等":
            return PromptStyle.PROFESSIONAL
        else:
            return PromptStyle.CONVERSATIONAL
    
    def _explain_recommendations(self, content_features: Dict[str, Any]) -> str:
        """解释推荐理由"""
        reasons = []
        
        if content_features.get("has_technical_terms"):
            reasons.append("内容包含技术术语，建议使用分析类型")
        
        if content_features.get("has_business_terms"):
            reasons.append("内容涉及商业领域，建议使用专业风格")
        
        if content_features.get("has_legal_terms"):
            reasons.append("内容包含法律术语，建议使用审阅类型")
        
        complexity = content_features.get("complexity_level", "中等")
        if complexity == "复杂":
            reasons.append("内容复杂度较高，建议使用结构化风格")
        
        return "；".join(reasons) if reasons else "基于内容特征的一般性推荐"
    
    def _generate_optimization_suggestions(self, content_features: Dict[str, Any], 
                                         target_output: str = None) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 基于内容特征的建议
        if content_features.get("length", 0) > 1000:
            suggestions.append("内容较长，建议在提示词中明确分析重点")
        
        if content_features.get("has_technical_terms"):
            suggestions.append("包含技术内容，建议要求提供具体的技术指标")
        
        if content_features.get("has_business_terms"):
            suggestions.append("涉及商业内容，建议要求提供市场分析")
        
        if content_features.get("has_legal_terms"):
            suggestions.append("包含法律内容，建议要求进行合规性检查")
        
        # 基于目标输出的建议
        if target_output:
            if "JSON" in target_output:
                suggestions.append("目标输出为JSON格式，建议明确指定输出结构")
            if "详细" in target_output:
                suggestions.append("要求详细输出，建议增加分析维度")
        
        return suggestions[:5]  # 最多返回5个建议 