#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intelligent Image Processor - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import os
import base64
import hashlib
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import json
import svgwrite

class IntelligentImageProcessor:
    """智能图片处理器"""
    
    def __init__(self):
        self.tool_name = "智能图片处理器"
        self.description = "处理文档中的图片字段，智能识别位置和格式"
        
        # 支持的图片格式
        self.supported_formats = {
            "jpg": "JPEG",
            "jpeg": "JPEG", 
            "png": "PNG",
            "gif": "GIF",
            "bmp": "BMP",
            "tiff": "TIFF",
            "webp": "WEBP"
        }
        
        # 图片处理配置
        self.image_config = {
            "max_size": (1920, 1080),  # 最大尺寸
            "min_size": (100, 100),    # 最小尺寸
            "quality": 85,             # JPEG质量
            "thumbnail_size": (200, 200),  # 缩略图尺寸
            "watermark_text": "AI生成",  # 水印文字
            "default_format": "PNG"
        }
        
        # 图片存储目录
        self.image_storage_dir = os.path.join("uploads", "images")
        os.makedirs(self.image_storage_dir, exist_ok=True)
    
    def process_uploaded_image(self, image_data: Union[str, bytes], 
                             image_name: str = None, 
                             target_position: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理上传的图片
        
        Args:
            image_data: 图片数据（base64字符串或二进制数据）
            image_name: 图片名称
            target_position: 目标位置信息
            
        Returns:
            处理结果
        """
        try:
            # 1. 解析图片数据
            image_bytes = self._parse_image_data(image_data)
            if not image_bytes:
                return {"error": "无效的图片数据"}
            
            # 2. 验证图片格式
            image_info = self._validate_image_format(image_bytes)
            if "error" in image_info:
                return image_info
            
            # 3. 处理图片
            processed_image = self._process_image(image_bytes, target_position)
            if "error" in processed_image:
                return processed_image
            
            # 4. 保存图片
            save_result = self._save_processed_image(processed_image, image_name)
            if "error" in save_result:
                return save_result
            
            # 5. 生成图片信息
            image_info = self._generate_image_info(processed_image, save_result)
            
            return {
                "success": True,
                "image_id": save_result["image_id"],
                "file_path": save_result["file_path"],
                "file_size": save_result["file_size"],
                "dimensions": image_info["dimensions"],
                "format": image_info["format"],
                "thumbnail_path": save_result.get("thumbnail_path"),
                "position_info": target_position,
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"图片处理失败: {str(e)}"}
    
    def _parse_image_data(self, image_data: Union[str, bytes]) -> Optional[bytes]:
        """解析图片数据"""
        try:
            if isinstance(image_data, str):
                # Base64编码的图片数据
                if image_data.startswith('data:image'):
                    # 移除data URL前缀
                    header, data = image_data.split(',', 1)
                    return base64.b64decode(data)
                else:
                    # 纯base64字符串
                    return base64.b64decode(image_data)
            elif isinstance(image_data, bytes):
                return image_data
            else:
                return None
        except Exception:
            return None
    
    def _validate_image_format(self, image_bytes: bytes) -> Dict[str, Any]:
        """验证图片格式"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # 检查格式
            format_name = image.format
            if format_name not in self.supported_formats.values():
                return {"error": f"不支持的图片格式: {format_name}"}
            
            # 检查尺寸
            width, height = image.size
            if width < self.image_config["min_size"][0] or height < self.image_config["min_size"][1]:
                return {"error": f"图片尺寸过小: {width}x{height}"}
            
            return {
                "format": format_name,
                "dimensions": (width, height),
                "mode": image.mode
            }
            
        except Exception as e:
            return {"error": f"图片格式验证失败: {str(e)}"}
    
    def _process_image(self, image_bytes: bytes, target_position: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理图片"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # 1. 调整尺寸
            processed_image = self._resize_image(image, target_position)
            
            # 2. 添加水印（如果需要）
            if target_position and target_position.get("add_watermark", False):
                processed_image = self._add_watermark(processed_image)
            
            # 3. 优化质量
            processed_image = self._optimize_image(processed_image)
            
            # 4. 转换为目标格式
            target_format = target_position.get("format", self.image_config["default_format"]) if target_position else self.image_config["default_format"]
            processed_image = self._convert_format(processed_image, target_format)
            
            return {
                "image": processed_image,
                "format": target_format,
                "dimensions": processed_image.size
            }
            
        except Exception as e:
            return {"error": f"图片处理失败: {str(e)}"}
    
    def _resize_image(self, image: Image.Image, target_position: Dict[str, Any] = None) -> Image.Image:
        """调整图片尺寸"""
        width, height = image.size
        max_width, max_height = self.image_config["max_size"]
        
        # 如果指定了目标尺寸
        if target_position and "suggested_size" in target_position:
            target_width, target_height = target_position["suggested_size"]
            # 保持宽高比
            ratio = min(target_width / width, target_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
        else:
            # 使用最大尺寸限制
            if width > max_width or height > max_height:
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
            else:
                return image
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _add_watermark(self, image: Image.Image) -> Image.Image:
        """添加水印"""
        try:
            # 创建水印图层
            watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # 尝试加载字体
            try:
                font_size = min(image.size) // 20
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # 计算文字位置（右下角）
            text = self.image_config["watermark_text"]
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = image.size[0] - text_width - 10
            y = image.size[1] - text_height - 10
            
            # 绘制水印
            draw.text((x, y), text, font=font, fill=(128, 128, 128, 128))
            
            # 合并图层
            return Image.alpha_composite(image.convert('RGBA'), watermark).convert('RGB')
            
        except Exception:
            return image
    
    def _optimize_image(self, image: Image.Image) -> Image.Image:
        """优化图片质量"""
        # 转换为RGB模式（如果不是）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def _convert_format(self, image: Image.Image, target_format: str) -> Image.Image:
        """转换图片格式"""
        # 这里只是返回原图，实际转换在保存时进行
        return image
    
    def _save_processed_image(self, processed_data: Dict[str, Any], image_name: str = None) -> Dict[str, Any]:
        """保存处理后的图片"""
        try:
            image = processed_data["image"]
            format_name = processed_data["format"]
            
            # 生成图片ID
            image_id = self._generate_image_id(image, image_name)
            
            # 生成文件名
            if image_name:
                base_name = os.path.splitext(image_name)[0]
            else:
                base_name = image_id
            
            # 确定文件扩展名
            ext_map = {v: k for k, v in self.supported_formats.items()}
            extension = ext_map.get(format_name, "png")
            
            # 保存主图片
            file_name = f"{base_name}.{extension}"
            file_path = os.path.join(self.image_storage_dir, file_name)
            
            save_kwargs = {}
            if format_name == "JPEG":
                save_kwargs["quality"] = self.image_config["quality"]
                save_kwargs["optimize"] = True
            
            image.save(file_path, format=format_name, **save_kwargs)
            
            # 生成缩略图
            thumbnail_path = self._generate_thumbnail(image, base_name, format_name)
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            return {
                "image_id": image_id,
                "file_path": file_path,
                "file_size": file_size,
                "thumbnail_path": thumbnail_path
            }
            
        except Exception as e:
            return {"error": f"保存图片失败: {str(e)}"}
    
    def _generate_image_id(self, image: Image.Image, image_name: str = None) -> str:
        """生成图片ID"""
        # 基于图片内容和名称生成唯一ID
        content_hash = hashlib.md5(image.tobytes()).hexdigest()[:8]
        name_hash = hashlib.md5((image_name or "").encode()).hexdigest()[:4]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        return f"img_{timestamp}_{content_hash}_{name_hash}"
    
    def _generate_thumbnail(self, image: Image.Image, base_name: str, format_name: str) -> str:
        """生成缩略图"""
        try:
            # 创建缩略图
            thumbnail_size = self.image_config["thumbnail_size"]
            thumbnail = image.copy()
            thumbnail.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            
            # 保存缩略图
            thumbnail_name = f"{base_name}_thumb.{format_name.lower()}"
            thumbnail_path = os.path.join(self.image_storage_dir, thumbnail_name)
            
            save_kwargs = {}
            if format_name == "JPEG":
                save_kwargs["quality"] = 70
            
            thumbnail.save(thumbnail_path, format=format_name, **save_kwargs)
            
            return thumbnail_path
            
        except Exception:
            return ""
    
    def _generate_image_info(self, processed_data: Dict[str, Any], save_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成图片信息"""
        return {
            "dimensions": processed_data["dimensions"],
            "format": processed_data["format"],
            "file_size": save_result["file_size"],
            "file_path": save_result["file_path"]
        }
    
    def insert_image_to_document(self, document_content: str, image_info: Dict[str, Any], 
                                target_position: Dict[str, Any]) -> str:
        """
        将图片插入到文档中
        
        Args:
            document_content: 文档内容
            image_info: 图片信息
            target_position: 目标位置
            
        Returns:
            插入图片后的文档内容
        """
        try:
            lines = document_content.split('\n')
            line_number = target_position.get("line_number", 1) - 1
            
            # 生成图片插入标记
            image_markup = self._generate_image_markup(image_info, target_position)
            
            # 插入图片
            if line_number < len(lines):
                lines.insert(line_number, image_markup)
            else:
                lines.append(image_markup)
            
            return '\n'.join(lines)
            
        except Exception as e:
            return document_content
    
    def _generate_image_markup(self, image_info: Dict[str, Any], target_position: Dict[str, Any]) -> str:
        """生成图片标记"""
        image_path = image_info.get("file_path", "")
        image_id = image_info.get("image_id", "")
        dimensions = image_info.get("dimensions", (400, 300))
        
        # 根据文档类型生成不同的标记
        document_type = target_position.get("document_type", "general")
        
        if document_type == "patent":
            # 专利文档格式
            return f"[附图{image_id}] {image_path} ({dimensions[0]}x{dimensions[1]})"
        elif document_type == "html":
            # HTML格式
            return f'<img src="{image_path}" alt="图片{image_id}" width="{dimensions[0]}" height="{dimensions[1]}">'
        else:
            # 通用格式
            return f"[图片{image_id}] {image_path}"
    
    def batch_process_images(self, image_list: List[Dict[str, Any]], 
                           document_content: str) -> Dict[str, Any]:
        """
        批量处理图片
        
        Args:
            image_list: 图片列表
            document_content: 文档内容
            
        Returns:
            批量处理结果
        """
        try:
            results = {
                "success": True,
                "processed_images": [],
                "updated_document": document_content,
                "errors": []
            }
            
            for i, image_data in enumerate(image_list):
                try:
                    # 处理单个图片
                    result = self.process_uploaded_image(
                        image_data["data"],
                        image_data.get("name", f"image_{i}"),
                        image_data.get("position")
                    )
                    
                    if "error" in result:
                        results["errors"].append({
                            "index": i,
                            "error": result["error"]
                        })
                    else:
                        results["processed_images"].append(result)
                        
                        # 插入到文档中
                        if image_data.get("position"):
                            results["updated_document"] = self.insert_image_to_document(
                                results["updated_document"],
                                result,
                                image_data["position"]
                            )
                
                except Exception as e:
                    results["errors"].append({
                        "index": i,
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            return {"error": f"批量处理图片失败: {str(e)}"}
    
    def get_image_statistics(self) -> Dict[str, Any]:
        """获取图片统计信息"""
        try:
            total_files = 0
            total_size = 0
            format_stats = {}
            
            for filename in os.listdir(self.image_storage_dir):
                if filename.lower().endswith(tuple(self.supported_formats.keys())):
                    file_path = os.path.join(self.image_storage_dir, filename)
                    file_size = os.path.getsize(file_path)
                    
                    total_files += 1
                    total_size += file_size
                    
                    # 统计格式
                    ext = os.path.splitext(filename)[1].lower()[1:]
                    format_stats[ext] = format_stats.get(ext, 0) + 1
            
            return {
                "total_images": total_files,
                "total_size": total_size,
                "format_distribution": format_stats,
                "storage_path": self.image_storage_dir
            }
            
        except Exception as e:
            return {"error": f"获取统计信息失败: {str(e)}"}
    
    def generate_svg_image(self, svg_elements: list, svg_size=(400, 300), svg_name: str = None) -> dict:
        """
        生成SVG图像并保存到本地临时文件
        Args:
            svg_elements: SVG元素列表（如矩形、圆、文本等）
            svg_size: SVG画布尺寸
            svg_name: 文件名（可选）
        Returns:
            {'svg_path': 路径, 'svg_content': 内容, 'success': True/False, 'error': ...}
        """
        try:
            dwg = svgwrite.Drawing(size=svg_size)
            for elem in svg_elements:
                # elem: {'type': 'rect', 'args': {...}} 或 {'type': 'text', ...}
                if elem['type'] == 'rect':
                    dwg.add(dwg.rect(**elem['args']))
                elif elem['type'] == 'circle':
                    dwg.add(dwg.circle(**elem['args']))
                elif elem['type'] == 'text':
                    dwg.add(dwg.text(elem['text'], **elem['args']))
                # 可扩展更多SVG元素
            svg_content = dwg.tostring()
            tmp_dir = tempfile.gettempdir()
            if not svg_name:
                import uuid
                svg_name = f"ai_image_{uuid.uuid4().hex[:8]}.svg"
            svg_path = os.path.join(tmp_dir, svg_name)
            dwg.saveas(svg_path)
            return {'svg_path': svg_path, 'svg_content': svg_content, 'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def insert_svg_to_document(self, document_content: str, svg_info: Dict[str, Any], 
                              target_position: Dict[str, Any], mode: str = "preview") -> str:
        """
        将SVG插入到文档中
        
        Args:
            document_content: 文档内容
            svg_info: SVG信息 {'svg_path': 路径, 'svg_content': 内容}
            target_position: 目标位置
            mode: 模式 - "preview" 或 "download"
            
        Returns:
            插入SVG后的文档内容
        """
        try:
            lines = document_content.split('\n')
            line_number = target_position.get("line_number", 1) - 1
            
            # 根据模式生成不同的SVG标记
            if mode == "preview":
                # 预览模式：直接插入SVG内容
                svg_markup = self._generate_svg_content_markup(svg_info, target_position)
            else:
                # 下载模式：引用本地SVG文件
                svg_markup = self._generate_svg_file_markup(svg_info, target_position)
            
            # 插入SVG
            if line_number < len(lines):
                lines.insert(line_number, svg_markup)
            else:
                lines.append(svg_markup)
            
            return '\n'.join(lines)
            
        except Exception as e:
            return document_content
    
    def _generate_svg_content_markup(self, svg_info: Dict[str, Any], target_position: Dict[str, Any]) -> str:
        """生成SVG内容标记（预览模式）"""
        svg_content = svg_info.get("svg_content", "")
        svg_id = svg_info.get("svg_id", "svg_placeholder")
        dimensions = target_position.get("suggested_size", (400, 300))
        
        # 根据文档类型生成不同的标记
        document_type = target_position.get("document_type", "general")
        
        if document_type == "patent":
            # 专利文档格式
            return f"""
            <div class="svg-container" id="{svg_id}">
                <h4>附图说明</h4>
                {svg_content}
                <p class="svg-caption">图{svg_id} - 技术方案示意图</p>
            </div>
            """
        elif document_type == "html":
            # HTML格式
            return f"""
            <div class="svg-container">
                {svg_content}
            </div>
            """
        else:
            # 通用格式
            return f"""
            <div class="svg-container">
                {svg_content}
            </div>
            """
    
    def _generate_svg_file_markup(self, svg_info: Dict[str, Any], target_position: Dict[str, Any]) -> str:
        """生成SVG文件标记（下载模式）"""
        svg_path = svg_info.get("svg_path", "")
        svg_id = svg_info.get("svg_id", "svg_placeholder")
        dimensions = target_position.get("suggested_size", (400, 300))
        
        # 根据文档类型生成不同的标记
        document_type = target_position.get("document_type", "general")
        
        if document_type == "patent":
            # 专利文档格式
            return f"""
            <div class="svg-container" id="{svg_id}">
                <h4>附图说明</h4>
                <img src="file://{svg_path}" alt="图{svg_id}" width="{dimensions[0]}" height="{dimensions[1]}">
                <p class="svg-caption">图{svg_id} - 技术方案示意图</p>
            </div>
            """
        elif document_type == "html":
            # HTML格式
            return f'<img src="file://{svg_path}" alt="图片{svg_id}" width="{dimensions[0]}" height="{dimensions[1]}">'
        else:
            # 通用格式
            return f'<img src="file://{svg_path}" alt="图片{svg_id}" width="{dimensions[0]}" height="{dimensions[1]}">'
    
    def generate_ai_svg_for_document(self, document_type: str, content_description: str, 
                                   svg_size: Tuple[int, int] = (400, 300)) -> Dict[str, Any]:
        """
        根据文档类型和内容描述生成AI SVG图像
        
        Args:
            document_type: 文档类型
            content_description: 内容描述
            svg_size: SVG尺寸
            
        Returns:
            SVG生成结果
        """
        try:
            # 根据文档类型生成不同的SVG元素
            if document_type == "patent":
                svg_elements = self._generate_patent_svg_elements(content_description, svg_size)
            elif document_type == "project":
                svg_elements = self._generate_project_svg_elements(content_description, svg_size)
            else:
                svg_elements = self._generate_general_svg_elements(content_description, svg_size)
            
            # 生成SVG
            svg_name = f"ai_{document_type}_{hash(content_description) % 10000}.svg"
            result = self.generate_svg_image(svg_elements, svg_size, svg_name)
            
            if result["success"]:
                result["svg_id"] = svg_name.replace(".svg", "")
                result["document_type"] = document_type
                result["content_description"] = content_description
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"生成AI SVG失败: {str(e)}"}
    
    def _generate_patent_svg_elements(self, description: str, size: Tuple[int, int]) -> List[Dict[str, Any]]:
        """生成专利文档的SVG元素"""
        width, height = size
        elements = []
        
        # 背景矩形
        elements.append({
            "type": "rect",
            "args": {
                "insert": (10, 10),
                "size": (width-20, height-20),
                "fill": "#f8f9fa",
                "stroke": "#dee2e6",
                "stroke_width": 2
            }
        })
        
        # 标题
        elements.append({
            "type": "text",
            "text": "技术方案示意图",
            "args": {
                "insert": (width//2, 40),
                "text_anchor": "middle",
                "font_size": 16,
                "font_weight": "bold",
                "fill": "#2c3e50"
            }
        })
        
        # 技术流程图示例
        # 开始节点
        elements.append({
            "type": "rect",
            "args": {
                "insert": (50, 80),
                "size": (80, 40),
                "fill": "#3498db",
                "stroke": "#2980b9",
                "stroke_width": 1,
                "rx": 5
            }
        })
        elements.append({
            "type": "text",
            "text": "开始",
            "args": {
                "insert": (90, 105),
                "text_anchor": "middle",
                "font_size": 12,
                "fill": "white"
            }
        })
        
        # 箭头
        elements.append({
            "type": "text",
            "text": "→",
            "args": {
                "insert": (140, 100),
                "font_size": 20,
                "fill": "#7f8c8d"
            }
        })
        
        # 处理节点
        elements.append({
            "type": "rect",
            "args": {
                "insert": (160, 80),
                "size": (80, 40),
                "fill": "#e74c3c",
                "stroke": "#c0392b",
                "stroke_width": 1,
                "rx": 5
            }
        })
        elements.append({
            "type": "text",
            "text": "处理",
            "args": {
                "insert": (200, 105),
                "text_anchor": "middle",
                "font_size": 12,
                "fill": "white"
            }
        })
        
        # 描述文本
        if len(description) > 50:
            description = description[:47] + "..."
        
        elements.append({
            "type": "text",
            "text": description,
            "args": {
                "insert": (width//2, height-30),
                "text_anchor": "middle",
                "font_size": 10,
                "fill": "#7f8c8d"
            }
        })
        
        return elements
    
    def _generate_project_svg_elements(self, description: str, size: Tuple[int, int]) -> List[Dict[str, Any]]:
        """生成项目文档的SVG元素"""
        width, height = size
        elements = []
        
        # 背景
        elements.append({
            "type": "rect",
            "args": {
                "insert": (10, 10),
                "size": (width-20, height-20),
                "fill": "#ecf0f1",
                "stroke": "#bdc3c7",
                "stroke_width": 2
            }
        })
        
        # 标题
        elements.append({
            "type": "text",
            "text": "项目流程图",
            "args": {
                "insert": (width//2, 40),
                "text_anchor": "middle",
                "font_size": 16,
                "font_weight": "bold",
                "fill": "#34495e"
            }
        })
        
        # 项目阶段节点
        stages = ["需求分析", "设计", "开发", "测试", "部署"]
        stage_width = 60
        stage_height = 30
        start_x = 30
        
        for i, stage in enumerate(stages):
            x = start_x + i * (stage_width + 20)
            y = 80
            
            # 节点
            elements.append({
                "type": "rect",
                "args": {
                    "insert": (x, y),
                    "size": (stage_width, stage_height),
                    "fill": "#9b59b6",
                    "stroke": "#8e44ad",
                    "stroke_width": 1,
                    "rx": 3
                }
            })
            
            # 节点文本
            elements.append({
                "type": "text",
                "text": stage,
                "args": {
                    "insert": (x + stage_width//2, y + stage_height//2 + 4),
                    "text_anchor": "middle",
                    "font_size": 10,
                    "fill": "white"
                }
            })
            
            # 箭头（除了最后一个）
            if i < len(stages) - 1:
                elements.append({
                    "type": "text",
                    "text": "→",
                    "args": {
                        "insert": (x + stage_width + 10, y + stage_height//2),
                        "font_size": 16,
                        "fill": "#7f8c8d"
                    }
                })
        
        return elements
    
    def _generate_general_svg_elements(self, description: str, size: Tuple[int, int]) -> List[Dict[str, Any]]:
        """生成通用文档的SVG元素"""
        width, height = size
        elements = []
        
        # 背景
        elements.append({
            "type": "rect",
            "args": {
                "insert": (10, 10),
                "size": (width-20, height-20),
                "fill": "#f1f2f6",
                "stroke": "#dcdde1",
                "stroke_width": 2
            }
        })
        
        # 标题
        elements.append({
            "type": "text",
            "text": "文档示意图",
            "args": {
                "insert": (width//2, 40),
                "text_anchor": "middle",
                "font_size": 16,
                "font_weight": "bold",
                "fill": "#2f3542"
            }
        })
        
        # 简单的图形元素
        # 圆形
        elements.append({
            "type": "circle",
            "args": {
                "center": (width//3, height//2),
                "r": 30,
                "fill": "#ff6b6b",
                "stroke": "#ee5a52",
                "stroke_width": 2
            }
        })
        
        # 矩形
        elements.append({
            "type": "rect",
            "args": {
                "insert": (2*width//3 - 30, height//2 - 30),
                "size": (60, 60),
                "fill": "#4ecdc4",
                "stroke": "#44a08d",
                "stroke_width": 2,
                "rx": 5
            }
        })
        
        # 描述文本
        if len(description) > 40:
            description = description[:37] + "..."
        
        elements.append({
            "type": "text",
            "text": description,
            "args": {
                "insert": (width//2, height-20),
                "text_anchor": "middle",
                "font_size": 10,
                "fill": "#747d8c"
            }
        })
        
        return elements 