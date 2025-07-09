#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成智能填报管理器 - 修复版

Author: AI Assistant (Claude)
Created: 2025-07-08
Last Modified: 2025-07-08
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.1 - 修复版
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

# 导入现有核心组件 - 修复版
CORE_COMPONENTS_AVAILABLE = False
available_components = {}

# 尝试导入各个组件，记录成功的组件
component_imports = [
    ('enhanced_document_filler', 'EnhancedDocumentFiller'),
    ('enhanced_table_processor', 'EnhancedTableProcessor'),
    ('enhanced_document_fill_coordinator', 'EnhancedDocumentFillCoordinator'),
    ('document_fill_coordinator', 'DocumentFillCoordinator'),
    ('smart_prompt_generator', 'SmartPromptGenerator'),
    ('scenario_template_manager', 'ScenarioTemplateManager')
]

for module_name, class_name in component_imports:
    try:
        module = __import__(f'.{module_name}', package='core.tools', fromlist=[class_name])
        component_class = getattr(module, class_name)
        available_components[module_name] = component_class
        print(f"✅ {class_name} 导入成功")
    except ImportError as e:
        print(f"⚠️ {class_name} 导入失败: {e}")
    except Exception as e:
        print(f"⚠️ {class_name} 导入异常: {e}")

# 检查是否至少有一个组件可用
if available_components:
    CORE_COMPONENTS_AVAILABLE = True
    print(f"✅ 成功导入 {len(available_components)} 个核心组件")
else:
    print("❌ 所有核心组件都不可用")

class IntegratedSmartFillManager:
    """集成智能填报管理器 - 修复版"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化集成智能填报管理器
        
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
        
        # 初始化现有组件（使用星火X1作为LLM引擎）
        self.components = {}
        if CORE_COMPONENTS_AVAILABLE and self.spark_x1_client:
            llm_client = self.spark_x1_client  # 使用星火X1作为LLM引擎
            
            # 尝试初始化各个组件
            for component_name, component_class in available_components.items():
                try:
                    if component_name in ['enhanced_document_filler', 'enhanced_table_processor', 
                                        'enhanced_document_fill_coordinator', 'document_fill_coordinator']:
                        # 需要LLM客户端的组件
                        self.components[component_name] = component_class(llm_client)
                    else:
                        # 不需要LLM客户端的组件
                        self.components[component_name] = component_class()
                    self.logger.info(f"✅ {component_name} 组件初始化成功")
                except Exception as e:
                    self.logger.error(f"❌ {component_name} 组件初始化失败: {e}")
        
        # 支持的填报类型（现有+新增）
        self.supported_types = {
            # 现有类型（通过现有组件处理）
            'patent': {'name': '专利申请', 'handler': 'existing_components'},
            'project': {'name': '项目申请', 'handler': 'existing_components'},
            'contract': {'name': '合同文档', 'handler': 'existing_components'},
            'report': {'name': '技术报告', 'handler': 'existing_components'},
            # 新增类型（直接使用星火X1）
            'summary': {'name': '年度总结', 'handler': 'spark_x1_direct'},
            'resume': {'name': '个人简历', 'handler': 'spark_x1_direct'},
            'government': {'name': '公文文档', 'handler': 'spark_x1_direct'},
            'academic': {'name': '学术论文', 'handler': 'spark_x1_direct'}
        }
        
        self.logger.info(f"集成智能填报管理器初始化完成，支持类型: {list(self.supported_types.keys())}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status = {
            'spark_x1_available': self.spark_x1_client is not None,
            'core_components_available': CORE_COMPONENTS_AVAILABLE,
            'supported_types': list(self.supported_types.keys()),
            'available_components': list(available_components.keys()),
            'initialized_components': list(self.components.keys()),
            'components_status': {},
            'integration_mode': 'progressive_deep_integration',
            'version': '1.1.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # 检查组件状态
        for name, component in self.components.items():
            status['components_status'][name] = component is not None
        
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
        智能填充文档 - 统一入口
        
        Args:
            document_type: 文档类型
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
                    'error': f'不支持的文档类型: {document_type}，支持的类型: {list(self.supported_types.keys())}'
                }
            
            type_info = self.supported_types[document_type]
            handler = type_info['handler']
            
            # 根据处理器类型选择处理方式
            if handler == 'spark_x1_direct':
                return self._handle_spark_x1_direct(document_type, content, user_data)
            elif handler == 'existing_components':
                return self._handle_existing_components(document_type, content, user_data)
            else:
                return {
                    'success': False,
                    'error': f'未知的处理器类型: {handler}'
                }
                
        except Exception as e:
            self.logger.error(f"智能填充文档失败: {e}")
            return {
                'success': False,
                'error': f'智能填充失败: {str(e)}'
            }
    
    def _handle_spark_x1_direct(self, document_type: str, content: str, 
                               user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用星火X1直接处理新增文档类型"""
        if not self.spark_x1_client:
            return {
                'success': False,
                'error': '星火X1客户端不可用，无法处理此类型文档'
            }
        
        try:
            if document_type == 'summary':
                result = self.spark_x1_client.generate_summary(content)
            elif document_type == 'resume':
                result = self.spark_x1_client.generate_resume(content)
            else:
                # 对于其他新增类型，使用通用生成方法
                prompt = self._build_generic_prompt(document_type, content, user_data)
                generated_content = self.spark_x1_client.generate(prompt)
                result = {
                    'success': True,
                    'content': generated_content,
                    'type': document_type
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
    
    def _handle_existing_components(self, document_type: str, content: str, 
                                  user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用现有组件处理传统文档类型（现在增强了星火X1）"""
        if not CORE_COMPONENTS_AVAILABLE:
            return {
                'success': False,
                'error': '核心组件不可用，无法处理此类型文档'
            }
        
        try:
            # 使用增强的文档填充器（现在使用星火X1作为LLM引擎）
            document_filler = self.components.get('enhanced_document_filler')
            if not document_filler:
                return {
                    'success': False,
                    'error': '文档填充器不可用'
                }
            
            # 构建分析结果（模拟现有流程）
            analysis_result = {
                'document_type': document_type,
                'original_content': content,
                'fields': [],  # 实际应该从模板分析中获取
                'total_objective': f'智能填充{self.supported_types[document_type]["name"]}',
                'core_theme': content[:100] + '...' if len(content) > 100 else content
            }
            
            # 调用现有组件进行填充（现在使用星火X1增强）
            fill_result = document_filler.intelligent_fill_document(
                analysis_result, user_data or {}
            )
            
            if 'error' not in fill_result:
                return {
                    'success': True,
                    'type': document_type,
                    'handler': 'existing_components_enhanced',
                    'data': fill_result,
                    'message': f'{self.supported_types[document_type]["name"]}填充成功（星火X1增强）'
                }
            else:
                return {
                    'success': False,
                    'error': fill_result['error']
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'文档填充失败: {str(e)}'
            }
    
    def _build_generic_prompt(self, document_type: str, content: str, 
                            user_data: Dict[str, Any] = None) -> str:
        """构建通用提示词"""
        type_name = self.supported_types[document_type]['name']
        
        prompt = f"""
请根据以下信息生成一份专业的{type_name}：

输入内容：
{content}

要求：
1. 内容专业、准确
2. 格式规范、清晰
3. 语言流畅、得体
4. 符合{type_name}的标准格式

请生成完整的{type_name}内容。
"""
        
        if user_data:
            prompt += f"\n\n补充信息：\n{json.dumps(user_data, ensure_ascii=False, indent=2)}"
        
        return prompt
    
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
