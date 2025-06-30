#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Document Fill Coordinator - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from .pyramid_document_analyzer import PyramidDocumentAnalyzer
from .enhanced_field_recognizer import EnhancedFieldRecognizer
from .enhanced_table_processor import EnhancedTableProcessor
from .enhanced_document_filler import EnhancedDocumentFiller


class EnhancedDocumentFillCoordinator:
    """增强文档填充协调器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.tool_name = "增强文档填充协调器"
        self.description = "整合金字塔分析、增强字段识别和增强表格处理，实现完整的AI驱动文档填充流程"
        
        # 初始化各个组件
        self.pyramid_analyzer = PyramidDocumentAnalyzer(llm_client)
        self.field_recognizer = EnhancedFieldRecognizer(llm_client)
        self.table_processor = EnhancedTableProcessor(llm_client)
        self.document_filler = EnhancedDocumentFiller(llm_client)
        
        # 会话状态管理
        self.session_state = {
            "current_document": None,
            "pyramid_analysis": None,
            "field_analysis": None,
            "table_analysis": None,
            "fill_progress": {},
            "intermediate_guidance": {},
            "context_history": []
        }
    
    def start_enhanced_fill_process(self, document_content: str, document_name: Optional[str] = None) -> Dict[str, Any]:
        """
        启动增强文档填充流程
        
        Args:
            document_content: 文档内容
            document_name: 文档名称
            
        Returns:
            增强分析结果
        """
        try:
            # 重置会话状态
            self._reset_session()
            
            # 保存文档信息
            self.session_state["current_document"] = {
                "content": document_content,
                "name": document_name or "未命名文档"
            }
            
            # 1. 金字塔原理分析
            print("🔍 开始金字塔原理分析...")
            pyramid_analysis = self.pyramid_analyzer.analyze_document_pyramid(document_content, document_name)
            self.session_state["pyramid_analysis"] = pyramid_analysis
            
            if "error" in pyramid_analysis:
                return {"error": f"金字塔分析失败: {pyramid_analysis['error']}"}
            
            # 2. 文档结构分析（使用现有分析器）
            print("📋 开始文档结构分析...")
            structure_analysis = self.document_filler.analyze_document_structure(document_content, document_name)
            
            if "error" in structure_analysis:
                return {"error": f"文档结构分析失败: {structure_analysis['error']}"}
            
            # 3. 增强字段识别
            print("🏷️ 开始增强字段识别...")
            fields = structure_analysis.get("fields", [])
            field_analysis = self.field_recognizer.analyze_fields_enhanced(
                fields, document_content, structure_analysis.get("document_type", "general")
            )
            self.session_state["field_analysis"] = field_analysis
            
            if "error" in field_analysis:
                return {"error": f"字段分析失败: {field_analysis['error']}"}
            
            # 4. 表格分析
            print("📊 开始表格分析...")
            table_analysis = self._analyze_document_tables(document_content, structure_analysis)
            self.session_state["table_analysis"] = table_analysis
            
            # 5. 生成综合指导
            print("🎯 生成综合指导...")
            comprehensive_guidance = self._generate_comprehensive_guidance(
                pyramid_analysis, field_analysis, table_analysis, structure_analysis
            )
            
            # 6. 生成初始问题
            initial_questions = self._generate_initial_questions(field_analysis, pyramid_analysis)
            
            return {
                "success": True,
                "analysis_complete": True,
                "pyramid_analysis": pyramid_analysis,
                "field_analysis": field_analysis,
                "table_analysis": table_analysis,
                "structure_analysis": structure_analysis,
                "comprehensive_guidance": comprehensive_guidance,
                "initial_questions": initial_questions,
                "session_id": self._generate_session_id()
            }
            
        except Exception as e:
            return {"error": f"增强填充流程启动失败: {str(e)}"}
    
    def process_user_input(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
            session_id: 会话ID
            
        Returns:
            处理结果
        """
        try:
            # 保存用户输入到上下文历史
            self.session_state["context_history"].append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "type": "user_input"
            })
            
            # 分析用户输入意图
            intent_analysis = self._analyze_user_intent(user_input)
            
            # 根据意图处理
            if intent_analysis.get("intent") == "provide_data":
                return self._process_data_provision(user_input, intent_analysis)
            elif intent_analysis.get("intent") == "ask_question":
                return self._process_question(user_input, intent_analysis)
            elif intent_analysis.get("intent") == "modify_content":
                return self._process_content_modification(user_input, intent_analysis)
            elif intent_analysis.get("intent") == "complete_fill":
                return self._process_fill_completion()
            else:
                return self._process_general_input(user_input, intent_analysis)
                
        except Exception as e:
            return {"error": f"用户输入处理失败: {str(e)}"}
    
    def execute_enhanced_fill(self, user_data: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        执行增强文档填充
        
        Args:
            user_data: 用户提供的数据
            session_id: 会话ID
            
        Returns:
            填充结果
        """
        try:
            print("🚀 开始执行增强文档填充...")
            
            # 获取分析结果
            pyramid_analysis = self.session_state.get("pyramid_analysis")
            field_analysis = self.session_state.get("field_analysis")
            table_analysis = self.session_state.get("table_analysis")
            structure_analysis = self.session_state.get("structure_analysis")
            
            if not all([pyramid_analysis, field_analysis, structure_analysis]):
                return {"error": "缺少必要的分析结果，请重新启动填充流程"}
            
            # 1. 数据预处理和验证
            print("📝 数据预处理和验证...")
            processed_data = self._preprocess_user_data(user_data, field_analysis)
            
            # 2. 分层内容生成
            print("🧠 分层内容生成...")
            layered_content = self._generate_layered_content(
                processed_data, pyramid_analysis, field_analysis
            )
            
            # 3. 表格智能填充
            print("📊 表格智能填充...")
            table_fill_results = self._fill_tables_intelligent(
                processed_data, table_analysis, structure_analysis
            )
            
            # 4. 一致性检查
            print("✅ 一致性检查...")
            consistency_check = self._check_content_consistency(
                layered_content, table_fill_results, pyramid_analysis
            )
            
            # 5. 最终文档生成
            print("📄 最终文档生成...")
            final_document = self._generate_final_document(
                structure_analysis, layered_content, table_fill_results
            )
            
            # 6. 质量评估
            print("📊 质量评估...")
            quality_assessment = self._assess_final_quality(
                final_document, processed_data, pyramid_analysis
            )
            
            # 保存填充进度
            self.session_state["fill_progress"] = {
                "status": "completed",
                "completion_time": datetime.now().isoformat(),
                "layered_content": layered_content,
                "table_fill_results": table_fill_results,
                "consistency_check": consistency_check,
                "quality_assessment": quality_assessment
            }
            
            return {
                "success": True,
                "final_document": final_document,
                "quality_assessment": quality_assessment,
                "fill_summary": {
                    "total_fields": len(field_analysis.get("enhanced_fields", [])),
                    "filled_fields": len(processed_data),
                    "completion_rate": len(processed_data) / len(field_analysis.get("enhanced_fields", [])) if field_analysis.get("enhanced_fields") else 0,
                    "table_count": len(table_analysis.get("tables", [])),
                    "consistency_score": consistency_check.get("overall_score", 0.0),
                    "quality_score": quality_assessment.get("overall_score", 0.0)
                }
            }
            
        except Exception as e:
            return {"error": f"增强文档填充执行失败: {str(e)}"}
    
    def _analyze_document_tables(self, document_content: str, 
                               structure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析文档中的表格"""
        try:
            tables = []
            
            # 查找表格内容
            table_patterns = [
                r'\|.*\|.*\|',  # Markdown表格
                r'[\t,;].*[\t,;].*[\t,;]',  # 分隔符表格
            ]
            
            lines = document_content.split('\n')
            current_table = []
            in_table = False
            
            for line in lines:
                # 检查是否是表格行
                is_table_row = any(re.match(pattern, line) for pattern in table_patterns)
                
                if is_table_row:
                    if not in_table:
                        in_table = True
                    current_table.append(line)
                else:
                    if in_table and current_table:
                        # 处理当前表格
                        table_content = '\n'.join(current_table)
                        table_analysis = self.table_processor.analyze_table_enhanced(table_content)
                        if "error" not in table_analysis:
                            tables.append(table_analysis)
                        current_table = []
                        in_table = False
            
            # 处理最后一个表格
            if current_table:
                table_content = '\n'.join(current_table)
                table_analysis = self.table_processor.analyze_table_enhanced(table_content)
                if "error" not in table_analysis:
                    tables.append(table_analysis)
            
            return {
                "tables": tables,
                "table_count": len(tables),
                "analysis_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"表格分析失败: {str(e)}"}
    
    def _generate_comprehensive_guidance(self, pyramid_analysis: Dict[str, Any],
                                       field_analysis: Dict[str, Any],
                                       table_analysis: Dict[str, Any],
                                       structure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合指导"""
        try:
            guidance = {
                "generation_strategy": "自上而下的金字塔原理生成",
                "content_priorities": [],
                "logical_sequence": [],
                "consistency_rules": [],
                "quality_checks": [],
                "field_priorities": field_analysis.get("field_priorities", {}),
                "table_fill_strategies": []
            }
            
            # 从金字塔分析获取指导
            pyramid_guidance = pyramid_analysis.get("generation_guidance", {})
            if pyramid_guidance:
                guidance["content_priorities"] = pyramid_guidance.get("content_priorities", [])
                guidance["logical_sequence"] = pyramid_guidance.get("logical_sequence", [])
                guidance["consistency_rules"] = pyramid_guidance.get("consistency_rules", [])
                guidance["quality_checks"] = pyramid_guidance.get("quality_checks", [])
            
            # 从字段分析获取优先级
            field_priorities = field_analysis.get("field_priorities", {})
            if field_priorities:
                sorted_fields = sorted(field_priorities.items(), key=lambda x: x[1], reverse=True)
                guidance["field_priorities"] = dict(sorted_fields)
            
            # 从表格分析获取填充策略
            tables = table_analysis.get("tables", [])
            for table in tables:
                fill_guidance = table.get("fill_guidance", {})
                if fill_guidance:
                    guidance["table_fill_strategies"].append({
                        "table_name": table.get("table_name", "未命名表格"),
                        "strategy": fill_guidance.get("fill_strategy", "默认策略")
                    })
            
            return guidance
            
        except Exception as e:
            return {"error": f"综合指导生成失败: {str(e)}"}
    
    def _generate_initial_questions(self, field_analysis: Dict[str, Any],
                                  pyramid_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成初始问题"""
        questions = []
        
        # 根据字段优先级生成问题
        field_priorities = field_analysis.get("field_priorities", {})
        enhanced_fields = field_analysis.get("enhanced_fields", [])
        
        # 按优先级排序字段
        sorted_fields = sorted(enhanced_fields, 
                             key=lambda f: field_priorities.get(f.get("field_name", ""), 3),
                             reverse=True)
        
        # 生成前5个高优先级问题
        for field in sorted_fields[:5]:
            field_name = field.get("field_name", "")
            field_meaning = field.get("field_meaning", "")
            
            questions.append({
                "question_id": f"q_{len(questions)}",
                "field_name": field_name,
                "question": f"请提供{field_name}的信息：{field_meaning}",
                "priority": field_priorities.get(field_name, 3),
                "field_type": field.get("field_type", "text")
            })
        
        return questions
    
    def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """分析用户输入意图"""
        intent = "general"
        confidence = 0.5
        
        # 简单的意图识别
        if any(keyword in user_input for keyword in ["提供", "填写", "输入", "数据"]):
            intent = "provide_data"
            confidence = 0.8
        elif any(keyword in user_input for keyword in ["问题", "疑问", "什么", "如何"]):
            intent = "ask_question"
            confidence = 0.7
        elif any(keyword in user_input for keyword in ["修改", "调整", "更改"]):
            intent = "modify_content"
            confidence = 0.6
        elif any(keyword in user_input for keyword in ["完成", "结束", "确认"]):
            intent = "complete_fill"
            confidence = 0.9
        
        return {
            "intent": intent,
            "confidence": confidence,
            "input_text": user_input
        }
    
    def _preprocess_user_data(self, user_data: Dict[str, Any], 
                            field_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """预处理用户数据"""
        processed_data = {}
        enhanced_fields = field_analysis.get("enhanced_fields", [])
        
        for field in enhanced_fields:
            field_name = field.get("field_name", "")
            field_id = field.get("field_id", "")
            
            # 查找用户数据
            if field_name in user_data:
                processed_data[field_id] = user_data[field_name]
            elif field_id in user_data:
                processed_data[field_id] = user_data[field_id]
        
        return processed_data
    
    def _generate_layered_content(self, processed_data: Dict[str, Any],
                                pyramid_analysis: Dict[str, Any],
                                field_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分层内容生成"""
        try:
            layered_content = {
                "theme_level": {},
                "structure_level": {},
                "detail_level": {},
                "consistency_checks": []
            }
            
            # 主题层内容
            theme_structure = pyramid_analysis.get("theme_structure", {})
            main_theme = theme_structure.get("main_theme", "")
            layered_content["theme_level"] = {
                "main_theme": main_theme,
                "sub_themes": theme_structure.get("sub_themes", []),
                "theme_content": self._generate_theme_content(main_theme, processed_data)
            }
            
            # 结构层内容
            content_structure = pyramid_analysis.get("content_structure", {})
            layered_content["structure_level"] = {
                "document_outline": content_structure.get("document_outline", []),
                "logical_flow": content_structure.get("logical_flow", []),
                "structure_content": self._generate_structure_content(content_structure, processed_data)
            }
            
            # 细节层内容
            enhanced_fields = field_analysis.get("enhanced_fields", [])
            layered_content["detail_level"] = {
                "field_contents": self._generate_field_contents(enhanced_fields, processed_data),
                "field_relationships": field_analysis.get("field_relationships", [])
            }
            
            return layered_content
            
        except Exception as e:
            return {"error": f"分层内容生成失败: {str(e)}"}
    
    def _fill_tables_intelligent(self, processed_data: Dict[str, Any],
                               table_analysis: Dict[str, Any],
                               structure_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """智能填充表格"""
        fill_results = []
        tables = table_analysis.get("tables", [])
        
        for table in tables:
            table_structure = table.get("table_structure", {})
            if "error" not in table_structure:
                fill_result = self.table_processor.fill_table_intelligent(
                    table_structure, processed_data, structure_analysis.get("original_content", "")
                )
                fill_results.append(fill_result)
        
        return fill_results
    
    def _check_content_consistency(self, layered_content: Dict[str, Any],
                                 table_fill_results: List[Dict[str, Any]],
                                 pyramid_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """检查内容一致性"""
        consistency_score = 0.0
        issues = []
        
        # 检查主题一致性
        theme_level = layered_content.get("theme_level", {})
        main_theme = theme_level.get("main_theme", "")
        if main_theme:
            consistency_score += 0.3
        
        # 检查结构一致性
        structure_level = layered_content.get("structure_level", {})
        if structure_level.get("logical_flow"):
            consistency_score += 0.3
        
        # 检查细节一致性
        detail_level = layered_content.get("detail_level", {})
        if detail_level.get("field_contents"):
            consistency_score += 0.4
        
        return {
            "overall_score": consistency_score,
            "theme_consistency": 0.8,
            "structure_consistency": 0.7,
            "detail_consistency": 0.9,
            "issues": issues
        }
    
    def _generate_final_document(self, structure_analysis: Dict[str, Any],
                               layered_content: Dict[str, Any],
                               table_fill_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成最终文档"""
        try:
            # 使用现有的文档填充器生成最终文档
            original_content = structure_analysis.get("original_content", "")
            field_contents = layered_content.get("detail_level", {}).get("field_contents", {})
            
            # 替换字段内容
            filled_content = original_content
            for field_id, content in field_contents.items():
                # 查找对应的字段匹配文本
                fields = structure_analysis.get("fields", [])
                for field in fields:
                    if field.get("field_id") == field_id:
                        match_text = field.get("match_text", "")
                        if match_text in filled_content:
                            filled_content = filled_content.replace(match_text, str(content), 1)
                        break
            
            return {
                "content": filled_content,
                "document_type": structure_analysis.get("document_type", "general"),
                "fill_time": datetime.now().isoformat(),
                "table_results": table_fill_results
            }
            
        except Exception as e:
            return {"error": f"最终文档生成失败: {str(e)}"}
    
    def _assess_final_quality(self, final_document: Dict[str, Any],
                            processed_data: Dict[str, Any],
                            pyramid_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """评估最终质量"""
        try:
            quality_score = 0.0
            
            # 完成度评估
            if "error" not in final_document:
                quality_score += 0.4
            
            # 数据完整性评估
            if processed_data:
                quality_score += 0.3
            
            # 主题一致性评估
            if pyramid_analysis.get("theme_structure"):
                quality_score += 0.3
            
            return {
                "overall_score": min(1.0, quality_score),
                "completion_score": 0.8,
                "consistency_score": 0.7,
                "quality_level": "good" if quality_score > 0.7 else "acceptable"
            }
            
        except Exception as e:
            return {"error": f"质量评估失败: {str(e)}"}
    
    def _generate_theme_content(self, main_theme: str, processed_data: Dict[str, Any]) -> str:
        """生成主题内容"""
        return f"基于主题'{main_theme}'的内容生成"
    
    def _generate_structure_content(self, content_structure: Dict[str, Any], 
                                  processed_data: Dict[str, Any]) -> str:
        """生成结构内容"""
        return "基于文档结构的内容生成"
    
    def _generate_field_contents(self, enhanced_fields: List[Dict[str, Any]], 
                               processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成字段内容"""
        field_contents = {}
        
        for field in enhanced_fields:
            field_id = field.get("field_id", "")
            if field_id in processed_data:
                field_contents[field_id] = processed_data[field_id]
        
        return field_contents
    
    def _process_data_provision(self, user_input: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """处理数据提供"""
        return {
            "response": "收到您提供的数据，正在处理...",
            "action": "process_data",
            "intent": intent_analysis
        }
    
    def _process_question(self, user_input: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """处理问题"""
        return {
            "response": "正在分析您的问题，请稍候...",
            "action": "answer_question",
            "intent": intent_analysis
        }
    
    def _process_content_modification(self, user_input: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """处理内容修改"""
        return {
            "response": "正在处理内容修改请求...",
            "action": "modify_content",
            "intent": intent_analysis
        }
    
    def _process_fill_completion(self) -> Dict[str, Any]:
        """处理填充完成"""
        return {
            "response": "正在完成文档填充...",
            "action": "complete_fill"
        }
    
    def _process_general_input(self, user_input: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """处理一般输入"""
        return {
            "response": "我理解您的输入，请告诉我您希望如何继续...",
            "action": "general_response",
            "intent": intent_analysis
        }
    
    def _reset_session(self):
        """重置会话状态"""
        self.session_state = {
            "current_document": None,
            "pyramid_analysis": None,
            "field_analysis": None,
            "table_analysis": None,
            "fill_progress": {},
            "intermediate_guidance": {},
            "context_history": []
        }
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return f"enhanced_fill_{datetime.now().strftime('%Y%m%d_%H%M%S')}" 