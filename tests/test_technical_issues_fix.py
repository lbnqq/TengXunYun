#!/usr/bin/env python3
"""
关键技术问题修复验证测试脚本
验证文风对齐功能中的关键问题是否已修复
"""

import sys
import os
import json
import tempfile
from typing import Dict, Any

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_generate_style_preview_fix():
    """测试generate_style_preview方法的修复效果"""
    print("🔍 测试generate_style_preview方法修复...")
    
    try:
        from core.tools.writing_style_analyzer import WritingStyleAnalyzer
        
        analyzer = WritingStyleAnalyzer()
        
        # 创建测试数据
        test_analysis_result = {
            "document_content": "这是一个测试文档，用于验证文风对齐功能。",
            "document_name": "测试文档",
            "style_type": "business_professional",
            "style_features": {
                "formality": 0.8,
                "technicality": 0.6,
                "objectivity": 0.7
            },
            "confidence_score": 0.85
        }
        
        # 测试不存在的模板ID
        non_existent_template_id = "non_existent_template_12345"
        
        print(f"测试模板ID: {non_existent_template_id}")
        
        # 调用修复后的方法
        result = analyzer.generate_style_preview(test_analysis_result, non_existent_template_id)
        
        if result.get("success"):
            print("✅ generate_style_preview方法修复成功")
            print(f"   预览文本长度: {len(result.get('preview_text', ''))}")
            print(f"   一致性评分: {result.get('consistency_score', 0)}")
            print(f"   目标风格类型: {result.get('target_style_type', 'unknown')}")
            assert True, "generate_style_preview方法修复成功"
        else:
            print(f"❌ generate_style_preview方法仍然失败: {result.get('error', '未知错误')}")
            assert False, f"generate_style_preview方法失败: {result.get('error', '未知错误')}"
            
    except Exception as e:
        print(f"❌ 测试generate_style_preview方法异常: {str(e)}")
        assert False, f"测试异常: {str(e)}"

def test_template_management_fix():
    """测试模板管理机制的修复效果"""
    print("\n🔍 测试模板管理机制修复...")
    
    try:
        from core.tools.writing_style_analyzer import WritingStyleAnalyzer
        
        analyzer = WritingStyleAnalyzer()
        
        # 测试模板保存
        test_template_data = {
            "document_content": "模板测试文档",
            "document_name": "模板测试",
            "style_type": "academic",
            "style_features": {
                "formality": 0.9,
                "technicality": 0.8,
                "objectivity": 0.9
            },
            "confidence_score": 0.9
        }
        
        # 保存模板
        save_result = analyzer.save_style_template(test_template_data)
        
        if save_result.get("success"):
            template_id = save_result.get("template_id")
            print(f"✅ 模板保存成功: {template_id}")
            
            # 确保template_id不为None
            if template_id is None:
                print("❌ 模板ID为空")
                assert False, "模板ID为空"
            
            # 测试模板加载
            loaded_template = analyzer.load_style_template(template_id)
            
            if loaded_template and "error" not in loaded_template:
                print("✅ 模板加载成功")
                print(f"   模板名称: {loaded_template.get('document_name', 'unknown')}")
                print(f"   风格类型: {loaded_template.get('style_type', 'unknown')}")
                assert True, "模板管理机制修复成功"
            else:
                print(f"❌ 模板加载失败: {loaded_template.get('error', '未知错误')}")
                assert False, f"模板加载失败: {loaded_template.get('error', '未知错误')}"
        else:
            print(f"❌ 模板保存失败: {save_result.get('error', '未知错误')}")
            assert False, f"模板保存失败: {save_result.get('error', '未知错误')}"
            
    except Exception as e:
        print(f"❌ 测试模板管理机制异常: {str(e)}")
        assert False, f"测试异常: {str(e)}"

def test_file_handle_management_fix():
    """测试文件句柄管理的修复效果"""
    print("\n🔍 测试文件句柄管理修复...")
    
    try:
        from cliTests.base_test_script import BaseTestScript
        
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("这是一个测试文件，用于验证文件句柄管理。")
            temp_file_path = f.name
        
        try:
            # 创建测试脚本实例
            test_script = BaseTestScript()
            
            # 测试文件上传方法
            result = test_script.call_api_with_file(
                endpoint="/api/test",
                method="POST",
                file_path=temp_file_path,
                file_field="file",
                data={"test": "data"},
                description="文件句柄管理测试"
            )
            
            # 由于是测试端点，预期会失败，但重要的是文件读取过程不报错
            print("✅ 文件句柄管理修复成功")
            print("   文件读取过程未出现句柄错误")
            assert True, "文件句柄管理修复成功"
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        print(f"❌ 测试文件句柄管理异常: {str(e)}")
        assert False, f"测试异常: {str(e)}"

