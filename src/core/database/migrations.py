"""
数据库迁移脚本
用于数据库版本升级和数据迁移
"""

import logging
import sqlite3
from typing import List, Dict, Any
from .database_manager import get_database_manager

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """数据库迁移管理器"""
    
    def __init__(self):
        self.db = get_database_manager()
        self.migrations = [
            self._migration_001_initial_schema,
            self._migration_002_add_indexes,
            self._migration_003_add_default_settings,
            # 在这里添加新的迁移函数
        ]
    
    def get_current_version(self) -> int:
        """获取当前数据库版本"""
        try:
            # 创建版本表（如果不存在）
            with self.db.get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version INTEGER PRIMARY KEY,
                        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                result = conn.execute("SELECT MAX(version) as version FROM schema_version").fetchone()
                return result['version'] if result and result['version'] else 0
        except Exception as e:
            logger.error(f"Failed to get current database version: {e}")
            return 0
    
    def apply_migrations(self) -> bool:
        """应用所有待执行的迁移"""
        current_version = self.get_current_version()
        target_version = len(self.migrations)
        
        if current_version >= target_version:
            logger.info(f"Database is up to date (version {current_version})")
            return True
        
        logger.info(f"Upgrading database from version {current_version} to {target_version}")
        
        try:
            for version in range(current_version + 1, target_version + 1):
                migration_func = self.migrations[version - 1]
                logger.info(f"Applying migration {version}: {migration_func.__name__}")
                
                if migration_func():
                    self._record_migration(version)
                    logger.info(f"Migration {version} applied successfully")
                else:
                    logger.error(f"Migration {version} failed")
                    return False
            
            logger.info("All migrations applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def _record_migration(self, version: int) -> bool:
        """记录已应用的迁移"""
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (version,)
                )
            return True
        except Exception as e:
            logger.error(f"Failed to record migration {version}: {e}")
            return False
    
    def _migration_001_initial_schema(self) -> bool:
        """迁移001: 初始数据库架构"""
        try:
            with self.db.get_connection() as conn:
                # 这个迁移在DatabaseManager初始化时已经执行
                # 这里只是为了版本控制
                pass
            return True
        except Exception as e:
            logger.error(f"Migration 001 failed: {e}")
            return False
    
    def _migration_002_add_indexes(self) -> bool:
        """迁移002: 添加性能索引"""
        try:
            with self.db.get_connection() as conn:
                # 这些索引在DatabaseManager初始化时已经创建
                # 这里只是为了版本控制
                pass
            return True
        except Exception as e:
            logger.error(f"Migration 002 failed: {e}")
            return False
    
    def _migration_003_add_default_settings(self) -> bool:
        """迁移003: 添加默认设置"""
        try:
            with self.db.get_connection() as conn:
                # 这些设置在DatabaseManager初始化时已经插入
                # 这里只是为了版本控制
                pass
            return True
        except Exception as e:
            logger.error(f"Migration 003 failed: {e}")
            return False
    
    def rollback_migration(self, target_version: int) -> bool:
        """回滚到指定版本（谨慎使用）"""
        current_version = self.get_current_version()
        
        if target_version >= current_version:
            logger.warning(f"Target version {target_version} is not lower than current version {current_version}")
            return False
        
        logger.warning(f"Rolling back database from version {current_version} to {target_version}")
        
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    "DELETE FROM schema_version WHERE version > ?",
                    (target_version,)
                )
            
            logger.info(f"Database rolled back to version {target_version}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """获取迁移历史"""
        try:
            results = self.db.execute_query("""
                SELECT version, applied_at 
                FROM schema_version 
                ORDER BY version
            """)
            
            history = []
            for row in results:
                history.append({
                    'version': row['version'],
                    'applied_at': row['applied_at'],
                    'migration_name': self.migrations[row['version'] - 1].__name__ if row['version'] <= len(self.migrations) else 'Unknown'
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []

def run_migrations():
    """运行数据库迁移的便捷函数"""
    migration = DatabaseMigration()
    return migration.apply_migrations()

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 运行迁移
    if run_migrations():
        print("✅ Database migrations completed successfully")
    else:
        print("❌ Database migrations failed")
        exit(1)
