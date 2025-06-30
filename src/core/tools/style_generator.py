#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Style Generator - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

import os
import yaml
from typing import Dict, Any, List, Optional
from .base_tool import BaseTool

class EnhancedStyleGeneratorTool(BaseTool):

    def __init__(self, llm_client, style_kb_path: str = "src/core/knowledge_base/style_templates.yaml", **kwargs):
        super().__init__(**kwargs)
        self.llm_client = llm_client
        self.style_kb_path = style_kb_path
        self.styles = self._load_styles()

        # Enhanced style definitions
        self.enhanced_styles = {
            "professional": {
                "description": "Formal, objective, and data-driven business communication",
                "characteristics": [
                    "Uses formal vocabulary and complete sentences",
                    "Avoids contractions and colloquialisms",
                    "Emphasizes facts and data",
                    "Maintains neutral, objective tone",
                    "Uses passive voice appropriately"
                ],
                "examples": {
                    "greeting": "Dear colleagues,",
                    "conclusion": "We recommend proceeding with the proposed solution.",
                    "transition": "Furthermore, the analysis indicates..."
                }
            },
            "casual": {
                "description": "Friendly, approachable, and conversational communication",
                "characteristics": [
                    "Uses contractions and informal language",
                    "Includes personal pronouns (you, we, I)",
                    "Conversational tone with shorter sentences",
                    "May include rhetorical questions",
                    "Uses active voice predominantly"
                ],
                "examples": {
                    "greeting": "Hi everyone!",
                    "conclusion": "So, what do you think? Let's give it a try!",
                    "transition": "Now, here's the interesting part..."
                }
            },
            "technical": {
                "description": "Precise, detailed, and domain-specific technical communication",
                "characteristics": [
                    "Uses technical terminology and jargon appropriately",
                    "Includes specific details and measurements",
                    "Structured and logical presentation",
                    "References standards and specifications",
                    "Emphasizes accuracy and precision"
                ],
                "examples": {
                    "greeting": "Technical team members,",
                    "conclusion": "Implementation requires adherence to specified protocols.",
                    "transition": "The algorithm complexity analysis reveals..."
                }
            },
            "academic": {
                "description": "Scholarly, research-oriented, and evidence-based communication",
                "characteristics": [
                    "Uses sophisticated vocabulary",
                    "Includes citations and references",
                    "Presents balanced arguments",
                    "Uses hedging language (may, might, appears)",
                    "Follows academic conventions"
                ],
                "examples": {
                    "greeting": "Esteemed colleagues,",
                    "conclusion": "The evidence suggests that further research is warranted.",
                    "transition": "However, it should be noted that..."
                }
            },
            "persuasive": {
                "description": "Compelling, influential, and action-oriented communication",
                "characteristics": [
                    "Uses strong, confident language",
                    "Includes calls to action",
                    "Emphasizes benefits and outcomes",
                    "Uses rhetorical devices",
                    "Creates sense of urgency"
                ],
                "examples": {
                    "greeting": "Valued stakeholders,",
                    "conclusion": "The time to act is now - let's seize this opportunity!",
                    "transition": "More importantly, this breakthrough will..."
                }
            },
            "creative": {
                "description": "Imaginative, engaging, and expressive communication",
                "characteristics": [
                    "Uses vivid imagery and metaphors",
                    "Varies sentence structure for rhythm",
                    "Includes storytelling elements",
                    "Uses emotional language",
                    "Engages multiple senses"
                ],
                "examples": {
                    "greeting": "Fellow innovators and dreamers,",
                    "conclusion": "Together, we'll paint a new future with bold strokes of innovation.",
                    "transition": "Picture this scenario..."
                }
            }
        }

    def _load_styles(self) -> Dict[str, Any]:
        """Load style definitions from YAML file or use defaults."""
        try:
            if os.path.exists(self.style_kb_path):
                with open(self.style_kb_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load style templates from {self.style_kb_path}: {e}")

        # Return basic styles as fallback
        return {
            "professional": {"description": "Formal, objective, and data-driven."},
            "casual": {"description": "Friendly, approachable, and informal."},
            "technical": {"description": "Precise, uses jargon, detail-oriented."},
        }

    def execute(self, operation: str = "transform_style", **kwargs) -> Dict[str, Any]:
        """
        Execute style generation operation.

        Args:
            operation: Type of operation (transform_style, analyze_style, suggest_improvements)
            **kwargs: Operation-specific parameters
        """
        try:
            if operation == "transform_style":
                return self.transform_style(**kwargs)
            elif operation == "analyze_style":
                return self.analyze_style(**kwargs)
            elif operation == "suggest_improvements":
                return self.suggest_style_improvements(**kwargs)
            elif operation == "compare_styles":
                return self.compare_styles(**kwargs)
            else:
                return {"error": f"Unknown operation: {operation}"}
        except Exception as e:
            return {"error": f"Error in style generation: {e}"}

    def transform_style(self, text_content: str, target_style: str,
                       original_role: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Transform text to target style with enhanced capabilities."""

        if not text_content or not text_content.strip():
            return {"error": "No text content provided for style transformation"}

        # Check if target style exists
        style_info = self._get_style_info(target_style)
        if not style_info:
            available_styles = list(self.enhanced_styles.keys()) + list(self.styles.keys())
            return {"error": f"Style '{target_style}' not found. Available styles: {available_styles}"}

        # Analyze original style
        original_style_analysis = self._analyze_text_style(text_content)

        # Generate transformation prompt
        prompt = self._create_style_transformation_prompt(
            text_content, target_style, style_info, original_role, context, original_style_analysis
        )

        try:
            if self.llm_client:
                # Use LLM for transformation
                rewritten_text = self.llm_client.generate(prompt)

                # Post-process the result
                rewritten_text = self._post_process_transformed_text(rewritten_text, target_style)

                # Validate transformation quality
                quality_score = self._assess_transformation_quality(text_content, rewritten_text, target_style)

                return {
                    "success": True,
                    "original_text": text_content,
                    "rewritten_text": rewritten_text,
                    "target_style": target_style,
                    "original_style_analysis": original_style_analysis,
                    "transformation_quality": quality_score,
                    "style_characteristics": style_info.get("characteristics", []),
                    "word_count_original": len(text_content.split()),
                    "word_count_transformed": len(rewritten_text.split())
                }
            else:
                # Fallback: Rule-based transformation
                rewritten_text = self._rule_based_style_transformation(text_content, target_style, style_info)

                return {
                    "success": True,
                    "original_text": text_content,
                    "rewritten_text": rewritten_text,
                    "target_style": target_style,
                    "transformation_method": "rule_based",
                    "note": "Used rule-based transformation (LLM not available)"
                }

        except Exception as e:
            return {"error": f"Error during style transformation: {e}"}

    def _get_style_info(self, style_name: str) -> Optional[Dict[str, Any]]:
        """Get style information from enhanced or basic styles."""
        if style_name in self.enhanced_styles:
            return self.enhanced_styles[style_name]
        elif style_name in self.styles:
            return self.styles[style_name]
        return None

    def _analyze_text_style(self, text: str) -> Dict[str, Any]:
        """Analyze the current style characteristics of text."""
        import re

        # Basic style analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        words = text.split()

        analysis = {
            "sentence_count": len(sentences),
            "word_count": len(words),
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "has_contractions": bool(re.search(r"\w+'\w+", text)),
            "has_questions": bool(re.search(r'\?', text)),
            "has_exclamations": bool(re.search(r'!', text)),
            "formality_indicators": {
                "formal_words": len(re.findall(r'\b(furthermore|however|therefore|consequently|nevertheless)\b', text, re.IGNORECASE)),
                "casual_words": len(re.findall(r'\b(yeah|okay|cool|awesome|stuff|things)\b', text, re.IGNORECASE)),
                "technical_words": len(re.findall(r'\b(algorithm|implementation|methodology|framework|architecture)\b', text, re.IGNORECASE))
            }
        }

        # Determine likely current style
        if analysis["formality_indicators"]["formal_words"] > 2:
            analysis["likely_style"] = "professional"
        elif analysis["formality_indicators"]["technical_words"] > 2:
            analysis["likely_style"] = "technical"
        elif analysis["has_contractions"] or analysis["formality_indicators"]["casual_words"] > 0:
            analysis["likely_style"] = "casual"
        else:
            analysis["likely_style"] = "neutral"

        return analysis

    def _create_style_transformation_prompt(self, text: str, target_style: str,
                                          style_info: Dict[str, Any], original_role: str = None,
                                          context: Dict[str, Any] = None,
                                          original_analysis: Dict[str, Any] = None) -> str:
        """Create a comprehensive prompt for style transformation."""

        prompt = f"""You are an expert writing coach specializing in style transformation.

TASK: Transform the following text to adopt a '{target_style}' writing style.

TARGET STYLE: {target_style}
DESCRIPTION: {style_info.get('description', 'No description available')}

STYLE CHARACTERISTICS:
"""

        # Add style characteristics
        if 'characteristics' in style_info:
            for char in style_info['characteristics']:
                prompt += f"- {char}\n"

        # Add examples if available
        if 'examples' in style_info:
            prompt += f"\nSTYLE EXAMPLES:\n"
            for example_type, example_text in style_info['examples'].items():
                prompt += f"- {example_type.title()}: {example_text}\n"

        # Add context information
        if context:
            prompt += f"\nCONTEXT:\n"
            if 'document_type' in context:
                prompt += f"- Document Type: {context['document_type']}\n"
            if 'audience' in context:
                prompt += f"- Target Audience: {context['audience']}\n"
            if 'purpose' in context:
                prompt += f"- Purpose: {context['purpose']}\n"

        if original_role:
            prompt += f"- Original Author Role: {original_role}\n"

        # Add original style analysis
        if original_analysis:
            prompt += f"\nORIGINAL STYLE ANALYSIS:\n"
            prompt += f"- Current likely style: {original_analysis.get('likely_style', 'unknown')}\n"
            prompt += f"- Average sentence length: {original_analysis.get('avg_sentence_length', 0):.1f} words\n"
            prompt += f"- Has contractions: {original_analysis.get('has_contractions', False)}\n"

        prompt += f"""
ORIGINAL TEXT:
---
{text}
---

INSTRUCTIONS:
1. Rewrite the text to match the {target_style} style exactly
2. Maintain the original meaning and key information
3. Apply the style characteristics consistently throughout
4. Ensure the tone matches the target style
5. Keep the content length similar to the original

TRANSFORMED TEXT:"""

        return prompt

    def _post_process_transformed_text(self, text: str, target_style: str) -> str:
        """Post-process the transformed text to ensure quality."""
        # Remove any unwanted prefixes or suffixes
        text = text.strip()

        # Remove common LLM response prefixes
        prefixes_to_remove = [
            "Here is the transformed text:",
            "Here's the rewritten text:",
            "Transformed text:",
            "Rewritten text:",
            "The transformed text is:",
        ]

        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()

        # Ensure proper capitalization
        if text and not text[0].isupper():
            text = text[0].upper() + text[1:]

        return text

    def _assess_transformation_quality(self, original: str, transformed: str, target_style: str) -> Dict[str, Any]:
        """Assess the quality of style transformation."""

        # Basic metrics
        original_words = len(original.split())
        transformed_words = len(transformed.split())
        length_ratio = transformed_words / max(original_words, 1)

        # Style consistency check
        transformed_analysis = self._analyze_text_style(transformed)
        style_match = transformed_analysis.get('likely_style') == target_style

        # Calculate quality score
        quality_score = 0.0

        # Length preservation (ideal ratio: 0.8 - 1.2)
        if 0.8 <= length_ratio <= 1.2:
            quality_score += 0.3
        elif 0.6 <= length_ratio <= 1.5:
            quality_score += 0.2
        else:
            quality_score += 0.1

        # Style matching
        if style_match:
            quality_score += 0.4
        else:
            quality_score += 0.2

        # Content preservation (basic check)
        if len(set(original.lower().split()) & set(transformed.lower().split())) > len(original.split()) * 0.3:
            quality_score += 0.3
        else:
            quality_score += 0.1

        return {
            "overall_score": min(quality_score, 1.0),
            "length_ratio": length_ratio,
            "style_match": style_match,
            "original_word_count": original_words,
            "transformed_word_count": transformed_words,
            "assessment": "Excellent" if quality_score >= 0.8 else "Good" if quality_score >= 0.6 else "Fair" if quality_score >= 0.4 else "Poor"
        }

    def _rule_based_style_transformation(self, text: str, target_style: str, style_info: Dict[str, Any]) -> str:
        """Perform basic rule-based style transformation when LLM is not available."""
        import re

        transformed = text

        if target_style == "professional":
            # Convert to professional style
            contractions = {
                "don't": "do not", "won't": "will not", "can't": "cannot",
                "isn't": "is not", "aren't": "are not", "we'll": "we will",
                "you'll": "you will", "I'll": "I will", "it's": "it is"
            }
            for contraction, expansion in contractions.items():
                transformed = re.sub(rf'\b{re.escape(contraction)}\b', expansion, transformed, flags=re.IGNORECASE)

            # Replace casual words
            casual_to_formal = {
                "awesome": "excellent", "cool": "effective", "stuff": "items",
                "things": "elements", "okay": "acceptable", "yeah": "yes"
            }
            for casual, formal in casual_to_formal.items():
                transformed = re.sub(rf'\b{re.escape(casual)}\b', formal, transformed, flags=re.IGNORECASE)

        elif target_style == "casual":
            # Convert to casual style
            expansions = {
                "do not": "don't", "will not": "won't", "cannot": "can't",
                "is not": "isn't", "are not": "aren't", "we will": "we'll"
            }
            for expansion, contraction in expansions.items():
                transformed = re.sub(rf'\b{re.escape(expansion)}\b', contraction, transformed, flags=re.IGNORECASE)

        return f"[Rule-based {target_style} transformation]\n{transformed}"

    def analyze_style(self, text_content: str) -> Dict[str, Any]:
        """Analyze the style characteristics of given text."""
        try:
            analysis = self._analyze_text_style(text_content)

            # Enhanced analysis with style recommendations
            style_recommendations = []

            if analysis["avg_sentence_length"] > 25:
                style_recommendations.append("Consider breaking long sentences for better readability")

            if analysis["has_contractions"] and analysis["formality_indicators"]["formal_words"] > 0:
                style_recommendations.append("Mixed formality detected - consider consistent style")

            if not analysis["has_questions"] and not analysis["has_exclamations"]:
                style_recommendations.append("Text could benefit from more engaging elements")

            return {
                "success": True,
                "style_analysis": analysis,
                "recommendations": style_recommendations,
                "suggested_styles": self._suggest_appropriate_styles(analysis)
            }

        except Exception as e:
            return {"error": f"Error analyzing style: {e}"}

    def suggest_style_improvements(self, text_content: str, current_style: str = None) -> Dict[str, Any]:
        """Suggest specific improvements for the current text style."""
        try:
            analysis = self._analyze_text_style(text_content)
            current_style = current_style or analysis.get("likely_style", "unknown")

            improvements = []

            # Sentence length improvements
            if analysis["avg_sentence_length"] > 30:
                improvements.append({
                    "type": "sentence_length",
                    "issue": "Sentences are too long",
                    "suggestion": "Break complex sentences into shorter, clearer ones",
                    "priority": "high"
                })
            elif analysis["avg_sentence_length"] < 8:
                improvements.append({
                    "type": "sentence_length",
                    "issue": "Sentences are too short",
                    "suggestion": "Combine related short sentences for better flow",
                    "priority": "medium"
                })

            # Style consistency improvements
            if analysis["has_contractions"] and current_style == "professional":
                improvements.append({
                    "type": "formality",
                    "issue": "Contractions in professional text",
                    "suggestion": "Expand contractions (don't → do not)",
                    "priority": "high"
                })

            # Engagement improvements
            if not analysis["has_questions"] and current_style == "casual":
                improvements.append({
                    "type": "engagement",
                    "issue": "Lacks interactive elements",
                    "suggestion": "Add rhetorical questions to engage readers",
                    "priority": "medium"
                })

            return {
                "success": True,
                "current_style": current_style,
                "improvements": improvements,
                "overall_assessment": self._assess_overall_style_quality(analysis)
            }

        except Exception as e:
            return {"error": f"Error suggesting improvements: {e}"}

    def compare_styles(self, text_content: str, styles_to_compare: List[str]) -> Dict[str, Any]:
        """Compare how text would look in different styles."""
        try:
            comparisons = {}
            original_analysis = self._analyze_text_style(text_content)

            for style in styles_to_compare:
                if style in self.enhanced_styles or style in self.styles:
                    # Get a preview of how the text would look in this style
                    transformation_result = self.transform_style(text_content, style)

                    if transformation_result.get("success"):
                        comparisons[style] = {
                            "transformed_preview": transformation_result["rewritten_text"][:200] + "..." if len(transformation_result["rewritten_text"]) > 200 else transformation_result["rewritten_text"],
                            "style_characteristics": self._get_style_info(style).get("characteristics", []),
                            "suitability_score": self._calculate_style_suitability(original_analysis, style)
                        }
                    else:
                        comparisons[style] = {"error": transformation_result.get("error", "Unknown error")}

            return {
                "success": True,
                "original_text_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content,
                "original_style_analysis": original_analysis,
                "style_comparisons": comparisons,
                "recommendations": self._recommend_best_styles(comparisons)
            }

        except Exception as e:
            return {"error": f"Error comparing styles: {e}"}

    def _suggest_appropriate_styles(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest appropriate styles based on text analysis."""
        suggestions = []

        if analysis["formality_indicators"]["formal_words"] > 2:
            suggestions.extend(["professional", "academic"])

        if analysis["formality_indicators"]["technical_words"] > 2:
            suggestions.append("technical")

        if analysis["has_contractions"] or analysis["formality_indicators"]["casual_words"] > 0:
            suggestions.extend(["casual", "creative"])

        if analysis["avg_sentence_length"] > 20:
            suggestions.append("academic")

        return list(set(suggestions)) or ["professional", "casual"]

    def _assess_overall_style_quality(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall style quality."""
        score = 0.0
        issues = []

        # Sentence length assessment
        avg_length = analysis["avg_sentence_length"]
        if 12 <= avg_length <= 20:
            score += 0.3
        elif 8 <= avg_length <= 25:
            score += 0.2
        else:
            score += 0.1
            if avg_length > 25:
                issues.append("Sentences too long")
            else:
                issues.append("Sentences too short")

        # Style consistency
        formal_words = analysis["formality_indicators"]["formal_words"]
        casual_words = analysis["formality_indicators"]["casual_words"]

        if (formal_words > 0 and casual_words == 0) or (casual_words > 0 and formal_words == 0):
            score += 0.4  # Consistent style
        else:
            score += 0.2
            if formal_words > 0 and casual_words > 0:
                issues.append("Mixed formality levels")

        # Engagement elements
        if analysis["has_questions"] or analysis["has_exclamations"]:
            score += 0.3
        else:
            score += 0.1
            issues.append("Lacks engaging elements")

        return {
            "quality_score": min(score, 1.0),
            "assessment": "Excellent" if score >= 0.8 else "Good" if score >= 0.6 else "Fair" if score >= 0.4 else "Poor",
            "issues": issues
        }

    def _calculate_style_suitability(self, text_analysis: Dict[str, Any], target_style: str) -> float:
        """Calculate how suitable a style is for the given text."""
        score = 0.5  # Base score

        current_style = text_analysis.get("likely_style", "neutral")

        # Style compatibility matrix
        compatibility = {
            "professional": {"professional": 1.0, "academic": 0.8, "technical": 0.7, "casual": 0.3, "creative": 0.2, "persuasive": 0.6},
            "casual": {"casual": 1.0, "creative": 0.8, "persuasive": 0.7, "professional": 0.4, "academic": 0.2, "technical": 0.3},
            "technical": {"technical": 1.0, "professional": 0.8, "academic": 0.9, "casual": 0.3, "creative": 0.2, "persuasive": 0.4},
            "academic": {"academic": 1.0, "professional": 0.8, "technical": 0.8, "casual": 0.2, "creative": 0.3, "persuasive": 0.5},
            "neutral": {"professional": 0.7, "casual": 0.7, "technical": 0.6, "academic": 0.6, "creative": 0.6, "persuasive": 0.7}
        }

        if current_style in compatibility and target_style in compatibility[current_style]:
            score = compatibility[current_style][target_style]

        return score

    def _recommend_best_styles(self, comparisons: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend the best styles based on comparisons."""
        recommendations = []

        for style, comparison in comparisons.items():
            if "suitability_score" in comparison:
                recommendations.append({
                    "style": style,
                    "suitability_score": comparison["suitability_score"],
                    "reason": f"Suitability score: {comparison['suitability_score']:.2f}"
                })

        # Sort by suitability score
        recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)

        return recommendations[:3]  # Return top 3 recommendations


# Backward compatibility wrapper
class StyleGeneratorTool(EnhancedStyleGeneratorTool):
    """Backward compatibility wrapper for the enhanced style generator."""

    def execute(self, text_content: str, target_style: str, original_role: str = None) -> dict:
        """Backward compatible execute method."""
        result = self.transform_style(text_content, target_style, original_role)

        if result.get("success"):
            return {"rewritten_text": result["rewritten_text"]}
        else:
            return result