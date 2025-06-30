#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数库
"""

import os
import yaml
import logging
from transformers import AutoModel, AutoTokenizer, AutoConfig
import layoutparser as lp
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path="config/config.yaml"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def get_paddleocr_kwargs(config: dict) -> dict:
    ocr_config = config.get("ocr_engine", {})
    # 示例：根据配置返回 lang 和 use_gpu
    # 实际应用中可能需要更复杂的逻辑来处理模型路径、设备等
    return {
        "lang": ocr_config.get("lang", "ch"),
        "use_gpu": ocr_config.get("use_gpu", False),
        # 添加其他 PaddleOCR 初始化参数，例如 model_dir, det_model_dir, rec_model_dir 等
        # "det_model_dir": ocr_config.get("det_model_dir"),
        # "rec_model_dir": ocr_config.get("rec_model_dir"),
        # "cls_model_dir": ocr_config.get("cls_model_dir"),
    }
