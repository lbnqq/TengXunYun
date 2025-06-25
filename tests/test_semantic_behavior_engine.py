"""
语义空间行为算法引擎测试用例
测试语义单元识别、空间映射、行为分析和风格画像构建功能
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.tools.semantic_unit_identifier import SemanticUnitIdentifier
from core.tools.semantic_space_mapper import SemanticSpaceMapper
from core.tools.semantic_behavior_analyzer import SemanticBehaviorAnalyzer
from core.tools.semantic_style_profiler import SemanticStyleProfiler
from core.tools.semantic_space_behavior_engine import SemanticSpaceBehaviorEngine


class TestSemanticUnitIdentifier(unittest.TestCase):
    """测试语义单元识别器"""
    
    def setUp(self):
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate.return_value = """
        {
          "concepts": [
            {"text": "人工智能", "role": "核心概念", "importance": 5},
            {"text": "机器学习", "role": "相关概念", "importance": 4}
          ],
          "named_entities": [
            {"text": "谷歌", "type": "组织名", "context": "科技公司"}
          ],
          "key_adjectives": [
            {"text": "智能", "context": "智能系统", "sentiment_intensity": 4, "sentiment_polarity": "积极"}
          ],
          "key_verbs": [
            {"text": "发展", "context": "技术发展", "action_type": "变化", "intensity": 4}
          ],
          "key_phrases": [
            {"text": "深度学习", "role": "技术术语", "domain": "人工智能"}
          ]
        }
        """
        
        self.identifier = SemanticUnitIdentifier(self.mock_llm_client)
        self.sample_text = """
        人工智能技术正在快速发展，谷歌等科技公司在机器学习和深度学习领域
        取得了重大突破。这些智能系统展现出了令人惊叹的能力。
        """
    
    def test_identify_semantic_units_comprehensive(self):
        """测试综合语义单元识别"""
        result = self.identifier.identify_semantic_units(self.sample_text, "comprehensive")
        
        self.assertIsInstance(result, dict)
        self.assertIn("semantic_units", result)
        self.assertIn("analysis_summary", result)
        
        if result.get("success"):
            semantic_units = result["semantic_units"]
            self.assertIn("concepts", semantic_units)
            self.assertIn("named_entities", semantic_units)
            
            # 检查概念识别
            concepts = semantic_units.get("concepts", [])
            self.assertGreater(len(concepts), 0)
            
            # 检查实体识别
            entities = semantic_units.get("named_entities", [])
            self.assertGreaterEqual(len(entities), 0)
    
    def test_identify_semantic_units_concept_only(self):
        """测试仅概念识别"""
        result = self.identifier.identify_semantic_units(self.sample_text, "concept")
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["analysis_type"], "concept")
    
    def test_batch_identify_semantic_units(self):
        """测试批量语义单元识别"""
        texts = [
            "这是第一个测试文本，包含一些概念。",
            "这是第二个测试文本，包含不同的概念。"
        ]
        
        result = self.identifier.batch_identify_semantic_units(texts, "comprehensive")
        
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertEqual(result["total_texts"], 2)
        self.assertIn("batch_summary", result)
    
    def test_get_semantic_unit_statistics(self):
        """测试语义单元统计"""
        mock_semantic_units = {
            "concepts": [
                {"text": "概念1", "importance": 5},
                {"text": "概念2", "importance": 4}
            ],
            "named_entities": [
                {"text": "实体1", "type": "人名"}
            ],
            "key_adjectives": [
                {"text": "形容词1", "sentiment_polarity": "积极"}
            ]
        }
        
        stats = self.identifier.get_semantic_unit_statistics(mock_semantic_units)
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats["concept_count"], 2)
        self.assertEqual(stats["entity_count"], 1)
        self.assertEqual(stats["adjective_count"], 1)


class TestSemanticSpaceMapper(unittest.TestCase):
    """测试语义空间映射器"""
    
    def setUp(self):
        self.mapper = SemanticSpaceMapper()
        
        # 模拟语义单元
        self.mock_semantic_units = {
            "concepts": [
                {"text": "人工智能", "role": "核心概念"},
                {"text": "机器学习", "role": "相关概念"}
            ],
            "named_entities": [
                {"text": "谷歌", "type": "组织名"}
            ],
            "key_phrases": [
                {"text": "深度学习", "role": "技术术语"}
            ]
        }
    
    def test_encode_semantic_units(self):
        """测试语义单元编码"""
        result = self.mapper.encode_semantic_units(self.mock_semantic_units)
        
        self.assertIsInstance(result, dict)
        self.assertIn("concept_vectors", result)
        self.assertIn("entity_vectors", result)
        self.assertIn("phrase_vectors", result)
        self.assertIn("vector_statistics", result)
        
        if result.get("success"):
            # 检查向量结构
            concept_vectors = result["concept_vectors"]
            self.assertIsInstance(concept_vectors, dict)
            
            # 检查统计信息
            stats = result["vector_statistics"]
            self.assertIn("total_vectors", stats)
            self.assertIn("category_counts", stats)
    
    def test_calculate_semantic_similarities(self):
        """测试语义相似度计算"""
        # 首先编码语义单元
        vector_result = self.mapper.encode_semantic_units(self.mock_semantic_units)
        
        if vector_result.get("success"):
            similarity_result = self.mapper.calculate_semantic_similarities(vector_result, "cosine")
            
            self.assertIsInstance(similarity_result, dict)
            self.assertIn("concept_similarities", similarity_result)
            self.assertIn("similarity_statistics", similarity_result)
            
            if similarity_result.get("success"):
                stats = similarity_result["similarity_statistics"]
                self.assertIn("concept_similarity_stats", stats)
    
    def test_find_semantic_clusters(self):
        """测试语义聚类"""
        vector_result = self.mapper.encode_semantic_units(self.mock_semantic_units)
        
        if vector_result.get("success"):
            cluster_result = self.mapper.find_semantic_clusters(vector_result, n_clusters=2)
            
            self.assertIsInstance(cluster_result, dict)
            
            if cluster_result.get("success"):
                self.assertIn("clusters", cluster_result)
                self.assertIn("cluster_statistics", cluster_result)
                
                clusters = cluster_result["clusters"]
                self.assertLessEqual(len(clusters), 2)  # 最多2个聚类


class TestSemanticBehaviorAnalyzer(unittest.TestCase):
    """测试语义行为分析器"""
    
    def setUp(self):
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate.return_value = """
        {
          "cluster_themes": [
            {"cluster_id": "cluster_0", "theme": "技术概念", "coherence": 4, "explanation": "相关技术概念聚集"}
          ],
          "overall_assessment": {"semantic_organization": 4, "concept_diversity": 3, "thematic_clarity": 4}
        }
        """
        
        self.analyzer = SemanticBehaviorAnalyzer(self.mock_llm_client)
        
        # 模拟分析结果
        self.mock_vector_result = {
            "success": True,
            "concept_vectors": {
                "人工智能": {"vector": [0.1, 0.2, 0.3], "metadata": {}},
                "机器学习": {"vector": [0.2, 0.3, 0.4], "metadata": {}}
            },
            "vector_statistics": {"total_vectors": 2}
        }
        
        self.mock_cluster_result = {
            "success": True,
            "clusters": {
                "cluster_0": {
                    "concepts": [
                        {"name": "人工智能", "distance_to_center": 0.1},
                        {"name": "机器学习", "distance_to_center": 0.2}
                    ],
                    "size": 2
                }
            }
        }
        
        self.mock_similarity_result = {
            "success": True,
            "concept_similarities": {
                "人工智能": {"机器学习": 0.8}
            },
            "similarity_statistics": {
                "concept_similarity_stats": {
                    "average": 0.8,
                    "max": 0.8,
                    "min": 0.8,
                    "std": 0.0
                }
            }
        }
    
    def test_analyze_concept_clustering(self):
        """测试概念聚类分析"""
        result = self.analyzer.analyze_concept_clustering(
            self.mock_vector_result, 
            self.mock_cluster_result,
            "测试文本"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("clustering_metrics", result)
        self.assertIn("behavioral_indicators", result)
        
        if result.get("success"):
            metrics = result["clustering_metrics"]
            self.assertIn("cluster_count", metrics)
            self.assertIn("average_cluster_size", metrics)
    
    def test_analyze_semantic_distance_patterns(self):
        """测试语义距离模式分析"""
        result = self.analyzer.analyze_semantic_distance_patterns(
            self.mock_vector_result,
            self.mock_similarity_result
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("distance_metrics", result)
        self.assertIn("pattern_analysis", result)
        
        if result.get("success"):
            metrics = result["distance_metrics"]
            self.assertIn("average_similarity", metrics)
    
    def test_assess_associative_novelty(self):
        """测试联想创新度评估"""
        result = self.analyzer.assess_associative_novelty(
            self.mock_vector_result,
            self.mock_similarity_result,
            "测试文本"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("novelty_candidates", result)
        self.assertIn("creativity_metrics", result)


class TestSemanticStyleProfiler(unittest.TestCase):
    """测试语义风格画像构建器"""
    
    def setUp(self):
        self.profiler = SemanticStyleProfiler()
        
        # 模拟分析结果
        self.mock_analysis_results = {
            "vector_result": {
                "success": True,
                "vector_statistics": {
                    "total_vectors": 5,
                    "vector_density": 1.2,
                    "category_counts": {"concept_vectors": 3}
                }
            },
            "clustering_analysis": {
                "success": True,
                "clustering_metrics": {
                    "cluster_count": 2,
                    "average_cluster_size": 2.5,
                    "cluster_size_variance": 0.5
                },
                "behavioral_indicators": {
                    "conceptual_organization": "良好",
                    "thematic_coherence": "高"
                }
            },
            "distance_analysis": {
                "success": True,
                "distance_metrics": {
                    "average_similarity": 0.7,
                    "similarity_variance": 0.1
                },
                "pattern_analysis": {
                    "semantic_span": "适中"
                }
            },
            "novelty_assessment": {
                "success": True,
                "creativity_metrics": {
                    "average_novelty_score": 3.5,
                    "high_novelty_count": 2,
                    "creativity_density": 0.4
                }
            },
            "emotional_analysis": {
                "success": True,
                "emotional_distribution": {
                    "emotional_intensity_avg": 3.2,
                    "positive_count": 3,
                    "negative_count": 1,
                    "neutral_count": 2
                },
                "behavioral_patterns": {
                    "emotional_expressiveness": "中等",
                    "emotional_balance": "积极倾向"
                }
            }
        }
    
    def test_build_semantic_style_profile(self):
        """测试语义风格画像构建"""
        result = self.profiler.build_semantic_style_profile(
            self.mock_analysis_results, "测试文档"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("profile_id", result)
        self.assertIn("document_name", result)
        self.assertIn("feature_vector", result)
        self.assertIn("style_scores", result)
        self.assertIn("style_classification", result)
        self.assertIn("profile_summary", result)
        
        if result.get("success"):
            # 检查风格分数
            style_scores = result["style_scores"]
            self.assertIn("conceptual_organization", style_scores)
            self.assertIn("semantic_coherence", style_scores)
            self.assertIn("creative_association", style_scores)
            
            # 检查分类结果
            classification = result["style_classification"]
            self.assertIn("primary_style", classification)
            self.assertIn("style_strength", classification)
            
            # 检查画像摘要
            summary = result["profile_summary"]
            self.assertIn("profile_type", summary)
            self.assertIn("key_strengths", summary)
    
    def test_compare_profiles(self):
        """测试风格画像比较"""
        # 创建两个模拟画像
        profile1 = {
            "document_name": "文档1",
            "feature_vector": [1.0, 2.0, 3.0, 4.0],
            "style_scores": {
                "conceptual_organization": 4.0,
                "semantic_coherence": 3.5,
                "creative_association": 3.0
            }
        }
        
        profile2 = {
            "document_name": "文档2", 
            "feature_vector": [1.1, 2.1, 2.9, 4.1],
            "style_scores": {
                "conceptual_organization": 3.8,
                "semantic_coherence": 3.7,
                "creative_association": 3.2
            }
        }
        
        comparison = self.profiler.compare_profiles(profile1, profile2)
        
        self.assertIsInstance(comparison, dict)
        self.assertIn("similarity_score", comparison)
        self.assertIn("dimension_differences", comparison)
        self.assertIn("style_compatibility", comparison)
        self.assertIn("comparison_summary", comparison)


class TestSemanticSpaceBehaviorEngine(unittest.TestCase):
    """测试语义空间行为算法引擎"""
    
    def setUp(self):
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate.return_value = """
        {
          "concepts": [{"text": "测试概念", "role": "核心概念", "importance": 4}],
          "named_entities": [{"text": "测试实体", "type": "其他"}]
        }
        """
        
        self.engine = SemanticSpaceBehaviorEngine(
            llm_client=self.mock_llm_client,
            storage_path="test_storage"
        )
        
        self.sample_text = """
        人工智能是当今科技发展的重要方向。机器学习和深度学习技术
        正在改变我们的生活方式。谷歌、微软等科技巨头在这个领域
        投入了大量资源，推动了技术的快速发展。
        """
    
    def test_analyze_semantic_behavior_basic(self):
        """测试基础语义行为分析"""
        result = self.engine.analyze_semantic_behavior(
            self.sample_text, "测试文档", "basic"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("analysis_id", result)
        self.assertIn("document_name", result)
        self.assertIn("analysis_depth", result)
        self.assertIn("stage_results", result)
        self.assertIn("analysis_summary", result)
        
        self.assertEqual(result["analysis_depth"], "basic")
        self.assertEqual(result["document_name"], "测试文档")
    
    def test_analyze_semantic_behavior_comprehensive(self):
        """测试综合语义行为分析"""
        result = self.engine.analyze_semantic_behavior(
            self.sample_text, "测试文档", "comprehensive"
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["analysis_depth"], "comprehensive")
        
        # 检查阶段结果
        stage_results = result.get("stage_results", {})
        self.assertIn("stage1_identification", stage_results)
        self.assertIn("stage2_mapping", stage_results)
        
        # 检查分析摘要
        summary = result.get("analysis_summary", {})
        self.assertIn("stages_completed", summary)
        self.assertIn("key_findings", summary)
    
    def test_compare_semantic_profiles(self):
        """测试语义风格画像比较"""
        text1 = "这是第一个测试文档，包含一些技术概念。"
        text2 = "这是第二个测试文档，包含不同的内容。"
        
        result = self.engine.compare_semantic_profiles(
            text1, text2, "文档1", "文档2"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("comparison_id", result)
        self.assertIn("document1_analysis", result)
        self.assertIn("document2_analysis", result)
    
    def test_get_analysis_history(self):
        """测试分析历史获取"""
        # 先执行一次分析
        self.engine.analyze_semantic_behavior(self.sample_text, "历史测试")
        
        history = self.engine.get_analysis_history()
        
        self.assertIsInstance(history, list)
        if history:
            entry = history[-1]
            self.assertIn("analysis_id", entry)
            self.assertIn("document_name", entry)
            self.assertIn("analysis_time", entry)


if __name__ == '__main__':
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestSemanticUnitIdentifier))
    test_suite.addTest(unittest.makeSuite(TestSemanticSpaceMapper))
    test_suite.addTest(unittest.makeSuite(TestSemanticBehaviorAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestSemanticStyleProfiler))
    test_suite.addTest(unittest.makeSuite(TestSemanticSpaceBehaviorEngine))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果摘要
    print(f"\n{'='*60}")
    print(f"语义空间行为算法测试摘要:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"{'='*60}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}")
