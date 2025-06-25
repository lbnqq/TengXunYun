#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集成测试模块
测试格式对齐和文风对齐功能的集成使用场景
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.tools.document_format_extractor import DocumentFormatExtractor
from src.core.tools.writing_style_analyzer import WritingStyleAnalyzer
from src.core.tools.format_alignment_coordinator import FormatAlignmentCoordinator


class TestIntegration(unittest.TestCase):
    """集成测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.format_extractor = DocumentFormatExtractor(storage_path=os.path.join(self.temp_dir, "formats"))
        self.style_analyzer = WritingStyleAnalyzer(storage_path=os.path.join(self.temp_dir, "styles"))
        
        # 创建协调器（模拟会话状态）
        self.coordinator = FormatAlignmentCoordinator()
        self.coordinator.session_state = {
            "uploaded_documents": {},
            "format_templates": [],
            "style_templates": []
        }
        
        # 测试文档
        self.test_documents = {
            "source_doc.txt": """
项目介绍
这是一个重要的项目。

主要内容
1. 需求分析
2. 方案设计
3. 实施计划

预期效果
通过项目实施，将显著提升效率。
            """.strip(),
            
            "target_format.txt": """
一、项目概述
本项目旨在提升公司整体运营效率。

二、实施方案
（一）技术方案
我们将采用先进的技术架构。

（二）人员安排
1. 项目经理：负责整体协调
2. 技术负责人：负责技术实施

三、预期收益
预计可以提升效率30%，降低成本20%。
            """.strip(),
            
            "style_reference.txt": """
