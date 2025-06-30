#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template Schema - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

class TemplateSchema:
    """
    模板Schema管理器
    提供模板数据的验证、标准化和转换功能
    """
    
    # 格式模板Schema
    FORMAT_TEMPLATE_SCHEMA = {
        "type": "object",
        "required": ["template_id", "document_name", "structure_analysis", "format_rules", "format_prompt"],
        "properties": {
            "template_id": {
                "type": "string",
                "description": "模板唯一标识符",
                "pattern": "^[a-f0-9]{32}$"
            },
            "document_name": {
                "type": "string",
                "description": "文档名称",
                "minLength": 1,
                "maxLength": 200
            },
            "structure_analysis": {
                "type": "object",
                "description": "文档结构分析结果",
                "properties": {
                    "total_lines": {"type": "integer", "minimum": 0},
                    "headings": {"type": "array"},
                    "paragraphs": {"type": "array"},
                    "lists": {"type": "array"},
                    "special_elements": {"type": "array"},
                    "estimated_format": {"type": "object"},
                    "analysis_confidence": {"type": "number", "minimum": 0, "maximum": 1}
                }
            },
            "format_rules": {
                "type": "object",
                "description": "格式规则定义",
                "properties": {
                    "heading_formats": {"type": "object"},
                    "paragraph_formats": {"type": "object"},
                    "list_formats": {"type": "object"},
                    "font_settings": {"type": "object"},
                    "spacing_settings": {"type": "object"}
                }
            },
            "format_prompt": {
                "type": "string",
                "description": "格式对齐提示词",
                "minLength": 1
            },
            "created_time": {
                "type": "string",
                "format": "date-time",
                "description": "模板创建时间"
            },
            "html_template": {
                "type": "string",
                "description": "HTML模板代码"
            },
            "version": {
                "type": "string",
                "description": "模板版本号",
                "default": "1.0.0"
            }
        }
    }
    
    # 文风模板Schema
    STYLE_TEMPLATE_SCHEMA = {
        "type": "object",
        "required": ["template_id", "document_name", "style_features", "style_type", "style_prompt"],
        "properties": {
            "template_id": {
                "type": "string",
                "description": "模板唯一标识符",
                "pattern": "^[a-f0-9]{32}$"
            },
            "document_name": {
                "type": "string",
                "description": "文档名称",
                "minLength": 1,
                "maxLength": 200
            },
            "analysis_time": {
                "type": "string",
                "format": "date-time",
                "description": "分析时间"
            },
            "analysis_method": {
                "type": "string",
                "enum": ["basic", "enhanced", "semantic"],
                "description": "分析方法"
            },
            "document_stats": {
                "type": "object",
                "description": "文档统计信息",
                "properties": {
                    "total_words": {"type": "integer"},
                    "total_sentences": {"type": "integer"},
                    "total_paragraphs": {"type": "integer"},
                    "average_sentence_length": {"type": "number"}
                }
            },
            "style_features": {
                "type": "object",
                "description": "文风特征分析",
                "properties": {
                    "sentence_structure": {"type": "object"},
                    "vocabulary_choice": {"type": "object"},
                    "expression_style": {"type": "object"},
                    "text_organization": {"type": "object"},
                    "language_habits": {"type": "object"}
                }
            },
            "style_type": {
                "type": "string",
                "enum": [
                    "formal_official", "business_professional", "academic_research",
                    "narrative_descriptive", "concise_practical"
                ],
                "description": "文风类型"
            },
            "confidence_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "分析置信度"
            },
            "style_prompt": {
                "type": "string",
                "description": "文风提示词",
                "minLength": 1
            },
            "detailed_analysis": {
                "type": "object",
                "description": "详细分析结果"
            },
            "writing_recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "写作建议"
            },
            "style_comparison": {
                "type": "object",
                "description": "风格对比信息"
            },
            "version": {
                "type": "string",
                "description": "模板版本号",
                "default": "1.0.0"
            }
        }
    }
    
    @classmethod
    def validate_format_template(cls, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证格式模板数据
        
        Args:
            template_data: 格式模板数据
            
        Returns:
            验证结果，包含success状态和错误信息
        """
        try:
            # 基本字段验证
            required_fields = ["template_id", "document_name", "structure_analysis", "format_rules", "format_prompt"]
            for field in required_fields:
                if field not in template_data:
                    return {
                        "success": False,
                        "error": f"缺少必需字段: {field}",
                        "field": field
                    }
            
            # 数据类型验证
            if not isinstance(template_data.get("template_id"), str):
                return {"success": False, "error": "template_id必须是字符串类型"}
            
            if not isinstance(template_data.get("document_name"), str):
                return {"success": False, "error": "document_name必须是字符串类型"}
            
            if not isinstance(template_data.get("structure_analysis"), dict):
                return {"success": False, "error": "structure_analysis必须是对象类型"}
            
            if not isinstance(template_data.get("format_rules"), dict):
                return {"success": False, "error": "format_rules必须是对象类型"}
            
            # 模板ID格式验证
            template_id = template_data.get("template_id", "")
            if not template_id or len(template_id) != 32:
                return {"success": False, "error": "template_id必须是32位字符串"}
            
            return {"success": True, "message": "格式模板验证通过"}
            
        except Exception as e:
            return {"success": False, "error": f"验证过程出错: {str(e)}"}
    
    @classmethod
    def validate_style_template(cls, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证文风模板数据
        
        Args:
            template_data: 文风模板数据
            
        Returns:
            验证结果，包含success状态和错误信息
        """
        try:
            # 基本字段验证
            required_fields = ["template_id", "document_name", "style_features", "style_type", "style_prompt"]
            for field in required_fields:
                if field not in template_data:
                    return {
                        "success": False,
                        "error": f"缺少必需字段: {field}",
                        "field": field
                    }
            
            # 数据类型验证
            if not isinstance(template_data.get("template_id"), str):
                return {"success": False, "error": "template_id必须是字符串类型"}
            
            if not isinstance(template_data.get("document_name"), str):
                return {"success": False, "error": "document_name必须是字符串类型"}
            
            if not isinstance(template_data.get("style_features"), dict):
                return {"success": False, "error": "style_features必须是对象类型"}
            
            # 文风类型验证
            valid_style_types = [
                "formal_official", "business_professional", "academic_research",
                "narrative_descriptive", "concise_practical"
            ]
            style_type = template_data.get("style_type")
            if style_type not in valid_style_types:
                return {"success": False, "error": f"无效的文风类型: {style_type}"}
            
            # 置信度验证
            confidence = template_data.get("confidence_score", 0)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                return {"success": False, "error": "confidence_score必须在0-1之间"}
            
            return {"success": True, "message": "文风模板验证通过"}
            
        except Exception as e:
            return {"success": False, "error": f"验证过程出错: {str(e)}"}
    
    @classmethod
    def normalize_format_template(cls, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化格式模板数据
        
        Args:
            template_data: 原始格式模板数据
            
        Returns:
            标准化后的格式模板数据
        """
        normalized = template_data.copy()
        
        # 确保必需字段存在
        if "template_id" not in normalized:
            normalized["template_id"] = cls._generate_template_id(normalized.get("document_name", ""))
        
        if "created_time" not in normalized:
            normalized["created_time"] = datetime.now().isoformat()
        
        if "version" not in normalized:
            normalized["version"] = "1.0.0"
        
        # 确保结构分析字段存在
        if "structure_analysis" not in normalized:
            normalized["structure_analysis"] = {
                "total_lines": 0,
                "headings": [],
                "paragraphs": [],
                "lists": [],
                "special_elements": [],
                "estimated_format": {},
                "analysis_confidence": 0.0
            }
        
        # 确保格式规则字段存在
        if "format_rules" not in normalized:
            normalized["format_rules"] = {
                "heading_formats": {},
                "paragraph_formats": {},
                "list_formats": {},
                "font_settings": {},
                "spacing_settings": {}
            }
        
        return normalized
    
    @classmethod
    def normalize_style_template(cls, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化文风模板数据
        
        Args:
            template_data: 原始文风模板数据
            
        Returns:
            标准化后的文风模板数据
        """
        normalized = template_data.copy()
        
        # 确保必需字段存在
        if "template_id" not in normalized:
            normalized["template_id"] = cls._generate_template_id(normalized.get("document_name", ""))
        
        if "analysis_time" not in normalized:
            normalized["analysis_time"] = datetime.now().isoformat()
        
        if "analysis_method" not in normalized:
            normalized["analysis_method"] = "basic"
        
        if "version" not in normalized:
            normalized["version"] = "1.0.0"
        
        # 确保文档统计字段存在
        if "document_stats" not in normalized:
            normalized["document_stats"] = {
                "total_words": 0,
                "total_sentences": 0,
                "total_paragraphs": 0,
                "average_sentence_length": 0.0
            }
        
        # 确保文风特征字段存在
        if "style_features" not in normalized:
            normalized["style_features"] = {
                "sentence_structure": {},
                "vocabulary_choice": {},
                "expression_style": {},
                "text_organization": {},
                "language_habits": {}
            }
        
        # 确保写作建议字段存在
        if "writing_recommendations" not in normalized:
            normalized["writing_recommendations"] = []
        
        # 确保风格对比字段存在
        if "style_comparison" not in normalized:
            normalized["style_comparison"] = {}
        
        return normalized
    
    @classmethod
    def _generate_template_id(cls, document_name: str) -> str:
        """
        生成模板ID
        
        Args:
            document_name: 文档名称
            
        Returns:
            32位模板ID
        """
        import hashlib
        import time
        
        # 使用文档名称和时间戳生成唯一ID
        content = f"{document_name}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    @classmethod
    def create_format_template_skeleton(cls, document_name: str) -> Dict[str, Any]:
        """
        创建格式模板骨架
        
        Args:
            document_name: 文档名称
            
        Returns:
            格式模板骨架数据
        """
        return {
            "template_id": cls._generate_template_id(document_name),
            "document_name": document_name,
            "created_time": datetime.now().isoformat(),
            "version": "1.0.0",
            "structure_analysis": {
                "total_lines": 0,
                "headings": [],
                "paragraphs": [],
                "lists": [],
                "special_elements": [],
                "estimated_format": {},
                "analysis_confidence": 0.0
            },
            "format_rules": {
                "heading_formats": {},
                "paragraph_formats": {},
                "list_formats": {},
                "font_settings": {},
                "spacing_settings": {}
            },
            "format_prompt": "",
            "html_template": ""
        }
    
    @classmethod
    def create_style_template_skeleton(cls, document_name: str) -> Dict[str, Any]:
        """
        创建文风模板骨架
        
        Args:
            document_name: 文档名称
            
        Returns:
            文风模板骨架数据
        """
        return {
            "template_id": cls._generate_template_id(document_name),
            "document_name": document_name,
            "analysis_time": datetime.now().isoformat(),
            "analysis_method": "basic",
            "version": "1.0.0",
            "document_stats": {
                "total_words": 0,
                "total_sentences": 0,
                "total_paragraphs": 0,
                "average_sentence_length": 0.0
            },
            "style_features": {
                "sentence_structure": {},
                "vocabulary_choice": {},
                "expression_style": {},
                "text_organization": {},
                "language_habits": {}
            },
            "style_type": "business_professional",
            "confidence_score": 0.0,
            "style_prompt": "",
            "detailed_analysis": {},
            "writing_recommendations": [],
            "style_comparison": {}
        } 