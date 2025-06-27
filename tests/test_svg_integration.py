#!/usr/bin/env python3
"""
SVG集成功能测试脚本
测试SVG生成、插入和文档处理功能
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.tools.intelligent_image_processor import IntelligentImageProcessor

class TestSVGIntegration(unittest.TestCase):
    """SVG集成功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.image_processor = IntelligentImageProcessor()
        self.temp_dir = tempfile.mkdtemp()
        
        # 测试文档内容
        self.test_document = """
        <html>
        <head><title>测试文档</title></head>
        <body>
            <h1>测试文档标题</h1>
            <p>这是一个测试文档的内容。</p>
            <p>这里应该插入SVG图像。</p>
        </body>
        </html>
        """
    
    def test_generate_svg_image(self):
        """测试SVG图像生成"""
        print("测试SVG图像生成...")
        
        # 测试生成通用SVG
        result = self.image_processor.generate_svg_image(
            elements=[
                {
                    "type": "rect",
                    "args": {
                        "insert": (10, 10),
                        "size": (100, 50),
                        "fill": "#3498db",
                        "stroke": "#2980b9",
                        "stroke_width": 2
                    }
                },
                {
                    "type": "text",
                    "text": "测试SVG",
                    "args": {
                        "insert": (60, 35),
                        "text_anchor": "middle",
                        "font_size": 14,
                        "fill": "white"
                    }
                }
            ],
            size=(200, 100),
            filename="test_svg.svg"
        )
        
        self.assertTrue(result["success"])
        self.assertIn("svg_path", result)
        self.assertTrue(os.path.exists(result["svg_path"]))
        
        print(f"✓ SVG生成成功: {result['svg_path']}")
    
    def test_generate_ai_svg_for_document(self):
        """测试AI SVG生成"""
        print("测试AI SVG生成...")
        
        # 测试专利文档SVG
        result = self.image_processor.generate_ai_svg_for_document(
            document_type="patent",
            content_description="技术方案流程图",
            svg_size=(400, 300)
        )
        
        self.assertTrue(result["success"])
        self.assertIn("svg_path", result)
        self.assertIn("svg_content", result)
        self.assertEqual(result["document_type"], "patent")
        
        print(f"✓ 专利文档SVG生成成功: {result['svg_path']}")
        
        # 测试项目文档SVG
        result = self.image_processor.generate_ai_svg_for_document(
            document_type="project",
            content_description="项目进度图",
            svg_size=(500, 200)
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["document_type"], "project")
        
        print(f"✓ 项目文档SVG生成成功: {result['svg_path']}")
    
    def test_insert_svg_to_document_preview_mode(self):
        """测试预览模式SVG插入"""
        print("测试预览模式SVG插入...")
        
        # 生成测试SVG
        svg_result = self.image_processor.generate_ai_svg_for_document(
            document_type="general",
            content_description="测试示意图",
            svg_size=(300, 200)
        )
        
        self.assertTrue(svg_result["success"])
        
        # 测试预览模式插入
        target_position = {
            "line_number": 3,
            "document_type": "general",
            "suggested_size": (300, 200)
        }
        
        updated_content = self.image_processor.insert_svg_to_document(
            self.test_document,
            svg_result,
            target_position,
            mode="preview"
        )
        
        # 检查是否包含SVG内容
        self.assertIn("<svg", updated_content)
        self.assertIn("svg-container", updated_content)
        
        print("✓ 预览模式SVG插入成功")
    
    def test_insert_svg_to_document_download_mode(self):
        """测试下载模式SVG插入"""
        print("测试下载模式SVG插入...")
        
        # 生成测试SVG
        svg_result = self.image_processor.generate_ai_svg_for_document(
            document_type="patent",
            content_description="技术方案图",
            svg_size=(400, 300)
        )
        
        self.assertTrue(svg_result["success"])
        
        # 测试下载模式插入
        target_position = {
            "line_number": 1,
            "document_type": "patent",
            "suggested_size": (400, 300)
        }
        
        updated_content = self.image_processor.insert_svg_to_document(
            self.test_document,
            svg_result,
            target_position,
            mode="download"
        )
        
        # 检查是否包含文件引用
        self.assertIn("file://", updated_content)
        self.assertIn(".svg", updated_content)
        self.assertIn("img src", updated_content)
        
        print("✓ 下载模式SVG插入成功")
    
    def test_patent_svg_elements(self):
        """测试专利文档SVG元素生成"""
        print("测试专利文档SVG元素生成...")
        
        elements = self.image_processor._generate_patent_svg_elements(
            "技术方案描述",
            (400, 300)
        )
        
        self.assertIsInstance(elements, list)
        self.assertGreater(len(elements), 0)
        
        # 检查是否包含必要的元素类型
        element_types = [elem["type"] for elem in elements]
        self.assertIn("rect", element_types)
        self.assertIn("text", element_types)
        
        print("✓ 专利文档SVG元素生成成功")
    
    def test_project_svg_elements(self):
        """测试项目文档SVG元素生成"""
        print("测试项目文档SVG元素生成...")
        
        elements = self.image_processor._generate_project_svg_elements(
            "项目流程描述",
            (500, 200)
        )
        
        self.assertIsInstance(elements, list)
        self.assertGreater(len(elements), 0)
        
        # 检查是否包含项目阶段
        element_types = [elem["type"] for elem in elements]
        self.assertIn("rect", element_types)
        self.assertIn("text", element_types)
        
        print("✓ 项目文档SVG元素生成成功")
    
    def test_general_svg_elements(self):
        """测试通用文档SVG元素生成"""
        print("测试通用文档SVG元素生成...")
        
        elements = self.image_processor._generate_general_svg_elements(
            "通用文档描述",
            (350, 250)
        )
        
        self.assertIsInstance(elements, list)
        self.assertGreater(len(elements), 0)
        
        # 检查是否包含基本图形元素
        element_types = [elem["type"] for elem in elements]
        self.assertIn("rect", element_types)
        self.assertIn("circle", element_types)
        self.assertIn("text", element_types)
        
        print("✓ 通用文档SVG元素生成成功")
    
    def test_svg_markup_generation(self):
        """测试SVG标记生成"""
        print("测试SVG标记生成...")
        
        svg_info = {
            "svg_content": "<svg>测试SVG内容</svg>",
            "svg_path": "/path/to/test.svg",
            "svg_id": "test_svg"
        }
        
        target_position = {
            "line_number": 1,
            "document_type": "patent",
            "suggested_size": (400, 300)
        }
        
        # 测试预览模式标记
        preview_markup = self.image_processor._generate_svg_content_markup(
            svg_info, target_position
        )
        
        self.assertIn("svg-container", preview_markup)
        self.assertIn("附图说明", preview_markup)
        self.assertIn("测试SVG内容", preview_markup)
        
        # 测试下载模式标记
        download_markup = self.image_processor._generate_svg_file_markup(
            svg_info, target_position
        )
        
        self.assertIn("file://", download_markup)
        self.assertIn("img src", download_markup)
        self.assertIn("附图说明", download_markup)
        
        print("✓ SVG标记生成成功")
    
    def test_document_type_detection(self):
        """测试文档类型检测"""
        print("测试文档类型检测...")
        
        # 测试专利文档
        patent_doc = "发明专利申请书\n技术方案..."
        result = self.image_processor.generate_ai_svg_for_document(
            "patent", "技术方案", (400, 300)
        )
        self.assertEqual(result["document_type"], "patent")
        
        # 测试项目文档
        project_doc = "项目申请报告\n项目进度..."
        result = self.image_processor.generate_ai_svg_for_document(
            "project", "项目流程", (400, 300)
        )
        self.assertEqual(result["document_type"], "project")
        
        print("✓ 文档类型检测成功")
    
    def test_error_handling(self):
        """测试错误处理"""
        print("测试错误处理...")
        
        # 测试无效的SVG元素
        result = self.image_processor.generate_svg_image(
            elements=[{"type": "invalid", "args": {}}],
            size=(100, 100),
            filename="error_test.svg"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        
        # 测试无效的文档类型
        result = self.image_processor.generate_ai_svg_for_document(
            "invalid_type", "描述", (100, 100)
        )
        
        # 应该回退到通用类型
        self.assertTrue(result["success"])
        
        print("✓ 错误处理测试成功")
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

def run_svg_integration_tests():
    """运行SVG集成测试"""
    print("=" * 60)
    print("🚀 开始SVG集成功能测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSVGIntegration)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 SVG集成测试结果")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ 所有SVG集成测试通过！")
    else:
        print("\n❌ 部分SVG集成测试失败")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_svg_integration_tests()
    sys.exit(0 if success else 1) 