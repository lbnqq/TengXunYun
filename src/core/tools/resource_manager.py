"""
统一资源管理器
管理项目中的各种资源，包括模板、会话、文件等
"""

import os
import json
import uuid
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class SessionData:
    """会话数据结构"""
    session_id: str
    session_type: str
    created_time: str
    last_updated: str
    data: Dict[str, Any]
    status: str = "active"


@dataclass
class TemplateData:
    """模板数据结构"""
    template_id: str
    template_name: str
    template_type: str
    created_time: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]


class ResourceManager:
    """
    统一资源管理器
    
    功能：
    1. 会话管理：创建、更新、清理会话
    2. 模板管理：创建、加载、查找模板
    3. 文件管理：缓存、清理文件
    4. 资源监控：监控资源使用情况
    """
    
    def __init__(self, base_path: str = "src/core/knowledge_base"):
        self.base_path = base_path
        self.sessions: Dict[str, SessionData] = {}
        self.templates: Dict[str, TemplateData] = {}
        self.file_cache: Dict[str, bytes] = {}
        
        # 配置
        self.session_timeout = 3600  # 1小时超时
        self.cache_size_limit = 100  # 缓存文件数量限制
        self.max_session_count = 1000  # 最大会话数量
        
        # 初始化目录
        self._init_directories()
        
        # 加载现有资源
        self._load_existing_resources()
    
    def _init_directories(self):
        """初始化必要的目录"""
        directories = [
            os.path.join(self.base_path, "sessions"),
            os.path.join(self.base_path, "templates"),
            os.path.join(self.base_path, "cache"),
            os.path.join(self.base_path, "temp")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _load_existing_resources(self):
        """加载现有的资源"""
        # 加载会话
        sessions_dir = os.path.join(self.base_path, "sessions")
        if os.path.exists(sessions_dir):
            for filename in os.listdir(sessions_dir):
                if filename.endswith('.json'):
                    session_path = os.path.join(sessions_dir, filename)
                    try:
                        with open(session_path, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)
                            session = SessionData(**session_data)
                            self.sessions[session.session_id] = session
                    except Exception as e:
                        print(f"加载会话失败 {filename}: {str(e)}")
        
        # 加载模板
        templates_dir = os.path.join(self.base_path, "templates")
        if os.path.exists(templates_dir):
            for filename in os.listdir(templates_dir):
                if filename.endswith('.json'):
                    template_path = os.path.join(templates_dir, filename)
                    try:
                        with open(template_path, 'r', encoding='utf-8') as f:
                            template_data = json.load(f)
                            template = TemplateData(**template_data)
                            self.templates[template.template_id] = template
                    except Exception as e:
                        print(f"加载模板失败 {filename}: {str(e)}")
    
    # ==================== 会话管理 ====================
    
    def create_session(self, session_type: str, initial_data: Dict[str, Any]) -> str:
        """
        创建新会话
        
        Args:
            session_type: 会话类型
            initial_data: 初始数据
            
        Returns:
            会话ID
        """
        # 检查会话数量限制
        if len(self.sessions) >= self.max_session_count:
            self._cleanup_expired_sessions()
            if len(self.sessions) >= self.max_session_count:
                # 强制清理最旧的会话
                self._force_cleanup_old_sessions()
        
        session_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        session = SessionData(
            session_id=session_id,
            session_type=session_type,
            created_time=current_time,
            last_updated=current_time,
            data=initial_data,
            status="active"
        )
        
        self.sessions[session_id] = session
        
        # 保存到文件
        self._save_session_to_file(session)
        
        return session_id
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新会话数据
        
        Args:
            session_id: 会话ID
            updates: 更新数据
            
        Returns:
            是否更新成功
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session.data.update(updates)
        session.last_updated = datetime.now().isoformat()
        
        # 保存到文件
        self._save_session_to_file(session)
        
        return True
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        获取会话数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话数据或None
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # 检查是否过期
        if self._is_session_expired(session):
            self.cleanup_session(session_id)
            return None
        
        return session
    
    def cleanup_session(self, session_id: str) -> bool:
        """
        清理指定会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否清理成功
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            # 删除文件
            session_file = os.path.join(self.base_path, "sessions", f"{session_id}.json")
            if os.path.exists(session_file):
                try:
                    os.remove(session_file)
                except Exception as e:
                    print(f"删除会话文件失败: {str(e)}")
            
            # 从内存中移除
            del self.sessions[session_id]
            return True
        
        return False
    
    def _is_session_expired(self, session: SessionData) -> bool:
        """检查会话是否过期"""
        try:
            last_updated = datetime.fromisoformat(session.last_updated)
            current_time = datetime.now()
            return (current_time - last_updated).total_seconds() > self.session_timeout
        except Exception:
            return True
    
    def _save_session_to_file(self, session: SessionData):
        """保存会话到文件"""
        try:
            session_file = os.path.join(self.base_path, "sessions", f"{session.session_id}.json")
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(session), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存会话文件失败: {str(e)}")
    
    def _cleanup_expired_sessions(self):
        """清理过期会话"""
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.cleanup_session(session_id)
    
    def _force_cleanup_old_sessions(self):
        """强制清理最旧的会话"""
        # 按创建时间排序
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda x: x[1].created_time
        )
        
        # 删除最旧的20%会话
        cleanup_count = max(1, len(sorted_sessions) // 5)
        
        for i in range(cleanup_count):
            session_id = sorted_sessions[i][0]
            self.cleanup_session(session_id)
    
    # ==================== 模板管理 ====================
    
    def create_template(self, template_name: str, template_type: str, 
                       template_data: Dict[str, Any], metadata: Dict[str, Any] = None) -> str:
        """
        创建新模板
        
        Args:
            template_name: 模板名称
            template_type: 模板类型
            template_data: 模板数据
            metadata: 元数据
            
        Returns:
            模板ID
        """
        template_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        template = TemplateData(
            template_id=template_id,
            template_name=template_name,
            template_type=template_type,
            created_time=current_time,
            data=template_data,
            metadata=metadata or {}
        )
        
        self.templates[template_id] = template
        
        # 保存到文件
        self._save_template_to_file(template)
        
        return template_id
    
    def get_template(self, template_id: str) -> Optional[TemplateData]:
        """
        获取模板数据
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板数据或None
        """
        return self.templates.get(template_id)
    
    def find_similar_template(self, template_id: str, template_type: str = None) -> Optional[TemplateData]:
        """
        查找相似模板
        
        Args:
            template_id: 目标模板ID
            template_type: 模板类型（可选）
            
        Returns:
            相似模板或None
        """
        # 基于ID前缀查找
        template_prefix = template_id[:8] if len(template_id) >= 8 else template_id
        
        for template in self.templates.values():
            current_id = template.template_id
            if current_id.startswith(template_prefix):
                if template_type is None or template.template_type == template_type:
                    return template
        
        # 如果没有找到相似ID，返回第一个同类型模板
        if template_type:
            for template in self.templates.values():
                if template.template_type == template_type:
                    return template
        
        # 返回第一个可用模板
        if self.templates:
            return next(iter(self.templates.values()))
        
        return None
    
    def list_templates(self, template_type: str = None) -> List[TemplateData]:
        """
        列出模板
        
        Args:
            template_type: 模板类型（可选）
            
        Returns:
            模板列表
        """
        if template_type:
            return [t for t in self.templates.values() if t.template_type == template_type]
        else:
            return list(self.templates.values())
    
    def _save_template_to_file(self, template: TemplateData):
        """保存模板到文件"""
        try:
            template_file = os.path.join(self.base_path, "templates", f"{template.template_id}.json")
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(template), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存模板文件失败: {str(e)}")
    
    # ==================== 文件管理 ====================
    
    def cache_file(self, file_path: str, content: bytes) -> str:
        """
        缓存文件内容
        
        Args:
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            缓存ID
        """
        cache_id = str(uuid.uuid4())
        
        # 检查缓存大小限制
        if len(self.file_cache) >= self.cache_size_limit:
            self._cleanup_old_cache()
        
        self.file_cache[cache_id] = content
        
        return cache_id
    
    def get_cached_file(self, cache_id: str) -> Optional[bytes]:
        """
        获取缓存的文件内容
        
        Args:
            cache_id: 缓存ID
            
        Returns:
            文件内容或None
        """
        return self.file_cache.get(cache_id)
    
    def clear_cache(self):
        """清空文件缓存"""
        self.file_cache.clear()
    
    def _cleanup_old_cache(self):
        """清理旧的缓存项"""
        # 简单的清理策略：删除最旧的20%缓存项
        cleanup_count = max(1, len(self.file_cache) // 5)
        
        for i in range(cleanup_count):
            if self.file_cache:
                oldest_key = next(iter(self.file_cache))
                del self.file_cache[oldest_key]
    
    # ==================== 资源监控 ====================
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """
        获取资源使用统计
        
        Returns:
            资源统计信息
        """
        return {
            "sessions": {
                "total_count": len(self.sessions),
                "active_count": len([s for s in self.sessions.values() if s.status == "active"]),
                "expired_count": len([s for s in self.sessions.values() if self._is_session_expired(s)])
            },
            "templates": {
                "total_count": len(self.templates),
                "by_type": self._get_template_type_stats()
            },
            "file_cache": {
                "cached_files": len(self.file_cache),
                "cache_size_limit": self.cache_size_limit
            },
            "storage": {
                "base_path": self.base_path,
                "disk_usage": self._get_disk_usage()
            }
        }
    
    def _get_template_type_stats(self) -> Dict[str, int]:
        """获取模板类型统计"""
        stats = {}
        for template in self.templates.values():
            template_type = template.template_type
            stats[template_type] = stats.get(template_type, 0) + 1
        return stats
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """获取磁盘使用情况"""
        try:
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except Exception:
                        pass
            
            return {
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "file_count": file_count
            }
        except Exception:
            return {"error": "无法获取磁盘使用情况"}
    
    def cleanup_all_resources(self):
        """清理所有资源"""
        # 清理过期会话
        self._cleanup_expired_sessions()
        
        # 清理文件缓存
        self._cleanup_old_cache()
        
        # 清理临时文件
        self._cleanup_temp_files()
    
    def _cleanup_temp_files(self):
        """清理临时文件"""
        temp_dir = os.path.join(self.base_path, "temp")
        if os.path.exists(temp_dir):
            try:
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    # 删除超过1小时的临时文件
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if datetime.now() - file_time > timedelta(hours=1):
                            os.remove(file_path)
            except Exception as e:
                print(f"清理临时文件失败: {str(e)}")


# 全局资源管理器实例
_resource_manager = None


def get_resource_manager() -> ResourceManager:
    """获取全局资源管理器实例"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager 