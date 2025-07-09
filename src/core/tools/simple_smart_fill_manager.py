#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化智能填报管理器 - 专注于星火X1功能

Author: AI Assistant (Claude)
Created: 2025-07-08
Last Modified: 2025-07-08
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0 - 简化版
License: MIT
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# 导入LLM客户端
try:
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(os.path.dirname(current_dir))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    from llm_clients.spark_x1_client import SparkX1Client
    from llm_clients.base_llm import BaseLLMClient
    SPARK_X1_AVAILABLE = True
except ImportError as e:
    print(f"警告: 星火X1客户端导入失败: {e}")
    SPARK_X1_AVAILABLE = False

class SimpleSmartFillManager:
    """简化智能填报管理器 - 专注于星火X1功能"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化简化智能填报管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化星火X1客户端
        self.spark_x1_client = None
        if SPARK_X1_AVAILABLE:
            api_password = self.config.get('spark_x1_api_password') or os.getenv('SPARK_X1_API_PASSWORD')
            if api_password:
                try:
                    self.spark_x1_client = SparkX1Client(api_password=api_password)
                    self.logger.info("✅ 星火X1客户端初始化成功")
                except Exception as e:
                    self.logger.error(f"❌ 星火X1客户端初始化失败: {e}")
        
        # 支持的填报类型（仅保留年度总结和简历生成）
        self.supported_types = {
            'summary': {'name': '年度总结', 'handler': 'spark_x1_direct'},
            'resume': {'name': '个人简历', 'handler': 'spark_x1_direct'}
        }
        
        self.logger.info(f"简化智能填报管理器初始化完成，支持类型: {list(self.supported_types.keys())}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status = {
            'spark_x1_available': self.spark_x1_client is not None,
            'core_components_available': True,  # 简化版认为组件可用
            'supported_types': list(self.supported_types.keys()),
            'available_components': ['spark_x1_client'],
            'initialized_components': ['spark_x1_client'] if self.spark_x1_client else [],
            'components_status': {
                'spark_x1_client': self.spark_x1_client is not None
            },
            'integration_mode': 'simplified_spark_x1_only',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # 测试星火X1连接
        if self.spark_x1_client:
            try:
                api_status = self.spark_x1_client.is_available()
                status['spark_x1_connection'] = 'connected' if api_status else 'disconnected'
            except Exception as e:
                status['spark_x1_connection'] = f'error: {str(e)}'
        
        return status
    
    def intelligent_fill_document(self, document_type: str, content: str,
                                user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        智能填充文档 - 仅支持年度总结和简历生成

        Args:
            document_type: 文档类型 ('summary' 或 'resume')
            content: 文档内容
            user_data: 用户数据

        Returns:
            填充结果
        """
        try:
            self.logger.info(f"开始智能填充文档，类型: {document_type}")

            # 验证文档类型
            if document_type not in self.supported_types:
                return {
                    'success': False,
                    'error': f'不支持的文档类型: {document_type}，仅支持: {list(self.supported_types.keys())}'
                }

            # 直接使用星火X1处理
            return self._handle_spark_x1_direct(document_type, content, user_data)

        except Exception as e:
            self.logger.error(f"智能填充文档失败: {e}")
            return {
                'success': False,
                'error': f'智能填充失败: {str(e)}'
            }
    
    def _handle_spark_x1_direct(self, document_type: str, content: str,
                               user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用星火X1直接处理年度总结和简历生成"""
        if not self.spark_x1_client:
            return {
                'success': False,
                'error': '星火X1客户端不可用，无法处理此类型文档'
            }

        try:
            # 只处理年度总结和简历生成
            if document_type == 'summary':
                result = self.spark_x1_client.generate_summary(content)
            elif document_type == 'resume':
                result = self.spark_x1_client.generate_resume(content)
            else:
                return {
                    'success': False,
                    'error': f'不支持的文档类型: {document_type}，仅支持年度总结和简历生成'
                }

            if result.get('success', False):
                return {
                    'success': True,
                    'type': document_type,
                    'handler': 'spark_x1_direct',
                    'content': result.get('content'),
                    'data': result.get('data'),
                    'file_path': result.get('file_path'),
                    'filename': result.get('filename'),
                    'usage': result.get('usage', {}),
                    'message': f'{self.supported_types[document_type]["name"]}生成成功'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', '生成失败')
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'{self.supported_types[document_type]["name"]}生成失败: {str(e)}'
            }
    

    
    def analyze_writing_style(self, content: str, document_type: str = None) -> Dict[str, Any]:
        """分析文档写作风格 - 使用星火X1增强"""
        try:
            if not self.spark_x1_client:
                return {
                    'success': False,
                    'error': '星火X1客户端不可用'
                }
            
            # 构建分析提示词
            prompt = f"""
请分析以下文档的写作风格特征：

文档类型：{document_type or '未指定'}
文档内容：
{content}

请从以下维度分析：
1. 语言风格（正式/非正式、学术/商务/日常）
2. 句式特点（长句/短句、复合句比例）
3. 词汇特征（专业术语、常用词汇）
4. 语气特点（客观/主观、肯定/谦逊）
5. 结构特征（逻辑性、条理性）

请以JSON格式返回分析结果。
"""
            
            response = self.spark_x1_client.generate(prompt)
            
            return {
                'success': True,
                'analysis': response,
                'document_type': document_type,
                'analysis_method': 'spark_x1_enhanced',
                'message': '写作风格分析完成'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'写作风格分析失败: {str(e)}'
            }
    
    def get_supported_types(self) -> Dict[str, str]:
        """获取支持的文档类型"""
        return {k: v['name'] for k, v in self.supported_types.items()}
