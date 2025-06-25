#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文风对齐功能测试模块
测试文风分析、风格识别、提示词生成、风格应用验证等核心功能
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

from src.core.tools.writing_style_analyzer import WritingStyleAnalyzer


class TestWritingStyle(unittest.TestCase):
    """文风对齐功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = WritingStyleAnalyzer(storage_path=self.temp_dir)
        
        # 测试文档样本
        self.sample_documents = {
            "business_professional": """
根据公司发展战略，我们制定了详细的实施方案。该方案包含三个核心模块：技术升级、人员培训和流程优化。
通过系统性的改进措施，预计可以提升整体运营效率25%，降低运营成本15%。
我们将建立完善的监控体系，确保各项指标达到预期目标。
            """.strip(),
            
            "academic_research": """
本研究采用定量分析方法，通过对1000个样本的数据分析，探讨了影响用户行为的关键因素。
研究结果表明，用户满意度与服务质量之间存在显著的正相关关系（r=0.78, p<0.01）。
进一步的回归分析显示，服务响应时间、服务态度和问题解决能力是影响用户满意度的三个主要因素。
这一发现为改进服务质量提供了重要的理论依据和实践指导。
            """.strip(),
            
            "government_official": """
根据上级部门的统一部署，结合我市实际情况，现就进一步加强城市管理工作提出如下要求：
一是要提高思想认识，充分认识城市管理工作的重要性和紧迫性。
二是要强化责任落实，各相关部门要按照职责分工，认真履行监管职责。
三是要完善工作机制，建立健全长效管理制度，确保各项工作落到实处。
            """.strip(),
            
            "narrative_descriptive": """
春天的阳光温暖而明媚，轻柔地洒在大地上。微风徐徐吹过，带来了花香的气息。
孩子们在公园里快乐地奔跑着，他们的笑声如银铃般清脆动听。
老人们坐在树荫下悠闲地聊天，脸上洋溢着满足的笑容。
这样美好的时光，让人感到无比的宁静和幸福。
            """.strip(),
            
            "concise_practical": """
