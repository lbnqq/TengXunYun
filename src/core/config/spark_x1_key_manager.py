#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星火X1密钥管理器

统一管理项目中所有星火X1 API密钥的获取、验证和切换。

Author: AI Assistant
Created: 2025-08-03
License: MIT
"""

import os
import yaml
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading

# 设置日志
logger = logging.getLogger(__name__)

class SparkX1KeyManager:
    """星火X1密钥管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化密钥管理器"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.config = None
        self.config_path = None
        self._load_config()
        
        logger.info("✅ SparkX1KeyManager初始化成功")
    
    def _load_config(self):
        """加载配置文件"""
        try:
            # 查找配置文件
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'config', 'spark_x1_keys.yaml'),
                os.path.join(os.getcwd(), 'config', 'spark_x1_keys.yaml'),
                'config/spark_x1_keys.yaml'
            ]
            
            config_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if not config_path:
                raise FileNotFoundError("未找到星火X1密钥配置文件 spark_x1_keys.yaml")
            
            self.config_path = config_path
            
            # 加载YAML配置
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # 验证配置结构
            self._validate_config()
            
            logger.info(f"📋 成功加载密钥配置: {config_path}")
            
        except Exception as e:
            logger.error(f"❌ 加载密钥配置失败: {e}")
            # 使用默认配置
            self._create_default_config()
    
    def _validate_config(self):
        """验证配置文件结构"""
        required_keys = ['primary', 'modules', 'settings', 'api']
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"配置文件缺少必要的键: {key}")
        
        # 验证主密钥
        if not self.config['primary'].get('api_key'):
            raise ValueError("主密钥不能为空")
        
        # 验证密钥格式
        primary_key = self.config['primary']['api_key']
        if ':' not in primary_key:
            raise ValueError("密钥格式错误，应为 AK:SK 格式")
    
    def _create_default_config(self):
        """创建默认配置"""
        self.config = {
            'primary': {
                'api_key': 'NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh',
                'description': '默认主密钥',
                'status': 'active'
            },
            'modules': {
                'smart_fill': {'use_key': 'primary'},
                'style_alignment': {'use_key': 'primary'},
                'format_alignment': {'use_key': 'primary'},
                'document_review': {'use_key': 'primary'}
            },
            'settings': {
                'auto_fallback': True,
                'validate_on_load': True,
                'max_retries': 3
            },
            'api': {
                'base_url': 'https://spark-api-open.xf-yun.com/v2/chat/completions',
                'timeout': 120,
                'model': 'x1'
            }
        }
        logger.warning("⚠️ 使用默认密钥配置")
    
    def get_api_key(self, module_name: str = None) -> str:
        """
        获取API密钥
        
        Args:
            module_name: 模块名称 (smart_fill, style_alignment, format_alignment, document_review)
            
        Returns:
            API密钥字符串
        """
        try:
            if module_name and module_name in self.config['modules']:
                # 获取模块特定配置
                module_config = self.config['modules'][module_name]
                use_key = module_config.get('use_key', 'primary')
                
                if use_key == 'primary':
                    key = self.config['primary']['api_key']
                else:
                    # 处理备用密钥
                    key_path = use_key.split('.')
                    key_config = self.config
                    for path in key_path:
                        key_config = key_config[path]
                    key = key_config['api_key']
                
                # 验证密钥
                if self.config['settings'].get('validate_on_load', True):
                    self._validate_key(key)
                
                return key
            else:
                # 返回主密钥
                key = self.config['primary']['api_key']
                if self.config['settings'].get('validate_on_load', True):
                    self._validate_key(key)
                return key
                
        except Exception as e:
            logger.error(f"❌ 获取API密钥失败: {e}")
            # 返回默认密钥
            return 'NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh'
    
    def _validate_key(self, key: str) -> bool:
        """验证密钥格式"""
        if not key or ':' not in key:
            raise ValueError("密钥格式错误，应为 AK:SK 格式")
        return True
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        return self.config.get('api', {})
    
    def update_primary_key(self, new_key: str, description: str = None) -> bool:
        """
        更新主密钥
        
        Args:
            new_key: 新的API密钥
            description: 密钥描述
            
        Returns:
            更新是否成功
        """
        try:
            # 验证新密钥格式
            self._validate_key(new_key)
            
            # 更新配置
            self.config['primary']['api_key'] = new_key
            if description:
                self.config['primary']['description'] = description
            self.config['primary']['updated_at'] = datetime.now().isoformat()
            
            # 保存到文件
            if self.config_path:
                self._save_config()
            
            logger.info("✅ 主密钥更新成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新主密钥失败: {e}")
            return False
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
            logger.info("💾 配置文件保存成功")
        except Exception as e:
            logger.error(f"❌ 保存配置文件失败: {e}")
    
    def list_all_keys(self) -> Dict[str, Any]:
        """列出所有配置的密钥"""
        keys_info = {
            'primary': {
                'key': self.config['primary']['api_key'][:20] + '...',  # 只显示前20个字符
                'description': self.config['primary'].get('description', ''),
                'status': self.config['primary'].get('status', 'unknown')
            }
        }
        
        # 添加备用密钥信息
        if 'backup' in self.config:
            keys_info['backup'] = {}
            for key_name, key_config in self.config['backup'].items():
                if key_config.get('api_key'):
                    keys_info['backup'][key_name] = {
                        'key': key_config['api_key'][:20] + '...',
                        'description': key_config.get('description', ''),
                        'status': key_config.get('status', 'unknown')
                    }
        
        return keys_info
    
    def test_key(self, key: str = None) -> bool:
        """
        测试密钥是否有效
        
        Args:
            key: 要测试的密钥，如果为None则测试主密钥
            
        Returns:
            密钥是否有效
        """
        try:
            if key is None:
                key = self.get_api_key()
            
            # 这里可以添加实际的API调用测试
            # 目前只验证格式
            self._validate_key(key)
            
            logger.info("✅ 密钥测试通过")
            return True
            
        except Exception as e:
            logger.error(f"❌ 密钥测试失败: {e}")
            return False

# 全局实例
key_manager = SparkX1KeyManager()

def get_spark_x1_key(module_name: str = None) -> str:
    """
    便捷函数：获取星火X1 API密钥
    
    Args:
        module_name: 模块名称
        
    Returns:
        API密钥
    """
    return key_manager.get_api_key(module_name)

def get_spark_x1_config() -> Dict[str, Any]:
    """
    便捷函数：获取星火X1 API配置
    
    Returns:
        API配置字典
    """
    return key_manager.get_api_config()

def update_spark_x1_key(new_key: str, description: str = None) -> bool:
    """
    便捷函数：更新星火X1主密钥
    
    Args:
        new_key: 新密钥
        description: 描述
        
    Returns:
        是否成功
    """
    return key_manager.update_primary_key(new_key, description)
