"""
统一错误处理机制
提供详细的错误信息、回退机制和错误分类管理
"""

import traceback
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

class ErrorLevel(Enum):
    """错误级别枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """错误分类枚举"""
    VALIDATION = "validation"
    API = "api"
    FILE_IO = "file_io"
    NETWORK = "network"
    DATABASE = "database"
    TEMPLATE = "template"
    LLM = "llm"
    UNKNOWN = "unknown"

class ErrorHandler:
    """
    统一错误处理器
    提供错误分类、详细错误信息、回退机制和错误报告功能
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_callbacks = {}
        self.fallback_handlers = {}
        
        # 初始化错误回调
        self._init_error_callbacks()
    
    def _init_error_callbacks(self):
        """初始化错误回调函数"""
        self.error_callbacks = {
            ErrorCategory.VALIDATION: self._handle_validation_error,
            ErrorCategory.API: self._handle_api_error,
            ErrorCategory.FILE_IO: self._handle_file_io_error,
            ErrorCategory.NETWORK: self._handle_network_error,
            ErrorCategory.DATABASE: self._handle_database_error,
            ErrorCategory.TEMPLATE: self._handle_template_error,
            ErrorCategory.LLM: self._handle_llm_error,
            ErrorCategory.UNKNOWN: self._handle_unknown_error
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理错误并返回标准化的错误响应
        
        Args:
            error: 异常对象
            context: 错误上下文信息
            
        Returns:
            标准化的错误响应
        """
        try:
            # 分类错误
            category = self._categorize_error(error)
            level = self._determine_error_level(error, category)
            
            # 生成错误ID
            error_id = self._generate_error_id()
            
            # 构建错误信息
            error_info = {
                "error_id": error_id,
                "timestamp": datetime.now().isoformat(),
                "category": category.value,
                "level": level.value,
                "message": str(error),
                "type": type(error).__name__,
                "traceback": traceback.format_exc(),
                "context": context or {}
            }
            
            # 记录错误
            self._log_error(error_info)
            
            # 调用相应的错误处理器
            if category in self.error_callbacks:
                result = self.error_callbacks[category](error_info)
            else:
                result = self._handle_unknown_error(error_info)
            
            # 尝试回退机制
            if result.get("can_fallback", False):
                fallback_result = self._try_fallback(category, error_info)
                if fallback_result:
                    result["fallback_result"] = fallback_result
                    result["message"] = f"{result['message']} (已启用回退机制)"
            
            return result
            
        except Exception as e:
            # 如果错误处理本身出错，返回基本信息
            return {
                "success": False,
                "error": f"错误处理失败: {str(e)}",
                "original_error": str(error),
                "can_fallback": False
            }
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """分类错误"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # 验证错误
        if any(keyword in error_str for keyword in ["validation", "invalid", "missing", "required"]):
            return ErrorCategory.VALIDATION
        
        # API错误
        if any(keyword in error_str for keyword in ["api", "http", "request", "response"]):
            return ErrorCategory.API
        
        # 文件IO错误
        if any(keyword in error_str for keyword in ["file", "io", "permission", "not found"]):
            return ErrorCategory.FILE_IO
        
        # 网络错误
        if any(keyword in error_str for keyword in ["network", "connection", "timeout"]):
            return ErrorCategory.NETWORK
        
        # 数据库错误
        if any(keyword in error_str for keyword in ["database", "sql", "db"]):
            return ErrorCategory.DATABASE
        
        # 模板错误
        if any(keyword in error_str for keyword in ["template", "format", "schema"]):
            return ErrorCategory.TEMPLATE
        
        # LLM错误
        if any(keyword in error_str for keyword in ["llm", "model", "generation"]):
            return ErrorCategory.LLM
        
        return ErrorCategory.UNKNOWN
    
    def _determine_error_level(self, error: Exception, category: ErrorCategory) -> ErrorLevel:
        """确定错误级别"""
        error_str = str(error).lower()
        
        # 严重错误
        if any(keyword in error_str for keyword in ["critical", "fatal", "system"]):
            return ErrorLevel.CRITICAL
        
        # 一般错误
        if category in [ErrorCategory.API, ErrorCategory.DATABASE, ErrorCategory.NETWORK]:
            return ErrorLevel.ERROR
        
        # 警告
        if category in [ErrorCategory.VALIDATION, ErrorCategory.TEMPLATE]:
            return ErrorLevel.WARNING
        
        return ErrorLevel.ERROR
    
    def _generate_error_id(self) -> str:
        """生成错误ID"""
        import hashlib
        import time
        import random
        
        content = f"{time.time()}_{random.randint(1000, 9999)}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def _log_error(self, error_info: Dict[str, Any]):
        """记录错误"""
        level = error_info["level"]
        message = f"[{error_info['error_id']}] {error_info['message']}"
        
        if level == ErrorLevel.CRITICAL.value:
            self.logger.critical(message, extra=error_info)
        elif level == ErrorLevel.ERROR.value:
            self.logger.error(message, extra=error_info)
        elif level == ErrorLevel.WARNING.value:
            self.logger.warning(message, extra=error_info)
        else:
            self.logger.info(message, extra=error_info)
    
    def _handle_validation_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理验证错误"""
        return {
            "success": False,
            "error": f"数据验证失败: {error_info['message']}",
            "error_id": error_info["error_id"],
            "category": "validation",
            "can_fallback": False,
            "suggestions": [
                "检查输入数据的格式和完整性",
                "确保所有必需字段都已提供",
                "验证数据类型是否正确"
            ]
        }
    
    def _handle_api_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理API错误"""
        return {
            "success": False,
            "error": f"API调用失败: {error_info['message']}",
            "error_id": error_info["error_id"],
            "category": "api",
            "can_fallback": True,
            "suggestions": [
                "检查API配置和认证信息",
                "验证网络连接状态",
                "尝试使用备用API端点"
            ]
        }
    
    def _handle_file_io_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理文件IO错误"""
        return {
            "success": False,
            "error": f"文件操作失败: {error_info['message']}",
            "error_id": error_info["error_id"],
            "category": "file_io",
            "can_fallback": True,
            "suggestions": [
                "检查文件路径和权限",
                "确保目录存在且可写",
                "验证文件格式是否正确"
            ]
        }
    
    def _handle_network_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理网络错误"""
        return {
            "success": False,
            "error": f"网络连接失败: {error_info['message']}",
            "error_id": error_info["error_id"],
            "category": "network",
            "can_fallback": True,
            "suggestions": [
                "检查网络连接状态",
                "验证服务器地址和端口",
                "尝试重新连接"
            ]
        }
    
    def _handle_database_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理数据库错误"""
        return {
            "success": False,
            "error": f"数据库操作失败: {error_info['message']}",
            "error_id": error_info["error_id"],
            "category": "database",
            "can_fallback": False,
            "suggestions": [
                "检查数据库连接状态",
                "验证SQL语句语法",
                "确认数据库权限"
            ]
        }
    
    def _handle_template_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理模板错误"""
        return {
            "success": False,
            "error": f"模板处理失败: {error_info['message']}",
            "error_id": error_info["error_id"],
            "category": "template",
            "can_fallback": True,
            "suggestions": [
                "检查模板格式和结构",
                "验证模板数据完整性",
                "使用默认模板作为回退"
            ]
        }
    
    def _handle_llm_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理LLM错误"""
        return {
            "success": False,
            "error": f"LLM服务失败: {error_info['message']}",
            "error_id": error_info["error_id"],
            "category": "llm",
            "can_fallback": True,
            "suggestions": [
                "检查LLM API配置",
                "验证模型可用性",
                "使用基础分析功能作为回退"
            ]
        }
    
    def _handle_unknown_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理未知错误"""
        return {
            "success": False,
            "error": f"未知错误: {error_info['message']}",
            "error_id": error_info["error_id"],
            "category": "unknown",
            "can_fallback": False,
            "suggestions": [
                "检查系统日志获取详细信息",
                "联系技术支持",
                "尝试重新启动服务"
            ]
        }
    
    def _try_fallback(self, category: ErrorCategory, error_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """尝试回退机制"""
        if category not in self.fallback_handlers:
            return None
        
        try:
            fallback_handler = self.fallback_handlers[category]
            return fallback_handler(error_info)
        except Exception as e:
            self.logger.warning(f"回退机制失败: {str(e)}")
            return None
    
    def register_fallback_handler(self, category: ErrorCategory, handler: Callable):
        """注册回退处理器"""
        self.fallback_handlers[category] = handler
    
    def get_error_summary(self, error_id: str) -> Optional[Dict[str, Any]]:
        """获取错误摘要"""
        # 这里可以实现从日志或数据库中获取错误摘要
        # 目前返回基本结构
        return {
            "error_id": error_id,
            "timestamp": datetime.now().isoformat(),
            "status": "resolved",
            "resolution_time": None
        }

# 全局错误处理器实例
error_handler = ErrorHandler() 