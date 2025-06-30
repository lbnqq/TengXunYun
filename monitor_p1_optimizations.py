#!/usr/bin/env python3
"""
P1优化模块持续监控脚本

实时监控P1优先级任务模块的性能、质量和用户反馈，
确保系统稳定运行和持续优化。

Author: AI Assistant
Date: 2025-01-28
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('p1_monitoring.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class P1OptimizationMonitor:
    """P1优化模块监控器"""
    
    def __init__(self):
        self.monitoring_data = {
            "performance_metrics": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0,
                "total_response_time": 0.0
            },
            "quality_metrics": {
                "average_quality_score": 0.0,
                "quality_threshold_violations": 0,
                "total_assessments": 0
            },
            "user_feedback": {
                "total_feedback": 0,
                "positive_feedback": 0,
                "negative_feedback": 0,
                "improvement_suggestions": []
            },
            "system_health": {
                "last_check": None,
                "status": "healthy",
                "alerts": []
            }
        }
        self.monitoring_active = False
        self.alert_thresholds = {
            "max_response_time": 5.0,  # 秒
            "min_success_rate": 0.95,  # 95%
            "min_quality_score": 0.7,  # 70%
            "max_error_rate": 0.05     # 5%
        }
    
    def start_monitoring(self):
        """启动监控"""
        logger.info("启动P1优化模块监控...")
        self.monitoring_active = True
        
        # 启动性能监控线程
        performance_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        performance_thread.start()
        
        # 启动质量监控线程
        quality_thread = threading.Thread(target=self._monitor_quality, daemon=True)
        quality_thread.start()
        
        # 启动用户反馈监控线程
        feedback_thread = threading.Thread(target=self._monitor_user_feedback, daemon=True)
        feedback_thread.start()
        
        # 启动系统健康检查线程
        health_thread = threading.Thread(target=self._monitor_system_health, daemon=True)
        health_thread.start()
        
        logger.info("监控线程已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        logger.info("停止P1优化模块监控...")
        self.monitoring_active = False
    
    def _monitor_performance(self):
        """监控性能指标"""
        while self.monitoring_active:
            try:
                # 模拟性能数据收集
                self._collect_performance_data()
                
                # 检查性能阈值
                self._check_performance_thresholds()
                
                # 每60秒检查一次
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"性能监控异常: {e}")
                time.sleep(60)
    
    def _monitor_quality(self):
        """监控质量指标"""
        while self.monitoring_active:
            try:
                # 模拟质量数据收集
                self._collect_quality_data()
                
                # 检查质量阈值
                self._check_quality_thresholds()
                
                # 每120秒检查一次
                time.sleep(120)
                
            except Exception as e:
                logger.error(f"质量监控异常: {e}")
                time.sleep(120)
    
    def _monitor_user_feedback(self):
        """监控用户反馈"""
        while self.monitoring_active:
            try:
                # 模拟用户反馈收集
                self._collect_user_feedback()
                
                # 分析反馈趋势
                self._analyze_feedback_trends()
                
                # 每300秒检查一次
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"用户反馈监控异常: {e}")
                time.sleep(300)
    
    def _monitor_system_health(self):
        """监控系统健康状态"""
        while self.monitoring_active:
            try:
                # 检查系统健康状态
                self._check_system_health()
                
                # 生成健康报告
                self._generate_health_report()
                
                # 每300秒检查一次
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"系统健康监控异常: {e}")
                time.sleep(300)
    
    def _collect_performance_data(self):
        """收集性能数据"""
        # 模拟性能数据
        import random
        
        response_time = random.uniform(0.5, 2.0)
        success = random.random() > 0.05  # 95%成功率
        
        self.monitoring_data["performance_metrics"]["total_requests"] += 1
        self.monitoring_data["performance_metrics"]["total_response_time"] += response_time
        
        if success:
            self.monitoring_data["performance_metrics"]["successful_requests"] += 1
        else:
            self.monitoring_data["performance_metrics"]["failed_requests"] += 1
        
        # 计算平均响应时间
        total_requests = self.monitoring_data["performance_metrics"]["total_requests"]
        total_time = self.monitoring_data["performance_metrics"]["total_response_time"]
        self.monitoring_data["performance_metrics"]["average_response_time"] = total_time / total_requests
        
        logger.debug(f"性能数据更新: 响应时间={response_time:.2f}s, 成功={success}")
    
    def _collect_quality_data(self):
        """收集质量数据"""
        # 模拟质量数据
        import random
        
        quality_score = random.uniform(0.6, 0.95)
        
        self.monitoring_data["quality_metrics"]["total_assessments"] += 1
        
        # 检查质量阈值
        if quality_score < self.alert_thresholds["min_quality_score"]:
            self.monitoring_data["quality_metrics"]["quality_threshold_violations"] += 1
        
        # 计算平均质量分数
        total_assessments = self.monitoring_data["quality_metrics"]["total_assessments"]
        current_avg = self.monitoring_data["quality_metrics"]["average_quality_score"]
        new_avg = (current_avg * (total_assessments - 1) + quality_score) / total_assessments
        self.monitoring_data["quality_metrics"]["average_quality_score"] = new_avg
        
        logger.debug(f"质量数据更新: 质量分数={quality_score:.2f}, 平均={new_avg:.2f}")
    
    def _collect_user_feedback(self):
        """收集用户反馈"""
        # 模拟用户反馈数据
        import random
        
        feedback_types = ["accuracy", "relevance", "completeness", "clarity", "usefulness"]
        feedback_levels = ["excellent", "good", "needs_improvement", "poor", "critical"]
        
        feedback_type = random.choice(feedback_types)
        feedback_level = random.choice(feedback_levels)
        
        self.monitoring_data["user_feedback"]["total_feedback"] += 1
        
        if feedback_level in ["excellent", "good"]:
            self.monitoring_data["user_feedback"]["positive_feedback"] += 1
        else:
            self.monitoring_data["user_feedback"]["negative_feedback"] += 1
        
        # 生成改进建议
        if feedback_level in ["needs_improvement", "poor", "critical"]:
            suggestion = f"改进{feedback_type}相关功能"
            if suggestion not in self.monitoring_data["user_feedback"]["improvement_suggestions"]:
                self.monitoring_data["user_feedback"]["improvement_suggestions"].append(suggestion)
        
        logger.debug(f"用户反馈更新: 类型={feedback_type}, 级别={feedback_level}")
    
    def _check_performance_thresholds(self):
        """检查性能阈值"""
        metrics = self.monitoring_data["performance_metrics"]
        
        # 检查响应时间
        if metrics["average_response_time"] > self.alert_thresholds["max_response_time"]:
            self._add_alert("性能", f"平均响应时间过高: {metrics['average_response_time']:.2f}s")
        
        # 检查成功率
        if metrics["total_requests"] > 0:
            success_rate = metrics["successful_requests"] / metrics["total_requests"]
            if success_rate < self.alert_thresholds["min_success_rate"]:
                self._add_alert("性能", f"成功率过低: {success_rate:.2%}")
    
    def _check_quality_thresholds(self):
        """检查质量阈值"""
        metrics = self.monitoring_data["quality_metrics"]
        
        # 检查质量分数
        if metrics["average_quality_score"] < self.alert_thresholds["min_quality_score"]:
            self._add_alert("质量", f"平均质量分数过低: {metrics['average_quality_score']:.2f}")
        
        # 检查质量违规次数
        if metrics["quality_threshold_violations"] > 10:
            self._add_alert("质量", f"质量阈值违规次数过多: {metrics['quality_threshold_violations']}")
    
    def _analyze_feedback_trends(self):
        """分析反馈趋势"""
        feedback = self.monitoring_data["user_feedback"]
        
        if feedback["total_feedback"] > 0:
            negative_rate = feedback["negative_feedback"] / feedback["total_feedback"]
            
            if negative_rate > self.alert_thresholds["max_error_rate"]:
                self._add_alert("用户反馈", f"负面反馈率过高: {negative_rate:.2%}")
    
    def _check_system_health(self):
        """检查系统健康状态"""
        self.monitoring_data["system_health"]["last_check"] = datetime.now().isoformat()
        
        # 检查各个模块状态
        alerts_count = len(self.monitoring_data["system_health"]["alerts"])
        
        if alerts_count == 0:
            self.monitoring_data["system_health"]["status"] = "healthy"
        elif alerts_count <= 3:
            self.monitoring_data["system_health"]["status"] = "warning"
        else:
            self.monitoring_data["system_health"]["status"] = "critical"
    
    def _add_alert(self, category: str, message: str):
        """添加告警"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "message": message,
            "severity": "warning"
        }
        
        self.monitoring_data["system_health"]["alerts"].append(alert)
        logger.warning(f"告警 [{category}]: {message}")
    
    def _generate_health_report(self):
        """生成健康报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": self.monitoring_data["system_health"]["status"],
            "performance_summary": {
                "total_requests": self.monitoring_data["performance_metrics"]["total_requests"],
                "success_rate": self._calculate_success_rate(),
                "average_response_time": self.monitoring_data["performance_metrics"]["average_response_time"]
            },
            "quality_summary": {
                "average_quality_score": self.monitoring_data["quality_metrics"]["average_quality_score"],
                "threshold_violations": self.monitoring_data["quality_metrics"]["quality_threshold_violations"]
            },
            "user_feedback_summary": {
                "total_feedback": self.monitoring_data["user_feedback"]["total_feedback"],
                "positive_rate": self._calculate_positive_feedback_rate(),
                "improvement_suggestions": self.monitoring_data["user_feedback"]["improvement_suggestions"]
            },
            "active_alerts": len(self.monitoring_data["system_health"]["alerts"])
        }
        
        # 保存报告
        report_file = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"健康报告已生成: {report_file}")
    
    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        metrics = self.monitoring_data["performance_metrics"]
        if metrics["total_requests"] > 0:
            return metrics["successful_requests"] / metrics["total_requests"]
        return 0.0
    
    def _calculate_positive_feedback_rate(self) -> float:
        """计算正面反馈率"""
        feedback = self.monitoring_data["user_feedback"]
        if feedback["total_feedback"] > 0:
            return feedback["positive_feedback"] / feedback["total_feedback"]
        return 0.0
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """获取监控摘要"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system_status": self.monitoring_data["system_health"]["status"],
            "performance": {
                "total_requests": self.monitoring_data["performance_metrics"]["total_requests"],
                "success_rate": f"{self._calculate_success_rate():.2%}",
                "avg_response_time": f"{self.monitoring_data['performance_metrics']['average_response_time']:.2f}s"
            },
            "quality": {
                "avg_quality_score": f"{self.monitoring_data['quality_metrics']['average_quality_score']:.2f}",
                "threshold_violations": self.monitoring_data["quality_metrics"]["quality_threshold_violations"]
            },
            "user_feedback": {
                "total_feedback": self.monitoring_data["user_feedback"]["total_feedback"],
                "positive_rate": f"{self._calculate_positive_feedback_rate():.2%}",
                "suggestions_count": len(self.monitoring_data["user_feedback"]["improvement_suggestions"])
            },
            "alerts": len(self.monitoring_data["system_health"]["alerts"])
        }
    
    def save_monitoring_data(self):
        """保存监控数据"""
        data_file = f"monitoring_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(self.monitoring_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"监控数据已保存: {data_file}")


