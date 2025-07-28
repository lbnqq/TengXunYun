#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星火X1大模型客户端 - 文档审查专用

@AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: document_review_spark_client
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SparkX1DocumentReviewClient:
    """星火X1大模型API客户端 - 专用于文档审查功能"""
    
    def __init__(self, api_password: str):
        """
        初始化星火X1文档审查客户端
        
        Args:
            api_password: API密码 (格式: api_key:api_secret)
        """
        self.api_password = api_password
        self.base_url = "https://spark-api-open.xf-yun.com/v2/chat/completions"
        self.model = "x1"
        logger.info("星火X1文档审查客户端初始化成功")
        
    def review_document(self, document_content: str, review_prompt: str, 
                       temperature: float = 0.3, max_tokens: int = 4096) -> Optional[Dict[str, Any]]:
        """
        文档审查API调用
        
        Args:
            document_content: 文档内容
            review_prompt: 审查提示词
            temperature: 温度参数 (文档审查建议使用较低值)
            max_tokens: 最大token数
            
        Returns:
            审查结果
        """
        try:
            # 构建完整的审查提示
            full_prompt = review_prompt.replace("[此处插入待审查的文档文本]", document_content)
            
            # 构建请求头和数据
            headers = {
                "Authorization": f"Bearer {self.api_password}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "user": f"document_reviewer_{int(time.time())}",
                "messages": [
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                "stream": False,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 发送请求
            logger.info(f"发送文档审查请求，文档长度: {len(document_content)} 字符")
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60  # 文档审查可能需要更长时间
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    # 解析审查结果
                    choices = result.get("choices", [])
                    if choices and "message" in choices[0]:
                        review_content = choices[0]["message"]["content"]
                        logger.info("文档审查完成")
                        return {
                            "success": True,
                            "review_content": review_content,
                            "document_length": len(document_content),
                            "review_time": time.time()
                        }
                    else:
                        logger.warning("星火X1 API返回格式异常")
                        return {
                            "success": False,
                            "error": "API返回格式异常"
                        }
                else:
                    error_msg = result.get('message', '未知错误')
                    logger.error(f"星火X1 API返回错误: {error_msg}")
                    return {
                        "success": False,
                        "error": f"API错误: {error_msg}"
                    }
            else:
                logger.error(f"HTTP请求失败: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP请求失败: {response.status_code}"
                }
            
        except requests.exceptions.Timeout:
            logger.error("星火X1 API请求超时")
            return {
                "success": False,
                "error": "API请求超时，请稍后重试"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"星火X1 API请求失败: {e}")
            return {
                "success": False,
                "error": f"API请求失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"星火X1 API调用异常: {e}")
            return {
                "success": False,
                "error": f"系统异常: {str(e)}"
            }
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        test_prompt = "请简单回复'连接测试成功'"
        result = self.review_document("测试文档", test_prompt, temperature=0.1, max_tokens=50)
        return result and result.get("success", False)
    
    def chunk_document(self, document_content: str, max_chunk_size: int = 2000) -> list:
        """
        智能分块长文档
        
        Args:
            document_content: 文档内容
            max_chunk_size: 最大分块大小（字符数）
            
        Returns:
            分块后的文档列表
        """
        if len(document_content) <= max_chunk_size:
            return [document_content]
        
        chunks = []
        current_chunk = ""
        
        # 按段落分割
        paragraphs = document_content.split('\n\n')
        
        for paragraph in paragraphs:
            # 如果当前段落加上现有块超过限制，保存当前块
            if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"文档分块完成，共 {len(chunks)} 个块")
        return chunks
