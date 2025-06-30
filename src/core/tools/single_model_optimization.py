#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Single Model Optimization - 核心模块

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
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import time
import hashlib
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import threading
from collections import defaultdict, deque
import random


class OptimizationLevel(Enum):
    """优化级别枚举"""
    BASIC = "basic"           # 基础优化
    STANDARD = "standard"     # 标准优化
    ADVANCED = "advanced"     # 高级优化
    EXPERT = "expert"         # 专家级优化


class CacheStrategy(Enum):
    """缓存策略枚举"""
    NONE = "none"             # 不缓存
    BASIC = "basic"           # 基础缓存
    SMART = "smart"           # 智能缓存
    AGGRESSIVE = "aggressive" # 激进缓存


@dataclass
class OptimizationConfig:
    """优化配置"""
    optimization_level: OptimizationLevel
    cache_strategy: CacheStrategy
    max_retries: int = 3
    retry_delay: float = 1.0
    cache_ttl: int = 3600
    max_cache_size: int = 1000
    quality_threshold: float = 0.8
    performance_threshold: float = 5.0  # 秒


@dataclass
class PerformanceMetrics:
    """性能指标"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    total_response_time: float = 0.0
    cache_hit_rate: float = 0.0
    quality_score: float = 0.0
    error_distribution: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    response_time_distribution: Dict[str, int] = field(default_factory=lambda: defaultdict(int))


class SingleModelOptimizer:
    """
    单模型优化器
    
    专门针对讯飞星火模型进行深度优化，提供全方位的性能和质量优化。
    
    Attributes:
        llm_client: LLM客户端实例
        config: 优化配置
        cache: 智能缓存
        metrics: 性能指标
        lock: 线程锁
        logger: 日志记录器
    """
    
    def __init__(self, llm_client, config: Optional[OptimizationConfig] = None):
        """
        初始化单模型优化器
        
        Args:
            llm_client: LLM客户端实例
            config: 优化配置，如果为None则使用默认配置
        """
        self.llm_client = llm_client
        self.config = config or OptimizationConfig(
            optimization_level=OptimizationLevel.STANDARD,
            cache_strategy=CacheStrategy.SMART
        )
        
        self.cache = {}
        self.metrics = PerformanceMetrics()
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # 初始化优化组件
        self._initialize_optimization_components()
    
    def _initialize_optimization_components(self):
        """初始化优化组件"""
        # 根据优化级别设置组件
        if self.config.optimization_level == OptimizationLevel.BASIC:
            self._setup_basic_optimization()
        elif self.config.optimization_level == OptimizationLevel.STANDARD:
            self._setup_standard_optimization()
        elif self.config.optimization_level == OptimizationLevel.ADVANCED:
            self._setup_advanced_optimization()
        elif self.config.optimization_level == OptimizationLevel.EXPERT:
            self._setup_expert_optimization()
    
    def _setup_basic_optimization(self):
        """设置基础优化"""
        self.prompt_optimizer = self._create_basic_prompt_optimizer()
        self.context_optimizer = self._create_basic_context_optimizer()
        self.response_processor = self._create_basic_response_processor()
    
    def _setup_standard_optimization(self):
        """设置标准优化"""
        self.prompt_optimizer = self._create_standard_prompt_optimizer()
        self.context_optimizer = self._create_standard_context_optimizer()
        self.response_processor = self._create_standard_response_processor()
        self.quality_assessor = self._create_quality_assessor()
    
    def _setup_advanced_optimization(self):
        """设置高级优化"""
        self.prompt_optimizer = self._create_advanced_prompt_optimizer()
        self.context_optimizer = self._create_advanced_context_optimizer()
        self.response_processor = self._create_advanced_response_processor()
        self.quality_assessor = self._create_advanced_quality_assessor()
        self.cache_manager = self._create_cache_manager()
    
    def _setup_expert_optimization(self):
        """设置专家级优化"""
        self.prompt_optimizer = self._create_expert_prompt_optimizer()
        self.context_optimizer = self._create_expert_context_optimizer()
        self.response_processor = self._create_expert_response_processor()
        self.quality_assessor = self._create_expert_quality_assessor()
        self.cache_manager = self._create_expert_cache_manager()
        self.performance_monitor = self._create_performance_monitor()
    
    def _create_basic_prompt_optimizer(self):
        """创建基础prompt优化器"""
        return {
            "optimize": lambda prompt: self._basic_prompt_optimization(prompt),
            "level": "basic"
        }
    
    def _create_standard_prompt_optimizer(self):
        """创建标准prompt优化器"""
        return {
            "optimize": lambda prompt: self._standard_prompt_optimization(prompt),
            "level": "standard"
        }
    
    def _create_advanced_prompt_optimizer(self):
        """创建高级prompt优化器"""
        return {
            "optimize": lambda prompt: self._advanced_prompt_optimization(prompt),
            "level": "advanced"
        }
    
    def _create_expert_prompt_optimizer(self):
        """创建专家级prompt优化器"""
        return {
            "optimize": lambda prompt: self._expert_prompt_optimization(prompt),
            "level": "expert"
        }
    
    def _basic_prompt_optimization(self, prompt: str) -> str:
        """基础prompt优化"""
        # 简单的清晰度优化
        if len(prompt) > 500:
            # 分割长prompt
            sentences = prompt.split('。')
            if len(sentences) > 5:
                prompt = '。'.join(sentences[:5]) + '。'
        
        return prompt
    
    def _standard_prompt_optimization(self, prompt: str) -> str:
        """标准prompt优化"""
        optimized_prompt = self._basic_prompt_optimization(prompt)
        
        # 添加结构化元素
        if "请" in optimized_prompt and "分析" in optimized_prompt:
            if "请从以下方面" not in optimized_prompt:
                optimized_prompt += "\n\n请从以下方面进行分析：\n1. \n2. \n3. \n4. \n5. "
        
        # 添加输出格式要求
        if "请提供" in optimized_prompt and "格式" not in optimized_prompt:
            optimized_prompt += "\n\n请提供结构化的输出格式。"
        
        return optimized_prompt
    
    def _advanced_prompt_optimization(self, prompt: str) -> str:
        """高级prompt优化"""
        optimized_prompt = self._standard_prompt_optimization(prompt)
        
        # 添加角色定位
        if "作为" not in optimized_prompt:
            optimized_prompt = "作为专业分析师，" + optimized_prompt
        
        # 添加质量标准
        if "质量" not in optimized_prompt:
            optimized_prompt += "\n\n请确保输出内容准确、专业、可操作。"
        
        # 添加示例要求
        if "示例" not in optimized_prompt and "例子" not in optimized_prompt:
            optimized_prompt += "\n\n如有可能，请提供具体的示例。"
        
        return optimized_prompt
    
    def _expert_prompt_optimization(self, prompt: str) -> str:
        """专家级prompt优化"""
        optimized_prompt = self._advanced_prompt_optimization(prompt)
        
        # 添加上下文增强
        optimized_prompt = self._enhance_context(optimized_prompt)
        
        # 添加约束条件
        optimized_prompt = self._add_constraints(optimized_prompt)
        
        # 添加质量检查点
        optimized_prompt = self._add_quality_checkpoints(optimized_prompt)
        
        return optimized_prompt
    
    def _enhance_context(self, prompt: str) -> str:
        """增强上下文"""
        # 添加时间上下文
        current_time = time.strftime("%Y年%m月%d日")
        prompt = f"当前时间：{current_time}\n\n" + prompt
        
        # 添加任务上下文
        if "任务" not in prompt:
            prompt += "\n\n任务目标：提供高质量、专业、可操作的分析结果。"
        
        return prompt
    
    def _add_constraints(self, prompt: str) -> str:
        """添加约束条件"""
        constraints = [
            "输出长度控制在合理范围内",
            "使用准确的专业术语",
            "提供可验证的数据支持",
            "确保逻辑清晰连贯"
        ]
        
        prompt += "\n\n约束条件：\n"
        for i, constraint in enumerate(constraints, 1):
            prompt += f"{i}. {constraint}\n"
        
        return prompt
    
    def _add_quality_checkpoints(self, prompt: str) -> str:
        """添加质量检查点"""
        checkpoints = [
            "准确性检查：确保信息准确无误",
            "完整性检查：确保内容完整全面",
            "清晰性检查：确保表达清晰易懂",
            "实用性检查：确保建议可操作"
        ]
        
        prompt += "\n\n质量检查点：\n"
        for checkpoint in checkpoints:
            prompt += f"- {checkpoint}\n"
        
        return prompt
    
    def _create_basic_context_optimizer(self):
        """创建基础上下文优化器"""
        return {
            "optimize": lambda context: self._basic_context_optimization(context),
            "level": "basic"
        }
    
    def _create_standard_context_optimizer(self):
        """创建标准上下文优化器"""
        return {
            "optimize": lambda context: self._standard_context_optimization(context),
            "level": "standard"
        }
    
    def _create_advanced_context_optimizer(self):
        """创建高级上下文优化器"""
        return {
            "optimize": lambda context: self._advanced_context_optimization(context),
            "level": "advanced"
        }
    
    def _create_expert_context_optimizer(self):
        """创建专家级上下文优化器"""
        return {
            "optimize": lambda context: self._expert_context_optimization(context),
            "level": "expert"
        }
    
    def _basic_context_optimization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """基础上下文优化"""
        # 简单的上下文清理
        optimized_context = {}
        for key, value in context.items():
            if value is not None and value != "":
                optimized_context[key] = value
        
        return optimized_context
    
    def _standard_context_optimization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """标准上下文优化"""
        optimized_context = self._basic_context_optimization(context)
        
        # 添加默认值
        if "max_length" not in optimized_context:
            optimized_context["max_length"] = 2000
        
        if "temperature" not in optimized_context:
            optimized_context["temperature"] = 0.7
        
        return optimized_context
    
    def _advanced_context_optimization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """高级上下文优化"""
        optimized_context = self._standard_context_optimization(context)
        
        # 智能参数调整
        if "task_type" in optimized_context:
            task_type = optimized_context["task_type"]
            if task_type == "analysis":
                optimized_context["temperature"] = 0.3
                optimized_context["max_length"] = 3000
            elif task_type == "generation":
                optimized_context["temperature"] = 0.8
                optimized_context["max_length"] = 1500
            elif task_type == "review":
                optimized_context["temperature"] = 0.5
                optimized_context["max_length"] = 2500
        
        return optimized_context
    
    def _expert_context_optimization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """专家级上下文优化"""
        optimized_context = self._advanced_context_optimization(context)
        
        # 动态参数优化
        optimized_context = self._dynamic_parameter_optimization(optimized_context)
        
        # 上下文增强
        optimized_context = self._enhance_context_data(optimized_context)
        
        return optimized_context
    
    def _dynamic_parameter_optimization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """动态参数优化"""
        # 根据历史性能调整参数
        if self.metrics.average_response_time > self.config.performance_threshold:
            # 性能较慢，降低复杂度
            context["max_length"] = min(context.get("max_length", 2000), 1500)
            context["temperature"] = min(context.get("temperature", 0.7), 0.5)
        
        if self.metrics.quality_score < self.config.quality_threshold:
            # 质量较低，提高精确度
            context["temperature"] = max(context.get("temperature", 0.7), 0.3)
        
        return context
    
    def _enhance_context_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """增强上下文数据"""
        # 添加性能历史
        context["performance_history"] = {
            "average_response_time": self.metrics.average_response_time,
            "success_rate": self.metrics.successful_requests / max(self.metrics.total_requests, 1),
            "quality_score": self.metrics.quality_score
        }
        
        # 添加优化建议
        context["optimization_suggestions"] = self._generate_optimization_suggestions()
        
        return context
    
    def _generate_optimization_suggestions(self) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        if self.metrics.average_response_time > 5.0:
            suggestions.append("响应时间较长，建议优化prompt长度和复杂度")
        
        if self.metrics.quality_score < 0.8:
            suggestions.append("质量分数较低，建议提高prompt的明确性和结构化程度")
        
        if self.metrics.cache_hit_rate < 0.3:
            suggestions.append("缓存命中率较低，建议优化缓存策略")
        
        return suggestions
    
    def _create_basic_response_processor(self):
        """创建基础响应处理器"""
        return {
            "process": lambda response: self._basic_response_processing(response),
            "level": "basic"
        }
    
    def _create_standard_response_processor(self):
        """创建标准响应处理器"""
        return {
            "process": lambda response: self._standard_response_processing(response),
            "level": "standard"
        }
    
    def _create_advanced_response_processor(self):
        """创建高级响应处理器"""
        return {
            "process": lambda response: self._advanced_response_processing(response),
            "level": "advanced"
        }
    
    def _create_expert_response_processor(self):
        """创建专家级响应处理器"""
        return {
            "process": lambda response: self._expert_response_processing(response),
            "level": "expert"
        }
    
    def _basic_response_processing(self, response: str) -> Dict[str, Any]:
        """基础响应处理"""
        return {
            "content": response,
            "processed": True,
            "format": "text"
        }
    
    def _standard_response_processing(self, response: str) -> Dict[str, Any]:
        """标准响应处理"""
        processed_response = self._basic_response_processing(response)
        
        # 尝试解析JSON
        try:
            json_data = json.loads(response)
            processed_response["content"] = json_data
            processed_response["format"] = "json"
        except json.JSONDecodeError:
            # 保持文本格式
            pass
        
        return processed_response
    
    def _advanced_response_processing(self, response: str) -> Dict[str, Any]:
        """高级响应处理"""
        processed_response = self._standard_response_processing(response)
        
        # 添加质量评估
        quality_score = self._assess_response_quality(response)
        processed_response["quality_score"] = quality_score
        
        # 添加处理时间戳
        processed_response["processed_at"] = time.time()
        
        return processed_response
    
    def _expert_response_processing(self, response: str) -> Dict[str, Any]:
        """专家级响应处理"""
        processed_response = self._advanced_response_processing(response)
        
        # 添加内容分析
        content_analysis = self._analyze_response_content(response)
        processed_response["content_analysis"] = content_analysis
        
        # 添加改进建议
        improvement_suggestions = self._generate_response_improvements(response)
        processed_response["improvement_suggestions"] = improvement_suggestions
        
        return processed_response
    
    def _assess_response_quality(self, response: str) -> float:
        """评估响应质量"""
        score = 0.8  # 基础分数
        
        # 长度评估
        if 100 <= len(response) <= 2000:
            score += 0.1
        
        # 结构评估
        if any(marker in response for marker in ['1.', '2.', '3.', '首先', '其次', '最后']):
            score += 0.05
        
        # 专业性评估
        if any(word in response for word in ['分析', '评估', '建议', '结论']):
            score += 0.05
        
        return min(1.0, score)
    
    def _analyze_response_content(self, response: str) -> Dict[str, Any]:
        """分析响应内容"""
        analysis = {
            "length": len(response),
            "word_count": len(response.split()),
            "has_structure": any(marker in response for marker in ['1.', '2.', '3.']),
            "has_numbers": any(char.isdigit() for char in response),
            "has_keywords": any(word in response for word in ['分析', '评估', '建议', '结论'])
        }
        
        return analysis
    
    def _generate_response_improvements(self, response: str) -> List[str]:
        """生成响应改进建议"""
        suggestions = []
        
        if len(response) < 100:
            suggestions.append("响应内容较短，建议提供更详细的分析")
        
        if not any(marker in response for marker in ['1.', '2.', '3.']):
            suggestions.append("建议使用编号列表提高结构化程度")
        
        if not any(word in response for word in ['分析', '评估', '建议']):
            suggestions.append("建议包含具体的分析和建议内容")
        
        return suggestions
    
    def _create_quality_assessor(self):
        """创建质量评估器"""
        return {
            "assess": lambda response: self._assess_quality(response),
            "level": "standard"
        }
    
    def _create_advanced_quality_assessor(self):
        """创建高级质量评估器"""
        return {
            "assess": lambda response: self._advanced_quality_assessment(response),
            "level": "advanced"
        }
    
    def _create_expert_quality_assessor(self):
        """创建专家级质量评估器"""
        return {
            "assess": lambda response: self._expert_quality_assessment(response),
            "level": "expert"
        }
    
    def _assess_quality(self, response: Dict[str, Any]) -> float:
        """基础质量评估"""
        return response.get("quality_score", 0.8)
    
    def _advanced_quality_assessment(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """高级质量评估"""
        quality_score = self._assess_quality(response)
        
        return {
            "overall_score": quality_score,
            "content_quality": quality_score * 0.4,
            "structure_quality": quality_score * 0.3,
            "relevance_quality": quality_score * 0.3,
            "assessment_time": time.time()
        }
    
    def _expert_quality_assessment(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """专家级质量评估"""
        assessment = self._advanced_quality_assessment(response)
        
        # 添加详细分析
        assessment["detailed_analysis"] = self._detailed_quality_analysis(response)
        
        # 添加质量趋势
        assessment["quality_trend"] = self._calculate_quality_trend()
        
        return assessment
    
    def _detailed_quality_analysis(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """详细质量分析"""
        content = response.get("content", "")
        if isinstance(content, dict):
            content = str(content)
        
        analysis = {
            "readability": self._assess_readability(content),
            "completeness": self._assess_completeness(content),
            "accuracy": self._assess_accuracy(content),
            "usefulness": self._assess_usefulness(content)
        }
        
        return analysis
    
    def _assess_readability(self, content: str) -> float:
        """评估可读性"""
        # 简单的可读性评估
        sentences = content.split('。')
        avg_sentence_length = sum(len(s) for s in sentences) / max(len(sentences), 1)
        
        if avg_sentence_length < 30:
            return 0.9
        elif avg_sentence_length < 50:
            return 0.7
        else:
            return 0.5
    
    def _assess_completeness(self, content: str) -> float:
        """评估完整性"""
        # 检查是否包含关键元素
        key_elements = ['分析', '结论', '建议']
        found_elements = sum(1 for element in key_elements if element in content)
        
        return found_elements / len(key_elements)
    
    def _assess_accuracy(self, content: str) -> float:
        """评估准确性"""
        # 基础准确性评估
        return 0.8  # 默认值，实际应用中需要更复杂的逻辑
    
    def _assess_usefulness(self, content: str) -> float:
        """评估实用性"""
        # 检查是否包含可操作的建议
        if '建议' in content or '可以' in content or '应该' in content:
            return 0.9
        else:
            return 0.6
    
    def _calculate_quality_trend(self) -> Dict[str, Any]:
        """计算质量趋势"""
        # 简化的趋势计算
        return {
            "trend": "stable",
            "average_quality": self.metrics.quality_score,
            "quality_variance": 0.1
        }
    
    def _create_cache_manager(self):
        """创建缓存管理器"""
        return {
            "get": lambda key: self._get_from_cache(key),
            "set": lambda key, value: self._set_to_cache(key, value),
            "clear": lambda: self._clear_cache(),
            "level": "advanced"
        }
    
    def _create_expert_cache_manager(self):
        """创建专家级缓存管理器"""
        return {
            "get": lambda key: self._smart_get_from_cache(key),
            "set": lambda key, value: self._smart_set_to_cache(key, value),
            "clear": lambda: self._clear_cache(),
            "optimize": lambda: self._optimize_cache(),
            "level": "expert"
        }
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取"""
        if self.config.cache_strategy == CacheStrategy.NONE:
            return None
        
        cache_entry = self.cache.get(key)
        if cache_entry and time.time() - cache_entry['timestamp'] < self.config.cache_ttl:
            return cache_entry['value']
        
        return None
    
    def _smart_get_from_cache(self, key: str) -> Optional[Any]:
        """智能从缓存获取"""
        value = self._get_from_cache(key)
        
        if value is not None:
            # 更新缓存命中统计
            self.metrics.cache_hit_rate = (
                self.metrics.cache_hit_rate * 0.9 + 0.1
            )
        
        return value
    
    def _set_to_cache(self, key: str, value: Any):
        """设置到缓存"""
        if self.config.cache_strategy == CacheStrategy.NONE:
            return
        
        # 检查缓存大小
        if len(self.cache) >= self.config.max_cache_size:
            # 删除最旧的缓存项
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def _smart_set_to_cache(self, key: str, value: Any):
        """智能设置到缓存"""
        self._set_to_cache(key, value)
        
        # 根据缓存策略调整TTL
        if self.config.cache_strategy == CacheStrategy.AGGRESSIVE:
            # 激进缓存策略，延长TTL
            self.cache[key]['ttl'] = self.config.cache_ttl * 2
    
    def _clear_cache(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def _optimize_cache(self):
        """优化缓存"""
        # 删除过期缓存
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] > self.config.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        # 如果缓存仍然过大，删除最旧的项
        while len(self.cache) > self.config.max_cache_size * 0.8:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
    
    def _create_performance_monitor(self):
        """创建性能监控器"""
        return {
            "monitor": lambda: self._monitor_performance(),
            "get_metrics": lambda: self._get_performance_metrics(),
            "level": "expert"
        }
    
    def _monitor_performance(self):
        """监控性能"""
        # 更新性能指标
        with self.lock:
            # 计算平均响应时间
            if self.metrics.total_requests > 0:
                self.metrics.average_response_time = (
                    self.metrics.total_response_time / self.metrics.total_requests
                )
            
            # 计算成功率
            success_rate = (
                self.metrics.successful_requests / max(self.metrics.total_requests, 1)
            )
            
            # 更新质量分数
            self.metrics.quality_score = success_rate * 0.7 + self.metrics.cache_hit_rate * 0.3
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        with self.lock:
            return {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": (
                    self.metrics.successful_requests / max(self.metrics.total_requests, 1)
                ),
                "average_response_time": self.metrics.average_response_time,
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "quality_score": self.metrics.quality_score,
                "error_distribution": dict(self.metrics.error_distribution),
                "cache_size": len(self.cache)
            }
    
    def generate_text(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        生成文本（优化版本）
        
        Args:
            prompt: 输入prompt
            context: 上下文信息
            
        Returns:
            生成结果字典
        """
        start_time = time.time()
        
        try:
            # 生成缓存键
            cache_key = self._generate_cache_key(prompt, context)
            
            # 检查缓存
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self._update_metrics(True, time.time() - start_time)
                return cached_result
            
            # 优化prompt
            optimized_prompt = self.prompt_optimizer["optimize"](prompt)
            
            # 优化上下文
            optimized_context = self.context_optimizer["optimize"](context or {})
            
            # 调用LLM
            response = self._call_llm_with_retry(optimized_prompt, optimized_context)
            
            # 处理响应
            processed_response = self.response_processor["process"](response)
            
            # 质量评估
            if hasattr(self, 'quality_assessor'):
                quality_result = self.quality_assessor["assess"](processed_response)
                processed_response["quality_assessment"] = quality_result
            
            # 缓存结果
            self._set_to_cache(cache_key, processed_response)
            
            # 更新指标
            response_time = time.time() - start_time
            self._update_metrics(True, response_time)
            
            return processed_response
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_metrics(False, response_time, str(e))
            raise
    
    def _generate_cache_key(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """生成缓存键"""
        content = prompt + json.dumps(context or {}, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _call_llm_with_retry(self, prompt: str, context: Dict[str, Any]) -> str:
        """带重试的LLM调用"""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.llm_client.generate_text(prompt)
                return response
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"LLM调用失败，尝试 {attempt + 1}/{self.config.max_retries}: {e}")
                
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))  # 指数退避
        
        if last_error:
            raise last_error
        else:
            raise Exception("LLM调用失败，未知错误")
    
    def _update_metrics(self, success: bool, response_time: float, error_type: str = None):
        """更新性能指标"""
        with self.lock:
            self.metrics.total_requests += 1
            self.metrics.total_response_time += response_time
            
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
                if error_type:
                    self.metrics.error_distribution[error_type] += 1
            
            # 更新响应时间分布
            if response_time < 1.0:
                self.metrics.response_time_distribution["fast"] += 1
            elif response_time < 3.0:
                self.metrics.response_time_distribution["normal"] += 1
            else:
                self.metrics.response_time_distribution["slow"] += 1
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """
        获取优化报告
        
        Returns:
            优化报告字典
        """
        with self.lock:
            return {
                "optimization_level": self.config.optimization_level.value,
                "cache_strategy": self.config.cache_strategy.value,
                "performance_metrics": self._get_performance_metrics(),
                "cache_statistics": {
                    "cache_size": len(self.cache),
                    "max_cache_size": self.config.max_cache_size,
                    "cache_utilization": len(self.cache) / self.config.max_cache_size
                },
                "optimization_components": {
                    "prompt_optimizer": self.prompt_optimizer["level"],
                    "context_optimizer": self.context_optimizer["level"],
                    "response_processor": self.response_processor["level"]
                }
            }
    
    def update_config(self, new_config: OptimizationConfig):
        """
        更新优化配置
        
        Args:
            new_config: 新的优化配置
        """
        with self.lock:
            self.config = new_config
            self._initialize_optimization_components()
        
        self.logger.info(f"优化配置已更新: {new_config.optimization_level.value}")
    
    def clear_cache(self):
        """清空缓存"""
        self._clear_cache()
        self.logger.info("缓存已清空")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计字典
        """
        with self.lock:
            return {
                "cache_size": len(self.cache),
                "max_cache_size": self.config.max_cache_size,
                "cache_utilization": len(self.cache) / self.config.max_cache_size,
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "cache_strategy": self.config.cache_strategy.value
            } 