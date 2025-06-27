"""
批量处理协调器
负责管理多文档的并行处理
"""

import os
import time
import uuid
import threading
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from dataclasses import dataclass
import logging

from ..database import (
    BatchProcessingRepository, 
    DocumentRepository,
    BatchProcessingRecord,
    DocumentRecord,
    get_database_manager
)
from ..monitoring import PerformanceTimer, record_performance

logger = logging.getLogger(__name__)

@dataclass
class BatchJob:
    """批量处理作业"""
    id: str
    name: str
    files: List[str]
    processing_config: Dict[str, Any]
    status: str = "pending"  # pending, processing, completed, failed, cancelled
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.progress is None:
            self.progress = {
                'total': len(self.files),
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'current_file': None
            }

class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, max_workers: int = 3):
        """
        初始化批量处理器
        
        Args:
            max_workers: 最大并行处理数
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_jobs: Dict[str, BatchJob] = {}
        self.job_lock = threading.RLock()
        
        # 数据库仓库
        self.batch_repo = BatchProcessingRepository()
        self.doc_repo = DocumentRepository()
        
        # 处理器映射
        self.processors = {}
        
        logger.info(f"BatchProcessor initialized with {max_workers} workers")
    
    def register_processor(self, operation_type: str, processor_func: Callable):
        """注册处理器函数"""
        self.processors[operation_type] = processor_func
        logger.info(f"Registered processor for operation: {operation_type}")
    
    def create_batch_job(self, name: str, files: List[str], 
                        processing_config: Dict[str, Any]) -> str:
        """
        创建批量处理作业
        
        Args:
            name: 作业名称
            files: 文件路径列表
            processing_config: 处理配置
            
        Returns:
            作业ID
        """
        job_id = str(uuid.uuid4())
        
        # 验证文件
        valid_files = []
        for file_path in files:
            # 检查文件路径是否为None或空字符串
            if file_path is None or file_path == "":
                logger.warning(f"Invalid file path: {file_path} (None or empty)")
                continue

            # 检查文件路径是否为字符串类型
            if not isinstance(file_path, (str, bytes, os.PathLike)):
                logger.warning(f"Invalid file path type: {type(file_path)} - {file_path}")
                continue

            # 检查文件是否存在
            try:
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    valid_files.append(file_path)
                else:
                    logger.warning(f"File not found or invalid: {file_path}")
            except (TypeError, OSError) as e:
                logger.warning(f"Error checking file path {file_path}: {e}")
        
        if not valid_files:
            raise ValueError("No valid files provided for batch processing")
        
        # 创建作业
        job = BatchJob(
            id=job_id,
            name=name,
            files=valid_files,
            processing_config=processing_config
        )
        
        with self.job_lock:
            self.active_jobs[job_id] = job
        
        # 保存到数据库
        batch_record = BatchProcessingRecord(
            batch_name=name,
            total_files=len(valid_files),
            configuration=processing_config
        )
        batch_record.set_configuration(processing_config)
        
        db_id = self.batch_repo.create_batch_record(batch_record)
        if db_id:
            job.progress['db_id'] = db_id
        
        logger.info(f"Created batch job {job_id} with {len(valid_files)} files")
        return job_id
    
    def start_batch_job(self, job_id: str) -> bool:
        """
        启动批量处理作业
        
        Args:
            job_id: 作业ID
            
        Returns:
            是否成功启动
        """
        with self.job_lock:
            if job_id not in self.active_jobs:
                logger.error(f"Job {job_id} not found")
                return False
            
            job = self.active_jobs[job_id]
            if job.status != "pending":
                logger.error(f"Job {job_id} is not in pending status: {job.status}")
                return False
            
            job.status = "processing"
            job.started_at = datetime.now()
        
        # 提交到线程池执行
        future = self.executor.submit(self._process_batch_job, job_id)
        
        logger.info(f"Started batch job {job_id}")
        return True
    
    def _process_batch_job(self, job_id: str):
        """处理批量作业的内部方法"""
        with self.job_lock:
            job = self.active_jobs.get(job_id)
            if not job:
                return
        
        operation_type = job.processing_config.get('operation', 'default')
        processor_func = self.processors.get(operation_type)
        
        if not processor_func:
            logger.error(f"No processor registered for operation: {operation_type}")
            self._complete_job(job_id, False, f"No processor for operation: {operation_type}")
            return
        
        try:
            with PerformanceTimer(f"batch_processing_{operation_type}"):
                self._process_files_parallel(job, processor_func)
            
            # 判断作业是否成功
            success = job.progress['failed'] == 0
            self._complete_job(job_id, success)
            
        except Exception as e:
            logger.error(f"Batch job {job_id} failed: {e}")
            self._complete_job(job_id, False, str(e))
    
    def _process_files_parallel(self, job: BatchJob, processor_func: Callable):
        """并行处理文件"""
        futures = {}
        
        # 提交所有文件处理任务
        for file_path in job.files:
            future = self.executor.submit(self._process_single_file, 
                                        job, file_path, processor_func)
            futures[future] = file_path
        
        # 等待所有任务完成
        for future in as_completed(futures):
            file_path = futures[future]
            
            try:
                success = future.result()
                
                with self.job_lock:
                    job.progress['processed'] += 1
                    if success:
                        job.progress['successful'] += 1
                    else:
                        job.progress['failed'] += 1
                    
                    job.progress['current_file'] = file_path
                    
                    # 更新数据库进度
                    if 'db_id' in job.progress:
                        self.batch_repo.update_batch_progress(
                            job.progress['db_id'],
                            job.progress['processed'],
                            job.progress['successful'],
                            job.progress['failed']
                        )
                
                logger.info(f"Processed file {file_path} in job {job.id}: {'success' if success else 'failed'}")
                
            except Exception as e:
                logger.error(f"Error processing file {file_path} in job {job.id}: {e}")
                
                with self.job_lock:
                    job.progress['processed'] += 1
                    job.progress['failed'] += 1
    
    def _process_single_file(self, job: BatchJob, file_path: str, 
                           processor_func: Callable) -> bool:
        """处理单个文件"""
        try:
            start_time = time.time()
            
            # 调用处理器函数
            result = processor_func(file_path, job.processing_config)
            
            processing_time = (time.time() - start_time) * 1000
            
            # 记录性能指标
            record_performance(
                f"batch_file_processing",
                processing_time,
                result.get('success', False) if isinstance(result, dict) else bool(result),
                result.get('error') if isinstance(result, dict) else None
            )
            
            return result.get('success', False) if isinstance(result, dict) else bool(result)
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            record_performance(f"batch_file_processing", 0, False, str(e))
            return False
    
    def _complete_job(self, job_id: str, success: bool, error_message: str = None):
        """完成作业"""
        with self.job_lock:
            job = self.active_jobs.get(job_id)
            if not job:
                return
            
            job.status = "completed" if success else "failed"
            job.completed_at = datetime.now()
            
            # 更新数据库
            if 'db_id' in job.progress:
                self.batch_repo.complete_batch(
                    job.progress['db_id'], 
                    success, 
                    error_message
                )
        
        logger.info(f"Batch job {job_id} completed: {'success' if success else 'failed'}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取作业状态"""
        with self.job_lock:
            job = self.active_jobs.get(job_id)
            if not job:
                return None
            
            return {
                'id': job.id,
                'name': job.name,
                'status': job.status,
                'progress': dict(job.progress),
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'total_files': len(job.files),
                'processing_config': job.processing_config
            }
    
    def cancel_job(self, job_id: str) -> bool:
        """取消作业"""
        with self.job_lock:
            job = self.active_jobs.get(job_id)
            if not job:
                return False
            
            if job.status in ["completed", "failed", "cancelled"]:
                return False
            
            job.status = "cancelled"
            job.completed_at = datetime.now()
            
            # 更新数据库
            if 'db_id' in job.progress:
                self.batch_repo.complete_batch(
                    job.progress['db_id'], 
                    False, 
                    "Job cancelled by user"
                )
        
        logger.info(f"Batch job {job_id} cancelled")
        return True
    
    def list_active_jobs(self) -> List[Dict[str, Any]]:
        """列出活跃的作业"""
        with self.job_lock:
            return [
                self.get_job_status(job_id) 
                for job_id in self.active_jobs.keys()
            ]
    
    def cleanup_completed_jobs(self, max_age_hours: int = 24):
        """清理已完成的作业"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        with self.job_lock:
            jobs_to_remove = []
            for job_id, job in self.active_jobs.items():
                if (job.status in ["completed", "failed", "cancelled"] and
                    job.completed_at and 
                    job.completed_at.timestamp() < cutoff_time):
                    jobs_to_remove.append(job_id)
            
            for job_id in jobs_to_remove:
                del self.active_jobs[job_id]
        
        logger.info(f"Cleaned up {len(jobs_to_remove)} completed jobs")
        return len(jobs_to_remove)
    
    def shutdown(self):
        """关闭批量处理器"""
        logger.info("Shutting down BatchProcessor")
        self.executor.shutdown(wait=True)

# 全局批量处理器实例
_global_batch_processor = None

def get_batch_processor() -> BatchProcessor:
    """获取全局批量处理器实例"""
    global _global_batch_processor
    if _global_batch_processor is None:
        _global_batch_processor = BatchProcessor()
    return _global_batch_processor
