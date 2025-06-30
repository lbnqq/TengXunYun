#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scenario Template Manager - 核心模块

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
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import defaultdict
import logging
from datetime import datetime


class TemplateCategory(Enum):
    """模板类别枚举"""
    TECHNICAL_REPORT = "technical_report"
    BUSINESS_PROPOSAL = "business_proposal"
    CONTRACT_REVIEW = "contract_review"
    ACADEMIC_PAPER = "academic_paper"
    GOVERNMENT_DOCUMENT = "government_document"
    MEETING_MINUTES = "meeting_minutes"
    MARKET_ANALYSIS = "market_analysis"
    GENERAL_DOCUMENT = "general_document"


class OutputFormat(Enum):
    """输出格式枚举"""
    JSON = "json"
    XML = "xml"
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"
    STRUCTURED_TEXT = "structured_text"


@dataclass
class QualityStandard:
    """质量标准定义"""
    name: str
    description: str
    criteria: List[str]
    weight: float = 1.0
    threshold: float = 0.8


@dataclass
class BusinessRule:
    """业务规则定义"""
    rule_id: str
    name: str
    description: str
    conditions: List[str]
    actions: List[str]
    priority: int = 1
    enabled: bool = True


@dataclass
class TemplateExample:
    """模板示例定义"""
    example_id: str
    title: str
    description: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    quality_score: float
    tags: List[str] = field(default_factory=list)


