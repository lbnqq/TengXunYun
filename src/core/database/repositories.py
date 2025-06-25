"""
数据访问层（Repository Pattern）
提供对数据库的高级操作接口
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .database_manager import get_database_manager
from .models import (
    AppSettings, DocumentRecord, PersonalTemplate, ProcessingResult,
    PerformanceRecord, BatchProcessingRecord
)

logger = logging.getLogger(__name__)

class BaseRepository:
    """基础仓库类"""
    
    def __init__(self):
        self.db = get_database_manager()

class AppSettingsRepository(BaseRepository):
    """应用设置仓库"""
    
    def get_setting(self, key: str, default_value: Any = None) -> Any:
        """获取设置值"""
        try:
            result = self.db.execute_query(
                "SELECT setting_value, setting_type FROM app_settings WHERE setting_key = ?",
                (key,)
            )
            if result:
                setting = AppSettings(
                    setting_key=key,
                    setting_value=result[0]['setting_value'],
                    setting_type=result[0]['setting_type']
                )
                return setting.get_typed_value()
            return default_value
        except Exception as e:
            logger.error(f"Failed to get setting {key}: {e}")
            return default_value
    
    def set_setting(self, key: str, value: Any) -> bool:
        """设置配置值"""
        try:
            setting = AppSettings(setting_key=key)
            setting.set_typed_value(value)
            
            # 使用 INSERT OR REPLACE 来更新或插入
            self.db.execute_update("""
                INSERT OR REPLACE INTO app_settings 
                (setting_key, setting_value, setting_type, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, setting.setting_value, setting.setting_type))
            
            return True
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """获取所有设置"""
        try:
            results = self.db.execute_query("SELECT * FROM app_settings")
            settings = {}
            for row in results:
                setting = AppSettings(
                    setting_key=row['setting_key'],
                    setting_value=row['setting_value'],
                    setting_type=row['setting_type']
                )
                settings[row['setting_key']] = setting.get_typed_value()
            return settings
        except Exception as e:
            logger.error(f"Failed to get all settings: {e}")
            return {}

class DocumentRepository(BaseRepository):
    """文档记录仓库"""
    
    def create_document_record(self, record: DocumentRecord) -> Optional[int]:
        """创建文档记录"""
        try:
            record_id = self.db.execute_insert("""
                INSERT INTO document_records 
                (original_filename, file_path, file_size, file_hash, document_type, 
                 intent_type, processing_status, confidence_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                record.original_filename, record.file_path, record.file_size,
                record.file_hash, record.document_type, record.intent_type,
                record.processing_status, record.confidence_score
            ))
            return record_id
        except Exception as e:
            logger.error(f"Failed to create document record: {e}")
            return None
    
    def update_processing_status(self, record_id: int, status: str, 
                               processing_time_ms: int = 0, error_message: str = None) -> bool:
        """更新处理状态"""
        try:
            completed_at = "CURRENT_TIMESTAMP" if status == "completed" else None
            
            if completed_at:
                self.db.execute_update("""
                    UPDATE document_records 
                    SET processing_status = ?, processing_time_ms = ?, 
                        error_message = ?, completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, processing_time_ms, error_message, record_id))
            else:
                self.db.execute_update("""
                    UPDATE document_records 
                    SET processing_status = ?, processing_time_ms = ?, error_message = ?
                    WHERE id = ?
                """, (status, processing_time_ms, error_message, record_id))
            
            return True
        except Exception as e:
            logger.error(f"Failed to update processing status: {e}")
            return False
    
    def get_document_record(self, record_id: int) -> Optional[DocumentRecord]:
        """获取文档记录"""
        try:
            result = self.db.execute_query(
                "SELECT * FROM document_records WHERE id = ?", (record_id,)
            )
            if result:
                row = result[0]
                return DocumentRecord(
                    id=row['id'],
                    original_filename=row['original_filename'],
                    file_path=row['file_path'],
                    file_size=row['file_size'],
                    file_hash=row['file_hash'],
                    document_type=row['document_type'],
                    intent_type=row['intent_type'],
                    processing_status=row['processing_status'],
                    confidence_score=row['confidence_score'],
                    processing_time_ms=row['processing_time_ms'],
                    error_message=row['error_message'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get document record {record_id}: {e}")
            return None
    
    def get_processing_history(self, limit: int = 50, status: str = None) -> List[DocumentRecord]:
        """获取处理历史"""
        try:
            if status:
                query = """
                    SELECT * FROM document_records 
                    WHERE processing_status = ?
                    ORDER BY created_at DESC LIMIT ?
                """
                params = (status, limit)
            else:
                query = """
                    SELECT * FROM document_records 
                    ORDER BY created_at DESC LIMIT ?
                """
                params = (limit,)
            
            results = self.db.execute_query(query, params)
            records = []
            
            for row in results:
                record = DocumentRecord(
                    id=row['id'],
                    original_filename=row['original_filename'],
                    file_path=row['file_path'],
                    file_size=row['file_size'],
                    file_hash=row['file_hash'],
                    document_type=row['document_type'],
                    intent_type=row['intent_type'],
                    processing_status=row['processing_status'],
                    confidence_score=row['confidence_score'],
                    processing_time_ms=row['processing_time_ms'],
                    error_message=row['error_message'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None
                )
                records.append(record)
            
            return records
        except Exception as e:
            logger.error(f"Failed to get processing history: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取文档处理统计信息"""
        try:
            stats = {}
            
            # 总文档数
            result = self.db.execute_query("SELECT COUNT(*) as count FROM document_records")
            stats['total_documents'] = result[0]['count'] if result else 0
            
            # 各状态文档数
            for status in ['pending', 'processing', 'completed', 'failed']:
                result = self.db.execute_query(
                    "SELECT COUNT(*) as count FROM document_records WHERE processing_status = ?",
                    (status,)
                )
                stats[f'{status}_documents'] = result[0]['count'] if result else 0
            
            # 平均处理时间
            result = self.db.execute_query("""
                SELECT AVG(processing_time_ms) as avg_time 
                FROM document_records 
                WHERE processing_status = 'completed' AND processing_time_ms > 0
            """)
            stats['avg_processing_time_ms'] = result[0]['avg_time'] if result and result[0]['avg_time'] else 0
            
            # 最近7天的文档数
            result = self.db.execute_query("""
                SELECT COUNT(*) as count FROM document_records 
                WHERE created_at > datetime('now', '-7 days')
            """)
            stats['recent_documents'] = result[0]['count'] if result else 0
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get document statistics: {e}")
            return {}

class TemplateRepository(BaseRepository):
    """模板仓库"""
    
    def create_template(self, template: PersonalTemplate) -> Optional[int]:
        """创建模板"""
        try:
            template_id = self.db.execute_insert("""
                INSERT INTO personal_templates 
                (template_name, document_type, template_category, template_config, 
                 usage_count, is_favorite, created_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                template.template_name, template.document_type, template.template_category,
                template.template_config, template.usage_count, template.is_favorite
            ))
            return template_id
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return None
    
    def get_templates(self, document_type: str = None, category: str = None) -> List[PersonalTemplate]:
        """获取模板列表"""
        try:
            if document_type and category:
                query = """
                    SELECT * FROM personal_templates 
                    WHERE document_type = ? AND template_category = ?
                    ORDER BY usage_count DESC, created_at DESC
                """
                params = (document_type, category)
            elif document_type:
                query = """
                    SELECT * FROM personal_templates 
                    WHERE document_type = ?
                    ORDER BY usage_count DESC, created_at DESC
                """
                params = (document_type,)
            else:
                query = """
                    SELECT * FROM personal_templates 
                    ORDER BY usage_count DESC, created_at DESC
                """
                params = ()
            
            results = self.db.execute_query(query, params)
            templates = []
            
            for row in results:
                template = PersonalTemplate(
                    id=row['id'],
                    template_name=row['template_name'],
                    document_type=row['document_type'],
                    template_category=row['template_category'],
                    template_config=row['template_config'],
                    usage_count=row['usage_count'],
                    is_favorite=bool(row['is_favorite']),
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    last_used_at=datetime.fromisoformat(row['last_used_at']) if row['last_used_at'] else None
                )
                templates.append(template)
            
            return templates
        except Exception as e:
            logger.error(f"Failed to get templates: {e}")
            return []
    
    def update_template_usage(self, template_id: int) -> bool:
        """更新模板使用次数"""
        try:
            self.db.execute_update("""
                UPDATE personal_templates 
                SET usage_count = usage_count + 1, last_used_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (template_id,))
            return True
        except Exception as e:
            logger.error(f"Failed to update template usage: {e}")
            return False

class ProcessingResultRepository(BaseRepository):
    """处理结果仓库"""
    
    def create_result(self, result: ProcessingResult) -> Optional[int]:
        """创建处理结果记录"""
        try:
            result_id = self.db.execute_insert("""
                INSERT INTO processing_results 
                (document_record_id, result_type, file_path, file_size, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                result.document_record_id, result.result_type, 
                result.file_path, result.file_size
            ))
            return result_id
        except Exception as e:
            logger.error(f"Failed to create processing result: {e}")
            return None
    
    def get_results_by_document(self, document_record_id: int) -> List[ProcessingResult]:
        """获取文档的所有处理结果"""
        try:
            results = self.db.execute_query("""
                SELECT * FROM processing_results 
                WHERE document_record_id = ?
                ORDER BY created_at DESC
            """, (document_record_id,))
            
            processing_results = []
            for row in results:
                result = ProcessingResult(
                    id=row['id'],
                    document_record_id=row['document_record_id'],
                    result_type=row['result_type'],
                    file_path=row['file_path'],
                    file_size=row['file_size'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                processing_results.append(result)
            
            return processing_results
        except Exception as e:
            logger.error(f"Failed to get processing results: {e}")
            return []

class PerformanceRepository(BaseRepository):
    """性能记录仓库"""

    def create_performance_record(self, record: PerformanceRecord) -> Optional[int]:
        """创建性能记录"""
        try:
            record_id = self.db.execute_insert("""
                INSERT INTO performance_records
                (operation, duration_ms, success, error_message, api_endpoint,
                 model_name, input_tokens, output_tokens, cache_hit, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                record.operation, record.duration_ms, record.success, record.error_message,
                record.api_endpoint, record.model_name, record.input_tokens,
                record.output_tokens, record.cache_hit, record.metadata
            ))
            return record_id
        except Exception as e:
            logger.error(f"Failed to create performance record: {e}")
            return None

    def get_performance_stats(self, operation: str = None,
                            time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """获取性能统计"""
        try:
            cutoff_time = datetime.now() - time_window

            base_query = """
                SELECT
                    COUNT(*) as total_count,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                    AVG(duration_ms) as avg_duration,
                    MIN(duration_ms) as min_duration,
                    MAX(duration_ms) as max_duration,
                    SUM(input_tokens) as total_input_tokens,
                    SUM(output_tokens) as total_output_tokens,
                    SUM(CASE WHEN cache_hit = 1 THEN 1 ELSE 0 END) as cache_hits
                FROM performance_records
                WHERE created_at >= ?
            """

            params = [cutoff_time.isoformat()]
            if operation:
                base_query += " AND operation = ?"
                params.append(operation)

            result = self.db.execute_query(base_query, tuple(params))

            if result:
                row = result[0]
                total_count = row['total_count'] or 0
                success_count = row['success_count'] or 0

                return {
                    'total_requests': total_count,
                    'successful_requests': success_count,
                    'failed_requests': total_count - success_count,
                    'success_rate': success_count / total_count if total_count > 0 else 0.0,
                    'avg_duration_ms': row['avg_duration'] or 0.0,
                    'min_duration_ms': row['min_duration'] or 0.0,
                    'max_duration_ms': row['max_duration'] or 0.0,
                    'total_input_tokens': row['total_input_tokens'] or 0,
                    'total_output_tokens': row['total_output_tokens'] or 0,
                    'cache_hits': row['cache_hits'] or 0,
                    'cache_hit_rate': (row['cache_hits'] or 0) / total_count if total_count > 0 else 0.0
                }
            else:
                return {}

        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {}

    def get_operation_breakdown(self, time_window: timedelta = timedelta(hours=24)) -> List[Dict[str, Any]]:
        """获取操作类型分解统计"""
        try:
            cutoff_time = datetime.now() - time_window

            results = self.db.execute_query("""
                SELECT
                    operation,
                    COUNT(*) as count,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                    AVG(duration_ms) as avg_duration,
                    SUM(input_tokens) as total_input_tokens,
                    SUM(output_tokens) as total_output_tokens
                FROM performance_records
                WHERE created_at >= ?
                GROUP BY operation
                ORDER BY count DESC
            """, (cutoff_time.isoformat(),))

            breakdown = []
            for row in results:
                count = row['count'] or 0
                success_count = row['success_count'] or 0

                breakdown.append({
                    'operation': row['operation'],
                    'count': count,
                    'success_count': success_count,
                    'success_rate': success_count / count if count > 0 else 0.0,
                    'avg_duration_ms': row['avg_duration'] or 0.0,
                    'total_input_tokens': row['total_input_tokens'] or 0,
                    'total_output_tokens': row['total_output_tokens'] or 0
                })

            return breakdown

        except Exception as e:
            logger.error(f"Failed to get operation breakdown: {e}")
            return []

    def cleanup_old_records(self, days_to_keep: int = 30) -> int:
        """清理旧的性能记录"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = self.db.execute_update("""
                DELETE FROM performance_records
                WHERE created_at < ?
            """, (cutoff_date.isoformat(),))

            logger.info(f"Cleaned up {deleted_count} old performance records")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old performance records: {e}")
            return 0

class BatchProcessingRepository(BaseRepository):
    """批量处理记录仓库"""

    def create_batch_record(self, record: BatchProcessingRecord) -> Optional[int]:
        """创建批量处理记录"""
        try:
            record_id = self.db.execute_insert("""
                INSERT INTO batch_processing_records
                (batch_name, total_files, processed_files, successful_files, failed_files,
                 processing_status, start_time, end_time, total_duration_ms,
                 error_summary, configuration, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                record.batch_name, record.total_files, record.processed_files,
                record.successful_files, record.failed_files, record.processing_status,
                record.start_time.isoformat() if record.start_time else None,
                record.end_time.isoformat() if record.end_time else None,
                record.total_duration_ms, record.error_summary, record.configuration
            ))
            return record_id
        except Exception as e:
            logger.error(f"Failed to create batch processing record: {e}")
            return None

    def update_batch_progress(self, batch_id: int, processed_files: int,
                            successful_files: int, failed_files: int) -> bool:
        """更新批量处理进度"""
        try:
            self.db.execute_update("""
                UPDATE batch_processing_records
                SET processed_files = ?, successful_files = ?, failed_files = ?
                WHERE id = ?
            """, (processed_files, successful_files, failed_files, batch_id))
            return True
        except Exception as e:
            logger.error(f"Failed to update batch progress: {e}")
            return False

    def complete_batch(self, batch_id: int, success: bool, error_summary: str = None) -> bool:
        """完成批量处理"""
        try:
            status = "completed" if success else "failed"
            self.db.execute_update("""
                UPDATE batch_processing_records
                SET processing_status = ?, end_time = CURRENT_TIMESTAMP, error_summary = ?
                WHERE id = ?
            """, (status, error_summary, batch_id))
            return True
        except Exception as e:
            logger.error(f"Failed to complete batch: {e}")
            return False

    def get_batch_record(self, batch_id: int) -> Optional[BatchProcessingRecord]:
        """获取批量处理记录"""
        try:
            results = self.db.execute_query("""
                SELECT * FROM batch_processing_records WHERE id = ?
            """, (batch_id,))

            if results:
                row = results[0]
                return BatchProcessingRecord(
                    id=row['id'],
                    batch_name=row['batch_name'],
                    total_files=row['total_files'],
                    processed_files=row['processed_files'],
                    successful_files=row['successful_files'],
                    failed_files=row['failed_files'],
                    processing_status=row['processing_status'],
                    start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    total_duration_ms=row['total_duration_ms'],
                    error_summary=row['error_summary'],
                    configuration=row['configuration'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get batch record: {e}")
            return None

    def get_recent_batches(self, limit: int = 20) -> List[BatchProcessingRecord]:
        """获取最近的批量处理记录"""
        try:
            results = self.db.execute_query("""
                SELECT * FROM batch_processing_records
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

            batches = []
            for row in results:
                batch = BatchProcessingRecord(
                    id=row['id'],
                    batch_name=row['batch_name'],
                    total_files=row['total_files'],
                    processed_files=row['processed_files'],
                    successful_files=row['successful_files'],
                    failed_files=row['failed_files'],
                    processing_status=row['processing_status'],
                    start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    total_duration_ms=row['total_duration_ms'],
                    error_summary=row['error_summary'],
                    configuration=row['configuration'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                batches.append(batch)

            return batches
        except Exception as e:
            logger.error(f"Failed to get recent batches: {e}")
            return []

    def get_batch_statistics(self) -> Dict[str, Any]:
        """获取批量处理统计"""
        try:
            stats = {}

            # 总批次数
            result = self.db.execute_query("SELECT COUNT(*) as count FROM batch_processing_records")
            stats['total_batches'] = result[0]['count'] if result else 0

            # 各状态批次数
            for status in ['pending', 'processing', 'completed', 'failed']:
                result = self.db.execute_query(
                    "SELECT COUNT(*) as count FROM batch_processing_records WHERE processing_status = ?",
                    (status,)
                )
                stats[f'{status}_batches'] = result[0]['count'] if result else 0

            # 总文件处理统计
            result = self.db.execute_query("""
                SELECT
                    SUM(total_files) as total_files,
                    SUM(processed_files) as processed_files,
                    SUM(successful_files) as successful_files,
                    SUM(failed_files) as failed_files
                FROM batch_processing_records
            """)

            if result and result[0]['total_files']:
                row = result[0]
                stats.update({
                    'total_files_in_batches': row['total_files'] or 0,
                    'total_processed_files': row['processed_files'] or 0,
                    'total_successful_files': row['successful_files'] or 0,
                    'total_failed_files': row['failed_files'] or 0
                })

                # 计算成功率
                if row['processed_files'] and row['processed_files'] > 0:
                    stats['overall_success_rate'] = (row['successful_files'] or 0) / row['processed_files']
                else:
                    stats['overall_success_rate'] = 0.0
            else:
                stats.update({
                    'total_files_in_batches': 0,
                    'total_processed_files': 0,
                    'total_successful_files': 0,
                    'total_failed_files': 0,
                    'overall_success_rate': 0.0
                })

            return stats
        except Exception as e:
            logger.error(f"Failed to get batch statistics: {e}")
            return {}
