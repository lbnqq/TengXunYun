"""
语义空间行为算法演示程序
展示如何使用讯飞大模型作为语义分析助手和风格评估员
"""

import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.tools.semantic_space_behavior_engine import SemanticSpaceBehaviorEngine
from core.tools.comprehensive_style_processor import ComprehensiveStyleProcessor


class MockXunfeiLLMClient:
    """模拟讯飞大模型客户端"""
    
    def generate(self, prompt: str) -> str:
        """模拟LLM响应"""
        if "语义单元识别" in prompt or "concepts" in prompt:
            return """
{
  "concepts": [
    {"text": "人工智能", "role": "核心概念", "importance": 5},
    {"text": "机器学习", "role": "相关概念", "importance": 4},
    {"text": "深度学习", "role": "相关概念", "importance": 4},
    {"text": "神经网络", "role": "相关概念", "importance": 3}
  ],
  "named_entities": [
    {"text": "谷歌", "type": "组织名", "context": "科技公司"},
    {"text": "OpenAI", "type": "组织名", "context": "AI研究机构"},
    {"text": "GPT", "type": "产品名", "context": "语言模型"}
  ],
  "key_adjectives": [
    {"text": "智能", "context": "智能系统", "sentiment_intensity": 4, "sentiment_polarity": "积极"},
    {"text": "先进", "context": "先进技术", "sentiment_intensity": 4, "sentiment_polarity": "积极"},
    {"text": "复杂", "context": "复杂算法", "sentiment_intensity": 3, "sentiment_polarity": "中性"}
  ],
  "key_verbs": [
    {"text": "发展", "context": "技术发展", "action_type": "变化", "intensity": 4},
    {"text": "突破", "context": "技术突破", "action_type": "动作", "intensity": 5},
    {"text": "应用", "context": "技术应用", "action_type": "动作", "intensity": 3}
  ],
  "key_phrases": [
    {"text": "自然语言处理", "role": "技术术语", "domain": "人工智能"},
    {"text": "计算机视觉", "role": "技术术语", "domain": "人工智能"},
    {"text": "算法优化", "role": "技术术语", "domain": "计算机科学"}
  ],
  "semantic_relations": [
    {"entity1": "人工智能", "relation": "包含", "entity2": "机器学习", "strength": 5},
    {"entity1": "机器学习", "relation": "包含", "entity2": "深度学习", "strength": 4}
  ]
}
"""
        elif "聚类" in prompt and "主题" in prompt:
            return """
{
  "cluster_themes": [
    {"cluster_id": "cluster_0", "theme": "AI核心技术", "coherence": 5, "explanation": "人工智能、机器学习、深度学习等核心技术概念聚集，主题明确"},
    {"cluster_id": "cluster_1", "theme": "技术应用", "coherence": 4, "explanation": "自然语言处理、计算机视觉等应用领域概念"}
  ],
  "cluster_relationships": [
    {"cluster1": "cluster_0", "cluster2": "cluster_1", "relationship": "支撑", "strength": 4}
  ],
  "overall_assessment": {"semantic_organization": 5, "concept_diversity": 4, "thematic_clarity": 5}
}
"""
        elif "创新度" in prompt or "novelty" in prompt:
            return """
{
  "novelty_assessments": [
    {
      "concept1": "人工智能",
      "concept2": "艺术创作",
      "novelty_score": 4,
      "novelty_type": "富有创意的联想",
      "explanation": "将AI技术与艺术创作结合是很有创意的想法",
      "context_relevance": 4
    }
  ],
  "overall_creativity": {"average_novelty": 4.0, "creative_density": 4, "innovation_style": "技术与人文的创新结合"}
}
"""
        elif "语义距离" in prompt:
            return """
{
  "distance_characteristics": {
    "semantic_span": "适中",
    "concept_coherence": 4,
    "thematic_focus": 4,
    "explanation": "概念间语义距离适中，既有核心主题又有适度扩展"
  },
  "writing_style_implications": {
    "style_type": "专业聚焦",
    "cognitive_pattern": "系统性思维，逻辑清晰",
    "audience_accessibility": 3
  }
}
"""
        elif "情感语义" in prompt:
            return """
{
  "emotional_patterns": {
    "dominant_emotion": "积极",
    "emotional_intensity": 4,
    "emotional_consistency": 4,
    "emotional_sophistication": 3
  },
  "concept_emotional_mapping": [
    {"concept": "人工智能", "emotional_association": "积极期待", "strength": 4},
    {"concept": "技术发展", "emotional_association": "乐观", "strength": 4}
  ],
  "style_characteristics": {
    "emotional_expressiveness": 3,
    "subjective_tendency": 2,
    "persuasive_power": 4
  }
}
"""
        else:
            return "评分：4\n理由：这是一个模拟的讯飞大模型响应，展示了语义分析能力。"


