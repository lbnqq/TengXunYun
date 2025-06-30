#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Field Recognizer - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class FieldInfo:
    """字段信息"""
    field_id: str
    field_name: str
    field_type: str
    field_meaning: str
    dependencies: List[str]
    priority: int
    constraints: Dict[str, Any]
    ai_fill_prompt: str


@dataclass
class FieldRelationship:
    """字段关系"""
    source_field: str
    target_field: str
    relationship_type: str  # dependency, conflict, complement
    strength: float
    description: str


class EnhancedFieldRecognizer:
    """增强字段识别器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.tool_name = "增强字段识别器"
        self.description = "LLM驱动的字段含义推断、依赖关系分析和优先级排序"
        
        # 字段识别模板
        self.recognition_templates = {
            "field_meaning": self._get_field_meaning_template(),
            "field_relationships": self._get_field_relationships_template(),
            "field_priorities": self._get_field_priorities_template(),
            "field_constraints": self._get_field_constraints_template()
        }
        
        # 字段类型映射
        self.field_type_patterns = {
            "text": [r"名称", r"标题", r"描述", r"说明", r"备注"],
            "number": [r"数量", r"金额", r"编号", r"序号", r"比例"],
            "date": [r"日期", r"时间", r"期限", r"截止"],
            "select": [r"类型", r"类别", r"选项", r"选择"],
            "file": [r"附件", r"文件", r"图片", r"文档"],
            "contact": [r"姓名", r"电话", r"邮箱", r"地址"]
        }
    
    def analyze_fields_enhanced(self, fields: List[Dict[str, Any]], 
                              document_content: str = "",
                              document_type: str = "general") -> Dict[str, Any]:
        """
        增强字段分析
        
        Args:
            fields: 字段列表
            document_content: 文档内容
            document_type: 文档类型
            
        Returns:
            增强分析结果
        """
        try:
            analysis_result = {
                "analysis_time": datetime.now().isoformat(),
                "analysis_method": "enhanced_field_recognition",
                "enhanced_fields": [],
                "field_relationships": [],
                "field_priorities": {},
                "field_categories": {},
                "consistency_checks": [],
                "confidence_score": 0.0
            }
            
            # 1. 字段含义推断
            enhanced_fields = []
            for field in fields:
                enhanced_field = self._analyze_field_meaning(field, document_content, document_type)
                enhanced_fields.append(enhanced_field)
            
            analysis_result["enhanced_fields"] = enhanced_fields
            
            # 2. 字段关系分析
            relationships = self._analyze_field_relationships(enhanced_fields, document_content)
            analysis_result["field_relationships"] = relationships
            
            # 3. 字段优先级排序
            priorities = self._analyze_field_priorities(enhanced_fields, document_type)
            analysis_result["field_priorities"] = priorities
            
            # 4. 字段分类
            categories = self._categorize_fields(enhanced_fields)
            analysis_result["field_categories"] = categories
            
            # 5. 一致性检查
            consistency_checks = self._check_field_consistency(enhanced_fields, relationships)
            analysis_result["consistency_checks"] = consistency_checks
            
            # 6. 计算置信度
            confidence = self._calculate_field_confidence(enhanced_fields, relationships, consistency_checks)
            analysis_result["confidence_score"] = confidence
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"增强字段分析失败: {str(e)}"}
    
    def _analyze_field_meaning(self, field: Dict[str, Any], document_content: str, 
                             document_type: str) -> Dict[str, Any]:
        """分析字段含义"""
        try:
            field_name = field.get("field_name", "")
            field_type = field.get("field_type", "text")
            
            if self.llm_client:
                prompt = self.recognition_templates["field_meaning"].format(
                    field_name=field_name,
                    field_type=field_type,
                    document_type=document_type,
                    document_content=document_content[:1000]
                )
                
                response = self.llm_client.generate(prompt)
                try:
                    result = json.loads(response)
                    return {**field, **result}
                except:
                    pass
            
            # 备用分析逻辑
            return self._fallback_field_meaning(field, document_type)
            
        except Exception as e:
            return {**field, "error": f"字段含义分析失败: {str(e)}"}
    
    def _analyze_field_relationships(self, fields: List[Dict[str, Any]], 
                                   document_content: str) -> List[Dict[str, Any]]:
        """分析字段关系"""
        try:
            if self.llm_client and len(fields) > 1:
                field_info = json.dumps([{
                    "field_name": f.get("field_name", ""),
                    "field_type": f.get("field_type", ""),
                    "field_meaning": f.get("field_meaning", "")
                } for f in fields], ensure_ascii=False)
                
                prompt = self.recognition_templates["field_relationships"].format(
                    fields_info=field_info,
                    document_content=document_content[:1000]
                )
                
                response = self.llm_client.generate(prompt)
                try:
                    result = json.loads(response)
                    return result.get("relationships", [])
                except:
                    pass
            
            # 备用关系分析
            return self._fallback_field_relationships(fields)
            
        except Exception as e:
            return [{"error": f"字段关系分析失败: {str(e)}"}]
    
    def _analyze_field_priorities(self, fields: List[Dict[str, Any]], 
                                document_type: str) -> Dict[str, int]:
        """分析字段优先级"""
        try:
            if self.llm_client:
                field_info = json.dumps([{
                    "field_name": f.get("field_name", ""),
                    "field_type": f.get("field_type", ""),
                    "field_meaning": f.get("field_meaning", "")
                } for f in fields], ensure_ascii=False)
                
                prompt = self.recognition_templates["field_priorities"].format(
                    fields_info=field_info,
                    document_type=document_type
                )
                
                response = self.llm_client.generate(prompt)
                try:
                    result = json.loads(response)
                    return result.get("priorities", {})
                except:
                    pass
            
            # 备用优先级分析
            return self._fallback_field_priorities(fields, document_type)
            
        except Exception as e:
            return {"error": f"字段优先级分析失败: {str(e)}"}
    
    def _categorize_fields(self, fields: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """字段分类"""
        categories = {
            "basic_info": [],
            "technical_details": [],
            "contact_info": [],
            "financial_info": [],
            "attachments": [],
            "other": []
        }
        
        for field in fields:
            field_name = field.get("field_name", "").lower()
            field_meaning = field.get("field_meaning", "").lower()
            
            # 基础信息
            if any(keyword in field_name or keyword in field_meaning 
                   for keyword in ["名称", "标题", "描述", "简介"]):
                categories["basic_info"].append(field.get("field_name", ""))
            
            # 技术细节
            elif any(keyword in field_name or keyword in field_meaning 
                     for keyword in ["技术", "参数", "规格", "配置"]):
                categories["technical_details"].append(field.get("field_name", ""))
            
            # 联系信息
            elif any(keyword in field_name or keyword in field_meaning 
                     for keyword in ["姓名", "电话", "邮箱", "地址"]):
                categories["contact_info"].append(field.get("field_name", ""))
            
            # 财务信息
            elif any(keyword in field_name or keyword in field_meaning 
                     for keyword in ["金额", "费用", "预算", "成本"]):
                categories["financial_info"].append(field.get("field_name", ""))
            
            # 附件
            elif any(keyword in field_name or keyword in field_meaning 
                     for keyword in ["附件", "文件", "图片", "文档"]):
                categories["attachments"].append(field.get("field_name", ""))
            
            else:
                categories["other"].append(field.get("field_name", ""))
        
        return categories
    
    def _check_field_consistency(self, fields: List[Dict[str, Any]], 
                               relationships: List[Dict[str, Any]]) -> List[str]:
        """检查字段一致性"""
        consistency_checks = []
        
        # 检查字段名称一致性
        field_names = [f.get("field_name", "") for f in fields]
        if len(field_names) != len(set(field_names)):
            consistency_checks.append("存在重复字段名称")
        
        # 检查字段类型一致性
        field_types = [f.get("field_type", "") for f in fields]
        if len(set(field_types)) == 1 and field_types[0] == "text":
            consistency_checks.append("所有字段都是文本类型，可能需要更精确的类型识别")
        
        # 检查关系一致性
        for rel in relationships:
            source = rel.get("source_field", "")
            target = rel.get("target_field", "")
            if source not in field_names or target not in field_names:
                consistency_checks.append(f"关系字段'{source}'或'{target}'不存在")
        
        return consistency_checks
    
    def _get_field_meaning_template(self) -> str:
        """获取字段含义分析模板"""
        return """
        分析以下字段的含义和填写要求：

        字段名称：{field_name}
        字段类型：{field_type}
        文档类型：{document_type}
        文档内容：{document_content}

        请以JSON格式返回分析结果：
        {{
            "field_meaning": "字段的具体含义和用途",
            "dependencies": ["依赖字段1", "依赖字段2"],
            "priority": 1-5,
            "constraints": {{
                "required": true/false,
                "min_length": 0,
                "max_length": 0,
                "options": ["选项1", "选项2"],
                "format": "格式要求"
            }},
            "ai_fill_prompt": "AI填写提示词"
        }}
        """
    
    def _get_field_relationships_template(self) -> str:
        """获取字段关系分析模板"""
        return """
        分析以下字段之间的关系：

        字段信息：
        {fields_info}

        文档内容：
        {document_content}

        请以JSON格式返回关系分析：
        {{
            "relationships": [
                {{
                    "source_field": "字段1",
                    "target_field": "字段2",
                    "relationship_type": "dependency/conflict/complement",
                    "strength": 0.0-1.0,
                    "description": "关系描述"
                }}
            ]
        }}
        """
    
    def _get_field_priorities_template(self) -> str:
        """获取字段优先级分析模板"""
        return """
        分析以下字段的填写优先级：

        字段信息：
        {fields_info}

        文档类型：{document_type}

        请以JSON格式返回优先级分析：
        {{
            "priorities": {{
                "字段名1": 1-5,
                "字段名2": 1-5
            }}
        }}
        """
    
    def _get_field_constraints_template(self) -> str:
        """获取字段约束分析模板"""
        return """
        分析以下字段的填写约束：

        字段信息：
        {fields_info}

        请以JSON格式返回约束分析：
        {{
            "constraints": {{
                "字段名1": {{
                    "required": true/false,
                    "min_length": 0,
                    "max_length": 0,
                    "options": ["选项1", "选项2"],
                    "format": "格式要求"
                }}
            }}
        }}
        """
    
    def _fallback_field_meaning(self, field: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """备用字段含义分析"""
        field_name = field.get("field_name", "")
        field_type = field.get("field_type", "text")
        
        # 简单的含义推断
        meaning = f"{field_name}字段"
        if "名称" in field_name:
            meaning = f"{field_name}，用于标识和区分"
        elif "日期" in field_name or "时间" in field_name:
            meaning = f"{field_name}，记录时间信息"
        elif "金额" in field_name or "费用" in field_name:
            meaning = f"{field_name}，记录财务信息"
        
        # 简单的约束推断
        constraints = {
            "required": "必填" in field_name or "必需" in field_name,
            "min_length": 0,
            "max_length": 100 if field_type == "text" else 0,
            "options": [],
            "format": ""
        }
        
        return {
            **field,
            "field_meaning": meaning,
            "dependencies": [],
            "priority": 3,
            "constraints": constraints,
            "ai_fill_prompt": f"请填写{field_name}，要求：{meaning}"
        }
    
    def _fallback_field_relationships(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """备用字段关系分析"""
        relationships = []
        
        # 简单的依赖关系推断
        field_names = [f.get("field_name", "") for f in fields]
        
        for i, field1 in enumerate(fields):
            for j, field2 in enumerate(fields):
                if i != j:
                    name1 = field1.get("field_name", "")
                    name2 = field2.get("field_name", "")
                    
                    # 检查是否有明显的依赖关系
                    if "总" in name1 and "分" in name2:
                        relationships.append({
                            "source_field": name1,
                            "target_field": name2,
                            "relationship_type": "dependency",
                            "strength": 0.7,
                            "description": f"{name1}可能包含{name2}的汇总信息"
                        })
        
        return relationships
    
    def _fallback_field_priorities(self, fields: List[Dict[str, Any]], 
                                 document_type: str) -> Dict[str, int]:
        """备用字段优先级分析"""
        priorities = {}
        
        for field in fields:
            field_name = field.get("field_name", "")
            priority = 3  # 默认优先级
            
            # 根据字段名称调整优先级
            if any(keyword in field_name for keyword in ["名称", "标题", "主题"]):
                priority = 5  # 最高优先级
            elif any(keyword in field_name for keyword in ["日期", "时间", "期限"]):
                priority = 4
            elif any(keyword in field_name for keyword in ["附件", "文件", "图片"]):
                priority = 2  # 较低优先级
            elif any(keyword in field_name for keyword in ["备注", "说明", "注释"]):
                priority = 1  # 最低优先级
            
            priorities[field_name] = priority
        
        return priorities
    
    def _calculate_field_confidence(self, fields: List[Dict[str, Any]], 
                                  relationships: List[Dict[str, Any]],
                                  consistency_checks: List[str]) -> float:
        """计算字段分析置信度"""
        try:
            confidence = 0.0
            
            # 字段分析质量
            valid_fields = len([f for f in fields if "error" not in f])
            total_fields = len(fields)
            if total_fields > 0:
                confidence += (valid_fields / total_fields) * 0.4
            
            # 关系分析质量
            valid_relationships = len([r for r in relationships if "error" not in r])
            total_relationships = len(relationships)
            if total_relationships > 0:
                confidence += (valid_relationships / total_relationships) * 0.3
            
            # 一致性检查
            consistency_score = max(0, 1 - len(consistency_checks) * 0.1)
            confidence += consistency_score * 0.3
            
            return min(1.0, confidence)
            
        except Exception as e:
            return 0.3  # 默认置信度 