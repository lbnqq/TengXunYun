#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Behavior Analyzer - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import numpy as np
import json
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

try:
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available for advanced analysis")


class SemanticBehaviorAnalyzer:
    """语义空间行为分析器 - 讯飞大模型作为风格评估员"""
    
    def __init__(self, llm_client=None):
        """
        初始化语义行为分析器
        
        Args:
            llm_client: 讯飞大模型客户端（作为风格评估员）
        """
        self.llm_client = llm_client
        self.evaluation_templates = self._init_evaluation_templates()
    
    def _init_evaluation_templates(self) -> Dict[str, str]:
        """初始化评估提示词模板"""
        return {
            "cluster_interpretation": """请分析以下概念聚类，描述每个聚类代表的主题和概念间的关联：

聚类结果：
{cluster_info}

请以JSON格式输出分析结果：
{{
  "cluster_themes": [
    {{"cluster_id": "cluster_0", "theme": "主题描述", "coherence": 1-5, "explanation": "聚类内概念关联解释"}},
    ...
  ],
  "cluster_relationships": [
    {{"cluster1": "cluster_0", "cluster2": "cluster_1", "relationship": "互补/对立/独立/包含", "strength": 1-5}},
    ...
  ],
  "overall_assessment": {{"semantic_organization": 1-5, "concept_diversity": 1-5, "thematic_clarity": 1-5}}
}}""",

            "novelty_assessment": """请评估以下概念对的关联创新度：

概念对分析：
{concept_pairs}

原文语境：
{original_text}

请以JSON格式输出评估结果：
{{
  "novelty_assessments": [
    {{
      "concept1": "概念1",
      "concept2": "概念2", 
      "novelty_score": 1-5,
      "novelty_type": "富有创意的联想/恰当的类比/牵强的比附/无意义的并列",
      "explanation": "评估理由",
      "context_relevance": 1-5
    }},
    ...
  ],
  "overall_creativity": {{"average_novelty": 0.0, "creative_density": 1-5, "innovation_style": "描述"}}
}}""",

            "semantic_distance_evaluation": """请评估以下文本的语义距离特征：

语义距离统计：
{distance_stats}

概念分布：
{concept_distribution}

请以JSON格式输出评估：
{{
  "distance_characteristics": {{
    "semantic_span": "紧密/适中/分散",
    "concept_coherence": 1-5,
    "thematic_focus": 1-5,
    "explanation": "语义距离特征描述"
  }},
  "writing_style_implications": {{
    "style_type": "专业聚焦/广泛涉猎/跳跃思维/逻辑严密",
    "cognitive_pattern": "描述认知模式",
    "audience_accessibility": 1-5
  }}
}}""",

            "emotional_semantic_analysis": """请分析以下文本的情感语义特征：

情感词汇分布：
{emotional_distribution}

概念情感倾向：
{concept_emotions}

请以JSON格式输出分析：
{{
  "emotional_patterns": {{
    "dominant_emotion": "积极/消极/中性/复杂",
    "emotional_intensity": 1-5,
    "emotional_consistency": 1-5,
    "emotional_sophistication": 1-5
  }},
  "concept_emotional_mapping": [
    {{"concept": "概念", "emotional_association": "情感倾向", "strength": 1-5}},
    ...
  ],
  "style_characteristics": {{
    "emotional_expressiveness": 1-5,
    "subjective_tendency": 1-5,
    "persuasive_power": 1-5
  }}
}}"""
        }
    
    def analyze_concept_clustering(self, vector_result: Dict[str, Any], 
                                 cluster_result: Dict[str, Any],
                                 original_text: str = "") -> Dict[str, Any]:
        """
        分析概念聚类行为
        
        Args:
            vector_result: 向量化结果
            cluster_result: 聚类结果
            original_text: 原始文本（用于上下文分析）
        """
        analysis_result = {
            "analysis_time": datetime.now().isoformat(),
            "clustering_metrics": {},
            "llm_interpretation": {},
            "behavioral_indicators": {},
            "success": False
        }
        
        try:
            print("🔍 正在分析概念聚类行为...")
            
            # 1. 计算聚类量化指标
            clustering_metrics = self._calculate_clustering_metrics(cluster_result, vector_result)
            analysis_result["clustering_metrics"] = clustering_metrics
            
            # 2. LLM聚类解释（讯飞大模型作为评估员）
            if self.llm_client:
                llm_interpretation = self._get_llm_cluster_interpretation(
                    cluster_result, original_text
                )
                analysis_result["llm_interpretation"] = llm_interpretation
            
            # 3. 提取行为指标
            behavioral_indicators = self._extract_clustering_behavioral_indicators(
                clustering_metrics, analysis_result.get("llm_interpretation", {})
            )
            analysis_result["behavioral_indicators"] = behavioral_indicators
            
            analysis_result["success"] = True
            print("✅ 概念聚类行为分析完成")
            
        except Exception as e:
            analysis_result["error"] = str(e)
            print(f"❌ 概念聚类行为分析失败: {str(e)}")
        
        return analysis_result
    
    def analyze_semantic_distance_patterns(self, vector_result: Dict[str, Any],
                                         similarity_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析语义距离模式"""
        analysis_result = {
            "analysis_time": datetime.now().isoformat(),
            "distance_metrics": {},
            "pattern_analysis": {},
            "llm_evaluation": {},
            "success": False
        }
        
        try:
            print("🔍 正在分析语义距离模式...")
            
            # 1. 计算距离指标
            distance_metrics = self._calculate_distance_metrics(similarity_result)
            analysis_result["distance_metrics"] = distance_metrics
            
            # 2. 模式分析
            pattern_analysis = self._analyze_distance_patterns(distance_metrics, vector_result)
            analysis_result["pattern_analysis"] = pattern_analysis
            
            # 3. LLM评估
            if self.llm_client:
                llm_evaluation = self._get_llm_distance_evaluation(
                    distance_metrics, pattern_analysis
                )
                analysis_result["llm_evaluation"] = llm_evaluation
            
            analysis_result["success"] = True
            print("✅ 语义距离模式分析完成")
            
        except Exception as e:
            analysis_result["error"] = str(e)
            print(f"❌ 语义距离模式分析失败: {str(e)}")
        
        return analysis_result
    
    def assess_associative_novelty(self, vector_result: Dict[str, Any],
                                 similarity_result: Dict[str, Any],
                                 original_text: str = "") -> Dict[str, Any]:
        """评估联想创新度"""
        assessment_result = {
            "assessment_time": datetime.now().isoformat(),
            "novelty_candidates": [],
            "llm_assessments": {},
            "creativity_metrics": {},
            "success": False
        }
        
        try:
            print("🔍 正在评估联想创新度...")
            
            # 1. 识别候选创新联想对
            novelty_candidates = self._identify_novelty_candidates(
                vector_result, similarity_result
            )
            assessment_result["novelty_candidates"] = novelty_candidates
            
            # 2. LLM创新度评估
            if self.llm_client and novelty_candidates:
                llm_assessments = self._get_llm_novelty_assessment(
                    novelty_candidates, original_text
                )
                assessment_result["llm_assessments"] = llm_assessments
            
            # 3. 计算创新度指标
            creativity_metrics = self._calculate_creativity_metrics(
                novelty_candidates, assessment_result.get("llm_assessments", {})
            )
            assessment_result["creativity_metrics"] = creativity_metrics
            
            assessment_result["success"] = True
            print("✅ 联想创新度评估完成")
            
        except Exception as e:
            assessment_result["error"] = str(e)
            print(f"❌ 联想创新度评估失败: {str(e)}")
        
        return assessment_result
    
    def analyze_emotional_semantic_behavior(self, semantic_units: Dict[str, Any],
                                          vector_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析情感语义行为"""
        analysis_result = {
            "analysis_time": datetime.now().isoformat(),
            "emotional_distribution": {},
            "concept_emotions": {},
            "llm_analysis": {},
            "behavioral_patterns": {},
            "success": False
        }
        
        try:
            print("🔍 正在分析情感语义行为...")
            
            # 1. 提取情感分布
            emotional_distribution = self._extract_emotional_distribution(semantic_units)
            analysis_result["emotional_distribution"] = emotional_distribution
            
            # 2. 分析概念情感倾向
            concept_emotions = self._analyze_concept_emotions(semantic_units, vector_result)
            analysis_result["concept_emotions"] = concept_emotions
            
            # 3. LLM情感语义分析
            if self.llm_client:
                llm_analysis = self._get_llm_emotional_analysis(
                    emotional_distribution, concept_emotions
                )
                analysis_result["llm_analysis"] = llm_analysis
            
            # 4. 提取行为模式
            behavioral_patterns = self._extract_emotional_behavioral_patterns(
                emotional_distribution, concept_emotions, analysis_result.get("llm_analysis", {})
            )
            analysis_result["behavioral_patterns"] = behavioral_patterns
            
            analysis_result["success"] = True
            print("✅ 情感语义行为分析完成")
            
        except Exception as e:
            analysis_result["error"] = str(e)
            print(f"❌ 情感语义行为分析失败: {str(e)}")
        
        return analysis_result
    
    def _calculate_clustering_metrics(self, cluster_result: Dict[str, Any],
                                    vector_result: Dict[str, Any]) -> Dict[str, Any]:
        """计算聚类量化指标"""
        metrics = {
            "cluster_count": 0,
            "average_cluster_size": 0,
            "cluster_size_variance": 0,
            "intra_cluster_distances": {},
            "inter_cluster_distances": {},
            "silhouette_score": None
        }
        
        try:
            clusters = cluster_result.get("clusters", {})
            metrics["cluster_count"] = len(clusters)
            
            if clusters:
                # 聚类大小统计
                cluster_sizes = [cluster["size"] for cluster in clusters.values()]
                metrics["average_cluster_size"] = np.mean(cluster_sizes)
                metrics["cluster_size_variance"] = np.var(cluster_sizes)
                
                # 计算簇内和簇间距离
                for cluster_id, cluster_data in clusters.items():
                    concepts = cluster_data["concepts"]
                    if len(concepts) > 1:
                        # 簇内平均距离
                        distances = []
                        for i, concept1 in enumerate(concepts):
                            for concept2 in concepts[i+1:]:
                                dist = concept1.get("distance_to_center", 0) + concept2.get("distance_to_center", 0)
                                distances.append(dist)
                        
                        if distances:
                            metrics["intra_cluster_distances"][cluster_id] = {
                                "average": np.mean(distances),
                                "max": np.max(distances),
                                "min": np.min(distances)
                            }
        
        except Exception as e:
            metrics["error"] = str(e)
        
        return metrics
    
    def _get_llm_cluster_interpretation(self, cluster_result: Dict[str, Any],
                                      original_text: str) -> Dict[str, Any]:
        """获取LLM聚类解释"""
        try:
            # 准备聚类信息
            clusters = cluster_result.get("clusters", {})
            cluster_info = []
            
            for cluster_id, cluster_data in clusters.items():
                concepts = [concept["name"] for concept in cluster_data["concepts"]]
                cluster_info.append(f"{cluster_id}: {', '.join(concepts)}")
            
            cluster_info_str = "\n".join(cluster_info)
            
            # 构建提示词
            prompt = self.evaluation_templates["cluster_interpretation"].format(
                cluster_info=cluster_info_str
            )
            
            # 调用LLM
            response = self.llm_client.generate(prompt)
            
            # 解析响应
            return self._parse_json_response(response, "cluster_interpretation")
            
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_distance_metrics(self, similarity_result: Dict[str, Any]) -> Dict[str, Any]:
        """计算距离指标"""
        metrics = {
            "average_similarity": 0,
            "similarity_variance": 0,
            "max_similarity": 0,
            "min_similarity": 1,
            "similarity_distribution": {}
        }
        
        try:
            # 从相似度统计中提取指标
            similarity_stats = similarity_result.get("similarity_statistics", {})
            concept_stats = similarity_stats.get("concept_similarity_stats", {})
            
            if concept_stats:
                metrics["average_similarity"] = concept_stats.get("average", 0)
                metrics["max_similarity"] = concept_stats.get("max", 0)
                metrics["min_similarity"] = concept_stats.get("min", 1)
                metrics["similarity_variance"] = concept_stats.get("std", 0) ** 2
            
            # 分析相似度分布
            concept_similarities = similarity_result.get("concept_similarities", {})
            all_similarities = []
            
            for name1, sims in concept_similarities.items():
                all_similarities.extend(sims.values())
            
            if all_similarities:
                # 分布统计
                metrics["similarity_distribution"] = {
                    "high_similarity_count": sum(1 for s in all_similarities if s > 0.7),
                    "medium_similarity_count": sum(1 for s in all_similarities if 0.3 <= s <= 0.7),
                    "low_similarity_count": sum(1 for s in all_similarities if s < 0.3),
                    "total_pairs": len(all_similarities)
                }
        
        except Exception as e:
            metrics["error"] = str(e)
        
        return metrics
    
    def _identify_novelty_candidates(self, vector_result: Dict[str, Any],
                                   similarity_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别候选创新联想对"""
        candidates = []
        
        try:
            # 从概念相似度中找出距离较大但可能有创新联想的概念对
            concept_similarities = similarity_result.get("concept_similarities", {})
            
            for concept1, similarities in concept_similarities.items():
                for concept2, similarity in similarities.items():
                    # 选择相似度较低但不是最低的概念对作为候选
                    if 0.1 <= similarity <= 0.4:  # 中等距离，可能有创新联想
                        candidates.append({
                            "concept1": concept1,
                            "concept2": concept2,
                            "similarity": similarity,
                            "distance": 1 - similarity,
                            "candidate_type": "medium_distance"
                        })
            
            # 按距离排序，选择最有潜力的候选
            candidates.sort(key=lambda x: x["distance"], reverse=True)
            return candidates[:10]  # 最多返回10个候选
        
        except Exception as e:
            return [{"error": str(e)}]
    
    def _get_llm_novelty_assessment(self, novelty_candidates: List[Dict[str, Any]],
                                   original_text: str) -> Dict[str, Any]:
        """获取LLM创新度评估"""
        try:
            # 准备概念对信息
            concept_pairs = []
            for candidate in novelty_candidates[:5]:  # 限制数量
                concept_pairs.append({
                    "concept1": candidate["concept1"],
                    "concept2": candidate["concept2"],
                    "similarity": candidate["similarity"]
                })
            
            # 构建提示词
            prompt = self.evaluation_templates["novelty_assessment"].format(
                concept_pairs=json.dumps(concept_pairs, ensure_ascii=False, indent=2),
                original_text=original_text[:1000]  # 限制文本长度
            )
            
            # 调用LLM
            response = self.llm_client.generate(prompt)
            
            # 解析响应
            return self._parse_json_response(response, "novelty_assessment")
            
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_emotional_distribution(self, semantic_units: Dict[str, Any]) -> Dict[str, Any]:
        """提取情感分布"""
        distribution = {
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "emotional_intensity_avg": 0,
            "emotional_words": []
        }
        
        try:
            # 分析形容词情感
            adjectives = semantic_units.get("key_adjectives", [])
            intensities = []
            
            for adj in adjectives:
                sentiment = adj.get("sentiment_polarity", "中性")
                intensity = adj.get("sentiment_intensity", 3)
                
                if sentiment == "积极":
                    distribution["positive_count"] += 1
                elif sentiment == "消极":
                    distribution["negative_count"] += 1
                else:
                    distribution["neutral_count"] += 1
                
                intensities.append(intensity)
                distribution["emotional_words"].append({
                    "word": adj.get("text", ""),
                    "sentiment": sentiment,
                    "intensity": intensity
                })
            
            if intensities:
                distribution["emotional_intensity_avg"] = np.mean(intensities)
        
        except Exception as e:
            distribution["error"] = str(e)
        
        return distribution
    
    def _parse_json_response(self, response: str, response_type: str) -> Dict[str, Any]:
        """解析JSON响应"""
        try:
            # 尝试提取JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"raw_response": response, "parsing_failed": True}
        except:
            return {"raw_response": response, "parsing_failed": True}
    
    def _analyze_distance_patterns(self, distance_metrics: Dict[str, Any],
                                 vector_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析距离模式"""
        patterns = {
            "semantic_span": "unknown",
            "concept_distribution": "unknown",
            "clustering_tendency": "unknown"
        }
        
        try:
            avg_sim = distance_metrics.get("average_similarity", 0)
            sim_variance = distance_metrics.get("similarity_variance", 0)
            
            # 语义跨度分析
            if avg_sim > 0.6:
                patterns["semantic_span"] = "紧密"
            elif avg_sim > 0.3:
                patterns["semantic_span"] = "适中"
            else:
                patterns["semantic_span"] = "分散"
            
            # 概念分布分析
            if sim_variance < 0.1:
                patterns["concept_distribution"] = "均匀"
            elif sim_variance < 0.3:
                patterns["concept_distribution"] = "适中"
            else:
                patterns["concept_distribution"] = "不均匀"
            
            # 聚类倾向
            distribution = distance_metrics.get("similarity_distribution", {})
            high_sim = distribution.get("high_similarity_count", 0)
            total_pairs = distribution.get("total_pairs", 1)
            
            if high_sim / total_pairs > 0.3:
                patterns["clustering_tendency"] = "强"
            elif high_sim / total_pairs > 0.1:
                patterns["clustering_tendency"] = "中等"
            else:
                patterns["clustering_tendency"] = "弱"
        
        except Exception as e:
            patterns["error"] = str(e)
        
        return patterns
    
    def _extract_clustering_behavioral_indicators(self, clustering_metrics: Dict[str, Any],
                                                llm_interpretation: Dict[str, Any]) -> Dict[str, Any]:
        """提取聚类行为指标"""
        indicators = {
            "conceptual_organization": "unknown",
            "thematic_coherence": "unknown", 
            "cognitive_complexity": "unknown"
        }
        
        try:
            cluster_count = clustering_metrics.get("cluster_count", 0)
            avg_size = clustering_metrics.get("average_cluster_size", 0)
            
            # 概念组织能力
            if cluster_count >= 3 and avg_size >= 2:
                indicators["conceptual_organization"] = "良好"
            elif cluster_count >= 2:
                indicators["conceptual_organization"] = "一般"
            else:
                indicators["conceptual_organization"] = "简单"
            
            # 从LLM解释中提取主题连贯性
            if "overall_assessment" in llm_interpretation:
                assessment = llm_interpretation["overall_assessment"]
                thematic_clarity = assessment.get("thematic_clarity", 3)
                
                if thematic_clarity >= 4:
                    indicators["thematic_coherence"] = "高"
                elif thematic_clarity >= 3:
                    indicators["thematic_coherence"] = "中等"
                else:
                    indicators["thematic_coherence"] = "低"
        
        except Exception as e:
            indicators["error"] = str(e)
        
        return indicators
    
    def _calculate_creativity_metrics(self, novelty_candidates: List[Dict[str, Any]],
                                    llm_assessments: Dict[str, Any]) -> Dict[str, Any]:
        """计算创新度指标"""
        metrics = {
            "total_candidates": len(novelty_candidates),
            "average_novelty_score": 0,
            "high_novelty_count": 0,
            "creativity_density": 0
        }
        
        try:
            # 从LLM评估中提取创新度分数
            assessments = llm_assessments.get("novelty_assessments", [])
            
            if assessments:
                scores = [a.get("novelty_score", 3) for a in assessments]
                metrics["average_novelty_score"] = np.mean(scores)
                metrics["high_novelty_count"] = sum(1 for s in scores if s >= 4)
                
                # 创新密度 = 高创新度概念对数量 / 总概念对数量
                total_pairs = len(novelty_candidates)
                metrics["creativity_density"] = metrics["high_novelty_count"] / total_pairs if total_pairs > 0 else 0
        
        except Exception as e:
            metrics["error"] = str(e)
        
        return metrics
    
    def _analyze_concept_emotions(self, semantic_units: Dict[str, Any],
                                vector_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析概念情感倾向"""
        concept_emotions = {}
        
        try:
            # 分析概念的情感关联
            concepts = semantic_units.get("concepts", [])
            adjectives = semantic_units.get("key_adjectives", [])
            
            # 为每个概念分配情感倾向（简化版本）
            for concept in concepts:
                concept_name = concept.get("text", "")
                # 这里可以通过更复杂的算法来分析概念与情感词的关联
                concept_emotions[concept_name] = {
                    "emotional_association": "中性",
                    "strength": 3,
                    "context": concept.get("role", "")
                }
        
        except Exception as e:
            concept_emotions["error"] = str(e)
        
        return concept_emotions
    
    def _extract_emotional_behavioral_patterns(self, emotional_distribution: Dict[str, Any],
                                             concept_emotions: Dict[str, Any],
                                             llm_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """提取情感行为模式"""
        patterns = {
            "emotional_expressiveness": "unknown",
            "emotional_balance": "unknown",
            "subjective_tendency": "unknown"
        }
        
        try:
            # 情感表达力
            total_emotional = (emotional_distribution.get("positive_count", 0) + 
                             emotional_distribution.get("negative_count", 0))
            total_words = total_emotional + emotional_distribution.get("neutral_count", 0)
            
            if total_words > 0:
                emotional_ratio = total_emotional / total_words
                if emotional_ratio > 0.6:
                    patterns["emotional_expressiveness"] = "高"
                elif emotional_ratio > 0.3:
                    patterns["emotional_expressiveness"] = "中等"
                else:
                    patterns["emotional_expressiveness"] = "低"
            
            # 情感平衡
            pos_count = emotional_distribution.get("positive_count", 0)
            neg_count = emotional_distribution.get("negative_count", 0)
            
            if pos_count > 0 and neg_count > 0:
                balance_ratio = min(pos_count, neg_count) / max(pos_count, neg_count)
                if balance_ratio > 0.7:
                    patterns["emotional_balance"] = "平衡"
                else:
                    patterns["emotional_balance"] = "偏向性"
            elif pos_count > neg_count:
                patterns["emotional_balance"] = "积极倾向"
            elif neg_count > pos_count:
                patterns["emotional_balance"] = "消极倾向"
            else:
                patterns["emotional_balance"] = "中性"
        
        except Exception as e:
            patterns["error"] = str(e)
        
        return patterns

    def _get_llm_distance_evaluation(self, distance_metrics: Dict[str, Any],
                                   pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """获取LLM距离评估"""
        try:
            # 准备距离统计信息
            distance_stats = {
                "average_similarity": distance_metrics.get("average_similarity", 0),
                "similarity_variance": distance_metrics.get("similarity_variance", 0),
                "distribution": distance_metrics.get("similarity_distribution", {})
            }

            # 准备概念分布信息
            concept_distribution = {
                "semantic_span": pattern_analysis.get("semantic_span", "unknown"),
                "concept_distribution": pattern_analysis.get("concept_distribution", "unknown"),
                "clustering_tendency": pattern_analysis.get("clustering_tendency", "unknown")
            }

            # 构建提示词
            prompt = self.evaluation_templates["semantic_distance_evaluation"].format(
                distance_stats=json.dumps(distance_stats, ensure_ascii=False, indent=2),
                concept_distribution=json.dumps(concept_distribution, ensure_ascii=False, indent=2)
            )

            # 调用LLM
            response = self.llm_client.generate(prompt)

            # 解析响应
            return self._parse_json_response(response, "distance_evaluation")

        except Exception as e:
            return {"error": str(e)}

    def _get_llm_emotional_analysis(self, emotional_distribution: Dict[str, Any],
                                  concept_emotions: Dict[str, Any]) -> Dict[str, Any]:
        """获取LLM情感分析"""
        try:
            # 构建提示词
            prompt = self.evaluation_templates["emotional_semantic_analysis"].format(
                emotional_distribution=json.dumps(emotional_distribution, ensure_ascii=False, indent=2),
                concept_emotions=json.dumps(concept_emotions, ensure_ascii=False, indent=2)
            )

            # 调用LLM
            response = self.llm_client.generate(prompt)

            # 解析响应
            return self._parse_json_response(response, "emotional_analysis")

        except Exception as e:
            return {"error": str(e)}
