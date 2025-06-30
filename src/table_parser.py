#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表格解析器

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""










import cv2
import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Any, Tuple
from sklearn.cluster import KMeans

class TableParser:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.table_config = config.get("table_parser", {})
        self.strategy = self.table_config.get("strategy", "ocr_based_rule")

        if self.strategy == "ocr_based_rule":
            logging.info("TableParser 初始化: 使用 OCR-based Rule 策略。")
        else:
            logging.warning(f"TableParser: 未知的解析策略 '{self.strategy}'，将尝试默认行为。")

    def parse(self, image_path: str, table_bbox: Tuple[int, int, int, int], ocr_results: List[Dict[str, Any]]) -> pd.DataFrame:
        if self.strategy == "ocr_based_rule":
            return self._parse_ocr_based(image_path, table_bbox, ocr_results)
        else:
            logging.error(f"TableParser: 不支持的解析策略 '{self.strategy}'")
            return None

    def _parse_ocr_based(self, image_path: str, table_bbox: Tuple[int, int, int, int], ocr_results: List[Dict[str, Any]]) -> pd.DataFrame:
        x1, y1, x2, y2 = table_bbox
        
        # 筛选出在当前表格区域内的 OCR 结果
        relevant_ocr = []
        for item in ocr_results:
            bbox = item['box']
            # 检查 OCR 文本的中心点是否在表格区域内
            cx = (bbox[0] + bbox[2] + bbox[4] + bbox[6]) / 4
            cy = (bbox[1] + bbox[3] + bbox[5] + bbox[7]) / 4
            if x1 <= cx < x2 and y1 <= cy < y2:
                # 将 OCR 框坐标转换为相对于表格区域的坐标
                relative_bbox = [
                    bbox[0] - x1, bbox[1] - y1,
                    bbox[2] - x1, bbox[3] - y1,
                    bbox[4] - x1, bbox[5] - y1,
                    bbox[6] - x1, bbox[7] - y1
                ]
                relevant_ocr.append({
                    "text": item['text'],
                    "box": relative_bbox,
                    "confidence": item['confidence']
                })

        if not relevant_ocr:
            logging.warning(f"在表格区域 {table_bbox} 内未找到相关的 OCR 结果。")
            return pd.DataFrame()

        # 尝试聚类行
        y_centers = np.array([sum(item['box'][1::2]) / len(item['box'][1::2]) for item in relevant_ocr]).reshape(-1, 1)
        
        # 基于行的阈值聚类
        row_threshold = (y2 - y1) * 0.1  # 假设行的间隙阈值是表格高度的10%
        current_row_y_start = relevant_ocr[0]['box'][1]
        current_row_texts = [relevant_ocr[0]]
        rows = []
        
        for i in range(1, len(relevant_ocr)):
            text_item = relevant_ocr[i]
            text_y_center = sum(text_item['box'][1::2]) / len(text_item['box'][1::2])
            
            if text_y_center - current_row_y_start > row_threshold:
                rows.append(current_row_texts)
                current_row_texts = [text_item]
                current_row_y_start = text_y_center
            else:
                current_row_texts.append(text_item)
        rows.append(current_row_texts)  # 添加最后一行

        if not rows:
            logging.warning("未能解析出表格的行结构。")
            return pd.DataFrame()

        # 填充 DataFrame
        max_cols = 0
        table_data = []
        for row_texts in rows:
            row_data = {}
            # 尝试对同一行内的文本按 X 坐标排序作为列
            row_texts.sort(key=lambda x: x['box'][0])
            
            for col_idx, text_item in enumerate(row_texts):
                col_key = f"Col_{col_idx}"
                row_data[col_key] = text_item['text']
                if col_idx + 1 > max_cols:
                    max_cols = col_idx + 1
            
            # 填充空单元格
            for i in range(max_cols):
                col_key = f"Col_{i}"
                if col_key not in row_data:
                    row_data[col_key] = ""
            
            table_data.append(row_data)

        if not table_data:
            logging.warning("未能从行数据生成表格数据。"); return pd.DataFrame()

        df = pd.DataFrame(table_data)
        logging.info(f"成功解析出表格，行数: {len(df)}, 列数: {len(df.columns) if not df.empty else 0}")
        return df
