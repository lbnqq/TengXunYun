"""
数据模型定义
定义数据库表对应的Python类
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

@dataclass
class AppSettings:
    """应用配置模型"""
    id: Optional[int] = None
    setting_key: str = ""
    setting_value: str = ""
    setting_type: str = "string"  # string, json, boolean, number
    updated_at: Optional[datetime] = None
    
    def get_typed_value(self) -> Any:
        """根据setting_type返回正确类型的值"""
        if self.setting_type == "boolean":
            return self.setting_value.lower() in ('true', '1', 'yes', 'on')
        elif self.setting_type == "number":
            try:
                if '.' in self.setting_value:
                    return float(self.setting_value)
                else:
                    return int(self.setting_value)
            except ValueError:
                return 0
        elif self.setting_type == "json":
            try:
                return json.loads(self.setting_value)
            except json.JSONDecodeError:
                return {}
        else:
            return self.setting_value
    
    def set_typed_value(self, value: Any):
        """根据值类型设置setting_value和setting_type"""
        if isinstance(value, bool):
            self.setting_type = "boolean"
            self.setting_value = str(value).lower()
        elif isinstance(value, (int, float)):
            self.setting_type = "number"
            self.setting_value = str(value)
        elif isinstance(value, (dict, list)):
            self.setting_type = "json"
            self.setting_value = json.dumps(value, ensure_ascii=False)
        else:
            self.setting_type = "string"
            self.setting_value = str(value)

@dataclass
class DocumentRecord:
    """文档处理记录模型"""
    id: Optional[int] = None
    original_filename: str = ""
    file_path: str = ""
    file_size: int = 0
    file_hash: str = ""
    document_type: str = ""
    intent_type: str = ""
    processing_status: str = "pending"  # pending, processing, completed, failed
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def is_completed(self) -> bool:
        """检查文档是否处理完成"""
        return self.processing_status == "completed"
    
    def is_failed(self) -> bool:
        """检查文档处理是否失败"""
        return self.processing_status == "failed"
    
    def get_processing_duration(self) -> Optional[float]:
        """获取处理耗时（秒）"""
        if self.processing_time_ms > 0:
            return self.processing_time_ms / 1000.0
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'document_type': self.document_type,
            'intent_type': self.intent_type,
            'processing_status': self.processing_status,
            'confidence_score': self.confidence_score,
            'processing_time_ms': self.processing_time_ms,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

@dataclass
class PersonalTemplate:
    """个人格式模板模型"""
    id: Optional[int] = None
    template_name: str = ""
    document_type: str = ""
    template_category: str = ""  # font, paragraph, numbering, table
    template_config: str = ""  # JSON格式的配置
    usage_count: int = 0
    is_favorite: bool = False
    created_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    def get_config(self) -> Dict[str, Any]:
        """获取模板配置（解析JSON）"""
        try:
            return json.loads(self.template_config) if self.template_config else {}
        except json.JSONDecodeError:
            return {}
    
    def set_config(self, config: Dict[str, Any]):
        """设置模板配置（转换为JSON）"""
        self.template_config = json.dumps(config, ensure_ascii=False)
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.last_used_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'template_name': self.template_name,
            'document_type': self.document_type,
            'template_category': self.template_category,
            'template_config': self.get_config(),
            'usage_count': self.usage_count,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }

@dataclass
class ProcessingResult:
    """处理结果存储模型"""
    id: Optional[int] = None
    document_record_id: int = 0
    result_type: str = ""  # original, processed, preview
    file_path: str = ""
    file_size: int = 0
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'document_record_id': self.document_record_id,
            'result_type': self.result_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 文档类型枚举
class DocumentType:
    """文档类型常量"""
    EMPTY_FORM = "empty_form"
    FORMAT_MESSY = "format_messy"
    CONTENT_INCOMPLETE = "content_incomplete"
    AIGC_HEAVY = "aigc_heavy"
    GENERAL_DOCUMENT = "general_document"
    TECHNICAL_REPORT = "technical_report"
    PRODUCT_PROPOSAL = "product_proposal"
    MARKET_ANALYSIS = "market_analysis"
    MEETING_MINUTES = "meeting_minutes"
    RESEARCH_PAPER = "research_paper"

# 意图类型枚举
class IntentType:
    """处理意图类型常量"""
    INTELLIGENT_FILLING = "intelligent_filling"
    FORMAT_CLEANUP = "format_cleanup"
    CONTENT_COMPLETION = "content_completion"
    STYLE_REWRITE = "style_rewrite"
    GENERAL_PROCESSING = "general_processing"

# 处理状态枚举
class ProcessingStatus:
    """处理状态常量"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# 模板类别枚举
class TemplateCategory:
    """模板类别常量"""
    FONT = "font"
    PARAGRAPH = "paragraph"
    NUMBERING = "numbering"
    TABLE = "table"
    LAYOUT = "layout"
    STYLE = "style"

# 结果类型枚举
class ResultType:
    """结果类型常量"""
    ORIGINAL = "original"
    PROCESSED = "processed"
    PREVIEW = "preview"
    BACKUP = "backup"

@dataclass
class PerformanceRecord:
    """性能记录模型"""
    id: Optional[int] = None
    operation: str = ""
    duration_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    api_endpoint: Optional[str] = None
    model_name: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    cache_hit: bool = False
    metadata: str = "{}"  # JSON字符串
    created_at: Optional[datetime] = None

    def get_metadata(self) -> Dict[str, Any]:
        """获取元数据字典"""
        try:
            return json.loads(self.metadata) if self.metadata else {}
        except json.JSONDecodeError:
            return {}

    def set_metadata(self, metadata: Dict[str, Any]):
        """设置元数据"""
        self.metadata = json.dumps(metadata, ensure_ascii=False)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'operation': self.operation,
            'duration_ms': self.duration_ms,
            'success': self.success,
            'error_message': self.error_message,
            'api_endpoint': self.api_endpoint,
            'model_name': self.model_name,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'cache_hit': self.cache_hit,
            'metadata': self.get_metadata(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class BatchProcessingRecord:
    """批量处理记录模型"""
    id: Optional[int] = None
    batch_name: str = ""
    total_files: int = 0
    processed_files: int = 0
    successful_files: int = 0
    failed_files: int = 0
    processing_status: str = "pending"  # pending, processing, completed, failed, cancelled
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration_ms: float = 0.0
    error_summary: Optional[str] = None
    configuration: str = "{}"  # JSON字符串
    created_at: Optional[datetime] = None

    def get_configuration(self) -> Dict[str, Any]:
        """获取配置字典"""
        try:
            return json.loads(self.configuration) if self.configuration else {}
        except json.JSONDecodeError:
            return {}

    def set_configuration(self, config: Dict[str, Any]):
        """设置配置"""
        self.configuration = json.dumps(config, ensure_ascii=False)

    def get_progress_percentage(self) -> float:
        """获取进度百分比"""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100.0

    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.processed_files == 0:
            return 0.0
        return (self.successful_files / self.processed_files) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'batch_name': self.batch_name,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'processing_status': self.processing_status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_duration_ms': self.total_duration_ms,
            'error_summary': self.error_summary,
            'configuration': self.get_configuration(),
            'progress_percentage': self.get_progress_percentage(),
            'success_rate': self.get_success_rate(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
