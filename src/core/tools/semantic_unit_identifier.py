#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Unit Identifier - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import json
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


class SemanticUnitIdentifier:
    """语义单元识别器 - 讯飞大模型作为语义分析助手"""
    
    def __init__(self, llm_client=None):
        """
        初始化语义单元识别器
        
        Args:
            llm_client: 讯飞大模型客户端
        """
        self.llm_client = llm_client
        self.identification_templates = self._init_prompt_templates()
    
    def _init_prompt_templates(self) -> Dict[str, str]:
        """初始化提示词模板"""
        return {
            "comprehensive_analysis": """请对以下中文文本进行全面的语义单元识别，以JSON格式输出结果：

文本内容：
{text}

请按照以下结构输出分析结果：
{{
  "concepts": [
    {{"text": "概念名称", "role": "核心概念/相关概念", "importance": 1-5}},
    ...
  ],
  "named_entities": [
    {{"text": "实体名称", "type": "人名/地名/组织名/产品名/其他", "context": "出现语境"}},
    ...
  ],
  "key_adjectives": [
    {{"text": "形容词", "context": "修饰语境", "sentiment_intensity": 1-5, "sentiment_polarity": "积极/消极/中性"}},
    ...
  ],
  "key_verbs": [
    {{"text": "动词", "context": "使用语境", "action_type": "状态/动作/变化", "intensity": 1-5}},
    ...
  ],
  "key_phrases": [
    {{"text": "关键短语", "role": "技术术语/专业表达/特色用法", "domain": "所属领域"}},
    ...
  ],
  "semantic_relations": [
    {{"entity1": "概念1", "relation": "关系类型", "entity2": "概念2", "strength": 1-5}},
    ...
  ]
}}

要求：
1. 识别出最重要的5-10个核心概念
2. 提取所有命名实体并分类
3. 找出具有强烈情感色彩或修饰作用的形容词
4. 识别表达动作、状态变化的关键动词
5. 提取专业术语和特色表达
6. 分析概念间的语义关系

请确保输出格式严格符合JSON规范。""",

            "concept_extraction": """请从以下文本中提取核心概念和相关概念：

文本：{text}

请以JSON格式输出：
{{
  "core_concepts": [
    {{"concept": "概念名", "importance": 1-5, "category": "主题/方法/工具/理论"}},
    ...
  ],
  "related_concepts": [
    {{"concept": "概念名", "relation_to_core": "支撑/应用/对比/扩展", "importance": 1-5}},
    ...
  ],
  "concept_clusters": [
    {{"cluster_name": "概念群名称", "concepts": ["概念1", "概念2"], "theme": "主题描述"}},
    ...
  ]
}}""",

            "entity_recognition": """请识别以下文本中的命名实体：

文本：{text}

请以JSON格式输出：
{{
  "persons": [
    {{"name": "人名", "role": "角色/职位", "context": "出现语境"}},
    ...
  ],
  "organizations": [
    {{"name": "组织名", "type": "公司/机构/团体", "context": "出现语境"}},
    ...
  ],
  "locations": [
    {{"name": "地名", "type": "国家/城市/地区", "context": "出现语境"}},
    ...
  ],
  "products": [
    {{"name": "产品名", "category": "软件/硬件/服务", "context": "出现语境"}},
    ...
  ],
  "others": [
    {{"name": "其他实体", "type": "类型", "context": "出现语境"}},
    ...
  ]
}}""",

            "sentiment_analysis": """请分析以下文本中关键词汇的情感色彩：

文本：{text}

请以JSON格式输出：
{{
  "emotional_adjectives": [
    {{"word": "形容词", "sentiment": "积极/消极/中性", "intensity": 1-5, "context": "使用语境"}},
    ...
  ],
  "emotional_verbs": [
    {{"word": "动词", "sentiment": "积极/消极/中性", "intensity": 1-5, "context": "使用语境"}},
    ...
  ],
  "emotional_phrases": [
    {{"phrase": "短语", "sentiment": "积极/消极/中性", "intensity": 1-5, "context": "使用语境"}},
    ...
  ],
  "overall_sentiment": {{"polarity": "积极/消极/中性", "intensity": 1-5, "confidence": 1-5}}
}}""",

            "semantic_relations": """请分析以下文本中概念之间的语义关系：

文本：{text}

请以JSON格式输出：
{{
  "hierarchical_relations": [
    {{"parent": "上级概念", "child": "下级概念", "relation_type": "包含/属于"}},
    ...
  ],
  "associative_relations": [
    {{"concept1": "概念1", "concept2": "概念2", "relation_type": "相关/对比/因果", "strength": 1-5}},
    ...
  ],
  "temporal_relations": [
    {{"before": "前序概念", "after": "后续概念", "relation_type": "时间顺序/发展过程"}},
    ...
  ],
  "causal_relations": [
    {{"cause": "原因", "effect": "结果", "strength": 1-5}},
    ...
  ]
}}"""
        }
    
    def identify_semantic_units(self, text: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        识别文本中的语义单元
        
        Args:
            text: 输入文本
            analysis_type: 分析类型 ("comprehensive", "concept", "entity", "sentiment", "relation")
        
        Returns:
            语义单元识别结果
        """
        if not self.llm_client:
            return {"error": "LLM client not available"}
        
        result = {
            "analysis_time": datetime.now().isoformat(),
            "text_length": len(text),
            "analysis_type": analysis_type,
            "semantic_units": {},
            "raw_response": "",
            "parsing_success": False,
            "success": False
        }
        
        try:
            # 选择合适的提示词模板
            if analysis_type == "comprehensive":
                prompt = self.identification_templates["comprehensive_analysis"].format(text=text)
            elif analysis_type == "concept":
                prompt = self.identification_templates["concept_extraction"].format(text=text)
            elif analysis_type == "entity":
                prompt = self.identification_templates["entity_recognition"].format(text=text)
            elif analysis_type == "sentiment":
                prompt = self.identification_templates["sentiment_analysis"].format(text=text)
            elif analysis_type == "relation":
                prompt = self.identification_templates["semantic_relations"].format(text=text)
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
            
            # 调用讯飞大模型
            print(f"🔍 正在使用讯飞大模型进行{analysis_type}语义分析...")
            response = self.llm_client.generate(prompt)
            result["raw_response"] = response
            
            # 解析JSON响应
            parsed_units = self._parse_llm_response(response, analysis_type)
            result["semantic_units"] = parsed_units
            result["parsing_success"] = True
            
            # 生成分析摘要
            result["analysis_summary"] = self._generate_analysis_summary(parsed_units, analysis_type)
            result["success"] = True
            
            print("✅ 语义单元识别完成")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ 语义单元识别失败: {str(e)}")
        
        return result
    
    def _parse_llm_response(self, response: str, analysis_type: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            # 尝试直接解析JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            
            # 如果直接解析失败，尝试提取结构化信息
            return self._extract_structured_info(response, analysis_type)
            
        except json.JSONDecodeError:
            # JSON解析失败，尝试文本解析
            return self._extract_structured_info(response, analysis_type)
    
    def _extract_structured_info(self, response: str, analysis_type: str) -> Dict[str, Any]:
        """从文本响应中提取结构化信息"""
        extracted = {}
        
        try:
            if analysis_type == "comprehensive":
                # 提取概念
                concepts = re.findall(r'概念[：:]\s*([^\n]+)', response)
                extracted["concepts"] = [{"text": concept.strip(), "role": "核心概念", "importance": 3} 
                                       for concept in concepts[:10]]
                
                # 提取实体
                entities = re.findall(r'实体[：:]\s*([^\n]+)', response)
                extracted["named_entities"] = [{"text": entity.strip(), "type": "其他", "context": ""} 
                                             for entity in entities[:10]]
                
                # 提取关键词
                keywords = re.findall(r'关键词[：:]\s*([^\n]+)', response)
                extracted["key_phrases"] = [{"text": keyword.strip(), "role": "关键表达", "domain": "通用"} 
                                          for keyword in keywords[:10]]
            
            elif analysis_type == "concept":
                concepts = re.findall(r'([^，,。；\n]+)', response)
                extracted["core_concepts"] = [{"concept": concept.strip(), "importance": 3, "category": "主题"} 
                                            for concept in concepts[:10] if len(concept.strip()) > 1]
            
            elif analysis_type == "entity":
                # 简单的实体提取
                lines = response.split('\n')
                persons = []
                organizations = []
                for line in lines:
                    if any(keyword in line for keyword in ['人名', '姓名', '人物']):
                        names = re.findall(r'([^\s，,。；]+)', line)
                        persons.extend([{"name": name, "role": "未知", "context": ""} for name in names[:5]])
                    elif any(keyword in line for keyword in ['公司', '组织', '机构']):
                        orgs = re.findall(r'([^\s，,。；]+)', line)
                        organizations.extend([{"name": org, "type": "组织", "context": ""} for org in orgs[:5]])
                
                extracted["persons"] = persons[:5]
                extracted["organizations"] = organizations[:5]
            
            # 如果提取失败，返回基本结构
            if not extracted:
                extracted = {"extracted_text": response[:500], "parsing_method": "fallback"}
        
        except Exception as e:
            extracted = {"error": f"Text parsing failed: {str(e)}", "raw_text": response[:200]}
        
        return extracted
    
    def _generate_analysis_summary(self, semantic_units: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """生成分析摘要"""
        summary = {
            "analysis_type": analysis_type,
            "total_units_identified": 0,
            "unit_categories": [],
            "key_findings": []
        }
        
        try:
            if analysis_type == "comprehensive":
                # 统计各类语义单元数量
                concepts_count = len(semantic_units.get("concepts", []))
                entities_count = len(semantic_units.get("named_entities", []))
                adjectives_count = len(semantic_units.get("key_adjectives", []))
                verbs_count = len(semantic_units.get("key_verbs", []))
                phrases_count = len(semantic_units.get("key_phrases", []))
                
                summary["total_units_identified"] = (concepts_count + entities_count + 
                                                   adjectives_count + verbs_count + phrases_count)
                summary["unit_categories"] = [
                    f"概念: {concepts_count}个",
                    f"实体: {entities_count}个", 
                    f"形容词: {adjectives_count}个",
                    f"动词: {verbs_count}个",
                    f"短语: {phrases_count}个"
                ]
                
                # 关键发现
                if concepts_count > 0:
                    core_concepts = [c.get("text", "") for c in semantic_units.get("concepts", [])[:3]]
                    summary["key_findings"].append(f"核心概念: {', '.join(core_concepts)}")
                
                if entities_count > 0:
                    entities = [e.get("text", "") for e in semantic_units.get("named_entities", [])[:3]]
                    summary["key_findings"].append(f"主要实体: {', '.join(entities)}")
            
            elif analysis_type == "concept":
                core_concepts = semantic_units.get("core_concepts", [])
                summary["total_units_identified"] = len(core_concepts)
                summary["unit_categories"] = ["核心概念"]
                if core_concepts:
                    top_concepts = [c.get("concept", "") for c in core_concepts[:3]]
                    summary["key_findings"].append(f"主要概念: {', '.join(top_concepts)}")
            
            elif analysis_type == "entity":
                persons = semantic_units.get("persons", [])
                orgs = semantic_units.get("organizations", [])
                summary["total_units_identified"] = len(persons) + len(orgs)
                summary["unit_categories"] = [f"人名: {len(persons)}个", f"组织: {len(orgs)}个"]
            
            elif analysis_type == "sentiment":
                emotional_adj = semantic_units.get("emotional_adjectives", [])
                overall_sentiment = semantic_units.get("overall_sentiment", {})
                summary["total_units_identified"] = len(emotional_adj)
                summary["unit_categories"] = ["情感形容词"]
                if overall_sentiment:
                    polarity = overall_sentiment.get("polarity", "中性")
                    intensity = overall_sentiment.get("intensity", 3)
                    summary["key_findings"].append(f"整体情感: {polarity} (强度: {intensity})")
            
            elif analysis_type == "relation":
                hierarchical = semantic_units.get("hierarchical_relations", [])
                associative = semantic_units.get("associative_relations", [])
                summary["total_units_identified"] = len(hierarchical) + len(associative)
                summary["unit_categories"] = ["层次关系", "关联关系"]
        
        except Exception as e:
            summary["error"] = str(e)
        
        return summary
    
    def batch_identify_semantic_units(self, texts: List[str], analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """批量识别语义单元"""
        batch_result = {
            "batch_time": datetime.now().isoformat(),
            "total_texts": len(texts),
            "analysis_type": analysis_type,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "results": [],
            "batch_summary": {}
        }
        
        for i, text in enumerate(texts):
            print(f"处理文本 {i+1}/{len(texts)}")
            
            try:
                result = self.identify_semantic_units(text, analysis_type)
                result["batch_index"] = i
                
                if result.get("success"):
                    batch_result["successful_analyses"] += 1
                else:
                    batch_result["failed_analyses"] += 1
                
                batch_result["results"].append(result)
                
            except Exception as e:
                batch_result["failed_analyses"] += 1
                batch_result["results"].append({
                    "batch_index": i,
                    "success": False,
                    "error": str(e),
                    "text_preview": text[:100]
                })
        
        # 生成批量摘要
        batch_result["batch_summary"] = self._generate_batch_summary(batch_result)
        
        return batch_result
    
    def _generate_batch_summary(self, batch_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成批量处理摘要"""
        summary = {
            "success_rate": batch_result["successful_analyses"] / batch_result["total_texts"] if batch_result["total_texts"] > 0 else 0,
            "total_units_identified": 0,
            "average_units_per_text": 0,
            "common_concepts": [],
            "common_entities": []
        }
        
        try:
            # 统计总的语义单元数量
            successful_results = [r for r in batch_result["results"] if r.get("success")]
            
            total_units = 0
            all_concepts = []
            all_entities = []
            
            for result in successful_results:
                analysis_summary = result.get("analysis_summary", {})
                total_units += analysis_summary.get("total_units_identified", 0)
                
                # 收集概念和实体
                semantic_units = result.get("semantic_units", {})
                concepts = semantic_units.get("concepts", [])
                entities = semantic_units.get("named_entities", [])
                
                all_concepts.extend([c.get("text", "") for c in concepts])
                all_entities.extend([e.get("text", "") for e in entities])
            
            summary["total_units_identified"] = total_units
            summary["average_units_per_text"] = total_units / len(successful_results) if successful_results else 0
            
            # 找出常见的概念和实体
            from collections import Counter
            concept_counts = Counter(all_concepts)
            entity_counts = Counter(all_entities)
            
            summary["common_concepts"] = [concept for concept, count in concept_counts.most_common(5)]
            summary["common_entities"] = [entity for entity, count in entity_counts.most_common(5)]
        
        except Exception as e:
            summary["error"] = str(e)
        
        return summary
    
    def get_semantic_unit_statistics(self, semantic_units: Dict[str, Any]) -> Dict[str, Any]:
        """获取语义单元统计信息"""
        stats = {
            "concept_count": 0,
            "entity_count": 0,
            "adjective_count": 0,
            "verb_count": 0,
            "phrase_count": 0,
            "relation_count": 0,
            "sentiment_distribution": {},
            "importance_distribution": {}
        }
        
        try:
            # 统计各类语义单元数量
            stats["concept_count"] = len(semantic_units.get("concepts", []))
            stats["entity_count"] = len(semantic_units.get("named_entities", []))
            stats["adjective_count"] = len(semantic_units.get("key_adjectives", []))
            stats["verb_count"] = len(semantic_units.get("key_verbs", []))
            stats["phrase_count"] = len(semantic_units.get("key_phrases", []))
            stats["relation_count"] = len(semantic_units.get("semantic_relations", []))
            
            # 情感分布统计
            adjectives = semantic_units.get("key_adjectives", [])
            sentiment_counts = {"积极": 0, "消极": 0, "中性": 0}
            for adj in adjectives:
                sentiment = adj.get("sentiment_polarity", "中性")
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            stats["sentiment_distribution"] = sentiment_counts
            
            # 重要性分布统计
            concepts = semantic_units.get("concepts", [])
            importance_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for concept in concepts:
                importance = concept.get("importance", 3)
                importance_counts[importance] = importance_counts.get(importance, 0) + 1
            stats["importance_distribution"] = importance_counts
        
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
