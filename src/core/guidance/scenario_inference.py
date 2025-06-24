import json
import yaml
import re
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter
import os

class MockLLMClient:
    def generate(self, prompt: str) -> str:
        print(f"--- LLM Prompt ---\n{prompt}\n--- End LLM Prompt ---")
        return json.dumps({
            "inferred_scenario": "Product Proposal",
            "supporting_evidence": "mentions 'user stories', 'tech stack', 'development plan'",
            "inferred_reporter_role": "Product Manager",
            "inferred_reader_role": "Development Team & Management"
        })

class EnhancedScenarioInferenceModule:
    """
    Enhanced scenario inference module with advanced document analysis capabilities.
    Features:
    - High-precision document type identification
    - Author role inference with confidence scoring
    - Target audience analysis
    - Application scenario matching
    - Multi-level confidence assessment
    """

    def __init__(self, llm_client, kb_path: str = "src/core/knowledge_base"):
        self.llm_client = llm_client
        self.kb_path = kb_path
        self.scenario_kb = self._load_kb("scenario_definitions.yaml")
        self.role_kb = self._load_kb("role_profiles.yaml")

        # Initialize pattern libraries for rule-based inference
        self._init_pattern_libraries()

        # Document type classifiers
        self.document_classifiers = {
            "technical_report": {
                "keywords": ["algorithm", "implementation", "performance", "results", "methodology", "analysis", "experiment", "evaluation"],
                "patterns": [r"section\s+\d+", r"figure\s+\d+", r"table\s+\d+", r"references?", r"bibliography"],
                "structure": ["abstract", "introduction", "methodology", "results", "conclusion"]
            },
            "product_proposal": {
                "keywords": ["product", "feature", "requirement", "user story", "roadmap", "MVP", "market", "business value"],
                "patterns": [r"user\s+story", r"acceptance\s+criteria", r"business\s+case", r"go-to-market"],
                "structure": ["overview", "requirements", "features", "timeline", "resources"]
            },
            "market_analysis": {
                "keywords": ["market", "competitor", "analysis", "SWOT", "target audience", "customer", "segment", "strategy"],
                "patterns": [r"market\s+size", r"competitive\s+landscape", r"target\s+market", r"customer\s+segment"],
                "structure": ["executive summary", "market overview", "competitive analysis", "recommendations"]
            },
            "meeting_minutes": {
                "keywords": ["meeting", "agenda", "action item", "decision", "attendee", "discussion", "follow-up"],
                "patterns": [r"action\s+item", r"next\s+steps", r"attendees?", r"agenda"],
                "structure": ["attendees", "agenda", "discussion", "decisions", "action items"]
            },
            "research_paper": {
                "keywords": ["research", "study", "hypothesis", "literature", "citation", "peer review", "journal"],
                "patterns": [r"abstract", r"keywords", r"doi:", r"citation", r"peer\s+review"],
                "structure": ["abstract", "keywords", "introduction", "literature review", "methodology", "results", "discussion", "conclusion", "references"]
            },
            "government_document": {
                "keywords": ["政府", "公文", "通知", "公告", "决定", "意见", "办法", "规定", "条例", "法规", "政策", "行政", "机关", "部门", "单位", "发文", "印发", "执行", "贯彻", "落实", "督办", "检查", "考核", "评估", "汇报", "请示", "批复", "函", "会议纪要", "工作方案", "实施方案", "应急预案"],
                "patterns": [r".*人民政府", r".*委员会", r".*办公室", r".*局", r".*厅", r".*部", r"发.*\[.*\].*号", r"关于.*的.*", r".*年.*月.*日"],
                "structure": ["标题", "主送机关", "正文", "附件", "发文机关署名", "成文日期", "印章", "附注"]
            }
        }

    def _load_kb(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(self.kb_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Knowledge base file not found: {filepath}")
            return {}
        except Exception as e:
            print(f"Error loading KB file {filepath}: {e}")
            return {}

    def _init_pattern_libraries(self):
        """Initialize pattern libraries for different analysis aspects."""

        # Role indicators
        self.role_indicators = {
            "product_manager": ["product", "feature", "requirement", "roadmap", "user story", "business value", "market fit"],
            "technical_lead": ["architecture", "implementation", "technical", "system design", "performance", "scalability"],
            "researcher": ["research", "study", "hypothesis", "methodology", "experiment", "analysis", "findings"],
            "analyst": ["analysis", "data", "metrics", "insights", "trends", "patterns", "statistics"],
            "manager": ["strategy", "planning", "resources", "timeline", "budget", "team", "objectives"],
            "consultant": ["recommendation", "assessment", "evaluation", "best practices", "optimization"],
            "marketing": ["campaign", "brand", "customer", "market", "promotion", "engagement", "conversion"],
            "government_official": ["政府", "机关", "部门", "公务员", "行政", "政策", "法规", "执行", "监督", "管理"],
            "policy_maker": ["政策制定", "法规起草", "制度建设", "规划编制", "决策", "调研", "论证"],
            "secretary": ["秘书", "办公室", "文秘", "公文处理", "会务", "档案", "信息", "协调"],
            "department_head": ["部门负责人", "主任", "局长", "厅长", "处长", "科长", "领导", "管理"]
        }

        # Audience indicators
        self.audience_indicators = {
            "technical_team": ["implementation", "code", "API", "technical details", "architecture"],
            "management": ["ROI", "budget", "strategy", "business impact", "resources", "timeline"],
            "stakeholders": ["overview", "summary", "key points", "recommendations", "next steps"],
            "customers": ["benefits", "features", "value proposition", "user experience"],
            "investors": ["market opportunity", "financial projections", "competitive advantage", "growth"],
            "academic": ["methodology", "literature review", "peer review", "citations", "research"]
        }

        # Formality indicators
        self.formality_indicators = {
            "formal": ["hereby", "pursuant", "aforementioned", "notwithstanding", "whereas"],
            "semi_formal": ["please note", "kindly", "we recommend", "it is suggested"],
            "informal": ["hey", "guys", "awesome", "cool", "let's", "we'll", "can't"]
        }

        # Purpose indicators
        self.purpose_indicators = {
            "informational": ["inform", "update", "notify", "report", "summary", "overview"],
            "persuasive": ["recommend", "propose", "suggest", "convince", "argue", "advocate"],
            "instructional": ["how to", "step by step", "guide", "tutorial", "instructions", "procedure"],
            "analytical": ["analyze", "evaluate", "assess", "compare", "examine", "investigate"]
        }

    def infer_scenario_and_roles(self, document_content: str, structural_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhanced scenario and role inference with multi-level analysis.

        Args:
            document_content: The text content of the document
            structural_analysis: Optional structural analysis from enhanced parser

        Returns:
            Comprehensive inference results with confidence scores
        """
        try:
            # Perform rule-based analysis first
            rule_based_results = self._rule_based_inference(document_content, structural_analysis)

            # Enhance with LLM-based analysis
            llm_results = self._llm_based_inference(document_content)

            # Combine and validate results
            combined_results = self._combine_inference_results(rule_based_results, llm_results)

            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(combined_results, document_content)

            # Generate final inference
            final_inference = {
                "document_type": combined_results["document_type"],
                "scenario": combined_results["scenario"],
                "author_role": combined_results["author_role"],
                "target_audience": combined_results["target_audience"],
                "document_purpose": combined_results["document_purpose"],
                "formality_level": combined_results["formality_level"],
                "confidence_scores": confidence_scores,
                "supporting_evidence": combined_results.get("supporting_evidence", []),
                "alternative_scenarios": combined_results.get("alternative_scenarios", []),
                "analysis_metadata": {
                    "rule_based_confidence": rule_based_results.get("confidence", 0.0),
                    "llm_confidence": llm_results.get("confidence", 0.0),
                    "combined_confidence": confidence_scores.get("overall", 0.0)
                }
            }

            return final_inference

        except Exception as e:
            return {"error": f"Error during enhanced scenario inference: {e}"}

    def _rule_based_inference(self, document_content: str, structural_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform rule-based inference using pattern matching and keyword analysis."""

        content_lower = document_content.lower()

        # Document type classification
        type_scores = {}
        for doc_type, classifier in self.document_classifiers.items():
            score = 0
            evidence = []

            # Keyword matching
            keyword_matches = sum(1 for keyword in classifier["keywords"] if keyword in content_lower)
            score += keyword_matches * 2
            if keyword_matches > 0:
                evidence.append(f"Keywords: {keyword_matches} matches")

            # Pattern matching
            pattern_matches = sum(1 for pattern in classifier["patterns"] if re.search(pattern, content_lower))
            score += pattern_matches * 3
            if pattern_matches > 0:
                evidence.append(f"Patterns: {pattern_matches} matches")

            # Structure matching (if structural analysis available)
            if structural_analysis and "headings" in structural_analysis:
                headings = [h["text"].lower() for h in structural_analysis["headings"]]
                structure_matches = sum(1 for struct_elem in classifier["structure"] if any(struct_elem in heading for heading in headings))
                score += structure_matches * 4
                if structure_matches > 0:
                    evidence.append(f"Structure: {structure_matches} matches")

            type_scores[doc_type] = {"score": score, "evidence": evidence}

        # Get best document type
        best_type = max(type_scores.items(), key=lambda x: x[1]["score"])
        document_type = best_type[0] if best_type[1]["score"] > 0 else "general_document"

        # Author role inference
        role_scores = {}
        for role, indicators in self.role_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            role_scores[role] = score

        best_role = max(role_scores.items(), key=lambda x: x[1])
        author_role = best_role[0] if best_role[1] > 0 else "general_author"

        # Audience inference
        audience_scores = {}
        for audience, indicators in self.audience_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            audience_scores[audience] = score

        best_audience = max(audience_scores.items(), key=lambda x: x[1])
        target_audience = best_audience[0] if best_audience[1] > 0 else "general_audience"

        # Purpose inference
        purpose_scores = {}
        for purpose, indicators in self.purpose_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            purpose_scores[purpose] = score

        best_purpose = max(purpose_scores.items(), key=lambda x: x[1])
        document_purpose = best_purpose[0] if best_purpose[1] > 0 else "general"

        # Formality level
        formality_scores = {}
        for level, indicators in self.formality_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            formality_scores[level] = score

        best_formality = max(formality_scores.items(), key=lambda x: x[1])
        formality_level = best_formality[0] if best_formality[1] > 0 else "neutral"

        # Calculate confidence based on score distribution
        total_score = sum(scores["score"] for scores in type_scores.values())
        confidence = best_type[1]["score"] / max(total_score, 1) if total_score > 0 else 0.0

        return {
            "document_type": document_type,
            "scenario": self._map_type_to_scenario(document_type),
            "author_role": author_role,
            "target_audience": target_audience,
            "document_purpose": document_purpose,
            "formality_level": formality_level,
            "confidence": confidence,
            "supporting_evidence": best_type[1]["evidence"],
            "type_scores": type_scores,
            "role_scores": role_scores,
            "audience_scores": audience_scores
        }

    def _map_type_to_scenario(self, document_type: str) -> str:
        """Map document type to scenario name."""
        type_to_scenario = {
            "technical_report": "Technical Report",
            "product_proposal": "Product Proposal",
            "market_analysis": "Market Analysis",
            "meeting_minutes": "Meeting Minutes",
            "research_paper": "Research Paper",
            "general_document": "General Document"
        }
        return type_to_scenario.get(document_type, "General Document")

    def _llm_based_inference(self, document_content: str) -> Dict[str, Any]:
        """Perform LLM-based inference for enhanced accuracy."""

        # If no LLM client available, return empty result (not an error)
        if not self.llm_client:
            return {"error": "No LLM client available", "confidence": 0.0}

        prompt = f"""
        You are an expert document analyst. Analyze the following document and provide a detailed assessment.

        Document Content (first 2000 characters):
        ---
        {document_content[:2000]}
        ---

        Please analyze and provide your assessment in the following JSON format:
        {{
            "document_type": "one of: technical_report, product_proposal, market_analysis, meeting_minutes, research_paper, business_plan, user_manual, policy_document, government_document, general_document",
            "scenario": "descriptive scenario name",
            "author_role": "most likely author role/position",
            "target_audience": "primary intended audience",
            "document_purpose": "one of: informational, persuasive, instructional, analytical, regulatory, administrative",
            "formality_level": "one of: formal, semi_formal, informal",
            "confidence": "confidence score from 0.0 to 1.0",
            "supporting_evidence": ["list of specific evidence from the text"],
            "key_topics": ["main topics discussed"],
            "writing_style": "description of writing style",
            "complexity_level": "one of: basic, intermediate, advanced"
        }}

        Ensure your response is valid JSON only.
        """

        try:
            llm_response = self.llm_client.generate(prompt)
            if isinstance(llm_response, str):
                try:
                    inferred_data = json.loads(llm_response)
                except json.JSONDecodeError:
                    # Try to extract JSON from response
                    match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                    if match:
                        inferred_data = json.loads(match.group(0))
                    else:
                        return {"error": "LLM did not return parsable JSON.", "confidence": 0.0}
            else:
                inferred_data = llm_response

            # Validate and normalize the response
            normalized_data = {
                "document_type": inferred_data.get("document_type", "general_document"),
                "scenario": inferred_data.get("scenario", "General Document"),
                "author_role": inferred_data.get("author_role", "unknown"),
                "target_audience": inferred_data.get("target_audience", "general_audience"),
                "document_purpose": inferred_data.get("document_purpose", "informational"),
                "formality_level": inferred_data.get("formality_level", "neutral"),
                "confidence": float(inferred_data.get("confidence", 0.5)),
                "supporting_evidence": inferred_data.get("supporting_evidence", []),
                "key_topics": inferred_data.get("key_topics", []),
                "writing_style": inferred_data.get("writing_style", "standard"),
                "complexity_level": inferred_data.get("complexity_level", "intermediate")
            }

            return normalized_data

        except Exception as e:
            return {"error": f"Error during LLM-based inference: {e}", "confidence": 0.0}

    def _combine_inference_results(self, rule_based: Dict[str, Any], llm_based: Dict[str, Any]) -> Dict[str, Any]:
        """Combine rule-based and LLM-based inference results."""

        # Handle errors
        if "error" in rule_based and "error" in llm_based:
            return {"error": "Both rule-based and LLM-based inference failed"}

        if "error" in rule_based:
            return llm_based

        if "error" in llm_based:
            return rule_based

        # Combine results with weighted confidence
        rule_confidence = rule_based.get("confidence", 0.0)
        llm_confidence = llm_based.get("confidence", 0.0)

        # Weight rule-based results higher for structured documents, LLM higher for complex analysis
        rule_weight = 0.4
        llm_weight = 0.6

        # Choose primary results based on confidence
        if rule_confidence > llm_confidence:
            primary_source = rule_based
            secondary_source = llm_based
            primary_weight = rule_weight + 0.2
        else:
            primary_source = llm_based
            secondary_source = rule_based
            primary_weight = llm_weight + 0.2

        # Combine evidence
        combined_evidence = []
        if isinstance(primary_source.get("supporting_evidence"), list):
            combined_evidence.extend(primary_source["supporting_evidence"])
        elif primary_source.get("supporting_evidence"):
            combined_evidence.append(str(primary_source["supporting_evidence"]))

        if isinstance(secondary_source.get("supporting_evidence"), list):
            combined_evidence.extend(secondary_source["supporting_evidence"])
        elif secondary_source.get("supporting_evidence"):
            combined_evidence.append(str(secondary_source["supporting_evidence"]))

        # Generate alternative scenarios
        alternative_scenarios = []
        if (primary_source.get("scenario") != secondary_source.get("scenario") and
            secondary_source.get("scenario") and
            "error" not in secondary_source):
            alternative_scenarios.append({
                "scenario": secondary_source.get("scenario", "Unknown"),
                "confidence": secondary_source.get("confidence", 0.0),
                "source": "secondary_analysis"
            })

        combined_result = {
            "document_type": primary_source.get("document_type", "general_document"),
            "scenario": primary_source.get("scenario", "General Document"),
            "author_role": primary_source.get("author_role", "unknown"),
            "target_audience": primary_source.get("target_audience", "general_audience"),
            "document_purpose": primary_source.get("document_purpose", "informational"),
            "formality_level": primary_source.get("formality_level", "neutral"),
            "supporting_evidence": combined_evidence,
            "alternative_scenarios": alternative_scenarios,
            "primary_source": "rule_based" if primary_source == rule_based else "llm_based",
            "rule_based_results": rule_based,
            "llm_based_results": llm_based
        }

        return combined_result

    def _calculate_confidence_scores(self, combined_results: Dict[str, Any], document_content: str) -> Dict[str, float]:
        """Calculate comprehensive confidence scores for the inference results."""

        scores = {}

        # Base confidence from primary analysis
        rule_confidence = combined_results.get("rule_based_results", {}).get("confidence", 0.0)
        llm_confidence = combined_results.get("llm_based_results", {}).get("confidence", 0.0)

        # Document length factor (longer documents generally provide more reliable signals)
        length_factor = min(len(document_content) / 500, 1.0)  # More reasonable threshold
        length_factor = max(length_factor, 0.3)  # Minimum factor to avoid too low scores

        # Evidence strength factor
        evidence_count = len(combined_results.get("supporting_evidence", []))
        evidence_factor = min(evidence_count / 3, 1.0)  # Lower threshold for evidence
        evidence_factor = max(evidence_factor, 0.5)  # Minimum factor

        # Consistency factor (how well rule-based and LLM results agree)
        consistency_factor = 1.0
        if combined_results.get("rule_based_results") and combined_results.get("llm_based_results"):
            rule_type = combined_results["rule_based_results"].get("document_type", "")
            llm_type = combined_results["llm_based_results"].get("document_type", "")
            if rule_type != llm_type:
                consistency_factor = 0.8  # Less penalty for disagreement

        # Base confidence boost for having both analyses
        base_boost = 0.2 if rule_confidence > 0 and llm_confidence > 0 else 0

        # Calculate individual confidence scores with improved formula
        combined_confidence = max(rule_confidence, llm_confidence) + base_boost
        scores["document_type"] = combined_confidence * length_factor * consistency_factor
        scores["scenario"] = scores["document_type"]  # Same as document type
        scores["author_role"] = combined_confidence * evidence_factor
        scores["target_audience"] = combined_confidence * evidence_factor
        scores["document_purpose"] = combined_confidence * evidence_factor * 0.9

        # Overall confidence (weighted average)
        scores["overall"] = (
            scores["document_type"] * 0.3 +
            scores["author_role"] * 0.25 +
            scores["target_audience"] * 0.25 +
            scores["document_purpose"] * 0.2
        )

        # Ensure all scores are between 0 and 1
        for key in scores:
            scores[key] = max(0.0, min(1.0, scores[key]))

        return scores

    def generate_enhanced_confirmation_prompt(self, inferred_data: Dict[str, Any]) -> str:
        """Generate an enhanced user confirmation prompt with detailed analysis."""

        if "error" in inferred_data:
            return f"I encountered an issue while analyzing the document: {inferred_data['error']}. Could you please provide more details about the document's purpose?"

        scenario = inferred_data.get('scenario', 'an unspecified document')
        author_role = inferred_data.get('author_role', 'unknown author')
        target_audience = inferred_data.get('target_audience', 'general audience')
        confidence = inferred_data.get('confidence_scores', {}).get('overall', 0.0)
        evidence = inferred_data.get('supporting_evidence', [])

        # Format evidence
        evidence_text = "key indicators in the content" if not evidence else ", ".join(evidence[:3])
        if len(evidence) > 3:
            evidence_text += f" and {len(evidence) - 3} other indicators"

        # Confidence level description
        if confidence >= 0.8:
            confidence_desc = "very confident"
        elif confidence >= 0.6:
            confidence_desc = "confident"
        elif confidence >= 0.4:
            confidence_desc = "moderately confident"
        else:
            confidence_desc = "uncertain"

        prompt = f"""
📋 **Document Analysis Results**

I'm {confidence_desc} (confidence: {confidence:.1%}) that this is a **{scenario}**.

🔍 **My Analysis:**
- **Document Type**: {scenario}
- **Likely Author**: {author_role}
- **Target Audience**: {target_audience}
- **Supporting Evidence**: {evidence_text}

❓ **Please Confirm:**
1. Does this assessment seem accurate? (Yes/No)
2. If not, what type of document is this? _______________
3. Who is the intended audience? _______________

"""

        # Add alternative scenarios if available
        alternatives = inferred_data.get('alternative_scenarios', [])
        if alternatives:
            prompt += f"\n🔄 **Alternative Possibilities:**\n"
            for alt in alternatives[:2]:  # Show top 2 alternatives
                prompt += f"- {alt['scenario']} (confidence: {alt['confidence']:.1%})\n"

        return prompt

    def generate_user_confirmation_prompt(self, inferred_data: Dict[str, Any]) -> str:
        if "error" in inferred_data:
            return f"I encountered an issue while analyzing the document: {inferred_data['error']}. Could you please provide more details about the document's purpose?"
        scenario = inferred_data.get('inferred_scenario', 'an unspecified document')
        evidence = inferred_data.get('supporting_evidence', 'some key phrases')
        reporter = inferred_data.get('inferred_reporter_role', 'the author')
        reader = inferred_data.get('inferred_reader_role', 'its readers')
        prompt = (
            f"I've analyzed your document. It seems to be a **{scenario}**.\n"
            f"I noticed **{evidence}**, which led me to this conclusion.\n\n"
            f"Does this initial assessment sound correct? (Yes/No/Specify Correct Scenario: _______)\n\n"
            f"I also inferred that it might be written by a **{reporter}** and intended for **{reader}**. Is this accurate? (Yes/No/Specify Roles: _______)"
        )
        return prompt

    def suggest_next_steps_and_roles(self, confirmed_scenario: str) -> Dict[str, Any]:
        scenario_config = next((s for s in self.scenario_kb.get('scenarios', []) if s.get('scenario_name') == confirmed_scenario), None)
        if scenario_config:
            suggested_roles = scenario_config.get('recommended_reviewer_roles', [])
            suggested_focus = scenario_config.get('default_review_focus', 'general review')
            action_description = f"Proceed with a review focusing on '{suggested_focus}'."
            return {
                "suggestion": action_description,
                "suggested_roles": suggested_roles,
                "default_review_focus": suggested_focus
            }
        else:
            return {
                "suggestion": "Proceed with a general review.",
                "suggested_roles": [],
                "default_review_focus": "general review"
            }

    def get_scenario_recommendations(self, scenario: str) -> Dict[str, Any]:
        """Get detailed recommendations for a specific scenario."""

        scenario_config = next((s for s in self.scenario_kb.get('scenarios', []) if s.get('scenario_name') == scenario), None)

        if not scenario_config:
            return {
                "error": f"No configuration found for scenario: {scenario}",
                "available_scenarios": [s.get('scenario_name') for s in self.scenario_kb.get('scenarios', [])]
            }

        return {
            "scenario_name": scenario_config.get('scenario_name'),
            "description": scenario_config.get('description', 'No description available'),
            "keywords": scenario_config.get('keywords', []),
            "typical_reporter_roles": scenario_config.get('typical_reporter_roles', []),
            "typical_reader_roles": scenario_config.get('typical_reader_roles', []),
            "recommended_reviewer_roles": scenario_config.get('recommended_reviewer_roles', []),
            "default_review_focus": scenario_config.get('default_review_focus', []),
            "suggested_tools": scenario_config.get('suggested_tools', []),
            "quality_criteria": scenario_config.get('quality_criteria', [])
        }

    def validate_inference_quality(self, inference_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of inference results and provide improvement suggestions."""

        quality_report = {
            "overall_quality": "good",
            "confidence_assessment": "acceptable",
            "evidence_strength": "sufficient",
            "consistency_check": "passed",
            "improvement_suggestions": []
        }

        # Check overall confidence
        overall_confidence = inference_results.get('confidence_scores', {}).get('overall', 0.0)
        if overall_confidence < 0.4:
            quality_report["overall_quality"] = "poor"
            quality_report["confidence_assessment"] = "low"
            quality_report["improvement_suggestions"].append("Document may need manual review due to low confidence")
        elif overall_confidence < 0.6:
            quality_report["overall_quality"] = "fair"
            quality_report["confidence_assessment"] = "moderate"
            quality_report["improvement_suggestions"].append("Consider additional context or longer document sample")

        # Check evidence strength
        evidence_count = len(inference_results.get('supporting_evidence', []))
        if evidence_count < 2:
            quality_report["evidence_strength"] = "weak"
            quality_report["improvement_suggestions"].append("Limited supporting evidence found")
        elif evidence_count < 4:
            quality_report["evidence_strength"] = "moderate"

        # Check for alternative scenarios
        alternatives = inference_results.get('alternative_scenarios', [])
        if alternatives and len(alternatives) > 0:
            top_alt_confidence = alternatives[0].get('confidence', 0.0)
            if top_alt_confidence > overall_confidence * 0.8:
                quality_report["consistency_check"] = "uncertain"
                quality_report["improvement_suggestions"].append("Multiple scenarios have similar confidence - manual verification recommended")

        return quality_report


# Backward compatibility wrapper
class ScenarioInferenceModule(EnhancedScenarioInferenceModule):
    """Backward compatibility wrapper for the enhanced scenario inference module."""

    def infer_scenario_and_roles(self, document_content: str) -> Dict[str, Any]:
        """Backward compatible method that returns results in the original format."""

        # Call the enhanced method
        enhanced_results = super().infer_scenario_and_roles(document_content)

        if "error" in enhanced_results:
            return enhanced_results

        # Convert to original format
        return {
            "inferred_scenario": enhanced_results.get("scenario", "General Document"),
            "supporting_evidence": ", ".join(enhanced_results.get("supporting_evidence", [])),
            "inferred_reporter_role": enhanced_results.get("author_role", "Unknown"),
            "inferred_reader_role": enhanced_results.get("target_audience", "General Audience")
        }