"""
精确格式应用器 - 将源文档内容严丝合缝地应用目标格式

核心功能：
1. 解析源文档内容结构
2. 加载目标格式模板
3. 精确映射和应用格式
4. 生成完全对齐的目标文档
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.shared import OxmlElement, qn
except ImportError:
    print("Warning: python-docx not installed. Word format application will be limited.")

from .precise_format_extractor import PreciseFormatExtractor, DocumentFormatTemplate


@dataclass
class ContentElement:
    """内容元素"""
    type: str  # title, heading, paragraph, table, list
    content: str
    level: int = 0
    attributes: Dict[str, Any] = None
    table_data: List[List[str]] = None  # 表格数据
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.table_data is None:
            self.table_data = []


class PreciseFormatApplier:
    """精确格式应用器"""
    
    def __init__(self, templates_dir: str = "src/core/knowledge_base/format_templates"):
        self.templates_dir = templates_dir
        self.format_extractor = PreciseFormatExtractor(templates_dir)
    
    def apply_format_precisely(self, source_content: str, target_template_id: str, 
                              output_path: str = None) -> Dict[str, Any]:
        """
        精确应用格式
        
        Args:
            source_content: 源文档内容（文本或文件路径）
            target_template_id: 目标格式模板ID
            output_path: 输出文件路径
            
        Returns:
            {
                "success": bool,
                "output_file": str,
                "format_applied": Dict[str, Any],
                "mapping_details": List[Dict[str, Any]]
            }
        """
        try:
            # 1. 加载目标格式模板
            template_result = self.format_extractor.load_format_template(target_template_id)
            if "error" in template_result:
                return template_result
            
            template_data = template_result["template_data"]
            
            # 2. 解析源文档内容结构
            if os.path.exists(source_content):
                content_elements = self._parse_document_file(source_content)
            else:
                content_elements = self._parse_text_content(source_content)
            
            # 3. 根据模板类型生成对应格式的文档
            doc_type = template_data.get("document_type", "docx")
            
            if doc_type == "docx":
                result = self._generate_word_document(content_elements, template_data, output_path)
            elif doc_type == "pdf":
                result = self._generate_pdf_document(content_elements, template_data, output_path)
            elif doc_type == "xlsx":
                result = self._generate_excel_document(content_elements, template_data, output_path)
            elif doc_type == "pptx":
                result = self._generate_ppt_document(content_elements, template_data, output_path)
            else:
                return {"error": f"不支持的文档类型: {doc_type}"}
            
            return result
            
        except Exception as e:
            return {"error": f"格式应用失败: {str(e)}"}
    
    def _parse_document_file(self, file_path: str) -> List[ContentElement]:
        """解析文档文件"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.docx':
            return self._parse_word_content(file_path)
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._parse_text_content(content)
        else:
            return {"error": f"不支持的源文档类型: {file_ext}"}
    
    def _parse_word_content(self, file_path: str) -> List[ContentElement]:
        """解析Word文档内容"""
        try:
            doc = Document(file_path)
            elements = []
            
            for paragraph in doc.paragraphs:
                if not paragraph.text.strip():
                    continue
                
                # 识别元素类型
                element_type, level = self._identify_content_type(paragraph.text, paragraph.style.name if paragraph.style else "Normal")
                
                elements.append(ContentElement(
                    type=element_type,
                    content=paragraph.text.strip(),
                    level=level
                ))
            
            # 处理表格
            for table in doc.tables:
                table_data = []
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    table_data.append(row_data)
                
                elements.append(ContentElement(
                    type="table",
                    content="",
                    table_data=table_data
                ))
            
            return elements
            
        except Exception as e:
            return [ContentElement(type="paragraph", content=f"解析失败: {str(e)}")]
    
    def _parse_text_content(self, content: str) -> List[ContentElement]:
        """解析文本内容"""
        elements = []
        lines = content.split('\n')
        
        current_table = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测表格
            if '|' in line or '\t' in line:
                if not in_table:
                    in_table = True
                    current_table = []
                
                # 解析表格行
                if '|' in line:
                    row_data = [cell.strip() for cell in line.split('|') if cell.strip()]
                else:
                    row_data = [cell.strip() for cell in line.split('\t')]
                
                current_table.append(row_data)
                continue
            else:
                # 结束表格
                if in_table and current_table:
                    elements.append(ContentElement(
                        type="table",
                        content="",
                        table_data=current_table
                    ))
                    current_table = []
                    in_table = False
            
            # 识别其他元素类型
            element_type, level = self._identify_content_type(line)
            
            elements.append(ContentElement(
                type=element_type,
                content=line,
                level=level
            ))
        
        # 处理最后的表格
        if in_table and current_table:
            elements.append(ContentElement(
                type="table",
                content="",
                table_data=current_table
            ))
        
        return elements
    
    def _identify_content_type(self, text: str, style_name: str = "") -> Tuple[str, int]:
        """识别内容类型和级别"""
        text = text.strip()
        
        # 基于样式名称判断
        if "Title" in style_name:
            return "title", 0
        elif "Heading" in style_name:
            level = 1
            if "Heading 2" in style_name:
                level = 2
            elif "Heading 3" in style_name:
                level = 3
            return "heading", level
        
        # 基于文本模式判断
        if len(text) < 50 and not text.endswith('。') and not text.endswith('：'):
            # 可能是标题
            if re.match(r'^[一二三四五六七八九十]+[、.]', text):
                return "heading", 1
            elif re.match(r'^\d+[、.]', text):
                return "heading", 2
            elif re.match(r'^[（(]\d+[）)]', text):
                return "heading", 3
            else:
                return "title", 0
        
        # 列表项
        if re.match(r'^\s*[-*+]\s', text) or re.match(r'^\s*\d+\.\s', text):
            return "list", 1
        
        # 默认为段落
        return "paragraph", 0
    
    def _generate_word_document(self, content_elements: List[ContentElement], 
                               template_data: Dict[str, Any], output_path: str = None) -> Dict[str, Any]:
        """生成Word文档"""
        try:
            doc = Document()
            
            # 应用页面设置
            self._apply_word_page_settings(doc, template_data.get("page_style", {}))
            
            # 处理内容元素
            mapping_details = []
            table_style_index = 0
            
            for element in content_elements:
                if element.type == "title":
                    para = doc.add_paragraph(element.content)
                    self._apply_word_style(para, template_data.get("title_style", {}))
                    mapping_details.append({"type": "title", "applied_style": "title_style"})
                
                elif element.type == "heading":
                    para = doc.add_paragraph(element.content)
                    heading_styles = template_data.get("heading_styles", {})
                    style_key = str(element.level)
                    if style_key in heading_styles:
                        self._apply_word_style(para, heading_styles[style_key])
                        mapping_details.append({"type": f"heading_{element.level}", "applied_style": f"heading_{element.level}_style"})
                    else:
                        # 使用默认标题样式
                        self._apply_word_style(para, template_data.get("title_style", {}))
                        mapping_details.append({"type": f"heading_{element.level}", "applied_style": "title_style"})
                
                elif element.type == "paragraph":
                    para = doc.add_paragraph(element.content)
                    self._apply_word_style(para, template_data.get("paragraph_style", {}))
                    mapping_details.append({"type": "paragraph", "applied_style": "paragraph_style"})
                
                elif element.type == "table" and element.table_data:
                    table = self._create_word_table(doc, element.table_data, template_data, table_style_index)
                    mapping_details.append({"type": "table", "applied_style": f"table_style_{table_style_index}"})
                    table_style_index += 1
                
                elif element.type == "list":
                    para = doc.add_paragraph(element.content)
                    self._apply_word_style(para, template_data.get("list_styles", {}))
                    mapping_details.append({"type": "list", "applied_style": "list_style"})
            
            # 保存文档
            if not output_path:
                output_path = f"output/formatted_document_{template_data.get('template_id', 'unknown')}.docx"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            doc.save(output_path)
            
            return {
                "success": True,
                "output_file": output_path,
                "format_applied": {
                    "template_id": template_data.get("template_id"),
                    "document_type": "docx",
                    "elements_processed": len(content_elements)
                },
                "mapping_details": mapping_details
            }
            
        except Exception as e:
            return {"error": f"Word文档生成失败: {str(e)}"}
    
    def _apply_word_page_settings(self, doc: Document, page_style: Dict[str, Any]):
        """应用Word页面设置"""
        try:
            section = doc.sections[0]
            
            if "width" in page_style:
                section.page_width = Inches(page_style["width"])
            if "height" in page_style:
                section.page_height = Inches(page_style["height"])
            if "margin_top" in page_style:
                section.top_margin = Inches(page_style["margin_top"])
            if "margin_bottom" in page_style:
                section.bottom_margin = Inches(page_style["margin_bottom"])
            if "margin_left" in page_style:
                section.left_margin = Inches(page_style["margin_left"])
            if "margin_right" in page_style:
                section.right_margin = Inches(page_style["margin_right"])
                
        except Exception as e:
            print(f"应用页面设置失败: {e}")
    
    def _apply_word_style(self, paragraph, style_info: Dict[str, Any]):
        """应用Word样式"""
        try:
            # 确保段落有内容
            if not paragraph.runs:
                paragraph.add_run()
            
            # 应用字体样式
            if "font" in style_info:
                font_info = style_info["font"]
                for run in paragraph.runs:
                    if "name" in font_info:
                        run.font.name = font_info["name"]
                    if "size" in font_info:
                        run.font.size = Pt(font_info["size"])
                    if "bold" in font_info:
                        run.font.bold = font_info["bold"]
                    if "italic" in font_info:
                        run.font.italic = font_info["italic"]
                    if "underline" in font_info:
                        run.font.underline = font_info["underline"]
                    if "color" in font_info and font_info["color"] != "#000000":
                        try:
                            color_hex = font_info["color"].replace("#", "")
                            rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                            run.font.color.rgb = RGBColor(*rgb)
                        except:
                            pass
            
            # 应用段落格式
            if "paragraph" in style_info:
                para_info = style_info["paragraph"]
                fmt = paragraph.paragraph_format
                
                if "alignment" in para_info:
                    alignment_map = {
                        "left": WD_ALIGN_PARAGRAPH.LEFT,
                        "center": WD_ALIGN_PARAGRAPH.CENTER,
                        "right": WD_ALIGN_PARAGRAPH.RIGHT,
                        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY
                    }
                    fmt.alignment = alignment_map.get(para_info["alignment"])
                
                if "line_spacing" in para_info:
                    fmt.line_spacing = para_info["line_spacing"]
                
                if "space_before" in para_info:
                    fmt.space_before = Pt(para_info["space_before"])
                
                if "space_after" in para_info:
                    fmt.space_after = Pt(para_info["space_after"])
                
                if "first_line_indent" in para_info:
                    fmt.first_line_indent = Pt(para_info["first_line_indent"])
                
                if "left_indent" in para_info:
                    fmt.left_indent = Pt(para_info["left_indent"])
                
                if "right_indent" in para_info:
                    fmt.right_indent = Pt(para_info["right_indent"])
        
        except Exception as e:
            print(f"应用样式失败: {e}")
    
    def _create_word_table(self, doc: Document, table_data: List[List[str]], 
                          template_data: Dict[str, Any], style_index: int) -> Any:
        """创建Word表格"""
        try:
            if not table_data:
                return None
            
            rows = len(table_data)
            cols = max(len(row) for row in table_data) if table_data else 1
            
            table = doc.add_table(rows=rows, cols=cols)
            
            # 填充表格数据
            for row_idx, row_data in enumerate(table_data):
                for col_idx, cell_data in enumerate(row_data):
                    if col_idx < len(table.rows[row_idx].cells):
                        cell = table.rows[row_idx].cells[col_idx]
                        cell.text = str(cell_data)
                        
                        # 应用单元格样式
                        if cell.paragraphs:
                            self._apply_table_cell_style(cell.paragraphs[0], template_data, style_index)
            
            # 应用表格样式
            self._apply_table_style(table, template_data, style_index)
            
            return table
            
        except Exception as e:
            print(f"创建表格失败: {e}")
            return None
    
    def _apply_table_style(self, table, template_data: Dict[str, Any], style_index: int):
        """应用表格样式"""
        try:
            table_styles = template_data.get("table_styles", [])
            if style_index < len(table_styles):
                table_style = table_styles[style_index]
                
                # 应用列宽
                if "column_widths" in table_style and table_style["column_widths"]:
                    for col_idx, width in enumerate(table_style["column_widths"]):
                        if col_idx < len(table.columns):
                            table.columns[col_idx].width = Inches(width)
                
                # 应用行高
                if "row_heights" in table_style and table_style["row_heights"]:
                    for row_idx, height in enumerate(table_style["row_heights"]):
                        if row_idx < len(table.rows):
                            table.rows[row_idx].height = Inches(height)
            
        except Exception as e:
            print(f"应用表格样式失败: {e}")
    
    def _apply_table_cell_style(self, paragraph, template_data: Dict[str, Any], style_index: int):
        """应用表格单元格样式"""
        try:
            table_styles = template_data.get("table_styles", [])
            if style_index < len(table_styles):
                table_style = table_styles[style_index]
                if "cell_styles" in table_style:
                    self._apply_word_style(paragraph, table_style["cell_styles"])
        except Exception as e:
            print(f"应用单元格样式失败: {e}")
    
    def _generate_pdf_document(self, content_elements: List[ContentElement], 
                              template_data: Dict[str, Any], output_path: str = None) -> Dict[str, Any]:
        """生成PDF文档（简化实现）"""
        return {"error": "PDF生成功能待实现"}
    
    def _generate_excel_document(self, content_elements: List[ContentElement], 
                                template_data: Dict[str, Any], output_path: str = None) -> Dict[str, Any]:
        """生成Excel文档（简化实现）"""
        return {"error": "Excel生成功能待实现"}
    
    def _generate_ppt_document(self, content_elements: List[ContentElement], 
                              template_data: Dict[str, Any], output_path: str = None) -> Dict[str, Any]:
        """生成PowerPoint文档（简化实现）"""
        return {"error": "PowerPoint生成功能待实现"}
    
    def batch_apply_format(self, source_files: List[str], target_template_id: str, 
                          output_dir: str = "output/batch_formatted") -> Dict[str, Any]:
        """批量应用格式"""
        results = []
        os.makedirs(output_dir, exist_ok=True)
        
        for source_file in source_files:
            try:
                filename = os.path.basename(source_file)
                name_without_ext = os.path.splitext(filename)[0]
                output_path = os.path.join(output_dir, f"{name_without_ext}_formatted.docx")
                
                result = self.apply_format_precisely(source_file, target_template_id, output_path)
                results.append({
                    "source_file": source_file,
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "source_file": source_file,
                    "result": {"error": f"处理失败: {str(e)}"}
                })
        
        return {
            "success": True,
            "processed_files": len(source_files),
            "results": results
        }
