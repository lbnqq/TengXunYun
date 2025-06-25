"""
语义风格画像构建器
整合所有量化指标，构建完整的语义风格画像
"""

import numpy as np
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

try:
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available for advanced profiling")


class SemanticStyleProfiler:
    """语义风格画像构建器"""
    
    def __init__(self, storage_path: str = "src/core/knowledge_base/semantic_profiles"):
        """
        初始化语义风格画像构建器
        
        Args:
            storage_path: 画像存储路径
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # 特征权重配置
        self.feature_weights = {
            "clustering_features": 0.25,
            "distance_features": 0.20,
            "novelty_features": 0.20,
            "emotional_features": 0.15,
            "vector_features": 0.10,
            "llm_features": 0.10
        }
        
        # 风格维度定义
        self.style_dimensions = {
            "conceptual_organization": "概念组织能力",
            "semantic_coherence": "语义连贯性", 
            "creative_association": "创新联想能力",
            "emotional_expression": "情感表达力",
            "cognitive_complexity": "认知复杂度",
            "thematic_focus": "主题聚焦度"
        }
    
    def build_semantic_style_profile(self, analysis_results: Dict[str, Any],
                                   document_name: str = None) -> Dict[str, Any]:
        """
        构建语义风格画像
        
        Args:
            analysis_results: 包含所有分析结果的字典
            document_name: 文档名称
        
        Returns:
            完整的语义风格画像
        """
        profile = {
            "profile_id": self._generate_profile_id(),
            "document_name": document_name or "未命名文档",
            "creation_time": datetime.now().isoformat(),
            "feature_vector": [],
            "style_scores": {},
            "behavioral_indicators": {},
            "style_classification": {},
            "comparative_metrics": {},
            "profile_summary": {},
            "success": False
        }
        
        try:
            print("🔄 正在构建语义风格画像...")
            
            # 1. 提取和整合特征
            integrated_features = self._integrate_all_features(analysis_results)
            profile["integrated_features"] = integrated_features
            
            # 2. 生成特征向量
            feature_vector = self._generate_feature_vector(integrated_features)
            profile["feature_vector"] = feature_vector
            
            # 3. 计算风格分数
            style_scores = self._calculate_style_scores(integrated_features)
            profile["style_scores"] = style_scores
            
            # 4. 提取行为指标
            behavioral_indicators = self._extract_behavioral_indicators(analysis_results)
            profile["behavioral_indicators"] = behavioral_indicators
            
            # 5. 风格分类
            style_classification = self._classify_writing_style(style_scores, behavioral_indicators)
            profile["style_classification"] = style_classification
            
            # 6. 比较指标
            comparative_metrics = self._calculate_comparative_metrics(feature_vector, style_scores)
            profile["comparative_metrics"] = comparative_metrics
            
            # 7. 生成画像摘要
            profile_summary = self._generate_profile_summary(profile)
            profile["profile_summary"] = profile_summary
            
            profile["success"] = True
            print("✅ 语义风格画像构建完成")
            
        except Exception as e:
            profile["error"] = str(e)
            print(f"❌ 语义风格画像构建失败: {str(e)}")
        
        return profile
    
    def _integrate_all_features(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """整合所有特征"""
        integrated = {
            "clustering_features": {},
            "distance_features": {},
            "novelty_features": {},
            "emotional_features": {},
            "vector_features": {},
            "llm_features": {}
        }
        
        try:
            # 1. 聚类特征
            clustering_analysis = analysis_results.get("clustering_analysis", {})
            if clustering_analysis.get("success"):
                clustering_metrics = clustering_analysis.get("clustering_metrics", {})
                integrated["clustering_features"] = {
                    "cluster_count": clustering_metrics.get("cluster_count", 0),
                    "avg_cluster_size": clustering_metrics.get("average_cluster_size", 0),
                    "cluster_variance": clustering_metrics.get("cluster_size_variance", 0),
                    "silhouette_score": clustering_metrics.get("silhouette_score", 0) or 0
                }
            
            # 2. 距离特征
            distance_analysis = analysis_results.get("distance_analysis", {})
            if distance_analysis.get("success"):
                distance_metrics = distance_analysis.get("distance_metrics", {})
                integrated["distance_features"] = {
                    "avg_similarity": distance_metrics.get("average_similarity", 0),
                    "similarity_variance": distance_metrics.get("similarity_variance", 0),
                    "semantic_span": self._encode_categorical(
                        distance_analysis.get("pattern_analysis", {}).get("semantic_span", "unknown")
                    )
                }
            
            # 3. 创新特征
            novelty_assessment = analysis_results.get("novelty_assessment", {})
            if novelty_assessment.get("success"):
                creativity_metrics = novelty_assessment.get("creativity_metrics", {})
                integrated["novelty_features"] = {
                    "avg_novelty_score": creativity_metrics.get("average_novelty_score", 0),
                    "high_novelty_count": creativity_metrics.get("high_novelty_count", 0),
                    "creativity_density": creativity_metrics.get("creativity_density", 0)
                }
            
            # 4. 情感特征
            emotional_analysis = analysis_results.get("emotional_analysis", {})
            if emotional_analysis.get("success"):
                emotional_dist = emotional_analysis.get("emotional_distribution", {})
                integrated["emotional_features"] = {
                    "emotional_intensity": emotional_dist.get("emotional_intensity_avg", 0),
                    "positive_ratio": self._calculate_emotion_ratio(emotional_dist, "positive"),
                    "negative_ratio": self._calculate_emotion_ratio(emotional_dist, "negative"),
                    "emotional_balance": self._calculate_emotional_balance(emotional_dist)
                }
            
            # 5. 向量特征
            vector_result = analysis_results.get("vector_result", {})
            if vector_result.get("success"):
                vector_stats = vector_result.get("vector_statistics", {})
                integrated["vector_features"] = {
                    "total_vectors": vector_stats.get("total_vectors", 0),
                    "vector_density": vector_stats.get("vector_density", 0),
                    "concept_count": vector_stats.get("category_counts", {}).get("concept_vectors", 0)
                }
            
            # 6. LLM特征
            llm_features = self._extract_llm_features(analysis_results)
            integrated["llm_features"] = llm_features
        
        except Exception as e:
            integrated["error"] = str(e)
        
        return integrated
    
    def _generate_feature_vector(self, integrated_features: Dict[str, Any]) -> List[float]:
        """生成特征向量"""
        feature_vector = []
        
        try:
            # 按类别提取特征值
            for category, weight in self.feature_weights.items():
                category_features = integrated_features.get(category, {})
                
                if category_features and not category_features.get("error"):
                    # 提取数值特征
                    for key, value in category_features.items():
                        if isinstance(value, (int, float)) and not np.isnan(value):
                            feature_vector.append(float(value))
                        elif isinstance(value, bool):
                            feature_vector.append(float(value))
                        else:
                            feature_vector.append(0.0)
                else:
                    # 如果类别特征缺失，用零填充
                    feature_vector.extend([0.0] * 3)  # 每个类别假设3个特征
            
            # 标准化特征向量
            if SKLEARN_AVAILABLE and len(feature_vector) > 0:
                scaler = StandardScaler()
                feature_vector = scaler.fit_transform([feature_vector])[0].tolist()
        
        except Exception as e:
            feature_vector = [0.0] * 18  # 默认18维特征向量
        
        return feature_vector
    
    def _calculate_style_scores(self, integrated_features: Dict[str, Any]) -> Dict[str, float]:
        """计算风格分数"""
        scores = {}
        
        try:
            # 概念组织能力
            clustering_features = integrated_features.get("clustering_features", {})
            cluster_count = clustering_features.get("cluster_count", 0)
            avg_cluster_size = clustering_features.get("avg_cluster_size", 0)
            
            if cluster_count > 0 and avg_cluster_size > 0:
                scores["conceptual_organization"] = min(5.0, (cluster_count * avg_cluster_size) / 3.0)
            else:
                scores["conceptual_organization"] = 1.0
            
            # 语义连贯性
            distance_features = integrated_features.get("distance_features", {})
            avg_similarity = distance_features.get("avg_similarity", 0)
            scores["semantic_coherence"] = avg_similarity * 5.0
            
            # 创新联想能力
            novelty_features = integrated_features.get("novelty_features", {})
            avg_novelty = novelty_features.get("avg_novelty_score", 0)
            scores["creative_association"] = avg_novelty
            
            # 情感表达力
            emotional_features = integrated_features.get("emotional_features", {})
            emotional_intensity = emotional_features.get("emotional_intensity", 0)
            scores["emotional_expression"] = emotional_intensity
            
            # 认知复杂度
            vector_features = integrated_features.get("vector_features", {})
            concept_count = vector_features.get("concept_count", 0)
            vector_density = vector_features.get("vector_density", 0)
            scores["cognitive_complexity"] = min(5.0, (concept_count / 5.0) + (vector_density / 2.0))
            
            # 主题聚焦度
            semantic_span = distance_features.get("semantic_span", 0)
            scores["thematic_focus"] = 5.0 - semantic_span  # 语义跨度越小，聚焦度越高
            
            # 确保所有分数在1-5范围内
            for key in scores:
                scores[key] = max(1.0, min(5.0, scores[key]))
        
        except Exception as e:
            # 默认分数
            for dimension in self.style_dimensions:
                scores[dimension] = 3.0
        
        return scores
    
    def _extract_behavioral_indicators(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """提取行为指标"""
        indicators = {
            "writing_patterns": {},
            "cognitive_patterns": {},
            "emotional_patterns": {},
            "structural_patterns": {}
        }
        
        try:
            # 写作模式
            clustering_analysis = analysis_results.get("clustering_analysis", {})
            if clustering_analysis.get("success"):
                behavioral_indicators = clustering_analysis.get("behavioral_indicators", {})
                indicators["writing_patterns"] = {
                    "conceptual_organization": behavioral_indicators.get("conceptual_organization", "unknown"),
                    "thematic_coherence": behavioral_indicators.get("thematic_coherence", "unknown")
                }
            
            # 认知模式
            distance_analysis = analysis_results.get("distance_analysis", {})
            if distance_analysis.get("success"):
                llm_evaluation = distance_analysis.get("llm_evaluation", {})
                writing_style = llm_evaluation.get("writing_style_implications", {})
                indicators["cognitive_patterns"] = {
                    "style_type": writing_style.get("style_type", "unknown"),
                    "cognitive_pattern": writing_style.get("cognitive_pattern", "unknown")
                }
            
            # 情感模式
            emotional_analysis = analysis_results.get("emotional_analysis", {})
            if emotional_analysis.get("success"):
                behavioral_patterns = emotional_analysis.get("behavioral_patterns", {})
                indicators["emotional_patterns"] = {
                    "emotional_expressiveness": behavioral_patterns.get("emotional_expressiveness", "unknown"),
                    "emotional_balance": behavioral_patterns.get("emotional_balance", "unknown")
                }
            
            # 结构模式
            vector_result = analysis_results.get("vector_result", {})
            if vector_result.get("success"):
                vector_stats = vector_result.get("vector_statistics", {})
                indicators["structural_patterns"] = {
                    "concept_diversity": "高" if vector_stats.get("total_vectors", 0) > 10 else "中等",
                    "semantic_density": "高" if vector_stats.get("vector_density", 0) > 1.0 else "低"
                }
        
        except Exception as e:
            indicators["error"] = str(e)
        
        return indicators
    
    def _classify_writing_style(self, style_scores: Dict[str, float],
                              behavioral_indicators: Dict[str, Any]) -> Dict[str, Any]:
        """风格分类"""
        classification = {
            "primary_style": "unknown",
            "secondary_styles": [],
            "style_strength": 0.0,
            "style_characteristics": []
        }
        
        try:
            # 基于分数确定主要风格
            max_score = 0
            primary_dimension = ""
            
            for dimension, score in style_scores.items():
                if score > max_score:
                    max_score = score
                    primary_dimension = dimension
            
            # 风格映射
            style_mapping = {
                "conceptual_organization": "系统性思维型",
                "semantic_coherence": "逻辑连贯型",
                "creative_association": "创新联想型",
                "emotional_expression": "情感表达型",
                "cognitive_complexity": "复杂思维型",
                "thematic_focus": "专注聚焦型"
            }
            
            classification["primary_style"] = style_mapping.get(primary_dimension, "综合型")
            classification["style_strength"] = max_score
            
            # 次要风格（分数>3.5的其他维度）
            secondary_styles = []
            for dimension, score in style_scores.items():
                if dimension != primary_dimension and score > 3.5:
                    secondary_styles.append(style_mapping.get(dimension, dimension))
            
            classification["secondary_styles"] = secondary_styles
            
            # 风格特征
            characteristics = []
            if style_scores.get("conceptual_organization", 0) > 4.0:
                characteristics.append("概念组织能力强")
            if style_scores.get("creative_association", 0) > 4.0:
                characteristics.append("富有创新性")
            if style_scores.get("emotional_expression", 0) > 4.0:
                characteristics.append("情感表达丰富")
            if style_scores.get("semantic_coherence", 0) > 4.0:
                characteristics.append("逻辑性强")
            
            classification["style_characteristics"] = characteristics
        
        except Exception as e:
            classification["error"] = str(e)
        
        return classification
    
    def _calculate_comparative_metrics(self, feature_vector: List[float],
                                     style_scores: Dict[str, float]) -> Dict[str, Any]:
        """计算比较指标"""
        metrics = {
            "feature_vector_norm": 0.0,
            "style_score_average": 0.0,
            "style_score_variance": 0.0,
            "distinctiveness_index": 0.0,
            "complexity_index": 0.0
        }
        
        try:
            # 特征向量范数
            if feature_vector:
                metrics["feature_vector_norm"] = float(np.linalg.norm(feature_vector))
            
            # 风格分数统计
            if style_scores:
                scores = list(style_scores.values())
                metrics["style_score_average"] = float(np.mean(scores))
                metrics["style_score_variance"] = float(np.var(scores))
                
                # 独特性指数（基于分数方差）
                metrics["distinctiveness_index"] = min(1.0, metrics["style_score_variance"] / 2.0)
                
                # 复杂度指数（基于高分维度数量）
                high_score_count = sum(1 for score in scores if score > 4.0)
                metrics["complexity_index"] = high_score_count / len(scores)
        
        except Exception as e:
            metrics["error"] = str(e)
        
        return metrics
    
    def _generate_profile_summary(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成画像摘要"""
        summary = {
            "profile_type": "unknown",
            "key_strengths": [],
            "potential_improvements": [],
            "style_description": "",
            "uniqueness_score": 0.0
        }
        
        try:
            style_classification = profile.get("style_classification", {})
            style_scores = profile.get("style_scores", {})
            comparative_metrics = profile.get("comparative_metrics", {})
            
            # 画像类型
            summary["profile_type"] = style_classification.get("primary_style", "综合型")
            
            # 关键优势（分数>4.0的维度）
            strengths = []
            for dimension, score in style_scores.items():
                if score > 4.0:
                    strengths.append(self.style_dimensions.get(dimension, dimension))
            summary["key_strengths"] = strengths
            
            # 潜在改进（分数<3.0的维度）
            improvements = []
            for dimension, score in style_scores.items():
                if score < 3.0:
                    improvements.append(self.style_dimensions.get(dimension, dimension))
            summary["potential_improvements"] = improvements
            
            # 风格描述
            primary_style = style_classification.get("primary_style", "")
            characteristics = style_classification.get("style_characteristics", [])
            summary["style_description"] = f"{primary_style}，特点：{', '.join(characteristics)}"
            
            # 独特性分数
            summary["uniqueness_score"] = comparative_metrics.get("distinctiveness_index", 0.0)
        
        except Exception as e:
            summary["error"] = str(e)
        
        return summary
    
    def _encode_categorical(self, category: str) -> float:
        """编码分类变量"""
        encoding_map = {
            "紧密": 1.0,
            "适中": 2.0,
            "分散": 3.0,
            "unknown": 2.0
        }
        return encoding_map.get(category, 2.0)
    
    def _calculate_emotion_ratio(self, emotional_dist: Dict[str, Any], emotion_type: str) -> float:
        """计算情感比例"""
        try:
            count_key = f"{emotion_type}_count"
            emotion_count = emotional_dist.get(count_key, 0)
            total_count = (emotional_dist.get("positive_count", 0) + 
                          emotional_dist.get("negative_count", 0) + 
                          emotional_dist.get("neutral_count", 0))
            
            return emotion_count / total_count if total_count > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_emotional_balance(self, emotional_dist: Dict[str, Any]) -> float:
        """计算情感平衡度"""
        try:
            pos_count = emotional_dist.get("positive_count", 0)
            neg_count = emotional_dist.get("negative_count", 0)
            
            if pos_count + neg_count == 0:
                return 1.0  # 完全中性
            
            # 平衡度 = 较小值 / 较大值
            return min(pos_count, neg_count) / max(pos_count, neg_count) if max(pos_count, neg_count) > 0 else 0.0
        except:
            return 0.5
    
    def _extract_llm_features(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """提取LLM特征"""
        llm_features = {
            "cluster_coherence": 3.0,
            "novelty_creativity": 3.0,
            "emotional_sophistication": 3.0
        }
        
        try:
            # 从聚类分析中提取LLM评估
            clustering_analysis = analysis_results.get("clustering_analysis", {})
            llm_interpretation = clustering_analysis.get("llm_interpretation", {})
            
            if "overall_assessment" in llm_interpretation:
                assessment = llm_interpretation["overall_assessment"]
                llm_features["cluster_coherence"] = assessment.get("thematic_clarity", 3.0)
            
            # 从创新度评估中提取
            novelty_assessment = analysis_results.get("novelty_assessment", {})
            llm_assessments = novelty_assessment.get("llm_assessments", {})
            
            if "overall_creativity" in llm_assessments:
                creativity = llm_assessments["overall_creativity"]
                llm_features["novelty_creativity"] = creativity.get("creative_density", 3.0)
            
            # 从情感分析中提取
            emotional_analysis = analysis_results.get("emotional_analysis", {})
            llm_analysis = emotional_analysis.get("llm_analysis", {})
            
            if "emotional_patterns" in llm_analysis:
                patterns = llm_analysis["emotional_patterns"]
                llm_features["emotional_sophistication"] = patterns.get("emotional_sophistication", 3.0)
        
        except Exception as e:
            pass  # 使用默认值
        
        return llm_features
    
    def _generate_profile_id(self) -> str:
        """生成画像ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"semantic_profile_{timestamp}"
    
    def save_profile(self, profile: Dict[str, Any], filename: str = None) -> str:
        """保存语义风格画像"""
        if not filename:
            profile_id = profile.get("profile_id", "unknown")
            filename = f"{profile_id}.json"
        
        filepath = os.path.join(self.storage_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
            return filepath
        except Exception as e:
            return f"保存失败: {str(e)}"
    
    def load_profile(self, filename: str) -> Dict[str, Any]:
        """加载语义风格画像"""
        filepath = os.path.join(self.storage_path, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"加载失败: {str(e)}"}

    def compare_profiles(self, profile1: Dict[str, Any], profile2: Dict[str, Any]) -> Dict[str, Any]:
        """比较两个语义风格画像"""
        comparison = {
            "comparison_time": datetime.now().isoformat(),
            "profile1_name": profile1.get("document_name", "文档1"),
            "profile2_name": profile2.get("document_name", "文档2"),
            "similarity_score": 0.0,
            "dimension_differences": {},
            "style_compatibility": "unknown",
            "comparison_summary": {}
        }

        try:
            # 比较特征向量
            vector1 = profile1.get("feature_vector", [])
            vector2 = profile2.get("feature_vector", [])

            if vector1 and vector2 and len(vector1) == len(vector2):
                # 计算余弦相似度
                from sklearn.metrics.pairwise import cosine_similarity
                similarity = cosine_similarity([vector1], [vector2])[0][0]
                comparison["similarity_score"] = float(similarity)

            # 比较风格分数
            scores1 = profile1.get("style_scores", {})
            scores2 = profile2.get("style_scores", {})

            dimension_diffs = {}
            for dimension in self.style_dimensions:
                score1 = scores1.get(dimension, 3.0)
                score2 = scores2.get(dimension, 3.0)
                dimension_diffs[dimension] = {
                    "profile1_score": score1,
                    "profile2_score": score2,
                    "difference": abs(score1 - score2),
                    "similarity": 1 - (abs(score1 - score2) / 4.0)  # 标准化到0-1
                }

            comparison["dimension_differences"] = dimension_diffs

            # 风格兼容性
            avg_dimension_similarity = np.mean([d["similarity"] for d in dimension_diffs.values()])
            if avg_dimension_similarity > 0.8:
                comparison["style_compatibility"] = "高度兼容"
            elif avg_dimension_similarity > 0.6:
                comparison["style_compatibility"] = "较为兼容"
            elif avg_dimension_similarity > 0.4:
                comparison["style_compatibility"] = "部分兼容"
            else:
                comparison["style_compatibility"] = "差异较大"

            # 生成比较摘要
            comparison["comparison_summary"] = self._generate_comparison_summary(comparison)

        except Exception as e:
            comparison["error"] = str(e)

        return comparison

    def _generate_comparison_summary(self, comparison: Dict[str, Any]) -> Dict[str, Any]:
        """生成比较摘要"""
        summary = {
            "overall_similarity": comparison.get("similarity_score", 0.0),
            "most_similar_dimensions": [],
            "most_different_dimensions": [],
            "compatibility_assessment": comparison.get("style_compatibility", "unknown")
        }

        try:
            dimension_diffs = comparison.get("dimension_differences", {})

            # 找出最相似和最不同的维度
            similarities = [(dim, data["similarity"]) for dim, data in dimension_diffs.items()]
            similarities.sort(key=lambda x: x[1], reverse=True)

            summary["most_similar_dimensions"] = [dim for dim, sim in similarities[:2]]
            summary["most_different_dimensions"] = [dim for dim, sim in similarities[-2:]]

        except Exception as e:
            summary["error"] = str(e)

        return summary
