#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scenario Specific Templates - 核心模块

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


class TemplateCategory(Enum):
    """模板类别"""
    TECHNICAL_REPORT = "technical_report"
    BUSINESS_PROPOSAL = "business_proposal"
    CONTRACT_ANALYSIS = "contract_analysis"
    ACADEMIC_PAPER = "academic_paper"
    GOVERNMENT_DOCUMENT = "government_document"


@dataclass
class ScenarioTemplate:
    """场景模板数据结构"""
    template_id: str
    category: TemplateCategory
    name: str
    description: str
    version: str
    created_time: str
    updated_time: str
    prompt_template: str
    expected_output_format: Dict[str, Any]
    quality_standards: Dict[str, Any]
    business_rules: List[str]
    examples: List[Dict[str, Any]]


class ScenarioSpecificTemplates:
    """场景特定模板系统"""
    
    def __init__(self, storage_path: str = "scenario_templates"):
        self.storage_path = storage_path
        self.templates_file = os.path.join(storage_path, "scenario_templates.json")
        
        os.makedirs(storage_path, exist_ok=True)
        
        self.templates = self._load_templates()
        
        if not self.templates:
            self._create_default_templates()
    
    def get_template(self, category: TemplateCategory) -> Optional[ScenarioTemplate]:
        """获取指定类别的模板"""
        template_data = self.templates.get(category.value)
        if template_data:
            return ScenarioTemplate(**template_data)
        return None
    
    def get_all_templates(self) -> List[ScenarioTemplate]:
        """获取所有模板"""
        return [ScenarioTemplate(**data) for data in self.templates.values()]
    
    def apply_template(self, category: TemplateCategory, text: str, 
                      user_role: str = "专业分析师") -> Dict[str, Any]:
        """应用模板进行分析"""
        try:
            template = self.get_template(category)
            if not template:
                return {
                    "success": False,
                    "error": "模板不存在",
                    "message": f"未找到类别为 {category.value} 的模板"
                }
            
            full_prompt = self._build_full_prompt(template, text, user_role)
            
            return {
                "success": True,
                "template_id": template.template_id,
                "template_name": template.name,
                "prompt": full_prompt,
                "expected_format": template.expected_output_format,
                "quality_standards": template.quality_standards,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "模板应用失败"
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
            # 技术报告模板
            ScenarioTemplate(
                template_id="tech_report_v1",
                category=TemplateCategory.TECHNICAL_REPORT,
                name="技术报告智能分析模板",
                description="专门用于技术报告的结构化分析",
                version="1.0",
                created_time=datetime.now().isoformat(),
                updated_time=datetime.now().isoformat(),
                prompt_template="""
请作为技术专家，对以下技术报告进行深度分析：

文档内容：
{text}

请从以下维度进行分析：
1. 技术指标评估
2. 创新性分析
3. 可行性评估
4. 应用前景分析
5. 改进建议

请以JSON格式输出分析结果。
""",
                expected_output_format={
                    "technical_indicators": {"key_metrics": [], "performance_analysis": ""},
                    "innovation_analysis": {"innovation_points": [], "innovation_level": ""},
                    "feasibility_assessment": {"technical_feasibility": "", "risk_analysis": []},
                    "application_prospects": {"market_potential": "", "target_users": []},
                    "improvement_suggestions": {"technical_improvements": [], "optimization_focus": []}
                },
                quality_standards={"completeness": 0.9, "accuracy": 0.85, "relevance": 0.9, "clarity": 0.8},
                business_rules=["技术指标必须基于客观数据", "创新性评估需要考虑技术难度"],
                examples=[{"title": "AI技术报告分析示例", "input": "人工智能技术...", "output": {}}]
            ),
            
            # 商业提案模板
            ScenarioTemplate(
                template_id="business_proposal_v1",
                category=TemplateCategory.BUSINESS_PROPOSAL,
                name="商业提案优化分析模板",
                description="专门用于商业提案的优化分析",
                version="1.0",
                created_time=datetime.now().isoformat(),
                updated_time=datetime.now().isoformat(),
                prompt_template="""
请作为商业顾问，对以下商业提案进行专业分析：

文档内容：
{text}

请从以下维度进行分析：
1. 商业价值评估
2. 市场机会分析
3. 竞争优势识别
4. 风险评估
5. 优化建议

请以JSON格式输出分析结果。
""",
                expected_output_format={
                    "business_value": {"value_proposition": "", "business_model": ""},
                    "market_opportunity": {"market_size": "", "market_trends": []},
                    "competitive_advantage": {"core_advantages": [], "differentiation_strategy": ""},
                    "risk_assessment": {"business_risks": [], "mitigation_measures": []},
                    "optimization_suggestions": {"structure_improvements": [], "content_enhancements": []}
                },
                quality_standards={"completeness": 0.9, "accuracy": 0.85, "relevance": 0.9, "clarity": 0.8},
                business_rules=["商业价值评估要基于客观数据", "市场分析要结合行业趋势"],
                examples=[{"title": "产品提案分析示例", "input": "我们推出了一款创新产品...", "output": {}}]
            ),
            
            # 合同分析模板
            ScenarioTemplate(
                template_id="contract_analysis_v1",
                category=TemplateCategory.CONTRACT_ANALYSIS,
                name="合同文档智能分析模板",
                description="专门用于合同文档的法律分析",
                version="1.0",
                created_time=datetime.now().isoformat(),
                updated_time=datetime.now().isoformat(),
                prompt_template="""
请作为法律顾问，对以下合同文档进行专业法律分析：

文档内容：
{text}

请从以下维度进行分析：
1. 权利义务条款分析
2. 风险条款识别
3. 违约责任评估
4. 合规性检查
5. 优化建议

请以JSON格式输出分析结果。
""",
                expected_output_format={
                    "rights_and_obligations": {"party_rights": [], "balance_assessment": ""},
                    "risk_analysis": {"legal_risks": [], "risk_allocation": ""},
                    "breach_liability": {"liability_clauses": [], "loopholes": []},
                    "compliance_check": {"legal_compliance": "", "compliance_risks": []},
                    "optimization_suggestions": {"clause_improvements": [], "legal_protection_strategies": []}
                },
                quality_standards={"completeness": 0.95, "accuracy": 0.9, "relevance": 0.9, "clarity": 0.85},
                business_rules=["法律分析必须基于现行法律法规", "风险评估要全面且具体"],
                examples=[{"title": "服务合同分析示例", "input": "甲方委托乙方提供技术服务...", "output": {}}]
            ),
            
            # 学术论文模板
            ScenarioTemplate(
                template_id="academic_paper_v1",
                category=TemplateCategory.ACADEMIC_PAPER,
                name="学术论文协作审阅模板",
                description="专门用于学术论文的审阅分析",
                version="1.0",
                created_time=datetime.now().isoformat(),
                updated_time=datetime.now().isoformat(),
                prompt_template="""
请作为学术专家，对以下学术论文进行专业审阅：

文档内容：
{text}

请从以下维度进行分析：
1. 研究方法论评估
2. 数据分析准确性验证
3. 创新贡献评价
4. 学术规范性检查
5. 改进建议

请以JSON格式输出分析结果。
""",
                expected_output_format={
                    "methodology_assessment": {"research_method": "", "design_analysis": ""},
                    "data_analysis": {"analysis_method": "", "interpretation_accuracy": ""},
                    "innovation_evaluation": {"innovation_points": [], "academic_contribution": ""},
                    "academic_standards": {"citation_format": "", "writing_standards": ""},
                    "improvement_suggestions": {"methodology_improvements": [], "writing_enhancements": []}
                },
                quality_standards={"completeness": 0.9, "accuracy": 0.9, "relevance": 0.9, "clarity": 0.85},
                business_rules=["学术评估必须基于科学标准", "数据分析要严谨准确"],
                examples=[{"title": "机器学习论文审阅示例", "input": "本文提出了一种新的深度学习算法...", "output": {}}]
            ),
            
            # 政府公文模板
            ScenarioTemplate(
                template_id="government_document_v1",
                category=TemplateCategory.GOVERNMENT_DOCUMENT,
                name="政府公文格式规范检查模板",
                description="专门用于政府公文的规范检查",
                version="1.0",
                created_time=datetime.now().isoformat(),
                updated_time=datetime.now().isoformat(),
                prompt_template="""
请作为公文专家，对以下政府公文进行专业分析：

文档内容：
{text}

请从以下维度进行分析：
1. 政策合规性检查
2. 格式规范性验证
3. 语言准确性评估
4. 逻辑严密性分析
5. 可操作性评估

请以JSON格式输出分析结果。
""",
                expected_output_format={
                    "policy_compliance": {"policy_basis": "", "compliance_assessment": ""},
                    "format_standards": {"format_compliance": "", "document_elements": []},
                    "language_accuracy": {"word_accuracy": "", "expression_clarity": ""},
                    "logical_rigor": {"structure_logic": "", "conclusion_reasonableness": ""},
                    "operability_assessment": {"implementation_measures": "", "supervision_mechanism": ""}
                },
                quality_standards={"completeness": 0.95, "accuracy": 0.9, "relevance": 0.9, "clarity": 0.85},
                business_rules=["政策合规性检查要严格", "格式规范性要求要准确"],
                examples=[{"title": "政策文件分析示例", "input": "为进一步规范市场秩序...", "output": {}}]
            )
        ]
        
        for template in default_templates:
            self.templates[template.template_id] = asdict(template)
        
        self._save_templates()
    
    def _build_full_prompt(self, template: ScenarioTemplate, text: str, user_role: str) -> str:
        """构建完整的提示词"""
        base_prompt = template.prompt_template.format(text=text)
        
        role_requirements = self._get_role_requirements(user_role, template.category)
        quality_requirements = self._get_quality_requirements(template.quality_standards)
        business_rules = "\n".join([f"- {rule}" for rule in template.business_rules])
        
        full_prompt = f"""
{base_prompt}

【角色要求】
{role_requirements}

【质量要求】
{quality_requirements}

【业务规则】
{business_rules}

【输出格式】
请严格按照以下JSON格式输出分析结果：
{json.dumps(template.expected_output_format, ensure_ascii=False, indent=2)}

请确保分析结果的质量和专业性。
"""
        
        return full_prompt
    
    def _get_role_requirements(self, user_role: str, category: TemplateCategory) -> str:
        """获取角色特定要求"""
        role_requirements = {
            TemplateCategory.TECHNICAL_REPORT: "请以技术专家的视角进行分析，重点关注技术指标、创新性和可行性",
            TemplateCategory.BUSINESS_PROPOSAL: "请以商业顾问的视角进行分析，重点关注商业价值、市场机会和竞争优势",
            TemplateCategory.CONTRACT_ANALYSIS: "请以法律顾问的视角进行分析，重点关注法律风险、合规性和权利义务",
            TemplateCategory.ACADEMIC_PAPER: "请以学术专家的视角进行分析，重点关注研究方法、数据分析和学术规范",
            TemplateCategory.GOVERNMENT_DOCUMENT: "请以公文专家的视角进行分析，重点关注政策合规、格式规范和语言准确"
        }
        
        return role_requirements.get(category, "请以专业分析师的视角进行全面分析")
    
    def _get_quality_requirements(self, quality_standards: Dict[str, Any]) -> str:
        """获取质量要求"""
        requirements = []
        
        if quality_standards.get("completeness", 0) >= 0.9:
            requirements.append("分析要全面完整，覆盖所有重要维度")
        
        if quality_standards.get("accuracy", 0) >= 0.9:
            requirements.append("分析要准确可靠，基于客观事实和数据")
        
        if quality_standards.get("relevance", 0) >= 0.9:
            requirements.append("分析要高度相关，紧扣主题和重点")
        
        if quality_standards.get("clarity", 0) >= 0.8:
            requirements.append("表达要清晰明确，逻辑结构合理")
        
        return "\n".join([f"- {req}" for req in requirements]) 