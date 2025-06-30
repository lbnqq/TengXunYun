#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Virtual Reviewer - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from .intelligent_role_selector import IntelligentRoleSelector
from .smart_prompt_generator import SmartPromptGenerator
from .base_tool import BaseTool

class EnhancedVirtualReviewer(BaseTool):
    """
    增强的虚拟评审器 - 最大化利用AI智能进行多角色文档评审
    """
    
    def __init__(self, llm_client=None, knowledge_base: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.llm_client = llm_client
        self.knowledge_base = knowledge_base or {}
        
        # 初始化智能组件
        self.role_selector = IntelligentRoleSelector()
        self.prompt_generator = SmartPromptGenerator()
        
        # 评审配置
        self.review_config = {
            "max_roles": 5,  # 最大角色数量
            "min_role_score": 0.3,  # 最小角色匹配分数
            "consensus_threshold": 0.7,  # 共识阈值
            "priority_weights": {
                "critical": 1.0,
                "high": 0.7,
                "medium": 0.4,
                "low": 0.2
            }
        }
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def execute(self, operation: str = "smart_review", **kwargs) -> Dict[str, Any]:
        """
        执行增强的虚拟评审操作
        
        Args:
            operation: 操作类型 (smart_review, analyze_consensus, generate_repair_guide)
            **kwargs: 操作特定参数
        """
        try:
            if operation == "smart_review":
                return self.smart_review_document(**kwargs)
            elif operation == "analyze_consensus":
                return self.analyze_reviewer_consensus(**kwargs)
            elif operation == "generate_repair_guide":
                return self.generate_repair_guidance(**kwargs)
            else:
                return {"error": f"Unknown operation: {operation}"}
        except Exception as e:
            self.logger.error(f"Error in enhanced virtual review: {e}")
            return {"error": f"Error in enhanced virtual review: {e}"}
    
    def smart_review_document(self, document_content: str, 
                            document_type: str = None,
                            review_focus: str = None,
                            custom_roles: List[str] = None) -> Dict[str, Any]:
        """
        智能文档评审 - 自动选择角色并生成专业评审意见
        
        Args:
            document_content: 文档内容
            document_type: 文档类型（可选）
            review_focus: 评审重点（可选）
            custom_roles: 自定义角色列表（可选）
            
        Returns:
            Dict: 智能评审结果
        """
        try:
            self.logger.info("🚀 开始智能文档评审")
            
            # 1. 文档分析
            document_analysis = self._analyze_document_characteristics(document_content)
            self.logger.info(f"📊 文档分析完成: {document_analysis.get('document_type', 'unknown')}")
            
            # 2. 智能角色选择
            if custom_roles:
                selected_roles = custom_roles
                self.logger.info(f"🎯 使用自定义角色: {selected_roles}")
            else:
                selected_roles = self.role_selector.select_roles_for_document(
                    document_content, document_type
                )
                self.logger.info(f"🎯 智能选择角色: {selected_roles}")
            
            # 3. 获取角色详细信息
            role_profiles = self.role_selector.get_role_details(selected_roles)
            
            # 4. 生成专业提示词
            prompts = self.prompt_generator.generate_multi_role_prompt(
                role_profiles, document_content, document_analysis, review_focus
            )
            
            # 5. 执行多角色评审
            reviewer_results = []
            for role_id, role_profile in zip(selected_roles, role_profiles):
                self.logger.info(f"👤 开始 {role_profile.get('role_name', role_id)} 评审")
                
                review_result = self._execute_single_role_review(
                    role_id, role_profile, prompts.get(role_id, ""), 
                    document_content, document_analysis
                )
                
                if review_result.get("success"):
                    reviewer_results.append(review_result)
                    self.logger.info(f"✅ {role_profile.get('role_name', role_id)} 评审完成")
                else:
                    self.logger.warning(f"⚠️ {role_profile.get('role_name', role_id)} 评审失败: {review_result.get('error')}")
            
            # 6. 智能意见综合
            consensus_analysis = self.analyze_reviewer_consensus(reviewer_results)
            
            # 7. 生成综合报告
            comprehensive_report = self._generate_comprehensive_report(
                reviewer_results, consensus_analysis, document_analysis
            )
            
            # 8. 生成修复指导
            repair_guidance = self.generate_repair_guidance(
                comprehensive_report, document_content
            )
            
            result = {
                "success": True,
                "session_id": f"smart_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "document_analysis": document_analysis,
                "selected_roles": selected_roles,
                "role_profiles": role_profiles,
                "reviewer_results": reviewer_results,
                "consensus_analysis": consensus_analysis,
                "comprehensive_report": comprehensive_report,
                "repair_guidance": repair_guidance,
                "review_metadata": {
                    "total_reviewers": len(reviewer_results),
                    "review_duration": "实时计算",
                    "consensus_level": consensus_analysis.get("consensus_level", "unknown"),
                    "critical_issues_count": comprehensive_report.get("critical_issues_count", 0),
                    "overall_quality_score": comprehensive_report.get("overall_quality_score", 0)
                }
            }
            
            self.logger.info("🎉 智能文档评审完成")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ 智能文档评审失败: {e}")
            return {"error": f"智能文档评审失败: {str(e)}"}
    
    def _execute_single_role_review(self, role_id: str, role_profile: Dict[str, Any],
                                  prompt: str, document_content: str,
                                  document_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个角色的评审
        
        Args:
            role_id: 角色ID
            role_profile: 角色配置
            prompt: 评审提示词
            document_content: 文档内容
            document_analysis: 文档分析结果
            
        Returns:
            Dict: 单个角色评审结果
        """
        try:
            # 如果有LLM客户端，使用AI评审
            if self.llm_client:
                review_text = self.llm_client.generate(prompt)
                review_analysis = self._parse_review_response(review_text, role_id)
            else:
                # 回退到规则评审
                review_analysis = self._rule_based_review(document_content, role_profile, document_analysis)
            
            return {
                "success": True,
                "role_id": role_id,
                "role_name": role_profile.get("role_name", role_id),
                "review_prompt": prompt,
                "review_response": review_analysis.get("review_text", ""),
                "review_analysis": review_analysis,
                "review_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ 角色 {role_id} 评审失败: {e}")
            return {
                "success": False,
                "role_id": role_id,
                "error": str(e)
            }
    
    def _parse_review_response(self, review_text: str, role_id: str) -> Dict[str, Any]:
        """
        解析AI评审响应
        
        Args:
            review_text: AI评审文本
            role_id: 角色ID
            
        Returns:
            Dict: 解析后的评审分析
        """
        try:
            # 提取问题和建议
            issues = self._extract_issues_from_text(review_text)
            recommendations = self._extract_recommendations_from_text(review_text)
            risks = self._extract_risks_from_text(review_text)
            
            # 计算质量分数
            quality_score = self._calculate_quality_score(issues, recommendations, risks)
            
            return {
                "review_text": review_text,
                "issues": issues,
                "recommendations": recommendations,
                "risks": risks,
                "quality_score": quality_score,
                "overall_assessment": self._extract_overall_assessment(review_text)
            }
            
        except Exception as e:
            self.logger.error(f"❌ 解析评审响应失败: {e}")
            return {
                "review_text": review_text,
                "issues": [],
                "recommendations": [],
                "risks": [],
                "quality_score": 0.0,
                "overall_assessment": "评审解析失败"
            }
    
    def _rule_based_review(self, document_content: str, role_profile: Dict[str, Any],
                          document_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于规则的评审（LLM不可用时的回退方案）
        
        Args:
            document_content: 文档内容
            role_profile: 角色配置
            document_analysis: 文档分析结果
            
        Returns:
            Dict: 规则评审结果
        """
        issues = []
        recommendations = []
        risks = []
        
        # 基于角色类型进行规则评审
        role_id = role_profile.get("role_id", "")
        
        if "technical" in role_id:
            # 技术评审规则
            if len(document_content) < 100:
                issues.append({
                    "severity": "high",
                    "category": "内容完整性",
                    "description": "文档内容过于简短，缺乏必要的技术细节",
                    "suggestion": "增加技术实现细节和架构说明"
                })
            
            if "API" in document_content and "错误处理" not in document_content:
                issues.append({
                    "severity": "medium",
                    "category": "技术完整性",
                    "description": "API设计缺少错误处理机制",
                    "suggestion": "添加完整的错误处理和异常管理"
                })
        
        elif "business" in role_id:
            # 商业评审规则
            if "成本" not in document_content and "收益" not in document_content:
                issues.append({
                    "severity": "high",
                    "category": "商业分析",
                    "description": "缺少成本效益分析",
                    "suggestion": "添加详细的成本分析和收益预测"
                })
        
        elif "legal" in role_id:
            # 法律评审规则
            if "责任" not in document_content and "风险" not in document_content:
                issues.append({
                    "severity": "critical",
                    "category": "法律合规",
                    "description": "缺少法律责任和风险条款",
                    "suggestion": "明确各方责任和风险承担"
                })
        
        # 通用规则
        if len(document_content.split()) < 50:
            issues.append({
                "severity": "medium",
                "category": "内容质量",
                "description": "文档内容不足，需要补充详细信息",
                "suggestion": "增加更多具体内容和示例"
            })
        
        return {
            "review_text": f"基于规则的{role_profile.get('role_name', '专业')}评审完成",
            "issues": issues,
            "recommendations": recommendations,
            "risks": risks,
            "quality_score": max(0, 100 - len(issues) * 10),
            "overall_assessment": f"文档需要{len(issues)}个方面的改进"
        }
    
    def analyze_reviewer_consensus(self, reviewer_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析评审者共识
        
        Args:
            reviewer_results: 评审结果列表
            
        Returns:
            Dict: 共识分析结果
        """
        try:
            if not reviewer_results:
                return {"error": "没有评审结果可供分析"}
            
            # 收集所有问题
            all_issues = []
            reviewer_scores = {}
            
            for result in reviewer_results:
                role_name = result.get("role_name", "Unknown")
                analysis = result.get("review_analysis", {})
                
                # 记录质量分数
                reviewer_scores[role_name] = analysis.get("quality_score", 0)
                
                # 收集问题
                issues = analysis.get("issues", [])
                for issue in issues:
                    issue["reviewer"] = role_name
                    all_issues.append(issue)
            
            # 分析共识
            consensus_areas = self._find_consensus_areas(all_issues)
            conflict_areas = self._find_conflict_areas(reviewer_results)
            
            # 计算共识分数
            consensus_score = self._calculate_consensus_score(reviewer_scores, consensus_areas)
            
            return {
                "total_reviewers": len(reviewer_results),
                "reviewer_scores": reviewer_scores,
                "consensus_areas": consensus_areas,
                "conflict_areas": conflict_areas,
                "consensus_score": consensus_score,
                "consensus_level": self._get_consensus_level(consensus_score),
                "agreement_analysis": self._analyze_agreement_patterns(all_issues)
            }
            
        except Exception as e:
            self.logger.error(f"❌ 共识分析失败: {e}")
            return {"error": f"共识分析失败: {str(e)}"}
    
    def generate_repair_guidance(self, comprehensive_report: Dict[str, Any],
                               document_content: str) -> Dict[str, Any]:
        """
        生成修复指导
        
        Args:
            comprehensive_report: 综合评审报告
            document_content: 原文档内容
            
        Returns:
            Dict: 修复指导
        """
        try:
            # 提取优先级问题
            critical_issues = comprehensive_report.get("critical_issues", [])
            high_issues = comprehensive_report.get("high_issues", [])
            
            # 生成修复建议
            repair_suggestions = []
            for issue in critical_issues + high_issues:
                repair_suggestions.append({
                    "issue": issue.get("description", ""),
                    "priority": issue.get("severity", "medium"),
                    "suggestion": issue.get("suggestion", ""),
                    "estimated_effort": self._estimate_repair_effort(issue.get("severity", "medium"))
                })
            
            # 生成修改后的文档大纲
            modified_outline = self._generate_modified_outline(document_content, repair_suggestions)
            
            return {
                "repair_suggestions": repair_suggestions,
                "modified_outline": modified_outline,
                "priority_ranking": self._rank_repair_priorities(repair_suggestions),
                "estimated_total_effort": self._calculate_total_effort(repair_suggestions),
                "repair_timeline": self._generate_repair_timeline(repair_suggestions)
            }
            
        except Exception as e:
            self.logger.error(f"❌ 生成修复指导失败: {e}")
            return {"error": f"生成修复指导失败: {str(e)}"}
    
    # 辅助方法
    def _analyze_document_characteristics(self, content: str) -> Dict[str, Any]:
        """分析文档特征"""
        words = content.split()
        sentences = content.split('.')
        
        return {
            "document_type": self._classify_document_type(content),
            "complexity_level": self._assess_complexity(content),
            "target_audience": self._identify_target_audience(content),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "formality_level": self._assess_formality(content)
        }
    
    def _classify_document_type(self, content: str) -> str:
        """分类文档类型"""
        content_lower = content.lower()
        
        if any(term in content_lower for term in ["技术", "系统", "架构", "API", "数据库"]):
            return "technical_report"
        elif any(term in content_lower for term in ["市场", "商业", "客户", "收益", "战略"]):
            return "business_proposal"
        elif any(term in content_lower for term in ["合同", "条款", "责任", "法律", "合规"]):
            return "legal_document"
        elif any(term in content_lower for term in ["政府", "政策", "法规", "通知", "决定"]):
            return "government_document"
        elif any(term in content_lower for term in ["研究", "实验", "方法", "结论", "引用"]):
            return "academic_paper"
        else:
            return "general_document"
    
    def _assess_complexity(self, content: str) -> str:
        """评估复杂度"""
        word_count = len(content.split())
        if word_count > 1000:
            return "high"
        elif word_count > 500:
            return "medium"
        else:
            return "low"
    
    def _identify_target_audience(self, content: str) -> str:
        """识别目标受众"""
        content_lower = content.lower()
        
        if any(term in content_lower for term in ["技术团队", "开发", "工程师"]):
            return "technical_team"
        elif any(term in content_lower for term in ["管理层", "领导", "决策"]):
            return "management"
        elif any(term in content_lower for term in ["客户", "用户", "消费者"]):
            return "customers"
        else:
            return "general_audience"
    
    def _assess_formality(self, content: str) -> str:
        """评估正式程度"""
        informal_words = ["我觉得", "挺好的", "应该可以"]
        informal_count = sum(1 for word in informal_words if word in content)
        
        if informal_count > 2:
            return "informal"
        elif informal_count > 0:
            return "semi_formal"
        else:
            return "formal"
    
    def _extract_issues_from_text(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取问题"""
        issues = []
        # 简化的规则提取
        if "问题" in text or "issue" in text.lower():
            issues.append({
                "severity": "medium",
                "category": "内容质量",
                "description": "发现内容问题",
                "suggestion": "需要进一步改进"
            })
        return issues
    
    def _extract_recommendations_from_text(self, text: str) -> List[str]:
        """从文本中提取建议"""
        recommendations = []
        # 简化的规则提取
        if "建议" in text or "recommend" in text.lower():
            recommendations.append("根据评审意见进行改进")
        return recommendations
    
    def _extract_risks_from_text(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取风险"""
        risks = []
        # 简化的规则提取
        if "风险" in text or "risk" in text.lower():
            risks.append({
                "risk_type": "general",
                "severity": "medium",
                "description": "存在潜在风险",
                "mitigation": "需要进一步评估"
            })
        return risks
    
    def _calculate_quality_score(self, issues: List[Dict], recommendations: List[str], risks: List[Dict]) -> float:
        """计算质量分数"""
        base_score = 100.0
        
        # 根据问题数量扣分
        for issue in issues:
            severity = issue.get("severity", "medium")
            if severity == "critical":
                base_score -= 20
            elif severity == "high":
                base_score -= 10
            elif severity == "medium":
                base_score -= 5
            else:
                base_score -= 2
        
        return max(0.0, base_score)
    
    def _extract_overall_assessment(self, text: str) -> str:
        """提取总体评价"""
        if "优秀" in text or "excellent" in text.lower():
            return "优秀"
        elif "良好" in text or "good" in text.lower():
            return "良好"
        elif "一般" in text or "fair" in text.lower():
            return "一般"
        else:
            return "需要改进"
    
    def _find_consensus_areas(self, all_issues: List[Dict]) -> Dict[str, List[Dict]]:
        """找到共识领域"""
        consensus_areas = {}
        
        # 按问题类别分组
        for issue in all_issues:
            category = issue.get("category", "general")
            if category not in consensus_areas:
                consensus_areas[category] = []
            consensus_areas[category].append(issue)
        
        # 过滤出多个评审者都提到的问题
        return {k: v for k, v in consensus_areas.items() if len(v) > 1}
    
    def _find_conflict_areas(self, reviewer_results: List[Dict]) -> List[Dict]:
        """找到冲突领域"""
        # 简化的冲突检测
        return []
    
    def _calculate_consensus_score(self, reviewer_scores: Dict[str, float], consensus_areas: Dict) -> float:
        """计算共识分数"""
        if not reviewer_scores:
            return 0.0
        
        # 基于分数差异和共识领域计算
        scores = list(reviewer_scores.values())
        score_variance = max(scores) - min(scores) if len(scores) > 1 else 0
        consensus_bonus = len(consensus_areas) * 10
        
        return min(100.0, 100 - score_variance + consensus_bonus)
    
    def _get_consensus_level(self, consensus_score: float) -> str:
        """获取共识等级"""
        if consensus_score >= 80:
            return "high"
        elif consensus_score >= 60:
            return "medium"
        else:
            return "low"
    
    def _analyze_agreement_patterns(self, all_issues: List[Dict]) -> Dict[str, Any]:
        """分析同意模式"""
        return {
            "total_issues": len(all_issues),
            "severity_distribution": self._get_severity_distribution(all_issues),
            "category_distribution": self._get_category_distribution(all_issues)
        }
    
    def _get_severity_distribution(self, issues: List[Dict]) -> Dict[str, int]:
        """获取严重程度分布"""
        distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity = issue.get("severity", "medium")
            distribution[severity] = distribution.get(severity, 0) + 1
        return distribution
    
    def _get_category_distribution(self, issues: List[Dict]) -> Dict[str, int]:
        """获取类别分布"""
        distribution = {}
        for issue in issues:
            category = issue.get("category", "general")
            distribution[category] = distribution.get(category, 0) + 1
        return distribution
    
    def _generate_comprehensive_report(self, reviewer_results: List[Dict], 
                                     consensus_analysis: Dict, 
                                     document_analysis: Dict) -> Dict[str, Any]:
        """生成综合报告"""
        # 收集所有问题
        all_issues = []
        for result in reviewer_results:
            analysis = result.get("review_analysis", {})
            issues = analysis.get("issues", [])
            all_issues.extend(issues)
        
        # 按严重程度分类
        critical_issues = [i for i in all_issues if i.get("severity") == "critical"]
        high_issues = [i for i in all_issues if i.get("severity") == "high"]
        medium_issues = [i for i in all_issues if i.get("severity") == "medium"]
        low_issues = [i for i in all_issues if i.get("severity") == "low"]
        
        # 计算总体质量分数
        total_score = sum(result.get("review_analysis", {}).get("quality_score", 0) for result in reviewer_results)
        avg_score = total_score / len(reviewer_results) if reviewer_results else 0
        
        return {
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "low_issues": low_issues,
            "critical_issues_count": len(critical_issues),
            "high_issues_count": len(high_issues),
            "medium_issues_count": len(medium_issues),
            "low_issues_count": len(low_issues),
            "overall_quality_score": avg_score,
            "consensus_level": consensus_analysis.get("consensus_level", "unknown"),
            "document_analysis": document_analysis
        }
    
    def _estimate_repair_effort(self, severity: str) -> str:
        """估算修复工作量"""
        effort_map = {
            "critical": "高工作量",
            "high": "中等工作量", 
            "medium": "低工作量",
            "low": "轻微工作量"
        }
        return effort_map.get(severity, "未知")
    
    def _generate_modified_outline(self, content: str, repair_suggestions: List[Dict]) -> List[str]:
        """生成修改后的大纲"""
        outline = ["文档修改建议大纲:"]
        
        for i, suggestion in enumerate(repair_suggestions, 1):
            outline.append(f"{i}. {suggestion['issue']} - {suggestion['suggestion']}")
        
        return outline
    
    def _rank_repair_priorities(self, repair_suggestions: List[Dict]) -> List[Dict]:
        """排序修复优先级"""
        return sorted(repair_suggestions, 
                     key=lambda x: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x.get("priority", "medium"), 0),
                     reverse=True)
    
    def _calculate_total_effort(self, repair_suggestions: List[Dict]) -> str:
        """计算总工作量"""
        critical_count = len([s for s in repair_suggestions if s.get("priority") == "critical"])
        high_count = len([s for s in repair_suggestions if s.get("priority") == "high"])
        
        if critical_count > 0:
            return "高工作量"
        elif high_count > 2:
            return "中等工作量"
        else:
            return "低工作量"
    
    def _generate_repair_timeline(self, repair_suggestions: List[Dict]) -> List[str]:
        """生成修复时间线"""
        timeline = []
        
        critical_issues = [s for s in repair_suggestions if s.get("priority") == "critical"]
        high_issues = [s for s in repair_suggestions if s.get("priority") == "high"]
        
        if critical_issues:
            timeline.append("立即处理: 严重问题需要优先解决")
        if high_issues:
            timeline.append("本周内: 重要问题需要及时处理")
        if len(repair_suggestions) > len(critical_issues) + len(high_issues):
            timeline.append("下周内: 其他问题可以逐步改进")
        
        return timeline 