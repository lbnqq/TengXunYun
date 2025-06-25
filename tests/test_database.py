#!/usr/bin/env python3
"""
数据库功能测试脚本
测试SQLite数据库的各项功能
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
    TemplateRepository,
    ProcessingResultRepository,
    DocumentRecord,
    PersonalTemplate,
    ProcessingResult,
    DocumentType,
    IntentType,
    ProcessingStatus
)

def test_database_initialization():
    """测试数据库初始化"""
    print("🔧 测试数据库初始化...")

    # 使用临时文件作为测试数据库
    import tempfile
    temp_dir = tempfile.gettempdir()
    test_db_path = os.path.join(temp_dir, f"test_db_{os.getpid()}.db")

    try:
        # 创建数据库管理器
        db_manager = DatabaseManager(test_db_path)

        # 检查表是否创建成功
        tables = ['app_settings', 'document_records', 'personal_templates', 'processing_results']
        for table in tables:
            table_info = db_manager.get_table_info(table)
            assert len(table_info) > 0, f"Table {table} not created"

        # 获取数据库统计信息
        stats = db_manager.get_database_stats()
        print(f"✅ 数据库初始化成功，统计信息: {stats}")

        # 关闭数据库连接
        db_manager.close()

        return True

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        raise
    finally:
        # 清理测试文件
        try:
            if os.path.exists(test_db_path):
                os.unlink(test_db_path)
        except:
            pass  # 忽略清理错误

def test_app_settings():
    """测试应用设置功能"""
    print("\n⚙️ 测试应用设置功能...")

    temp_dir = tempfile.gettempdir()
    test_db_path = os.path.join(temp_dir, f"test_settings_{os.getpid()}.db")

    try:
        db_manager = DatabaseManager(test_db_path)
        settings_repo = AppSettingsRepository()

        # 测试设置和获取字符串值
        settings_repo.set_setting('test_string', 'hello world')
        value = settings_repo.get_setting('test_string')
        assert value == 'hello world', f"Expected 'hello world', got {value}"

        # 测试设置和获取布尔值
        settings_repo.set_setting('test_bool', True)
        value = settings_repo.get_setting('test_bool')
        assert value is True, f"Expected True, got {value}"

        # 测试设置和获取数字值
        settings_repo.set_setting('test_number', 42)
        value = settings_repo.get_setting('test_number')
        assert value == 42, f"Expected 42, got {value}"

        # 测试设置和获取JSON值
        test_dict = {'key': 'value', 'number': 123}
        settings_repo.set_setting('test_json', test_dict)
        value = settings_repo.get_setting('test_json')
        assert value == test_dict, f"Expected {test_dict}, got {value}"

        # 测试获取所有设置
        all_settings = settings_repo.get_all_settings()
        assert 'test_string' in all_settings
        assert 'test_bool' in all_settings
        assert 'test_number' in all_settings
        assert 'test_json' in all_settings

        print("✅ 应用设置功能测试通过")

        # 关闭数据库连接
        db_manager.close()

    except Exception as e:
        print(f"❌ 应用设置功能测试失败: {e}")
        raise
    finally:
        try:
            if os.path.exists(test_db_path):
                os.unlink(test_db_path)
        except:
            pass

def test_document_records():
    """测试文档记录功能"""
    print("\n📄 测试文档记录功能...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        db_manager = DatabaseManager(test_db_path)
        doc_repo = DocumentRepository()
        
        # 创建测试文档记录
        test_content = "这是一个测试文档"
        file_hash = hashlib.md5(test_content.encode()).hexdigest()
        
        record = DocumentRecord(
            original_filename="test_document.txt",
            file_path="/tmp/test_document.txt",
            file_size=len(test_content),
            file_hash=file_hash,
            document_type=DocumentType.GENERAL_DOCUMENT,
            intent_type=IntentType.GENERAL_PROCESSING,
            processing_status=ProcessingStatus.PENDING,
            confidence_score=0.85
        )
        
        # 创建记录
        record_id = doc_repo.create_document_record(record)
        assert record_id is not None, "Failed to create document record"
        print(f"✅ 创建文档记录成功，ID: {record_id}")
        
        # 获取记录
        retrieved_record = doc_repo.get_document_record(record_id)
        assert retrieved_record is not None, "Failed to retrieve document record"
        assert retrieved_record.original_filename == "test_document.txt"
        assert retrieved_record.file_hash == file_hash
        print("✅ 获取文档记录成功")
        
        # 更新处理状态
        success = doc_repo.update_processing_status(
            record_id, 
            ProcessingStatus.COMPLETED, 
            processing_time_ms=5000
        )
        assert success, "Failed to update processing status"
        
        # 验证状态更新
        updated_record = doc_repo.get_document_record(record_id)
        assert updated_record.processing_status == ProcessingStatus.COMPLETED
        assert updated_record.processing_time_ms == 5000
        assert updated_record.completed_at is not None
        print("✅ 更新处理状态成功")
        
        # 测试处理历史
        history = doc_repo.get_processing_history(limit=10)
        assert len(history) >= 1, "Processing history should contain at least one record"
        print(f"✅ 获取处理历史成功，共 {len(history)} 条记录")
        
        # 测试统计信息
        stats = doc_repo.get_statistics()
        assert stats['total_documents'] >= 1
        assert stats['completed_documents'] >= 1
        print(f"✅ 获取统计信息成功: {stats}")
        
    except Exception as e:
        print(f"❌ 文档记录功能测试失败: {e}")
        raise
    finally:
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)

def test_template_management():
    """测试模板管理功能"""
    print("\n📋 测试模板管理功能...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        db_manager = DatabaseManager(test_db_path)
        template_repo = TemplateRepository()
        
        # 创建测试模板
        template = PersonalTemplate(
            template_name="标准报告格式",
            document_type=DocumentType.TECHNICAL_REPORT,
            template_category="paragraph",
            usage_count=0,
            is_favorite=False
        )
        
        # 设置模板配置
        config = {
            "font_family": "宋体",
            "font_size": 12,
            "line_spacing": 1.5,
            "paragraph_spacing": 6
        }
        template.set_config(config)
        
        # 创建模板
        template_id = template_repo.create_template(template)
        assert template_id is not None, "Failed to create template"
        print(f"✅ 创建模板成功，ID: {template_id}")
        
        # 获取模板列表
        templates = template_repo.get_templates()
        assert len(templates) >= 1, "Template list should contain at least one template"
        
        created_template = templates[0]
        assert created_template.template_name == "标准报告格式"
        assert created_template.get_config() == config
        print("✅ 获取模板列表成功")
        
        # 按文档类型获取模板
        report_templates = template_repo.get_templates(document_type=DocumentType.TECHNICAL_REPORT)
        assert len(report_templates) >= 1
        print("✅ 按文档类型获取模板成功")
        
        # 更新模板使用次数
        success = template_repo.update_template_usage(template_id)
        assert success, "Failed to update template usage"
        
        # 验证使用次数更新
        updated_templates = template_repo.get_templates()
        updated_template = next(t for t in updated_templates if t.id == template_id)
        assert updated_template.usage_count == 1
        assert updated_template.last_used_at is not None
        print("✅ 更新模板使用次数成功")
        
    except Exception as e:
        print(f"❌ 模板管理功能测试失败: {e}")
        raise
    finally:
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)

def test_processing_results():
    """测试处理结果功能"""
    print("\n📊 测试处理结果功能...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        db_manager = DatabaseManager(test_db_path)
        doc_repo = DocumentRepository()
        result_repo = ProcessingResultRepository()
        
        # 先创建一个文档记录
        record = DocumentRecord(
            original_filename="test.txt",
            file_path="/tmp/test.txt",
            file_size=100,
            file_hash="test_hash",
            document_type=DocumentType.GENERAL_DOCUMENT,
            intent_type=IntentType.GENERAL_PROCESSING
        )
        
        record_id = doc_repo.create_document_record(record)
        assert record_id is not None
        
        # 创建处理结果
        result = ProcessingResult(
            document_record_id=record_id,
            result_type="processed",
            file_path="/tmp/test_processed.txt",
            file_size=150
        )
        
        result_id = result_repo.create_result(result)
        assert result_id is not None, "Failed to create processing result"
        print(f"✅ 创建处理结果成功，ID: {result_id}")
        
        # 获取文档的处理结果
        results = result_repo.get_results_by_document(record_id)
        assert len(results) >= 1, "Should have at least one processing result"
        
        created_result = results[0]
        assert created_result.document_record_id == record_id
        assert created_result.result_type == "processed"
        assert created_result.file_path == "/tmp/test_processed.txt"
        print("✅ 获取处理结果成功")
        
    except Exception as e:
        print(f"❌ 处理结果功能测试失败: {e}")
        raise
    finally:
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)

def main():
    """运行所有测试"""
    print("🚀 开始数据库功能测试\n")
    
    try:
        test_database_initialization()
        test_app_settings()
        test_document_records()
        test_template_management()
        test_processing_results()
        
        print("\n🎉 所有数据库功能测试通过！")
        
    except Exception as e:
        print(f"\n💥 测试失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