@dataclass
class ScenarioTemplate:
    """场景模板定义"""
    template_id: str
    category: TemplateCategory
    name: str
    description: str
    version: str
    created_at: float
    updated_at: float
    
    # 模板内容
    prompt_template: str
    variables: List[str]
    output_format: OutputFormat
    output_schema: Dict[str, Any]
    
    # 质量标准
    quality_standards: List[QualityStandard]
    
    # 业务规则
    business_rules: List[BusinessRule]
    
    # 示例
    examples: List[TemplateExample]
    
    # 配置
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ScenarioTemplateManager:
    """
    场景模板管理器
    
    管理关键业务场景的模板，提供模板的创建、更新、查询和应用功能。
    
    Attributes:
        templates: 模板存储字典
        lock: 线程锁
        logger: 日志记录器
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化场景模板管理器
        
        Args:
            storage_path: 模板存储路径，如果为None则使用内存存储
        """
        self.storage_path = storage_path
        self.templates = {}
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # 初始化默认模板
        self._initialize_default_templates()
        
        # 加载自定义模板
        if storage_path:
            self._load_templates()
    
    def _initialize_default_templates(self):
        """初始化默认模板"""
        # 技术报告模板
        self._create_technical_report_template()
        
        # 商业提案模板
        self._create_business_proposal_template()
        
        # 合同审阅模板
        self._create_contract_review_template()
        
        # 学术论文模板
        self._create_academic_paper_template()
        
        # 政府文档模板
        self._create_government_document_template()
    
    def _create_technical_report_template(self):
        """创建技术报告模板"""
        template_id = "tech_report_v1.0"
        
        quality_standards = [
            QualityStandard(
                name="技术准确性",
                description="技术内容的准确性和专业性",
                criteria=[
                    "技术概念使用准确",
                    "数据来源可靠",
                    "分析方法科学",
                    "结论合理"
                ],
                weight=0.3,
                threshold=0.85
            ),
            QualityStandard(
                name="结构完整性",
                description="报告结构的完整性和逻辑性",
                criteria=[
                    "章节结构清晰",
                    "内容逻辑连贯",
                    "信息覆盖全面",
                    "重点突出"
                ],
                weight=0.25,
                threshold=0.8
            ),
            QualityStandard(
                name="可读性",
                description="报告的可读性和表达清晰度",
                criteria=[
                    "语言表达清晰",
                    "图表使用恰当",
                    "专业术语解释",
                    "格式规范"
                ],
                weight=0.2,
                threshold=0.8
            ),
            QualityStandard(
                name="实用性",
                description="报告的实用价值和可操作性",
                criteria=[
                    "建议具体可行",
                    "风险评估全面",
                    "资源需求明确",
                    "时间规划合理"
                ],
                weight=0.25,
                threshold=0.8
            )
        ]
        
        business_rules = [
            BusinessRule(
                rule_id="tech_rule_001",
                name="技术风险评估",
                description="必须包含技术风险评估",
                conditions=["报告类型为技术报告"],
                actions=["添加风险评估章节", "识别技术风险点", "提供缓解措施"],
                priority=1
            ),
            BusinessRule(
                rule_id="tech_rule_002",
                name="资源需求分析",
                description="必须包含资源需求分析",
                conditions=["报告涉及项目实施"],
                actions=["分析人力资源需求", "评估技术资源需求", "计算成本预算"],
                priority=2
            )
        ]
        
        examples = [
            TemplateExample(
                example_id="tech_example_001",
                title="系统架构技术报告",
                description="关于新系统架构设计的技术报告示例",
                input_data={
                    "project_name": "企业级微服务架构",
                    "requirements": "高可用、可扩展、易维护",
                    "constraints": "预算限制、时间要求"
                },
                expected_output={
                    "technical_analysis": {
                        "architecture_overview": "微服务架构设计",
                        "technology_stack": ["Spring Cloud", "Docker", "Kubernetes"],
                        "scalability_analysis": "水平扩展能力评估"
                    },
                    "risk_assessment": {
                        "technical_risks": ["服务间通信复杂性", "数据一致性挑战"],
                        "mitigation_strategies": ["API网关", "分布式事务"]
                    },
                    "resource_requirements": {
                        "human_resources": "5-8人开发团队",
                        "technical_resources": "云服务器、数据库、监控工具",
                        "timeline": "6-8个月"
                    }
                },
                quality_score=0.92,
                tags=["架构设计", "微服务", "技术评估"]
            )
        ]
        
        template = ScenarioTemplate(
            template_id=template_id,
            category=TemplateCategory.TECHNICAL_REPORT,
            name="技术报告标准模板",
            description="适用于技术项目评估、系统设计、技术可行性分析等场景",
            version="1.0",
            created_at=time.time(),
            updated_at=time.time(),
            prompt_template="""你是一位资深技术专家，请根据以下信息生成专业的技术报告：

项目信息：
- 项目名称：{project_name}
- 技术需求：{requirements}
- 约束条件：{constraints}

请从以下方面进行分析：
1. 技术方案设计
2. 技术可行性评估
3. 风险评估和缓解措施
4. 资源需求分析
5. 实施计划和时间安排
6. 质量保证措施

请提供结构化的技术报告，包含具体的技术指标和可操作的建议。""",
            variables=["project_name", "requirements", "constraints"],
            output_format=OutputFormat.JSON,
            output_schema={
                "type": "object",
                "properties": {
                    "technical_analysis": {
                        "type": "object",
                        "properties": {
                            "architecture_overview": {"type": "string"},
                            "technology_stack": {"type": "array", "items": {"type": "string"}},
                            "scalability_analysis": {"type": "string"}
                        }
                    },
                    "risk_assessment": {
                        "type": "object",
                        "properties": {
                            "technical_risks": {"type": "array", "items": {"type": "string"}},
                            "mitigation_strategies": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "resource_requirements": {
                        "type": "object",
                        "properties": {
                            "human_resources": {"type": "string"},
                            "technical_resources": {"type": "string"},
                            "timeline": {"type": "string"}
                        }
                    }
                }
            },
            quality_standards=quality_standards,
            business_rules=business_rules,
            examples=examples,
            config={
                "max_length": 5000,
                "include_charts": True,
                "require_citations": True
            }
        )
        
        self.templates[template_id] = template
    
    def _create_business_proposal_template(self):
        """创建商业提案模板"""
        template_id = "business_proposal_v1.0"
        
        quality_standards = [
            QualityStandard(
                name="市场分析准确性",
                description="市场分析的准确性和深度",
                criteria=[
                    "市场数据准确",
                    "竞争分析全面",
                    "机会识别准确",
                    "趋势预测合理"
                ],
                weight=0.25,
                threshold=0.85
            ),
            QualityStandard(
                name="商业价值",
                description="商业价值的清晰度和说服力",
                criteria=[
                    "价值主张清晰",
                    "收益预测合理",
                    "投资回报明确",
                    "竞争优势突出"
                ],
                weight=0.3,
                threshold=0.85
            ),
            QualityStandard(
                name="可行性",
                description="商业模式的可行性",
                criteria=[
                    "商业模式清晰",
                    "实施路径可行",
                    "风险控制合理",
                    "资源需求明确"
                ],
                weight=0.25,
                threshold=0.8
            ),
            QualityStandard(
                name="表达质量",
                description="提案的表达质量和专业性",
                criteria=[
                    "结构清晰",
                    "语言专业",
                    "数据可视化",
                    "逻辑连贯"
                ],
                weight=0.2,
                threshold=0.8
            )
        ]
        
        business_rules = [
            BusinessRule(
                rule_id="business_rule_001",
                name="市场分析",
                description="必须包含市场分析",
                conditions=["提案类型为商业提案"],
                actions=["分析目标市场", "评估市场规模", "识别市场机会"],
                priority=1
            ),
            BusinessRule(
                rule_id="business_rule_002",
                name="财务预测",
                description="必须包含财务预测",
                conditions=["提案涉及投资"],
                actions=["收入预测", "成本分析", "利润计算", "投资回报分析"],
                priority=1
            )
        ]
        
        examples = [
            TemplateExample(
                example_id="business_example_001",
                title="新产品市场推广提案",
                description="关于新产品市场推广的商业提案示例",
                input_data={
                    "product_name": "智能办公助手",
                    "target_market": "中小企业",
                    "investment_amount": "500万元"
                },
                expected_output={
                    "market_analysis": {
                        "market_size": "100亿元",
                        "target_segment": "中小企业办公自动化需求",
                        "growth_rate": "15%年增长率"
                    },
                    "competitive_advantage": {
                        "unique_features": ["AI智能分析", "云端协作", "移动办公"],
                        "competitive_position": "技术领先，用户体验优秀"
                    },
                    "financial_projections": {
                        "revenue_forecast": "3年内达到5000万元",
                        "profit_margin": "30%",
                        "roi": "300%"
                    }
                },
                quality_score=0.88,
                tags=["市场推广", "新产品", "投资分析"]
            )
        ]
        
        template = ScenarioTemplate(
            template_id=template_id,
            category=TemplateCategory.BUSINESS_PROPOSAL,
            name="商业提案标准模板",
            description="适用于产品推广、投资提案、商业合作等场景",
            version="1.0",
            created_at=time.time(),
            updated_at=time.time(),
            prompt_template="""你是一位经验丰富的商业顾问，请根据以下信息生成专业的商业提案：

项目信息：
- 产品/服务名称：{product_name}
- 目标市场：{target_market}
- 投资金额：{investment_amount}

请从以下维度进行分析：
1. 市场机会分析
2. 竞争优势评估
3. 商业模式设计
4. 财务预测和投资回报
5. 风险因素识别
6. 实施策略和计划

请提供详细的商业分析报告，包含市场数据支持和投资建议。""",
            variables=["product_name", "target_market", "investment_amount"],
            output_format=OutputFormat.JSON,
            output_schema={
                "type": "object",
                "properties": {
                    "market_analysis": {
                        "type": "object",
                        "properties": {
                            "market_size": {"type": "string"},
                            "target_segment": {"type": "string"},
                            "growth_rate": {"type": "string"}
                        }
                    },
                    "competitive_advantage": {
                        "type": "object",
                        "properties": {
                            "unique_features": {"type": "array", "items": {"type": "string"}},
                            "competitive_position": {"type": "string"}
                        }
                    },
                    "financial_projections": {
                        "type": "object",
                        "properties": {
                            "revenue_forecast": {"type": "string"},
                            "profit_margin": {"type": "string"},
                            "roi": {"type": "string"}
                        }
                    }
                }
            },
            quality_standards=quality_standards,
            business_rules=business_rules,
            examples=examples,
            config={
                "max_length": 4000,
                "include_charts": True,
                "require_market_data": True
            }
        )
        
        self.templates[template_id] = template
    
    def _create_contract_review_template(self):
        """创建合同审阅模板"""
        template_id = "contract_review_v1.0"
        
        quality_standards = [
            QualityStandard(
                name="法律准确性",
                description="法律分析的准确性",
                criteria=[
                    "法律条款准确",
                    "法规引用正确",
                    "风险识别全面",
                    "建议合法有效"
                ],
                weight=0.4,
                threshold=0.9
            ),
            QualityStandard(
                name="风险识别",
                description="合同风险识别的全面性",
                criteria=[
                    "风险点识别准确",
                    "风险等级评估合理",
                    "风险影响分析深入",
                    "风险控制建议可行"
                ],
                weight=0.3,
                threshold=0.85
            ),
            QualityStandard(
                name="实用性",
                description="审阅意见的实用性",
                criteria=[
                    "修改建议具体",
                    "条款优化可行",
                    "操作指导明确",
                    "成本效益合理"
                ],
                weight=0.3,
                threshold=0.8
            )
        ]
        
        business_rules = [
            BusinessRule(
                rule_id="contract_rule_001",
                name="法律风险检查",
                description="必须检查法律风险",
                conditions=["文档类型为合同"],
                actions=["识别法律风险点", "评估风险等级", "提供修改建议"],
                priority=1
            ),
            BusinessRule(
                rule_id="contract_rule_002",
                name="条款平衡性",
                description="检查条款平衡性",
                conditions=["合同涉及双方权利义务"],
                actions=["分析权利义务平衡", "识别不公平条款", "建议平衡方案"],
                priority=2
            )
        ]
        
        examples = [
            TemplateExample(
                example_id="contract_example_001",
                title="技术合作协议审阅",
                description="技术合作协议的法律风险审阅示例",
                input_data={
                    "contract_type": "技术合作协议",
                    "parties": ["甲方：技术公司", "乙方：客户公司"],
                    "key_terms": ["技术转让", "知识产权", "保密条款"]
                },
                expected_output={
                    "legal_analysis": {
                        "contract_validity": "合同整体有效",
                        "key_legal_issues": ["知识产权归属", "保密义务期限"],
                        "compliance_status": "基本符合相关法规"
                    },
                    "risk_assessment": {
                        "high_risks": ["知识产权争议风险"],
                        "medium_risks": ["保密条款执行风险"],
                        "low_risks": ["付款条款风险"]
                    },
                    "modification_suggestions": {
                        "critical_changes": ["明确知识产权归属条款"],
                        "recommended_changes": ["细化保密义务范围"],
                        "optional_changes": ["增加争议解决机制"]
                    }
                },
                quality_score=0.95,
                tags=["合同审阅", "法律风险", "技术合作"]
            )
        ]
        
        template = ScenarioTemplate(
            template_id=template_id,
            category=TemplateCategory.CONTRACT_REVIEW,
            name="合同审阅标准模板",
            description="适用于各类合同的法律风险审查和条款优化",
            version="1.0",
            created_at=time.time(),
            updated_at=time.time(),
            prompt_template="""你是一位专业的法律顾问，请对以下合同进行法律风险审查：

合同信息：
- 合同类型：{contract_type}
- 合同方：{parties}
- 关键条款：{key_terms}

请重点关注以下方面：
1. 合同条款的合法性和有效性
2. 权利义务的平衡性
3. 违约责任和争议解决机制
4. 知识产权和保密条款
5. 法律风险点识别
6. 修改建议和优化方案

请提供详细的法律审查报告，包含风险等级评估和修改建议。""",
            variables=["contract_type", "parties", "key_terms"],
            output_format=OutputFormat.JSON,
            output_schema={
                "type": "object",
                "properties": {
                    "legal_analysis": {
                        "type": "object",
                        "properties": {
                            "contract_validity": {"type": "string"},
                            "key_legal_issues": {"type": "array", "items": {"type": "string"}},
                            "compliance_status": {"type": "string"}
                        }
                    },
                    "risk_assessment": {
                        "type": "object",
                        "properties": {
                            "high_risks": {"type": "array", "items": {"type": "string"}},
                            "medium_risks": {"type": "array", "items": {"type": "string"}},
                            "low_risks": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "modification_suggestions": {
                        "type": "object",
                        "properties": {
                            "critical_changes": {"type": "array", "items": {"type": "string"}},
                            "recommended_changes": {"type": "array", "items": {"type": "string"}},
                            "optional_changes": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            },
            quality_standards=quality_standards,
            business_rules=business_rules,
            examples=examples,
            config={
                "max_length": 3000,
                "require_legal_citations": True,
                "risk_level_threshold": "medium"
            }
        )
        
        self.templates[template_id] = template
    
    def _create_academic_paper_template(self):
        """创建学术论文模板"""
        template_id = "academic_paper_v1.0"
        
        quality_standards = [
            QualityStandard(
                name="学术规范性",
                description="学术标准的符合性",
                criteria=[
                    "研究方法科学",
                    "文献引用规范",
                    "学术表达准确",
                    "格式符合标准"
                ],
                weight=0.3,
                threshold=0.9
            ),
            QualityStandard(
                name="研究质量",
                description="研究内容的质量",
                criteria=[
                    "问题定义清晰",
                    "方法选择合理",
                    "数据分析准确",
                    "结论有说服力"
                ],
                weight=0.35,
                threshold=0.85
            ),
            QualityStandard(
                name="创新性",
                description="研究的创新性",
                criteria=[
                    "研究问题新颖",
                    "方法有创新",
                    "结论有贡献",
                    "应用价值明确"
                ],
                weight=0.2,
                threshold=0.8
            ),
            QualityStandard(
                name="表达质量",
                description="论文的表达质量",
                criteria=[
                    "结构清晰",
                    "语言准确",
                    "图表恰当",
                    "逻辑连贯"
                ],
                weight=0.15,
                threshold=0.8
            )
        ]
        
        business_rules = [
            BusinessRule(
                rule_id="academic_rule_001",
                name="研究方法",
                description="必须包含研究方法",
                conditions=["文档类型为学术论文"],
                actions=["明确研究问题", "选择研究方法", "设计研究流程"],
                priority=1
            ),
            BusinessRule(
                rule_id="academic_rule_002",
                name="文献引用",
                description="必须规范文献引用",
                conditions=["论文包含参考文献"],
                actions=["检查引用格式", "验证参考文献", "确保引用准确"],
                priority=1
            )
        ]
        
        examples = [
            TemplateExample(
                example_id="academic_example_001",
                title="机器学习算法研究论文",
                description="机器学习算法研究的学术论文示例",
                input_data={
                    "research_topic": "深度学习在自然语言处理中的应用",
                    "research_method": "实验研究",
                    "data_source": "公开数据集"
                },
                expected_output={
                    "methodology_review": {
                        "research_design": "实验设计合理",
                        "data_collection": "数据来源可靠",
                        "analysis_method": "分析方法科学"
                    },
                    "data_analysis": {
                        "statistical_tests": "统计检验适当",
                        "results_interpretation": "结果解释合理",
                        "limitations": "局限性分析充分"
                    },
                    "conclusions_assessment": {
                        "conclusion_validity": "结论有效",
                        "contribution": "学术贡献明确",
                        "future_work": "未来工作方向"
                    }
                },
                quality_score=0.91,
                tags=["机器学习", "自然语言处理", "学术研究"]
            )
        ]
        
        template = ScenarioTemplate(
            template_id=template_id,
            category=TemplateCategory.ACADEMIC_PAPER,
            name="学术论文标准模板",
            description="适用于学术研究论文的审阅和质量评估",
            version="1.0",
            created_at=time.time(),
            updated_at=time.time(),
            prompt_template="""你是一位学术专家，请对以下学术论文进行专业审阅：

论文信息：
- 研究主题：{research_topic}
- 研究方法：{research_method}
- 数据来源：{data_source}

请从以下角度进行审阅：
1. 研究方法的科学性
2. 数据分析的准确性
3. 结论的合理性
4. 文献引用的规范性
5. 学术贡献和创新性
6. 论文结构和表达质量

请提供详细的学术审阅报告，包含质量评估和改进建议。""",
            variables=["research_topic", "research_method", "data_source"],
            output_format=OutputFormat.JSON,
            output_schema={
                "type": "object",
                "properties": {
                    "methodology_review": {
                        "type": "object",
                        "properties": {
                            "research_design": {"type": "string"},
                            "data_collection": {"type": "string"},
                            "analysis_method": {"type": "string"}
                        }
                    },
                    "data_analysis": {
                        "type": "object",
                        "properties": {
                            "statistical_tests": {"type": "string"},
                            "results_interpretation": {"type": "string"},
                            "limitations": {"type": "string"}
                        }
                    },
                    "conclusions_assessment": {
                        "type": "object",
                        "properties": {
                            "conclusion_validity": {"type": "string"},
                            "contribution": {"type": "string"},
                            "future_work": {"type": "string"}
                        }
                    }
                }
            },
            quality_standards=quality_standards,
            business_rules=business_rules,
            examples=examples,
            config={
                "max_length": 6000,
                "require_citations": True,
                "citation_format": "APA"
            }
        )
        
        self.templates[template_id] = template
    
    def _create_government_document_template(self):
        """创建政府文档模板"""
        template_id = "government_document_v1.0"
        
        quality_standards = [
            QualityStandard(
                name="政策合规性",
                description="政策法规的符合性",
                criteria=[
                    "政策依据准确",
                    "法规引用正确",
                    "程序符合规定",
                    "权限设置合理"
                ],
                weight=0.4,
                threshold=0.95
            ),
            QualityStandard(
                name="格式规范性",
                description="文档格式的规范性",
                criteria=[
                    "格式符合标准",
                    "结构清晰",
                    "编号规范",
                    "字体统一"
                ],
                weight=0.25,
                threshold=0.9
            ),
            QualityStandard(
                name="内容准确性",
                description="内容的准确性",
                criteria=[
                    "信息准确",
                    "数据可靠",
                    "表述清晰",
                    "逻辑合理"
                ],
                weight=0.25,
                threshold=0.85
            ),
            QualityStandard(
                name="程序完整性",
                description="程序流程的完整性",
                criteria=[
                    "程序完整",
                    "环节清晰",
                    "责任明确",
                    "时限合理"
                ],
                weight=0.1,
                threshold=0.8
            )
        ]
        
        business_rules = [
            BusinessRule(
                rule_id="gov_rule_001",
                name="政策合规检查",
                description="必须检查政策合规性",
                conditions=["文档类型为政府文档"],
                actions=["检查政策依据", "验证法规引用", "确认程序合规"],
                priority=1
            ),
            BusinessRule(
                rule_id="gov_rule_002",
                name="格式规范检查",
                description="检查格式规范性",
                conditions=["文档需要正式发布"],
                actions=["检查格式标准", "验证编号规范", "确认字体统一"],
                priority=2
            )
        ]
        
        examples = [
            TemplateExample(
                example_id="gov_example_001",
                title="政府项目申请报告",
                description="政府项目申请报告的规范性审查示例",
                input_data={
                    "project_type": "科技创新项目",
                    "applicant": "高新技术企业",
                    "funding_amount": "500万元"
                },
                expected_output={
                    "compliance_check": {
                        "policy_compliance": "符合科技创新政策",
                        "eligibility": "申请主体符合条件",
                        "documentation": "材料齐全规范"
                    },
                    "format_review": {
                        "structure": "结构符合标准",
                        "numbering": "编号规范统一",
                        "formatting": "格式符合要求"
                    },
                    "content_accuracy": {
                        "information_accuracy": "信息准确无误",
                        "data_reliability": "数据来源可靠",
                        "logic_consistency": "逻辑一致合理"
                    }
                },
                quality_score=0.93,
                tags=["政府文档", "项目申请", "合规审查"]
            )
        ]
        
        template = ScenarioTemplate(
            template_id=template_id,
            category=TemplateCategory.GOVERNMENT_DOCUMENT,
            name="政府文档标准模板",
            description="适用于政府文档的规范性审查和合规性检查",
            version="1.0",
            created_at=time.time(),
            updated_at=time.time(),
            prompt_template="""你是一位政府文档专家，请对以下政府文档进行规范性审查：

文档信息：
- 项目类型：{project_type}
- 申请主体：{applicant}
- 资金金额：{funding_amount}

请重点关注以下方面：
1. 政策法规的符合性
2. 文档格式的规范性
3. 内容表述的准确性
4. 程序流程的完整性
5. 审批权限的合理性
6. 材料要求的满足性

请提供详细的规范性审查报告，包含合规性评估和修改建议。""",
            variables=["project_type", "applicant", "funding_amount"],
            output_format=OutputFormat.JSON,
            output_schema={
                "type": "object",
                "properties": {
                    "compliance_check": {
                        "type": "object",
                        "properties": {
                            "policy_compliance": {"type": "string"},
                            "eligibility": {"type": "string"},
                            "documentation": {"type": "string"}
                        }
                    },
                    "format_review": {
                        "type": "object",
                        "properties": {
                            "structure": {"type": "string"},
                            "numbering": {"type": "string"},
                            "formatting": {"type": "string"}
                        }
                    },
                    "content_accuracy": {
                        "type": "object",
                        "properties": {
                            "information_accuracy": {"type": "string"},
                            "data_reliability": {"type": "string"},
                            "logic_consistency": {"type": "string"}
                        }
                    }
                }
            },
            quality_standards=quality_standards,
            business_rules=business_rules,
            examples=examples,
            config={
                "max_length": 4000,
                "require_policy_citations": True,
                "format_standard": "政府文档标准格式"
            }
        )
        
        self.templates[template_id] = template
    
    def get_template(self, template_id: str) -> Optional[ScenarioTemplate]:
        """
        获取指定模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板对象，如果不存在则返回None
        """
        return self.templates.get(template_id)
    
    def get_templates_by_category(self, category: TemplateCategory) -> List[ScenarioTemplate]:
        """
        根据类别获取模板列表
        
        Args:
            category: 模板类别
            
        Returns:
            模板列表
        """
        return [
            template for template in self.templates.values()
            if template.category == category
        ]
    
    def get_all_templates(self) -> List[ScenarioTemplate]:
        """
        获取所有模板
        
        Returns:
            所有模板列表
        """
        return list(self.templates.values())
    
    def create_template(self, template: ScenarioTemplate) -> str:
        """
        创建新模板
        
        Args:
            template: 模板对象
            
        Returns:
            模板ID
            
        Raises:
            ValueError: 当模板ID已存在时
        """
        if template.template_id in self.templates:
            raise ValueError(f"模板ID已存在: {template.template_id}")
        
        with self.lock:
            self.templates[template.template_id] = template
            
            # 保存到文件
            if self.storage_path:
                self._save_templates()
        
        self.logger.info(f"新模板已创建: {template.template_id}")
        return template.template_id
    
    def update_template(self, template_id: str, template: ScenarioTemplate) -> bool:
        """
        更新模板
        
        Args:
            template_id: 模板ID
            template: 更新后的模板
            
        Returns:
            是否更新成功
            
        Raises:
            ValueError: 当模板不存在时
        """
        if template_id not in self.templates:
            raise ValueError(f"模板不存在: {template_id}")
        
        with self.lock:
            template.updated_at = time.time()
            self.templates[template_id] = template
            
            # 保存到文件
            if self.storage_path:
                self._save_templates()
        
        self.logger.info(f"模板已更新: {template_id}")
        return True
    
    def delete_template(self, template_id: str) -> bool:
        """
        删除模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            是否删除成功
            
        Raises:
            ValueError: 当模板不存在时
        """
        if template_id not in self.templates:
            raise ValueError(f"模板不存在: {template_id}")
        
        with self.lock:
            del self.templates[template_id]
            
            # 保存到文件
            if self.storage_path:
                self._save_templates()
        
        self.logger.info(f"模板已删除: {template_id}")
        return True
    
    def apply_template(self, template_id: str, variables: Dict[str, Any]) -> str:
        """
        应用模板生成内容
        
        Args:
            template_id: 模板ID
            variables: 模板变量
            
        Returns:
            生成的prompt内容
            
        Raises:
            ValueError: 当模板不存在或变量不完整时
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"模板不存在: {template_id}")
        
        # 检查必要变量
        for var in template.variables:
            if var not in variables:
                raise ValueError(f"缺少必要变量: {var}")
        
        # 生成prompt
        prompt = template.prompt_template
        for var, value in variables.items():
            prompt = prompt.replace(f"{{{var}}}", str(value))
        
        return prompt
    
    def _save_templates(self):
        """保存模板到文件"""
        if not self.storage_path:
            return
        
        try:
            data = {
                "templates": {
                    template_id: asdict(template)
                    for template_id, template in self.templates.items()
                },
                "saved_at": time.time()
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存模板失败: {e}")
    
    def _load_templates(self):
        """从文件加载模板"""
        if not self.storage_path:
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载模板数据
            for template_id, template_data in data.get("templates", {}).items():
                # 转换枚举类型
                template_data["category"] = TemplateCategory(template_data["category"])
                template_data["output_format"] = OutputFormat(template_data["output_format"])
                
                # 转换质量标准
                for qs_data in template_data.get("quality_standards", []):
                    qs_data = QualityStandard(**qs_data)
                
                # 转换业务规则
                for br_data in template_data.get("business_rules", []):
                    br_data = BusinessRule(**br_data)
                
                # 转换示例
                for ex_data in template_data.get("examples", []):
                    ex_data = TemplateExample(**ex_data)
                
                template = ScenarioTemplate(**template_data)
                self.templates[template_id] = template
                
        except FileNotFoundError:
            self.logger.info("模板文件不存在，将使用默认模板")
        except Exception as e:
            self.logger.error(f"加载模板失败: {e}")
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """
        获取模板统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "total_templates": len(self.templates),
            "templates_by_category": defaultdict(int),
            "templates_by_version": defaultdict(int),
            "recent_updates": []
        }
        
        for template in self.templates.values():
            stats["templates_by_category"][template.category.value] += 1
            stats["templates_by_version"][template.version] += 1
            
            # 最近更新的模板
            if template.updated_at > time.time() - 7 * 24 * 3600:  # 一周内
                stats["recent_updates"].append({
                    "template_id": template.template_id,
                    "name": template.name,
                    "updated_at": template.updated_at
                })
        
        # 转换为普通字典
        stats["templates_by_category"] = dict(stats["templates_by_category"])
        stats["templates_by_version"] = dict(stats["templates_by_version"])
        
        return stats 