#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Table Processor - 核心模块

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
class TableStructure:
    """表格结构"""
    table_id: str
    headers: List[str]
    rows: List[List[str]]
    table_type: str
    semantic_meaning: str
    fill_strategy: str


@dataclass
class TableCell:
    """表格单元格"""
    row_index: int
    col_index: int
    header: str
    value: str
    data_type: str
    constraints: Dict[str, Any]


class EnhancedTableProcessor:
    """增强表格处理器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.tool_name = "增强表格处理器"
        self.description = "LLM驱动的表格语义理解和智能填充"
        
        # 表格处理模板
        self.table_templates = {
            "table_analysis": self._get_table_analysis_template(),
            "table_semantics": self._get_table_semantics_template(),
            "table_filling": self._get_table_filling_template(),
            "table_validation": self._get_table_validation_template()
        }
        
        # 表格类型识别模式
        self.table_type_patterns = {
            "data_table": [r"数据", r"统计", r"汇总", r"列表"],
            "form_table": [r"表单", r"申请", r"登记", r"填写"],
            "comparison_table": [r"对比", r"比较", r"对照", r"分析"],
            "schedule_table": [r"计划", r"安排", r"时间", r"进度"]
        }
    
    def analyze_table_enhanced(self, table_content: str, table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        增强表格分析
        
        Args:
            table_content: 表格内容
            table_name: 表格名称
            
        Returns:
            增强分析结果
        """
        try:
            analysis_result = {
                "table_name": table_name or "未命名表格",
                "analysis_time": datetime.now().isoformat(),
                "analysis_method": "enhanced_table_processing",
                "table_structure": {},
                "semantic_analysis": {},
                "fill_guidance": {},
                "validation_rules": [],
                "confidence_score": 0.0
            }
            
            # 1. 解析表格结构
            table_structure = self._parse_table_structure(table_content)
            analysis_result["table_structure"] = table_structure
            
            # 2. 语义分析
            semantic_analysis = self._analyze_table_semantics(table_structure, table_content)
            analysis_result["semantic_analysis"] = semantic_analysis
            
            # 3. 填充指导
            fill_guidance = self._generate_fill_guidance(table_structure, semantic_analysis)
            analysis_result["fill_guidance"] = fill_guidance
            
            # 4. 验证规则
            validation_rules = self._generate_validation_rules(table_structure, semantic_analysis)
            analysis_result["validation_rules"] = validation_rules
            
            # 5. 计算置信度
            confidence = self._calculate_table_confidence(table_structure, semantic_analysis)
            analysis_result["confidence_score"] = confidence
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"增强表格分析失败: {str(e)}"}
    
    def fill_table_intelligent(self, table_structure: Dict[str, Any], 
                             fill_data: Dict[str, Any],
                             document_context: str = "") -> Dict[str, Any]:
        """
        智能填充表格
        
        Args:
            table_structure: 表格结构
            fill_data: 填充数据
            document_context: 文档上下文
            
        Returns:
            填充结果
        """
        try:
            fill_result = {
                "fill_time": datetime.now().isoformat(),
                "fill_method": "intelligent_table_filling",
                "filled_table": {},
                "fill_summary": {},
                "validation_results": [],
                "quality_assessment": {}
            }
            
            # 1. 数据映射
            data_mapping = self._map_data_to_table(fill_data, table_structure)
            
            # 2. 智能填充
            filled_table = self._intelligent_fill_table(table_structure, data_mapping, document_context)
            fill_result["filled_table"] = filled_table
            
            # 3. 数据验证
            validation_results = self._validate_filled_table(filled_table, table_structure)
            fill_result["validation_results"] = validation_results
            
            # 4. 质量评估
            quality_assessment = self._assess_fill_quality(filled_table, table_structure, fill_data)
            fill_result["quality_assessment"] = quality_assessment
            
            # 5. 生成摘要
            fill_summary = self._generate_fill_summary(filled_table, validation_results, quality_assessment)
            fill_result["fill_summary"] = fill_summary
            
            return fill_result
            
        except Exception as e:
            return {"error": f"智能表格填充失败: {str(e)}"}
    
    def _parse_table_structure(self, table_content: str) -> Dict[str, Any]:
        """解析表格结构"""
        try:
            lines = table_content.strip().split('\n')
            if not lines:
                return {"error": "表格内容为空"}
            
            # 识别分隔符
            separators = ['|', '\t', ',', ';']
            detected_separator = None
            
            for sep in separators:
                if any(sep in line for line in lines[:3]):
                    detected_separator = sep
                    break
            
            if not detected_separator:
                detected_separator = '|'  # 默认分隔符
            
            # 解析表格
            rows = []
            for line in lines:
                if line.strip():
                    cells = [cell.strip() for cell in line.split(detected_separator)]
                    rows.append(cells)
            
            if not rows:
                return {"error": "无法解析表格行"}
            
            # 提取表头
            headers = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []
            
            # 识别表格类型
            table_type = self._identify_table_type(headers, data_rows)
            
            return {
                "headers": headers,
                "data_rows": data_rows,
                "separator": detected_separator,
                "table_type": table_type,
                "row_count": len(data_rows),
                "column_count": len(headers) if headers else 0
            }
            
        except Exception as e:
            return {"error": f"表格结构解析失败: {str(e)}"}
    
    def _analyze_table_semantics(self, table_structure: Dict[str, Any], 
                               table_content: str) -> Dict[str, Any]:
        """分析表格语义"""
        try:
            if self.llm_client:
                headers = table_structure.get("headers", [])
                table_type = table_structure.get("table_type", "unknown")
                
                prompt = self.table_templates["table_semantics"].format(
                    headers=json.dumps(headers, ensure_ascii=False),
                    table_type=table_type,
                    table_content=table_content[:2000]
                )
                
                response = self.llm_client.generate(prompt)
                try:
                    result = json.loads(response)
                    return result
                except:
                    pass
            
            # 备用语义分析
            return self._fallback_semantic_analysis(table_structure)
            
        except Exception as e:
            return {"error": f"表格语义分析失败: {str(e)}"}
    
    def _generate_fill_guidance(self, table_structure: Dict[str, Any], 
                              semantic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成填充指导"""
        try:
            if self.llm_client:
                headers = table_structure.get("headers", [])
                table_type = table_structure.get("table_type", "unknown")
                semantic_info = json.dumps(semantic_analysis, ensure_ascii=False)
                
                prompt = self.table_templates["table_filling"].format(
                    headers=json.dumps(headers, ensure_ascii=False),
                    table_type=table_type,
                    semantic_info=semantic_info
                )
                
                response = self.llm_client.generate(prompt)
                try:
                    result = json.loads(response)
                    return result
                except:
                    pass
            
            # 备用填充指导
            return self._fallback_fill_guidance(table_structure, semantic_analysis)
            
        except Exception as e:
            return {"error": f"填充指导生成失败: {str(e)}"}
    
    def _generate_validation_rules(self, table_structure: Dict[str, Any], 
                                 semantic_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成验证规则"""
        validation_rules = []
        
        headers = table_structure.get("headers", [])
        
        for header in headers:
            rule = {
                "column": header,
                "data_type": "text",
                "required": False,
                "constraints": {}
            }
            
            # 根据列名推断数据类型和约束
            if any(keyword in header for keyword in ["数量", "金额", "编号"]):
                rule["data_type"] = "number"
                rule["constraints"]["min_value"] = 0
            elif any(keyword in header for keyword in ["日期", "时间"]):
                rule["data_type"] = "date"
            elif any(keyword in header for keyword in ["姓名", "名称"]):
                rule["required"] = True
                rule["constraints"]["min_length"] = 1
            
            validation_rules.append(rule)
        
        return validation_rules
    
    def _map_data_to_table(self, fill_data: Dict[str, Any], 
                          table_structure: Dict[str, Any]) -> Dict[str, Any]:
        """映射数据到表格"""
        mapping = {}
        headers = table_structure.get("headers", [])
        
        for header in headers:
            # 尝试精确匹配
            if header in fill_data:
                mapping[header] = fill_data[header]
                continue
            
            # 尝试模糊匹配
            for key, value in fill_data.items():
                if self._is_similar_field(header, key):
                    mapping[header] = value
                    break
        
        return mapping
    
    def _intelligent_fill_table(self, table_structure: Dict[str, Any], 
                              data_mapping: Dict[str, Any],
                              document_context: str) -> Dict[str, Any]:
        """智能填充表格"""
        try:
            if self.llm_client:
                headers = table_structure.get("headers", [])
                data_info = json.dumps(data_mapping, ensure_ascii=False)
                
                prompt = self.table_templates["table_filling"].format(
                    headers=json.dumps(headers, ensure_ascii=False),
                    data_info=data_info,
                    context=document_context[:1000]
                )
                
                response = self.llm_client.generate(prompt)
                try:
                    result = json.loads(response)
                    return result
                except:
                    pass
            
            # 备用填充逻辑
            return self._fallback_table_filling(table_structure, data_mapping)
            
        except Exception as e:
            return {"error": f"智能表格填充失败: {str(e)}"}
    
    def _validate_filled_table(self, filled_table: Dict[str, Any], 
                             table_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """验证填充后的表格"""
        validation_results = []
        
        # 实现表格验证逻辑
        # 这里可以根据具体的验证规则进行检查
        
        return validation_results
    
    def _assess_fill_quality(self, filled_table: Dict[str, Any], 
                           table_structure: Dict[str, Any],
                           fill_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估填充质量"""
        try:
            headers = table_structure.get("headers", [])
            total_cells = len(headers)
            filled_cells = len([h for h in headers if h in fill_data and fill_data[h]])
            
            completion_rate = filled_cells / total_cells if total_cells > 0 else 0
            
            return {
                "completion_rate": completion_rate,
                "filled_cells": filled_cells,
                "total_cells": total_cells,
                "quality_score": min(1.0, completion_rate * 1.2)  # 简单的质量评分
            }
            
        except Exception as e:
            return {"error": f"质量评估失败: {str(e)}"}
    
    def _generate_fill_summary(self, filled_table: Dict[str, Any], 
                             validation_results: List[Dict[str, Any]],
                             quality_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """生成填充摘要"""
        return {
            "fill_status": "completed" if "error" not in filled_table else "failed",
            "validation_passed": len([r for r in validation_results if r.get("valid", False)]),
            "validation_failed": len([r for r in validation_results if not r.get("valid", False)]),
            "quality_score": quality_assessment.get("quality_score", 0.0),
            "completion_rate": quality_assessment.get("completion_rate", 0.0)
        }
    
    def _identify_table_type(self, headers: List[str], data_rows: List[List[str]]) -> str:
        """识别表格类型"""
        header_text = " ".join(headers).lower()
        
        for table_type, patterns in self.table_type_patterns.items():
            if any(pattern in header_text for pattern in patterns):
                return table_type
        
        return "general"
    
    def _is_similar_field(self, field1: str, field2: str) -> bool:
        """检查字段是否相似"""
        field1_lower = field1.lower()
        field2_lower = field2.lower()
        
        # 简单的相似性检查
        if field1_lower == field2_lower:
            return True
        
        # 检查包含关系
        if field1_lower in field2_lower or field2_lower in field1_lower:
            return True
        
        # 检查关键词匹配
        keywords1 = set(re.findall(r'[\u4e00-\u9fff]+', field1_lower))
        keywords2 = set(re.findall(r'[\u4e00-\u9fff]+', field2_lower))
        
        if keywords1 and keywords2:
            intersection = keywords1.intersection(keywords2)
            if len(intersection) > 0:
                return True
        
        return False
    
    def _get_table_analysis_template(self) -> str:
        """获取表格分析模板"""
        return """
        分析以下表格的结构和特征：

        表格内容：
        {table_content}

        请以JSON格式返回分析结果：
        {{
            "table_purpose": "表格用途",
            "data_patterns": ["数据模式1", "数据模式2"],
            "column_relationships": ["列关系1", "列关系2"],
            "fill_complexity": "simple/medium/complex"
        }}
        """
    
    def _get_table_semantics_template(self) -> str:
        """获取表格语义分析模板"""
        return """
        分析以下表格的语义含义：

        表头：{headers}
        表格类型：{table_type}
        表格内容：{table_content}

        请以JSON格式返回语义分析：
        {{
            "semantic_meaning": "表格的语义含义",
            "column_meanings": {{
                "列名1": "列含义1",
                "列名2": "列含义2"
            }},
            "data_relationships": ["数据关系1", "数据关系2"],
            "business_context": "业务上下文"
        }}
        """
    
    def _get_table_filling_template(self) -> str:
        """获取表格填充模板"""
        return """
        为以下表格生成智能填充指导：

        表头：{headers}
        表格类型：{table_type}
        语义信息：{semantic_info}

        请以JSON格式返回填充指导：
        {{
            "fill_strategy": "填充策略",
            "column_priorities": ["优先级1", "优先级2"],
            "data_mapping_rules": ["映射规则1", "映射规则2"],
            "fill_guidance": "填充指导说明"
        }}
        """
    
    def _get_table_validation_template(self) -> str:
        """获取表格验证模板"""
        return """
        为以下表格生成验证规则：

        表头：{headers}
        表格类型：{table_type}

        请以JSON格式返回验证规则：
        {{
            "validation_rules": [
                {{
                    "column": "列名",
                    "data_type": "数据类型",
                    "required": true/false,
                    "constraints": {{}}
                }}
            ]
        }}
        """
    
    def _fallback_semantic_analysis(self, table_structure: Dict[str, Any]) -> Dict[str, Any]:
        """备用语义分析"""
        headers = table_structure.get("headers", [])
        
        return {
            "semantic_meaning": "数据记录表格",
            "column_meanings": {header: f"{header}字段" for header in headers},
            "data_relationships": [],
            "business_context": "通用数据表格"
        }
    
    def _fallback_fill_guidance(self, table_structure: Dict[str, Any], 
                              semantic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """备用填充指导"""
        headers = table_structure.get("headers", [])
        
        return {
            "fill_strategy": "按列顺序填充",
            "column_priorities": headers,
            "data_mapping_rules": ["精确匹配", "模糊匹配"],
            "fill_guidance": "根据字段名称匹配数据进行填充"
        }
    
    def _fallback_table_filling(self, table_structure: Dict[str, Any], 
                              data_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """备用表格填充"""
        headers = table_structure.get("headers", [])
        filled_rows = []
        
        # 创建填充后的行
        row_data = []
        for header in headers:
            value = data_mapping.get(header, "")
            row_data.append(value)
        
        filled_rows.append(row_data)
        
        return {
            "headers": headers,
            "filled_rows": filled_rows,
            "fill_status": "completed"
        }
    
    def _calculate_table_confidence(self, table_structure: Dict[str, Any], 
                                  semantic_analysis: Dict[str, Any]) -> float:
        """计算表格分析置信度"""
        try:
            confidence = 0.0
            
            # 结构解析质量
            if "error" not in table_structure:
                confidence += 0.4
            
            # 语义分析质量
            if "error" not in semantic_analysis:
                confidence += 0.3
            
            # 表格复杂度
            headers = table_structure.get("headers", [])
            if len(headers) > 0:
                confidence += min(0.3, len(headers) * 0.05)
            
            return min(1.0, confidence)
            
        except Exception as e:
            return 0.3  # 默认置信度 