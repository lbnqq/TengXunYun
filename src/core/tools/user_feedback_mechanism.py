#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Feedback Mechanism - 核心模块

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


class FeedbackType(Enum):
    """反馈类型"""
    ACCURACY = "accuracy"           # 准确性反馈
    RELEVANCE = "relevance"         # 相关性反馈
    COMPLETENESS = "completeness"   # 完整性反馈
    CLARITY = "clarity"             # 清晰度反馈
    USEFULNESS = "usefulness"       # 实用性反馈
    GENERAL = "general"             # 一般反馈


class FeedbackLevel(Enum):
    """反馈等级"""
    VERY_POOR = 1      # 很差
    POOR = 2           # 差
    AVERAGE = 3        # 一般
    GOOD = 4           # 好
    EXCELLENT = 5      # 优秀


@dataclass
class UserFeedback:
    """用户反馈数据结构"""
    feedback_id: str
    analysis_id: str
    business_scenario: str
    feedback_type: FeedbackType
    feedback_level: FeedbackLevel
    feedback_text: str
    user_role: str
    timestamp: str
    metadata: Dict[str, Any]


class UserFeedbackMechanism:
    """用户反馈机制"""
    
    def __init__(self, storage_path: str = "feedback_storage"):
        """
        初始化用户反馈机制
        
        Args:
            storage_path: 反馈数据存储路径
        """
        self.storage_path = storage_path
        self.feedback_file = os.path.join(storage_path, "user_feedback.json")
        self.analytics_file = os.path.join(storage_path, "feedback_analytics.json")
        
        # 确保存储目录存在
        os.makedirs(storage_path, exist_ok=True)
        
        # 初始化反馈数据
        self.feedback_data = self._load_feedback_data()
        self.analytics_data = self._load_analytics_data()
        
        # 反馈统计
        self.feedback_stats = {
            "total_feedback": 0,
            "feedback_by_type": {},
            "feedback_by_scenario": {},
            "average_rating": 0.0,
            "improvement_suggestions": []
        }
    
    def collect_feedback(self, analysis_result: Dict[str, Any], 
                        feedback_type: FeedbackType,
                        feedback_level: FeedbackLevel,
                        feedback_text: str,
                        user_role: str = "用户") -> Dict[str, Any]:
        """
        收集用户反馈
        
        Args:
            analysis_result: AI分析结果
            feedback_type: 反馈类型
            feedback_level: 反馈等级
            feedback_text: 反馈文本
            user_role: 用户角色
            
        Returns:
            反馈收集结果
        """
        try:
            # 生成反馈ID
            feedback_id = self._generate_feedback_id(analysis_result, feedback_type)
            
            # 创建反馈对象
            feedback = UserFeedback(
                feedback_id=feedback_id,
                analysis_id=analysis_result.get("analysis_id", "unknown"),
                business_scenario=analysis_result.get("business_scenario", "unknown"),
                feedback_type=feedback_type,
                feedback_level=feedback_level,
                feedback_text=feedback_text,
                user_role=user_role,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "original_text_length": len(analysis_result.get("original_text_preview", "")),
                    "quality_metrics": analysis_result.get("quality_metrics", {}),
                    "analysis_time": analysis_result.get("analysis_time", "")
                }
            )
            
            # 保存反馈
            self._save_feedback(feedback)
            
            # 更新统计
            self._update_feedback_stats(feedback)
            
            # 生成改进建议
            improvement_suggestions = self._generate_improvement_suggestions(feedback)
            
            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": "反馈收集成功",
                "improvement_suggestions": improvement_suggestions,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "反馈收集失败"
            }
    
    def get_feedback_analytics(self, business_scenario: Optional[str] = None,
                              time_range: Optional[str] = None) -> Dict[str, Any]:
        """
        获取反馈分析数据
        
        Args:
            business_scenario: 业务场景过滤
            time_range: 时间范围过滤
            
        Returns:
            反馈分析数据
        """
        try:
            # 过滤反馈数据
            filtered_feedback = self._filter_feedback(business_scenario, time_range)
            
            # 计算分析指标
            analytics = {
                "total_feedback": len(filtered_feedback),
                "feedback_distribution": self._calculate_feedback_distribution(filtered_feedback),
                "average_ratings": self._calculate_average_ratings(filtered_feedback),
                "trend_analysis": self._analyze_feedback_trends(filtered_feedback),
                "improvement_areas": self._identify_improvement_areas(filtered_feedback),
                "user_satisfaction": self._calculate_user_satisfaction(filtered_feedback),
                "scenario_performance": self._analyze_scenario_performance(filtered_feedback)
            }
            
            return {
                "success": True,
                "analytics": analytics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "反馈分析失败"
            }
    
    def apply_feedback_learning(self, feedback_data: List[UserFeedback]) -> Dict[str, Any]:
        """
        应用反馈学习，生成改进建议
        
        Args:
            feedback_data: 反馈数据列表
            
        Returns:
            学习结果和改进建议
        """
        try:
            # 分析反馈模式
            feedback_patterns = self._analyze_feedback_patterns(feedback_data)
            
            # 识别问题模式
            problem_patterns = self._identify_problem_patterns(feedback_data)
            
            # 生成改进策略
            improvement_strategies = self._generate_improvement_strategies(
                feedback_patterns, problem_patterns
            )
            
            # 生成提示词优化建议
            prompt_optimization_suggestions = self._generate_prompt_optimization_suggestions(
                feedback_data
            )
            
            return {
                "success": True,
                "feedback_patterns": feedback_patterns,
                "problem_patterns": problem_patterns,
                "improvement_strategies": improvement_strategies,
                "prompt_optimization_suggestions": prompt_optimization_suggestions,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "反馈学习失败"
            }
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """获取反馈摘要"""
        return {
            "total_feedback": self.feedback_stats["total_feedback"],
            "average_rating": self.feedback_stats["average_rating"],
            "top_improvement_areas": self.feedback_stats["improvement_suggestions"][:5],
            "feedback_by_type": self.feedback_stats["feedback_by_type"],
            "feedback_by_scenario": self.feedback_stats["feedback_by_scenario"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _load_feedback_data(self) -> List[Dict[str, Any]]:
        """加载反馈数据"""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载反馈数据失败: {e}")
        return []
    
    def _load_analytics_data(self) -> Dict[str, Any]:
        """加载分析数据"""
        if os.path.exists(self.analytics_file):
            try:
                with open(self.analytics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载分析数据失败: {e}")
        return {}
    
    def _save_feedback(self, feedback: UserFeedback):
        """保存反馈数据"""
        feedback_dict = asdict(feedback)
        feedback_dict["feedback_type"] = feedback.feedback_type.value
        feedback_dict["feedback_level"] = feedback.feedback_level.value
        
        self.feedback_data.append(feedback_dict)
        
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存反馈数据失败: {e}")
    
    def _generate_feedback_id(self, analysis_result: Dict[str, Any], 
                            feedback_type: FeedbackType) -> str:
        """生成反馈ID"""
        content = f"{analysis_result.get('analysis_id', '')}_{feedback_type.value}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _update_feedback_stats(self, feedback: UserFeedback):
        """更新反馈统计"""
        self.feedback_stats["total_feedback"] += 1
        
        # 按类型统计
        feedback_type = feedback.feedback_type.value
        if feedback_type not in self.feedback_stats["feedback_by_type"]:
            self.feedback_stats["feedback_by_type"][feedback_type] = 0
        self.feedback_stats["feedback_by_type"][feedback_type] += 1
        
        # 按场景统计
        scenario = feedback.business_scenario
        if scenario not in self.feedback_stats["feedback_by_scenario"]:
            self.feedback_stats["feedback_by_scenario"][scenario] = 0
        self.feedback_stats["feedback_by_scenario"][scenario] += 1
        
        # 更新平均评分
        current_total = self.feedback_stats["average_rating"] * (self.feedback_stats["total_feedback"] - 1)
        new_total = current_total + feedback.feedback_level.value
        self.feedback_stats["average_rating"] = new_total / self.feedback_stats["total_feedback"]
    
    def _generate_improvement_suggestions(self, feedback: UserFeedback) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if feedback.feedback_level.value <= 2:  # 差评
            if feedback.feedback_type == FeedbackType.ACCURACY:
                suggestions.append("建议增强模型的知识库和推理能力")
            elif feedback.feedback_type == FeedbackType.RELEVANCE:
                suggestions.append("建议优化提示词，提高分析的相关性")
            elif feedback.feedback_type == FeedbackType.COMPLETENESS:
                suggestions.append("建议扩展分析维度，提高完整性")
            elif feedback.feedback_type == FeedbackType.CLARITY:
                suggestions.append("建议改进输出格式，提高可读性")
        
        if feedback.feedback_text:
            # 从用户反馈文本中提取具体建议
            if "不够详细" in feedback.feedback_text:
                suggestions.append("增加分析深度和细节")
            if "不够准确" in feedback.feedback_text:
                suggestions.append("提高分析准确性")
            if "格式不好" in feedback.feedback_text:
                suggestions.append("优化输出格式")
        
        return suggestions[:3]  # 最多返回3个建议
    
    def _filter_feedback(self, business_scenario: Optional[str] = None,
                        time_range: Optional[str] = None) -> List[Dict[str, Any]]:
        """过滤反馈数据"""
        filtered = self.feedback_data
        
        if business_scenario:
            filtered = [f for f in filtered if f.get("business_scenario") == business_scenario]
        
        if time_range:
            # 简单的时间过滤逻辑
            cutoff_time = datetime.now().isoformat()
            if time_range == "day":
                cutoff_time = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
            elif time_range == "week":
                # 一周前
                from datetime import timedelta
                cutoff_time = (datetime.now() - timedelta(days=7)).isoformat()
            
            filtered = [f for f in filtered if f.get("timestamp", "") >= cutoff_time]
        
        return filtered
    
    def _calculate_feedback_distribution(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算反馈分布"""
        distribution = {
            "by_type": {},
            "by_level": {},
            "by_scenario": {}
        }
        
        for feedback in feedback_data:
            # 按类型分布
            feedback_type = feedback.get("feedback_type", "unknown")
            distribution["by_type"][feedback_type] = distribution["by_type"].get(feedback_type, 0) + 1
            
            # 按等级分布
            feedback_level = feedback.get("feedback_level", 3)
            distribution["by_level"][feedback_level] = distribution["by_level"].get(feedback_level, 0) + 1
            
            # 按场景分布
            scenario = feedback.get("business_scenario", "unknown")
            distribution["by_scenario"][scenario] = distribution["by_scenario"].get(scenario, 0) + 1
        
        return distribution
    
    def _calculate_average_ratings(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算平均评分"""
        if not feedback_data:
            return {}
        
        ratings = {
            "overall": 0.0,
            "by_type": {},
            "by_scenario": {}
        }
        
        total_rating = 0
        type_ratings = {}
        scenario_ratings = {}
        
        for feedback in feedback_data:
            level = feedback.get("feedback_level", 3)
            total_rating += level
            
            # 按类型统计
            feedback_type = feedback.get("feedback_type", "unknown")
            if feedback_type not in type_ratings:
                type_ratings[feedback_type] = {"total": 0, "count": 0}
            type_ratings[feedback_type]["total"] += level
            type_ratings[feedback_type]["count"] += 1
            
            # 按场景统计
            scenario = feedback.get("business_scenario", "unknown")
            if scenario not in scenario_ratings:
                scenario_ratings[scenario] = {"total": 0, "count": 0}
            scenario_ratings[scenario]["total"] += level
            scenario_ratings[scenario]["count"] += 1
        
        ratings["overall"] = total_rating / len(feedback_data)
        
        for feedback_type, data in type_ratings.items():
            ratings["by_type"][feedback_type] = data["total"] / data["count"]
        
        for scenario, data in scenario_ratings.items():
            ratings["by_scenario"][scenario] = data["total"] / data["count"]
        
        return ratings
    
    def _analyze_feedback_trends(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析反馈趋势"""
        if not feedback_data:
            return {}
        
        # 按时间排序
        sorted_feedback = sorted(feedback_data, key=lambda x: x.get("timestamp", ""))
        
        trends = {
            "rating_trend": [],
            "volume_trend": [],
            "type_trend": {}
        }
        
        # 简单的趋势分析
        for i, feedback in enumerate(sorted_feedback):
            trends["rating_trend"].append({
                "index": i,
                "rating": feedback.get("feedback_level", 3),
                "timestamp": feedback.get("timestamp", "")
            })
        
        return trends
    
    def _identify_improvement_areas(self, feedback_data: List[Dict[str, Any]]) -> List[str]:
        """识别改进领域"""
        improvement_areas = []
        
        # 分析低评分反馈
        low_ratings = [f for f in feedback_data if f.get("feedback_level", 3) <= 2]
        
        if low_ratings:
            # 按类型统计低评分
            type_counts = {}
            for feedback in low_ratings:
                feedback_type = feedback.get("feedback_type", "unknown")
                type_counts[feedback_type] = type_counts.get(feedback_type, 0) + 1
            
            # 找出问题最多的类型
            for feedback_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                improvement_areas.append(f"改进{feedback_type}类型的分析质量")
        
        return improvement_areas[:5]
    
    def _calculate_user_satisfaction(self, feedback_data: List[Dict[str, Any]]) -> float:
        """计算用户满意度"""
        if not feedback_data:
            return 0.0
        
        total_rating = sum(f.get("feedback_level", 3) for f in feedback_data)
        return total_rating / (len(feedback_data) * 5)  # 5分制转换为百分比
    
    def _analyze_scenario_performance(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析场景性能"""
        scenario_performance = {}
        
        for feedback in feedback_data:
            scenario = feedback.get("business_scenario", "unknown")
            if scenario not in scenario_performance:
                scenario_performance[scenario] = {
                    "total_feedback": 0,
                    "total_rating": 0,
                    "average_rating": 0.0
                }
            
            scenario_performance[scenario]["total_feedback"] += 1
            scenario_performance[scenario]["total_rating"] += feedback.get("feedback_level", 3)
        
        # 计算平均评分
        for scenario, data in scenario_performance.items():
            if data["total_feedback"] > 0:
                data["average_rating"] = data["total_rating"] / data["total_feedback"]
        
        return scenario_performance
    
    def _analyze_feedback_patterns(self, feedback_data: List[UserFeedback]) -> Dict[str, Any]:
        """分析反馈模式"""
        patterns = {
            "common_issues": [],
            "positive_patterns": [],
            "user_preferences": []
        }
        
        # 分析常见问题
        low_rating_feedback = [f for f in feedback_data if f.feedback_level.value <= 2]
        if low_rating_feedback:
            common_issues = {}
            for feedback in low_rating_feedback:
                issue_key = f"{feedback.feedback_type.value}_{feedback.business_scenario}"
                common_issues[issue_key] = common_issues.get(issue_key, 0) + 1
            
            patterns["common_issues"] = [
                {"issue": issue, "count": count} 
                for issue, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
        
        return patterns
    
    def _identify_problem_patterns(self, feedback_data: List[UserFeedback]) -> List[str]:
        """识别问题模式"""
        problem_patterns = []
        
        # 分析低评分模式
        low_ratings = [f for f in feedback_data if f.feedback_level.value <= 2]
        
        if low_ratings:
            # 按场景分析
            scenario_issues = {}
            for feedback in low_ratings:
                scenario = feedback.business_scenario
                if scenario not in scenario_issues:
                    scenario_issues[scenario] = []
                scenario_issues[scenario].append(feedback.feedback_type.value)
            
            for scenario, issues in scenario_issues.items():
                if len(issues) >= 2:  # 至少2个问题
                    problem_patterns.append(f"{scenario}场景存在多个问题: {', '.join(set(issues))}")
        
        return problem_patterns
    
    def _generate_improvement_strategies(self, feedback_patterns: Dict[str, Any], 
                                       problem_patterns: List[str]) -> List[str]:
        """生成改进策略"""
        strategies = []
        
        # 基于问题模式生成策略
        for pattern in problem_patterns:
            if "技术报告" in pattern:
                strategies.append("增强技术报告分析的专业性和深度")
            elif "商业提案" in pattern:
                strategies.append("提高商业提案分析的实用性和针对性")
            elif "合同分析" in pattern:
                strategies.append("加强合同分析的法律专业性和风险识别能力")
        
        # 基于反馈模式生成策略
        if feedback_patterns.get("common_issues"):
            strategies.append("针对常见问题优化分析算法和提示词")
        
        return strategies
    
    def _generate_prompt_optimization_suggestions(self, feedback_data: List[UserFeedback]) -> List[str]:
        """生成提示词优化建议"""
        suggestions = []
        
        # 分析反馈类型
        accuracy_issues = [f for f in feedback_data 
                          if f.feedback_type == FeedbackType.ACCURACY and f.feedback_level.value <= 2]
        relevance_issues = [f for f in feedback_data 
                           if f.feedback_type == FeedbackType.RELEVANCE and f.feedback_level.value <= 2]
        
        if accuracy_issues:
            suggestions.append("在提示词中增加准确性要求，要求模型提供更精确的分析")
        
        if relevance_issues:
            suggestions.append("优化提示词结构，明确分析重点和相关性要求")
        
        return suggestions 