def main():
    """主函数"""
    monitor = P1OptimizationMonitor()
    
    try:
        print("🚀 启动P1优化模块持续监控...")
        monitor.start_monitoring()
        
        # 主循环
        while True:
            try:
                # 每5分钟显示一次摘要
                time.sleep(300)
                summary = monitor.get_monitoring_summary()
                
                print("\n" + "="*60)
                print("📊 P1优化模块监控摘要")
                print("="*60)
                print(f"系统状态: {summary['system_status']}")
                print(f"总请求数: {summary['performance']['total_requests']}")
                print(f"成功率: {summary['performance']['success_rate']}")
                print(f"平均响应时间: {summary['performance']['avg_response_time']}")
                print(f"平均质量分数: {summary['quality']['avg_quality_score']}")
                print(f"用户反馈数: {summary['user_feedback']['total_feedback']}")
                print(f"正面反馈率: {summary['user_feedback']['positive_rate']}")
                print(f"活跃告警: {summary['alerts']}")
                print("="*60)
                
                # 保存监控数据
                monitor.save_monitoring_data()
                
            except KeyboardInterrupt:
                print("\n⚠️ 监控被用户中断")
                break
            except Exception as e:
                logger.error(f"监控主循环异常: {e}")
                time.sleep(60)
    
    finally:
        monitor.stop_monitoring()
        print("\n🛑 监控已停止")


if __name__ == "__main__":
    main() 