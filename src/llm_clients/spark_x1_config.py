#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星火X1配置管理模块

Author: AI Assistant (Claude)
Created: 2025-01-15
Last Modified: 2025-01-15
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SparkX1Config:
    """星火X1配置类"""
    
    # API配置
    api_password: str = None
    base_url: str = "https://spark-api-open.xf-yun.com/v2/chat/completions"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    
    # 模型配置
    model: str = "x1"
    temperature: float = 0.7
    max_tokens: int = 32768
    top_p: float = 0.95
    
    # 处理配置
    max_file_size: int = 10485760  # 10MB
    supported_formats: list = None
    batch_size: int = 5
    concurrent_limit: int = 3
    
    # 存储配置
    upload_path: str = "uploads/format_alignment"
    result_path: str = "results/format_alignment"
    template_path: str = "templates/format_alignment"
    cleanup_after_hours: int = 24
    
    def __post_init__(self):
        """初始化后处理"""
        if self.supported_formats is None:
            self.supported_formats = ["txt", "docx", "pdf"]

        # 从环境变量获取API密钥
        if not self.api_password:
            self.api_password = os.getenv('SPARK_X1_API_PASSWORD')

        # 如果环境变量也没有，使用默认密钥
        if not self.api_password:
            self.api_password = 'NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh'

        # 从环境变量获取其他配置
        self.base_url = os.getenv('SPARK_X1_BASE_URL', self.base_url)

        # 验证必要配置
        if not self.api_password:
            raise ValueError("缺少星火X1 API密钥配置")

        if ':' not in self.api_password:
            raise ValueError("API密钥格式错误，应为 AK:SK 格式")
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SparkX1Config':
        """从字典创建配置对象"""
        return cls(**config_dict)
    
    @classmethod
    def from_json_file(cls, file_path: str) -> 'SparkX1Config':
        """从JSON文件加载配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            return cls.from_dict(config_dict)
        except FileNotFoundError:
            # 如果配置文件不存在，使用默认配置
            return cls()
        except Exception as e:
            raise ValueError(f"加载配置文件失败: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'api': {
                'base_url': self.base_url,
                'timeout': self.timeout,
                'max_retries': self.max_retries,
                'retry_delay': self.retry_delay
            },
            'model': {
                'name': self.model,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens,
                'top_p': self.top_p
            },
            'processing': {
                'max_file_size': self.max_file_size,
                'supported_formats': self.supported_formats,
                'batch_size': self.batch_size,
                'concurrent_limit': self.concurrent_limit
            },
            'storage': {
                'upload_path': self.upload_path,
                'result_path': self.result_path,
                'template_path': self.template_path,
                'cleanup_after_hours': self.cleanup_after_hours
            }
        }
    
    def save_to_json_file(self, file_path: str) -> None:
        """保存配置到JSON文件"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"保存配置文件失败: {str(e)}")
    
    def validate(self) -> bool:
        """验证配置有效性"""
        try:
            # 验证API密钥
            if not self.api_password or ':' not in self.api_password:
                return False
            
            # 验证URL
            if not self.base_url or not self.base_url.startswith('http'):
                return False
            
            # 验证数值范围
            if self.temperature < 0 or self.temperature > 2:
                return False
            
            if self.max_tokens <= 0:
                return False
            
            if self.top_p < 0 or self.top_p > 1:
                return False
            
            return True
            
        except Exception:
            return False

# 默认配置实例
DEFAULT_CONFIG = SparkX1Config()

def get_config(config_path: Optional[str] = None) -> SparkX1Config:
    """
    获取配置实例
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认配置
        
    Returns:
        配置实例
    """
    if config_path and os.path.exists(config_path):
        return SparkX1Config.from_json_file(config_path)
    else:
        return SparkX1Config()

def create_default_config_file(file_path: str) -> None:
    """
    创建默认配置文件
    
    Args:
        file_path: 配置文件路径
    """
    config = SparkX1Config()
    config.save_to_json_file(file_path)
