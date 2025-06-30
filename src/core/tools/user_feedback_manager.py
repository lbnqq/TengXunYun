#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Feedback Manager - 核心模块

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
from collections import defaultdict, deque
import logging
from datetime import datetime, timedelta


class FeedbackType(Enum):
    """反馈类型枚举"""
    ACCURACY = "accuracy"           # 准确性反馈
    RELEVANCE = "relevance"         # 相关性反馈
    COMPLETENESS = "completeness"   # 完整性反馈
    CLARITY = "clarity"             # 清晰度反馈
    USEFULNESS = "usefulness"       # 实用性反馈
    FORMAT = "format"               # 格式反馈
    TIMELINESS = "timeliness"       # 及时性反馈
    GENERAL = "general"             # 一般反馈


class FeedbackLevel(Enum):
    """反馈级别枚举"""
    EXCELLENT = "excellent"     # 优秀
    GOOD = "good"              # 良好
    SATISFACTORY = "satisfactory"  # 满意
    NEEDS_IMPROVEMENT = "needs_improvement"  # 需要改进
    POOR = "poor"              # 差
    CRITICAL = "critical"      # 严重问题


@dataclass
class UserFeedback:
    """用户反馈数据结构"""
    feedback_id: str
    user_id: str
    session_id: str
    analysis_id: str
    feedback_type: FeedbackType
    feedback_level: FeedbackLevel
    content: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False
    improvement_suggestions: List[str] = field(default_factory=list)


@dataclass
class FeedbackAnalytics:
    """反馈分析数据结构"""
    total_feedback: int = 0
    feedback_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    feedback_by_level: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    average_satisfaction_score: float = 0.0
    improvement_areas: List[str] = field(default_factory=list)
    recent_trends: Dict[str, Any] = field(default_factory=dict)


