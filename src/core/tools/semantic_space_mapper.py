#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Space Mapper - 核心模块

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

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Install with: pip install sentence-transformers")

try:
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available for advanced vector operations")


class SemanticSpaceMapper:
    """语义空间映射器 - 将语义单元转化为向量表示"""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-mpnet-base-v2", 
                 cache_dir: str = "src/core/knowledge_base/semantic_vectors"):
        """
        初始化语义空间映射器
        
        Args:
            model_name: Sentence-BERT模型名称
            cache_dir: 向量缓存目录
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # 初始化Sentence-BERT模型
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print(f"🔄 正在加载Sentence-BERT模型: {model_name}")

                # 尝试使用镜像源
                os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

                # 尝试加载模型，如果失败则使用备用方案
                try:
                    self.sentence_model = SentenceTransformer(model_name)
                    self.model_available = True
                    print("✅ Sentence-BERT模型加载成功")
                except Exception as e1:
                    print(f"⚠️ 主模型加载失败，尝试备用模型: {str(e1)}")
                    try:
                        # 尝试使用更简单的模型
                        backup_model = "all-MiniLM-L6-v2"
                        self.sentence_model = SentenceTransformer(backup_model)
                        self.model_available = True
                        print(f"✅ 备用模型加载成功: {backup_model}")
                    except Exception as e2:
                        print(f"❌ 备用模型也加载失败: {str(e2)}")
                        print("💡 使用模拟向量模式")
                        self.sentence_model = None
                        self.model_available = False
                        self.use_mock_vectors = True

            except Exception as e:
                print(f"❌ Sentence-BERT初始化失败: {str(e)}")
                self.sentence_model = None
                self.model_available = False
                self.use_mock_vectors = True
        else:
            self.sentence_model = None
            self.model_available = False
            self.use_mock_vectors = True
        
        # 向量缓存
        self.vector_cache = {}
        self.load_vector_cache()

        # 模拟向量模式标志
        if not hasattr(self, 'use_mock_vectors'):
            self.use_mock_vectors = False
    
    def load_vector_cache(self):
        """加载向量缓存"""
        cache_file = os.path.join(self.cache_dir, "vector_cache.json")
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # 将列表转换回numpy数组
                    for key, value in cache_data.items():
                        if isinstance(value, list):
                            self.vector_cache[key] = np.array(value)
                print(f"✅ 加载向量缓存: {len(self.vector_cache)} 个向量")
        except Exception as e:
            print(f"⚠️ 向量缓存加载失败: {str(e)}")
    
    def save_vector_cache(self):
        """保存向量缓存"""
        cache_file = os.path.join(self.cache_dir, "vector_cache.json")
        try:
            # 将numpy数组转换为列表以便JSON序列化
            cache_data = {}
            for key, value in self.vector_cache.items():
                if isinstance(value, np.ndarray):
                    cache_data[key] = value.tolist()
                else:
                    cache_data[key] = value
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 保存向量缓存: {len(cache_data)} 个向量")
        except Exception as e:
            print(f"⚠️ 向量缓存保存失败: {str(e)}")
    
    def encode_semantic_units(self, semantic_units: Dict[str, Any]) -> Dict[str, Any]:
        """
        将语义单元编码为向量

        Args:
            semantic_units: 语义单元识别结果

        Returns:
            向量化结果
        """
        if not self.model_available and not self.use_mock_vectors:
            return {"error": "Sentence-BERT model not available and mock vectors disabled"}
        
        result = {
            "encoding_time": datetime.now().isoformat(),
            "model_name": self.model_name,
            "concept_vectors": {},
            "entity_vectors": {},
            "phrase_vectors": {},
            "adjective_vectors": {},
            "verb_vectors": {},
            "vector_statistics": {},
            "success": False
        }
        
        try:
            print("🔄 正在将语义单元编码为向量...")
            
            # 编码概念
            concepts = semantic_units.get("concepts", [])
            if concepts:
                concept_texts = [c.get("text", "") for c in concepts]
                concept_vectors = self._encode_texts_with_cache(concept_texts)
                result["concept_vectors"] = self._create_vector_dict(concepts, concept_vectors, "text")
            
            # 编码实体
            entities = semantic_units.get("named_entities", [])
            if entities:
                entity_texts = [e.get("text", "") for e in entities]
                entity_vectors = self._encode_texts_with_cache(entity_texts)
                result["entity_vectors"] = self._create_vector_dict(entities, entity_vectors, "text")
            
            # 编码关键短语
            phrases = semantic_units.get("key_phrases", [])
            if phrases:
                phrase_texts = [p.get("text", "") for p in phrases]
                phrase_vectors = self._encode_texts_with_cache(phrase_texts)
                result["phrase_vectors"] = self._create_vector_dict(phrases, phrase_vectors, "text")
            
            # 编码形容词
            adjectives = semantic_units.get("key_adjectives", [])
            if adjectives:
                adj_texts = [a.get("text", "") for a in adjectives]
                adj_vectors = self._encode_texts_with_cache(adj_texts)
                result["adjective_vectors"] = self._create_vector_dict(adjectives, adj_vectors, "text")
            
            # 编码动词
            verbs = semantic_units.get("key_verbs", [])
            if verbs:
                verb_texts = [v.get("text", "") for v in verbs]
                verb_vectors = self._encode_texts_with_cache(verb_texts)
                result["verb_vectors"] = self._create_vector_dict(verbs, verb_vectors, "text")
            
            # 计算向量统计信息
            result["vector_statistics"] = self._calculate_vector_statistics(result)
            result["success"] = True
            
            # 保存缓存
            self.save_vector_cache()
            
            print("✅ 语义单元向量编码完成")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ 语义单元向量编码失败: {str(e)}")
        
        return result
    
    def _encode_texts_with_cache(self, texts: List[str]) -> List[np.ndarray]:
        """使用缓存编码文本"""
        vectors = []
        texts_to_encode = []
        cache_indices = []
        
        # 检查缓存
        for i, text in enumerate(texts):
            if text in self.vector_cache:
                vectors.append(self.vector_cache[text])
            else:
                vectors.append(None)
                texts_to_encode.append(text)
                cache_indices.append(i)
        
        # 编码未缓存的文本
        if texts_to_encode:
            try:
                if self.model_available and self.sentence_model:
                    new_vectors = self.sentence_model.encode(texts_to_encode)
                else:
                    # 使用模拟向量
                    print("💡 使用模拟向量进行编码")
                    new_vectors = self._generate_mock_vectors(texts_to_encode)

                # 更新缓存和结果
                for i, (text, vector) in enumerate(zip(texts_to_encode, new_vectors)):
                    self.vector_cache[text] = vector
                    vectors[cache_indices[i]] = vector

            except Exception as e:
                print(f"⚠️ 文本编码失败: {str(e)}")
                # 使用模拟向量作为fallback
                new_vectors = self._generate_mock_vectors(texts_to_encode)
                for i, (text, vector) in enumerate(zip(texts_to_encode, new_vectors)):
                    self.vector_cache[text] = vector
                    vectors[cache_indices[i]] = vector
        
        return [v for v in vectors if v is not None]

    def _generate_mock_vectors(self, texts: List[str]) -> List[np.ndarray]:
        """生成模拟向量用于测试"""
        import hashlib

        vectors = []
        vector_dim = 384  # 使用较小的维度

        for text in texts:
            # 基于文本内容生成确定性的向量
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

            # 将哈希值转换为向量
            vector = np.zeros(vector_dim)
            for i, char in enumerate(text_hash[:vector_dim//16]):
                idx = i * 16
                if idx < vector_dim:
                    vector[idx] = ord(char) / 255.0  # 归一化到0-1

            # 添加一些基于文本长度的特征
            length_feature = min(len(text) / 100.0, 1.0)
            vector[0] = length_feature

            # 添加一些随机性但保持确定性
            np.random.seed(hash(text) % (2**32))
            noise = np.random.normal(0, 0.1, vector_dim)
            vector = vector + noise

            # 归一化向量
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm

            vectors.append(vector)

        return vectors
    
    def _create_vector_dict(self, items: List[Dict], vectors: List[np.ndarray], text_key: str) -> Dict[str, Any]:
        """创建向量字典"""
        vector_dict = {}
        
        for item, vector in zip(items, vectors):
            text = item.get(text_key, "")
            if text and vector is not None:
                vector_dict[text] = {
                    "vector": vector.tolist(),  # 转换为列表以便JSON序列化
                    "metadata": {k: v for k, v in item.items() if k != text_key},
                    "vector_norm": float(np.linalg.norm(vector)),
                    "vector_dim": len(vector)
                }
        
        return vector_dict
    
    def _calculate_vector_statistics(self, vector_result: Dict[str, Any]) -> Dict[str, Any]:
        """计算向量统计信息"""
        stats = {
            "total_vectors": 0,
            "vector_dimensions": 0,
            "category_counts": {},
            "average_norms": {},
            "vector_density": 0.0
        }
        
        try:
            all_vectors = []
            
            # 收集所有向量
            for category in ["concept_vectors", "entity_vectors", "phrase_vectors", 
                           "adjective_vectors", "verb_vectors"]:
                category_data = vector_result.get(category, {})
                category_vectors = []
                
                for item_name, item_data in category_data.items():
                    if "vector" in item_data:
                        vector = np.array(item_data["vector"])
                        all_vectors.append(vector)
                        category_vectors.append(vector)
                
                stats["category_counts"][category] = len(category_vectors)
                
                if category_vectors:
                    norms = [np.linalg.norm(v) for v in category_vectors]
                    stats["average_norms"][category] = float(np.mean(norms))
            
            # 整体统计
            if all_vectors:
                stats["total_vectors"] = len(all_vectors)
                stats["vector_dimensions"] = len(all_vectors[0])
                
                # 计算向量密度（平均向量间距离）
                if len(all_vectors) > 1 and SKLEARN_AVAILABLE:
                    distances = euclidean_distances(all_vectors)
                    # 排除对角线（自身距离为0）
                    mask = np.ones(distances.shape, dtype=bool)
                    np.fill_diagonal(mask, False)
                    stats["vector_density"] = float(np.mean(distances[mask]))
        
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
    
    def calculate_semantic_similarities(self, vector_result: Dict[str, Any], 
                                      similarity_type: str = "cosine") -> Dict[str, Any]:
        """
        计算语义相似度
        
        Args:
            vector_result: 向量化结果
            similarity_type: 相似度类型 ("cosine", "euclidean")
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not available for similarity calculation"}
        
        similarity_result = {
            "calculation_time": datetime.now().isoformat(),
            "similarity_type": similarity_type,
            "concept_similarities": {},
            "cross_category_similarities": {},
            "similarity_statistics": {},
            "success": False
        }
        
        try:
            print(f"🔄 正在计算{similarity_type}相似度...")
            
            # 提取概念向量
            concept_vectors = vector_result.get("concept_vectors", {})
            if len(concept_vectors) > 1:
                concept_names = list(concept_vectors.keys())
                concept_matrix = np.array([concept_vectors[name]["vector"] for name in concept_names])
                
                # 计算概念间相似度
                if similarity_type == "cosine":
                    similarities = cosine_similarity(concept_matrix)
                elif similarity_type == "euclidean":
                    distances = euclidean_distances(concept_matrix)
                    # 转换为相似度（距离越小，相似度越高）
                    max_distance = np.max(distances)
                    similarities = 1 - (distances / max_distance) if max_distance > 0 else distances
                
                # 构建相似度字典
                concept_sim_dict = {}
                for i, name1 in enumerate(concept_names):
                    concept_sim_dict[name1] = {}
                    for j, name2 in enumerate(concept_names):
                        if i != j:  # 排除自身
                            concept_sim_dict[name1][name2] = float(similarities[i][j])
                
                similarity_result["concept_similarities"] = concept_sim_dict
            
            # 计算跨类别相似度
            cross_similarities = self._calculate_cross_category_similarities(
                vector_result, similarity_type
            )
            similarity_result["cross_category_similarities"] = cross_similarities
            
            # 计算相似度统计
            similarity_result["similarity_statistics"] = self._calculate_similarity_statistics(
                similarity_result
            )
            
            similarity_result["success"] = True
            print("✅ 语义相似度计算完成")
            
        except Exception as e:
            similarity_result["error"] = str(e)
            print(f"❌ 语义相似度计算失败: {str(e)}")
        
        return similarity_result
    
    def _calculate_cross_category_similarities(self, vector_result: Dict[str, Any], 
                                             similarity_type: str) -> Dict[str, Any]:
        """计算跨类别相似度"""
        cross_similarities = {}
        
        categories = ["concept_vectors", "entity_vectors", "phrase_vectors"]
        
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                vectors1 = vector_result.get(cat1, {})
                vectors2 = vector_result.get(cat2, {})
                
                if vectors1 and vectors2:
                    # 计算类别间的平均相似度
                    similarities = []
                    
                    for name1, data1 in vectors1.items():
                        for name2, data2 in vectors2.items():
                            vec1 = np.array(data1["vector"]).reshape(1, -1)
                            vec2 = np.array(data2["vector"]).reshape(1, -1)
                            
                            if similarity_type == "cosine":
                                sim = cosine_similarity(vec1, vec2)[0][0]
                            elif similarity_type == "euclidean":
                                dist = euclidean_distances(vec1, vec2)[0][0]
                                sim = 1 / (1 + dist)  # 转换为相似度
                            
                            similarities.append(sim)
                    
                    if similarities:
                        cross_similarities[f"{cat1}_vs_{cat2}"] = {
                            "average_similarity": float(np.mean(similarities)),
                            "max_similarity": float(np.max(similarities)),
                            "min_similarity": float(np.min(similarities)),
                            "std_similarity": float(np.std(similarities))
                        }
        
        return cross_similarities
    
    def _calculate_similarity_statistics(self, similarity_result: Dict[str, Any]) -> Dict[str, Any]:
        """计算相似度统计信息"""
        stats = {
            "concept_similarity_stats": {},
            "cross_category_stats": {},
            "overall_stats": {}
        }
        
        try:
            # 概念相似度统计
            concept_similarities = similarity_result.get("concept_similarities", {})
            if concept_similarities:
                all_concept_sims = []
                for name1, sims in concept_similarities.items():
                    all_concept_sims.extend(sims.values())
                
                if all_concept_sims:
                    stats["concept_similarity_stats"] = {
                        "average": float(np.mean(all_concept_sims)),
                        "max": float(np.max(all_concept_sims)),
                        "min": float(np.min(all_concept_sims)),
                        "std": float(np.std(all_concept_sims))
                    }
            
            # 跨类别相似度统计
            cross_similarities = similarity_result.get("cross_category_similarities", {})
            if cross_similarities:
                avg_cross_sims = [data["average_similarity"] for data in cross_similarities.values()]
                if avg_cross_sims:
                    stats["cross_category_stats"] = {
                        "average": float(np.mean(avg_cross_sims)),
                        "max": float(np.max(avg_cross_sims)),
                        "min": float(np.min(avg_cross_sims))
                    }
            
            # 整体统计
            all_similarities = []
            if concept_similarities:
                for sims in concept_similarities.values():
                    all_similarities.extend(sims.values())
            if cross_similarities:
                for data in cross_similarities.values():
                    all_similarities.append(data["average_similarity"])
            
            if all_similarities:
                stats["overall_stats"] = {
                    "total_comparisons": len(all_similarities),
                    "average_similarity": float(np.mean(all_similarities)),
                    "similarity_variance": float(np.var(all_similarities))
                }
        
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
    
    def find_semantic_clusters(self, vector_result: Dict[str, Any], 
                             n_clusters: int = None) -> Dict[str, Any]:
        """发现语义聚类"""
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not available for clustering"}
        
        from sklearn.cluster import KMeans
        
        cluster_result = {
            "clustering_time": datetime.now().isoformat(),
            "n_clusters": n_clusters,
            "clusters": {},
            "cluster_statistics": {},
            "success": False
        }
        
        try:
            # 收集所有概念向量
            concept_vectors = vector_result.get("concept_vectors", {})
            if len(concept_vectors) < 2:
                return {"error": "Not enough concepts for clustering"}
            
            concept_names = list(concept_vectors.keys())
            concept_matrix = np.array([concept_vectors[name]["vector"] for name in concept_names])
            
            # 自动确定聚类数量
            if n_clusters is None:
                n_clusters = min(max(2, len(concept_names) // 3), 5)
            
            # 执行K-means聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(concept_matrix)
            
            # 组织聚类结果
            clusters = {}
            for i, (name, label) in enumerate(zip(concept_names, cluster_labels)):
                cluster_id = f"cluster_{label}"
                if cluster_id not in clusters:
                    clusters[cluster_id] = {
                        "concepts": [],
                        "center": kmeans.cluster_centers_[label].tolist(),
                        "size": 0
                    }
                
                clusters[cluster_id]["concepts"].append({
                    "name": name,
                    "metadata": concept_vectors[name]["metadata"],
                    "distance_to_center": float(np.linalg.norm(
                        concept_matrix[i] - kmeans.cluster_centers_[label]
                    ))
                })
                clusters[cluster_id]["size"] += 1
            
            cluster_result["clusters"] = clusters
            cluster_result["n_clusters"] = n_clusters
            
            # 计算聚类统计
            cluster_result["cluster_statistics"] = self._calculate_cluster_statistics(
                clusters, kmeans
            )
            
            cluster_result["success"] = True
            print(f"✅ 语义聚类完成，发现 {n_clusters} 个聚类")
            
        except Exception as e:
            cluster_result["error"] = str(e)
            print(f"❌ 语义聚类失败: {str(e)}")
        
        return cluster_result
    
    def _calculate_cluster_statistics(self, clusters: Dict[str, Any], kmeans) -> Dict[str, Any]:
        """计算聚类统计信息"""
        stats = {
            "total_clusters": len(clusters),
            "cluster_sizes": {},
            "average_cluster_size": 0,
            "inertia": float(kmeans.inertia_),
            "silhouette_score": None
        }
        
        try:
            # 聚类大小统计
            sizes = []
            for cluster_id, cluster_data in clusters.items():
                size = cluster_data["size"]
                stats["cluster_sizes"][cluster_id] = size
                sizes.append(size)
            
            if sizes:
                stats["average_cluster_size"] = float(np.mean(sizes))
            
            # 计算轮廓系数（如果可能）
            try:
                from sklearn.metrics import silhouette_score
                # 这里需要原始数据和标签，暂时跳过
                pass
            except ImportError:
                pass
        
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
