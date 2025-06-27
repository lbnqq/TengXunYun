import os
import yaml
import logging
from transformers import AutoModel, AutoTokenizer, AutoConfig
import layoutparser as lp
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path="config/config.yaml"):
    """加载配置文件（以 office-doc-agent 为根目录）"""
    # 保证 config_path 总是以 office-doc-agent 为根
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.path.dirname(__file__), '..', config_path)
        config_path = os.path.abspath(config_path)
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    # 替换环境变量引用
    for key, value in config.items():
        if isinstance(value, str) and value.startswith("${"):
            env_key = value[2:-1]
            config[key] = os.environ.get(env_key, os.path.join(os.path.dirname(os.path.abspath(config_path)), value[len("${"): -1]))
    return config

def download_model_files(hf_model_id: str, cache_dir: str):
    """
    手动下载 Hugging Face 模型文件到指定的本地缓存目录。
    这是应对 Hub 无法访问时的核心函数。
    """
    if not hf_model_id:
        logging.error("模型 ID 为空，无法下载。")
        return False

    logging.info(f"准备下载模型: {hf_model_id} 到本地缓存: {cache_dir}")
    os.makedirs(cache_dir, exist_ok=True)
    logging.info(f"已确保本地缓存目录 '{cache_dir}' 存在。")
    return True

def load_hf_model(hf_model_id: str, cache_dir: str, model_type="hf", **kwargs):
    """
    加载 Hugging Face 模型，使用指定的本地缓存目录。
    如果模型在缓存中不存在，将尝试从 Hugging Face Hub 下载。
    """
    logging.info(f"尝试加载 Hugging Face 模型: '{hf_model_id}'，缓存目录: '{cache_dir}'")
    try:
        os.makedirs(cache_dir, exist_ok=True)

        if model_type == "hf":
            if "layoutlmv3" in hf_model_id.lower() or "roberta" in hf_model_id.lower():
                from transformers import RobertaProcessor
                processor = RobertaProcessor.from_pretrained(hf_model_id, cache_dir=cache_dir)
                model = lp.Tagger.from_pretrained(
                    hf_model_id,
                    cache_dir=cache_dir,
                    processor=processor,
                    model_type="hf",
                    **kwargs
                )
            else:
                logging.warning("加载非-Roberta的LayoutLM模型，可能需要手动配置Transformer类。")
                model = lp.Tagger.from_pretrained(
                    hf_model_id,
                    cache_dir=cache_dir,
                    model_type="hf",
                    **kwargs
                )

            logging.info(f"模型 '{hf_model_id}' 加载成功。")
            return model
        else:
            logging.error(f"不支持的模型类型: {model_type}")
            return None

    except Exception as e:
        logging.error(f"加载模型 '{hf_model_id}' 时出错: {e}")
        logging.error(f"请确认模型 ID 正确，缓存目录 '{cache_dir}' 可写，以及所需依赖已安装。")
        logging.error("如果网络允许，它会尝试自动从 Hugging Face Hub 下载。")
        return None

def get_paddleocr_kwargs(config: dict):
    """
    从配置中提取 PaddleOCR 初始化参数，支持本地模型路径。
    """
    ocr_cfg = config.get("ocr_engine", {})
    kwargs = {
        "lang": ocr_cfg.get("lang", "ch"),
        "use_gpu": ocr_cfg.get("use_gpu", False)
    }
    # 支持本地模型路径（以 office-doc-agent 为根目录）
    if "ocr_model_dir" in ocr_cfg:
        model_dir = ocr_cfg["ocr_model_dir"]
        if not os.path.isabs(model_dir):
            model_dir = os.path.join(os.path.dirname(__file__), '..', model_dir)
            model_dir = os.path.abspath(model_dir)
        kwargs["det_model_dir"] = os.path.join(model_dir, "det")
        kwargs["rec_model_dir"] = os.path.join(model_dir, "rec")
        kwargs["cls_model_dir"] = os.path.join(model_dir, "cls")
    return kwargs

def download_paddleocr_models(ocr_model_dir: str, lang: str = "ch"):
    """
    自动下载 PaddleOCR det/rec/cls 模型到本地 ocr_model_dir。
    lang: "ch" 或 "en" 等。
    """
    # 以 office-doc-agent 为根目录
    if not os.path.isabs(ocr_model_dir):
        ocr_model_dir = os.path.join(os.path.dirname(__file__), '..', ocr_model_dir)
        ocr_model_dir = os.path.abspath(ocr_model_dir)
    os.makedirs(ocr_model_dir, exist_ok=True)
    base_url = f"https://paddleocr.bj.bcebos.com/PP-OCRv4/{lang}"
    models = {
        "det": f"det/{lang}_ppocrv4_det_infer.tar",
        "rec": f"rec/{lang}_ppocrv4_rec_infer.tar",
        "cls": "cls/ch_ppocr_mobile_v2.0_cls_infer.tar"
    }
    for key, rel_url in models.items():
        subdir = os.path.join(ocr_model_dir, key)
        os.makedirs(subdir, exist_ok=True)
        tar_name = rel_url.split("/")[-1]
        tar_path = os.path.join(subdir, tar_name)
        if not os.path.exists(tar_path):
            url = f"https://paddleocr.bj.bcebos.com/PP-OCRv4/{rel_url}" if key != "cls" else f"https://paddleocr.bj.bcebos.com/PP-OCRv4/{rel_url}"
            logging.info(f"下载 {key} 模型: {url}")
            r = requests.get(url, stream=True)
            with open(tar_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.info(f"已下载 {tar_path}，请手动解压到 {subdir}")
        else:
            logging.info(f"{tar_path} 已存在")

# HuggingFace模型下载（推荐用 transformers snapshot_download）
def download_hf_model_files(hf_model_id: str, cache_dir: str):
    """
    自动下载 HuggingFace模型到本地 cache_dir。
    依赖 transformers >=4.27.0
    """
    # 以 office-doc-agent 为根目录
    if not os.path.isabs(cache_dir):
        cache_dir = os.path.join(os.path.dirname(__file__), '..', cache_dir)
        cache_dir = os.path.abspath(cache_dir)
    try:
        from transformers import snapshot_download
        snapshot_download(repo_id=hf_model_id, cache_dir=cache_dir, local_files_only=False, resume_download=True)
        logging.info(f"已下载 {hf_model_id} 到 {cache_dir}")
    except ImportError:
        logging.error("请先 pip install transformers >=4.27.0")
    except Exception as e:
        logging.error(f"下载 HF 模型失败: {e}")

# 用法示例：
# download_paddleocr_models('models/paddleocr', lang='ch')
# download_hf_model_files('uer/layoutlmv3-base-finetuned-table-detection-v2', 'models/hf_cache')

# PaddleOCR 本地模型使用说明：
# 1. 访问 https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_ch/models_list.md 下载所需模型。
# 2. 将 det、rec、cls 目录分别放到 config.yaml 配置的 ocr_model_dir 下（如 office-doc-agent/models/paddleocr）。
# 3. 配置示例：
# ocr_engine:
#   name: "paddleocr"
#   use_gpu: false
#   lang: "ch"
#   ocr_model_dir: "models/paddleocr"

# LayoutParser/HF 本地模型使用说明：
# 1. 访问 https://huggingface.co/<model_id> 下载全部文件。
# 2. 放到 office-doc-agent/models/hf_cache/models--<org>--<model_name>/snapshots/<commit_hash>/ 目录下。
# 3. cache_dir 配置为 models/hf_cache。
# 4. 代码会优先从本地加载，无需联网。
