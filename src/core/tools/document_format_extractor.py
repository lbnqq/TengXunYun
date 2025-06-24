import re
import json
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime
import hashlib

class DocumentFormatExtractor:
    """
    文档格式提取器
    智能分析文档格式并生成格式对齐提示词
    """
    
    def __init__(self, storage_path: str = "src/core/knowledge_base/format_templates"):
        self.tool_name = "文档格式提取器"
        self.description = "智能分析文档格式，生成格式对齐提示词，支持格式模板保存和复用"
        self.storage_path = storage_path
        
        # 确保存储目录存在
        os.makedirs(storage_path, exist_ok=True)
        
        # 字体大小映射（磅值到中文描述）
        self.font_size_mapping = {
            "42": "初号", "36": "小初", "26": "一号", "24": "小一",
            "22": "二号", "18": "小二", "16": "三号", "15": "小三",
            "14": "四号", "12": "小四", "10.5": "五号", "9": "小五",
            "7.5": "六号", "6.5": "小六", "5.5": "七号", "5": "八号"
        }
        
        # 常见字体映射
        self.font_family_mapping = {
            "SimSun": "宋体", "SimHei": "黑体", "KaiTi": "楷体",
            "FangSong": "仿宋", "Microsoft YaHei": "微软雅黑",
            "Times New Roman": "Times New Roman", "Arial": "Arial"
        }
    
    def extract_format_from_document(self, document_content: str, document_name: str = None) -> Dict[str, Any]:
        """
        从文档中提取格式信息
        
        Args:
            document_content: 文档内容
            document_name: 文档名称
            
        Returns:
            格式分析结果
        """
        try:
            # 分析文档结构
            structure_analysis = self._analyze_document_structure(document_content)
            
            # 提取格式规范
            format_rules = self._extract_format_rules(structure_analysis)
            
            # 生成格式提示词
            format_prompt = self._generate_format_prompt(format_rules)
            
            # 生成格式模板ID
            template_id = self._generate_template_id(document_name, format_rules)
            
            result = {
                "template_id": template_id,
                "document_name": document_name or "未命名文档",
                "structure_analysis": structure_analysis,
                "format_rules": format_rules,
                "format_prompt": format_prompt,
                "created_time": datetime.now().isoformat(),
                "html_template": self._generate_html_template(format_rules)
            }
            
            return result
            
        except Exception as e:
            return {"error": f"格式提取失败: {str(e)}"}
    
    def save_format_template(self, format_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存格式模板到持久化存储
        
        Args:
            format_data: 格式数据
            
        Returns:
            保存结果
        """
        try:
            template_id = format_data.get("template_id")
            if not template_id:
                return {"error": "缺少模板ID"}
            
            # 保存到JSON文件
            template_file = os.path.join(self.storage_path, f"{template_id}.json")
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(format_data, f, ensure_ascii=False, indent=2)
            
            # 更新模板索引
            self._update_template_index(template_id, format_data)
            
            return {
                "success": True,
                "template_id": template_id,
                "template_name": format_data.get("document_name", "未命名模板"),
                "saved_path": template_file
            }
            
        except Exception as e:
            return {"error": f"保存格式模板失败: {str(e)}"}
    
    def load_format_template(self, template_id: str) -> Dict[str, Any]:
        """
        加载格式模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            格式模板数据
        """
        try:
            template_file = os.path.join(self.storage_path, f"{template_id}.json")
            if not os.path.exists(template_file):
                return {"error": f"模板不存在: {template_id}"}
            
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            return template_data
            
        except Exception as e:
            return {"error": f"加载格式模板失败: {str(e)}"}
    
    def list_format_templates(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的格式模板
        
        Returns:
            模板列表
        """
        try:
            index_file = os.path.join(self.storage_path, "template_index.json")
            if not os.path.exists(index_file):
                return []
            
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            return index_data.get("templates", [])
            
        except Exception as e:
            print(f"加载模板索引失败: {str(e)}")
            return []
    
    def align_document_format(self, source_content: str, target_template_id: str) -> Dict[str, Any]:
        """
        将源文档格式对齐到目标模板
        
        Args:
            source_content: 源文档内容
            target_template_id: 目标格式模板ID
            
        Returns:
            格式对齐结果
        """
        try:
            # 加载目标格式模板
            template_data = self.load_format_template(target_template_id)
            if "error" in template_data:
                return template_data
            
            # 分析源文档结构
            source_structure = self._analyze_document_structure(source_content)
            
            # 应用目标格式
            aligned_content = self._apply_format_template(source_structure, template_data)
            
            return {
                "success": True,
                "aligned_content": aligned_content,
                "template_used": template_data.get("document_name", "未知模板"),
                "format_prompt": template_data.get("format_prompt", ""),
                "html_output": self._generate_formatted_html(aligned_content, template_data)
            }
            
        except Exception as e:
            return {"error": f"格式对齐失败: {str(e)}"}
    
    def _analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """分析文档结构"""
        lines = content.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        structure = {
            "total_lines": len(lines),
            "headings": [],
            "paragraphs": [],
            "lists": [],
            "estimated_format": {}
        }
        
        current_level = 0
        for i, line in enumerate(lines):
            line_analysis = self._analyze_line(line, i)
            
            if line_analysis["type"] == "heading":
                structure["headings"].append({
                    "level": line_analysis["level"],
                    "text": line,
                    "line_number": i,
                    "estimated_font": line_analysis.get("font_info", {})
                })
            elif line_analysis["type"] == "paragraph":
                structure["paragraphs"].append({
                    "text": line,
                    "line_number": i,
                    "estimated_font": line_analysis.get("font_info", {})
                })
            elif line_analysis["type"] == "list":
                structure["lists"].append({
                    "text": line,
                    "line_number": i,
                    "list_type": line_analysis.get("list_type", "bullet")
                })
        
        return structure
    
    def _analyze_line(self, line: str, line_number: int) -> Dict[str, Any]:
        """分析单行内容"""
        analysis = {"type": "paragraph", "level": 0}
        
        # 检测标题模式
        heading_patterns = [
            (r'^[一二三四五六七八九十]+[、．.]', 1),  # 一、二、三、
            (r'^[1-9]\d*[、．.]', 1),  # 1. 2. 3.
            (r'^（[一二三四五六七八九十]+）', 2),  # （一）（二）
            (r'^[1-9]\d*\.[1-9]\d*', 2),  # 1.1 1.2
            (r'^[1-9]\d*\.[1-9]\d*\.[1-9]\d*', 3),  # 1.1.1
        ]
        
        for pattern, level in heading_patterns:
            if re.match(pattern, line):
                analysis["type"] = "heading"
                analysis["level"] = level
                break
        
        # 检测列表
        list_patterns = [
            (r'^[•·▪▫◦‣⁃]', "bullet"),
            (r'^[-*+]', "bullet"),
            (r'^[1-9]\d*[)）]', "numbered")
        ]
        
        for pattern, list_type in list_patterns:
            if re.match(pattern, line):
                analysis["type"] = "list"
                analysis["list_type"] = list_type
                break
        
        # 估算字体信息（基于内容特征）
        analysis["font_info"] = self._estimate_font_info(line, analysis["type"], analysis.get("level", 0))
        
        return analysis
    
    def _estimate_font_info(self, text: str, text_type: str, level: int = 0) -> Dict[str, Any]:
        """估算字体信息"""
        font_info = {
            "family": "宋体",
            "size": "小四",
            "weight": "normal",
            "line_height": "1.5"
        }
        
        if text_type == "heading":
            font_info["family"] = "黑体"
            font_info["weight"] = "bold"
            
            if level == 1:
                font_info["size"] = "小三"
            elif level == 2:
                font_info["size"] = "四号"
            elif level == 3:
                font_info["size"] = "小四"
        
        return font_info
    
    def _extract_format_rules(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """提取格式规则"""
        rules = {
            "heading_formats": {},
            "paragraph_format": {},
            "list_format": {},
            "general_settings": {}
        }
        
        # 分析标题格式
        heading_levels = {}
        for heading in structure["headings"]:
            level = heading["level"]
            if level not in heading_levels:
                heading_levels[level] = []
            heading_levels[level].append(heading["estimated_font"])
        
        for level, fonts in heading_levels.items():
            # 取最常见的格式
            common_font = fonts[0] if fonts else {}
            rules["heading_formats"][f"level_{level}"] = {
                "font_family": common_font.get("family", "黑体"),
                "font_size": common_font.get("size", "小四"),
                "font_weight": "bold",
                "line_height": "1.5",
                "margin_top": "0",
                "margin_bottom": "0"
            }
        
        # 正文格式
        rules["paragraph_format"] = {
            "font_family": "宋体",
            "font_size": "小四",
            "text_align": "left",
            "text_indent": "2em",
            "line_height": "1.5"
        }
        
        # 列表格式
        rules["list_format"] = {
            "font_family": "宋体",
            "font_size": "小四",
            "list_style": "minimal"
        }
        
        return rules
    
    def _generate_format_prompt(self, format_rules: Dict[str, Any]) -> str:
        """生成格式提示词"""
        prompt_parts = [
            "请把内容以HTML生成，智能自动识别各级标题，内容排版要求如下:"
        ]
        
        # 标题格式
        heading_formats = format_rules.get("heading_formats", {})
        for level_key, format_info in heading_formats.items():
            level_num = level_key.split("_")[1]
            if level_num == "1":
                level_name = "一级标题"
            elif level_num == "2":
                level_name = "二级标题"
            elif level_num == "3":
                level_name = "三级标题"
            else:
                level_name = f"{level_num}级标题"
            
            font_family = format_info.get("font_family", "黑体")
            font_size = format_info.get("font_size", "小四")
            line_height = format_info.get("line_height", "1.5")
            
            prompt_parts.append(
                f"{level_num}、{level_name} 字体为{font_family}({font_size})，{line_height}倍行距，段前段后空0行；"
            )
        
        # 正文格式
        para_format = format_rules.get("paragraph_format", {})
        font_size = para_format.get("font_size", "小四")
        font_family = para_format.get("font_family", "宋体")
        text_align = para_format.get("text_align", "左对齐")
        
        prompt_parts.append(
            f"{len(heading_formats) + 1}、正文 {font_size} {font_family}，对齐方式为{text_align}，首行缩进两个字符。"
        )
        
        # 列表格式
        prompt_parts.append(
            f"{len(heading_formats) + 2}、少用项目符号，禁止多级项目符号，去掉后面无文字的项目符号"
        )
        
        prompt_parts.append(
            "用Html的格式输出，需要有能直接下载word文档的功能（不要调用doc JS库）。"
        )
        
        return "\n".join(prompt_parts)
    
    def _generate_template_id(self, document_name: str, format_rules: Dict[str, Any]) -> str:
        """生成模板ID"""
        # 基于文档名和格式规则生成唯一ID
        content = f"{document_name}_{json.dumps(format_rules, sort_keys=True)}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
    
    def _generate_html_template(self, format_rules: Dict[str, Any]) -> str:
        """生成HTML模板"""
        css_styles = []
        
        # 标题样式
        heading_formats = format_rules.get("heading_formats", {})
        for level_key, format_info in heading_formats.items():
            level_num = level_key.split("_")[1]
            css_styles.append(f"""
            h{level_num} {{
                font-family: '{format_info.get("font_family", "黑体")}';
                font-size: {self._convert_font_size(format_info.get("font_size", "小四"))};
                font-weight: bold;
                line-height: {format_info.get("line_height", "1.5")};
                margin-top: 0;
                margin-bottom: 0;
            }}""")
        
        # 正文样式
        para_format = format_rules.get("paragraph_format", {})
        css_styles.append(f"""
        p {{
            font-family: '{para_format.get("font_family", "宋体")}';
            font-size: {self._convert_font_size(para_format.get("font_size", "小四"))};
            text-align: {para_format.get("text_align", "left")};
            text-indent: 2em;
            line-height: {para_format.get("line_height", "1.5")};
        }}""")
        
        return f"<style>{''.join(css_styles)}</style>"
    
    def _convert_font_size(self, chinese_size: str) -> str:
        """转换中文字号为CSS大小"""
        size_mapping = {
            "初号": "42pt", "小初": "36pt", "一号": "26pt", "小一": "24pt",
            "二号": "22pt", "小二": "18pt", "三号": "16pt", "小三": "15pt",
            "四号": "14pt", "小四": "12pt", "五号": "10.5pt", "小五": "9pt"
        }
        return size_mapping.get(chinese_size, "12pt")
    
    def _update_template_index(self, template_id: str, template_data: Dict[str, Any]):
        """更新模板索引"""
        index_file = os.path.join(self.storage_path, "template_index.json")
        
        # 读取现有索引
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        else:
            index_data = {"templates": []}
        
        # 更新或添加模板信息
        template_info = {
            "template_id": template_id,
            "name": template_data.get("document_name", "未命名模板"),
            "created_time": template_data.get("created_time", datetime.now().isoformat()),
            "description": f"规范格式：{template_data.get('document_name', '未命名文档')}"
        }
        
        # 检查是否已存在
        existing_index = -1
        for i, template in enumerate(index_data["templates"]):
            if template["template_id"] == template_id:
                existing_index = i
                break
        
        if existing_index >= 0:
            index_data["templates"][existing_index] = template_info
        else:
            index_data["templates"].append(template_info)
        
        # 保存索引
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def _apply_format_template(self, source_structure: Dict[str, Any], template_data: Dict[str, Any]) -> str:
        """应用格式模板到源文档"""
        # 这里实现格式应用逻辑
        # 目前返回带格式说明的内容
        lines = []
        lines.append("# 格式对齐结果")
        lines.append("")
        lines.append(f"已应用格式模板：{template_data.get('document_name', '未知模板')}")
        lines.append("")
        lines.append("## 应用的格式规则")
        lines.append(template_data.get('format_prompt', '无格式规则'))
        
        return "\n".join(lines)
    
    def _generate_formatted_html(self, content: str, template_data: Dict[str, Any]) -> str:
        """生成格式化的HTML"""
        html_template = template_data.get("html_template", "")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>格式化文档</title>
            {html_template}
        </head>
        <body>
            <div class="document-content">
                {self._convert_to_html(content)}
            </div>
            <script>
                function downloadAsWord() {{
                    const content = document.querySelector('.document-content').innerHTML;
                    const blob = new Blob([content], {{type: 'application/msword'}});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'formatted_document.doc';
                    a.click();
                }}
            </script>
            <button onclick="downloadAsWord()">下载Word文档</button>
        </body>
        </html>
        """
        
        return html_content
    
    def _convert_to_html(self, content: str) -> str:
        """将文本内容转换为HTML"""
        lines = content.split('\n')
        html_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 简单的HTML转换
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('# ').strip()
                html_lines.append(f"<h{level}>{text}</h{level}>")
            else:
                html_lines.append(f"<p>{line}</p>")
        
        return '\n'.join(html_lines)
