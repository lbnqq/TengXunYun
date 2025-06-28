#!/usr/bin/env python3
"""
测试缺失方法的修复
验证 handle_style_change 和 generate_review_report 方法的实现
"""

import os
import sys
import json
import unittest
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.tools.writing_style_analyzer import WritingStyleAnalyzer
from src.core.tools.virtual_reviewer import EnhancedVirtualReviewerTool


class TestMissingMethodsFix(unittest.TestCase):
    """测试缺失方法的修复"""
    
    def setUp(self):
        """测试初始化"""
        # 创建测试目录
        self.test_dir = project_root / "test_storage" / "missing_methods_test"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化文风分析器
        self.style_analyzer = WritingStyleAnalyzer(
            storage_path=str(self.test_dir / "style_templates")
        )
        
        # 初始化虚拟评审器
        self.reviewer = EnhancedVirtualReviewerTool(
            llm_client=None,  # 不使用LLM进行测试
            knowledge_base={
                "roles": [
                    {
                        "role_name": "editor",
                        "background": "Professional editor with 10+ years experience",
                        "expertise": ["grammar", "style", "clarity"]
                    }
                ],
                "review_criteria": {
                    "editorial": {
                        "grammar": "Grammar and punctuation",
                        "style": "Writing style and tone",
                        "clarity": "Clarity and readability"
                    }
                }
            }
        )
        
        # 测试数据
        self.test_content = """
        这是一个测试文档。我觉得这个文档挺好的，应该可以用。
        我们用了很多技术，算了一下效果不错。
        总的来说，这个方案应该能用。
        """
        
        self.session_id = "test_session_123"
        self.change_id = "change_001"
    
    def tearDown(self):
        """测试清理"""
        # 清理测试文件
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_handle_style_change_method_exists(self):
        """测试 handle_style_change 方法是否存在"""
        print("🔍 测试 handle_style_change 方法是否存在...")
        
        # 检查方法是否存在
        self.assertTrue(hasattr(self.style_analyzer, 'handle_style_change'))
        self.assertTrue(callable(getattr(self.style_analyzer, 'handle_style_change')))
        
        print("✅ handle_style_change 方法存在")
    
    def test_handle_style_change_parameter_validation(self):
        """测试 handle_style_change 参数验证"""
        print("🔍 测试 handle_style_change 参数验证...")
        
        # 测试无效操作
        result = self.style_analyzer.handle_style_change(
            session_id=self.session_id,
            change_id=self.change_id,
            action="invalid_action"
        )
        
        self.assertFalse(result.get("success", True))
        self.assertIn("不支持的操作", result.get("error", ""))
        
        print("✅ 参数验证测试通过")
    
    def test_handle_style_change_session_not_found(self):
        """测试 handle_style_change 会话不存在的情况"""
        print("🔍 测试 handle_style_change 会话不存在...")
        
        result = self.style_analyzer.handle_style_change(
            session_id="non_existent_session",
            change_id=self.change_id,
            action="accept"
        )
        
        self.assertFalse(result.get("success", True))
        self.assertIn("会话文件不存在", result.get("error", ""))
        
        print("✅ 会话不存在测试通过")
    
    def test_generate_review_report_method_exists(self):
        """测试 generate_review_report 方法是否存在"""
        print("🔍 测试 generate_review_report 方法是否存在...")
        
        # 检查方法是否存在
        self.assertTrue(hasattr(self.reviewer, 'generate_review_report'))
        self.assertTrue(callable(getattr(self.reviewer, 'generate_review_report')))
        
        print("✅ generate_review_report 方法存在")
    
    def test_generate_review_report_empty_content(self):
        """测试 generate_review_report 空内容处理"""
        print("🔍 测试 generate_review_report 空内容处理...")
        
        result = self.reviewer.generate_review_report(
            document_content="",
            reviewer_role_name="editor"
        )
        
        self.assertFalse(result.get("success", True))
        self.assertIn("文档内容为空", result.get("error", ""))
        
        print("✅ 空内容处理测试通过")
    
    def test_generate_review_report_success(self):
        """测试 generate_review_report 成功生成报告"""
        print("🔍 测试 generate_review_report 成功生成报告...")
        
        result = self.reviewer.generate_review_report(
            document_content=self.test_content,
            reviewer_role_name="editor",
            review_focus="文档质量评估"
        )
        
        self.assertTrue(result.get("success", False))
        self.assertIn("report_id", result)
        self.assertIn("executive_summary", result)
        self.assertIn("recommendations", result)
        self.assertIn("approval_status", result)
        
        # 检查报告结构
        report = result
        self.assertIsInstance(report["document_info"], dict)
        self.assertIsInstance(report["reviewer_info"], dict)
        self.assertIsInstance(report["executive_summary"], dict)
        self.assertIsInstance(report["recommendations"], list)
        self.assertIsInstance(report["next_steps"], list)
        
        print("✅ 报告生成测试通过")
        print(f"   报告ID: {report['report_id']}")
        print(f"   文档字数: {report['document_info']['word_count']}")
        print(f"   审批状态: {report['approval_status']['status']}")
    
    def test_generate_review_report_with_detailed_analysis(self):
        """测试 generate_review_report 包含详细分析"""
        print("🔍 测试 generate_review_report 包含详细分析...")
        
        result = self.reviewer.generate_review_report(
            document_content=self.test_content,
            reviewer_role_name="editor",
            include_detailed_analysis=True
        )
        
        self.assertTrue(result.get("success", False))
        self.assertIn("detailed_analysis", result)
        
        detailed_analysis = result["detailed_analysis"]
        self.assertIn("document_characteristics", detailed_analysis)
        self.assertIn("style_analysis", detailed_analysis)
        self.assertIn("structure_analysis", detailed_analysis)
        self.assertIn("content_quality_analysis", detailed_analysis)
        
        print("✅ 详细分析测试通过")
    
    def test_generate_review_report_without_detailed_analysis(self):
        """测试 generate_review_report 不包含详细分析"""
        print("🔍 测试 generate_review_report 不包含详细分析...")
        
        result = self.reviewer.generate_review_report(
            document_content=self.test_content,
            reviewer_role_name="editor",
            include_detailed_analysis=False
        )
        
        self.assertTrue(result.get("success", False))
        self.assertNotIn("detailed_analysis", result)
        
        print("✅ 不包含详细分析测试通过")
    
    def test_method_signatures(self):
        """测试方法签名"""
        print("🔍 测试方法签名...")
        
        # 检查 handle_style_change 方法签名
        import inspect
        handle_style_change_sig = inspect.signature(self.style_analyzer.handle_style_change)
        params = list(handle_style_change_sig.parameters.keys())
        
        self.assertIn("session_id", params)
        self.assertIn("change_id", params)
        self.assertIn("action", params)
        
        # 检查 generate_review_report 方法签名
        generate_report_sig = inspect.signature(self.reviewer.generate_review_report)
        params = list(generate_report_sig.parameters.keys())
        
        self.assertIn("document_content", params)
        self.assertIn("reviewer_role_name", params)
        self.assertIn("review_focus", params)
        self.assertIn("custom_criteria", params)
        self.assertIn("include_detailed_analysis", params)
        
        print("✅ 方法签名测试通过")
    
    def test_return_types(self):
        """测试返回类型"""
        print("🔍 测试返回类型...")
        
        # 测试 handle_style_change 返回类型
        result = self.style_analyzer.handle_style_change(
            session_id="test",
            change_id="test",
            action="accept"
        )
        self.assertIsInstance(result, dict)
        
        # 测试 generate_review_report 返回类型
        result = self.reviewer.generate_review_report(
            document_content="测试内容",
            reviewer_role_name="editor"
        )
        self.assertIsInstance(result, dict)
        
        print("✅ 返回类型测试通过")


def run_missing_methods_tests():
    """运行缺失方法修复测试"""
    print("🚀 开始测试缺失方法修复...")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMissingMethodsFix)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 生成测试报告
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！缺失方法修复成功。")
        return True
    else:
        print("\n❌ 部分测试失败，需要进一步检查。")
        return False


if __name__ == "__main__":
    success = run_missing_methods_tests()
    sys.exit(0 if success else 1) 