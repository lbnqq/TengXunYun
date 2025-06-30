#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Single Model Optimizer - 核心模块

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
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict


class OptimizationLevel(Enum):
    """优化级别"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"


@dataclass
class OptimizationConfig:
    """优化配置"""
    level: OptimizationLevel
    max_retries: int = 3
    cache_ttl: int = 3600
    max_cache_size: int = 1000
    quality_threshold: float = 0.8


@dataclass
class PerformanceMetrics:
    """性能指标"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    cache_hit_rate: float = 0.0
    quality_score: float = 0.0


class SingleModelOptimizer:
    """单模型优化器"""
    
    def __init__(self, llm_client, config: Optional[OptimizationConfig] = None):
        """初始化优化器"""
        self.llm_client = llm_client
        self.config = config or OptimizationConfig(level=OptimizationLevel.STANDARD)
        self.cache = {}
        self.metrics = PerformanceMetrics()
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def optimize_prompt(self, prompt: str) -> str:
        """优化prompt"""
        if self.config.level == OptimizationLevel.BASIC:
            return self._basic_prompt_optimization(prompt)
        elif self.config.level == OptimizationLevel.STANDARD:
            return self._standard_prompt_optimization(prompt)
        else:
            return self._advanced_prompt_optimization(prompt)
    
    def _basic_prompt_optimization(self, prompt: str) -> str:
        """基础prompt优化"""
        # 简单的清晰度优化
        if len(prompt) > 500:
            sentences = prompt.split('。')
            if len(sentences) > 5:
                prompt = '。'.join(sentences[:5]) + '。'
        return prompt
    
    def _standard_prompt_optimization(self, prompt: str) -> str:
        """标准prompt优化"""
        optimized = self._basic_prompt_optimization(prompt)
        
        # 添加结构化元素
        if "请" in optimized and "分析" in optimized:
            if "请从以下方面" not in optimized:
                optimized += "\n\n请从以下方面进行分析：\n1. \n2. \n3. \n4. \n5. "
        
        # 添加输出格式要求
        if "请提供" in optimized and "格式" not in optimized:
            optimized += "\n\n请提供结构化的输出格式。"
        
        return optimized
    
    def _advanced_prompt_optimization(self, prompt: str) -> str:
        """高级prompt优化"""
        optimized = self._standard_prompt_optimization(prompt)
        
        # 添加角色定位
        if "作为" not in optimized:
            optimized = "作为专业分析师，" + optimized
        
        # 添加质量标准
        if "质量" not in optimized:
            optimized += "\n\n请确保输出内容准确、专业、可操作。"
        
        return optimized
    
    def generate_text(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """生成文本（优化版本）"""
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
            optimized_prompt = self.optimize_prompt(prompt)
            
            # 调用LLM
            response = self._call_llm_with_retry(optimized_prompt)
            
            # 处理响应
            processed_response = self._process_response(response)
            
            # 缓存结果
            self._set_to_cache(cache_key, processed_response)
            
            # 更新指标
            response_time = time.time() - start_time
            self._update_metrics(True, response_time)
            
            return processed_response
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_metrics(False, response_time)
            raise
    
    def _generate_cache_key(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """生成缓存键"""
        content = prompt + json.dumps(context or {}, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取"""
        cache_entry = self.cache.get(key)
        if cache_entry and time.time() - cache_entry['timestamp'] < self.config.cache_ttl:
            return cache_entry['value']
        return None
    
    def _set_to_cache(self, key: str, value: Any):
        """设置到缓存"""
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
    
    def _call_llm_with_retry(self, prompt: str) -> str:
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
                    time.sleep(1.0 * (2 ** attempt))  # 指数退避
        
        if last_error:
            raise last_error
        else:
            raise Exception("LLM调用失败，未知错误")
    
    def _process_response(self, response: str) -> Dict[str, Any]:
        """处理响应"""
        processed = {
            "content": response,
            "processed": True,
            "format": "text",
            "processed_at": time.time()
        }
        
        # 尝试解析JSON
        try:
            json_data = json.loads(response)
            processed["content"] = json_data
            processed["format"] = "json"
        except json.JSONDecodeError:
            pass
        
        # 添加质量评估
        quality_score = self._assess_quality(response)
        processed["quality_score"] = quality_score
        
        return processed
    
    def _assess_quality(self, response: str) -> float:
        """评估质量"""
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
    
    def _update_metrics(self, success: bool, response_time: float):
        """更新性能指标"""
        with self.lock:
            self.metrics.total_requests += 1
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.total_requests - 1) + response_time) /
                self.metrics.total_requests
            )
            
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        with self.lock:
            return {
                "optimization_level": self.config.level.value,
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": (
                    self.metrics.successful_requests / max(self.metrics.total_requests, 1)
                ),
                "average_response_time": self.metrics.average_response_time,
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "quality_score": self.metrics.quality_score,
                "cache_size": len(self.cache)
            }
    
    def clear_cache(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def update_config(self, new_config: OptimizationConfig):
        """更新配置"""
        with self.lock:
            self.config = new_config
        self.logger.info(f"配置已更新: {new_config.level.value}") 