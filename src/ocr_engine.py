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
        """
        识别图像中的文本，返回文本列表及位置信息。
        返回格式: [ {'text': text, 'box': [x1,y1,x2,y1,x2,y2,x1,y2], 'confidence': score} ]
        """
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
