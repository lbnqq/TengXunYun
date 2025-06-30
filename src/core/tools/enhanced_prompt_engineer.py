#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Prompt Engineer - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import defaultdict
import logging


class PromptType(Enum):
    """Prompt类型枚举"""
    ANALYSIS = "analysis"           # 分析类
    GENERATION = "generation"       # 生成类
    REVIEW = "review"              # 审阅类
    OPTIMIZATION = "optimization"   # 优化类
    CLASSIFICATION = "classification"  # 分类类
    SUMMARIZATION = "summarization"  # 总结类


class PromptStyle(Enum):
    """Prompt风格枚举"""
    FORMAL = "formal"              # 正式风格
    CONVERSATIONAL = "conversational"  # 对话风格
    TECHNICAL = "technical"        # 技术风格
    CREATIVE = "creative"          # 创意风格
    CONCISE = "concise"           # 简洁风格
    DETAILED = "detailed"         # 详细风格


@dataclass
class PromptTemplate:
    """Prompt模板定义"""
    template_id: str
    name: str
    description: str
    prompt_type: PromptType
    prompt_style: PromptStyle
    template: str
    variables: List[str]
    optimization_tips: List[str]
    quality_criteria: List[str]
    examples: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationStrategy:
    """优化策略定义"""
    strategy_id: str
    name: str
    description: str
    rules: List[str]
    parameters: Dict[str, Any]
    effectiveness_score: float = 0.0


@dataclass
class QualityAssessment:
    """质量评估结果"""
    clarity_score: float
    specificity_score: float
    structure_score: float
    context_score: float
    output_format_score: float
    overall_score: float
    suggestions: List[str] = field(default_factory=list)