def demonstrate_semantic_unit_identification():
    """演示语义单元识别功能"""
    print("=" * 60)
    print("阶段一：语义单元识别与表示")
    print("=" * 60)
    
    mock_llm = MockXunfeiLLMClient()
    
    # 示例文本
    text = """
    人工智能技术正在经历前所未有的发展阶段。谷歌、OpenAI等科技巨头
    在机器学习和深度学习领域取得了重大突破。这些先进的神经网络算法
    不仅在自然语言处理方面表现出色，在计算机视觉领域也展现了
    令人惊叹的能力。随着技术的不断发展，AI系统正在变得越来越智能，
    为人类社会带来了无限的可能性。
    """
    
    from core.tools.semantic_unit_identifier import SemanticUnitIdentifier
    
    identifier = SemanticUnitIdentifier(mock_llm)
    
    print("🔍 正在识别语义单元...")
    result = identifier.identify_semantic_units(text, "comprehensive")
    
    if result.get("success"):
        print("✅ 语义单元识别成功")
        
        semantic_units = result["semantic_units"]
        
        # 显示识别结果
        concepts = semantic_units.get("concepts", [])
        print(f"\n📋 识别出 {len(concepts)} 个概念:")
        for concept in concepts[:5]:
            print(f"  - {concept.get('text', '')} (重要性: {concept.get('importance', 0)})")
        
        entities = semantic_units.get("named_entities", [])
        print(f"\n🏢 识别出 {len(entities)} 个实体:")
        for entity in entities[:3]:
            print(f"  - {entity.get('text', '')} ({entity.get('type', '')})")
        
        adjectives = semantic_units.get("key_adjectives", [])
        print(f"\n💭 识别出 {len(adjectives)} 个关键形容词:")
        for adj in adjectives[:3]:
            print(f"  - {adj.get('text', '')} (情感: {adj.get('sentiment_polarity', '')})")
        
        # 统计信息
        stats = identifier.get_semantic_unit_statistics(semantic_units)
        print(f"\n📊 统计信息:")
        print(f"  - 概念数量: {stats.get('concept_count', 0)}")
        print(f"  - 实体数量: {stats.get('entity_count', 0)}")
        print(f"  - 形容词数量: {stats.get('adjective_count', 0)}")
        
    else:
        print("❌ 语义单元识别失败")
        print(f"错误: {result.get('error', '未知错误')}")
    
    return result


