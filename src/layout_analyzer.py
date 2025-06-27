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
            raise ValueError("Layout Analyzer 模型 ID (hf_model_id) 未在配置中指定。")
        if not self.cache_dir:
            raise ValueError("Layout Analyzer 缓存目录 (cache_dir) 未在配置中指定。")

        os.makedirs(self.cache_dir, exist_ok=True)
        logging.info(f"LayoutAnalyzer: 模型 '{self.hf_model_id}' 将使用缓存目录 '{self.cache_dir}'")

        self.model = self._load_model()

    def _load_model(self):
        """加载模型，优先使用本地缓存"""
        from utils import load_hf_model
        model = load_hf_model(
            hf_model_id=self.hf_model_id,
            cache_dir=self.cache_dir,
            model_type=self.model_type,
            label_map=self.label_map,
            threshold=self.detection_threshold
        )
        if model is None:
            raise RuntimeError("Layout Analyzer 模型加载失败。请检查配置和日志。")
        return model

    def analyze(self, image_path: str) -> lp.Layout:
        """
        分析图像版面，返回包含检测到的元素（包括表格）的 Layout 对象。
        """
        if not os.path.exists(image_path):
            logging.error(f"LayoutAnalyzer 错误: 文件 '{image_path}' 不存在。")
            return lp.Layout()

        try:
            image = cv2.imread(image_path)
            if image is None:
                logging.error(f"LayoutAnalyzer 错误: 无法读取图像文件 '{image_path}'。")
                return lp.Layout()

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # 使用 Tagger 进行推断
            layout = self.model.detect(image_rgb)
            
            # 筛选出表格类型的块
            table_blocks = lp.Layout([b for b in layout if b.type == 'Table'])
            logging.info(f"LayoutAnalyzer: 在 '{image_path}' 中检测到 {len(table_blocks)} 个表格区域。")
            return table_blocks

        except Exception as e:
            logging.error(f"LayoutAnalyzer 分析过程中发生错误: {e}")
            return lp.Layout()
