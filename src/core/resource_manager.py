#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源管理统一机制
管理模板、session、文件等资源的创建、查找、清理
"""

import os
import json
import shutil
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ResourceManager:
    """资源管理器"""
    
    def __init__(self, base_path: str = "src/core/knowledge_base"):
        self.base_path = base_path
        self.template_path = os.path.join(base_path, "writing_style_templates")
        self.session_path = os.path.join(base_path, "writing_style_templates/semantic_behavior/profiles")
        self.backup_path = os.path.join(base_path, "backups")
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [self.template_path, self.session_path, self.backup_path]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def create_template(self, template_id: str, content: Dict[str, Any]) -> bool:
        """
        创建模板
        
        Args:
            template_id: 模板ID
            content: 模板内容
            
        Returns:
            bool: 是否创建成功
        """
        try:
            template_file = os.path.join(self.template_path, f"{template_id}.json")
            
            # 添加元数据
            template_data = {
                'id': template_id,
                'created_at': datetime.now().isoformat(),
                'content': content,
                'version': '1.0'
            }
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"模板创建成功: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"模板创建失败 {template_id}: {e}")
            return False
    
    def find_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        查找模板，包含回退策略
        
        Args:
            template_id: 模板ID
            
        Returns:
            Optional[Dict]: 模板数据，如果不存在返回None
        """
        # 策略1: 直接查找
        template_file = os.path.join(self.template_path, f"{template_id}.json")
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"读取模板失败 {template_id}: {e}")
        
        # 策略2: 查找相似模板
        similar_template = self._find_similar_template(template_id)
        if similar_template:
            logger.info(f"使用相似模板: {similar_template['id']}")
            return similar_template
        
        # 策略3: 使用默认模板
        default_template = self._get_default_template()
        if default_template:
            logger.info("使用默认模板")
            return default_template
        
        logger.warning(f"未找到模板: {template_id}")
        return None
    
    def _find_similar_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """查找相似模板"""
        try:
            # 获取所有模板文件
            template_files = [f for f in os.listdir(self.template_path) 
                            if f.endswith('.json')]
            
            # 简单的相似性检查（可以根据需要改进）
            for file_name in template_files:
                file_path = os.path.join(self.template_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    # 这里可以添加更复杂的相似性判断逻辑
                    if template_data.get('content', {}).get('style_type'):
                        return template_data
            
        except Exception as e:
            logger.error(f"查找相似模板失败: {e}")
        
        return None
    
    def _get_default_template(self) -> Optional[Dict[str, Any]]:
        """获取默认模板"""
        default_template = {
            'id': 'default_template',
            'created_at': datetime.now().isoformat(),
            'content': {
                'style_type': 'formal',
                'language_style': 'professional',
                'tone': 'neutral'
            },
            'version': '1.0'
        }
        return default_template
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """
        保存会话数据
        
        Args:
            session_id: 会话ID
            session_data: 会话数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            session_file = os.path.join(self.session_path, f"{session_id}.json")
            
            # 添加元数据
            session_data['session_id'] = session_id
            session_data['created_at'] = datetime.now().isoformat()
            session_data['last_updated'] = datetime.now().isoformat()
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"会话保存成功: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"会话保存失败 {session_id}: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        加载会话数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[Dict]: 会话数据
        """
        session_file = os.path.join(self.session_path, f"{session_id}.json")
        
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # 更新最后访问时间
                session_data['last_accessed'] = datetime.now().isoformat()
                self.save_session(session_id, session_data)
                
                return session_data
                
            except Exception as e:
                logger.error(f"加载会话失败 {session_id}: {e}")
        
        return None
    
    def cleanup_resources(self, session_id: str, cleanup_type: str = 'session') -> bool:
        """
        清理资源
        
        Args:
            session_id: 会话ID
            cleanup_type: 清理类型 ('session', 'template', 'all')
            
        Returns:
            bool: 是否清理成功
        """
        try:
            if cleanup_type in ['session', 'all']:
                # 清理会话文件
                session_file = os.path.join(self.session_path, f"{session_id}.json")
                if os.path.exists(session_file):
                    # 创建备份
                    backup_file = os.path.join(self.backup_path, f"{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                    shutil.copy2(session_file, backup_file)
                    
                    # 删除原文件
                    os.remove(session_file)
                    logger.info(f"会话清理成功: {session_id}")
            
            if cleanup_type in ['template', 'all']:
                # 清理相关模板（这里需要根据业务逻辑确定哪些模板需要清理）
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"资源清理失败 {session_id}: {e}")
            return False
    
    def cleanup_old_sessions(self, max_age_days: int = 7) -> int:
        """
        清理过期会话
        
        Args:
            max_age_days: 最大保留天数
            
        Returns:
            int: 清理的会话数量
        """
        cleaned_count = 0
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        
        try:
            session_files = [f for f in os.listdir(self.session_path) 
                           if f.endswith('.json')]
            
            for file_name in session_files:
                file_path = os.path.join(self.session_path, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    created_at = datetime.fromisoformat(session_data.get('created_at', '1970-01-01'))
                    
                    if created_at < cutoff_time:
                        # 创建备份
                        backup_file = os.path.join(self.backup_path, f"expired_{file_name}")
                        shutil.copy2(file_path, backup_file)
                        
                        # 删除原文件
                        os.remove(file_path)
                        cleaned_count += 1
                        logger.info(f"清理过期会话: {file_name}")
                
                except Exception as e:
                    logger.error(f"处理会话文件失败 {file_name}: {e}")
            
        except Exception as e:
            logger.error(f"清理过期会话失败: {e}")
        
        return cleaned_count
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        获取会话统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            session_files = [f for f in os.listdir(self.session_path) 
                           if f.endswith('.json')]
            
            total_sessions = len(session_files)
            total_size = sum(os.path.getsize(os.path.join(self.session_path, f)) 
                           for f in session_files)
            
            # 按日期统计
            date_stats = {}
            for file_name in session_files:
                file_path = os.path.join(self.session_path, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    created_date = session_data.get('created_at', '')[:10]
                    date_stats[created_date] = date_stats.get(created_date, 0) + 1
                
                except Exception:
                    pass
            
            return {
                'total_sessions': total_sessions,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'date_distribution': date_stats,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取会话统计失败: {e}")
            return {}
    
    def backup_resources(self, backup_name: Optional[str] = None) -> str:
        """
        备份资源
        
        Args:
            backup_name: 备份名称
            
        Returns:
            str: 备份路径
        """
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = os.path.join(self.backup_path, backup_name)
        
        try:
            # 备份模板
            template_backup = os.path.join(backup_dir, "templates")
            if os.path.exists(self.template_path):
                shutil.copytree(self.template_path, template_backup)
            
            # 备份会话
            session_backup = os.path.join(backup_dir, "sessions")
            if os.path.exists(self.session_path):
                shutil.copytree(self.session_path, session_backup)
            
            logger.info(f"资源备份成功: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            logger.error(f"资源备份失败: {e}")
            return ""
    
    def cleanup_test_resources(self, test_session_id: Optional[str] = None, cleanup_type: str = 'all') -> Dict[str, Any]:
        """
        清理测试资源
        
        Args:
            test_session_id: 测试会话ID
            cleanup_type: 清理类型 ('session', 'template', 'all')
            
        Returns:
            Dict[str, Any]: 清理结果
        """
        try:
            cleaned_items = {
                'temp_files': 0,
                'test_sessions': 0,
                'cache_files': 0,
                'upload_files': 0
            }
            
            # 清理临时文件 - 使用绝对路径
            temp_dir = 'temp'  # 相对于项目根目录
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    if filename.endswith('.tmp') or 'test_' in filename:
                        file_path = os.path.join(temp_dir, filename)
                        try:
                            os.remove(file_path)
                            cleaned_items['temp_files'] += 1
                            print(f"清理临时文件: {file_path}")
                        except Exception as e:
                            logger.error(f"清理临时文件失败 {filename}: {e}")
            
            # 清理测试会话
            if test_session_id:
                session_file = os.path.join(self.session_path, f"{test_session_id}.json")
                if os.path.exists(session_file):
                    try:
                        os.remove(session_file)
                        cleaned_items['test_sessions'] += 1
                    except Exception as e:
                        logger.error(f"清理会话文件失败: {e}")
            
            # 清理缓存文件
            cache_dir = 'cache'
            if os.path.exists(cache_dir):
                for filename in os.listdir(cache_dir):
                    if (
                        filename.endswith('.tmp') or
                        filename.startswith('test_') or
                        filename.startswith('.test_') or
                        filename.endswith('.cache')
                    ):
                        file_path = os.path.join(cache_dir, filename)
                        try:
                            os.remove(file_path)
                            cleaned_items['cache_files'] += 1
                            print(f"清理缓存文件: {file_path}")
                        except Exception as e:
                            logger.error(f"清理缓存文件失败 {filename}: {e}")
            
            # 清理上传文件（仅测试文件）
            upload_dir = 'uploads'
            if os.path.exists(upload_dir):
                for filename in os.listdir(upload_dir):
                    if filename.startswith('test_') or 'temp_' in filename:
                        file_path = os.path.join(upload_dir, filename)
                        try:
                            os.remove(file_path)
                            cleaned_items['upload_files'] += 1
                        except Exception as e:
                            logger.error(f"清理上传文件失败 {filename}: {e}")
            
            return {
                'success': True,
                'cleaned_items': cleaned_items,
                'total_cleaned': sum(cleaned_items.values())
            }
            
        except Exception as e:
            logger.error(f"清理测试资源失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# 全局实例
resource_manager = ResourceManager()


def create_template(template_id: str, content: Dict[str, Any]) -> bool:
    """便捷函数：创建模板"""
    return resource_manager.create_template(template_id, content)


def find_template(template_id: str) -> Optional[Dict[str, Any]]:
    """便捷函数：查找模板"""
    return resource_manager.find_template(template_id)


def save_session(session_id: str, session_data: Dict[str, Any]) -> bool:
    """便捷函数：保存会话"""
    return resource_manager.save_session(session_id, session_data)


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    """便捷函数：加载会话"""
    return resource_manager.load_session(session_id)


def cleanup_resources(session_id: str, cleanup_type: str = 'session') -> bool:
    """便捷函数：清理资源"""
    return resource_manager.cleanup_resources(session_id, cleanup_type) 