class EnhancedPromptEngineer:
    """
    增强Prompt工程师
    
    专门针对讯飞星火模型进行prompt优化，提供多种优化策略和质量评估。
    
    Attributes:
        templates: Prompt模板存储
        strategies: 优化策略存储
        performance_stats: 性能统计
        lock: 线程锁
        logger: 日志记录器
    """
    
    def __init__(self):
        """初始化增强Prompt工程师"""
        self.templates = {}
        self.strategies = {}
        self.performance_stats = defaultdict(int)
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # 初始化默认模板和策略
        self._initialize_default_templates()
        self._initialize_optimization_strategies()
    
    def _initialize_default_templates(self):
        """初始化默认Prompt模板"""
        # 分析类模板
        self._create_analysis_templates()
        
        # 生成类模板
        self._create_generation_templates()
        
        # 审阅类模板
        self._create_review_templates()
        
        # 优化类模板
        self._create_optimization_templates()
    
    def _create_analysis_templates(self):
        """创建分析类模板"""
        # 技术分析模板
        tech_analysis = PromptTemplate(
            template_id="tech_analysis_v1.0",
            name="技术分析模板",
            description="适用于技术文档、系统架构等技术内容的分析",
            prompt_type=PromptType.ANALYSIS,
            prompt_style=PromptStyle.TECHNICAL,
            template="""作为资深技术专家，请对以下技术内容进行专业分析：

内容：{content}

请从以下维度进行分析：
1. 技术可行性评估
2. 架构设计合理性
3. 性能影响分析
4. 风险评估和缓解措施
5. 实施建议和最佳实践

请提供结构化的技术分析报告，包含具体的技术指标和可操作的建议。""",
            variables=["content"],
            optimization_tips=[
                "明确技术指标和评估标准",
                "提供量化的性能分析",
                "识别潜在技术风险",
                "给出具体的实施建议"
            ],
            quality_criteria=[
                "技术分析的专业性和准确性",
                "评估维度的全面性",
                "建议的可操作性",
                "输出格式的规范性"
            ],
            examples=[
                {
                    "input": "微服务架构设计方案",
                    "output": "包含可行性评估、架构分析、性能影响、风险识别等结构化技术分析"
                }
            ]
        )
        self.templates[tech_analysis.template_id] = tech_analysis
        
        # 商业分析模板
        business_analysis = PromptTemplate(
            template_id="business_analysis_v1.0",
            name="商业分析模板",
            description="适用于商业计划、市场分析等商业内容的分析",
            prompt_type=PromptType.ANALYSIS,
            prompt_style=PromptStyle.FORMAL,
            template="""作为资深商业顾问，请对以下商业内容进行专业分析：

内容：{content}

请从以下维度进行分析：
1. 市场机会评估
2. 竞争优势分析
3. 商业模式可行性
4. 财务预测合理性
5. 风险因素识别

请提供详细的商业分析报告，包含市场数据支持和投资建议。""",
            variables=["content"],
            optimization_tips=[
                "提供具体的市场数据支持",
                "分析竞争对手情况",
                "给出量化的财务预测",
                "识别关键风险因素"
            ],
            quality_criteria=[
                "市场分析的准确性",
                "竞争优势的识别",
                "财务预测的合理性",
                "风险评估的全面性"
            ],
            examples=[
                {
                    "input": "新产品市场推广计划",
                    "output": "包含市场分析、竞争评估、财务预测、风险识别等商业分析"
                }
            ]
        )
        self.templates[business_analysis.template_id] = business_analysis
    
    def _create_generation_templates(self):
        """创建生成类模板"""
        # 内容生成模板
        content_generation = PromptTemplate(
            template_id="content_generation_v1.0",
            name="内容生成模板",
            description="适用于文档内容、报告等内容的生成",
            prompt_type=PromptType.GENERATION,
            prompt_style=PromptStyle.DETAILED,
            template="""请根据以下要求生成专业内容：

主题：{topic}
要求：{requirements}
格式：{format}

请确保生成的内容：
1. 符合主题要求
2. 结构清晰合理
3. 内容详实准确
4. 表达专业规范
5. 满足格式要求

请生成高质量的内容。""",
            variables=["topic", "requirements", "format"],
            optimization_tips=[
                "明确内容主题和要求",
                "确保结构清晰合理",
                "使用专业规范表达",
                "满足指定格式要求"
            ],
            quality_criteria=[
                "内容的准确性和专业性",
                "结构的清晰性和逻辑性",
                "表达的规范性和可读性",
                "格式的符合性"
            ],
            examples=[
                {
                    "input": "技术报告生成",
                    "output": "结构清晰、内容专业、格式规范的技术报告"
                }
            ]
        )
        self.templates[content_generation.template_id] = content_generation
    
    def _create_review_templates(self):
        """创建审阅类模板"""
        # 文档审阅模板
        document_review = PromptTemplate(
            template_id="document_review_v1.0",
            name="文档审阅模板",
            description="适用于各类文档的审阅和质量评估",
            prompt_type=PromptType.REVIEW,
            prompt_style=PromptStyle.FORMAL,
            template="""作为专业审阅员，请对以下文档进行质量审阅：

文档内容：{content}
审阅重点：{focus_areas}

请从以下方面进行审阅：
1. 内容准确性
2. 结构完整性
3. 表达清晰度
4. 格式规范性
5. 逻辑一致性

请提供详细的审阅报告，包含问题识别和改进建议。""",
            variables=["content", "focus_areas"],
            optimization_tips=[
                "明确审阅重点和要求",
                "系统性地检查各个方面",
                "提供具体的改进建议",
                "确保审阅的客观性"
            ],
            quality_criteria=[
                "审阅的全面性和准确性",
                "问题识别的准确性",
                "建议的实用性和可操作性",
                "报告的客观性和专业性"
            ],
            examples=[
                {
                    "input": "技术文档审阅",
                    "output": "包含准确性检查、结构评估、改进建议等审阅报告"
                }
            ]
        )
        self.templates[document_review.template_id] = document_review
    
    def _create_optimization_templates(self):
        """创建优化类模板"""
        # 内容优化模板
        content_optimization = PromptTemplate(
            template_id="content_optimization_v1.0",
            name="内容优化模板",
            description="适用于文档内容、表达方式的优化",
            prompt_type=PromptType.OPTIMIZATION,
            prompt_style=PromptStyle.CONCISE,
            template="""请对以下内容进行优化：

原始内容：{original_content}
优化目标：{optimization_goals}

请从以下方面进行优化：
1. 表达清晰度
2. 逻辑结构
3. 专业术语使用
4. 可读性提升
5. 目标达成度

请提供优化后的内容。""",
            variables=["original_content", "optimization_goals"],
            optimization_tips=[
                "明确优化目标和要求",
                "保持内容核心不变",
                "提升表达清晰度",
                "优化逻辑结构"
            ],
            quality_criteria=[
                "优化效果的明显性",
                "内容核心的保持",
                "表达质量的提升",
                "目标达成的程度"
            ],
            examples=[
                {
                    "input": "技术文档优化",
                    "output": "表达更清晰、结构更合理、可读性更强的优化内容"
                }
            ]
        )
        self.templates[content_optimization.template_id] = content_optimization
    
    def _initialize_optimization_strategies(self):
        """初始化优化策略"""
        # 清晰度优化策略
        clarity_strategy = OptimizationStrategy(
            strategy_id="clarity_optimization",
            name="清晰度优化",
            description="优化prompt的清晰度和可理解性",
            rules=[
                "使用简洁明了的语言",
                "避免歧义和模糊表达",
                "明确任务要求和期望",
                "提供具体的指导"
            ],
            parameters={
                "max_sentence_length": 25,
                "use_active_voice": True,
                "avoid_jargon": True,
                "provide_examples": True
            },
            effectiveness_score=0.85
        )
        self.strategies[clarity_strategy.strategy_id] = clarity_strategy
        
        # 特异性优化策略
        specificity_strategy = OptimizationStrategy(
            strategy_id="specificity_optimization",
            name="特异性优化",
            description="提高prompt的特定性和精确性",
            rules=[
                "提供具体的参数和要求",
                "明确输出格式和结构",
                "指定质量标准",
                "包含约束条件"
            ],
            parameters={
                "require_specific_output": True,
                "include_format_specification": True,
                "specify_quality_criteria": True,
                "add_constraints": True
            },
            effectiveness_score=0.82
        )
        self.strategies[specificity_strategy.strategy_id] = specificity_strategy
        
        # 结构化优化策略
        structure_strategy = OptimizationStrategy(
            strategy_id="structure_optimization",
            name="结构化优化",
            description="优化prompt的结构和组织",
            rules=[
                "使用清晰的层次结构",
                "按逻辑顺序组织内容",
                "使用编号和列表",
                "突出重要信息"
            ],
            parameters={
                "use_numbering": True,
                "organize_logically": True,
                "highlight_key_points": True,
                "use_sections": True
            },
            effectiveness_score=0.88
        )
        self.strategies[structure_strategy.strategy_id] = structure_strategy
        
        # 上下文优化策略
        context_strategy = OptimizationStrategy(
            strategy_id="context_optimization",
            name="上下文优化",
            description="增强prompt的上下文信息",
            rules=[
                "提供背景信息",
                "明确角色定位",
                "说明任务目的",
                "包含相关约束"
            ],
            parameters={
                "include_background": True,
                "specify_role": True,
                "state_purpose": True,
                "add_constraints": True
            },
            effectiveness_score=0.80
        )
        self.strategies[context_strategy.strategy_id] = context_strategy
        
        # 输出格式优化策略
        output_format_strategy = OptimizationStrategy(
            strategy_id="output_format_optimization",
            name="输出格式优化",
            description="优化输出格式要求",
            rules=[
                "明确输出格式",
                "指定结构要求",
                "提供格式示例",
                "设置质量标准"
            ],
            parameters={
                "specify_format": True,
                "require_structure": True,
                "provide_examples": True,
                "set_quality_standards": True
            },
            effectiveness_score=0.87
        )
        self.strategies[output_format_strategy.strategy_id] = output_format_strategy
    
    def optimize_prompt(self, original_prompt: str, prompt_type: PromptType,
                       prompt_style: PromptStyle, optimization_goals: List[str]) -> str:
        """
        优化Prompt
        
        Args:
            original_prompt: 原始prompt
            prompt_type: prompt类型
            prompt_style: prompt风格
            optimization_goals: 优化目标
            
        Returns:
            优化后的prompt
        """
        optimized_prompt = original_prompt
        
        # 应用优化策略
        for goal in optimization_goals:
            if goal in self.strategies:
                strategy = self.strategies[goal]
                optimized_prompt = self._apply_strategy(optimized_prompt, strategy)
        
        # 根据类型和风格进行调整
        optimized_prompt = self._adjust_for_type_and_style(
            optimized_prompt, prompt_type, prompt_style
        )
        
        return optimized_prompt
    
    def _apply_strategy(self, prompt: str, strategy: OptimizationStrategy) -> str:
        """
        应用优化策略
        
        Args:
            prompt: 原始prompt
            strategy: 优化策略
            
        Returns:
            应用策略后的prompt
        """
        optimized_prompt = prompt
        
        # 根据策略规则进行优化
        for rule in strategy.rules:
            if "清晰度" in rule:
                optimized_prompt = self._optimize_clarity(optimized_prompt)
            elif "特异性" in rule:
                optimized_prompt = self._optimize_specificity(optimized_prompt)
            elif "结构化" in rule:
                optimized_prompt = self._optimize_structure(optimized_prompt)
            elif "上下文" in rule:
                optimized_prompt = self._optimize_context(optimized_prompt)
            elif "输出格式" in rule:
                optimized_prompt = self._optimize_output_format(optimized_prompt)
        
        return optimized_prompt
    
    def _optimize_clarity(self, prompt: str) -> str:
        """优化清晰度"""
        # 简化复杂句子
        sentences = prompt.split('。')
        optimized_sentences = []
        
        for sentence in sentences:
            if len(sentence) > 30:  # 长句子优化
                # 尝试分割长句
                parts = sentence.split('，')
                if len(parts) > 2:
                    optimized_sentences.extend(parts)
                else:
                    optimized_sentences.append(sentence)
            else:
                optimized_sentences.append(sentence)
        
        return '。'.join(optimized_sentences)
    
    def _optimize_specificity(self, prompt: str) -> str:
        """优化特异性"""
        # 添加具体的指导
        if "请" in prompt and "分析" in prompt:
            prompt += "\n\n具体要求：\n1. 提供具体的分析维度\n2. 给出量化的评估结果\n3. 包含可操作的建议"
        
        return prompt
    
    def _optimize_structure(self, prompt: str) -> str:
        """优化结构"""
        # 添加结构化的组织
        if "请从以下方面" in prompt:
            # 已经是结构化格式
            return prompt
        else:
            # 添加结构化组织
            prompt += "\n\n请从以下方面进行分析：\n1. \n2. \n3. \n4. \n5. "
        
        return prompt
    
    def _optimize_context(self, prompt: str) -> str:
        """优化上下文"""
        # 添加角色定位
        if "作为" not in prompt:
            prompt = "作为专业分析师，" + prompt
        
        return prompt
    
    def _optimize_output_format(self, prompt: str) -> str:
        """优化输出格式"""
        # 添加输出格式要求
        if "请提供" in prompt and "格式" not in prompt:
            prompt += "\n\n请提供结构化的输出格式，包含具体的分析结果和建议。"
        
        return prompt
    
    def _adjust_for_type_and_style(self, prompt: str, prompt_type: PromptType,
                                  prompt_style: PromptStyle) -> str:
        """
        根据类型和风格调整prompt
        
        Args:
            prompt: 原始prompt
            prompt_type: prompt类型
            prompt_style: prompt风格
            
        Returns:
            调整后的prompt
        """
        adjusted_prompt = prompt
        
        # 根据类型调整
        if prompt_type == PromptType.ANALYSIS:
            if "分析" not in adjusted_prompt:
                adjusted_prompt += "\n\n请进行深入分析并提供详细的分析报告。"
        elif prompt_type == PromptType.GENERATION:
            if "生成" not in adjusted_prompt:
                adjusted_prompt += "\n\n请生成高质量的内容。"
        elif prompt_type == PromptType.REVIEW:
            if "审阅" not in adjusted_prompt:
                adjusted_prompt += "\n\n请进行专业审阅并提供审阅报告。"
        
        # 根据风格调整
        if prompt_style == PromptStyle.FORMAL:
            # 确保正式风格
            if "请" not in adjusted_prompt:
                adjusted_prompt = "请" + adjusted_prompt
        elif prompt_style == PromptStyle.TECHNICAL:
            # 确保技术风格
            if "专业" not in adjusted_prompt:
                adjusted_prompt += "\n\n请使用专业的技术术语和分析方法。"
        elif prompt_style == PromptStyle.CONCISE:
            # 确保简洁风格
            # 移除冗余表达
            adjusted_prompt = adjusted_prompt.replace("请进行深入分析并提供详细的分析报告", "请分析")
        
        return adjusted_prompt
    
    def assess_quality(self, prompt: str) -> QualityAssessment:
        """
        评估prompt质量
        
        Args:
            prompt: 待评估的prompt
            
        Returns:
            质量评估结果
        """
        # 清晰度评估
        clarity_score = self._assess_clarity(prompt)
        
        # 特异性评估
        specificity_score = self._assess_specificity(prompt)
        
        # 结构化评估
        structure_score = self._assess_structure(prompt)
        
        # 上下文评估
        context_score = self._assess_context(prompt)
        
        # 输出格式评估
        output_format_score = self._assess_output_format(prompt)
        
        # 计算总体分数
        overall_score = (clarity_score + specificity_score + structure_score + 
                        context_score + output_format_score) / 5
        
        # 生成改进建议
        suggestions = self._generate_quality_suggestions(
            clarity_score, specificity_score, structure_score,
            context_score, output_format_score
        )
        
        return QualityAssessment(
            clarity_score=clarity_score,
            specificity_score=specificity_score,
            structure_score=structure_score,
            context_score=context_score,
            output_format_score=output_format_score,
            overall_score=overall_score,
            suggestions=suggestions
        )
    
    def _assess_clarity(self, prompt: str) -> float:
        """评估清晰度"""
        score = 0.8  # 基础分数
        
        # 检查句子长度
        sentences = prompt.split('。')
        long_sentences = [s for s in sentences if len(s) > 30]
        if len(long_sentences) > 0:
            score -= 0.1 * len(long_sentences)
        
        # 检查是否有歧义词汇
        ambiguous_words = ['可能', '也许', '大概', '差不多']
        for word in ambiguous_words:
            if word in prompt:
                score -= 0.05
        
        # 检查是否有明确的任务描述
        if '请' in prompt and ('分析' in prompt or '生成' in prompt or '审阅' in prompt):
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _assess_specificity(self, prompt: str) -> float:
        """评估特异性"""
        score = 0.7  # 基础分数
        
        # 检查是否有具体的参数
        if any(word in prompt for word in ['具体', '详细', '明确']):
            score += 0.1
        
        # 检查是否有输出格式要求
        if any(word in prompt for word in ['格式', '结构', '报告']):
            score += 0.1
        
        # 检查是否有质量标准
        if any(word in prompt for word in ['质量', '标准', '要求']):
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _assess_structure(self, prompt: str) -> float:
        """评估结构化程度"""
        score = 0.6  # 基础分数
        
        # 检查是否有编号列表
        if any(char.isdigit() + '.' in prompt for char in prompt):
            score += 0.2
        
        # 检查是否有分段
        if '\n\n' in prompt:
            score += 0.1
        
        # 检查是否有层次结构
        if any(word in prompt for word in ['首先', '其次', '最后', '第一', '第二']):
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _assess_context(self, prompt: str) -> float:
        """评估上下文信息"""
        score = 0.5  # 基础分数
        
        # 检查是否有角色定位
        if '作为' in prompt:
            score += 0.2
        
        # 检查是否有背景信息
        if any(word in prompt for word in ['背景', '情况', '环境']):
            score += 0.2
        
        # 检查是否有目的说明
        if any(word in prompt for word in ['目的', '目标', '要求']):
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _assess_output_format(self, prompt: str) -> float:
        """评估输出格式要求"""
        score = 0.6  # 基础分数
        
        # 检查是否有格式要求
        if any(word in prompt for word in ['格式', '结构', '报告']):
            score += 0.2
        
        # 检查是否有具体输出类型
        if any(word in prompt for word in ['JSON', 'XML', '表格', '列表']):
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _generate_quality_suggestions(self, clarity_score: float, specificity_score: float,
                                    structure_score: float, context_score: float,
                                    output_format_score: float) -> List[str]:
        """生成质量改进建议"""
        suggestions = []
        
        if clarity_score < 0.7:
            suggestions.append("建议简化复杂句子，使用更清晰的语言表达")
        
        if specificity_score < 0.7:
            suggestions.append("建议添加具体的参数和要求，明确输出格式")
        
        if structure_score < 0.7:
            suggestions.append("建议使用编号列表和分段，提高结构化程度")
        
        if context_score < 0.7:
            suggestions.append("建议添加角色定位和背景信息")
        
        if output_format_score < 0.7:
            suggestions.append("建议明确输出格式和结构要求")
        
        return suggestions
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        获取指定模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板对象，如果不存在则返回None
        """
        return self.templates.get(template_id)
    
    def get_templates_by_type(self, prompt_type: PromptType) -> List[PromptTemplate]:
        """
        根据类型获取模板列表
        
        Args:
            prompt_type: prompt类型
            
        Returns:
            模板列表
        """
        return [
            template for template in self.templates.values()
            if template.prompt_type == prompt_type
        ]
    
    def get_optimization_strategies(self) -> List[OptimizationStrategy]:
        """
        获取所有优化策略
        
        Returns:
            优化策略列表
        """
        return list(self.strategies.values())
    
    def create_custom_template(self, template: PromptTemplate) -> str:
        """
        创建自定义模板
        
        Args:
            template: 模板对象
            
        Returns:
            模板ID
        """
        if template.template_id in self.templates:
            raise ValueError(f"模板ID已存在: {template.template_id}")
        
        with self.lock:
            self.templates[template.template_id] = template
        
        self.logger.info(f"自定义模板已创建: {template.template_id}")
        return template.template_id
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        获取性能统计信息
        
        Returns:
            统计信息字典
        """
        with self.lock:
            return {
                "total_templates": len(self.templates),
                "total_strategies": len(self.strategies),
                "templates_by_type": defaultdict(int),
                "templates_by_style": defaultdict(int),
                "strategy_effectiveness": {
                    strategy_id: strategy.effectiveness_score
                    for strategy_id, strategy in self.strategies.items()
                }
            } 