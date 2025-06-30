#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iflytek Spark Optimizer - 核心模块

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
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import defaultdict, deque

# 修复导入路径
try:
    from ...llm_clients.base_llm import BaseLLMClient
except ImportError:
    try:
        from src.llm_clients.base_llm import BaseLLMClient
    except ImportError:
        # 如果都失败，创建一个基础类
        class BaseLLMClient:
            def generate_text(self, prompt: str) -> str:
                return "模拟响应"

try:
    from ...knowledge_base.scenario_definitions import SCENARIO_DEFINITIONS
except ImportError:
    SCENARIO_DEFINITIONS = {}

try:
    from ...monitoring.performance_monitor import PerformanceMonitor
except ImportError:
    class PerformanceMonitor:
        """性能监控器占位类"""
        pass


class SparkModelVersion(Enum):
    """讯飞星火模型版本枚举"""
    SPARK_V1_5 = "spark-v1.5"
    SPARK_V2_0 = "spark-v2.0"
    SPARK_V3_0 = "spark-v3.0"


class BusinessScenario(Enum):
    """业务场景枚举"""
    TECHNICAL_REPORT = "technical_report"
    BUSINESS_PROPOSAL = "business_proposal"
    CONTRACT_REVIEW = "contract_review"
    ACADEMIC_PAPER = "academic_paper"
    GOVERNMENT_DOCUMENT = "government_document"
    MEETING_MINUTES = "meeting_minutes"
    MARKET_ANALYSIS = "market_analysis"
    GENERAL_DOCUMENT = "general_document"


@dataclass
class PromptTemplate:
    """Prompt模板数据结构"""
    scenario: BusinessScenario
    template: str
    variables: List[str]
    expected_output_format: str
    quality_standards: List[str]
    examples: List[Dict[str, str]]
    optimization_tips: List[str]


@dataclass
class PerformanceStats:
    """性能统计数据结构"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    total_response_time: float = 0.0
    cache_hit_rate: float = 0.0
    last_request_time: float = 0.0
    error_types: Dict[str, int] = field(default_factory=lambda: defaultdict(int))


class SparkModelOptimizer:
    """
    讯飞星火模型优化器
    
    专门针对讯飞星火模型进行深度优化，提供业务场景特定的prompt模板、
    智能缓存、性能监控和错误处理机制。
    
    Attributes:
        llm_client: LLM客户端实例
        cache: 智能缓存字典
        performance_stats: 性能统计
        prompt_templates: 业务场景prompt模板
        monitor: 性能监控器
        lock: 线程锁
    """
    
    def __init__(self, llm_client: BaseLLMClient):
        """
        初始化讯飞星火模型优化器
        
        Args:
            llm_client: LLM客户端实例
            
        Raises:
            ValueError: 当llm_client为None时
        """
        if llm_client is None:
            raise ValueError("LLM客户端不能为空")
            
        self.llm_client = llm_client
        self.cache = {}
        self.performance_stats = PerformanceStats()
        self.prompt_templates = self._initialize_prompt_templates()
        self.monitor = PerformanceMonitor()
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # 初始化默认配置
        self.max_cache_size = 1000
        self.cache_ttl = 3600  # 1小时
        self.max_retries = 3
        self.retry_delay = 1.0
        
    def _initialize_prompt_templates(self) -> Dict[BusinessScenario, PromptTemplate]:
        """
        初始化业务场景特定的prompt模板
        
        Returns:
            包含所有业务场景prompt模板的字典
        """
        templates = {}
        
        # 技术报告场景模板
        templates[BusinessScenario.TECHNICAL_REPORT] = PromptTemplate(
            scenario=BusinessScenario.TECHNICAL_REPORT,
            template="""你是一位资深技术专家，请对以下技术报告进行专业分析：

报告内容：{content}

请从以下角度进行分析：
1. 技术可行性评估
2. 风险评估和缓解措施
3. 资源需求分析
4. 时间进度规划
5. 质量保证措施

请提供结构化的分析报告，包含具体的技术指标和可操作的建议。""",
            variables=["content"],
            expected_output_format="JSON格式，包含analysis_sections、technical_metrics、recommendations等字段",
            quality_standards=[
                "技术分析准确性和专业性",
                "风险评估的全面性",
                "建议的可操作性",
                "输出格式的规范性"
            ],
            examples=[
                {
                    "input": "关于新系统架构的技术报告",
                    "output": "包含技术可行性、风险评估、资源需求等结构化分析"
                }
            ],
            optimization_tips=[
                "明确技术指标和评估标准",
                "提供量化的风险评估",
                "给出具体的实施建议"
            ]
        )
        
        # 商业提案场景模板
        templates[BusinessScenario.BUSINESS_PROPOSAL] = PromptTemplate(
            scenario=BusinessScenario.BUSINESS_PROPOSAL,
            template="""你是一位经验丰富的商业顾问，请对以下商业提案进行专业评估：

