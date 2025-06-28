#!/usr/bin/env python3
"""
全面测试所有新实现的方法
包括预览、应用变化、导出功能等
"""

import os
import sys
import json
import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.tools.writing_style_analyzer import WritingStyleAnalyzer
from src.core.tools.virtual_reviewer import EnhancedVirtualReviewerTool
from src.core.tools.enhanced_document_filler import EnhancedDocumentFiller


class TestComprehensiveMethods(unittest.TestCase):
    """全面测试所有新实现的方法"""
    
    def setUp(self):
        """测试初始化"""
        # 创建测试目录
        self.test_dir = project_root / "test_storage" / "comprehensive_test"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化工具
        self.style_analyzer = WritingStyleAnalyzer(
            storage_dir=str(self.test_dir / "style_analysis")
        )
        self.reviewer = EnhancedVirtualReviewerTool(
            storage_dir=str(self.test_dir / "review")
        )
        self.document_filler = EnhancedDocumentFiller()
        
        # 测试数据
        self.test_document = """
        这是一个测试文档。
        
        我们正在测试文档处理功能。
        这个文档包含多个段落和不同的内容。
        
        测试内容包括：
        1. 文档分析
        2. 风格调整
        3. 内容填充
        4. 导出功能
        """
        
        self.test_analysis_result = {
            "document_type": "general",
            "original_content": self.test_document,
            "title": "测试文档",
            "fields": [
                {"name": "title", "type": "text", "required": True},
                {"name": "author", "type": "text", "required": True},
                {"name": "content", "type": "text", "required": True},
                {"name": "date", "type": "date", "required": False}
            ]
        }
        
        self.test_fill_data = {
            "title": "测试文档标题",
            "author": "测试作者",
            "content": "这是填充的内容",
            "date": "2024-01-01"
        }
    
    def test_handle_style_change(self):
        """测试handle_style_change方法"""
        # 创建测试session
        session_id = "test_session_001"
        session_data = {
            "original_content": self.test_document,
            "suggested_changes": [
                {
                    "change_id": "change_001",
                    "original_text": "我们",
                    "suggested_text": "本机构",
                    "status": "pending"
                }
            ]
        }
        
        # 保存session文件
        session_file = self.test_dir / "style_analysis" / "profiles" / f"{session_id}.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        # 测试接受变化
        result = self.style_analyzer.handle_style_change(session_id, "change_001", "accept")
        self.assertTrue(result["success"])
        self.assertEqual(result["action"], "accept")
        
        # 测试拒绝变化
        result = self.style_analyzer.handle_style_change(session_id, "change_001", "reject")
        self.assertTrue(result["success"])
        self.assertEqual(result["action"], "reject")
        
        # 测试无效操作
        result = self.style_analyzer.handle_style_change(session_id, "change_001", "invalid")
        self.assertFalse(result["success"])
    
    def test_apply_style_changes(self):
        """测试apply_style_changes方法"""
        # 创建测试session
        session_id = "test_session_002"
        session_data = {
            "original_content": self.test_document
        }
        
        # 保存session文件
        session_file = self.test_dir / "style_analysis" / "profiles" / f"{session_id}.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        # 测试应用变化
        changes = [
            {
                "id": "change_001",
                "type": "text_replacement",
                "data": {
                    "old_text": "我们",
                    "new_text": "本机构"
                }
            }
        ]
        
        result = self.style_analyzer.apply_style_changes(session_id, changes)
        self.assertTrue(result["success"])
        self.assertEqual(result["applied_changes_count"], 1)
        self.assertEqual(result["failed_changes_count"], 0)
    
    def test_generate_review_report(self):
        """测试generate_review_report方法"""
        # 测试生成评审报告
        result = self.reviewer.generate_review_report(
            document_content=self.test_document,
            reviewer_role_name="technical_reviewer",
            review_focus="文档质量和技术准确性"
        )
        
        self.assertTrue(result["success"])
        self.assertIn("review_summary", result)
        self.assertIn("detailed_comments", result)
        self.assertIn("quality_assessment", result)
    
    def test_generate_fill_preview(self):
        """测试generate_fill_preview方法"""
        # 测试生成填充预览
        result = self.document_filler.generate_fill_preview(
            analysis_result=self.test_analysis_result,
            user_data=self.test_fill_data
        )
        
        self.assertTrue(result["success"])
        self.assertIn("preview_content", result)
        self.assertIn("preview_report", result)
        self.assertIn("field_mapping", result)
        self.assertIn("quality_metrics", result)
    
    def test_apply_fill_changes(self):
        """测试apply_fill_changes方法"""
        # 测试应用填充变化
        result = self.document_filler.apply_fill_changes(
            analysis_result=self.test_analysis_result,
            fill_data=self.test_fill_data
        )
        
        self.assertTrue(result["success"])
        self.assertIn("final_document", result)
        self.assertIn("application_report", result)
        self.assertIn("fill_statistics", result)
        self.assertIn("quality_assessment", result)
    
    def test_export_document(self):
        """测试export_document方法"""
        # 创建测试文档
        final_document = {
            "content": self.test_document,
            "document_type": "general",
            "metadata": {
                "title": "测试文档",
                "author": "测试作者",
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            },
            "format": "text"
        }
        
        # 测试导出为TXT格式
        result = self.document_filler.export_document(
            final_document=final_document,
            export_format="txt"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["export_format"], "txt")
        self.assertIn("export_result", result)
        self.assertIn("export_report", result)
        
        # 测试导出为HTML格式
        result = self.document_filler.export_document(
            final_document=final_document,
            export_format="html"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["export_format"], "html")
    
    def test_integrated_workflow(self):
        """测试完整工作流程"""
        # 1. 生成填充预览
        preview_result = self.document_filler.generate_fill_preview(
            analysis_result=self.test_analysis_result,
            user_data=self.test_fill_data
        )
        self.assertTrue(preview_result["success"])
        
        # 2. 应用填充变化
        fill_result = self.document_filler.apply_fill_changes(
            analysis_result=self.test_analysis_result,
            fill_data=self.test_fill_data
        )
        self.assertTrue(fill_result["success"])
        
        # 3. 导出文档
        final_document = fill_result["final_document"]
        export_result = self.document_filler.export_document(
            final_document=final_document,
            export_format="txt"
        )
        self.assertTrue(export_result["success"])
        
        # 4. 生成评审报告
        review_result = self.reviewer.generate_review_report(
            document_content=final_document["content"],
            reviewer_role_name="editor"
        )
        self.assertTrue(review_result["success"])
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效的分析结果
        result = self.document_filler.generate_fill_preview(
            analysis_result={"error": "测试错误"},
            user_data=self.test_fill_data
        )
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        
        # 测试无效的导出格式
        final_document = {
            "content": self.test_document,
            "metadata": {"title": "测试"}
        }
        result = self.document_filler.export_document(
            final_document=final_document,
            export_format="invalid_format"
        )
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_quality_metrics(self):
        """测试质量指标计算"""
        # 测试预览质量
        preview_result = self.document_filler.generate_fill_preview(
            analysis_result=self.test_analysis_result,
            user_data=self.test_fill_data
        )
        
        quality_metrics = preview_result["quality_metrics"]
        self.assertIn("completeness", quality_metrics)
        self.assertIn("validation_score", quality_metrics)
        self.assertIn("consistency_score", quality_metrics)
        
        # 测试最终质量
        fill_result = self.document_filler.apply_fill_changes(
            analysis_result=self.test_analysis_result,
            fill_data=self.test_fill_data
        )
        
        quality_assessment = fill_result["quality_assessment"]
        self.assertIn("overall_score", quality_assessment)
        self.assertIn("quality_level", quality_assessment)
        self.assertIn("assessment", quality_assessment)
    
    def test_field_validation(self):
        """测试字段验证"""
        # 测试有效数据
        valid_data = {
            "title": "有效标题",
            "author": "有效作者",
            "date": "2024-01-01"
        }
        
        result = self.document_filler._validate_fill_data(
            valid_data, self.test_analysis_result
        )
        self.assertTrue(result["valid"])
        
        # 测试无效数据
        invalid_data = {
            "title": "",  # 空必填字段
            "date": "invalid-date"  # 无效日期格式
        }
        
        result = self.document_filler._validate_fill_data(
            invalid_data, self.test_analysis_result
        )
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)
    
    def test_export_options(self):
        """测试导出选项"""
        final_document = {
            "content": self.test_document,
            "metadata": {
                "title": "测试文档",
                "author": "测试作者",
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        # 测试自定义导出选项
        export_options = {
            "include_metadata": False,
            "include_watermark": True,
            "font_size": 14,
            "line_spacing": 2.0
        }
        
        result = self.document_filler.export_document(
            final_document=final_document,
            export_format="html",
            export_options=export_options
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["export_format"], "html")
    
    def tearDown(self):
        """清理测试文件"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2) 