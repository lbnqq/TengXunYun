import os
import time
import json
import requests
import logging
import hashlib
import threading
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base_llm import BaseLLMClient

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMultiLLMClient(BaseLLMClient):
    """
    增强的多API支持LLM客户端，具备以下特性：
    - 智能重试和错误恢复
    - API性能监控和统计
    - 动态负载均衡
    - 请求缓存机制
    - 详细的错误报告
    """

    def __init__(self, api_config: Optional[Dict] = None):
        super().__init__()

        # API配置
        self.api_config = api_config or self._load_api_config()

        # API端点配置
        self.api_endpoints = {
            'qiniu': {
                'url': 'https://api.qnaigc.com/v1/chat/completions',
                'key': self.api_config.get('QINIU_API_KEY'),
                'group': 'DeepSeek',
                'priority': 1,  # 优先级（数字越小优先级越高）
                'timeout': 60,
                'max_tokens': 4096
            },
            'together': {
                'url': 'https://api.together.xyz/v1/chat/completions',
                'key': self.api_config.get('TOGETHER_API_KEY'),
                'priority': 2,
                'timeout': 120,
                'max_tokens': 8192
            },
            'openrouter': {
                'url': 'https://openrouter.ai/api/v1/chat/completions',
                'key': self.api_config.get('OPENROUTER_API_KEY'),
                'priority': 3,
                'timeout': 120,
                'max_tokens': 8192
            },
            'xingcheng': {
                'url': 'https://spark-api-open.xf-yun.com/v2/chat/completions',
                'base_url': 'https://spark-api-open.xf-yun.com/v2/',
                'key': self.api_config.get('XINGCHENG_API_KEY'),
                'secret': self.api_config.get('XINGCHENG_API_SECRET'),
                'priority': 4,
                'timeout': 120,
                'max_tokens': 4096
            }
        }

        # 默认模型配置
        self.default_models = {
            'qiniu': 'deepseek-v3',
            'together': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
            'openrouter': 'mistralai/mixtral-8x7b-instruct',
            'xingcheng': 'x1'
        }

        # 性能监控
        self.api_stats = {
            endpoint: {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_response_time': 0.0,
                'average_response_time': 0.0,
                'last_success': None,
                'last_failure': None,
                'consecutive_failures': 0,
                'is_healthy': True
            } for endpoint in self.api_endpoints.keys()
        }

        # 智能缓存系统
        self.request_cache = {}
        self.cache_ttl = 300  # 5分钟缓存
        self.cache_lock = threading.RLock()

        # 性能优化配置
        self.max_concurrent_requests = 3
        self.request_timeout_base = 30
        self.adaptive_timeout = True

        # 智能重试配置
        self.max_retries = 3
        self.retry_delays = [1, 2, 4]  # 指数退避
        self.circuit_breaker_threshold = 5  # 连续失败阈值

        # 负载均衡配置
        self.load_balancing_enabled = True
        self.health_check_interval = 60  # 健康检查间隔（秒）
        self.last_health_check = {}

        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_requests)

        # 初始化统计
        available_endpoints = sum(1 for endpoint in self.api_endpoints.values() if endpoint.get('key'))
        logger.info(f"EnhancedMultiLLMClient initialized with {available_endpoints}/{len(self.api_endpoints)} available API endpoints")

        # 启动健康检查
        self._start_health_monitoring()
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        实现BaseLLMClient的generate方法，带有增强的错误处理和性能优化
        """
        messages = [{"role": "user", "content": prompt}]
        model = kwargs.get('model', 'auto')
        options = kwargs.get('options', {})

        # 检查智能缓存
        cache_key = self._generate_cache_key(messages, model, options)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            logger.info("Returning cached response")
            self._update_cache_hit_stats()
            return cached_response

        start_time = time.time()
        try:
            response = self.chat_completion(messages, model, options)
            content = response['choices'][0]['message']['content']

            # 缓存成功的响应
            self._cache_response(cache_key, content)

            # 记录性能指标
            processing_time = time.time() - start_time
            self._record_performance_metrics('generate', processing_time, True)

            return content
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)

            # 记录错误指标
            self._record_performance_metrics('generate', processing_time, False, str(e))

            return error_msg

    def _generate_cache_key(self, messages: List[Dict], model: str, options: Dict) -> str:
        """生成缓存键"""
        import hashlib
        content = json.dumps({
            'messages': messages,
            'model': model,
            'options': options
        }, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """获取缓存的响应"""
        if cache_key in self.request_cache:
            cached_data = self.request_cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached_data['response']
            else:
                # 清理过期缓存
                del self.request_cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response: str):
        """缓存响应"""
        self.request_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now()
        }

        # 简单的缓存清理：如果缓存太大，清理最旧的条目
        if len(self.request_cache) > 100:
            oldest_key = min(self.request_cache.keys(),
                           key=lambda k: self.request_cache[k]['timestamp'])
            del self.request_cache[oldest_key]

    def _update_api_stats(self, endpoint: str, success: bool, response_time: float, error: str = None):
        """更新API统计信息"""
        stats = self.api_stats[endpoint]
        stats['total_requests'] += 1

        if success:
            stats['successful_requests'] += 1
            stats['total_response_time'] += response_time
            stats['average_response_time'] = stats['total_response_time'] / stats['successful_requests']
            stats['last_success'] = datetime.now()
            stats['consecutive_failures'] = 0
            stats['is_healthy'] = True
        else:
            stats['failed_requests'] += 1
            stats['last_failure'] = datetime.now()
            stats['consecutive_failures'] += 1

            # 如果连续失败超过3次，标记为不健康
            if stats['consecutive_failures'] >= 3:
                stats['is_healthy'] = False
                logger.warning(f"API endpoint {endpoint} marked as unhealthy after {stats['consecutive_failures']} consecutive failures")

    def get_api_health_status(self) -> Dict[str, Any]:
        """获取API健康状态"""
        health_status = {}

        for endpoint, stats in self.api_stats.items():
            endpoint_config = self.api_endpoints[endpoint]
            is_configured = bool(endpoint_config.get('key'))

            health_status[endpoint] = {
                'configured': is_configured,
                'healthy': stats['is_healthy'] if is_configured else False,
                'total_requests': stats['total_requests'],
                'success_rate': (stats['successful_requests'] / max(stats['total_requests'], 1)) * 100,
                'average_response_time': stats['average_response_time'],
                'consecutive_failures': stats['consecutive_failures'],
                'last_success': stats['last_success'].isoformat() if stats['last_success'] else None,
                'last_failure': stats['last_failure'].isoformat() if stats['last_failure'] else None
            }

        return health_status

    def get_best_available_endpoints(self) -> List[str]:
        """获取最佳可用的API端点列表，按优先级和健康状态排序"""
        available_endpoints = []

        for endpoint, config in self.api_endpoints.items():
            if config.get('key') and self.api_stats[endpoint]['is_healthy']:
                available_endpoints.append((endpoint, config['priority']))

        # 按优先级排序
        available_endpoints.sort(key=lambda x: x[1])
        return [endpoint for endpoint, _ in available_endpoints]
    
    def _load_api_config(self) -> Dict:
        """从环境变量加载API配置"""
        return {
            'QINIU_API_KEY': os.getenv('QINIU_API_KEY'),
            'TOGETHER_API_KEY': os.getenv('TOGETHER_API_KEY'),
            'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
            'XINGCHENG_API_KEY': os.getenv('XINGCHENG_API_KEY'),
            'XINGCHENG_API_SECRET': os.getenv('XINGCHENG_API_SECRET')
        }
    
    def call_qiniu_api(self, messages: List[Dict], model: str = None, options: Dict = None, max_retries: int = 3) -> Tuple[str, Optional[Dict]]:
        """调用七牛云 DeepSeek API，带有增强的错误处理和统计"""
        endpoint_name = 'qiniu'
        endpoint_config = self.api_endpoints[endpoint_name]

        if not endpoint_config['key']:
            error_msg = "[API Error: Qiniu API key not configured]"
            self._update_api_stats(endpoint_name, False, 0, error_msg)
            return error_msg, None

        headers = {
            "Authorization": f"Bearer {endpoint_config['key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model or self.default_models[endpoint_name],
            "messages": messages,
            "max_tokens": options.get("max_tokens", endpoint_config['max_tokens']) if options else endpoint_config['max_tokens'],
            "temperature": options.get("temperature", 0.7) if options else 0.7,
        }

        start_time = time.time()
        last_error = None

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    endpoint_config['url'],
                    headers=headers,
                    json=payload,
                    timeout=endpoint_config['timeout']
                )
                response.raise_for_status()
                data = response.json()
                content = data['choices'][0]['message']['content']

                if content and content.strip():
                    response_time = time.time() - start_time
                    self._update_api_stats(endpoint_name, True, response_time)
                    logger.info(f"✅ Qiniu DeepSeek success: {len(content)} chars in {response_time:.2f}s")
                    return content, data['choices'][0]['message']
                else:
                    logger.warning(f"⚠️ Empty response from Qiniu DeepSeek on attempt {attempt + 1}")
                    last_error = "Empty response"

            except requests.exceptions.Timeout:
                last_error = f"Timeout after {endpoint_config['timeout']}s"
                logger.warning(f"⏰ Qiniu DeepSeek timeout on attempt {attempt + 1}")
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
                logger.error(f"❌ Qiniu DeepSeek HTTP error on attempt {attempt + 1}: {last_error}")
            except Exception as e:
                last_error = str(e)
                logger.error(f"❌ Qiniu DeepSeek API error on attempt {attempt + 1}: {last_error}")

            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt  # 指数退避
                logger.info(f"Retrying in {sleep_time}s...")
                time.sleep(sleep_time)

        response_time = time.time() - start_time
        error_msg = f"[API Error: Qiniu DeepSeek API failed after {max_retries} attempts. Last error: {last_error}]"
        self._update_api_stats(endpoint_name, False, response_time, error_msg)
        return error_msg, None
    
    def call_together_api(self, messages: List[Dict], model: str = None, options: Dict = None, max_retries: int = 3) -> Tuple[str, Optional[Dict]]:
        """调用 Together.ai API"""
        if not self.api_endpoints['together']['key']:
            return "[API Error: Together.ai API key not configured]", None
            
        headers = {
            "Authorization": f"Bearer {self.api_endpoints['together']['key']}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model or self.default_models['together'],
            "messages": messages,
            "max_tokens": options.get("max_tokens", 4096) if options else 4096,
            "temperature": options.get("temperature", 0.7) if options else 0.7,
            "top_p": options.get("top_p", 0.7) if options else 0.7,
            "top_k": options.get("top_k", 50) if options else 50,
            "repetition_penalty": options.get("repetition_penalty", 1) if options else 1
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_endpoints['together']['url'], 
                    headers=headers, 
                    json=payload, 
                    timeout=120
                )
                response.raise_for_status()
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                if content and content.strip():
                    print(f"✅ Together.ai success: {len(content)} chars")
                    return content, data['choices'][0]['message']
                else:
                    print(f"⚠️ Empty response from Together.ai on attempt {attempt + 1}")
                    
            except Exception as e:
                print(f"❌ Together.ai API error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
        
        return "[API Error: Together.ai API failed]", None
    
    def call_openrouter_api(self, messages: List[Dict], model: str = None, options: Dict = None, max_retries: int = 3) -> Tuple[str, Optional[Dict]]:
        """调用 OpenRouter API"""
        if not self.api_endpoints['openrouter']['key']:
            return "[API Error: OpenRouter API key not configured]", None
            
        headers = {
            "Authorization": f"Bearer {self.api_endpoints['openrouter']['key']}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model or self.default_models['openrouter'],
            "messages": messages,
            "max_tokens": options.get("max_tokens", 4096) if options else 4096,
            "temperature": options.get("temperature", 0.7) if options else 0.7,
            "top_p": options.get("top_p", 0.7) if options else 0.7,
            "top_k": options.get("top_k", 50) if options else 50,
            "repetition_penalty": options.get("repetition_penalty", 1) if options else 1
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_endpoints['openrouter']['url'], 
                    headers=headers, 
                    json=payload, 
                    timeout=120
                )
                response.raise_for_status()
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                if content and content.strip():
                    print(f"✅ OpenRouter success: {len(content)} chars")
                    return content, data['choices'][0]['message']
                else:
                    print(f"⚠️ Empty response from OpenRouter on attempt {attempt + 1}")
                    
            except Exception as e:
                print(f"❌ OpenRouter API error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
        
        return "[API Error: OpenRouter API failed]", None
    
    def call_xingcheng_api(self, messages: List[Dict], model: str = None, options: Dict = None, max_retries: int = 3) -> Tuple[str, Optional[Dict]]:
        """调用星程 API - 使用正确的AK:SK格式认证"""
        endpoint_name = 'xingcheng'
        endpoint_config = self.api_endpoints[endpoint_name]

        if not endpoint_config['key'] or not endpoint_config['secret']:
            error_msg = "[API Error: Xingcheng API key or secret not configured]"
            self._update_api_stats(endpoint_name, False, 0, error_msg)
            return error_msg, None

        # 使用AK:SK格式的Bearer token（科大讯飞标准格式）
        ak_sk_token = f"{endpoint_config['key']}:{endpoint_config['secret']}"
        headers = {
            "Authorization": f"Bearer {ak_sk_token}",
            "Content-Type": "application/json",
        }

        # 构建请求payload，使用OpenAI兼容格式
        payload = {
            "model": model or self.default_models[endpoint_name],
            "messages": messages,
            "max_tokens": options.get("max_tokens", endpoint_config['max_tokens']) if options else endpoint_config['max_tokens'],
            "temperature": options.get("temperature", 0.7) if options else 0.7,
        }

        # 添加可选参数（如果API支持）
        if options:
            if "top_p" in options:
                payload["top_p"] = options["top_p"]
            if "stream" in options:
                payload["stream"] = options["stream"]

        start_time = time.time()
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"Xingcheng API attempt {attempt + 1}/{max_retries}")

                response = requests.post(
                    endpoint_config['url'],
                    headers=headers,
                    json=payload,
                    timeout=endpoint_config['timeout']
                )

                # 详细的错误处理
                if response.status_code == 401:
                    last_error = f"Authentication failed - check API key"
                    logger.error(f"❌ Xingcheng API authentication error: {response.text}")
                elif response.status_code == 400:
                    last_error = f"Bad request - check parameters"
                    logger.error(f"❌ Xingcheng API bad request: {response.text}")
                elif response.status_code == 429:
                    last_error = f"Rate limit exceeded"
                    logger.warning(f"⏰ Xingcheng API rate limit: {response.text}")
                elif response.status_code != 200:
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                    logger.error(f"❌ Xingcheng API HTTP error: {last_error}")
                else:
                    # 成功响应
                    data = response.json()

                    if 'choices' in data and len(data['choices']) > 0:
                        choice = data['choices'][0]
                        if 'message' in choice and 'content' in choice['message']:
                            content = choice['message']['content']

                            if content and content.strip():
                                response_time = time.time() - start_time
                                self._update_api_stats(endpoint_name, True, response_time)
                                logger.info(f"✅ Xingcheng success: {len(content)} chars in {response_time:.2f}s")
                                return content, choice['message']
                            else:
                                last_error = "Empty content in response"
                                logger.warning(f"⚠️ Empty response from Xingcheng on attempt {attempt + 1}")
                        else:
                            last_error = "Invalid response format - missing message/content"
                            logger.error(f"❌ Invalid Xingcheng response format: {data}")
                    else:
                        last_error = "Invalid response format - missing choices"
                        logger.error(f"❌ Invalid Xingcheng response format: {data}")

                # 如果不是最后一次尝试，等待后重试
                if attempt < max_retries - 1:
                    sleep_time = 2 ** attempt  # 指数退避
                    logger.info(f"Retrying Xingcheng API in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    response.raise_for_status()  # 最后一次尝试时抛出异常

            except requests.exceptions.Timeout:
                last_error = f"Timeout after {endpoint_config['timeout']}s"
                logger.warning(f"⏰ Xingcheng API timeout on attempt {attempt + 1}")
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP error: {e}"
                logger.error(f"❌ Xingcheng API HTTP error on attempt {attempt + 1}: {last_error}")
            except Exception as e:
                last_error = str(e)
                logger.error(f"❌ Xingcheng API error on attempt {attempt + 1}: {last_error}")

            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt  # 指数退避
                logger.info(f"Retrying in {sleep_time}s...")
                time.sleep(sleep_time)

        response_time = time.time() - start_time
        error_msg = f"[API Error: Xingcheng API failed after {max_retries} attempts. Last error: {last_error}]"
        self._update_api_stats(endpoint_name, False, response_time, error_msg)
        return error_msg, None
    
    def call_multi_cloud(self, messages: List[Dict], model: str = None, options: Dict = None) -> Tuple[str, Optional[Dict]]:
        """智能负载均衡的多云API调用"""
        if self.load_balancing_enabled:
            return self._call_with_load_balancing(messages, model, options)
        else:
            return self._call_sequential(messages, model, options)

    def _call_with_load_balancing(self, messages: List[Dict], model: str = None, options: Dict = None) -> Tuple[str, Optional[Dict]]:
        """基于负载均衡的API调用"""
        # 获取健康的API端点，按优先级和性能排序
        healthy_apis = self._get_healthy_apis_sorted()

        if not healthy_apis:
            logger.error("No healthy API endpoints available")
            return "[API Error: No healthy endpoints available]", None

        # 尝试调用健康的API
        for api_name in healthy_apis:
            try:
                logger.info(f"Trying {api_name} API (load balanced)")
                content, response_message = self._call_single_api(api_name, messages, model, options)
                if content and not str(content).startswith("[API Error"):
                    logger.info(f"✅ Success with {api_name} API")
                    return content, response_message
            except Exception as e:
                logger.warning(f"❌ {api_name} API failed: {e}")
                continue

        return "[API Error: All healthy endpoints failed]", None

    def _call_sequential(self, messages: List[Dict], model: str = None, options: Dict = None) -> Tuple[str, Optional[Dict]]:
        """顺序调用API（原有逻辑）"""
        api_funcs = [
            ('qiniu', lambda: self.call_qiniu_api(messages, model, options)),
            ('together', lambda: self.call_together_api(messages, model, options)),
            ('openrouter', lambda: self.call_openrouter_api(messages, model, options)),
            ('xingcheng', lambda: self.call_xingcheng_api(messages, model, options))
        ]

        for i, (api_name, api_func) in enumerate(api_funcs):
            if not self.api_endpoints[api_name].get('key'):
                continue

            print(f"Trying {api_name} API ({i+1}/{len(api_funcs)})...")
            content, response_message = api_func()
            if content and not str(content).startswith("[API Error"):
                print(f"✅ Success with {api_name} API")
                return content, response_message

        return "[API Error: All cloud APIs failed]", None

    def _get_healthy_apis_sorted(self) -> List[str]:
        """获取健康的API端点，按性能排序"""
        healthy_apis = []

        for api_name, stats in self.api_stats.items():
            if (stats['is_healthy'] and
                self.api_endpoints[api_name].get('key') and
                stats['consecutive_failures'] < self.circuit_breaker_threshold):

                # 计算API的性能分数（响应时间越短分数越高）
                avg_time = stats.get('average_response_time', float('inf'))
                success_rate = (stats['successful_requests'] / max(stats['total_requests'], 1))
                priority = self.api_endpoints[api_name].get('priority', 10)

                # 综合评分：成功率 * 1000 - 平均响应时间 - 优先级 * 100
                score = success_rate * 1000 - avg_time - priority * 100

                healthy_apis.append((api_name, score))

        # 按分数降序排序
        healthy_apis.sort(key=lambda x: x[1], reverse=True)
        return [api_name for api_name, _ in healthy_apis]

    def _call_single_api(self, api_name: str, messages: List[Dict], model: str = None, options: Dict = None) -> Tuple[str, Optional[Dict]]:
        """调用单个API"""
        if api_name == 'qiniu':
            return self.call_qiniu_api(messages, model, options)
        elif api_name == 'together':
            return self.call_together_api(messages, model, options)
        elif api_name == 'openrouter':
            return self.call_openrouter_api(messages, model, options)
        elif api_name == 'xingcheng':
            return self.call_xingcheng_api(messages, model, options)
        else:
            raise ValueError(f"Unknown API: {api_name}")
    
    def chat_completion(self, messages: List[Dict], model: str = "auto", options: Optional[Dict] = None) -> Dict:
        """
        统一的聊天完成接口
        Args:
            messages: 消息列表
            model: 模型名称，支持以下格式：
                - "auto": 自动选择可用的API
                - "qiniu/deepseek-v3": 指定使用七牛云
                - "together/mistralai/Mixtral-8x7B-Instruct-v0.1": 指定使用Together.ai
                - "openrouter/mistralai/mixtral-8x7b-instruct": 指定使用OpenRouter
                - "xingcheng/x1": 指定使用星程
            options: 选项参数
        """
        if options is None:
            options = {}
        
        print(f"MultiLLMClient: Processing with model '{model}'")
        
        # 解析模型名称
        if model == "auto":
            # 自动模式：依次尝试所有API
            content, response_message = self.call_multi_cloud(messages, None, options)
        elif model.startswith("qiniu/"):
            # 七牛云
            actual_model = model.split('/', 1)[1]
            content, response_message = self.call_qiniu_api(messages, actual_model, options)
        elif model.startswith("together/"):
            # Together.ai
            actual_model = model.split('/', 1)[1]
            content, response_message = self.call_together_api(messages, actual_model, options)
        elif model.startswith("openrouter/"):
            # OpenRouter
            actual_model = model.split('/', 1)[1]
            content, response_message = self.call_openrouter_api(messages, actual_model, options)
        elif model.startswith("xingcheng/"):
            # 星程
            actual_model = model.split('/', 1)[1]
            content, response_message = self.call_xingcheng_api(messages, actual_model, options)
        else:
            # 默认使用自动模式
            content, response_message = self.call_multi_cloud(messages, model, options)
        
        if response_message is None:
            response_message = {"role": "assistant", "content": content}
        
        return {
            "choices": [{
                "message": response_message,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(str(messages)),
                "completion_tokens": len(content),
                "total_tokens": len(str(messages)) + len(content)
            }
        }
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        models = []
        
        if self.api_endpoints['qiniu']['key']:
            models.append("qiniu/deepseek-v3")
        
        if self.api_endpoints['together']['key']:
            models.extend([
                "together/mistralai/Mixtral-8x7B-Instruct-v0.1",
                "together/meta-llama/Llama-2-70b-chat-hf"
            ])
        
        if self.api_endpoints['openrouter']['key']:
            models.extend([
                "openrouter/mistralai/mixtral-8x7b-instruct",
                "openrouter/anthropic/claude-3-opus"
            ])
        
        if self.api_endpoints['xingcheng']['key']:
            models.extend([
                "xingcheng/x1"
            ])
        
        models.append("auto")  # 自动模式
        return models

    # ==================== 新增的优化方法 ====================

    def _generate_cache_key(self, messages: List[Dict], model: str, options: Dict) -> str:
        """生成缓存键"""
        cache_data = {
            'messages': messages,
            'model': model,
            'options': options
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """获取缓存的响应"""
        with self.cache_lock:
            if cache_key in self.request_cache:
                cached_item = self.request_cache[cache_key]
                if time.time() - cached_item['timestamp'] < self.cache_ttl:
                    return cached_item['response']
                else:
                    # 清理过期缓存
                    del self.request_cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response: str):
        """缓存响应"""
        with self.cache_lock:
            self.request_cache[cache_key] = {
                'response': response,
                'timestamp': time.time()
            }

            # 清理过期缓存（简单的LRU策略）
            if len(self.request_cache) > 1000:  # 最大缓存1000条
                self._cleanup_cache()

    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self.request_cache.items()
            if current_time - value['timestamp'] > self.cache_ttl
        ]
        for key in expired_keys:
            del self.request_cache[key]

    def _update_cache_hit_stats(self):
        """更新缓存命中统计"""
        if not hasattr(self, 'cache_stats'):
            self.cache_stats = {'hits': 0, 'misses': 0}
        self.cache_stats['hits'] += 1

    def _record_performance_metrics(self, operation: str, duration: float, success: bool, error: str = None):
        """记录性能指标"""
        if not hasattr(self, 'performance_metrics'):
            self.performance_metrics = {
                'operations': {},
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'average_response_time': 0.0
            }

        # 记录操作级别的指标
        if operation not in self.performance_metrics['operations']:
            self.performance_metrics['operations'][operation] = {
                'count': 0,
                'success_count': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'errors': []
            }

        op_metrics = self.performance_metrics['operations'][operation]
        op_metrics['count'] += 1
        op_metrics['total_time'] += duration
        op_metrics['avg_time'] = op_metrics['total_time'] / op_metrics['count']

        if success:
            op_metrics['success_count'] += 1
            self.performance_metrics['successful_requests'] += 1
        else:
            if error and len(op_metrics['errors']) < 10:  # 保留最近10个错误
                op_metrics['errors'].append({
                    'error': error,
                    'timestamp': datetime.now().isoformat()
                })
            self.performance_metrics['failed_requests'] += 1

        # 更新全局指标
        self.performance_metrics['total_requests'] += 1
        total_time = sum(op['total_time'] for op in self.performance_metrics['operations'].values())
        self.performance_metrics['average_response_time'] = total_time / self.performance_metrics['total_requests']

    def _start_health_monitoring(self):
        """启动健康监控"""
        def health_check():
            while True:
                try:
                    self._perform_health_checks()
                    time.sleep(self.health_check_interval)
                except Exception as e:
                    logger.error(f"Health check error: {e}")
                    time.sleep(self.health_check_interval)

        # 在后台线程中运行健康检查
        health_thread = threading.Thread(target=health_check, daemon=True)
        health_thread.start()

    def _perform_health_checks(self):
        """执行健康检查"""
        for endpoint_name, endpoint_config in self.api_endpoints.items():
            if not endpoint_config.get('key'):
                continue

            # 检查连续失败次数
            stats = self.api_stats[endpoint_name]
            if stats['consecutive_failures'] >= self.circuit_breaker_threshold:
                stats['is_healthy'] = False
                logger.warning(f"Circuit breaker activated for {endpoint_name}")
            else:
                stats['is_healthy'] = True

    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        report = {
            'cache_stats': getattr(self, 'cache_stats', {'hits': 0, 'misses': 0}),
            'performance_metrics': getattr(self, 'performance_metrics', {}),
            'api_stats': self.api_stats,
            'cache_size': len(self.request_cache),
            'healthy_endpoints': sum(1 for stats in self.api_stats.values() if stats['is_healthy'])
        }

        # 计算缓存命中率
        cache_stats = report['cache_stats']
        total_cache_requests = cache_stats['hits'] + cache_stats['misses']
        if total_cache_requests > 0:
            report['cache_hit_rate'] = cache_stats['hits'] / total_cache_requests
        else:
            report['cache_hit_rate'] = 0.0

        return report

    def clear_cache(self):
        """清空缓存"""
        with self.cache_lock:
            self.request_cache.clear()
            logger.info("Cache cleared")

    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        return {
            'healthy_endpoints': [
                name for name, stats in self.api_stats.items()
                if stats['is_healthy'] and self.api_endpoints[name].get('key')
            ],
            'unhealthy_endpoints': [
                name for name, stats in self.api_stats.items()
                if not stats['is_healthy'] and self.api_endpoints[name].get('key')
            ],
            'total_endpoints': len([
                name for name in self.api_endpoints.keys()
                if self.api_endpoints[name].get('key')
            ])
        }


# 向后兼容的类别名
class MultiLLMClient(EnhancedMultiLLMClient):
    """向后兼容的MultiLLMClient类，继承自EnhancedMultiLLMClient"""
    pass