#!/usr/bin/env python3
"""
简化的数据库功能测试脚本
"""

import os
import sys
import tempfile
import hashlib
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.database import (
    DatabaseManager, 
    AppSettingsRepository, 
    DocumentRepository, 
    DocumentRecord,
    DocumentType,
    IntentType,
    ProcessingStatus
)

def test_basic_functionality():
    """测试基础功能"""
    print("🔧 测试数据库基础功能...")
    
    # 使用内存数据库进行测试
    db_manager = DatabaseManager(":memory:")
    
    try:
        # 测试应用设置
        print("  📝 测试应用设置...")
        settings_repo = AppSettingsRepository()
        
        # 设置和获取值
        settings_repo.set_setting('test_key', 'test_value')
        value = settings_repo.get_setting('test_key')
        assert value == 'test_value', f"Expected 'test_value', got {value}"
        print("    ✅ 应用设置功能正常")
        
        # 测试文档记录
        print("  📄 测试文档记录...")
        doc_repo = DocumentRepository()
        
        # 创建文档记录
        record = DocumentRecord(
            original_filename="test.txt",
            file_path="/tmp/test.txt",
            file_size=100,
            file_hash="test_hash_123",
            document_type=DocumentType.GENERAL_DOCUMENT,
            intent_type=IntentType.GENERAL_PROCESSING,
            processing_status=ProcessingStatus.PENDING,
            confidence_score=0.85
        )
        
        record_id = doc_repo.create_document_record(record)
        assert record_id is not None, "Failed to create document record"
        print(f"    ✅ 创建文档记录成功，ID: {record_id}")
        
        # 获取文档记录
        retrieved_record = doc_repo.get_document_record(record_id)
        assert retrieved_record is not None, "Failed to retrieve document record"
        assert retrieved_record.original_filename == "test.txt"
        print("    ✅ 获取文档记录成功")
        
        # 更新处理状态
        success = doc_repo.update_processing_status(
            record_id, 
            ProcessingStatus.COMPLETED, 
            processing_time_ms=3000
        )
        assert success, "Failed to update processing status"
        print("    ✅ 更新处理状态成功")
        
        # 获取统计信息
        stats = doc_repo.get_statistics()
        assert stats['total_documents'] >= 1
        print(f"    ✅ 获取统计信息成功: {stats}")
        
        # 测试数据库统计
        print("  📊 测试数据库统计...")
        db_stats = db_manager.get_database_stats()
        print(f"    ✅ 数据库统计: {db_stats}")
        
        print("✅ 所有基础功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭数据库连接
        db_manager.close()

def test_real_database():
    """测试真实数据库文件"""
    print("\n🗄️ 测试真实数据库文件...")
    
    # 使用用户目录下的测试数据库
    user_dir = os.path.expanduser("~")
    test_dir = os.path.join(user_dir, ".office_doc_agent_test")
    os.makedirs(test_dir, exist_ok=True)
    test_db_path = os.path.join(test_dir, "test.db")
    
    try:
        # 如果测试数据库已存在，先删除
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)
        
        # 创建数据库
        db_manager = DatabaseManager(test_db_path)
        
        # 验证数据库文件创建
        assert os.path.exists(test_db_path), "Database file not created"
        print(f"  ✅ 数据库文件创建成功: {test_db_path}")
        
        # 测试基本操作
        settings_repo = AppSettingsRepository()
        settings_repo.set_setting('version', '1.0.0')
        version = settings_repo.get_setting('version')
        assert version == '1.0.0'
        print("  ✅ 数据库读写操作正常")
        
        # 获取数据库信息
        stats = db_manager.get_database_stats()
        print(f"  ✅ 数据库统计: {stats}")
        
        # 关闭数据库
        db_manager.close()
        
        # 验证数据持久化
        db_manager2 = DatabaseManager(test_db_path)
        settings_repo2 = AppSettingsRepository()
        version2 = settings_repo2.get_setting('version')
        assert version2 == '1.0.0', "Data not persisted"
        print("  ✅ 数据持久化验证成功")
        
        db_manager2.close()
        
        print("✅ 真实数据库测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 真实数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试文件
        try:
            if os.path.exists(test_db_path):
                os.unlink(test_db_path)
            if os.path.exists(test_dir):
                os.rmdir(test_dir)
        except:
            pass

def main():
    """运行测试"""
    print("🚀 开始数据库功能测试\n")
    
    success = True
    
    # 测试基础功能
    if not test_basic_functionality():
        success = False
    
    # 测试真实数据库
    if not test_real_database():
        success = False
    
    if success:
        print("\n🎉 所有数据库功能测试通过！")
        print("\n📋 测试总结:")
        print("  ✅ SQLite数据库初始化")
        print("  ✅ 应用设置管理")
        print("  ✅ 文档记录管理")
        print("  ✅ 数据持久化")
        print("  ✅ 统计信息获取")
        return True
    else:
        print("\n💥 部分测试失败！")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