def demonstrate_semantic_space_mapping(semantic_units_result):
    """演示语义空间映射功能"""
    print("\n" + "=" * 60)
    print("阶段二：语义空间映射")
    print("=" * 60)
    
    if not semantic_units_result.get("success"):
        print("❌ 无法进行语义空间映射，语义单元识别失败")
        return {}
    
    from core.tools.semantic_space_mapper import SemanticSpaceMapper
    
    mapper = SemanticSpaceMapper()
    semantic_units = semantic_units_result["semantic_units"]
    
    print("🗺️ 正在进行语义空间映射...")
    
    # 1. 向量编码
    print("  🔄 编码语义单元为向量...")
    vector_result = mapper.encode_semantic_units(semantic_units)
    
    if vector_result.get("success"):
        print("  ✅ 向量编码完成")
        
        stats = vector_result.get("vector_statistics", {})
        print(f"    - 总向量数: {stats.get('total_vectors', 0)}")
        print(f"    - 向量维度: {stats.get('vector_dimensions', 0)}")
        print(f"    - 向量密度: {stats.get('vector_density', 0):.3f}")
        
        # 2. 相似度计算
        print("  🔄 计算语义相似度...")
        similarity_result = mapper.calculate_semantic_similarities(vector_result, "cosine")
        
        if similarity_result.get("success"):
            print("  ✅ 相似度计算完成")
            
            sim_stats = similarity_result.get("similarity_statistics", {})
            concept_stats = sim_stats.get("concept_similarity_stats", {})
            if concept_stats:
                print(f"    - 平均相似度: {concept_stats.get('average', 0):.3f}")
                print(f"    - 最大相似度: {concept_stats.get('max', 0):.3f}")
                print(f"    - 最小相似度: {concept_stats.get('min', 0):.3f}")
        
        # 3. 聚类分析
        print("  🔄 进行语义聚类...")
        cluster_result = mapper.find_semantic_clusters(vector_result)
        
        if cluster_result.get("success"):
            print("  ✅ 语义聚类完成")
            
            clusters = cluster_result.get("clusters", {})
            print(f"    - 聚类数量: {len(clusters)}")
            
            for cluster_id, cluster_data in clusters.items():
                concepts = [c["name"] for c in cluster_data["concepts"]]
                print(f"    - {cluster_id}: {', '.join(concepts[:3])}")
        
        return {
            "vector_result": vector_result,
            "similarity_result": similarity_result,
            "cluster_result": cluster_result
        }
    
    else:
        print("❌ 语义空间映射失败")
        return {}


def demonstrate_semantic_behavior_analysis(mapping_results, original_text):
    """演示语义空间行为分析"""
    print("\n" + "=" * 60)
    print("阶段三：语义空间行为分析")
    print("=" * 60)
    
    if not mapping_results:
        print("❌ 无法进行行为分析，语义空间映射失败")
        return {}
    
    from core.tools.semantic_behavior_analyzer import SemanticBehaviorAnalyzer
    
    mock_llm = MockXunfeiLLMClient()
    analyzer = SemanticBehaviorAnalyzer(mock_llm)
    
    vector_result = mapping_results.get("vector_result", {})
    similarity_result = mapping_results.get("similarity_result", {})
    cluster_result = mapping_results.get("cluster_result", {})
    
    behavior_results = {}
    
    # 1. 概念聚类行为分析
    if cluster_result.get("success"):
        print("🧠 正在分析概念聚类行为...")
        clustering_analysis = analyzer.analyze_concept_clustering(
            vector_result, cluster_result, original_text
        )
        
        if clustering_analysis.get("success"):
            print("  ✅ 概念聚类行为分析完成")
            
            behavioral_indicators = clustering_analysis.get("behavioral_indicators", {})
            print(f"    - 概念组织能力: {behavioral_indicators.get('conceptual_organization', 'unknown')}")
            print(f"    - 主题连贯性: {behavioral_indicators.get('thematic_coherence', 'unknown')}")
            
            behavior_results["clustering_analysis"] = clustering_analysis
    
    # 2. 语义距离模式分析
    if similarity_result.get("success"):
        print("  🔄 分析语义距离模式...")
        distance_analysis = analyzer.analyze_semantic_distance_patterns(
            vector_result, similarity_result
        )
        
        if distance_analysis.get("success"):
            print("  ✅ 语义距离模式分析完成")
            
            pattern_analysis = distance_analysis.get("pattern_analysis", {})
            print(f"    - 语义跨度: {pattern_analysis.get('semantic_span', 'unknown')}")
            print(f"    - 概念分布: {pattern_analysis.get('concept_distribution', 'unknown')}")
            
            behavior_results["distance_analysis"] = distance_analysis
    
    # 3. 联想创新度评估
    if similarity_result.get("success"):
        print("  🔄 评估联想创新度...")
        novelty_assessment = analyzer.assess_associative_novelty(
            vector_result, similarity_result, original_text
        )
        
        if novelty_assessment.get("success"):
            print("  ✅ 联想创新度评估完成")
            
            creativity_metrics = novelty_assessment.get("creativity_metrics", {})
            print(f"    - 平均创新度: {creativity_metrics.get('average_novelty_score', 0):.1f}")
            print(f"    - 高创新度数量: {creativity_metrics.get('high_novelty_count', 0)}")
            
            behavior_results["novelty_assessment"] = novelty_assessment
    
    return behavior_results


