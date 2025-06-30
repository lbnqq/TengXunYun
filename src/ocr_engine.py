#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR引擎

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""














import os
import cv2
import logging
from paddleocr import PaddleOCR
from typing import List, Dict, Any

class PaddleOCRWrapper:
    def __init__(self, lang='ch', use_gpu=False, **kwargs):
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=use_gpu, **kwargs)
        logging.info(f"PaddleOCR initialized with lang='{lang}', use_gpu={use_gpu}")

    def recognize(self, image_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(image_path):
            logging.error(f"OCR 错误: 文件 '{image_path}' 不存在。")
            return []

        try:
            result = self.ocr_engine.ocr(image_path, cls=True)
            
            extracted_texts = []
            if result and result[0]:
                for line in result[0]:
                    if line:
                        bbox = [int(coord) for coord in line[0]]
                        text = line[1][0]
                        confidence = line[1][1]
                        extracted_texts.append({
                            "text": text,
                            "box": bbox,
                            "confidence": confidence
                        })
            return extracted_texts
        except Exception as e:
            logging.error(f"OCR 过程中发生错误: {e}")
            return []
