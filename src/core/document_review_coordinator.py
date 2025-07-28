#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档审查协调器

@AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: document_review_coordinator
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

# 导入文档审查专用的星火X1客户端
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from llm_clients.spark_x1_review_client import SparkX1DocumentReviewClient

logger = logging.getLogger(__name__)

class DocumentReviewCoordinator:
    """文档审查协调器 - 管理文档审查的完整流程"""
    
    def __init__(self, api_password: str):
        """
        初始化文档审查协调器
        
        Args:
            api_password: 星火X1 API密码
        """
        self.spark_client = SparkX1DocumentReviewClient(api_password)
        self.review_templates = self._load_review_templates()
        logger.info("文档审查协调器初始化成功")
    
    def _load_review_templates(self) -> Dict[str, str]:
        """加载审查模板"""
        templates = {
            "keyword_review": """
你是一位专业的文档关键词分析专家，请对以下文档进行关键词审查分析。

**审查重点：**
1. **关键词识别：** 识别文档中的核心关键词和主题词
2. **关键词密度：** 分析关键词的分布和密度是否合理
3. **关键词相关性：** 评估关键词与文档主题的相关性
4. **缺失关键词：** 识别可能缺失的重要关键词

**输出格式要求：**
请以Markdown格式输出，包含：
- **核心关键词：** 列出3-5个最重要的关键词
- **关键词分析：** 分析关键词使用情况
- **建议：** 提供关键词优化建议
- **评分：** 给出关键词使用评分（1-10分）

---
**请开始审查以下文档内容：**

[此处插入待审查的文档文本]
""",
            
            "date_review": """
你是一位专业的文档日期审查专家，请对以下文档进行日期相关的审查。

**审查重点：**
1. **日期格式：** 检查日期格式是否统一、规范
2. **日期逻辑：** 验证日期的逻辑性和合理性
3. **时间一致性：** 检查文档中各个日期的一致性
4. **截止日期：** 检查截止日期是否合理

**输出格式要求：**
请以Markdown格式输出，包含：
- **发现的日期：** 列出文档中所有日期
- **格式问题：** 指出日期格式不统一的地方
- **逻辑问题：** 指出日期逻辑不合理的地方
- **建议：** 提供日期规范化建议

---
**请开始审查以下文档内容：**

[此处插入待审查的文档文本]
""",
            
            "sensitive_info_review": """
你是一位专业的信息安全审查员，请对以下文档进行敏感信息检测。

**检测重点：**
1. **个人信息：** 姓名、身份证号、电话、邮箱、地址等
2. **财务信息：** 银行账号、金额、财务数据等
3. **机密信息：** 内部文件、商业机密、技术秘密等
4. **不当内容：** 不当言论、违规内容等

**输出格式要求：**
请以Markdown格式输出，包含：
- **敏感信息类型：** 发现的敏感信息类别
- **具体位置：** 在文档中的位置
- **风险等级：** 低/中/高
- **处理建议：** 如何处理这些敏感信息

---
**请开始审查以下文档内容：**

[此处插入待审查的文档文本]
""",
            
            "professional_review": """
你是一位资深的专业文档审查专家，请对以下文档进行专业性评估。

**评估维度：**
1. **专业术语：** 专业术语使用是否准确、恰当
2. **表达规范：** 语言表达是否符合专业标准
3. **逻辑结构：** 文档结构是否清晰、逻辑性强
4. **内容深度：** 内容是否具有足够的专业深度

**输出格式要求：**
请以Markdown格式输出，包含：
- **专业性评分：** 给出1-10分的专业性评分
- **优点分析：** 指出文档的专业性优点
- **问题识别：** 指出专业性不足的地方
- **改进建议：** 提供专业性提升建议

---
**请开始审查以下文档内容：**

[此处插入待审查的文档文text]
"""
        }
        return templates
    
    def review_document(self, document_content: str, review_type: str = "keyword_review", 
                       custom_prompt: str = None) -> Dict[str, Any]:
        """
        执行文档审查
        
        Args:
            document_content: 文档内容
            review_type: 审查类型 (keyword_review, date_review, sensitive_info_review, professional_review)
            custom_prompt: 自定义审查提示词
            
        Returns:
            审查结果
        """
        try:
            # 选择审查提示词
            if custom_prompt:
                review_prompt = custom_prompt
            elif review_type in self.review_templates:
                review_prompt = self.review_templates[review_type]
            else:
                return {
                    "success": False,
                    "error": f"不支持的审查类型: {review_type}"
                }
            
            # 检查文档长度，如果太长则分块处理
            if len(document_content) > 3000:
                return self._review_long_document(document_content, review_prompt)
            else:
                return self._review_single_document(document_content, review_prompt)
                
        except Exception as e:
            logger.error(f"文档审查失败: {e}")
            return {
                "success": False,
                "error": f"文档审查失败: {str(e)}"
            }
    
    def _review_single_document(self, document_content: str, review_prompt: str) -> Dict[str, Any]:
        """审查单个文档"""
        start_time = time.time()
        
        result = self.spark_client.review_document(
            document_content=document_content,
            review_prompt=review_prompt,
            temperature=0.3,
            max_tokens=4096
        )
        
        if result and result.get("success"):
            return {
                "success": True,
                "review_result": result["review_content"],
                "document_length": len(document_content),
                "processing_time": time.time() - start_time,
                "review_type": "single_document"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "未知错误") if result else "API调用失败"
            }
    
    def _review_long_document(self, document_content: str, review_prompt: str) -> Dict[str, Any]:
        """审查长文档（分块处理）"""
        start_time = time.time()
        
        # 分块
        chunks = self.spark_client.chunk_document(document_content, max_chunk_size=2500)
        chunk_results = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"审查文档块 {i+1}/{len(chunks)}")
            
            result = self.spark_client.review_document(
                document_content=chunk,
                review_prompt=review_prompt,
                temperature=0.3,
                max_tokens=4096
            )
            
            if result and result.get("success"):
                chunk_results.append({
                    "chunk_index": i + 1,
                    "chunk_content": chunk[:100] + "..." if len(chunk) > 100 else chunk,
                    "review_result": result["review_content"]
                })
            else:
                chunk_results.append({
                    "chunk_index": i + 1,
                    "error": result.get("error", "审查失败") if result else "API调用失败"
                })
        
        # 合并结果
        combined_result = self._combine_chunk_results(chunk_results)
        
        return {
            "success": True,
            "review_result": combined_result,
            "document_length": len(document_content),
            "processing_time": time.time() - start_time,
            "review_type": "chunked_document",
            "chunks_count": len(chunks),
            "chunk_details": chunk_results
        }
    
    def _combine_chunk_results(self, chunk_results: List[Dict]) -> str:
        """合并分块审查结果"""
        combined = "# 文档审查结果（分块处理）\n\n"
        
        for chunk_result in chunk_results:
            chunk_index = chunk_result["chunk_index"]
            if "error" in chunk_result:
                combined += f"## 文档块 {chunk_index} - 审查失败\n"
                combined += f"错误信息：{chunk_result['error']}\n\n"
            else:
                combined += f"## 文档块 {chunk_index} 审查结果\n"
                combined += chunk_result["review_result"] + "\n\n"
        
        return combined
    
    def get_available_review_types(self) -> List[Dict[str, str]]:
        """获取可用的审查类型"""
        return [
            {"id": "keyword_review", "name": "关键词审查", "description": "分析文档关键词使用情况"},
            {"id": "date_review", "name": "日期审查", "description": "检查文档中的日期格式和逻辑"},
            {"id": "sensitive_info_review", "name": "敏感信息检测", "description": "检测文档中的敏感信息"},
            {"id": "professional_review", "name": "专业性评估", "description": "评估文档的专业性水平"}
        ]