def demonstrate_style_profile_construction(all_results, document_name):
    """演示风格画像构建"""
    print("\n" + "=" * 60)
    print("阶段四：特征融合与风格画像构建")
    print("=" * 60)
    
    from core.tools.semantic_style_profiler import SemanticStyleProfiler
    
    profiler = SemanticStyleProfiler()
    
    print("🎨 正在构建语义风格画像...")
    
    # 整合所有分析结果
    analysis_results = {
        "vector_result": all_results.get("mapping_results", {}).get("vector_result", {}),
        "similarity_result": all_results.get("mapping_results", {}).get("similarity_result", {}),
        "cluster_result": all_results.get("mapping_results", {}).get("cluster_result", {}),
        **all_results.get("behavior_results", {})
    }
    
    profile = profiler.build_semantic_style_profile(analysis_results, document_name)
    
    if profile.get("success"):
        print("✅ 语义风格画像构建完成")
        
        # 显示风格分数
        style_scores = profile.get("style_scores", {})
        print("\n📊 风格维度评分:")
        for dimension, score in style_scores.items():
            dimension_name = profiler.style_dimensions.get(dimension, dimension)
            print(f"  - {dimension_name}: {score:.1f}/5.0")
        
        # 显示风格分类
        classification = profile.get("style_classification", {})
        print(f"\n🏷️ 风格分类:")
        print(f"  - 主要风格: {classification.get('primary_style', 'unknown')}")
        print(f"  - 风格强度: {classification.get('style_strength', 0):.1f}")
        
        characteristics = classification.get("style_characteristics", [])
        if characteristics:
            print(f"  - 风格特征: {', '.join(characteristics)}")
        
        # 显示画像摘要
        summary = profile.get("profile_summary", {})
        print(f"\n📋 画像摘要:")
        print(f"  - 风格类型: {summary.get('profile_type', 'unknown')}")
        print(f"  - 独特性分数: {summary.get('uniqueness_score', 0):.2f}")
        
        strengths = summary.get("key_strengths", [])
        if strengths:
            print(f"  - 关键优势: {', '.join(strengths)}")
        
        improvements = summary.get("potential_improvements", [])
        if improvements:
            print(f"  - 改进建议: {', '.join(improvements)}")
    
    else:
        print("❌ 语义风格画像构建失败")
        print(f"错误: {profile.get('error', '未知错误')}")
    
    return profile


