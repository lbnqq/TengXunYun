#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI文风统一核心模块

基于讯飞星火大模型X1的文风统一功能，支持：
- 预设风格文本生成
- Few-Shot风格模仿
- 多语言风格支持
- 风格强度控制

Author: AI Assistant
Created: 2025-01-16
License: MIT
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StyleTransferEngine:
    """AI文风统一引擎"""
    
    def __init__(self, spark_x1_client=None):
        """
        初始化文风统一引擎
        
        Args:
            spark_x1_client: 星火X1客户端实例
        """
        self.spark_x1_client = spark_x1_client
        self.preset_styles = self._load_preset_styles()
        self.supported_languages = ['zh', 'en', 'auto']  # 中文、英文、自动识别
        
        logger.info("✅ StyleTransferEngine初始化成功")
    
    def _load_preset_styles(self) -> Dict[str, Dict[str, Any]]:
        """加载预设风格模板库"""
        return {
            "academic": {
                "name": "学术风格",
                "name_en": "Academic Style",
                "description": "严谨、客观、逻辑性强的学术写作风格",
                "description_en": "Rigorous, objective, and logically structured academic writing style",
                "prompt_template_zh": "请用学术论文的严谨风格来{action}以下内容，要求：1.使用准确的专业术语 2.保持客观中性的语调 3.逻辑结构清晰 4.避免主观色彩",
                "prompt_template_en": "Please {action} the following content in a rigorous academic style: 1.Use precise professional terminology 2.Maintain objective and neutral tone 3.Clear logical structure 4.Avoid subjective coloring",
                "parameters": {"temperature": 0.3},
                "examples_zh": [
                    "研究表明，该方法在处理复杂数据时具有显著优势。",
                    "基于实验结果，我们可以得出以下结论..."
                ],
                "examples_en": [
                    "Research indicates that this method demonstrates significant advantages in processing complex data.",
                    "Based on experimental results, we can draw the following conclusions..."
                ]
            },
            "business": {
                "name": "商务风格",
                "name_en": "Business Style", 
                "description": "专业、正式的商务沟通风格",
                "description_en": "Professional and formal business communication style",
                "prompt_template_zh": "请用正式的商务语言来{action}以下内容，要求：1.语言简洁明了 2.态度专业礼貌 3.重点突出 4.便于理解和执行",
                "prompt_template_en": "Please {action} the following content in formal business language: 1.Concise and clear language 2.Professional and polite attitude 3.Highlight key points 4.Easy to understand and execute",
                "parameters": {"temperature": 0.5},
                "examples_zh": [
                    "感谢您的来信。经过仔细考虑，我们决定采纳您的建议。",
                    "为了提高工作效率，建议实施以下措施..."
                ],
                "examples_en": [
                    "Thank you for your letter. After careful consideration, we have decided to adopt your suggestion.",
                    "To improve work efficiency, we recommend implementing the following measures..."
                ]
            },
            "humorous": {
                "name": "幽默风格",
                "name_en": "Humorous Style",
                "description": "轻松幽默、生动有趣的表达风格",
                "description_en": "Light-hearted, humorous, and engaging expression style",
                "prompt_template_zh": "请用轻松幽默的语言来{action}以下内容，要求：1.语言生动有趣 2.适当使用比喻和俏皮话 3.保持内容的准确性 4.让读者感到轻松愉快",
                "prompt_template_en": "Please {action} the following content in a light and humorous language: 1.Vivid and interesting language 2.Appropriate use of metaphors and witty remarks 3.Maintain content accuracy 4.Make readers feel relaxed and happy",
                "parameters": {"temperature": 0.8},
                "examples_zh": [
                    "这个问题就像打结的耳机线，看起来复杂，其实只要找对方法就能轻松解开。",
                    "别担心，这比学会用筷子吃意大利面还要简单！"
                ],
                "examples_en": [
                    "This problem is like tangled headphone wires - looks complicated, but easy to solve once you find the right method.",
                    "Don't worry, this is easier than learning to eat spaghetti with chopsticks!"
                ]
            },
            "child_friendly": {
                "name": "儿童友好",
                "name_en": "Child-Friendly Style",
                "description": "简单易懂、生动活泼的儿童语言风格",
                "description_en": "Simple, understandable, and lively language style for children",
                "prompt_template_zh": "请用儿童容易理解的语言来{action}以下内容，要求：1.使用简单的词汇 2.句子短小易懂 3.多用比喻和故事 4.语调亲切友好",
                "prompt_template_en": "Please {action} the following content in language that children can easily understand: 1.Use simple vocabulary 2.Short and easy sentences 3.Use metaphors and stories 4.Friendly and kind tone",
                "parameters": {"temperature": 0.7},
                "examples_zh": [
                    "你知道吗？电脑就像一个很聪明的朋友，它能帮我们做很多事情！",
                    "学习新知识就像收集宝石一样，每学会一样东西，你就得到了一颗闪亮的宝石！"
                ],
                "examples_en": [
                    "Do you know? A computer is like a very smart friend that can help us do many things!",
                    "Learning new knowledge is like collecting gems - every time you learn something, you get a shiny gem!"
                ]
            },
            "technical": {
                "name": "技术文档",
                "name_en": "Technical Documentation",
                "description": "准确、详细的技术说明文档风格",
                "description_en": "Accurate and detailed technical documentation style",
                "prompt_template_zh": "请用技术文档的规范格式来{action}以下内容，要求：1.术语准确专业 2.步骤清晰详细 3.包含必要的注意事项 4.便于技术人员理解和操作",
                "prompt_template_en": "Please {action} the following content in standard technical documentation format: 1.Accurate professional terminology 2.Clear and detailed steps 3.Include necessary precautions 4.Easy for technical personnel to understand and operate",
                "parameters": {"temperature": 0.2},
                "examples_zh": [
                    "步骤1：打开配置文件config.yaml，修改以下参数...",
                    "注意：在执行此操作前，请确保已备份相关数据。"
                ],
                "examples_en": [
                    "Step 1: Open the configuration file config.yaml and modify the following parameters...",
                    "Note: Please ensure relevant data is backed up before performing this operation."
                ]
            },
            "creative": {
                "name": "创意文案",
                "name_en": "Creative Writing",
                "description": "富有创意、吸引眼球的文案写作风格",
                "description_en": "Creative and eye-catching copywriting style",
                "prompt_template_zh": "请用富有创意的文案风格来{action}以下内容，要求：1.语言新颖独特 2.富有感染力 3.能够吸引读者注意 4.保持内容的核心信息",
                "prompt_template_en": "Please {action} the following content in a creative copywriting style: 1.Novel and unique language 2.Highly engaging 3.Attract reader attention 4.Maintain core information",
                "parameters": {"temperature": 0.9},
                "examples_zh": [
                    "不是所有的改变都叫进步，但所有的进步都始于改变。",
                    "在这个快节奏的世界里，我们为您按下了'慢'键。"
                ],
                "examples_en": [
                    "Not all changes are progress, but all progress begins with change.",
                    "In this fast-paced world, we've pressed the 'slow' button for you."
                ]
            }
        }
    
    def detect_language(self, text: str) -> str:
        """
        自动检测文本语言
        
        Args:
            text: 输入文本
            
        Returns:
            语言代码 ('zh' 或 'en')
        """
        # 简单的语言检测逻辑
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if chinese_chars > english_chars:
            return 'zh'
        elif english_chars > chinese_chars:
            return 'en'
        else:
            # 默认返回中文
            return 'zh'

    def get_preset_styles(self, language: str = 'auto') -> Dict[str, Dict[str, Any]]:
        """
        获取预设风格模板库

        Args:
            language: 语言代码 ('zh', 'en', 'auto')

        Returns:
            预设风格字典
        """
        if language == 'auto':
            # 返回完整的多语言风格库
            return self.preset_styles

        # 根据语言过滤返回相应的风格信息
        filtered_styles = {}
        for style_id, style_info in self.preset_styles.items():
            if language == 'zh':
                filtered_styles[style_id] = {
                    'name': style_info['name'],
                    'description': style_info['description'],
                    'parameters': style_info['parameters'],
                    'examples': style_info['examples_zh']
                }
            elif language == 'en':
                filtered_styles[style_id] = {
                    'name': style_info['name_en'],
                    'description': style_info['description_en'],
                    'parameters': style_info['parameters'],
                    'examples': style_info['examples_en']
                }

        return filtered_styles

    def generate_with_style(self, content: str, style_id: str, action: str = "重写",
                          language: str = 'auto', temperature: Optional[float] = None,
                          user_id: str = "user_style_transfer") -> Dict[str, Any]:
        """
        基于指定风格生成文本（核心方法）

        Args:
            content: 原始内容
            style_id: 风格ID
            action: 操作类型（重写、改写、润色等）
            language: 语言代码
            temperature: 温度参数（覆盖默认值）
            user_id: 用户ID

        Returns:
            生成结果字典
        """
        try:
            # 检查风格是否存在
            if style_id not in self.preset_styles:
                raise ValueError(f"不支持的风格ID: {style_id}")

            # 自动检测语言
            if language == 'auto':
                language = self.detect_language(content)

            # 获取风格配置
            style_config = self.preset_styles[style_id]

            # 构建提示词
            if language == 'zh':
                prompt_template = style_config['prompt_template_zh']
            else:
                prompt_template = style_config['prompt_template_en']

            prompt_instruction = prompt_template.format(action=action) + f"\n\n原文内容：\n{content}"

            # 设置温度参数
            if temperature is None:
                temperature = style_config['parameters']['temperature']

            # 调用星火X1 API
            if self.spark_x1_client:
                result = self.spark_x1_client.format_text(
                    instruction=prompt_instruction,
                    content="",  # 内容已包含在instruction中
                    temperature=temperature,
                    max_tokens=3000,
                    timeout=60
                )

                return {
                    'success': True,
                    'generated_content': result,
                    'style_id': style_id,
                    'style_name': style_config['name'] if language == 'zh' else style_config['name_en'],
                    'language': language,
                    'temperature': temperature,
                    'original_content': content,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("星火X1客户端未初始化")

        except Exception as e:
            logger.error(f"文风生成失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'style_id': style_id,
                'original_content': content
            }

    def few_shot_style_transfer(self, content: str, reference_examples: List[str],
                              target_description: str = "", language: str = 'auto',
                              temperature: float = 0.7) -> Dict[str, Any]:
        """
        Few-Shot风格迁移

        Args:
            content: 要转换的内容
            reference_examples: 参考示例列表
            target_description: 目标风格描述
            language: 语言代码
            temperature: 温度参数

        Returns:
            转换结果字典
        """
        try:
            # 自动检测语言
            if language == 'auto':
                language = self.detect_language(content)

            # 构建Few-Shot提示词
            if language == 'zh':
                prompt_instruction = f"请参考以下示例的写作风格，将给定内容转换为相同的风格。\n\n"
                if target_description:
                    prompt_instruction += f"目标风格描述：{target_description}\n\n"
                prompt_instruction += "参考示例：\n"
                for i, example in enumerate(reference_examples, 1):
                    prompt_instruction += f"示例{i}：{example}\n"
                prompt_instruction += f"\n请将以下内容转换为上述示例的风格：\n{content}"
            else:
                prompt_instruction = f"Please refer to the writing style of the following examples and convert the given content to the same style.\n\n"
                if target_description:
                    prompt_instruction += f"Target style description: {target_description}\n\n"
                prompt_instruction += "Reference examples:\n"
                for i, example in enumerate(reference_examples, 1):
                    prompt_instruction += f"Example {i}: {example}\n"
                prompt_instruction += f"\nPlease convert the following content to the style of the above examples:\n{content}"

            # 调用星火X1 API
            if self.spark_x1_client:
                result = self.spark_x1_client.format_text(
                    instruction=prompt_instruction,
                    content="",
                    temperature=temperature,
                    max_tokens=3000,
                    timeout=60
                )

                return {
                    'success': True,
                    'generated_content': result,
                    'method': 'few_shot',
                    'reference_count': len(reference_examples),
                    'language': language,
                    'temperature': temperature,
                    'original_content': content,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("星火X1客户端未初始化")

        except Exception as e:
            logger.error(f"Few-Shot风格迁移失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': 'few_shot',
                'original_content': content
            }

    def extract_style_from_document(self, document_content: str, language: str = 'auto') -> Dict[str, Any]:
        """
        从参考文档中提取风格特征

        Args:
            document_content: 文档内容
            language: 语言代码

        Returns:
            风格特征字典
        """
        try:
            # 自动检测语言
            if language == 'auto':
                language = self.detect_language(document_content)

            # 构建风格分析提示词
            if language == 'zh':
                analysis_prompt = """请分析以下文档的写作风格特征，包括：
1. 语言风格（正式/非正式、严谨/轻松等）
2. 句式特点（长短句比例、复杂度等）
3. 词汇选择（专业术语、口语化程度等）
4. 表达方式（直接/委婉、客观/主观等）
5. 整体语调和情感色彩

请提供详细的风格分析报告：

文档内容：
""" + document_content
            else:
                analysis_prompt = """Please analyze the writing style characteristics of the following document, including:
1. Language style (formal/informal, rigorous/casual, etc.)
2. Sentence patterns (ratio of long/short sentences, complexity, etc.)
3. Vocabulary choice (technical terms, colloquial level, etc.)
4. Expression methods (direct/indirect, objective/subjective, etc.)
5. Overall tone and emotional coloring

Please provide a detailed style analysis report:

Document content:
""" + document_content

            # 调用星火X1进行风格分析
            if self.spark_x1_client:
                analysis_result = self.spark_x1_client.format_text(
                    instruction=analysis_prompt,
                    content="",
                    temperature=0.3,  # 使用较低温度确保分析的一致性
                    max_tokens=2000,
                    timeout=60
                )

                return {
                    'success': True,
                    'style_analysis': analysis_result,
                    'document_length': len(document_content),
                    'language': language,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("星火X1客户端未初始化")

        except Exception as e:
            logger.error(f"风格提取失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'document_length': len(document_content) if document_content else 0
            }

    def validate_style_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        验证风格提示词的有效性

        Args:
            prompt: 风格提示词

        Returns:
            验证结果字典
        """
        validation_result = {
            'is_valid': True,
            'issues': [],
            'suggestions': []
        }

        # 检查提示词长度
        if len(prompt.strip()) < 10:
            validation_result['is_valid'] = False
            validation_result['issues'].append("提示词过短，可能无法有效指导风格转换")
            validation_result['suggestions'].append("请提供更详细的风格描述")

        if len(prompt) > 1000:
            validation_result['issues'].append("提示词过长，可能影响处理效率")
            validation_result['suggestions'].append("建议简化提示词，突出关键风格要求")

        # 检查是否包含风格相关关键词
        style_keywords = ['风格', '语调', '表达', '写作', '语言', 'style', 'tone', 'writing', 'language']
        has_style_keywords = any(keyword in prompt.lower() for keyword in style_keywords)

        if not has_style_keywords:
            validation_result['issues'].append("提示词中缺少明确的风格指导")
            validation_result['suggestions'].append("建议添加具体的风格要求，如'正式'、'幽默'、'学术'等")

        return validation_result

    def get_style_comparison(self, original: str, styled: str, style_id: str) -> Dict[str, Any]:
        """
        生成原文与风格化文本的对比分析

        Args:
            original: 原始文本
            styled: 风格化文本
            style_id: 使用的风格ID

        Returns:
            对比分析结果
        """
        try:
            style_info = self.preset_styles.get(style_id, {})

            comparison = {
                'original_length': len(original),
                'styled_length': len(styled),
                'length_change_ratio': len(styled) / len(original) if len(original) > 0 else 0,
                'style_applied': style_info.get('name', style_id),
                'style_description': style_info.get('description', ''),
                'changes_summary': self._analyze_text_changes(original, styled),
                'timestamp': datetime.now().isoformat()
            }

            return comparison

        except Exception as e:
            logger.error(f"风格对比分析失败: {str(e)}")
            return {
                'error': str(e),
                'original_length': len(original) if original else 0,
                'styled_length': len(styled) if styled else 0
            }

    def _analyze_text_changes(self, original: str, styled: str) -> Dict[str, Any]:
        """
        分析文本变化

        Args:
            original: 原始文本
            styled: 风格化文本

        Returns:
            变化分析结果
        """
        # 简单的文本变化分析
        original_sentences = len(re.split(r'[.!?。！？]', original))
        styled_sentences = len(re.split(r'[.!?。！？]', styled))

        original_words = len(re.findall(r'\b\w+\b', original)) + len(re.findall(r'[\u4e00-\u9fff]', original))
        styled_words = len(re.findall(r'\b\w+\b', styled)) + len(re.findall(r'[\u4e00-\u9fff]', styled))

        return {
            'sentence_count_change': styled_sentences - original_sentences,
            'word_count_change': styled_words - original_words,
            'avg_sentence_length_original': original_words / original_sentences if original_sentences > 0 else 0,
            'avg_sentence_length_styled': styled_words / styled_sentences if styled_sentences > 0 else 0
        }