class UserFeedbackManager:
    """
    用户反馈管理器
    
    负责收集、存储、分析和应用用户反馈，提供改进建议和统计报告。
    
    Attributes:
        feedback_storage: 反馈存储字典
        analytics: 反馈分析数据
        lock: 线程锁
        logger: 日志记录器
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化用户反馈管理器
        
        Args:
            storage_path: 反馈数据存储路径，如果为None则使用内存存储
        """
        self.storage_path = storage_path
        self.feedback_storage = {}
        self.analytics = FeedbackAnalytics()
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # 加载历史反馈数据
        if storage_path:
            self._load_feedback_data()
    
    def submit_feedback(self, user_id: str, session_id: str, analysis_id: str,
                       feedback_type: FeedbackType, feedback_level: FeedbackLevel,
                       content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        提交用户反馈
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            analysis_id: 分析ID
            feedback_type: 反馈类型
            feedback_level: 反馈级别
            content: 反馈内容
            metadata: 元数据
            
        Returns:
            反馈ID
            
        Raises:
            ValueError: 当必要参数缺失时
        """
        if not all([user_id, session_id, analysis_id, content]):
            raise ValueError("用户ID、会话ID、分析ID和反馈内容不能为空")
        
        feedback_id = str(uuid.uuid4())
        timestamp = time.time()
        
        feedback = UserFeedback(
            feedback_id=feedback_id,
            user_id=user_id,
            session_id=session_id,
            analysis_id=analysis_id,
            feedback_type=feedback_type,
            feedback_level=feedback_level,
            content=content,
            timestamp=timestamp,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.feedback_storage[feedback_id] = feedback
            self._update_analytics(feedback)
            
            # 保存到文件
            if self.storage_path:
                self._save_feedback_data()
        
        self.logger.info(f"用户反馈已提交: {feedback_id}, 类型: {feedback_type.value}, 级别: {feedback_level.value}")
        return feedback_id
    
    def get_feedback(self, feedback_id: str) -> Optional[UserFeedback]:
        """
        获取指定反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            反馈对象，如果不存在则返回None
        """
        return self.feedback_storage.get(feedback_id)
    
    def get_user_feedback(self, user_id: str, limit: int = 50) -> List[UserFeedback]:
        """
        获取用户的所有反馈
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            用户反馈列表
        """
        user_feedback = [
            feedback for feedback in self.feedback_storage.values()
            if feedback.user_id == user_id
        ]
        
        # 按时间倒序排序
        user_feedback.sort(key=lambda x: x.timestamp, reverse=True)
        return user_feedback[:limit]
    
    def get_session_feedback(self, session_id: str) -> List[UserFeedback]:
        """
        获取会话的所有反馈
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话反馈列表
        """
        return [
            feedback for feedback in self.feedback_storage.values()
            if feedback.session_id == session_id
        ]
    
    def get_analysis_feedback(self, analysis_id: str) -> List[UserFeedback]:
        """
        获取分析结果的所有反馈
        
        Args:
            analysis_id: 分析ID
            
        Returns:
            分析反馈列表
        """
        return [
            feedback for feedback in self.feedback_storage.values()
            if feedback.analysis_id == analysis_id
        ]
    
    def process_feedback(self, feedback_id: str) -> Dict[str, Any]:
        """
        处理反馈并生成改进建议
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            处理结果字典
            
        Raises:
            ValueError: 当反馈不存在时
        """
        feedback = self.get_feedback(feedback_id)
        if not feedback:
            raise ValueError(f"反馈不存在: {feedback_id}")
        
        # 生成改进建议
        improvement_suggestions = self._generate_improvement_suggestions(feedback)
        
        with self.lock:
            feedback.improvement_suggestions = improvement_suggestions
            feedback.processed = True
            
            # 保存到文件
            if self.storage_path:
                self._save_feedback_data()
        
        return {
            "feedback_id": feedback_id,
            "improvement_suggestions": improvement_suggestions,
            "processed": True,
            "processed_at": time.time()
        }
    
    def _generate_improvement_suggestions(self, feedback: UserFeedback) -> List[str]:
        """
        根据反馈生成改进建议
        
        Args:
            feedback: 反馈对象
            
        Returns:
            改进建议列表
        """
        suggestions = []
        
        # 根据反馈类型和级别生成建议
        if feedback.feedback_type == FeedbackType.ACCURACY:
            if feedback.feedback_level in [FeedbackLevel.NEEDS_IMPROVEMENT, FeedbackLevel.POOR, FeedbackLevel.CRITICAL]:
                suggestions.extend([
                    "增强数据验证和准确性检查机制",
                    "改进算法逻辑和推理过程",
                    "增加人工审核环节",
                    "建立准确性基准测试"
                ])
        
        elif feedback.feedback_type == FeedbackType.RELEVANCE:
            if feedback.feedback_level in [FeedbackType.NEEDS_IMPROVEMENT, FeedbackType.POOR, FeedbackType.CRITICAL]:
                suggestions.extend([
                    "优化内容相关性算法",
                    "改进上下文理解能力",
                    "增强主题匹配精度",
                    "建立相关性评估标准"
                ])
        
        elif feedback.feedback_type == FeedbackType.COMPLETENESS:
            if feedback.feedback_level in [FeedbackType.NEEDS_IMPROVEMENT, FeedbackType.POOR, FeedbackType.CRITICAL]:
                suggestions.extend([
                    "完善内容覆盖范围",
                    "增加遗漏信息检测",
                    "改进完整性检查机制",
                    "建立完整性评估标准"
                ])
        
        elif feedback.feedback_type == FeedbackType.CLARITY:
            if feedback.feedback_level in [FeedbackType.NEEDS_IMPROVEMENT, FeedbackType.POOR, FeedbackType.CRITICAL]:
                suggestions.extend([
                    "优化输出格式和结构",
                    "改进语言表达清晰度",
                    "增加可视化元素",
                    "建立清晰度评估标准"
                ])
        
        elif feedback.feedback_type == FeedbackType.USEFULNESS:
            if feedback.feedback_level in [FeedbackType.NEEDS_IMPROVEMENT, FeedbackType.POOR, FeedbackType.CRITICAL]:
                suggestions.extend([
                    "增强实用性评估",
                    "改进用户需求理解",
                    "优化输出内容价值",
                    "建立实用性评估标准"
                ])
        
        # 通用改进建议
        if feedback.feedback_level in [FeedbackType.POOR, FeedbackType.CRITICAL]:
            suggestions.extend([
                "增加用户反馈收集频率",
                "建立快速响应机制",
                "加强质量监控",
                "定期进行系统优化"
            ])
        
        return suggestions
    
    def get_analytics_report(self, time_range_days: int = 30) -> Dict[str, Any]:
        """
        获取反馈分析报告
        
        Args:
            time_range_days: 时间范围（天）
            
        Returns:
            分析报告字典
        """
        cutoff_time = time.time() - (time_range_days * 24 * 3600)
        
        # 筛选时间范围内的反馈
        recent_feedback = [
            feedback for feedback in self.feedback_storage.values()
            if feedback.timestamp >= cutoff_time
        ]
        
        # 计算统计信息
        total_recent = len(recent_feedback)
        feedback_by_type = defaultdict(int)
        feedback_by_level = defaultdict(int)
        satisfaction_scores = []
        
        for feedback in recent_feedback:
            feedback_by_type[feedback.feedback_type.value] += 1
            feedback_by_level[feedback.feedback_level.value] += 1
            
            # 计算满意度分数
            level_scores = {
                FeedbackLevel.EXCELLENT: 5,
                FeedbackLevel.GOOD: 4,
                FeedbackLevel.SATISFACTORY: 3,
                FeedbackLevel.NEEDS_IMPROVEMENT: 2,
                FeedbackLevel.POOR: 1,
                FeedbackLevel.CRITICAL: 0
            }
            satisfaction_scores.append(level_scores[feedback.feedback_level])
        
        # 计算平均满意度
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
        
        # 识别改进领域
        improvement_areas = []
        for feedback_type, count in feedback_by_type.items():
            if count > total_recent * 0.2:  # 超过20%的反馈
                improvement_areas.append(feedback_type)
        
        return {
            "time_range_days": time_range_days,
            "total_feedback": total_recent,
            "feedback_by_type": dict(feedback_by_type),
            "feedback_by_level": dict(feedback_by_level),
            "average_satisfaction_score": round(avg_satisfaction, 2),
            "improvement_areas": improvement_areas,
            "processed_feedback_count": len([f for f in recent_feedback if f.processed]),
            "unprocessed_feedback_count": len([f for f in recent_feedback if not f.processed])
        }
    
    def get_trend_analysis(self, days: int = 7) -> Dict[str, Any]:
        """
        获取趋势分析
        
        Args:
            days: 分析天数
            
        Returns:
            趋势分析结果
        """
        end_time = time.time()
        start_time = end_time - (days * 24 * 3600)
        
        # 按天分组反馈
        daily_feedback = defaultdict(list)
        for feedback in self.feedback_storage.values():
            if start_time <= feedback.timestamp <= end_time:
                date = datetime.fromtimestamp(feedback.timestamp).strftime('%Y-%m-%d')
                daily_feedback[date].append(feedback)
        
        # 计算每日统计
        daily_stats = {}
        for date, feedbacks in daily_feedback.items():
            level_scores = {
                FeedbackLevel.EXCELLENT: 5,
                FeedbackLevel.GOOD: 4,
                FeedbackLevel.SATISFACTORY: 3,
                FeedbackLevel.NEEDS_IMPROVEMENT: 2,
                FeedbackLevel.POOR: 1,
                FeedbackLevel.CRITICAL: 0
            }
            
            scores = [level_scores[f.feedback_level] for f in feedbacks]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            daily_stats[date] = {
                "total_feedback": len(feedbacks),
                "average_satisfaction": round(avg_score, 2),
                "feedback_types": defaultdict(int),
                "feedback_levels": defaultdict(int)
            }
            
            for feedback in feedbacks:
                daily_stats[date]["feedback_types"][feedback.feedback_type.value] += 1
                daily_stats[date]["feedback_levels"][feedback.feedback_level.value] += 1
        
        return {
            "analysis_period_days": days,
            "daily_statistics": daily_stats,
            "trend_summary": {
                "total_days": len(daily_stats),
                "total_feedback": sum(stats["total_feedback"] for stats in daily_stats.values()),
                "average_daily_feedback": sum(stats["total_feedback"] for stats in daily_stats.values()) / len(daily_stats) if daily_stats else 0
            }
        }
    
    def _update_analytics(self, feedback: UserFeedback):
        """
        更新分析数据
        
        Args:
            feedback: 反馈对象
        """
        self.analytics.total_feedback += 1
        self.analytics.feedback_by_type[feedback.feedback_type.value] += 1
        self.analytics.feedback_by_level[feedback.feedback_level.value] += 1
        
        # 更新平均满意度分数
        level_scores = {
            FeedbackLevel.EXCELLENT: 5,
            FeedbackLevel.GOOD: 4,
            FeedbackLevel.SATISFACTORY: 3,
            FeedbackLevel.NEEDS_IMPROVEMENT: 2,
            FeedbackLevel.POOR: 1,
            FeedbackLevel.CRITICAL: 0
        }
        
        current_score = level_scores[feedback.feedback_level]
        self.analytics.average_satisfaction_score = (
            (self.analytics.average_satisfaction_score * (self.analytics.total_feedback - 1) + current_score) /
            self.analytics.total_feedback
        )
    
    def _save_feedback_data(self):
        """保存反馈数据到文件"""
        if not self.storage_path:
            return
        
        try:
            data = {
                "feedback": {
                    feedback_id: asdict(feedback)
                    for feedback_id, feedback in self.feedback_storage.items()
                },
                "analytics": asdict(self.analytics),
                "saved_at": time.time()
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存反馈数据失败: {e}")
    
    def _load_feedback_data(self):
        """从文件加载反馈数据"""
        if not self.storage_path:
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载反馈数据
            for feedback_id, feedback_data in data.get("feedback", {}).items():
                feedback = UserFeedback(
                    feedback_id=feedback_data["feedback_id"],
                    user_id=feedback_data["user_id"],
                    session_id=feedback_data["session_id"],
                    analysis_id=feedback_data["analysis_id"],
                    feedback_type=FeedbackType(feedback_data["feedback_type"]),
                    feedback_level=FeedbackLevel(feedback_data["feedback_level"]),
                    content=feedback_data["content"],
                    timestamp=feedback_data["timestamp"],
                    metadata=feedback_data.get("metadata", {}),
                    processed=feedback_data.get("processed", False),
                    improvement_suggestions=feedback_data.get("improvement_suggestions", [])
                )
                self.feedback_storage[feedback_id] = feedback
            
            # 重新计算分析数据
            self.analytics = FeedbackAnalytics()
            for feedback in self.feedback_storage.values():
                self._update_analytics(feedback)
                
        except FileNotFoundError:
            self.logger.info("反馈数据文件不存在，将创建新文件")
        except Exception as e:
            self.logger.error(f"加载反馈数据失败: {e}")
    
    def clear_old_feedback(self, days: int = 90):
        """
        清理旧反馈数据
        
        Args:
            days: 保留天数
        """
        cutoff_time = time.time() - (days * 24 * 3600)
        
        with self.lock:
            old_feedback_ids = [
                feedback_id for feedback_id, feedback in self.feedback_storage.items()
                if feedback.timestamp < cutoff_time
            ]
            
            for feedback_id in old_feedback_ids:
                del self.feedback_storage[feedback_id]
            
            # 重新计算分析数据
            self.analytics = FeedbackAnalytics()
            for feedback in self.feedback_storage.values():
                self._update_analytics(feedback)
            
            # 保存到文件
            if self.storage_path:
                self._save_feedback_data()
        
        self.logger.info(f"已清理 {len(old_feedback_ids)} 条旧反馈数据") 