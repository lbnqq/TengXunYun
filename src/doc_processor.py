#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: doc_processor.py
Description: 文档处理器

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

import os
import logging
import pandas as pd
from typing import List, Dict, Any

from ocr_engine import PaddleOCRWrapper
from layout_analyzer import LayoutAnalyzer
from table_parser import TableParser
from utils import load_config, get_paddleocr_kwargs

class DocumentProcessor:
    def __init__(self, config_path="config/config.yaml"):
        self.config = load_config(config_path)
        self.ocr_config = self.config.get("ocr_engine", {})
        self.layout_config = self.config.get("layout_analyzer", {})
        self.table_config = self.config.get("table_parser", {})
        self.data_dir = self.config.get("data_dir", "data")
        
        # 优先用本地 PaddleOCR 模型参数初始化 OCR 引擎
        ocr_kwargs = get_paddleocr_kwargs(self.config)
        self.ocr_engine = PaddleOCRWrapper(**ocr_kwargs)
        
        # 初始化 Layout Analyzer
        self.layout_analyzer = LayoutAnalyzer(self.config)
        
        # 初始化 Table Parser
        self.table_parser = TableParser(self.config)

    def process_document(self, image_filename: str) -> List[pd.DataFrame]:
        image_path = os.path.join(self.data_dir, image_filename)
        
        if not os.path.exists(image_path):
            logging.error(f"文档处理错误: 文件 '{image_path}' 不存在。")
            return []

        logging.info(f"开始处理文档: {image_path}")

        # 1. OCR 识别
        ocr_results = self.ocr_engine.recognize(image_path)
        if not ocr_results:
            logging.warning(f"文档 '{image_path}' OCR 结果为空。")
            return []
        logging.info(f"OCR 识别完成，共找到 {len(ocr_results)} 个文本块。")

        # 2. 版面分析 (表格检测)
        table_blocks = self.layout_analyzer.analyze(image_path)
        
        if not table_blocks:
            logging.info(f"文档 '{image_path}' 中未检测到表格。")
            return []

        # 3. 表格解析与内容提取
        extracted_tables = []
        for i, block in enumerate(table_blocks):
            logging.info(f"正在解析表格 {i+1}/{len(table_blocks)}...")
            table_bbox = block.block.box # [x1, y1, x2, y2]
            
            if not (isinstance(table_bbox, (list, tuple)) and len(table_bbox) == 4 and
                    table_bbox[0] < table_bbox[2] and table_bbox[1] < table_bbox[3]):
                logging.warning(f"跳过无效的表格边界框: {table_bbox}")
                continue
                
            df_table = self.table_parser.parse(image_path, table_bbox, ocr_results)
            
            if df_table is not None and not df_table.empty:
                extracted_tables.append(df_table)
                logging.info(f"表格 {i+1} 解析成功，包含 {len(df_table)} 行 {len(df_table.columns) if not df_table.empty else 0} 列。")
            else:
                logging.warning(f"表格 {i+1} (Box: {table_bbox}) 解析失败或结果为空。")
        
        logging.info(f"文档 '{image_path}' 处理完成，共提取 {len(extracted_tables)} 个表格。")
        return extracted_tables

    def save_tables(self, tables: List[pd.DataFrame], output_prefix: str = "output_table"):
        import os
        for idx, table in enumerate(tables):
            output_path = f"{output_prefix}_{idx+1}.csv"
            table.to_csv(output_path, index=False)
            logging.info(f"表格已保存到: {output_path}")