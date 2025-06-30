#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Monitor - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import time
import json
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """性能指标数据类"""
    timestamp: datetime
    operation: str
    duration: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_metrics: int = 10000):
        """
        初始化性能监控器
        
        Args:
            max_metrics: 最大保存的指标数量
        """
        self.max_metrics = max_metrics
        self.metrics = deque(maxlen=max_metrics)
        self.operation_stats = defaultdict(lambda: {
            'count': 0,
            'success_count': 0,
            'total_duration': 0.0,
            'avg_duration': 0.0,
            'min_duration': float('inf'),
            'max_duration': 0.0,
            'recent_errors': deque(maxlen=10)
        })
        self.lock = threading.RLock()
        
        # 实时统计
        self.current_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'avg_response_time': 0.0,
            'operations_per_minute': 0.0,
            'error_rate': 0.0
        }
        
        # 启动统计更新线程
        self._start_stats_updater()
    
    def record_metric(self, operation: str, duration: float, success: bool, 
                     error_message: str = None, metadata: Dict[str, Any] = None):
        """记录性能指标"""
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            operation=operation,
            duration=duration,
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.metrics.append(metric)
            self._update_operation_stats(metric)
    
    def _update_operation_stats(self, metric: PerformanceMetric):
        """更新操作统计"""
        stats = self.operation_stats[metric.operation]
        stats['count'] += 1
        stats['total_duration'] += metric.duration
        stats['avg_duration'] = stats['total_duration'] / stats['count']
        stats['min_duration'] = min(stats['min_duration'], metric.duration)
        stats['max_duration'] = max(stats['max_duration'], metric.duration)
        
        if metric.success:
            stats['success_count'] += 1
        else:
            if metric.error_message:
                stats['recent_errors'].append({
                    'timestamp': metric.timestamp.isoformat(),
                    'error': metric.error_message
                })
    
    def get_operation_stats(self, operation: str = None) -> Dict[str, Any]:
        """获取操作统计信息"""
        with self.lock:
            if operation:
                if operation in self.operation_stats:
                    stats = dict(self.operation_stats[operation])
                    stats['success_rate'] = stats['success_count'] / max(stats['count'], 1)
                    stats['error_rate'] = (stats['count'] - stats['success_count']) / max(stats['count'], 1)
                    return stats
                else:
                    return {}
            else:
                result = {}
                for op, stats in self.operation_stats.items():
                    op_stats = dict(stats)
                    op_stats['success_rate'] = op_stats['success_count'] / max(op_stats['count'], 1)
                    op_stats['error_rate'] = (op_stats['count'] - op_stats['success_count']) / max(op_stats['count'], 1)
                    result[op] = op_stats
                return result
    
    def get_current_stats(self) -> Dict[str, Any]:
        """获取当前统计信息"""
        with self.lock:
            return dict(self.current_stats)
    
    def get_time_series_data(self, operation: str = None, 
                           time_window: timedelta = timedelta(hours=1)) -> List[Dict[str, Any]]:
        """获取时间序列数据"""
        cutoff_time = datetime.now() - time_window
        
        with self.lock:
            filtered_metrics = [
                metric for metric in self.metrics
                if metric.timestamp >= cutoff_time and (operation is None or metric.operation == operation)
            ]
        
        return [
            {
                'timestamp': metric.timestamp.isoformat(),
                'operation': metric.operation,
                'duration': metric.duration,
                'success': metric.success,
                'error_message': metric.error_message,
                'metadata': metric.metadata
            }
            for metric in filtered_metrics
        ]
    
    def get_performance_summary(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """获取性能摘要"""
        cutoff_time = datetime.now() - time_window
        
        with self.lock:
            recent_metrics = [
                metric for metric in self.metrics
                if metric.timestamp >= cutoff_time
            ]
        
        if not recent_metrics:
            return {
                'total_operations': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'operations_per_hour': 0.0,
                'top_operations': [],
                'recent_errors': []
            }
        
        total_ops = len(recent_metrics)
        successful_ops = sum(1 for m in recent_metrics if m.success)
        total_duration = sum(m.duration for m in recent_metrics)
        
        # 按操作类型分组
        operation_counts = defaultdict(int)
        for metric in recent_metrics:
            operation_counts[metric.operation] += 1
        
        # 获取最近的错误
        recent_errors = [
            {
                'timestamp': m.timestamp.isoformat(),
                'operation': m.operation,
                'error': m.error_message
            }
            for m in recent_metrics[-10:] if not m.success and m.error_message
        ]
        
        return {
            'time_window_hours': time_window.total_seconds() / 3600,
            'total_operations': total_ops,
            'successful_operations': successful_ops,
            'failed_operations': total_ops - successful_ops,
            'success_rate': successful_ops / total_ops if total_ops > 0 else 0.0,
            'avg_response_time': total_duration / total_ops if total_ops > 0 else 0.0,
            'operations_per_hour': total_ops / (time_window.total_seconds() / 3600),
            'top_operations': sorted(operation_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'recent_errors': recent_errors
        }
    
    def _start_stats_updater(self):
        """启动统计更新线程"""
        def update_stats():
            while True:
                try:
                    self._update_current_stats()
                    time.sleep(60)  # 每分钟更新一次
                except Exception as e:
                    logger.error(f"Stats updater error: {e}")
                    time.sleep(60)
        
        stats_thread = threading.Thread(target=update_stats, daemon=True)
        stats_thread.start()
    
    def _update_current_stats(self):
        """更新当前统计信息"""
        with self.lock:
            # 计算最近一小时的统计
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_metrics = [m for m in self.metrics if m.timestamp >= one_hour_ago]
            
            if recent_metrics:
                total_ops = len(recent_metrics)
                successful_ops = sum(1 for m in recent_metrics if m.success)
                total_duration = sum(m.duration for m in recent_metrics)
                
                self.current_stats.update({
                    'total_operations': total_ops,
                    'successful_operations': successful_ops,
                    'failed_operations': total_ops - successful_ops,
                    'avg_response_time': total_duration / total_ops if total_ops > 0 else 0.0,
                    'operations_per_minute': total_ops / 60.0,
                    'error_rate': (total_ops - successful_ops) / total_ops if total_ops > 0 else 0.0
                })
    
    def clear_metrics(self):
        """清空指标数据"""
        with self.lock:
            self.metrics.clear()
            self.operation_stats.clear()
            logger.info("Performance metrics cleared")
    
    def export_metrics(self, filepath: str, time_window: timedelta = timedelta(hours=24)):
        """导出指标数据到文件"""
        try:
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'time_window_hours': time_window.total_seconds() / 3600,
                'performance_summary': self.get_performance_summary(time_window),
                'operation_stats': self.get_operation_stats(),
                'time_series_data': self.get_time_series_data(time_window=time_window)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Performance metrics exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")

# 全局性能监控器实例
_global_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor

def record_performance(operation: str, duration: float, success: bool, 
                      error_message: str = None, metadata: Dict[str, Any] = None):
    """记录性能指标的便捷函数"""
    monitor = get_performance_monitor()
    monitor.record_metric(operation, duration, success, error_message, metadata)

class PerformanceTimer:
    """性能计时器上下文管理器"""
    
    def __init__(self, operation: str, metadata: Dict[str, Any] = None):
        self.operation = operation
        self.metadata = metadata or {}
        self.start_time = None
        self.success = True
        self.error_message = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is not None:
            self.success = False
            self.error_message = str(exc_val)
        
        record_performance(
            self.operation, 
            duration, 
            self.success, 
            self.error_message, 
            self.metadata
        )
        
        return False  # 不抑制异常