根据公司发展战略，我们制定了全面的数字化转型方案。
该方案包含技术升级、流程优化和人员培训三个核心模块。
通过系统性的改进措施，预计可以提升整体运营效率25%。
我们将建立完善的监控体系，确保各项目标的达成。
            """.strip()
        }
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_format_extraction_and_application(self):
        """测试格式提取和应用的完整流程"""
        # 1. 提取目标格式
        target_format = self.format_extractor.extract_format_from_document(
            self.test_documents["target_format.txt"],
            "目标格式文档"
        )
        
        self.assertNotIn("error", target_format)
        self.assertIn("template_id", target_format)
        
        # 2. 保存格式模板
        save_result = self.format_extractor.save_format_template(target_format)
        self.assertTrue(save_result["success"])
        
        # 3. 应用格式到源文档
        alignment_result = self.format_extractor.align_document_format(
            self.test_documents["source_doc.txt"],
            target_format["template_id"]
        )
        
        self.assertTrue(alignment_result["success"])
        self.assertIn("aligned_content", alignment_result)
        self.assertIn("html_output", alignment_result)
    
    def test_style_analysis_and_application(self):
        """测试文风分析和应用的完整流程"""
        # 1. 分析参考文档的文风
        style_analysis = self.style_analyzer.analyze_writing_style(
            self.test_documents["style_reference.txt"],
            "参考文风文档"
        )
        
        self.assertNotIn("error", style_analysis)
        self.assertIn("style_type", style_analysis)
        self.assertIn("style_prompt", style_analysis)
        
        # 2. 保存文风模板
        save_result = self.style_analyzer.save_style_template(style_analysis)
        self.assertTrue(save_result["success"])
        
        # 3. 验证文风应用效果
        test_generated_content = """
        基于公司战略规划，我们开发了综合性的转型计划。
        此计划涵盖技术提升、流程改进和培训发展三大领域。
        预期通过这些举措，能够提高运营效率20%。
        我们会设立监控系统，保证目标的实现。
        """
        
        validation_result = self.style_analyzer.validate_style_application(
            self.test_documents["style_reference.txt"],
            test_generated_content,
            style_analysis["style_type"],
            style_analysis["style_features"]
        )
        
        self.assertTrue(validation_result["success"])
        self.assertIn("consistency_score", validation_result)
        self.assertIn("improvement_suggestions", validation_result)
    
    def test_coordinator_workflow(self):
        """测试协调器的完整工作流程"""
        # 模拟上传文档
        self.coordinator.session_state["uploaded_documents"] = {
            "源文档.txt": self.test_documents["source_doc.txt"],
            "目标格式.txt": self.test_documents["target_format.txt"]
        }
        
        # 执行格式对齐
        alignment_result = self.coordinator.align_documents_format(
            "源文档.txt", "目标格式.txt"
        )
        
        # 验证结果
        self.assertIn("success", alignment_result)
        if alignment_result.get("success"):
            self.assertIn("aligned_content", alignment_result)
            self.assertIn("template_id", alignment_result)
            self.assertIn("actions", alignment_result)
    
    def test_template_management(self):
        """测试模板管理功能"""
        # 创建多个格式模板
        format_templates = []
        for i, (doc_name, content) in enumerate(self.test_documents.items()):
            if i < 2:  # 只创建前两个
                format_data = self.format_extractor.extract_format_from_document(
                    content, f"模板{i+1}"
                )
                self.format_extractor.save_format_template(format_data)
                format_templates.append(format_data["template_id"])
        
        # 创建多个文风模板
        style_templates = []
        for i, (doc_name, content) in enumerate(self.test_documents.items()):
            if i < 2:  # 只创建前两个
                style_data = self.style_analyzer.analyze_writing_style(
                    content, f"文风模板{i+1}"
                )
                self.style_analyzer.save_style_template(style_data)
                style_templates.append(style_data["template_id"])
        
        # 验证模板列表
        format_list = self.format_extractor.list_format_templates()
        style_list = self.style_analyzer.list_style_templates()
        
        self.assertGreaterEqual(len(format_list), 2)
        self.assertGreaterEqual(len(style_list), 2)
        
        # 验证模板加载
        for template_id in format_templates:
            loaded = self.format_extractor.load_format_template(template_id)
            self.assertNotIn("error", loaded)
        
        for template_id in style_templates:
            loaded = self.style_analyzer.load_style_template(template_id)
            self.assertNotIn("error", loaded)
    
    def test_error_recovery(self):
        """测试错误恢复机制"""
        # 测试格式对齐中的错误处理
        alignment_result = self.coordinator.align_documents_format(
            "不存在的源文档.txt", "不存在的目标文档.txt"
        )
        self.assertIn("error", alignment_result)
        
        # 测试使用不存在的模板
        invalid_alignment = self.format_extractor.align_document_format(
            "测试内容", "无效模板ID"
        )
        self.assertIn("error", invalid_alignment)
        
        # 测试文风验证中的错误处理
        invalid_validation = self.style_analyzer.validate_style_application(
            "", "", "invalid_style", {}
        )
        # 应该能处理而不崩溃
        self.assertIsInstance(invalid_validation, dict)
    
    def test_performance_with_large_content(self):
        """测试大内容的处理性能"""
        # 生成大文档内容
        large_content = "\n".join([
            f"第{i}段：这是一个测试段落，用来验证系统处理大文档的能力。" * 10
            for i in range(100)
        ])
        
        # 测试格式提取性能
        import time
        start_time = time.time()
        
        format_result = self.format_extractor.extract_format_from_document(
            large_content, "大文档测试"
        )
        
        format_time = time.time() - start_time
        
        # 验证结果正确性
        self.assertNotIn("error", format_result)
        
        # 测试文风分析性能
        start_time = time.time()
        
        style_result = self.style_analyzer.analyze_writing_style(
            large_content, "大文档文风测试"
        )
        
        style_time = time.time() - start_time
        
        # 验证结果正确性
        self.assertNotIn("error", style_result)
        
        # 性能要求：处理时间应该在合理范围内（这里设为10秒）
        self.assertLess(format_time, 10.0, f"格式提取耗时过长: {format_time:.2f}秒")
        self.assertLess(style_time, 10.0, f"文风分析耗时过长: {style_time:.2f}秒")
    
    def test_concurrent_operations(self):
        """测试并发操作的安全性"""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # 每个线程处理不同的文档
                content = f"线程{worker_id}的测试文档内容。" * 50
                
                # 格式提取
                format_result = self.format_extractor.extract_format_from_document(
                    content, f"线程{worker_id}格式测试"
                )
                
                # 文风分析
                style_result = self.style_analyzer.analyze_writing_style(
                    content, f"线程{worker_id}文风测试"
                )
                
                results.append({
                    "worker_id": worker_id,
                    "format_success": "error" not in format_result,
                    "style_success": "error" not in style_result
                })
                
            except Exception as e:
                errors.append(f"线程{worker_id}出错: {str(e)}")
        
        # 启动多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=30)  # 30秒超时
        
        # 验证结果
        self.assertEqual(len(errors), 0, f"并发操作出现错误: {errors}")
        self.assertEqual(len(results), 5, "并非所有线程都完成了操作")
        
        # 验证所有操作都成功
        for result in results:
            self.assertTrue(result["format_success"], f"线程{result['worker_id']}格式提取失败")
            self.assertTrue(result["style_success"], f"线程{result['worker_id']}文风分析失败")


if __name__ == '__main__':
    unittest.main()