def demonstrate_comprehensive_integration():
    """演示综合集成功能"""
    print("\n" + "=" * 60)
    print("综合集成演示：语义分析 + 传统分析")
    print("=" * 60)
    
    mock_llm = MockXunfeiLLMClient()
    processor = ComprehensiveStyleProcessor(
        llm_client=mock_llm,
        storage_path="demo_comprehensive_storage"
    )
    
    text = """
    在人工智能快速发展的今天，我们见证了技术的巨大变革。从早期的
    专家系统到现在的深度学习，AI技术经历了多次重大突破。谷歌的
    AlphaGo战胜围棋世界冠军，OpenAI的GPT系列模型在自然语言处理
    方面的卓越表现，都标志着人工智能进入了一个全新的时代。
    
    这些技术进步不仅改变了我们的工作方式，也深刻影响着社会的
    各个层面。智能推荐系统让我们的生活更加便利，自动驾驶技术
    正在重塑交通行业，而医疗AI则为疾病诊断带来了新的希望。
    
    然而，随着AI技术的普及，我们也面临着新的挑战。如何确保AI
    系统的公平性和透明度？如何平衡技术发展与隐私保护？这些问题
    需要我们深入思考，并寻找合适的解决方案。
    """
    
    if processor.semantic_analysis_enabled:
        print("🚀 开始综合分析...")
        
        result = processor.analyze_semantic_behavior(
            text, "AI技术发展综述", "comprehensive"
        )
        
        if result.get("success"):
            print("✅ 综合分析完成")
            
            # 显示语义分析结果
            semantic_analysis = result.get("semantic_analysis", {})
            if semantic_analysis.get("success"):
                summary = semantic_analysis.get("analysis_summary", {})
                print(f"\n🧠 语义分析摘要:")
                print(f"  - 完成阶段: {summary.get('stages_completed', 0)}/4")
                
                findings = summary.get("key_findings", [])
                for finding in findings[:3]:
                    print(f"  - {finding}")
                
                semantic_chars = summary.get("semantic_characteristics", {})
                if semantic_chars:
                    print(f"\n📊 语义特征:")
                    for char, score in semantic_chars.items():
                        print(f"    - {char}: {score:.1f}")
            
            # 显示综合洞察
            comprehensive_insights = result.get("comprehensive_insights", {})
            if comprehensive_insights:
                print(f"\n💡 综合洞察:")
                
                multi_dim = comprehensive_insights.get("multi_dimensional_assessment", {})
                if multi_dim:
                    print("  多维度评估:")
                    for level, assessment in multi_dim.items():
                        print(f"    {level}: {assessment}")
                
                recommendations = comprehensive_insights.get("actionable_recommendations", [])
                if recommendations:
                    print("  可操作建议:")
                    for rec in recommendations[:3]:
                        print(f"    - {rec}")
        
        else:
            print("❌ 综合分析失败")
            print(f"错误: {result.get('error', '未知错误')}")
    
    else:
        print("⚠️ 语义空间行为分析功能未启用，仅进行传统分析")
        
        traditional_result = processor.extract_comprehensive_style_features(
            text, "AI技术发展综述", True
        )
        
        if traditional_result.get("success"):
            print("✅ 传统分析完成")
            
            summary = traditional_result.get("processing_summary", {})
            print(f"  - 提取特征数: {summary.get('features_extracted', 0)}")
            print(f"  - 分析模块: {', '.join(summary.get('analysis_modules_used', []))}")


def main():
    """主演示函数"""
    print("🎯 语义空间行为算法演示")
    print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("基于讯飞大模型的语义分析助手和风格评估员")
    
    # 示例文本
    demo_text = """
    人工智能技术正在经历前所未有的发展阶段。谷歌、OpenAI等科技巨头
    在机器学习和深度学习领域取得了重大突破。这些先进的神经网络算法
    不仅在自然语言处理方面表现出色，在计算机视觉领域也展现了
    令人惊叹的能力。随着技术的不断发展，AI系统正在变得越来越智能，
    为人类社会带来了无限的可能性。
    """
    
    try:
        # 阶段一：语义单元识别
        semantic_units_result = demonstrate_semantic_unit_identification()
        
        # 阶段二：语义空间映射
        mapping_results = demonstrate_semantic_space_mapping(semantic_units_result)
        
        # 阶段三：语义空间行为分析
        behavior_results = demonstrate_semantic_behavior_analysis(mapping_results, demo_text)
        
        # 阶段四：风格画像构建
        all_results = {
            "semantic_units_result": semantic_units_result,
            "mapping_results": mapping_results,
            "behavior_results": behavior_results
        }
        
        profile = demonstrate_style_profile_construction(all_results, "AI技术演示文档")
        
        # 综合集成演示
        demonstrate_comprehensive_integration()
        
        print("\n" + "=" * 60)
        print("演示总结")
        print("=" * 60)
        print("✅ 语义空间行为算法演示完成")
        print("\n🔧 技术实现要点:")
        print("  1. 讯飞大模型作为语义分析助手，识别语义单元")
        print("  2. Sentence-BERT作为量化引擎，生成向量表示")
        print("  3. 讯飞大模型作为风格评估员，提供深度分析")
        print("  4. 多维度特征融合，构建完整风格画像")
        
        print("\n💡 应用价值:")
        print("  - 深度挖掘中文文风的个性化特征")
        print("  - 结合定量分析和定性评估的优势")
        print("  - 为文风分析和对齐提供科学依据")
        print("  - 支持作者识别、风格分类等下游任务")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {str(e)}")
        print("请检查依赖包安装和配置是否正确")


if __name__ == "__main__":
    main()