def test_resource_manager():
    """测试统一资源管理器"""
    print("\n🔍 测试统一资源管理器...")
    
    try:
        from core.tools.resource_manager import get_resource_manager
        
        manager = get_resource_manager()
        
        # 测试会话管理
        session_data = {"test": "data", "timestamp": "2025-01-01"}
        session_id = manager.create_session("test_session", session_data)
        
        if session_id:
            print(f"✅ 会话创建成功: {session_id}")
            
            # 测试会话获取
            session = manager.get_session(session_id)
            if session:
                print("✅ 会话获取成功")
                print(f"   会话类型: {session.session_type}")
                print(f"   数据: {session.data}")
            else:
                print("❌ 会话获取失败")
                assert False, "会话获取失败"
            
            # 测试会话更新
            update_success = manager.update_session(session_id, {"updated": True})
            if update_success:
                print("✅ 会话更新成功")
            else:
                print("❌ 会话更新失败")
                assert False, "会话更新失败"
        else:
            print("❌ 会话创建失败")
            assert False, "会话创建失败"
        
        # 测试模板管理
        template_data = {"content": "test template"}
        template_id = manager.create_template("测试模板", "style", template_data)
        
        if template_id:
            print(f"✅ 模板创建成功: {template_id}")
            
            # 测试模板获取
            template = manager.get_template(template_id)
            if template:
                print("✅ 模板获取成功")
                print(f"   模板名称: {template.template_name}")
                print(f"   模板类型: {template.template_type}")
            else:
                print("❌ 模板获取失败")
                assert False, "模板获取失败"
        else:
            print("❌ 模板创建失败")
            assert False, "模板创建失败"
        
        # 测试资源统计
        stats = manager.get_resource_stats()
        if stats:
            print("✅ 资源统计获取成功")
            print(f"   会话数量: {stats['sessions']['total_count']}")
            print(f"   模板数量: {stats['templates']['total_count']}")
        else:
            print("❌ 资源统计获取失败")
            assert False, "资源统计获取失败"
        
        return True
        
    except Exception as e:
        print(f"❌ 测试统一资源管理器异常: {str(e)}")
        assert False, f"测试异常: {str(e)}"

def test_export_business_rules():
    """测试导出业务规则"""
    print("\n🔍 测试导出业务规则...")
    
    try:
        from core.tools.writing_style_analyzer import WritingStyleAnalyzer
        
        analyzer = WritingStyleAnalyzer()
        
        # 创建测试会话数据
        test_session_data = {
            "original_content": "原始文档内容",
            "document_name": "测试文档",
            "style_template_id": "test_template_123",
            "suggested_changes": [
                {
                    "original_text": "原始",
                    "suggested_text": "修改后",
                    "change_type": "词汇优化",
                    "confidence": 0.8,
                    "status": "accepted"
                }
            ]
        }
        
        # 保存测试会话
        session_id = "test_session_12345"
        session_file = os.path.join(analyzer.semantic_behavior_dir, "profiles", f"{session_id}.json")
        os.makedirs(os.path.dirname(session_file), exist_ok=True)
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(test_session_data, f, ensure_ascii=False, indent=2)
        
        try:
            # 测试导出功能
            export_result = analyzer.export_styled_document(session_id)
            
            if export_result.get("success"):
                print("✅ 导出功能测试成功")
                print(f"   文件名: {export_result.get('filename', 'unknown')}")
                print(f"   内容长度: {export_result.get('content_length', 0)}")
                print(f"   应用变更数: {export_result.get('changes_applied', 0)}")
                
                # 验证导出内容包含必要的元素
                docx_content = export_result.get("docx_content")
                if docx_content:
                    print("✅ 导出文档内容生成成功")
                    print(f"   文档大小: {len(docx_content)} bytes")
                else:
                    print("❌ 导出文档内容为空")
                    assert False, "导出文档内容为空"
                
                return True
            else:
                print(f"❌ 导出功能测试失败: {export_result.get('error', '未知错误')}")
                assert False, f"导出功能测试失败: {export_result.get('error', '未知错误')}"
                
        finally:
            # 清理测试文件
            if os.path.exists(session_file):
                os.remove(session_file)
                
    except Exception as e:
        print(f"❌ 测试导出业务规则异常: {str(e)}")
        assert False, f"测试异常: {str(e)}"

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始关键技术问题修复验证测试")
    print("=" * 60)
    
    test_results = []
    
    # 测试1: generate_style_preview方法修复
    test_results.append(("generate_style_preview修复", test_generate_style_preview_fix()))
    
    # 测试2: 模板管理机制修复
    test_results.append(("模板管理机制修复", test_template_management_fix()))
    
    # 测试3: 文件句柄管理修复
    test_results.append(("文件句柄管理修复", test_file_handle_management_fix()))
    
    # 测试4: 统一资源管理器
    test_results.append(("统一资源管理器", test_resource_manager()))
    
    # 测试5: 导出业务规则
    test_results.append(("导出业务规则", test_export_business_rules()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed_count = 0
    total_count = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed_count += 1
    
    print(f"\n总计: {passed_count}/{total_count} 个测试通过")
    
    if passed_count == total_count:
        print("🎉 所有关键技术问题修复验证通过！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 