"""
综合文风处理器测试用例
测试文风特征提取、融合、对齐等功能
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.tools.comprehensive_style_processor import ComprehensiveStyleProcessor
from core.tools.enhanced_style_extractor import QuantitativeFeatureExtractor
from core.tools.feature_fusion_processor import FeatureFusionProcessor
from core.tools.style_alignment_engine import StyleSimilarityCalculator


class TestQuantitativeFeatureExtractor(unittest.TestCase):
    """测试量化特征提取器"""
    
    def setUp(self):
        self.extractor = QuantitativeFeatureExtractor()
        self.sample_text = """
        这是一个测试文档。文档包含多个句子，用于测试文风分析功能。
        我们希望通过这个测试来验证系统的准确性和可靠性。
        测试文本应该包含不同的句式结构，以及各种标点符号的使用。
        """
    
    def test_extract_lexical_features(self):
        """测试词汇特征提取"""
        try:
            features = self.extractor.extract_lexical_features(self.sample_text)
            
            # 检查基本结构
            self.assertIsInstance(features, dict)
            
            # 如果依赖可用，检查具体特征
            if not features.get("error"):
                self.assertIn("total_chars", features)
                self.assertIn("total_words", features)
                self.assertIn("ttr", features)
                self.assertGreater(features["total_chars"], 0)
                self.assertGreater(features["total_words"], 0)
                self.assertGreaterEqual(features["ttr"], 0)
                self.assertLessEqual(features["ttr"], 1)
            
        except Exception as e:
            self.skipTest(f"依赖不可用或其他错误: {str(e)}")
    
    def test_extract_syntactic_features(self):
        """测试句法特征提取"""
        features = self.extractor.extract_syntactic_features(self.sample_text)
        
        self.assertIsInstance(features, dict)
        if not features.get("error"):
            self.assertIn("total_sentences", features)
            self.assertIn("avg_sentence_length", features)
            self.assertGreater(features["total_sentences"], 0)
            self.assertGreater(features["avg_sentence_length"], 0)
    
    def test_extract_punctuation_features(self):
        """测试标点符号特征提取"""
        features = self.extractor.extract_punctuation_features(self.sample_text)
        
        self.assertIsInstance(features, dict)
        if not features.get("error"):
            self.assertIn("total_punctuation", features)
            self.assertIn("punctuation_density", features)
            self.assertGreaterEqual(features["total_punctuation"], 0)
            self.assertGreaterEqual(features["punctuation_density"], 0)
    
    def test_empty_text_handling(self):
        """测试空文本处理"""
        features = self.extractor.extract_all_quantitative_features("")
        
        self.assertIsInstance(features, dict)
        self.assertEqual(features["text_length"], 0)


class TestFeatureFusionProcessor(unittest.TestCase):
    """测试特征融合处理器"""
    
    def setUp(self):
        self.processor = FeatureFusionProcessor()
        
        # 模拟量化特征
        self.mock_quantitative_features = {
            "lexical_features": {
                "ttr": 0.75,
                "avg_word_length": 2.5,
                "formal_word_density": 10.5,
                "informal_word_density": 2.3,
                "function_word_density": 45.2
            },
            "syntactic_features": {
                "avg_sentence_length": 15.2,
                "sentence_length_std": 5.8,
                "short_sentence_ratio": 0.3,
                "long_sentence_ratio": 0.2,
                "compound_sentence_ratio": 0.4
            },
            "punctuation_features": {
                "punctuation_density": 8.5,
                "question_mark_count": 2,
                "exclamation_mark_count": 1
            }
        }
        
        # 模拟LLM特征
        self.mock_llm_features = {
            "evaluations": {
                "词汇风格": {"score": 4.0, "reason": "词汇丰富"},
                "句子结构风格": {"score": 3.5, "reason": "结构适中"},
                "语气情感风格": {"score": 3.0, "reason": "较为客观"}
            },
            "overall_style_profile": {
                "average_score": 3.5,
                "score_std": 0.5
            }
        }
    
    def test_fuse_features_weighted_concat(self):
        """测试加权拼接融合"""
        result = self.processor.fuse_features(
            self.mock_quantitative_features,
            self.mock_llm_features,
            fusion_method="weighted_concat"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("fused_vector", result)
        self.assertIn("feature_names", result)
        self.assertIn("fusion_weights", result)
        
        if result.get("success"):
            self.assertGreater(len(result["fused_vector"]), 0)
            self.assertEqual(len(result["fused_vector"]), len(result["feature_names"]))
    
    def test_fuse_features_hierarchical(self):
        """测试分层融合"""
        result = self.processor.fuse_features(
            self.mock_quantitative_features,
            self.mock_llm_features,
            fusion_method="hierarchical"
        )
        
        self.assertIsInstance(result, dict)
        if result.get("success"):
            self.assertIn("fused_vector", result)
            self.assertGreater(len(result["fused_vector"]), 0)
    
    def test_invalid_fusion_method(self):
        """测试无效融合方法"""
        result = self.processor.fuse_features(
            self.mock_quantitative_features,
            self.mock_llm_features,
            fusion_method="invalid_method"
        )
        
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)


class TestStyleSimilarityCalculator(unittest.TestCase):
    """测试文风相似度计算器"""
    
    def setUp(self):
        self.calculator = StyleSimilarityCalculator()
        self.features1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.features2 = [1.1, 2.1, 2.9, 4.1, 4.9]
        self.features3 = [5.0, 4.0, 3.0, 2.0, 1.0]
    
    def test_cosine_similarity(self):
        """测试余弦相似度计算"""
        result = self.calculator.calculate_similarity(
            self.features1, self.features2, method="cosine"
        )
        
        self.assertTrue(result.get("success"))
        self.assertIn("similarity_score", result)
        self.assertGreaterEqual(result["similarity_score"], 0)
        self.assertLessEqual(result["similarity_score"], 1)
        
        # 相似向量应该有高相似度
        self.assertGreater(result["similarity_score"], 0.9)
    
    def test_euclidean_similarity(self):
        """测试欧氏距离相似度计算"""
        result = self.calculator.calculate_similarity(
            self.features1, self.features2, method="euclidean"
        )
        
        self.assertTrue(result.get("success"))
        self.assertIn("similarity_score", result)
        self.assertIn("distance", result)
        self.assertGreaterEqual(result["similarity_score"], 0)
        self.assertGreaterEqual(result["distance"], 0)
    
    def test_different_vectors(self):
        """测试不同向量的相似度"""
        result = self.calculator.calculate_similarity(
            self.features1, self.features3, method="cosine"
        )
        
        self.assertTrue(result.get("success"))
        # 相反的向量应该有较低的相似度
        self.assertLess(result["similarity_score"], 0.5)
    
    def test_empty_vectors(self):
        """测试空向量处理"""
        result = self.calculator.calculate_similarity([], [], method="cosine")
        
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)
    
    def test_different_length_vectors(self):
        """测试不同长度向量处理"""
        result = self.calculator.calculate_similarity(
            [1, 2, 3], [1, 2], method="cosine"
        )
        
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)


class TestComprehensiveStyleProcessor(unittest.TestCase):
    """测试综合文风处理器"""
    
    def setUp(self):
        # 创建模拟的LLM客户端
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate.return_value = """
        ## 1. 词汇风格分析
        评分：4
        特征描述：词汇使用较为丰富，包含一定的专业术语
        典型词汇：测试、验证、系统、功能、准确性
        
        ## 6. 整体风格判断
        主要风格类型：商务专业
        风格强度：4
        风格一致性：4
        """
        
        self.processor = ComprehensiveStyleProcessor(
            llm_client=self.mock_llm_client,
            storage_path="test_storage"
        )
        
        self.sample_text = """
        本报告旨在分析公司第三季度的业务表现。通过详细的数据分析和市场调研，
        我们发现销售额较上季度增长了15%，客户满意度也有显著提升。
        建议在下一季度继续加强市场推广力度，优化产品结构，提高服务质量。
        """
        
        self.formal_text = """
        根据相关法律法规和公司章程的规定，现将本次董事会会议的决议事项公告如下：
        经董事会审议通过，同意公司投资建设新的生产基地项目。
        特此公告，请各相关部门按照决议要求认真执行。
        """
    
    def test_extract_comprehensive_style_features(self):
        """测试综合文风特征提取"""
        result = self.processor.extract_comprehensive_style_features(
            self.sample_text, "测试文档"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("processing_id", result)
        self.assertIn("document_name", result)
        self.assertIn("basic_features", result)
        self.assertIn("processing_summary", result)
        
        # 检查文档名称
        self.assertEqual(result["document_name"], "测试文档")
        
        # 检查文本长度
        self.assertEqual(result["text_length"], len(self.sample_text))
    
    def test_compare_document_styles(self):
        """测试文档风格比较"""
        result = self.processor.compare_document_styles(
            self.sample_text, self.formal_text, "商务文档", "正式公告"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("comparison_id", result)
        self.assertIn("document1_name", result)
        self.assertIn("document2_name", result)
        self.assertIn("document1_features", result)
        self.assertIn("document2_features", result)
        self.assertIn("comparison_summary", result)
        
        # 检查文档名称
        self.assertEqual(result["document1_name"], "商务文档")
        self.assertEqual(result["document2_name"], "正式公告")
    
    def test_align_text_style(self):
        """测试文风对齐"""
        content_to_align = "我们需要提高产品质量，增加客户满意度。"
        
        result = self.processor.align_text_style(
            self.sample_text, self.formal_text, content_to_align,
            "源文档", "目标文档"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("alignment_id", result)
        self.assertIn("original_content", result)
        self.assertIn("source_features", result)
        self.assertIn("target_features", result)
        
        # 检查原始内容
        self.assertEqual(result["original_content"], content_to_align)
    
    def test_batch_process_documents(self):
        """测试批量处理文档"""
        documents = [
            {"text": self.sample_text, "name": "文档1"},
            {"text": self.formal_text, "name": "文档2"},
            {"text": "这是第三个测试文档。", "name": "文档3"}
        ]
        
        result = self.processor.batch_process_documents(documents, "extract")
        
        self.assertIsInstance(result, dict)
        self.assertIn("batch_id", result)
        self.assertIn("total_documents", result)
        self.assertIn("processing_results", result)
        self.assertIn("batch_summary", result)
        
        # 检查文档数量
        self.assertEqual(result["total_documents"], 3)
        self.assertEqual(len(result["processing_results"]), 3)
    
    def test_processing_history(self):
        """测试处理历史记录"""
        # 执行一次处理
        self.processor.extract_comprehensive_style_features(self.sample_text, "历史测试")
        
        # 获取历史记录
        history = self.processor.get_processing_history()
        
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        
        # 检查历史记录结构
        last_entry = history[-1]
        self.assertIn("processing_id", last_entry)
        self.assertIn("document_name", last_entry)
        self.assertIn("processing_time", last_entry)
        self.assertEqual(last_entry["document_name"], "历史测试")
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试空文本
        result = self.processor.extract_comprehensive_style_features("", "空文档")
        self.assertIsInstance(result, dict)
        
        # 测试无效输入
        result = self.processor.compare_document_styles("", "", "空文档1", "空文档2")
        self.assertIsInstance(result, dict)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate.return_value = "评分：3\n理由：测试响应"
        
        self.processor = ComprehensiveStyleProcessor(
            llm_client=self.mock_llm_client,
            storage_path="integration_test_storage"
        )
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流程"""
        # 1. 特征提取
        text1 = "这是一个正式的商务文档，用于测试系统功能。"
        text2 = "这个文档比较随意，就是想试试看效果怎么样。"
        
        features1 = self.processor.extract_comprehensive_style_features(text1, "正式文档")
        features2 = self.processor.extract_comprehensive_style_features(text2, "随意文档")
        
        self.assertIsInstance(features1, dict)
        self.assertIsInstance(features2, dict)
        
        # 2. 风格比较
        comparison = self.processor.compare_document_styles(text1, text2, "正式文档", "随意文档")
        self.assertIsInstance(comparison, dict)
        
        # 3. 风格对齐
        content_to_align = "我们要做好这个项目。"
        alignment = self.processor.align_text_style(text2, text1, content_to_align, "随意", "正式")
        self.assertIsInstance(alignment, dict)
        
        # 4. 检查处理历史
        history = self.processor.get_processing_history()
        self.assertGreaterEqual(len(history), 2)  # 至少有两次特征提取记录


if __name__ == '__main__':
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestQuantitativeFeatureExtractor))
    test_suite.addTest(unittest.makeSuite(TestFeatureFusionProcessor))
    test_suite.addTest(unittest.makeSuite(TestStyleSimilarityCalculator))
    test_suite.addTest(unittest.makeSuite(TestComprehensiveStyleProcessor))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果摘要
    print(f"\n{'='*50}")
    print(f"测试摘要:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"{'='*50}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
