#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature Fusion Processor - 核心模块

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
import os
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime
from collections import defaultdict

try:
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
    from sklearn.decomposition import PCA, TruncatedSVD
    from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Feature processing will be limited.")


class FeatureFusionProcessor:
    """特征融合处理器"""
    
    def __init__(self, storage_path: str = "src/core/knowledge_base/feature_models"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # 特征权重配置
        self.feature_weights = {
            "quantitative": {
                "lexical": 0.3,
                "syntactic": 0.25,
                "punctuation": 0.15
            },
            "llm": {
                "vocabulary_style": 0.2,
                "sentence_structure": 0.2,
                "tone_emotion": 0.15,
                "formality": 0.15,
                "professionalism": 0.1,
                "creativity": 0.1
            }
        }
        
        # 缓存处理器
        self.scalers = {}
        self.pca_models = {}
        self.feature_selectors = {}
    
    def fuse_features(self, quantitative_features: Dict[str, Any], 
                     llm_features: Dict[str, Any], 
                     fusion_method: str = "weighted_concat") -> Dict[str, Any]:
        """
        融合量化特征和LLM特征
        
        Args:
            quantitative_features: 量化特征
            llm_features: LLM特征
            fusion_method: 融合方法 ("weighted_concat", "hierarchical", "attention")
        """
        result = {
            "fusion_time": datetime.now().isoformat(),
            "fusion_method": fusion_method,
            "quantitative_vector": [],
            "llm_vector": [],
            "fused_vector": [],
            "feature_names": [],
            "fusion_weights": {},
            "fusion_summary": {}
        }
        
        try:
            # 提取量化特征向量
            quant_vector, quant_names = self._extract_quantitative_vector(quantitative_features)
            result["quantitative_vector"] = quant_vector
            
            # 提取LLM特征向量
            llm_vector, llm_names = self._extract_llm_vector(llm_features)
            result["llm_vector"] = llm_vector
            
            # 执行特征融合
            if fusion_method == "weighted_concat":
                fused_vector, feature_names, weights = self._weighted_concatenation(
                    quant_vector, llm_vector, quant_names, llm_names
                )
            elif fusion_method == "hierarchical":
                fused_vector, feature_names, weights = self._hierarchical_fusion(
                    quant_vector, llm_vector, quant_names, llm_names
                )
            elif fusion_method == "attention":
                fused_vector, feature_names, weights = self._attention_fusion(
                    quant_vector, llm_vector, quant_names, llm_names
                )
            else:
                raise ValueError(f"Unknown fusion method: {fusion_method}")
            
            result["fused_vector"] = fused_vector
            result["feature_names"] = feature_names
            result["fusion_weights"] = weights
            result["fusion_summary"] = self._generate_fusion_summary(
                quant_vector, llm_vector, fused_vector
            )
            result["success"] = True
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    def _extract_quantitative_vector(self, features: Dict[str, Any]) -> Tuple[List[float], List[str]]:
        """从量化特征中提取向量"""
        vector = []
        names = []
        
        # 词汇特征
        lexical = features.get("lexical_features", {})
        if lexical:
            vector.extend([
                lexical.get("ttr", 0),
                lexical.get("avg_word_length", 0),
                lexical.get("formal_word_density", 0),
                lexical.get("informal_word_density", 0),
                lexical.get("function_word_density", 0)
            ])
            names.extend([
                "ttr", "avg_word_length", "formal_density", 
                "informal_density", "function_word_density"
            ])
        
        # 句法特征
        syntactic = features.get("syntactic_features", {})
        if syntactic:
            vector.extend([
                syntactic.get("avg_sentence_length", 0),
                syntactic.get("sentence_length_std", 0),
                syntactic.get("short_sentence_ratio", 0),
                syntactic.get("long_sentence_ratio", 0),
                syntactic.get("compound_sentence_ratio", 0)
            ])
            names.extend([
                "avg_sentence_length", "sentence_length_std", "short_sentence_ratio",
                "long_sentence_ratio", "compound_sentence_ratio"
            ])
        
        # 标点特征
        punctuation = features.get("punctuation_features", {})
        if punctuation:
            vector.extend([
                punctuation.get("punctuation_density", 0),
                punctuation.get("question_mark_count", 0),
                punctuation.get("exclamation_mark_count", 0)
            ])
            names.extend([
                "punctuation_density", "question_marks", "exclamation_marks"
            ])
        
        return vector, names
    
    def _extract_llm_vector(self, features: Dict[str, Any]) -> Tuple[List[float], List[str]]:
        """从LLM特征中提取向量"""
        vector = []
        names = []
        
        # 从评估结果中提取分数
        evaluations = features.get("evaluations", {})
        if evaluations:
            for dimension, eval_data in evaluations.items():
                if isinstance(eval_data, dict) and "score" in eval_data:
                    vector.append(eval_data["score"])
                    names.append(f"llm_{dimension}")
        
        # 从整体风格档案中提取特征
        profile = features.get("overall_style_profile", {})
        if profile:
            vector.extend([
                profile.get("average_score", 3.0),
                profile.get("score_std", 0.0)
            ])
            names.extend(["llm_avg_score", "llm_score_std"])
        
        return vector, names
    
    def _weighted_concatenation(self, quant_vector: List[float], llm_vector: List[float],
                              quant_names: List[str], llm_names: List[str]) -> Tuple[List[float], List[str], Dict]:
        """加权拼接融合"""
        # 标准化特征
        quant_normalized = self._normalize_vector(quant_vector, "quantitative")
        llm_normalized = self._normalize_vector(llm_vector, "llm")
        
        # 应用权重
        quant_weighted = [x * 0.6 for x in quant_normalized]  # 量化特征权重60%
        llm_weighted = [x * 0.4 for x in llm_normalized]      # LLM特征权重40%
        
        # 拼接
        fused_vector = quant_weighted + llm_weighted
        feature_names = [f"quant_{name}" for name in quant_names] + [f"llm_{name}" for name in llm_names]
        
        weights = {
            "quantitative_weight": 0.6,
            "llm_weight": 0.4,
            "total_features": len(fused_vector)
        }
        
        return fused_vector, feature_names, weights
    
    def _hierarchical_fusion(self, quant_vector: List[float], llm_vector: List[float],
                           quant_names: List[str], llm_names: List[str]) -> Tuple[List[float], List[str], Dict]:
        """分层融合"""
        # 第一层：特征组内融合
        quant_groups = self._group_quantitative_features(quant_vector, quant_names)
        llm_groups = self._group_llm_features(llm_vector, llm_names)
        
        # 第二层：组间融合
        fused_vector = []
        feature_names = []
        
        # 融合量化特征组
        for group_name, group_features in quant_groups.items():
            group_mean = np.mean(group_features) if group_features else 0
            fused_vector.append(group_mean)
            feature_names.append(f"quant_group_{group_name}")
        
        # 融合LLM特征组
        for group_name, group_features in llm_groups.items():
            group_mean = np.mean(group_features) if group_features else 0
            fused_vector.append(group_mean)
            feature_names.append(f"llm_group_{group_name}")
        
        weights = {
            "fusion_type": "hierarchical",
            "quantitative_groups": len(quant_groups),
            "llm_groups": len(llm_groups)
        }
        
        return fused_vector, feature_names, weights
    
    def _attention_fusion(self, quant_vector: List[float], llm_vector: List[float],
                         quant_names: List[str], llm_names: List[str]) -> Tuple[List[float], List[str], Dict]:
        """注意力机制融合"""
        # 计算特征重要性权重
        all_features = quant_vector + llm_vector
        all_names = quant_names + llm_names
        
        # 简化的注意力权重计算（基于特征方差）
        if len(all_features) > 0:
            feature_variance = np.var(all_features) if len(all_features) > 1 else 1.0
            attention_weights = [abs(f) / (feature_variance + 1e-8) for f in all_features]
            
            # 归一化权重
            total_weight = sum(attention_weights)
            if total_weight > 0:
                attention_weights = [w / total_weight for w in attention_weights]
            else:
                attention_weights = [1.0 / len(all_features)] * len(all_features)
        else:
            attention_weights = []
        
        # 应用注意力权重
        fused_vector = [f * w for f, w in zip(all_features, attention_weights)]
        
        weights = {
            "fusion_type": "attention",
            "attention_weights": attention_weights,
            "max_attention": max(attention_weights) if attention_weights else 0,
            "min_attention": min(attention_weights) if attention_weights else 0
        }
        
        return fused_vector, all_names, weights
    
    def _normalize_vector(self, vector: List[float], feature_type: str) -> List[float]:
        """标准化特征向量"""
        if not vector:
            return vector
        
        if not SKLEARN_AVAILABLE:
            # 简单的min-max标准化
            min_val = min(vector)
            max_val = max(vector)
            if max_val > min_val:
                return [(x - min_val) / (max_val - min_val) for x in vector]
            else:
                return [0.0] * len(vector)
        
        # 使用sklearn标准化
        scaler_key = f"{feature_type}_scaler"
        if scaler_key not in self.scalers:
            self.scalers[scaler_key] = StandardScaler()
        
        vector_array = np.array(vector).reshape(-1, 1)
        normalized = self.scalers[scaler_key].fit_transform(vector_array)
        return normalized.flatten().tolist()
    
    def _group_quantitative_features(self, vector: List[float], names: List[str]) -> Dict[str, List[float]]:
        """分组量化特征"""
        groups = defaultdict(list)
        
        for i, name in enumerate(names):
            if i < len(vector):
                if any(keyword in name for keyword in ["ttr", "word_length", "density"]):
                    groups["lexical"].append(vector[i])
                elif any(keyword in name for keyword in ["sentence", "ratio"]):
                    groups["syntactic"].append(vector[i])
                elif any(keyword in name for keyword in ["punctuation", "mark"]):
                    groups["punctuation"].append(vector[i])
                else:
                    groups["other"].append(vector[i])
        
        return dict(groups)
    
    def _group_llm_features(self, vector: List[float], names: List[str]) -> Dict[str, List[float]]:
        """分组LLM特征"""
        groups = defaultdict(list)
        
        for i, name in enumerate(names):
            if i < len(vector):
                if any(keyword in name for keyword in ["vocabulary", "词汇"]):
                    groups["vocabulary"].append(vector[i])
                elif any(keyword in name for keyword in ["structure", "句式"]):
                    groups["structure"].append(vector[i])
                elif any(keyword in name for keyword in ["emotion", "tone", "情感"]):
                    groups["emotion"].append(vector[i])
                elif any(keyword in name for keyword in ["formal", "正式"]):
                    groups["formality"].append(vector[i])
                else:
                    groups["other"].append(vector[i])
        
        return dict(groups)
    
    def _generate_fusion_summary(self, quant_vector: List[float], 
                               llm_vector: List[float], 
                               fused_vector: List[float]) -> Dict[str, Any]:
        """生成融合摘要"""
        return {
            "quantitative_features_count": len(quant_vector),
            "llm_features_count": len(llm_vector),
            "fused_features_count": len(fused_vector),
            "quantitative_mean": np.mean(quant_vector) if quant_vector else 0,
            "llm_mean": np.mean(llm_vector) if llm_vector else 0,
            "fused_mean": np.mean(fused_vector) if fused_vector else 0,
            "fusion_ratio": len(fused_vector) / (len(quant_vector) + len(llm_vector)) if (len(quant_vector) + len(llm_vector)) > 0 else 0
        }
    
    def apply_dimensionality_reduction(self, feature_vector: List[float], 
                                     method: str = "pca", 
                                     target_dimensions: int = 10) -> Dict[str, Any]:
        """应用降维"""
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not available for dimensionality reduction"}
        
        if not feature_vector or len(feature_vector) <= target_dimensions:
            return {
                "reduced_vector": feature_vector,
                "original_dimensions": len(feature_vector),
                "target_dimensions": target_dimensions,
                "method": method,
                "reduction_applied": False
            }
        
        try:
            vector_array = np.array(feature_vector).reshape(1, -1)
            
            if method == "pca":
                reducer = PCA(n_components=min(target_dimensions, len(feature_vector)))
                reduced_array = reducer.fit_transform(vector_array)
                explained_variance = reducer.explained_variance_ratio_.tolist()
            elif method == "svd":
                reducer = TruncatedSVD(n_components=min(target_dimensions, len(feature_vector)))
                reduced_array = reducer.fit_transform(vector_array)
                explained_variance = reducer.explained_variance_ratio_.tolist()
            else:
                raise ValueError(f"Unknown reduction method: {method}")
            
            return {
                "reduced_vector": reduced_array.flatten().tolist(),
                "original_dimensions": len(feature_vector),
                "target_dimensions": target_dimensions,
                "actual_dimensions": reduced_array.shape[1],
                "method": method,
                "explained_variance": explained_variance,
                "total_variance_explained": sum(explained_variance),
                "reduction_applied": True,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "reduction_applied": False
            }
    
    def calculate_feature_importance(self, features: List[List[float]], 
                                   labels: List[str] = None) -> Dict[str, Any]:
        """计算特征重要性"""
        if not SKLEARN_AVAILABLE or not features:
            return {"error": "Cannot calculate feature importance"}
        
        try:
            features_array = np.array(features)
            
            if labels is None:
                # 无监督特征重要性（基于方差）
                variances = np.var(features_array, axis=0)
                importance_scores = variances / np.sum(variances) if np.sum(variances) > 0 else variances
            else:
                # 有监督特征重要性
                selector = SelectKBest(score_func=f_classif, k='all')
                selector.fit(features_array, labels)
                importance_scores = selector.scores_
                importance_scores = importance_scores / np.sum(importance_scores) if np.sum(importance_scores) > 0 else importance_scores
            
            return {
                "importance_scores": importance_scores.tolist(),
                "top_features": np.argsort(importance_scores)[::-1].tolist(),
                "calculation_method": "supervised" if labels else "unsupervised",
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def save_fusion_model(self, fusion_result: Dict[str, Any], model_name: str) -> str:
        """保存融合模型"""
        try:
            filepath = os.path.join(self.storage_path, f"{model_name}_fusion_model.json")
            
            # 准备保存的数据
            save_data = {
                "model_name": model_name,
                "creation_time": datetime.now().isoformat(),
                "fusion_result": fusion_result,
                "feature_weights": self.feature_weights
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return filepath
            
        except Exception as e:
            return f"保存失败: {str(e)}"
    
    def load_fusion_model(self, model_name: str) -> Dict[str, Any]:
        """加载融合模型"""
        try:
            filepath = os.path.join(self.storage_path, f"{model_name}_fusion_model.json")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            return {"error": f"加载失败: {str(e)}"}
