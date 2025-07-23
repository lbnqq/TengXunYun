#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Format Extractor - 核心模块

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
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import hashlib
import time

class DocumentFormatExtractor:
    
    def __init__(self, storage_path: str = "src/core/knowledge_base/format_templates", spark_x1_client=None):
        self.tool_name = "文档格式提取器"
        self.description = "智能分析文档格式，生成格式对齐提示词，支持格式模板保存和复用"
        self.storage_path = storage_path
        self.spark_x1_client = spark_x1_client

        # 确保存储目录存在
        os.makedirs(storage_path, exist_ok=True)
        
        # 字体大小映射（磅值到中文描述）
        self.font_size_mapping = {
            "42": "初号", "36": "小初", "26": "一号", "24": "小一",
            "22": "二号", "18": "小二", "16": "三号", "15": "小三",
            "14": "四号", "12": "小四", "10.5": "五号", "9": "小五",
            "7.5": "六号", "6.5": "小六", "5.5": "七号", "5": "八号"
        }
        
        # 常见字体映射
        self.font_family_mapping = {
            "SimSun": "宋体", "SimHei": "黑体", "KaiTi": "楷体",
            "FangSong": "仿宋", "Microsoft YaHei": "微软雅黑",
            "Times New Roman": "Times New Roman", "Arial": "Arial"
        }
    
    def extract_format_from_document(self, document_content: str, document_name: Optional[str] = None) -> Dict[str, Any]:
        """
        从文档中提取格式信息
        
        Args:
            document_content: 文档内容
            document_name: 文档名称
            
        Returns:
            格式分析结果
        """
        try:
            # 分析文档结构
            structure_analysis = self._analyze_document_structure(document_content)
            
            # 提取格式规范
            format_rules = self._extract_format_rules(structure_analysis)
            
            # 生成格式提示词
            doc_name = document_name or "未命名文档"
            template_id = self._generate_template_id(doc_name, format_rules)
            
            # 生成示范文档
            demo_document = self.generate_format_demo_document(format_rules)
            
            result = {
                "template_id": template_id,
                "document_name": doc_name,
                "structure_analysis": structure_analysis,
                "format_rules": format_rules,
                "format_prompt": self._generate_format_prompt(format_rules),
                "demo_document": demo_document,  # 添加示范文档
                "created_time": datetime.now().isoformat(),
                "html_template": self._generate_html_template(format_rules)
            }
            
            return result
            
        except Exception as e:
            return {"error": f"格式提取失败: {str(e)}"}
    
    def save_format_template(self, format_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存格式模板到持久化存储
        
        Args:
            format_data: 格式数据，可以是完整的格式数据或包含template_name和template_data的结构
            
        Returns:
            保存结果
        """
        try:
            # 支持两种参数格式：
            # 1. 完整的格式数据对象
            # 2. 包含template_name和template_data的结构
            
            if "template_name" in format_data and "template_data" in format_data:
                # 格式2：从template_data中提取完整数据
                template_name = format_data.get("template_name", "")
                template_data = format_data.get("template_data", {})
                
                # 如果template_data中没有template_id，生成一个
                if "template_id" not in template_data:
                    template_data["template_id"] = self._generate_template_id(template_name, {})
                
                # 如果template_data中没有document_name，使用template_name
                if "document_name" not in template_data:
                    template_data["document_name"] = template_name
                
                format_data = template_data
            
            # 确保有template_id
            template_id = format_data.get("template_id")
            if not template_id:
                template_id = self._generate_template_id(format_data.get("document_name", "未命名模板"), {})
                format_data["template_id"] = template_id
            
            # 确保有document_name
            if "document_name" not in format_data:
                format_data["document_name"] = "未命名模板"
            
            # 保存到JSON文件
            template_file = os.path.join(self.storage_path, f"{template_id}.json")
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(format_data, f, ensure_ascii=False, indent=2)
            
            # 更新模板索引
            self._update_template_index(template_id, format_data)
            
            return {
                "success": True,
                "template_id": template_id,
                "template_name": format_data.get("document_name", "未命名模板"),
                "saved_path": template_file
            }
            
        except Exception as e:
            return {"error": f"保存格式模板失败: {str(e)}"}
    
    def load_format_template(self, template_id: str) -> Dict[str, Any]:
        """
        加载格式模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            格式模板数据
        """
        try:
            template_file = os.path.join(self.storage_path, f"{template_id}.json")
            if not os.path.exists(template_file):
                return {"error": f"模板不存在: {template_id}"}
            
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            return template_data
            
        except Exception as e:
            return {"error": f"加载格式模板失败: {str(e)}"}
    
    def list_format_templates(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的格式模板
        
        Returns:
            模板列表
        """
        try:
            index_file = os.path.join(self.storage_path, "template_index.json")
            if not os.path.exists(index_file):
                return []
            
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            return index_data.get("templates", [])
            
        except Exception as e:
            print(f"加载模板索引失败: {str(e)}")
            return []
    
    def align_document_format(self, source_content: str, target_template_id: str) -> Dict[str, Any]:
        """
        将源文档格式对齐到目标模板
        
        Args:
            source_content: 源文档内容
            target_template_id: 目标格式模板ID
            
        Returns:
            格式对齐结果
        """
        try:
            # 加载目标格式模板
            template_data = self.load_format_template(target_template_id)
            if "error" in template_data:
                return template_data
            
            # 获取格式提示词
            format_rules = template_data.get("format_rules", {})
            format_prompt = self._generate_format_prompt(format_rules)
            
            # 生成示范文档
            demo_document = self.generate_format_demo_document(format_rules)
            
            # 构建完整的LLM提示词
            full_prompt = self._build_alignment_prompt(
                source_content, 
                format_prompt, 
                demo_document,
                template_data.get("document_name", "目标格式")
            )
            
            # 调用LLM进行格式对齐
            aligned_content = self._call_llm_for_alignment(full_prompt)
            
            # 生成HTML输出
            html_output = self._generate_formatted_html(aligned_content, template_data)
            
            return {
                "success": True,
                "aligned_content": aligned_content,
                "template_used": template_data.get("document_name", "未知模板"),
                "format_prompt": format_prompt,
                "demo_document": demo_document,
                "html_output": html_output,
                "llm_prompt_used": full_prompt  # 添加使用的提示词用于调试
            }
            
        except Exception as e:
            return {"error": f"格式对齐失败: {str(e)}"}
    
    def _build_alignment_prompt(self, source_content: str, format_prompt: str, 
                               demo_document: str, template_name: str) -> str:
        """构建完整的格式对齐提示词"""
        
        prompt_parts = [
            "# 文档格式对齐任务",
            "",
            "## 任务说明",
            f"请将以下源文档的格式对齐到目标格式模板：{template_name}",
            "",
            "## 源文档内容",
            "```",
            source_content,
            "```",
            "",
            "## 目标格式要求",
            format_prompt,
            "",
            "## 格式示范文档",
            "以下是目标格式的示范文档，展示了所有格式要素：",
            "```",
            demo_document,
            "```",
            "",
            "## 对齐要求",
            "1. 保持源文档的核心内容和逻辑结构不变",
            "2. 严格按照目标格式要求调整文档格式",
            "3. 确保标题层级、段落格式、列表样式等完全符合示范文档",
            "4. 输出格式化的文本内容（不需要HTML标签）",
            "",
            "## 输出格式",
            "请直接输出对齐后的文档内容，不需要额外的说明或标记。",
            "",
            "对齐后的文档内容："
        ]
        
        return "\n".join(prompt_parts)
    
    def _call_llm_for_alignment(self, prompt: str) -> str:
        """调用LLM进行格式对齐"""
        try:
            # 优先使用星火X1客户端
            if self.spark_x1_client:
                print(f"🤖 使用星火X1进行格式对齐...")
                print(f"📝 提示词长度: {len(prompt)} 字符")

                # 提取指令和内容
                instruction, content = self._extract_instruction_and_content(prompt)

                response = self.spark_x1_client.format_text(
                    instruction=instruction,
                    content=content,
                    temperature=0.3,  # 低温度确保格式一致性
                    max_tokens=4000
                )

                print(f"✅ 星火X1响应长度: {len(response)} 字符")
                return self._clean_llm_response(response)

            # 回退到原有LLM客户端
            llm_client = self._get_llm_client()

            if llm_client is None:
                # 如果没有LLM客户端，使用模拟对齐
                return self._mock_alignment(prompt)

            # 调用LLM
            print(f"🤖 调用传统LLM进行格式对齐...")
            print(f"📝 提示词长度: {len(prompt)} 字符")

            response = llm_client.generate(
                prompt,
                temperature=0.3,  # 低温度确保格式一致性
                max_tokens=4000
            )

            print(f"✅ LLM响应长度: {len(response)} 字符")

            # 清理响应内容
            cleaned_response = self._clean_llm_response(response)

            return cleaned_response

        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            # 回退到模拟对齐
            return self._mock_alignment(prompt)

    def _extract_instruction_and_content(self, prompt: str) -> Tuple[str, str]:
        """
        从完整提示词中提取指令和内容

        Args:
            prompt: 完整的提示词

        Returns:
            (instruction, content) 元组
        """
        try:
            # 查找源文档内容部分
            content_start = prompt.find("## 源文档内容")
            if content_start == -1:
                # 如果没有找到标准格式，尝试其他模式
                content_start = prompt.find("原文内容：")
                if content_start != -1:
                    content_start = prompt.find("\n", content_start) + 1
            else:
                # 找到```后的内容
                content_start = prompt.find("```", content_start) + 3
                content_start = prompt.find("\n", content_start) + 1

            if content_start == -1:
                # 如果都没找到，返回整个prompt作为内容
                return "请格式化以下内容", prompt

            # 查找内容结束位置
            content_end = prompt.find("```", content_start)
            if content_end == -1:
                content_end = len(prompt)

            content = prompt[content_start:content_end].strip()

            # 提取指令部分（内容之前的部分）
            instruction_part = prompt[:content_start]

            # 简化指令
            instruction = "请按照以下要求格式化文档内容：\n" + instruction_part

            return instruction, content

        except Exception as e:
            print(f"⚠️ 提取指令和内容失败: {e}")
            return "请格式化以下内容", prompt

    def _get_llm_client(self):
        """获取LLM客户端"""
        try:
            # 尝试从全局变量或环境获取LLM客户端
            import os
            from src.llm_clients.xingcheng_llm import XingchengLLMClient
            from src.llm_clients.multi_llm import MultiLLMClient
            
            # 优先使用多API客户端
            try:
                return MultiLLMClient()
            except:
                pass
            
            # 回退到星程客户端
            api_key = os.getenv("XINGCHENG_API_KEY")
            api_secret = os.getenv("XINGCHENG_API_SECRET")
            
            if api_key and api_secret:
                return XingchengLLMClient(
                    api_key=api_key,
                    api_secret=api_secret,
                    model_name="x1"
                )
            
            return None
            
        except Exception as e:
            print(f"⚠️ 无法获取LLM客户端: {e}")
            return None
    
    def _clean_llm_response(self, response: str) -> str:
        """清理LLM响应内容"""
        # 移除可能的markdown标记
        lines = response.split('\n')
        cleaned_lines = []
        
        in_content = False
        for line in lines:
            # 跳过markdown代码块标记
            if line.strip().startswith('```'):
                if not in_content:
                    in_content = True
                else:
                    in_content = False
                continue
            
            # 跳过标题和说明
            if line.strip().startswith('#') or line.strip().startswith('##'):
                continue
            
            # 跳过空行（在开始部分）
            if not in_content and not line.strip():
                continue
            
            cleaned_lines.append(line)
        
        # 移除开头和结尾的空行
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def _mock_alignment(self, prompt: str) -> str:
        """模拟格式对齐（当LLM不可用时）"""
        print("🎭 使用模拟格式对齐")
        
        # 从提示词中提取源文档内容
        import re
        source_match = re.search(r'## 源文档内容\s*```\s*(.*?)\s*```', prompt, re.DOTALL)
        if source_match:
            source_content = source_match.group(1).strip()
        else:
            source_content = "无法提取源文档内容"
        
        # 简单的格式调整
        lines = source_content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 简单的格式调整
            if re.match(r'^[一二三四五六七八九十]+[、．.，,]', line):
                # 一级标题
                formatted_lines.append(f"一、{line.split('、')[1] if '、' in line else line}")
            elif re.match(r'^[1-9]\d*[、．.，,]', line):
                # 数字标题
                formatted_lines.append(f"1. {line.split('、')[1] if '、' in line else line}")
            elif re.match(r'^（[^）]+）', line):
                # 括号标题
                formatted_lines.append(f"（一）{line[1:-1]}")
            else:
                # 普通段落，添加缩进
                if not line.startswith('　　'):
                    line = f"　　{line}"
                formatted_lines.append(line)
        
        return '\n\n'.join(formatted_lines)
    
    def _analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """分析文档结构"""
        if not content or not content.strip():
            return {
                "total_lines": 0,
                "headings": [],
                "paragraphs": [],
                "lists": [],
                "special_elements": [],
                "estimated_format": {},
                "analysis_confidence": 0.0
            }

        lines = content.strip().split('\n')
        original_lines = lines[:]  # 保留原始行
        lines = [line for line in lines if line.strip()]  # 过滤空行但保留索引关系

        structure = {
            "total_lines": len(lines),
            "headings": [],
            "paragraphs": [],
            "lists": [],
            "special_elements": [],
            "estimated_format": {},
            "analysis_confidence": 0.0
        }

        if not lines:
            return structure

        confidence_scores = []

        for i, line in enumerate(lines):
            try:
                line_analysis = self._analyze_line(line, i)
                confidence_scores.append(line_analysis.get("confidence", 0.5))

                if line_analysis["type"] == "heading":
                    structure["headings"].append({
                        "level": line_analysis["level"],
                        "text": line,
                        "line_number": i,
                        "confidence": line_analysis.get("confidence", 0.5),
                        "estimated_font": line_analysis.get("font_info", {})
                    })
                elif line_analysis["type"] == "paragraph":
                    structure["paragraphs"].append({
                        "text": line,
                        "line_number": i,
                        "confidence": line_analysis.get("confidence", 0.8),
                        "estimated_font": line_analysis.get("font_info", {})
                    })
                elif line_analysis["type"] == "list":
                    structure["lists"].append({
                        "text": line,
                        "line_number": i,
                        "list_type": line_analysis.get("list_type", "bullet"),
                        "confidence": line_analysis.get("confidence", 0.7)
                    })
                elif line_analysis["type"] in ["table_row", "quote", "code", "date"]:
                    structure["special_elements"].append({
                        "type": line_analysis["type"],
                        "text": line,
                        "line_number": i,
                        "confidence": line_analysis.get("confidence", 0.6)
                    })
            except Exception as e:
                # 如果单行分析失败，将其作为普通段落处理
                structure["paragraphs"].append({
                    "text": line,
                    "line_number": i,
                    "confidence": 0.3,
                    "estimated_font": self._estimate_font_info(line, "paragraph", 0, 0),
                    "analysis_error": str(e)
                })
                confidence_scores.append(0.3)

        # 计算整体分析置信度
        structure["analysis_confidence"] = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        # 后处理：验证和调整分析结果
        structure = self._post_process_structure(structure)

        return structure

    def _post_process_structure(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """后处理文档结构分析结果"""
        # 验证标题层级的合理性
        headings = structure["headings"]
        if headings:
            # 按行号排序
            headings.sort(key=lambda x: x["line_number"])

            # 调整不合理的标题层级
            for i, heading in enumerate(headings):
                if i > 0:
                    prev_level = headings[i-1]["level"]
                    curr_level = heading["level"]

                    # 如果层级跳跃过大，调整当前层级
                    if curr_level > prev_level + 1:
                        heading["level"] = prev_level + 1
                        heading["confidence"] *= 0.8  # 降低置信度

        # 验证列表的连续性
        lists = structure["lists"]
        if len(lists) > 1:
            # 检查相邻列表项的类型一致性
            for i in range(1, len(lists)):
                if lists[i]["line_number"] == lists[i-1]["line_number"] + 1:
                    # 相邻列表项，应该保持类型一致
                    if lists[i]["list_type"] != lists[i-1]["list_type"]:
                        # 选择置信度更高的类型
                        if lists[i]["confidence"] < lists[i-1]["confidence"]:
                            lists[i]["list_type"] = lists[i-1]["list_type"]

        return structure
    
    def _analyze_line(self, line: str, line_number: int) -> Dict[str, Any]:
        """分析单行内容"""
        analysis = {"type": "paragraph", "level": 0, "confidence": 0.0}

        # 预处理：去除多余空格，但保留缩进信息
        original_line = line
        stripped_line = line.strip()
        indent_level = len(line) - len(line.lstrip())

        if not stripped_line:
            analysis["type"] = "empty"
            return analysis

        # 增强的标题检测模式
        heading_patterns = [
            # 中文数字标题
            (r'^[一二三四五六七八九十百千万]+[、．.，,]', 1, 0.9),
            (r'^第[一二三四五六七八九十百千万]+[章节部分条款项][、．.，,]?', 1, 0.95),

            # 阿拉伯数字标题
            (r'^[1-9]\d*[、．.，,]', 1, 0.9),
            (r'^[1-9]\d*\.[1-9]\d*[、．.，,]?', 2, 0.85),
            (r'^[1-9]\d*\.[1-9]\d*\.[1-9]\d*[、．.，,]?', 3, 0.8),
            (r'^[1-9]\d*\.[1-9]\d*\.[1-9]\d*\.[1-9]\d*[、．.，,]?', 4, 0.75),

            # 括号标题
            (r'^（[一二三四五六七八九十]+）', 2, 0.85),
            (r'^\([1-9]\d*\)', 2, 0.85),
            (r'^【[^】]+】', 2, 0.8),
            (r'^\[[^\]]+\]', 2, 0.75),

            # 字母标题
            (r'^[A-Z][、．.，,]', 2, 0.7),
            (r'^[a-z][、．.，,]', 3, 0.65),

            # 特殊标题格式
            (r'^附件[1-9]\d*[：:]', 1, 0.9),
            (r'^附录[A-Z]?[：:]', 1, 0.9),
        ]

        max_confidence = 0
        best_match = None

        for pattern, level, confidence in heading_patterns:
            if re.match(pattern, stripped_line):
                if confidence > max_confidence:
                    max_confidence = confidence
                    best_match = (level, confidence)

        if best_match:
            analysis["type"] = "heading"
            analysis["level"] = best_match[0]
            analysis["confidence"] = best_match[1]

            # 根据内容长度和位置调整置信度
            if len(stripped_line) > 50:  # 标题通常较短
                analysis["confidence"] *= 0.8
            if line_number == 0:  # 文档标题
                analysis["confidence"] *= 1.2
                analysis["level"] = 0  # 文档标题级别

        # 增强的列表检测
        if analysis["type"] == "paragraph":  # 只有非标题才检测列表
            list_patterns = [
                (r'^[•·▪▫◦‣⁃⁌⁍]', "bullet", 0.9),
                (r'^[-*+](?=\s)', "bullet", 0.85),
                (r'^[1-9]\d*[)）](?=\s)', "numbered", 0.9),
                (r'^[a-z][)）](?=\s)', "lettered", 0.8),
                (r'^[A-Z][)）](?=\s)', "lettered", 0.8),
                (r'^[ivxlcdm]+[)）](?=\s)', "roman", 0.75),
            ]

            for pattern, list_type, confidence in list_patterns:
                if re.match(pattern, stripped_line):
                    analysis["type"] = "list"
                    analysis["list_type"] = list_type
                    analysis["confidence"] = confidence
                    break

        # 检测特殊内容类型
        if analysis["type"] == "paragraph":
            # 表格检测
            if '|' in stripped_line or '\t' in line:
                analysis["type"] = "table_row"
                analysis["confidence"] = 0.7

            # 引用检测
            elif stripped_line.startswith('"') or stripped_line.startswith('"'):
                analysis["type"] = "quote"
                analysis["confidence"] = 0.8

            # 代码检测
            elif stripped_line.startswith('```') or stripped_line.startswith('    '):
                analysis["type"] = "code"
                analysis["confidence"] = 0.8

            # 日期检测
            elif re.match(r'^\d{4}[年-]\d{1,2}[月-]\d{1,2}[日]?', stripped_line):
                analysis["type"] = "date"
                analysis["confidence"] = 0.9

        # 估算字体信息（基于内容特征和上下文）
        analysis["font_info"] = self._estimate_font_info(
            stripped_line, analysis["type"], analysis.get("level", 0), indent_level
        )
        analysis["indent_level"] = indent_level
        analysis["original_line"] = original_line
        analysis["processed_line"] = stripped_line

        return analysis
    
    def _estimate_font_info(self, text: str, text_type: str, level: int = 0, indent_level: int = 0) -> Dict[str, Any]:
        """估算字体信息"""
        font_info = {
            "family": "宋体",
            "size": "小四",
            "weight": "normal",
            "line_height": "1.5",
            "text_align": "left",
            "margin_top": "0",
            "margin_bottom": "0",
            "text_indent": "0"
        }

        if text_type == "heading":
            font_info["family"] = "黑体"
            font_info["weight"] = "bold"
            font_info["text_align"] = "left"

            # 根据标题级别设置字体大小和间距
            if level == 0:  # 文档标题
                font_info["size"] = "二号"
                font_info["text_align"] = "center"
                font_info["margin_top"] = "0"
                font_info["margin_bottom"] = "18pt"
            elif level == 1:  # 一级标题
                font_info["size"] = "小三"
                font_info["margin_top"] = "12pt"
                font_info["margin_bottom"] = "6pt"
            elif level == 2:  # 二级标题
                font_info["size"] = "四号"
                font_info["margin_top"] = "6pt"
                font_info["margin_bottom"] = "3pt"
            elif level == 3:  # 三级标题
                font_info["size"] = "小四"
                font_info["margin_top"] = "3pt"
                font_info["margin_bottom"] = "3pt"
            else:  # 更低级标题
                font_info["size"] = "小四"
                font_info["weight"] = "normal"
                font_info["margin_top"] = "0"
                font_info["margin_bottom"] = "0"

        elif text_type == "paragraph":
            font_info["text_indent"] = "2em"  # 首行缩进
            font_info["margin_bottom"] = "0"

        elif text_type == "list":
            font_info["text_indent"] = f"{indent_level * 2}em"
            font_info["margin_bottom"] = "0"

        elif text_type == "quote":
            font_info["family"] = "楷体"
            font_info["text_indent"] = "2em"
            font_info["margin_left"] = "2em"
            font_info["margin_right"] = "2em"

        elif text_type == "code":
            font_info["family"] = "Courier New, monospace"
            font_info["size"] = "小五"
            font_info["background_color"] = "#f5f5f5"
            font_info["padding"] = "4px"

        elif text_type == "table_row":
            font_info["size"] = "小四"
            font_info["text_align"] = "center"

        elif text_type == "date":
            font_info["text_align"] = "right"
            font_info["margin_top"] = "12pt"

        # 根据文本长度调整行高
        if len(text) > 100:
            font_info["line_height"] = "1.6"
        elif len(text) < 20:
            font_info["line_height"] = "1.4"

        return font_info
    
    def _extract_format_rules(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """提取格式规则"""
        rules = {
            "heading_formats": {},
            "paragraph_format": {},
            "list_format": {},
            "general_settings": {}
        }
        
        # 分析标题格式 - 使用统计方法
        heading_levels = {}
        for heading in structure["headings"]:
            level = heading["level"]
            confidence = heading.get("confidence", 0.5)

            if level not in heading_levels:
                heading_levels[level] = []

            # 只考虑高置信度的标题
            if confidence > 0.7:
                heading_levels[level].append(heading["estimated_font"])

        for level, fonts in heading_levels.items():
            if not fonts:
                continue

            # 统计最常见的格式属性
            font_families = [f.get("family", "黑体") for f in fonts]
            font_sizes = [f.get("size", "小四") for f in fonts]

            # 取众数
            common_family = max(set(font_families), key=font_families.count) if font_families else "黑体"
            common_size = max(set(font_sizes), key=font_sizes.count) if font_sizes else "小四"

            # 合并所有属性
            merged_format = {}
            for font in fonts:
                for key, value in font.items():
                    if key not in merged_format:
                        merged_format[key] = []
                    merged_format[key].append(value)

            # 取每个属性的众数或平均值
            final_format = {
                "font_family": common_family,
                "font_size": common_size,
                "font_weight": "bold",
                "line_height": "1.5"
            }

            # 处理其他属性
            for key, values in merged_format.items():
                if key not in final_format:
                    if isinstance(values[0], str):
                        final_format[key] = max(set(values), key=values.count)
                    else:
                        try:
                            final_format[key] = sum(values) / len(values)
                        except:
                            final_format[key] = values[0]

            rules["heading_formats"][f"level_{level}"] = final_format

        # 分析正文格式
        if structure["paragraphs"]:
            para_fonts = [p["estimated_font"] for p in structure["paragraphs"]]

            # 统计正文格式
            families = [f.get("family", "宋体") for f in para_fonts]
            sizes = [f.get("size", "小四") for f in para_fonts]

            rules["paragraph_format"] = {
                "font_family": max(set(families), key=families.count) if families else "宋体",
                "font_size": max(set(sizes), key=sizes.count) if sizes else "小四",
                "text_align": "left",
                "text_indent": "2em",
                "line_height": "1.5",
                "margin_bottom": "0"
            }
        else:
            rules["paragraph_format"] = {
                "font_family": "宋体",
                "font_size": "小四",
                "text_align": "left",
                "text_indent": "2em",
                "line_height": "1.5",
                "margin_bottom": "0"
            }

        # 分析列表格式
        if structure["lists"]:
            list_types = [l.get("list_type", "bullet") for l in structure["lists"]]
            common_list_type = max(set(list_types), key=list_types.count) if list_types else "bullet"

            rules["list_format"] = {
                "list_type": common_list_type,
                "font_family": "宋体",
                "font_size": "小四",
                "line_height": "1.5",
                "margin_left": "2em"
            }
        else:
            rules["list_format"] = {
                "list_type": "bullet",
                "font_family": "宋体",
                "font_size": "小四",
                "line_height": "1.5",
                "margin_left": "2em"
            }
        
        return rules
    
    def _generate_format_prompt(self, format_rules: Dict[str, Any]) -> str:
        """生成格式提示词"""
        # 生成HTML格式模板
        html_template = self._generate_html_template(format_rules)
        
        prompt_parts = [
            "请把文章的内容以HTML格式保存，HTML格式具体要求如下：",
            f"<格式HTML>{html_template}</格式HTML>",
            "",
            "并支持DOCX文档下载的链接。用Html的格式输出，需要有能直接下载word文档的功能（不要调用doc JS库）。"
        ]
        
        return "\n".join(prompt_parts)
    
    def generate_format_demo_document(self, format_rules: Dict[str, Any]) -> str:
        """
        生成格式示范文档，展示所有格式要素
        
        Args:
            format_rules: 格式规则
            
        Returns:
            示范文档内容
        """
        demo_parts = []
        
        # 添加文档标题
        demo_parts.append("格式示范文档")
        demo_parts.append("")
        
        # 添加各级标题示例
        heading_formats = format_rules.get("heading_formats", {})
        for level_key, format_info in heading_formats.items():
            level_num = level_key.split("_")[1]
            if level_num == "1":
                demo_parts.append("一、一级标题示例")
            elif level_num == "2":
                demo_parts.append("（一）二级标题示例")
            elif level_num == "3":
                demo_parts.append("1. 三级标题示例")
            else:
                demo_parts.append(f"{level_num}. {level_num}级标题示例")
            
            # 添加该标题下的示例段落
            para_format = format_rules.get("paragraph_format", {})
            font_family = para_format.get("font_family", "宋体")
            font_size = para_format.get("font_size", "小四")
            demo_parts.append(f"　　这是{font_size}{font_family}的正文段落示例，展示正文格式。")
            demo_parts.append("")
        
        # 如果没有标题格式，添加默认正文示例
        if not heading_formats:
            para_format = format_rules.get("paragraph_format", {})
            font_family = para_format.get("font_family", "宋体")
            font_size = para_format.get("font_size", "小四")
            demo_parts.append(f"这是{font_size}{font_family}的正文段落示例，展示正文格式。")
            demo_parts.append("")
        
        # 添加列表示例
        list_format = format_rules.get("list_format", {})
        list_type = list_format.get("list_type", "bullet")
        if list_type == "numbered":
            demo_parts.append("列表示例：")
            demo_parts.append("1. 第一个列表项")
            demo_parts.append("2. 第二个列表项")
            demo_parts.append("3. 第三个列表项")
        else:
            demo_parts.append("列表示例：")
            demo_parts.append("• 第一个列表项")
            demo_parts.append("• 第二个列表项")
            demo_parts.append("• 第三个列表项")
        
        demo_parts.append("")
        
        # 添加表格示例
        demo_parts.append("表格示例：")
        demo_parts.append("| 列标题1 | 列标题2 | 列标题3 |")
        demo_parts.append("|---------|---------|---------|")
        demo_parts.append("| 数据1   | 数据2   | 数据3   |")
        demo_parts.append("| 数据4   | 数据5   | 数据6   |")
        demo_parts.append("")
        
        # 添加格式说明
        demo_parts.append("格式说明：")
        demo_parts.append("• 标题：使用黑体字体，不同级别使用不同字号")
        demo_parts.append("• 正文：使用宋体字体，首行缩进两个字符")
        demo_parts.append("• 列表：使用项目符号或数字编号")
        demo_parts.append("• 表格：使用标准表格格式")
        
        return "\n".join(demo_parts)
    
    def _generate_template_id(self, document_name: str, format_rules: Dict[str, Any]) -> str:
        """生成模板ID"""
        # 规范化输入
        normalized_name = document_name.strip().lower()
        
        # 排序格式规则以确保一致性
        sorted_rules = json.dumps(format_rules, sort_keys=True, ensure_ascii=False)
        
        # 生成内容哈希
        content = f"{normalized_name}_{sorted_rules}"
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # 添加时间戳前缀以确保唯一性
        timestamp = str(int(time.time()))[-8:]  # 取后8位时间戳
        
        # 生成最终ID
        template_id = f"template_{timestamp}_{content_hash[:12]}"
        
        return template_id
    
    def _generate_html_template(self, format_rules: Dict[str, Any]) -> str:
        """生成HTML模板"""
        css_styles = []
        
        # 标题样式
        heading_formats = format_rules.get("heading_formats", {})
        for level_key, format_info in heading_formats.items():
            level_num = level_key.split("_")[1]
            css_styles.append(f"""
            h{level_num} {{
                font-family: '{format_info.get("font_family", "黑体")}';
                font-size: {self._convert_font_size(format_info.get("font_size", "小四"))};
                font-weight: bold;
                line-height: {format_info.get("line_height", "1.5")};
                margin-top: 0;
                margin-bottom: 0;
            }}""")
        
        # 正文样式
        para_format = format_rules.get("paragraph_format", {})
        css_styles.append(f"""
        p {{
            font-family: '{para_format.get("font_family", "宋体")}';
            font-size: {self._convert_font_size(para_format.get("font_size", "小四"))};
            text-align: {para_format.get("text_align", "left")};
            text-indent: 2em;
            line-height: {para_format.get("line_height", "1.5")};
        }}""")
        
        return f"<style>{''.join(css_styles)}</style>"
    
    def _convert_font_size(self, chinese_size: str) -> str:
        """转换中文字号为CSS大小"""
        size_mapping = {
            "初号": "42pt", "小初": "36pt", "一号": "26pt", "小一": "24pt",
            "二号": "22pt", "小二": "18pt", "三号": "16pt", "小三": "15pt",
            "四号": "14pt", "小四": "12pt", "五号": "10.5pt", "小五": "9pt"
        }
        return size_mapping.get(chinese_size, "12pt")
    
    def _update_template_index(self, template_id: str, template_data: Dict[str, Any]):
        """更新模板索引"""
        index_file = os.path.join(self.storage_path, "template_index.json")
        
        # 读取现有索引
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        else:
            index_data = {"templates": []}
        
        # 更新或添加模板信息
        template_info = {
            "template_id": template_id,
            "name": template_data.get("document_name", "未命名模板"),
            "created_time": template_data.get("created_time", datetime.now().isoformat()),
            "description": f"规范格式：{template_data.get('document_name', '未命名文档')}"
        }
        
        # 检查是否已存在
        existing_index = -1
        for i, template in enumerate(index_data["templates"]):
            if template["template_id"] == template_id:
                existing_index = i
                break
        
        if existing_index >= 0:
            index_data["templates"][existing_index] = template_info
        else:
            index_data["templates"].append(template_info)
        
        # 保存索引
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def _generate_formatted_html(self, content: str, template_data: Dict[str, Any]) -> str:
        """生成格式化的HTML"""
        html_template = template_data.get("html_template", "")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>格式化文档</title>
            {html_template}
        </head>
        <body>
            <div class="document-content">
                {self._convert_to_html(content)}
            </div>
            <script>
                function downloadAsWord() {{
                    const content = document.querySelector('.document-content').innerHTML;
                    const blob = new Blob([content], {{type: 'application/msword'}});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'formatted_document.doc';
                    a.click();
                }}
            </script>
            <button onclick="downloadAsWord()">下载Word文档</button>
        </body>
        </html>
        """
        
        return html_content
    
    def _convert_to_html(self, content: str) -> str:
        """将文本内容转换为HTML"""
        lines = content.split('\n')
        html_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 简单的HTML转换
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('# ').strip()
                html_lines.append(f"<h{level}>{text}</h{level}>")
            else:
                html_lines.append(f"<p>{line}</p>")
        
        return '\n'.join(html_lines)
