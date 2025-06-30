#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intelligent Role Selector - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import re
import yaml
import os
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter
import json

class IntelligentRoleSelector:
    """
    智能角色选择器 - 根据文档内容智能选择最合适的专家角色
    """
    
    def __init__(self, role_profiles_path: str = "src/core/knowledge_base/role_profiles.yaml"):
        self.role_profiles_path = role_profiles_path
        self.role_profiles = self._load_role_profiles()
        self.domain_keywords = self._init_domain_keywords()
        self.audience_indicators = self._init_audience_indicators()
        self.scenario_indicators = self._init_scenario_indicators()
    
    def _load_role_profiles(self) -> Dict[str, Any]:
        """加载角色配置文件"""
        try:
            with open(self.role_profiles_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                # 转换为字典格式，便于查找
                roles_dict = {}
                for role in data.get('roles', []):
                    roles_dict[role['role_id']] = role
                return roles_dict
        except Exception as e:
            print(f"Warning: Failed to load role profiles: {e}")
            return {}
    
    def _init_domain_keywords(self) -> Dict[str, List[str]]:
        """初始化专业领域关键词"""
        return {
            "technical": [
                "技术", "系统", "架构", "开发", "代码", "算法", "性能", "API", "数据库",
                "technical", "system", "architecture", "development", "code", "algorithm",
                "performance", "api", "database", "implementation", "optimization"
            ],
            "business": [
                "业务", "市场", "商业", "战略", "营销", "销售", "客户", "产品", "服务",
                "business", "market", "strategy", "marketing", "sales", "customer",
                "product", "service", "revenue", "profit", "growth"
            ],
            "financial": [
                "财务", "金融", "预算", "成本", "投资", "收益", "风险", "资金", "财务分析",
                "financial", "budget", "cost", "investment", "revenue", "risk", "funding",
                "financial analysis", "ROI", "profitability"
            ],
            "legal": [
                "法律", "法规", "合规", "合同", "条款", "责任", "风险", "知识产权", "诉讼",
                "legal", "regulation", "compliance", "contract", "liability", "risk",
                "intellectual property", "litigation", "legal review"
            ],
            "government": [
                "政府", "公文", "政策", "法规", "行政", "机关", "部门", "通知", "决定",
                "government", "policy", "regulation", "administrative", "official",
                "document", "notice", "decision", "implementation"
            ],
            "academic": [
                "学术", "研究", "论文", "方法", "实验", "分析", "结论", "引用", "期刊",
                "academic", "research", "paper", "methodology", "experiment", "analysis",
                "conclusion", "citation", "journal", "peer review"
            ],
            "quality": [
                "质量", "标准", "测试", "验证", "检查", "评估", "改进", "流程", "规范",
                "quality", "standard", "testing", "verification", "inspection",
                "evaluation", "improvement", "process", "compliance"
            ],
            "project": [
                "项目", "计划", "时间", "资源", "团队", "里程碑", "交付", "管理", "协调",
                "project", "planning", "timeline", "resources", "team", "milestone",
                "delivery", "management", "coordination"
            ]
        }
    
    def _init_audience_indicators(self) -> Dict[str, List[str]]:
        """初始化目标用户指示器"""
        return {
            "technical_team": [
                "开发团队", "技术团队", "工程师", "程序员", "架构师", "运维",
                "development team", "technical team", "engineer", "programmer",
                "architect", "operations"
            ],
            "management": [
                "管理层", "领导", "经理", "总监", "CEO", "CTO", "决策者",
                "management", "leadership", "manager", "director", "executive",
                "decision maker"
            ],
            "stakeholders": [
                "利益相关者", "股东", "投资者", "客户", "用户", "合作伙伴",
                "stakeholder", "shareholder", "investor", "customer", "user",
                "partner"
            ],
            "government_officials": [
                "政府官员", "公务员", "部门领导", "政策制定者", "监管机构",
                "government official", "civil servant", "department head",
                "policy maker", "regulator"
            ],
            "academic_community": [
                "学术界", "研究人员", "学者", "学生", "同行评议", "学术期刊",
                "academic community", "researcher", "scholar", "student",
                "peer review", "journal"
            ]
        }
    
    def _init_scenario_indicators(self) -> Dict[str, List[str]]:
        """初始化应用场景指示器"""
        return {
            "development": [
                "开发", "实现", "编程", "编码", "构建", "部署", "测试",
                "development", "implementation", "programming", "coding",
                "building", "deployment", "testing"
            ],
            "review": [
                "评审", "审查", "检查", "评估", "审核", "验证", "确认",
                "review", "inspection", "evaluation", "audit", "verification",
                "validation"
            ],
            "planning": [
                "规划", "计划", "设计", "架构", "策略", "路线图", "蓝图",
                "planning", "design", "architecture", "strategy", "roadmap",
                "blueprint"
            ],
            "analysis": [
                "分析", "研究", "调查", "评估", "比较", "统计", "报告",
                "analysis", "research", "investigation", "assessment",
                "comparison", "statistics", "report"
            ],
            "compliance": [
                "合规", "监管", "标准", "规范", "要求", "检查", "认证",
                "compliance", "regulation", "standard", "requirement",
                "inspection", "certification"
            ]
        }
    
    def select_roles_for_document(self, document_content: str, document_type: str = None) -> List[str]:
        """
        为文档智能选择专家角色
        
        Args:
            document_content: 文档内容
            document_type: 文档类型（可选）
            
        Returns:
            List[str]: 选中的角色ID列表
        """
        try:
            # 1. 文档内容分析
            content_analysis = self._analyze_document_content(document_content)
            
            # 2. 专业领域识别
            domain_scores = self._identify_domains(document_content)
            
            # 3. 目标用户分析
            audience_scores = self._analyze_target_audience(document_content)
            
            # 4. 应用场景判断
            scenario_scores = self._determine_application_scenario(document_content)
            
            # 5. 角色匹配和评分
            role_scores = self._calculate_role_scores(
                domain_scores, audience_scores, scenario_scores, content_analysis, document_type
            )
            
            # 6. 选择最佳角色组合
            selected_roles = self._select_optimal_role_combination(role_scores)
            
            print(f"🎯 智能角色选择结果:")
            print(f"   文档类型: {document_type or '自动识别'}")
            print(f"   识别领域: {list(domain_scores.keys())[:3]}")
            print(f"   目标用户: {list(audience_scores.keys())[:2]}")
            print(f"   应用场景: {list(scenario_scores.keys())[:2]}")
            print(f"   选中角色: {selected_roles}")
            
            return selected_roles
            
        except Exception as e:
            print(f"❌ 智能角色选择失败: {e}")
            # 回退到默认角色
            return ["technical_reviewer", "qa_specialist"]
    
    def _analyze_document_content(self, content: str) -> Dict[str, Any]:
        """分析文档内容特征"""
        content_lower = content.lower()
        words = content.split()
        
        return {
            "word_count": len(words),
            "sentence_count": len(content.split('.')),
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
            "has_technical_terms": any(term in content_lower for term in ["API", "数据库", "算法", "架构"]),
            "has_business_terms": any(term in content_lower for term in ["市场", "客户", "收益", "战略"]),
            "has_legal_terms": any(term in content_lower for term in ["合同", "条款", "责任", "合规"]),
            "has_government_terms": any(term in content_lower for term in ["政府", "政策", "法规", "通知"]),
            "complexity_level": self._assess_complexity(content),
            "formality_level": self._assess_formality(content)
        }
    
    def _identify_domains(self, content: str) -> Dict[str, float]:
        """识别文档涉及的专业领域"""
        content_lower = content.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            if matches > 0:
                # 计算匹配分数（考虑关键词密度）
                score = min(matches * 0.1, 1.0)  # 最高1.0分
                domain_scores[domain] = score
        
        return domain_scores
    
    def _analyze_target_audience(self, content: str) -> Dict[str, float]:
        """分析目标用户群体"""
        content_lower = content.lower()
        audience_scores = {}
        
        for audience, indicators in self.audience_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in content_lower)
            if matches > 0:
                score = min(matches * 0.15, 1.0)
                audience_scores[audience] = score
        
        return audience_scores
    
    def _determine_application_scenario(self, content: str) -> Dict[str, float]:
        """判断应用场景"""
        content_lower = content.lower()
        scenario_scores = {}
        
        for scenario, indicators in self.scenario_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in content_lower)
            if matches > 0:
                score = min(matches * 0.12, 1.0)
                scenario_scores[scenario] = score
        
        return scenario_scores
    
    def _calculate_role_scores(self, domain_scores: Dict[str, float], 
                             audience_scores: Dict[str, float],
                             scenario_scores: Dict[str, float],
                             content_analysis: Dict[str, Any],
                             document_type: str = None) -> Dict[str, float]:
        """计算每个角色的匹配分数"""
        role_scores = {}
        
        for role_id, role_profile in self.role_profiles.items():
            score = 0.0
            
            # 1. 基于专业领域匹配
            role_focus = role_profile.get("review_focus", [])
            for domain, domain_score in domain_scores.items():
                if any(domain_keyword in str(role_focus).lower() for domain_keyword in self.domain_keywords.get(domain, [])):
                    score += domain_score * 0.4
            
            # 2. 基于目标用户匹配
            for audience, audience_score in audience_scores.items():
                if audience in str(role_profile).lower():
                    score += audience_score * 0.3
            
            # 3. 基于应用场景匹配
            for scenario, scenario_score in scenario_scores.items():
                if scenario in str(role_profile).lower():
                    score += scenario_score * 0.2
            
            # 4. 基于文档类型匹配
            if document_type:
                if document_type in str(role_profile).lower():
                    score += 0.1
            
            # 5. 基于内容复杂度匹配
            if content_analysis["complexity_level"] == "high" and "expert" in role_id:
                score += 0.1
            elif content_analysis["complexity_level"] == "low" and "end_user" in role_id:
                score += 0.1
            
            role_scores[role_id] = min(score, 1.0)
        
        return role_scores
    
    def _select_optimal_role_combination(self, role_scores: Dict[str, float]) -> List[str]:
        """选择最优的角色组合"""
        # 按分数排序
        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 选择分数最高的3-5个角色
        selected_roles = []
        for role_id, score in sorted_roles:
            if score > 0.3 and len(selected_roles) < 5:  # 分数阈值和数量限制
                selected_roles.append(role_id)
        
        # 确保至少有一个角色
        if not selected_roles:
            selected_roles = ["technical_reviewer"]
        
        return selected_roles
    
    def _assess_complexity(self, content: str) -> str:
        """评估文档复杂度"""
        word_count = len(content.split())
        avg_sentence_length = word_count / max(len(content.split('.')), 1)
        
        if word_count > 1000 or avg_sentence_length > 25:
            return "high"
        elif word_count > 500 or avg_sentence_length > 15:
            return "medium"
        else:
            return "low"
    
    def _assess_formality(self, content: str) -> str:
        """评估文档正式程度"""
        informal_words = ["我觉得", "挺好的", "应该可以", "用了", "做了"]
        informal_count = sum(1 for word in informal_words if word in content)
        
        if informal_count > 3:
            return "informal"
        elif informal_count > 1:
            return "semi_formal"
        else:
            return "formal"
    
    def get_role_details(self, role_ids: List[str]) -> List[Dict[str, Any]]:
        """获取角色详细信息"""
        role_details = []
        for role_id in role_ids:
            if role_id in self.role_profiles:
                role_details.append(self.role_profiles[role_id])
        return role_details 