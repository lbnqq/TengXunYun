#!/usr/bin/env python3
"""
基础测试脚本类
提供通用的API调用、文件处理和测试框架
"""

import os
import sys
import json
import time
import requests
import traceback
from typing import Dict, List, Any, Optional
from pathlib import Path


class BaseTestScript:
    """基础测试脚本类"""
    
    def __init__(self, base_url: str = "http://localhost:5000", verbose: bool = True):
        """
        初始化测试脚本
        
        Args:
            base_url: API基础URL
            verbose: 是否输出详细日志
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.verbose = verbose
        self.test_results = {
            "start_time": time.time(),
            "steps": [],
            "errors": [],
            "warnings": [],
            "success": False
        }
        
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = time.strftime("%H:%M:%S")
        if self.verbose:
            print(f"[{timestamp}] {level}: {message}")
        
        self.test_results["steps"].append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })
    
    def log_error(self, message: str, error: Exception = None):
        """记录错误"""
        error_info = {
            "message": message,
            "error_type": type(error).__name__ if error else None,
            "error_details": str(error) if error else None,
            "traceback": traceback.format_exc() if error else None
        }
        self.test_results["errors"].append(error_info)
        self.log(f"ERROR: {message}", "ERROR")
        if error:
            self.log(f"Exception: {str(error)}", "ERROR")
    
    def log_warning(self, message: str):
        """记录警告"""
        self.test_results["warnings"].append({"message": message})
        self.log(f"WARNING: {message}", "WARN")
    
    def validate_file_exists(self, file_path: str, description: str = "文件") -> bool:
        """验证文件是否存在"""
        if not os.path.exists(file_path):
            self.log_error(f"{description}不存在: {file_path}")
            return False
        if not os.path.isfile(file_path):
            self.log_error(f"{description}不是文件: {file_path}")
            return False
        self.log(f"{description}验证通过: {file_path}")
        return True
    
    def validate_output_path(self, output_path: str) -> bool:
        """验证输出路径"""
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                self.log(f"创建输出目录: {output_dir}")
            except Exception as e:
                self.log_error(f"创建输出目录失败: {output_dir}", e)
                return False
        return True
    
    def upload_file(self, file_path: str, description: str = "文件") -> Optional[Dict]:
        """上传文件到服务器"""
        try:
            self.log(f"开始上传{description}: {file_path}")
            
            if not self.validate_file_exists(file_path, description):
                return None
            
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'text/plain')}
                response = self.session.post(f"{self.base_url}/api/upload", files=files, timeout=30)
            
            if response.status_code != 200:
                self.log_error(f"上传{description}失败: HTTP {response.status_code}")
                return None
            
            result = response.json()
            if not result.get('success', False):
                self.log_error(f"上传{description}失败: {result.get('error', '未知错误')}")
                return None
            
            self.log(f"{description}上传成功: {result.get('filename', 'unknown')}")
            return result
            
        except Exception as e:
            self.log_error(f"上传{description}异常", e)
            return None
    
    def call_api(self, endpoint: str, method: str = "POST", 
                 data: Dict = None, files: Dict = None, 
                 description: str = "API调用") -> Optional[Dict]:
        """通用API调用方法"""
        try:
            url = f"{self.base_url}{endpoint}"
            self.log(f"调用API: {method} {url}")
            
            if data:
                self.log(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if method.upper() == "GET":
                response = self.session.get(url, params=data, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, files=files, timeout=30)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data, timeout=30)
            else:
                self.log_error(f"不支持的HTTP方法: {method}")
                return None
            
            self.log(f"响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                self.log_error(f"{description}失败: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
                except:
                    self.log(f"错误响应: {response.text}")
                return None
            
            try:
                result = response.json()
                self.log(f"{description}成功")
                return result
            except Exception as e:
                self.log_error(f"解析响应JSON失败", e)
                return None
                
        except Exception as e:
            self.log_error(f"{description}异常", e)
            return None
    
    def call_api_with_file(self, endpoint: str, method: str = "POST", 
                          file_path: str = None, file_field: str = "file",
                          data: Dict = None, description: str = "API调用") -> Optional[Dict]:
        """支持文件上传的API调用方法（优化版）"""
        try:
            url = f"{self.base_url}{endpoint}"
            self.log(f"调用API: {method} {url}")
            
            if not self.validate_file_exists(file_path, description):
                return None
            
            # 准备文件数据（优化：确保文件内容在内存中可用）
            files = {}
            if file_path:
                # 读取文件内容到内存中，确保在整个请求过程中可用
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    # 获取文件MIME类型
                    file_ext = os.path.splitext(file_path)[1].lower()
                    mime_type = self._get_mime_type(file_ext)
                    
                    files[file_field] = (os.path.basename(file_path), file_content, mime_type)
                    self.log(f"文件已加载到内存: {os.path.basename(file_path)} ({len(file_content)} bytes)")
                    
                except Exception as e:
                    self.log_error(f"读取文件失败: {str(e)}")
                    return None
            
            # 准备表单数据
            form_data = {}
            if data:
                form_data.update(data)
                self.log(f"表单数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if method.upper() == "POST":
                response = self.session.post(url, data=form_data, files=files, timeout=30)
            else:
                self.log_error(f"不支持的HTTP方法: {method}")
                return None
            
            self.log(f"响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                self.log_error(f"{description}失败: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
                except:
                    self.log(f"错误响应: {response.text}")
                return None
            
            try:
                result = response.json()
                self.log(f"{description}成功")
                return result
            except Exception as e:
                self.log_error(f"解析响应JSON失败", e)
                return None
                
        except Exception as e:
            self.log_error(f"{description}异常", e)
            return None
    
    def _get_mime_type(self, file_ext: str) -> str:
        """
        根据文件扩展名获取MIME类型
        
        Args:
            file_ext: 文件扩展名（包含点号）
            
        Returns:
            MIME类型字符串
        """
        mime_types = {
            '.txt': 'text/plain',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.pdf': 'application/pdf',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.csv': 'text/csv',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.ppt': 'application/vnd.ms-powerpoint'
        }
        
        return mime_types.get(file_ext.lower(), 'application/octet-stream')
    
    def save_output(self, content: str, output_path: str, description: str = "输出文件") -> bool:
        """保存输出文件"""
        try:
            if not self.validate_output_path(output_path):
                return False
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log(f"{description}保存成功: {output_path}")
            return True
            
        except Exception as e:
            self.log_error(f"保存{description}失败", e)
            return False
    
    def save_json_output(self, data: Dict, output_path: str, description: str = "JSON输出") -> bool:
        """保存JSON输出文件"""
        try:
            if not self.validate_output_path(output_path):
                return False
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.log(f"{description}保存成功: {output_path}")
            return True
            
        except Exception as e:
            self.log_error(f"保存{description}失败", e)
            return False
    
    def validate_response(self, response: Dict, required_fields: List[str] = None) -> bool:
        """验证API响应"""
        if not response:
            self.log_error("响应为空")
            return False
        
        if not isinstance(response, dict):
            self.log_error(f"响应格式错误，期望dict，实际{type(response)}")
            return False
        
        if required_fields:
            for field in required_fields:
                if field not in response:
                    self.log_error(f"响应缺少必需字段: {field}")
                    return False
        
        self.log("响应验证通过")
        return True
    
    def check_api_health(self) -> bool:
        """检查API健康状态"""
        try:
            self.log("检查API健康状态...")
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                self.log("API服务正常")
                return True
            else:
                self.log_error(f"API服务异常: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error("API健康检查失败", e)
            return False
    
    def generate_test_report(self, output_dir: str = "test_results") -> str:
        """生成测试报告"""
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            self.test_results["end_time"] = time.time()
            self.test_results["duration"] = self.test_results["end_time"] - self.test_results["start_time"]
            self.test_results["success"] = len(self.test_results["errors"]) == 0
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(output_dir, f"test_report_{timestamp}.json")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            # 生成简化的控制台报告
            self.print_summary()
            
            return report_file
            
        except Exception as e:
            self.log_error("生成测试报告失败", e)
            return ""
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("测试摘要")
        print("="*60)
        print(f"测试结果: {'成功' if self.test_results['success'] else '失败'}")
        print(f"执行时间: {self.test_results.get('duration', 0):.2f}秒")
        print(f"执行步骤: {len(self.test_results['steps'])}")
        print(f"错误数量: {len(self.test_results['errors'])}")
        print(f"警告数量: {len(self.test_results['warnings'])}")
        
        if self.test_results['errors']:
            print("\n错误详情:")
            for i, error in enumerate(self.test_results['errors'], 1):
                print(f"  {i}. {error['message']}")
                if error.get('error_details'):
                    print(f"     详情: {error['error_details']}")
        
        if self.test_results['warnings']:
            print("\n警告详情:")
            for i, warning in enumerate(self.test_results['warnings'], 1):
                print(f"  {i}. {warning['message']}")
        
        print("="*60)
    
    def run_test(self, input_files: List[str], output_file: str) -> bool:
        """
        执行测试流程（子类需要重写）
        
        Args:
            input_files: 输入文件列表
            output_file: 输出文件路径
            
        Returns:
            bool: 测试是否成功
        """
        raise NotImplementedError("子类必须实现run_test方法") 