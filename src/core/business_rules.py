#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务规则管理模块
统一管理各个功能的业务规则和配置
"""

from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime


class BusinessRuleManager:
    """业务规则管理器"""
    
    def __init__(self):
        self.rules = self._load_default_rules()
    
    def _load_default_rules(self) -> Dict[str, Dict[str, Any]]:
        """加载默认业务规则"""
        return {
            'style_alignment': {
                'export_rules': {
                    'content_processing': '原文+已接受的风格变更（按diff顺序应用）',
                    'format_preservation': '保持原文格式（字体、字号、行距、页边距）',
                    'structure_preservation': '保留原文标题、章节、段落等结构',
                    'naming_convention': '原文件名_模板名_时间戳.docx',
                    'highlighting': '所有风格变更高亮显示（黄色高亮+批注）',
                    'auto_generation': '自动生成封面、目录、风格调整报告'
                },
                'template_rules': {
                    'auto_save': True,
                    'fallback_strategy': '当模板不存在时自动保存分析结果',
                    'template_id_format': 'uuid4'
                },
                'session_rules': {
                    'cleanup_after_export': False,
                    'max_session_age': '7d',
                    'auto_backup': True
                }
            },
            'document_fill': {
                'export_rules': {
                    'content_processing': '模板+填充数据（智能匹配）',
                    'format_preservation': '保持模板格式',
                    'data_validation': '验证数据完整性和格式',
                    'naming_convention': '原模板名_数据源名_时间戳.docx',
                    'error_handling': '未匹配字段标记为待填写'
                },
                'matching_rules': {
                    'fuzzy_match': True,
                    'confidence_threshold': 0.8,
                    'field_mapping': '智能字段映射'
                }
            },
            'format_alignment': {
                'export_rules': {
                    'content_processing': '原文+格式调整（保持内容不变）',
                    'format_priority': '参考文档格式优先',
                    'conflict_resolution': '用户确认冲突处理',
                    'naming_convention': '原文件名_格式对齐_时间戳.docx',
                    'change_tracking': '格式变更高亮显示'
                },
                'alignment_rules': {
                    'preserve_content': True,
                    'style_inheritance': '继承参考文档样式',
                    'section_handling': '按章节分别处理'
                }
            },
            'document_review': {
                'export_rules': {
                    'content_processing': '原文+评审建议（可选择性应用）',
                    'review_tracking': '评审意见和修改建议',
                    'naming_convention': '原文件名_评审报告_时间戳.docx',
                    'approval_status': '包含审批状态和建议'
                },
                'review_rules': {
                    'multi_role_review': True,
                    'priority_ranking': '按重要性排序建议',
                    'auto_approval_threshold': 0.9
                }
            }
        }
    
    def get_export_rules(self, feature_name: str) -> Dict[str, Any]:
        """
        获取指定功能的导出规则
        
        Args:
            feature_name: 功能名称
            
        Returns:
            Dict: 导出规则
        """
        return self.rules.get(feature_name, {}).get('export_rules', {})
    
    def get_template_rules(self, feature_name: str) -> Dict[str, Any]:
        """
        获取指定功能的模板规则
        
        Args:
            feature_name: 功能名称
            
        Returns:
            Dict: 模板规则
        """
        return self.rules.get(feature_name, {}).get('template_rules', {})
    
    def get_session_rules(self, feature_name: str) -> Dict[str, Any]:
        """
        获取指定功能的会话规则
        
        Args:
            feature_name: 功能名称
            
        Returns:
            Dict: 会话规则
        """
        return self.rules.get(feature_name, {}).get('session_rules', {})
    
    def generate_filename(self, feature_name: str, original_name: str, 
                         template_name: Optional[str] = None, data_source: Optional[str] = None) -> str:
        """
        根据业务规则生成文件名
        
        Args:
            feature_name: 功能名称
            original_name: 原文件名
            template_name: 模板名称
            data_source: 数据源名称
            
        Returns:
            str: 生成的文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 移除原文件扩展名
        base_name = os.path.splitext(original_name)[0]
        
        # 根据功能类型生成文件名
        if feature_name == 'style_alignment':
            template_suffix = template_name or 'template'
            return f"{base_name}_{template_suffix}_{timestamp}.docx"
        elif feature_name == 'document_fill':
            data_suffix = data_source or 'data'
            return f"{base_name}_{data_suffix}_{timestamp}.docx"
        elif feature_name == 'format_alignment':
            return f"{base_name}_格式对齐_{timestamp}.docx"
        elif feature_name == 'document_review':
            return f"{base_name}_评审报告_{timestamp}.docx"
        else:
            return f"{base_name}_{feature_name}_{timestamp}.docx"
    
    def validate_export_content(self, feature_name: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证导出内容是否符合业务规则
        
        Args:
            feature_name: 功能名称
            content: 导出内容
            
        Returns:
            Dict: 验证结果 {'valid': bool, 'issues': List[str]}
        """
        rules = self.get_export_rules(feature_name)
        issues = []
        
        # 检查必需字段
        required_fields = ['original_content', 'processed_content']
        for field in required_fields:
            if field not in content:
                issues.append(f"缺少必需字段: {field}")
        
        # 检查内容处理规则
        if feature_name == 'style_alignment':
            if 'style_changes' not in content:
                issues.append("缺少风格变更信息")
            if 'template_id' not in content:
                issues.append("缺少模板ID")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'rules_applied': list(rules.keys())
        }
    
    def get_processing_pipeline(self, feature_name: str) -> List[str]:
        """
        获取指定功能的处理流程
        
        Args:
            feature_name: 功能名称
            
        Returns:
            List[str]: 处理步骤列表
        """
        pipelines = {
            'style_alignment': [
                'analyze_writing_style',
                'generate_style_preview', 
                'apply_style_changes',
                'export_styled_document'
            ],
            'document_fill': [
                'analyze_template_structure',
                'match_data_to_template',
                'generate_fill_preview',
                'apply_fill_changes',
                'export_filled_document'
            ],
            'format_alignment': [
                'analyze_format_differences',
                'generate_alignment_preview',
                'apply_format_changes',
                'export_aligned_document'
            ],
            'document_review': [
                'analyze_document_quality',
                'generate_review_report',
                'apply_review_suggestions',
                'export_reviewed_document'
            ]
        }
        
        return pipelines.get(feature_name, [])
    
    def save_rules_to_file(self, file_path: str = "business_rules.json"):
        """
        保存业务规则到文件
        
        Args:
            file_path: 文件路径
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.rules, f, ensure_ascii=False, indent=2)
    
    def load_rules_from_file(self, file_path: str = "business_rules.json"):
        """
        从文件加载业务规则
        
        Args:
            file_path: 文件路径
        """
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)


# 全局实例
business_rule_manager = BusinessRuleManager()


def get_export_rules(feature_name: str) -> Dict[str, Any]:
    """便捷函数：获取导出规则"""
    return business_rule_manager.get_export_rules(feature_name)


def generate_filename(feature_name: str, original_name: str, 
                     template_name: Optional[str] = None, data_source: Optional[str] = None) -> str:
    """便捷函数：生成文件名"""
    return business_rule_manager.generate_filename(feature_name, original_name, 
                                                 template_name, data_source)


def validate_export_content(feature_name: str, content: Dict[str, Any]) -> Dict[str, Any]:
    """便捷函数：验证导出内容"""
    return business_rule_manager.validate_export_content(feature_name, content) 