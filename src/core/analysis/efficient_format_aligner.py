"""
高效格式对齐器 - 基于结构映射的格式对齐架构

核心思想：
1. 结构解析 - 将文档抽象为结构树
2. 模式匹配 - 识别对应的结构元素
3. 规则映射 - 应用目标格式规则
4. 内容重建 - 生成对齐后的文档
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ElementType(Enum):
    """文档元素类型"""
    TITLE = "title"
    HEADER = "header"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    QUOTE = "quote"
    CODE = "code"
    SEPARATOR = "separator"


@dataclass
class DocumentElement:
    """文档元素"""
    type: ElementType
    content: str
    level: int = 0  # 层级（如标题级别）
    attributes: Dict[str, Any] = None
    children: List['DocumentElement'] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.children is None:
            self.children = []


@dataclass
class FormatRule:
    """格式规则"""
    element_type: ElementType
    level: int
    prefix: str = ""
    suffix: str = ""
    indent: str = ""
    spacing_before: int = 0
    spacing_after: int = 0
    style_attributes: Dict[str, str] = None
    
    def __post_init__(self):
        if self.style_attributes is None:
            self.style_attributes = {}


class EfficientFormatAligner:
    """高效格式对齐器"""
    
    def __init__(self):
        # 预定义的格式模式
        self.format_patterns = {
            "government_official": self._get_government_format_rules(),
            "business_report": self._get_business_format_rules(),
            "academic_paper": self._get_academic_format_rules(),
            "technical_doc": self._get_technical_format_rules()
        }
    
    def align_format(self, source_content: str, target_format: str, 
                    custom_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        高效格式对齐主流程
        
        Args:
            source_content: 源文档内容
            target_format: 目标格式类型或格式规则
            custom_rules: 自定义格式规则
            
        Returns:
            {
                "aligned_content": str,
                "format_rules_applied": List[str],
                "structure_mapping": Dict[str, Any],
                "confidence": float
            }
        """
        try:
            # 1. 解析源文档结构
            source_structure = self._parse_document_structure(source_content)
            
            # 2. 获取目标格式规则
            if isinstance(target_format, str) and target_format in self.format_patterns:
                format_rules = self.format_patterns[target_format]
            elif isinstance(target_format, dict):
                format_rules = self._parse_custom_format_rules(target_format)
            else:
                format_rules = self._extract_format_from_content(target_format)
            
            # 3. 结构映射和对齐
            aligned_structure = self._map_and_align_structure(source_structure, format_rules)
            
            # 4. 重建文档
            aligned_content = self._rebuild_document(aligned_structure, format_rules)
            
            # 5. 质量评估
            confidence = self._assess_alignment_quality(source_content, aligned_content)
            
            return {
                "success": True,
                "aligned_content": aligned_content,
                "format_rules_applied": list(format_rules.keys()),
                "structure_mapping": self._generate_mapping_summary(source_structure, aligned_structure),
                "confidence": confidence
            }
            
        except Exception as e:
            return {"error": f"格式对齐失败: {str(e)}"}
    
    def _parse_document_structure(self, content: str) -> List[DocumentElement]:
        """解析文档结构为元素树"""
        if not content or not content.strip():
            return []
        
        lines = content.split('\n')
        elements = []
        current_paragraph = []
        
        for line in lines:
            stripped_line = line.strip()
            
            if not stripped_line:
                # 空行 - 结束当前段落
                if current_paragraph:
                    elements.append(DocumentElement(
                        type=ElementType.PARAGRAPH,
                        content='\n'.join(current_paragraph)
                    ))
                    current_paragraph = []
                continue
            
            # 检测元素类型
            element_type, level, content_text = self._identify_element_type(stripped_line)
            
            if element_type == ElementType.PARAGRAPH:
                current_paragraph.append(stripped_line)
            else:
                # 非段落元素 - 先保存当前段落
                if current_paragraph:
                    elements.append(DocumentElement(
                        type=ElementType.PARAGRAPH,
                        content='\n'.join(current_paragraph)
                    ))
                    current_paragraph = []
                
                # 添加当前元素
                elements.append(DocumentElement(
                    type=element_type,
                    content=content_text,
                    level=level
                ))
        
        # 处理最后的段落
        if current_paragraph:
            elements.append(DocumentElement(
                type=ElementType.PARAGRAPH,
                content='\n'.join(current_paragraph)
            ))
        
        return elements
    
    def _identify_element_type(self, line: str) -> Tuple[ElementType, int, str]:
        """识别元素类型和层级"""
        # 标题检测
        if re.match(r'^[一二三四五六七八九十]+[、.]', line):
            return ElementType.HEADER, 1, line
        elif re.match(r'^\d+[、.]', line):
            return ElementType.HEADER, 2, line
        elif re.match(r'^[（(]\d+[）)]', line):
            return ElementType.HEADER, 3, line
        elif re.match(r'^#+\s', line):
            level = len(re.match(r'^#+', line).group())
            return ElementType.HEADER, level, line[level:].strip()
        
        # 列表检测
        elif re.match(r'^\s*[-*+]\s', line):
            return ElementType.LIST, 1, line
        elif re.match(r'^\s*\d+\.\s', line):
            return ElementType.LIST, 1, line
        
        # 表格检测
        elif '|' in line or '\t' in line:
            return ElementType.TABLE, 0, line
        
        # 引用检测
        elif line.startswith('>') or line.startswith('"'):
            return ElementType.QUOTE, 0, line
        
        # 代码检测
        elif line.startswith('```') or line.startswith('    '):
            return ElementType.CODE, 0, line
        
        # 分隔符检测
        elif re.match(r'^[-=_]{3,}$', line):
            return ElementType.SEPARATOR, 0, line
        
        # 默认为段落
        else:
            return ElementType.PARAGRAPH, 0, line
    
    def _map_and_align_structure(self, source_elements: List[DocumentElement], 
                                format_rules: Dict[str, FormatRule]) -> List[DocumentElement]:
        """映射和对齐结构"""
        aligned_elements = []
        
        for element in source_elements:
            # 查找对应的格式规则
            rule_key = f"{element.type.value}_level_{element.level}"
            if rule_key not in format_rules:
                rule_key = element.type.value
            
            if rule_key in format_rules:
                rule = format_rules[rule_key]
                # 应用格式规则
                aligned_element = self._apply_format_rule(element, rule)
                aligned_elements.append(aligned_element)
            else:
                # 没有对应规则，保持原样
                aligned_elements.append(element)
        
        return aligned_elements
    
    def _apply_format_rule(self, element: DocumentElement, rule: FormatRule) -> DocumentElement:
        """应用格式规则到元素"""
        new_element = DocumentElement(
            type=element.type,
            content=element.content,
            level=element.level,
            attributes=element.attributes.copy(),
            children=element.children.copy()
        )
        
        # 应用前缀和后缀
        if rule.prefix:
            new_element.content = rule.prefix + new_element.content
        if rule.suffix:
            new_element.content = new_element.content + rule.suffix
        
        # 应用缩进
        if rule.indent:
            new_element.content = rule.indent + new_element.content
        
        # 保存格式属性
        new_element.attributes.update({
            "spacing_before": rule.spacing_before,
            "spacing_after": rule.spacing_after,
            "style_attributes": rule.style_attributes
        })
        
        return new_element
    
    def _rebuild_document(self, elements: List[DocumentElement], 
                         format_rules: Dict[str, FormatRule]) -> str:
        """重建文档"""
        result_lines = []
        
        for i, element in enumerate(elements):
            # 添加前置空行
            spacing_before = element.attributes.get("spacing_before", 0)
            if spacing_before > 0 and result_lines:
                result_lines.extend([""] * spacing_before)
            
            # 添加元素内容
            result_lines.append(element.content)
            
            # 添加后置空行
            spacing_after = element.attributes.get("spacing_after", 0)
            if spacing_after > 0 and i < len(elements) - 1:
                result_lines.extend([""] * spacing_after)
        
        return '\n'.join(result_lines)
    
    def _assess_alignment_quality(self, source: str, aligned: str) -> float:
        """评估对齐质量"""
        # 简单的质量评估
        source_lines = len(source.split('\n'))
        aligned_lines = len(aligned.split('\n'))
        
        # 长度保持度
        length_ratio = min(aligned_lines / max(source_lines, 1), 1.0)
        
        # 内容保持度（关键词保持）
        source_words = set(source.split())
        aligned_words = set(aligned.split())
        content_preservation = len(source_words & aligned_words) / max(len(source_words), 1)
        
        # 综合评分
        quality = (length_ratio * 0.3 + content_preservation * 0.7)
        return min(1.0, quality)
    
    def _generate_mapping_summary(self, source: List[DocumentElement], 
                                 aligned: List[DocumentElement]) -> Dict[str, Any]:
        """生成映射摘要"""
        return {
            "source_elements": len(source),
            "aligned_elements": len(aligned),
            "element_types": list(set(elem.type.value for elem in aligned)),
            "structure_preserved": len(source) == len(aligned)
        }
    
    def _get_government_format_rules(self) -> Dict[str, FormatRule]:
        """政府公文格式规则"""
        return {
            "title": FormatRule(
                element_type=ElementType.TITLE,
                level=0,
                spacing_before=0,
                spacing_after=2,
                style_attributes={"align": "center", "font_weight": "bold"}
            ),
            "header_level_1": FormatRule(
                element_type=ElementType.HEADER,
                level=1,
                spacing_before=1,
                spacing_after=1,
                style_attributes={"font_weight": "bold"}
            ),
            "paragraph": FormatRule(
                element_type=ElementType.PARAGRAPH,
                level=0,
                indent="    ",
                spacing_after=1
            )
        }
    
    def _get_business_format_rules(self) -> Dict[str, FormatRule]:
        """商务报告格式规则"""
        return {
            "title": FormatRule(
                element_type=ElementType.TITLE,
                level=0,
                spacing_after=2,
                style_attributes={"font_size": "18px", "font_weight": "bold"}
            ),
            "header_level_1": FormatRule(
                element_type=ElementType.HEADER,
                level=1,
                prefix="",
                spacing_before=2,
                spacing_after=1,
                style_attributes={"font_weight": "bold", "color": "#2c3e50"}
            ),
            "paragraph": FormatRule(
                element_type=ElementType.PARAGRAPH,
                level=0,
                spacing_after=1,
                style_attributes={"line_height": "1.6"}
            )
        }
    
    def _get_academic_format_rules(self) -> Dict[str, FormatRule]:
        """学术论文格式规则"""
        return {
            "title": FormatRule(
                element_type=ElementType.TITLE,
                level=0,
                spacing_after=3,
                style_attributes={"align": "center", "font_size": "16px", "font_weight": "bold"}
            ),
            "header_level_1": FormatRule(
                element_type=ElementType.HEADER,
                level=1,
                spacing_before=2,
                spacing_after=1,
                style_attributes={"font_weight": "bold"}
            ),
            "paragraph": FormatRule(
                element_type=ElementType.PARAGRAPH,
                level=0,
                indent="    ",
                spacing_after=1,
                style_attributes={"text_align": "justify"}
            )
        }
    
    def _get_technical_format_rules(self) -> Dict[str, FormatRule]:
        """技术文档格式规则"""
        return {
            "title": FormatRule(
                element_type=ElementType.TITLE,
                level=0,
                prefix="# ",
                spacing_after=2
            ),
            "header_level_1": FormatRule(
                element_type=ElementType.HEADER,
                level=1,
                prefix="## ",
                spacing_before=2,
                spacing_after=1
            ),
            "header_level_2": FormatRule(
                element_type=ElementType.HEADER,
                level=2,
                prefix="### ",
                spacing_before=1,
                spacing_after=1
            ),
            "code": FormatRule(
                element_type=ElementType.CODE,
                level=0,
                prefix="```\n",
                suffix="\n```",
                spacing_before=1,
                spacing_after=1
            )
        }
    
    def _parse_custom_format_rules(self, custom_rules: Dict[str, Any]) -> Dict[str, FormatRule]:
        """解析自定义格式规则"""
        # 将字典格式转换为FormatRule对象
        rules = {}
        for key, rule_data in custom_rules.items():
            rules[key] = FormatRule(**rule_data)
        return rules
    
    def _extract_format_from_content(self, target_content: str) -> Dict[str, FormatRule]:
        """从目标内容中提取格式规则"""
        # 分析目标内容的格式模式
        target_elements = self._parse_document_structure(target_content)
        
        # 基于分析结果生成格式规则
        rules = {}
        for element in target_elements:
            rule_key = f"{element.type.value}_level_{element.level}"
            if rule_key not in rules:
                # 分析该元素的格式特征
                rules[rule_key] = self._infer_format_rule_from_element(element)
        
        return rules
    
    def _infer_format_rule_from_element(self, element: DocumentElement) -> FormatRule:
        """从元素推断格式规则"""
        # 简单的格式推断逻辑
        return FormatRule(
            element_type=element.type,
            level=element.level,
            spacing_after=1 if element.type != ElementType.PARAGRAPH else 0
        )