提案内容：{content}

请从以下维度进行评估：
1. 市场机会分析
2. 竞争优势评估
3. 商业模式可行性
4. 财务预测合理性
5. 风险因素识别

请提供详细的商业分析报告，包含市场数据支持和投资建议。""",
            variables=["content"],
            expected_output_format="JSON格式，包含market_analysis、competitive_advantage、financial_projections等字段",
            quality_standards=[
                "市场分析的准确性",
                "竞争优势的识别",
                "财务预测的合理性",
                "风险评估的全面性"
            ],
            examples=[
                {
                    "input": "新产品市场推广提案",
                    "output": "包含市场分析、竞争优势、财务预测等商业评估"
                }
            ],
            optimization_tips=[
                "提供具体的市场数据支持",
                "分析竞争对手情况",
                "给出量化的财务预测"
            ]
        )
        
        # 合同审阅场景模板
        templates[BusinessScenario.CONTRACT_REVIEW] = PromptTemplate(
            scenario=BusinessScenario.CONTRACT_REVIEW,
            template="""你是一位专业的法律顾问，请对以下合同进行法律风险审查：

合同内容：{content}

请重点关注以下方面：
1. 合同条款的合法性和有效性
2. 权利义务的平衡性
3. 违约责任和争议解决机制
4. 知识产权和保密条款
5. 法律风险点识别

请提供详细的法律审查报告，包含风险等级评估和修改建议。""",
            variables=["content"],
            expected_output_format="JSON格式，包含legal_analysis、risk_assessment、modification_suggestions等字段",
            quality_standards=[
                "法律分析的准确性",
                "风险识别的全面性",
                "建议的实用性",
                "合规性检查的完整性"
            ],
            examples=[
                {
                    "input": "技术合作协议",
                    "output": "包含法律风险分析、条款评估、修改建议等法律审查"
                }
            ],
            optimization_tips=[
                "引用相关法律法规",
                "识别潜在法律风险",
                "提供具体的修改建议"
            ]
        )
        
        # 学术论文场景模板
        templates[BusinessScenario.ACADEMIC_PAPER] = PromptTemplate(
            scenario=BusinessScenario.ACADEMIC_PAPER,
            template="""你是一位学术专家，请对以下学术论文进行专业审阅：

论文内容：{content}

请从以下角度进行审阅：
1. 研究方法的科学性
2. 数据分析的准确性
3. 结论的合理性
4. 文献引用的规范性
5. 学术贡献和创新性

请提供详细的学术审阅报告，包含质量评估和改进建议。""",
            variables=["content"],
            expected_output_format="JSON格式，包含methodology_review、data_analysis、conclusions_assessment等字段",
            quality_standards=[
                "学术标准的符合性",
                "研究方法的科学性",
                "数据分析的准确性",
                "结论的合理性"
            ],
            examples=[
                {
                    "input": "机器学习算法研究论文",
                    "output": "包含方法评估、数据分析、结论审阅等学术审查"
                }
            ],
            optimization_tips=[
                "评估研究方法的科学性",
                "检查数据分析的准确性",
                "验证结论的合理性"
            ]
        )
        
        # 政府文档场景模板
        templates[BusinessScenario.GOVERNMENT_DOCUMENT] = PromptTemplate(
            scenario=BusinessScenario.GOVERNMENT_DOCUMENT,
            template="""你是一位政府文档专家，请对以下政府文档进行规范性审查：

文档内容：{content}

请重点关注以下方面：
1. 政策法规的符合性
2. 文档格式的规范性
3. 内容表述的准确性
4. 程序流程的完整性
5. 审批权限的合理性

