#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
布局分析器

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
import layoutparser as lp
from typing import Dict, Any

class LayoutAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.layout_config = config.get("layout_analyzer", {})
        self.hf_model_id = self.layout_config.get("hf_model_id")
        self.model_type = self.layout_config.get("model_type", "hf")
        self.cache_dir = self.layout_config.get("cache_dir")
        self.label_map = self.layout_config.get("label_map", {})
        self.detection_threshold = self.layout_config.get("detection_threshold", 0.3)

        if not self.hf_model_id:
            raise ValueError("Layout Analyzer model ID (hf_model_id) not specified in config.")
        if not self.cache_dir:
            raise ValueError("Layout Analyzer cache directory (cache_dir) not specified in config.")

        os.makedirs(self.cache_dir, exist_ok=True)
        logging.info(f"LayoutAnalyzer: Model '{self.hf_model_id}' will use cache dir '{self.cache_dir}'")

        self.model = self._load_model()

    def _load_model(self):
        model = lp.Detectron2LayoutModel(
            self.hf_model_id,
            extra_config=None,
            label_map=self.label_map,
            enforce_cpu=False,
            config_path=None,
            cache_dir=self.cache_dir,
        )
        return model