操作步骤：
1. 打开应用程序
2. 点击"新建"按钮
3. 输入必要信息
4. 保存文件
注意：请确保网络连接正常。
            """.strip()
        }
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_style_feature_analysis(self):
        """测试文风特征分析"""
        content = self.sample_documents["business_professional"]
        features = self.analyzer._analyze_style_features(content)
        
        # 验证特征结构
        expected_features = [
            "sentence_structure", "vocabulary_choice", "expression_style",
            "text_organization", "language_habits", "emotional_tone",
            "professionalism", "rhetorical_devices"
        ]
        
        for feature in expected_features:
            self.assertIn(feature, features)
        
        # 验证句式结构特征
        sentence_features = features["sentence_structure"]
        self.assertIn("average_length", sentence_features)
        self.assertIn("total_sentences", sentence_features)
        self.assertGreater(sentence_features["average_length"], 0)
        
        # 验证词汇选择特征
        vocab_features = features["vocabulary_choice"]
        self.assertIn("formality_score", vocab_features)
        self.assertIn("action_verb_ratio", vocab_features)
        self.assertGreaterEqual(vocab_features["formality_score"], 0)
    
    def test_sentence_structure_analysis(self):
        """测试句式结构分析"""
        # 测试长句文本
        long_sentence_text = "这是一个非常长的句子，包含了多个从句和复杂的语法结构，用来测试句式分析功能的准确性和可靠性。"
        features = self.analyzer._analyze_sentence_structure(long_sentence_text)
        
        self.assertGreater(features["average_length"], 20)
        self.assertEqual(features["total_sentences"], 1)
        
        # 测试短句文本
        short_sentence_text = "短句。测试。分析。"
        features = self.analyzer._analyze_sentence_structure(short_sentence_text)
        
        self.assertLess(features["average_length"], 10)
        self.assertEqual(features["total_sentences"], 3)
    
    def test_vocabulary_analysis(self):
        """测试词汇分析"""
        formal_text = "根据相关法规，我们将严格执行各项规定，确保工作的规范性和有效性。"
        features = self.analyzer._analyze_vocabulary_choice(formal_text)
        
        # 正式文本应该有较高的正式度分数
        self.assertGreater(features["formality_score"], 5)
        
        # 测试动作动词
        action_text = "我们将实施、推进、完成、达成各项目标。"
        features = self.analyzer._analyze_vocabulary_choice(action_text)
        self.assertGreater(features["action_verb_ratio"], 10)
    
    def test_style_type_identification(self):
        """测试文风类型识别"""
        test_cases = [
            ("business_professional", "business_professional"),
            ("academic_research", "academic_research"),
            ("government_official", "formal_official"),
            ("narrative_descriptive", "narrative_descriptive"),
            ("concise_practical", "concise_practical")
        ]
        
        for doc_key, expected_style in test_cases:
            with self.subTest(doc_key=doc_key):
                content = self.sample_documents[doc_key]
                features = self.analyzer._analyze_style_features(content)
                identified_style, confidence = self.analyzer._identify_style_type(content, features)
                
                # 验证识别结果
                self.assertIsInstance(identified_style, str)
                self.assertGreaterEqual(confidence, 0.0)
                self.assertLessEqual(confidence, 1.0)
                
                # 对于明显的风格特征，置信度应该较高
                if doc_key in ["business_professional", "concise_practical"]:
                    self.assertGreater(confidence, 0.3)
    
    def test_style_prompt_generation(self):
        """测试文风提示词生成"""
        content = self.sample_documents["business_professional"]
        features = self.analyzer._analyze_style_features(content)
        style_type = "business_professional"
        
        prompt = self.analyzer._generate_style_prompt(features, style_type)
        
        # 验证提示词结构
        self.assertIn("【文风特征】", prompt)
        self.assertIn("【句式要求】", prompt)
        self.assertIn("【词汇要求】", prompt)
        self.assertIn("【表达方式】", prompt)
        self.assertIn("【组织结构】", prompt)
        self.assertIn("【避免事项】", prompt)
        
        # 验证内容不为空
        self.assertGreater(len(prompt), 100)
    
    def test_emotional_tone_analysis(self):
        """测试情感色彩分析"""
        positive_text = "这个项目非常成功，取得了优秀的成果，大家都很满意。"
        features = self.analyzer._analyze_emotional_tone(positive_text)
        
        self.assertGreater(features["positive_ratio"], 0.5)
        self.assertLess(features["negative_ratio"], 0.3)
        
        negative_text = "项目遇到了严重问题，存在很多困难和挑战。"
        features = self.analyzer._analyze_emotional_tone(negative_text)
        
        self.assertGreater(features["negative_ratio"], 0.5)
    
    def test_professionalism_analysis(self):
        """测试专业性分析"""
        professional_text = "根据权威研究数据显示，该技术方案的成功率达到95.6%。"
        features = self.analyzer._analyze_professionalism(professional_text)
        
        self.assertGreater(features["authority_indicators"], 0)
        self.assertGreater(features["precision_level"], 0)
    
    def test_style_template_operations(self):
        """测试文风模板操作"""
        # 分析文风
        analysis_result = self.analyzer.analyze_writing_style(
            self.sample_documents["business_professional"],
            "商务报告样本"
        )
        
        # 验证分析结果
        self.assertNotIn("error", analysis_result)
        self.assertIn("template_id", analysis_result)
        self.assertIn("style_type", analysis_result)
        self.assertIn("style_prompt", analysis_result)
        
        # 保存模板
        save_result = self.analyzer.save_style_template(analysis_result)
        self.assertIn("success", save_result)
        self.assertTrue(save_result["success"])
        
        # 加载模板
        template_id = analysis_result["template_id"]
        loaded_template = self.analyzer.load_style_template(template_id)
        self.assertNotIn("error", loaded_template)
        self.assertEqual(loaded_template["template_id"], template_id)
        
        # 列出模板
        templates = self.analyzer.list_style_templates()
        self.assertIsInstance(templates, list)
    
    def test_style_validation(self):
        """测试风格应用验证"""
        original_content = self.sample_documents["business_professional"]
        generated_content = """
我们已经制定了完整的实施计划。这个计划涵盖了技术改进、团队培训和流程优化三个方面。
通过这些措施，我们预期能够提高效率20%，减少成本10%。
我们会建立监控机制，确保目标实现。
        """.strip()
        
        # 分析原始内容特征
        original_features = self.analyzer._analyze_style_features(original_content)
        
        # 验证风格应用
        validation_result = self.analyzer.validate_style_application(
            original_content, generated_content, "business_professional", original_features
        )
        
        # 验证验证结果
        self.assertIn("success", validation_result)
        self.assertTrue(validation_result["success"])
        self.assertIn("consistency_score", validation_result)
        self.assertIn("quality_metrics", validation_result)
        self.assertIn("improvement_suggestions", validation_result)
        
        # 验证分数范围
        consistency_score = validation_result["consistency_score"]
        self.assertGreaterEqual(consistency_score, 0.0)
        self.assertLessEqual(consistency_score, 1.0)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试空内容分析
        result = self.analyzer.analyze_writing_style("", "空文档")
        self.assertNotIn("error", result)  # 应该能处理空内容
        
        # 测试加载不存在的模板
        load_result = self.analyzer.load_style_template("不存在的ID")
        self.assertIn("error", load_result)
        
        # 测试无效的验证参数
        validation_result = self.analyzer.validate_style_application(
            "", "", "invalid_style", {}
        )
        # 应该能处理无效输入而不崩溃
        self.assertIsInstance(validation_result, dict)
    
    def test_feature_comparison(self):
        """测试特征比较功能"""
        target_features = {"average_length": 20, "complex_ratio": 0.6}
        generated_features = {"average_length": 22, "complex_ratio": 0.5}
        
        score = self.analyzer._compare_sentence_features(target_features, generated_features)
        
        # 验证比较分数
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # 相同特征应该得到高分
        identical_score = self.analyzer._compare_sentence_features(
            target_features, target_features
        )
        self.assertGreater(identical_score, 0.8)


if __name__ == '__main__':
    unittest.main()
