import re
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from .base_tool import BaseTool

class EnhancedContentGeneratorTool(BaseTool):
    """
    Enhanced content generation and optimization engine.
    Features:
    - Intelligent content filling with context awareness
    - Style transfer and adaptation
    - Content optimization and enhancement
    - Template matching and selection
    - Context consistency guarantee
    - Multi-format support
    """

    def __init__(self, llm_client=None, **kwargs):
        super().__init__(**kwargs)
        self.llm_client = llm_client

        # Initialize style profiles
        self.style_profiles = {
            "formal": {
                "tone": "professional and authoritative",
                "vocabulary": "sophisticated and precise",
                "sentence_structure": "complex and well-structured",
                "patterns": ["hereby", "pursuant to", "in accordance with", "furthermore", "consequently"],
                "avoid": ["contractions", "colloquialisms", "casual expressions"]
            },
            "semi_formal": {
                "tone": "professional but approachable",
                "vocabulary": "clear and accessible",
                "sentence_structure": "balanced complexity",
                "patterns": ["we recommend", "please note", "it is important", "consider", "ensure"],
                "avoid": ["overly casual language", "slang"]
            },
            "informal": {
                "tone": "conversational and friendly",
                "vocabulary": "simple and relatable",
                "sentence_structure": "varied and natural",
                "patterns": ["let's", "we'll", "you can", "here's", "that's"],
                "avoid": ["overly complex terms", "bureaucratic language"]
            },
            "technical": {
                "tone": "precise and objective",
                "vocabulary": "domain-specific and accurate",
                "sentence_structure": "clear and logical",
                "patterns": ["implementation", "methodology", "analysis", "optimization", "framework"],
                "avoid": ["ambiguous terms", "emotional language"]
            },
            "persuasive": {
                "tone": "compelling and confident",
                "vocabulary": "impactful and engaging",
                "sentence_structure": "varied for emphasis",
                "patterns": ["proven", "innovative", "significant", "essential", "transform"],
                "avoid": ["weak qualifiers", "uncertain language"]
            }
        }

        # Content templates for different scenarios
        self.content_templates = {
            "executive_summary": {
                "structure": ["overview", "key_findings", "recommendations", "next_steps"],
                "length": "concise",
                "style": "formal"
            },
            "technical_section": {
                "structure": ["background", "methodology", "implementation", "results"],
                "length": "detailed",
                "style": "technical"
            },
            "product_description": {
                "structure": ["overview", "features", "benefits", "use_cases"],
                "length": "moderate",
                "style": "persuasive"
            },
            "meeting_summary": {
                "structure": ["attendees", "agenda", "discussions", "decisions", "action_items"],
                "length": "structured",
                "style": "semi_formal"
            }
        }

        # Placeholder patterns
        self.placeholder_patterns = [
            r'\{\{([^}]+)\}\}',  # {{variable}}
            r'\[([^\]]+)\]',     # [placeholder]
            r'<([^>]+)>',        # <placeholder>
            r'\$\{([^}]+)\}',    # ${variable}
        ]

    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute content generation operation.

        Args:
            operation: Type of operation (fill_template, optimize_content, transfer_style, etc.)
            **kwargs: Operation-specific parameters
        """
        try:
            if operation == "fill_template":
                return self.fill_template(**kwargs)
            elif operation == "optimize_content":
                return self.optimize_content(**kwargs)
            elif operation == "transfer_style":
                return self.transfer_style(**kwargs)
            elif operation == "generate_content":
                return self.generate_content(**kwargs)
            elif operation == "enhance_structure":
                return self.enhance_structure(**kwargs)
            elif operation == "ensure_consistency":
                return self.ensure_consistency(**kwargs)
            else:
                return {"error": f"Unknown operation: {operation}"}
        except Exception as e:
            return {"error": f"Error in content generation: {e}"}

    def fill_template(self, template_content: str, data: Dict[str, Any],
                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Intelligent template filling with context awareness.

        Args:
            template_content: Template text with placeholders
            data: Data to fill into template
            context: Additional context for intelligent filling
        """
        try:
            filled_content = template_content
            placeholders_found = []
            placeholders_filled = []

            # Find all placeholders
            for pattern in self.placeholder_patterns:
                matches = re.finditer(pattern, template_content)
                for match in matches:
                    placeholder = match.group(1).strip()
                    placeholders_found.append({
                        "placeholder": placeholder,
                        "full_match": match.group(0),
                        "start": match.start(),
                        "end": match.end()
                    })

            # Fill placeholders with intelligent content generation
            for placeholder_info in placeholders_found:
                placeholder = placeholder_info["placeholder"]
                full_match = placeholder_info["full_match"]

                # Try direct data mapping first
                if placeholder in data:
                    replacement = str(data[placeholder])
                    placeholders_filled.append({
                        "placeholder": placeholder,
                        "value": replacement,
                        "method": "direct_mapping"
                    })
                else:
                    # Intelligent content generation
                    replacement = self._generate_placeholder_content(
                        placeholder, data, context, template_content
                    )
                    placeholders_filled.append({
                        "placeholder": placeholder,
                        "value": replacement,
                        "method": "intelligent_generation"
                    })

                # Replace in content
                filled_content = filled_content.replace(full_match, replacement)

            # Post-process for consistency
            filled_content = self._ensure_content_consistency(filled_content, context)

            return {
                "success": True,
                "filled_content": filled_content,
                "placeholders_found": len(placeholders_found),
                "placeholders_filled": placeholders_filled,
                "processing_metadata": {
                    "template_length": len(template_content),
                    "filled_length": len(filled_content),
                    "fill_ratio": len(placeholders_filled) / max(len(placeholders_found), 1)
                }
            }

        except Exception as e:
            return {"error": f"Error filling template: {e}"}

    def _generate_placeholder_content(self, placeholder: str, data: Dict[str, Any],
                                    context: Dict[str, Any], template: str) -> str:
        """Generate intelligent content for placeholders."""

        placeholder_lower = placeholder.lower()

        # Date/time placeholders
        if any(keyword in placeholder_lower for keyword in ['date', 'time', 'timestamp']):
            if 'current' in placeholder_lower or 'today' in placeholder_lower:
                return datetime.now().strftime("%Y-%m-%d")
            elif 'year' in placeholder_lower:
                return str(datetime.now().year)
            else:
                return datetime.now().strftime("%Y-%m-%d %H:%M")

        # Author/user placeholders
        if any(keyword in placeholder_lower for keyword in ['author', 'user', 'name', 'creator']):
            return data.get('author', data.get('user_name', data.get('name', 'Document Author')))

        # Company/organization placeholders
        if any(keyword in placeholder_lower for keyword in ['company', 'organization', 'org']):
            return data.get('company', data.get('organization', 'Organization Name'))

        # Version/revision placeholders
        if any(keyword in placeholder_lower for keyword in ['version', 'revision', 'ver']):
            return data.get('version', '1.0')

        # Status placeholders
        if 'status' in placeholder_lower:
            return data.get('status', 'In Progress')

        # Priority placeholders
        if 'priority' in placeholder_lower:
            return data.get('priority', 'Medium')

        # Use LLM for complex content generation
        if self.llm_client and context:
            return self._llm_generate_content(placeholder, data, context, template)

        # Fallback to placeholder name
        return f"[{placeholder}]"

    def _llm_generate_content(self, placeholder: str, data: Dict[str, Any],
                            context: Dict[str, Any], template: str) -> str:
        """Use LLM to generate contextual content for placeholders."""

        prompt = f"""
        You are a professional content writer. Generate appropriate content for the placeholder "{placeholder}"
        in the following context:

        Template Context:
        {template[:500]}...

        Available Data:
        {json.dumps(data, indent=2)}

        Document Context:
        - Document Type: {context.get('document_type', 'Unknown')}
        - Target Audience: {context.get('target_audience', 'General')}
        - Style: {context.get('style', 'Professional')}

        Generate concise, appropriate content for this placeholder. Return only the content, no explanations.
        """

        try:
            response = self.llm_client.generate(prompt)
            return response.strip()
        except Exception:
            return f"[Generated content for {placeholder}]"

    def optimize_content(self, content: str, optimization_goals: List[str],
                        context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optimize content based on specified goals.

        Args:
            content: Original content to optimize
            optimization_goals: List of goals (clarity, conciseness, engagement, etc.)
            context: Additional context for optimization
        """
        try:
            optimized_content = content
            optimizations_applied = []

            for goal in optimization_goals:
                if goal == "clarity":
                    optimized_content, changes = self._optimize_for_clarity(optimized_content)
                    optimizations_applied.extend(changes)
                elif goal == "conciseness":
                    optimized_content, changes = self._optimize_for_conciseness(optimized_content)
                    optimizations_applied.extend(changes)
                elif goal == "engagement":
                    optimized_content, changes = self._optimize_for_engagement(optimized_content)
                    optimizations_applied.extend(changes)
                elif goal == "professionalism":
                    optimized_content, changes = self._optimize_for_professionalism(optimized_content)
                    optimizations_applied.extend(changes)
                elif goal == "readability":
                    optimized_content, changes = self._optimize_for_readability(optimized_content)
                    optimizations_applied.extend(changes)

            # Calculate improvement metrics
            improvement_metrics = self._calculate_improvement_metrics(content, optimized_content)

            return {
                "success": True,
                "optimized_content": optimized_content,
                "optimizations_applied": optimizations_applied,
                "improvement_metrics": improvement_metrics,
                "original_length": len(content),
                "optimized_length": len(optimized_content)
            }

        except Exception as e:
            return {"error": f"Error optimizing content: {e}"}

    def transfer_style(self, content: str, target_style: str,
                      source_style: str = None) -> Dict[str, Any]:
        """
        Transfer content from one style to another.

        Args:
            content: Original content
            target_style: Target style (formal, informal, technical, etc.)
            source_style: Source style (auto-detected if None)
        """
        try:
            if target_style not in self.style_profiles:
                return {"error": f"Unknown target style: {target_style}"}

            # Detect source style if not provided
            if source_style is None:
                source_style = self._detect_content_style(content)

            # If styles are the same, return original
            if source_style == target_style:
                return {
                    "success": True,
                    "transferred_content": content,
                    "style_changes": [],
                    "source_style": source_style,
                    "target_style": target_style,
                    "transfer_confidence": 1.0  # Same style, perfect confidence
                }

            # Perform style transfer
            transferred_content, style_changes = self._perform_style_transfer(
                content, source_style, target_style
            )

            return {
                "success": True,
                "transferred_content": transferred_content,
                "style_changes": style_changes,
                "source_style": source_style,
                "target_style": target_style,
                "transfer_confidence": self._calculate_transfer_confidence(style_changes)
            }

        except Exception as e:
            return {"error": f"Error transferring style: {e}"}

    def _optimize_for_clarity(self, content: str) -> Tuple[str, List[str]]:
        """Optimize content for clarity."""
        optimized = content
        changes = []

        # Replace complex words with simpler alternatives
        clarity_replacements = {
            r'\butilize\b': 'use',
            r'\bfacilitate\b': 'help',
            r'\bdemonstrate\b': 'show',
            r'\baccommodate\b': 'fit',
            r'\binitiate\b': 'start',
            r'\bterminate\b': 'end',
            r'\bsubsequent\b': 'next',
            r'\bprior to\b': 'before',
            r'\bin order to\b': 'to'
        }

        for pattern, replacement in clarity_replacements.items():
            if re.search(pattern, optimized, re.IGNORECASE):
                optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
                changes.append(f"Simplified '{pattern}' to '{replacement}'")

        # Break long sentences
        sentences = re.split(r'[.!?]', optimized)
        improved_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 150:  # Long sentence
                # Try to split on conjunctions
                if ' and ' in sentence or ' but ' in sentence or ' however ' in sentence:
                    # Split and create multiple sentences
                    parts = re.split(r'\s+(and|but|however)\s+', sentence)
                    if len(parts) > 1:
                        improved_sentences.append(parts[0].strip())
                        for i in range(1, len(parts), 2):
                            if i + 1 < len(parts):
                                improved_sentences.append(parts[i + 1].strip())
                        changes.append("Split long sentence for clarity")
                    else:
                        improved_sentences.append(sentence)
                else:
                    improved_sentences.append(sentence)
            else:
                improved_sentences.append(sentence)

        optimized = '. '.join([s for s in improved_sentences if s])

        return optimized, changes

    def _optimize_for_conciseness(self, content: str) -> Tuple[str, List[str]]:
        """Optimize content for conciseness."""
        optimized = content
        changes = []

        # Remove redundant phrases
        redundant_patterns = [
            (r'\bin order to\b', 'to'),
            (r'\bdue to the fact that\b', 'because'),
            (r'\bat this point in time\b', 'now'),
            (r'\bfor the purpose of\b', 'to'),
            (r'\bin the event that\b', 'if'),
            (r'\bwith regard to\b', 'about'),
            (r'\bit is important to note that\b', ''),
            (r'\bit should be mentioned that\b', ''),
            (r'\bplease be aware that\b', ''),
        ]

        for pattern, replacement in redundant_patterns:
            if re.search(pattern, optimized, re.IGNORECASE):
                optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
                changes.append(f"Removed redundant phrase: {pattern}")

        # Remove filler words
        filler_words = [r'\bvery\b', r'\breally\b', r'\bquite\b', r'\brather\b', r'\bsomewhat\b']
        for filler in filler_words:
            if re.search(filler, optimized, re.IGNORECASE):
                optimized = re.sub(filler, '', optimized, flags=re.IGNORECASE)
                changes.append(f"Removed filler word: {filler}")

        # Clean up extra spaces
        optimized = re.sub(r'\s+', ' ', optimized).strip()

        return optimized, changes

    def _optimize_for_engagement(self, content: str) -> Tuple[str, List[str]]:
        """Optimize content for engagement."""
        optimized = content
        changes = []

        # Add engaging transitions
        engagement_patterns = [
            (r'^([A-Z][^.!?]*[.!?])', r'\1 This is particularly important because'),
            (r'\bHowever,', 'On the other hand,'),
            (r'\bTherefore,', 'As a result,'),
        ]

        for pattern, replacement in engagement_patterns:
            if re.search(pattern, optimized):
                optimized = re.sub(pattern, replacement, optimized)
                changes.append(f"Enhanced engagement with transition")

        return optimized, changes

    def _optimize_for_professionalism(self, content: str) -> Tuple[str, List[str]]:
        """Optimize content for professionalism."""
        optimized = content
        changes = []

        # Replace casual language
        professional_replacements = {
            r'\bguys\b': 'team members',
            r'\bawesome\b': 'excellent',
            r'\bcool\b': 'effective',
            r'\bstuff\b': 'items',
            r'\bthings\b': 'elements',
            r'\bokay\b': 'acceptable',
            r'\bOK\b': 'acceptable'
        }

        for pattern, replacement in professional_replacements.items():
            if re.search(pattern, optimized, re.IGNORECASE):
                optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
                changes.append(f"Professionalized: {pattern} → {replacement}")

        return optimized, changes

    def _optimize_for_readability(self, content: str) -> Tuple[str, List[str]]:
        """Optimize content for readability."""
        optimized = content
        changes = []

        # Add paragraph breaks for long text blocks
        sentences = re.split(r'[.!?]', optimized)
        if len(sentences) > 6:  # Long paragraph
            # Insert paragraph breaks every 3-4 sentences
            new_sentences = []
            for i, sentence in enumerate(sentences):
                new_sentences.append(sentence.strip())
                if (i + 1) % 4 == 0 and i < len(sentences) - 1:
                    new_sentences.append('\n\n')
            optimized = '. '.join([s for s in new_sentences if s and s != '\n\n'])
            optimized = optimized.replace('. \n\n', '.\n\n')
            changes.append("Added paragraph breaks for readability")

        return optimized, changes

    def _detect_content_style(self, content: str) -> str:
        """Detect the style of content."""
        content_lower = content.lower()

        # Count style indicators
        style_scores = {}
        for style, profile in self.style_profiles.items():
            score = 0
            for pattern in profile.get("patterns", []):
                score += len(re.findall(pattern.lower(), content_lower))
            style_scores[style] = score

        # Return style with highest score
        if style_scores:
            return max(style_scores.items(), key=lambda x: x[1])[0]
        return "neutral"

    def _perform_style_transfer(self, content: str, source_style: str,
                              target_style: str) -> Tuple[str, List[str]]:
        """Perform actual style transfer."""
        transferred = content
        changes = []

        source_profile = self.style_profiles.get(source_style, {})
        target_profile = self.style_profiles.get(target_style, {})

        # Remove source style patterns
        source_patterns = source_profile.get("patterns", [])
        for pattern in source_patterns:
            if pattern in transferred.lower():
                changes.append(f"Removed source style pattern: {pattern}")

        # Apply target style patterns
        target_patterns = target_profile.get("patterns", [])

        # Simple style transfer rules
        if target_style == "formal":
            # Convert contractions
            contractions = {
                "don't": "do not",
                "won't": "will not",
                "can't": "cannot",
                "isn't": "is not",
                "aren't": "are not",
                "we'll": "we will",
                "you'll": "you will"
            }
            for contraction, expansion in contractions.items():
                if contraction in transferred:
                    transferred = transferred.replace(contraction, expansion)
                    changes.append(f"Expanded contraction: {contraction} → {expansion}")

        elif target_style == "informal":
            # Add contractions where appropriate
            expansions = {
                "do not": "don't",
                "will not": "won't",
                "cannot": "can't",
                "is not": "isn't",
                "are not": "aren't"
            }
            for expansion, contraction in expansions.items():
                if expansion in transferred:
                    transferred = transferred.replace(expansion, contraction)
                    changes.append(f"Added contraction: {expansion} → {contraction}")

        return transferred, changes

    def _calculate_transfer_confidence(self, style_changes: List[str]) -> float:
        """Calculate confidence in style transfer."""
        if not style_changes:
            return 0.5  # No changes made

        # More changes generally indicate higher confidence
        confidence = min(len(style_changes) / 10, 1.0)
        return confidence

    def _calculate_improvement_metrics(self, original: str, optimized: str) -> Dict[str, Any]:
        """Calculate improvement metrics."""
        return {
            "length_reduction": len(original) - len(optimized),
            "length_reduction_percent": ((len(original) - len(optimized)) / len(original)) * 100 if original else 0,
            "sentence_count_original": len(re.split(r'[.!?]', original)),
            "sentence_count_optimized": len(re.split(r'[.!?]', optimized)),
            "word_count_original": len(original.split()),
            "word_count_optimized": len(optimized.split())
        }

    def _ensure_content_consistency(self, content: str, context: Dict[str, Any]) -> str:
        """Ensure content consistency throughout the document."""
        if not context:
            return content

        # Ensure consistent terminology
        terminology = context.get("terminology", {})
        for term, preferred in terminology.items():
            content = re.sub(rf'\b{re.escape(term)}\b', preferred, content, flags=re.IGNORECASE)

        # Ensure consistent formatting
        # Standardize date formats
        content = re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', r'\3-\1-\2', content)

        # Standardize number formats
        content = re.sub(r'\b(\d+),(\d{3})\b', r'\1,\2', content)

        return content

    def generate_content(self, content_type: str, parameters: Dict[str, Any],
                        context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate new content based on type and parameters."""
        try:
            if content_type in self.content_templates:
                template = self.content_templates[content_type]
                generated_content = self._generate_from_template(template, parameters, context)
            else:
                generated_content = self._generate_custom_content(content_type, parameters, context)

            return {
                "success": True,
                "generated_content": generated_content,
                "content_type": content_type,
                "generation_metadata": {
                    "parameters_used": list(parameters.keys()),
                    "content_length": len(generated_content),
                    "generation_method": "template" if content_type in self.content_templates else "custom"
                }
            }

        except Exception as e:
            return {"error": f"Error generating content: {e}"}

    def _generate_from_template(self, template: Dict[str, Any],
                              parameters: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate content from predefined template."""
        structure = template.get("structure", [])
        style = template.get("style", "neutral")

        sections = []
        for section_type in structure:
            section_content = self._generate_section_content(section_type, parameters, context)
            sections.append(f"## {section_type.title()}\n\n{section_content}")

        return "\n\n".join(sections)

    def _generate_section_content(self, section_type: str,
                                parameters: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate content for a specific section type."""
        # This would typically use the LLM for more sophisticated generation
        section_templates = {
            "overview": "This section provides an overview of {topic}.",
            "key_findings": "The key findings include: {findings}",
            "recommendations": "Based on the analysis, we recommend: {recommendations}",
            "next_steps": "The next steps are: {next_steps}",
            "background": "Background information: {background}",
            "methodology": "The methodology used: {methodology}",
            "implementation": "Implementation details: {implementation}",
            "results": "Results obtained: {results}"
        }

        template = section_templates.get(section_type, f"Content for {section_type}: {{content}}")

        # Fill with available parameters
        try:
            return template.format(**parameters)
        except KeyError:
            return template.format(content=parameters.get("content", "To be determined"))

    def _generate_custom_content(self, content_type: str,
                               parameters: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate custom content using LLM if available."""
        if self.llm_client:
            prompt = f"""
            Generate {content_type} content with the following parameters:
            {json.dumps(parameters, indent=2)}

            Context: {json.dumps(context, indent=2) if context else 'None'}

            Generate professional, well-structured content appropriate for the specified type.
            """
            try:
                return self.llm_client.generate(prompt)
            except Exception:
                pass

        return f"Generated {content_type} content based on provided parameters."


# Backward compatibility wrapper
class ContentFillerTool(EnhancedContentGeneratorTool):
    """Backward compatibility wrapper for the enhanced content generator."""

    def execute(self, template_path: str, data: dict, output_path: str):
        """Backward compatible execute method."""
        try:
            # Read template if it's a file path
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            else:
                template_content = template_path  # Assume it's template content

            # Fill template
            result = self.fill_template(template_content, data)

            if result.get("success"):
                # Write to output file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result["filled_content"])

                return {
                    "success": True,
                    "message": f"Template filled and saved to {output_path}",
                    "placeholders_filled": result.get("placeholders_filled", 0)
                }
            else:
                return result

        except Exception as e:
            return {"error": f"Error in content filling: {e}"}