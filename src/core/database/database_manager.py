"""
SQLite数据库管理器
负责数据库连接、初始化和迁移管理
"""

import sqlite3
import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径，默认为用户目录下的office_doc_agent.db
        """
        if db_path is None:
            # 默认数据库路径：用户目录/.office_doc_agent/user_data.db
            user_dir = os.path.expanduser("~")
            app_dir = os.path.join(user_dir, ".office_doc_agent")
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "user_data.db")
        
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()
        
        # 初始化数据库
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取线程本地的数据库连接"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            # 启用外键约束
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            # 设置行工厂，返回字典格式
            self._local.connection.row_factory = sqlite3.Row
        
        return self._local.connection
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = self._get_connection()
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            conn.commit()
    
    def _initialize_database(self):
        """初始化数据库表结构"""
        with self._lock:
            try:
                with self.get_connection() as conn:
                    # 创建应用配置表
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS app_settings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            setting_key TEXT UNIQUE NOT NULL,
                            setting_value TEXT NOT NULL,
                            setting_type TEXT DEFAULT 'string',
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # 创建文档处理记录表
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS document_records (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            original_filename TEXT NOT NULL,
                            file_path TEXT NOT NULL,
                            file_size INTEGER NOT NULL,
                            file_hash TEXT NOT NULL,
                            document_type TEXT NOT NULL,
                            intent_type TEXT NOT NULL,
                            processing_status TEXT DEFAULT 'pending',
                            confidence_score REAL DEFAULT 0.0,
                            processing_time_ms INTEGER DEFAULT 0,
                            error_message TEXT,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            completed_at DATETIME
                        )
                    """)
                    
                    # 创建个人格式模板表
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS personal_templates (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            template_name TEXT NOT NULL,
                            document_type TEXT NOT NULL,
                            template_category TEXT NOT NULL,
                            template_config TEXT NOT NULL,
                            usage_count INTEGER DEFAULT 0,
                            is_favorite BOOLEAN DEFAULT FALSE,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            last_used_at DATETIME
                        )
                    """)
                    
                    # 创建处理结果存储表
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS processing_results (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            document_record_id INTEGER REFERENCES document_records(id),
                            result_type TEXT NOT NULL,
                            file_path TEXT NOT NULL,
                            file_size INTEGER NOT NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

                    # 创建性能记录表
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS performance_records (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            operation TEXT NOT NULL,
                            duration_ms REAL NOT NULL,
                            success BOOLEAN NOT NULL,
                            error_message TEXT,
                            api_endpoint TEXT,
                            model_name TEXT,
                            input_tokens INTEGER DEFAULT 0,
                            output_tokens INTEGER DEFAULT 0,
                            cache_hit BOOLEAN DEFAULT FALSE,
                            metadata TEXT DEFAULT '{}',
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

                    # 创建批量处理记录表
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS batch_processing_records (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            batch_name TEXT NOT NULL,
                            total_files INTEGER NOT NULL,
                            processed_files INTEGER DEFAULT 0,
                            successful_files INTEGER DEFAULT 0,
                            failed_files INTEGER DEFAULT 0,
                            processing_status TEXT DEFAULT 'pending',
                            start_time DATETIME,
                            end_time DATETIME,
                            total_duration_ms REAL DEFAULT 0,
                            error_summary TEXT,
                            configuration TEXT DEFAULT '{}',
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

                    # 创建索引
                    self._create_indexes(conn)
                    
                    # 插入默认设置
                    self._insert_default_settings(conn)
                    
                logger.info(f"Database initialized successfully at {self.db_path}")
                
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                raise
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """创建数据库索引"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_document_records_type ON document_records(document_type)",
            "CREATE INDEX IF NOT EXISTS idx_document_records_status ON document_records(processing_status)",
            "CREATE INDEX IF NOT EXISTS idx_document_records_created ON document_records(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_personal_templates_type ON personal_templates(document_type)",
            "CREATE INDEX IF NOT EXISTS idx_personal_templates_category ON personal_templates(template_category)",
            "CREATE INDEX IF NOT EXISTS idx_processing_results_document ON processing_results(document_record_id)",
            "CREATE INDEX IF NOT EXISTS idx_app_settings_key ON app_settings(setting_key)",
            # 性能记录表索引
            "CREATE INDEX IF NOT EXISTS idx_performance_records_operation ON performance_records(operation)",
            "CREATE INDEX IF NOT EXISTS idx_performance_records_created ON performance_records(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_performance_records_success ON performance_records(success)",
            "CREATE INDEX IF NOT EXISTS idx_performance_records_api ON performance_records(api_endpoint)",
            # 批量处理记录表索引
            "CREATE INDEX IF NOT EXISTS idx_batch_processing_status ON batch_processing_records(processing_status)",
            "CREATE INDEX IF NOT EXISTS idx_batch_processing_created ON batch_processing_records(created_at)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
    
    def _insert_default_settings(self, conn: sqlite3.Connection):
        """插入默认应用设置"""
        default_settings = [
            ('app_version', '1.0.0', 'string'),
            ('default_api_type', 'xingcheng', 'string'),
            ('max_file_size_mb', '50', 'number'),
            ('auto_save_templates', 'true', 'boolean'),
            ('processing_timeout_seconds', '300', 'number'),
            ('ui_theme', 'light', 'string'),
            ('language', 'zh-CN', 'string')
        ]
        
        for key, value, setting_type in default_settings:
            conn.execute("""
                INSERT OR IGNORE INTO app_settings (setting_key, setting_value, setting_type)
                VALUES (?, ?, ?)
            """, (key, value, setting_type))
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """执行查询并返回结果"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新操作并返回影响的行数"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """执行插入操作并返回新记录的ID"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            return cursor.lastrowid
    
    def get_table_info(self, table_name: str) -> list:
        """获取表结构信息"""
        return self.execute_query(f"PRAGMA table_info({table_name})")
    
    def backup_database(self, backup_path: str) -> bool:
        """备份数据库"""
        try:
            with self.get_connection() as source:
                backup_conn = sqlite3.connect(backup_path)
                source.backup(backup_conn)
                backup_conn.close()
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        stats = {}
        
        try:
            with self.get_connection() as conn:
                # 获取各表的记录数
                tables = ['app_settings', 'document_records', 'personal_templates', 'processing_results']
                for table in tables:
                    result = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                    stats[f"{table}_count"] = result[0] if result else 0
                
                # 获取数据库文件大小
                stats['db_file_size'] = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                # 获取最近处理的文档数量
                result = conn.execute("""
                    SELECT COUNT(*) FROM document_records 
                    WHERE created_at > datetime('now', '-7 days')
                """).fetchone()
                stats['recent_documents'] = result[0] if result else 0
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            stats['error'] = str(e)
        
        return stats
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')


# 全局数据库管理器实例
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """获取全局数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
