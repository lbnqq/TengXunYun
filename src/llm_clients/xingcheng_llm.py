import os
import json
import requests
from typing import Optional
from dotenv import load_dotenv
from .base_llm import BaseLLMClient

class XingchengLLMClient(BaseLLMClient):
    def __init__(self, api_key: str, api_secret: Optional[str] = None, model_name: str = "x1", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.api_secret = api_secret
        self.model_name = model_name
        self.api_url = "https://spark-api-open.xf-yun.com/v2/chat/completions"
        
        print(f"XingchengLLMClient initialized with model: {self.model_name}")
        print(f"API URL: {self.api_url}")

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Calls the Xingcheng X1 LLM API to generate text.
        根据科大讯飞官方文档: https://www.xfyun.cn/doc/spark/X1http.html
        """
        try:
            # 准备请求数据 - 使用兼容OpenAI的格式
            data = {
                "model": self.model_name,
                "user": kwargs.get('user', 'user123'),
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": kwargs.get('stream', False),
                "temperature": kwargs.get('temperature', 0.7),
                "max_tokens": kwargs.get('max_tokens', 2048)
            }

            # 可选参数：工具配置
            if kwargs.get('enable_web_search', False):
                data["tools"] = [
                    {
                        "type": "web_search",
                        "web_search": {
                            "enable": True,
                            "search_mode": "deep"
                        }
                    }
                ]

            # 设置请求头 - 使用Bearer token认证
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            print(f"--- Calling Xingcheng X1 LLM (Model: {self.model_name}) ---")
            print(f"Prompt: {prompt[:200]}...")
            print(f"API URL: {self.api_url}")

            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print(f"API Response Status: {response.status_code}")
                
                # 提取响应内容 - 兼容OpenAI格式
                if 'choices' in result and len(result['choices']) > 0:
                    choice = result['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        content = choice['message']['content']
                        return content
                    elif 'delta' in choice and 'content' in choice['delta']:
                        # 流式响应处理
                        content = choice['delta']['content']
                        return content
                    else:
                        print(f"Unexpected response format: {result}")
                        return json.dumps({"error": "Unexpected response format"})
                else:
                    print(f"No choices in response: {result}")
                    return json.dumps({"error": "No choices in response"})
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return json.dumps({"error": f"API Error: {response.status_code} - {response.text}"})

        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return json.dumps({"error": f"Request Error: {e}"})
        except Exception as e:
            print(f"Error calling Xingcheng LLM API: {e}")
            return json.dumps({"error": f"Xingcheng API error: {e}"})

    def generate_with_stream(self, prompt: str, **kwargs):
        """
        流式调用API
        """
        kwargs['stream'] = True
        return self.generate(prompt, **kwargs)

    def chat_completion(self, messages, model=None, options=None):
        """
        OpenAI兼容的聊天接口
        """
        prompt = messages[-1]["content"] if messages else ""
        content = self.generate(prompt, model=model or getattr(self, 'model_name', None), options=options or {})
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(str(messages)),
                "completion_tokens": len(content),
                "total_tokens": len(str(messages)) + len(content)
            }
        } 