请提供详细的规范性审查报告，包含合规性评估和修改建议。""",
            variables=["content"],
            expected_output_format="JSON格式，包含compliance_check、format_review、content_accuracy等字段",
            quality_standards=[
                "政策法规的符合性",
                "文档格式的规范性",
                "内容表述的准确性",
                "程序流程的完整性"
            ],
            examples=[
                {
                    "input": "政府项目申请报告",
                    "output": "包含合规性检查、格式审查、内容评估等规范性审查"
                }
            ],
            optimization_tips=[
                "检查政策法规符合性",
                "验证文档格式规范性",
                "确保内容表述准确性"
            ]
        )
        
        return templates
    
    def get_optimized_prompt(self, scenario: BusinessScenario, **kwargs) -> str:
        """
        获取优化后的prompt
        
        Args:
            scenario: 业务场景
            **kwargs: prompt变量参数
            
        Returns:
            优化后的prompt字符串
            
        Raises:
            ValueError: 当场景不存在或缺少必要参数时
        """
        if scenario not in self.prompt_templates:
            raise ValueError(f"不支持的业务场景: {scenario}")
            
        template = self.prompt_templates[scenario]
        
        # 检查必要参数
        for var in template.variables:
            if var not in kwargs:
                raise ValueError(f"缺少必要参数: {var}")
        
        # 生成prompt
        prompt = template.template
        for var, value in kwargs.items():
            prompt = prompt.replace(f"{{{var}}}", str(value))
        
        # 添加优化提示
        if template.optimization_tips:
            prompt += "\n\n优化提示：\n"
            for tip in template.optimization_tips:
                prompt += f"- {tip}\n"
        
        return prompt
    
    def analyze_with_cache(self, scenario: BusinessScenario, content: str, 
                          use_cache: bool = True) -> Dict[str, Any]:
        """
        使用缓存进行内容分析
        
        Args:
            scenario: 业务场景
            content: 分析内容
            use_cache: 是否使用缓存
            
        Returns:
            分析结果字典
        """
        # 生成缓存键
        cache_key = self._generate_cache_key(scenario, content)
        
        # 检查缓存
        if use_cache and cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if time.time() - cached_result['timestamp'] < self.cache_ttl:
                self.performance_stats.cache_hit_rate = (
                    self.performance_stats.cache_hit_rate * 0.9 + 0.1
                )
                return cached_result['result']
        
        # 执行分析
        start_time = time.time()
        try:
            prompt = self.get_optimized_prompt(scenario, content=content)
            result = self._call_llm_with_retry(prompt)
            
            # 更新性能统计
            response_time = time.time() - start_time
            self._update_performance_stats(True, response_time)
            
            # 缓存结果
            if use_cache:
                self._cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_performance_stats(False, response_time, str(e))
            raise
    
    def _generate_cache_key(self, scenario: BusinessScenario, content: str) -> str:
        """
        生成缓存键
        
        Args:
            scenario: 业务场景
            content: 内容
            
        Returns:
            缓存键字符串
        """
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{scenario.value}_{content_hash}"
    
    def _call_llm_with_retry(self, prompt: str) -> Dict[str, Any]:
        """
        带重试机制的LLM调用
        
        Args:
            prompt: 输入prompt
            
        Returns:
            LLM响应结果
            
        Raises:
            Exception: 当所有重试都失败时
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.llm_client.generate_text(prompt)
                return self._parse_response(response)
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"LLM调用失败，尝试 {attempt + 1}/{self.max_retries}: {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
        
        if last_error is not None:
            raise last_error
        else:
            raise Exception("LLM调用失败，未知错误")
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM响应
        
        Args:
            response: LLM原始响应
            
        Returns:
            解析后的结果字典
        """
        try:
            # 尝试解析JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # 如果不是JSON格式，返回文本格式
            return {
                "content": response,
                "format": "text",
                "parsed_at": time.time()
            }
    
    def _update_performance_stats(self, success: bool, response_time: float, 
                                error_type: Optional[str] = None):
        """
        更新性能统计
        
        Args:
            success: 是否成功
            response_time: 响应时间
            error_type: 错误类型
        """
        with self.lock:
            self.performance_stats.total_requests += 1
            self.performance_stats.total_response_time += response_time
            
            if success:
                self.performance_stats.successful_requests += 1
            else:
                self.performance_stats.failed_requests += 1
                if error_type:
                    self.performance_stats.error_types[error_type] += 1
            
            # 计算平均响应时间
            self.performance_stats.average_response_time = (
                self.performance_stats.total_response_time / 
                self.performance_stats.total_requests
            )
            
            self.performance_stats.last_request_time = time.time()
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """
        缓存结果
        
        Args:
            cache_key: 缓存键
            result: 结果数据
        """
        # 检查缓存大小
        if len(self.cache) >= self.max_cache_size:
            # 删除最旧的缓存项
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        获取性能报告
        
        Returns:
            性能报告字典
        """
        with self.lock:
            stats = self.performance_stats
            
            return {
                "total_requests": stats.total_requests,
                "successful_requests": stats.successful_requests,
                "failed_requests": stats.failed_requests,
                "success_rate": (stats.successful_requests / stats.total_requests * 100 
                               if stats.total_requests > 0 else 0),
                "average_response_time": stats.average_response_time,
                "cache_hit_rate": stats.cache_hit_rate,
                "last_request_time": stats.last_request_time,
                "error_distribution": dict(stats.error_types),
                "cache_size": len(self.cache),
                "supported_scenarios": [s.value for s in self.prompt_templates.keys()]
            }
    
    def clear_cache(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def get_supported_scenarios(self) -> List[str]:
        """
        获取支持的业务场景列表
        
        Returns:
            支持的场景列表
        """
        return [scenario.value for scenario in self.prompt_templates.keys()]
    
    def get_template_info(self, scenario: BusinessScenario) -> Dict[str, Any]:
        """
        获取模板信息
        
        Args:
            scenario: 业务场景
            
        Returns:
            模板信息字典
        """
        if scenario not in self.prompt_templates:
            raise ValueError(f"不支持的业务场景: {scenario}")
        
        template = self.prompt_templates[scenario]
        return asdict(template) 