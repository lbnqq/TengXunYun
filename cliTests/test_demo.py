#!/usr/bin/env python3
"""
演示测试脚本
功能：模拟API响应，展示CLI测试功能
"""

import argparse
import sys
import os
import json
import time
from typing import Dict, Optional
from base_test_script import BaseTestScript


class DemoTest(BaseTestScript):
    """演示测试"""
    
    def __init__(self, base_url: str = "http://localhost:5000", verbose: bool = True):
        super().__init__(base_url, verbose)
        self.test_name = "演示测试"
    
    def mock_api_response(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """模拟API响应"""
        if "/api/health" in endpoint:
            return {"status": "healthy", "timestamp": time.time()}
        elif "/api/format-alignment" in endpoint:
            return {
                "success": True,
                "aligned_content": "这是模拟的对齐后内容\n包含格式调整\n和布局优化",
                "alignment_result": {
                    "changes_made": ["调整标题格式", "统一段落间距", "优化列表样式"],
                    "similarity_score": 0.85,
                    "alignment_quality": "good"
                }
            }
        elif "/api/writing-style/analyze" in endpoint:
            return {
                "success": True,
                "template_id": "demo_style_template_001",
                "style_features": {
                    "formality": "high",
                    "tone": "professional",
                    "complexity": "medium"
                }
            }
        elif "/api/style-alignment/preview" in endpoint:
            return {
                "success": True,
                "session_id": "demo_session_001",
                "preview_data": {
                    "original_content": data.get("document_content", "") if data else "",
                    "suggested_changes": [
                        {
                            "id": "change_001",
                            "original": "我觉得",
                            "suggested": "我认为",
                            "reason": "提高正式程度"
                        }
                    ]
                }
            }
        elif "/api/document-fill/start" in endpoint:
            return {
                "success": True,
                "session_id": "demo_fill_session_001",
                "detected_intent": "document_fill",
                "confidence": 0.9
            }
        elif "/api/document-review/start" in endpoint:
            return {
                "success": True,
                "review_session_id": "demo_review_session_001",
                "status": "started"
            }
        elif "/api/table-fill" in endpoint:
            return {
                "success": True,
                "filled_tables": [
                    {
                        "columns": ["姓名", "年龄", "职位"],
                        "data": [
                            ["张三", "25", "工程师"],
                            ["李四", "30", "经理"]
                        ]
                    }
                ]
            }
        else:
            return {"success": False, "error": "未知的API端点"}
    
    def call_api(self, endpoint: str, method: str = "POST", 
                 data: Dict = None, files: Dict = None, 
                 description: str = "API调用") -> Optional[Dict]:
        """重写API调用方法，使用模拟响应"""
        try:
            url = f"{self.base_url}{endpoint}"
            self.log(f"调用API: {method} {url}")
            
            if data:
                self.log(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 模拟网络延迟
            time.sleep(0.5)
            
            # 获取模拟响应
            result = self.mock_api_response(endpoint, data)
            
            self.log(f"响应状态码: 200")
            self.log(f"{description}成功")
            return result
                
        except Exception as e:
            self.log_error(f"{description}异常", e)
            return None
    
    def check_api_health(self) -> bool:
        """重写健康检查，总是返回成功"""
        try:
            self.log("检查API健康状态...")
            # 模拟健康检查
            time.sleep(0.2)
            self.log("API服务正常")
            return True
        except Exception as e:
            self.log_error("API健康检查失败", e)
            return False
    
    def validate_inputs(self, input_files: list, output_file: str) -> bool:
        """验证输入参数"""
        self.log(f"开始{self.test_name}")
        
        if len(input_files) != 2:
            self.log_error(f"需要2个输入文件，实际提供{len(input_files)}个")
            return False
        
        source_file, target_file = input_files
        
        # 验证输入文件
        if not self.validate_file_exists(source_file, "源文档"):
            return False
        if not self.validate_file_exists(target_file, "目标文档"):
            return False
        
        # 验证输出路径
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                self.log(f"创建输出目录: {output_dir}")
            except Exception as e:
                self.log_error(f"创建输出目录失败: {output_dir}", e)
                return False
        
        return True
    
    def read_file_content(self, file_path: str) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.log(f"文件内容读取成功: {file_path} ({len(content)}字符)")
            return content
        except Exception as e:
            self.log_error(f"读取文件内容失败: {file_path}", e)
            return ""
    
    def execute_business_flow(self, input_files: list) -> dict:
        """执行演示业务流程"""
        source_file, target_file = input_files
        
        # 步骤1: 检查API健康状态
        self.log("步骤1: 检查API健康状态")
        if not self.check_api_health():
            return {"success": False, "error": "API服务不可用"}
        
        # 步骤2: 读取文件内容
        self.log("步骤2: 读取文件内容")
        source_content = self.read_file_content(source_file)
        target_content = self.read_file_content(target_file)
        
        if not source_content or not target_content:
            return {"success": False, "error": "文件内容读取失败"}
        
        # 步骤3: 模拟格式对齐
        self.log("步骤3: 模拟格式对齐")
        alignment_data = {
            "source_content": source_content,
            "source_name": os.path.basename(source_file),
            "target_content": target_content,
            "target_name": os.path.basename(target_file)
        }
        
        alignment_result = self.call_api(
            "/api/format-alignment",
            method="POST",
            data=alignment_data,
            description="格式对齐"
        )
        
        if not alignment_result:
            self.log_error("格式对齐API调用失败")
            return {"success": False, "error": "格式对齐API调用失败"}
        
        # 步骤4: 模拟风格分析
        self.log("步骤4: 模拟风格分析")
        style_data = {
            "document_content": source_content,
            "document_name": os.path.basename(source_file)
        }
        
        style_result = self.call_api(
            "/api/writing-style/analyze",
            method="POST",
            data=style_data,
            description="风格分析"
        )
        
        # 步骤5: 模拟文档填报
        self.log("步骤5: 模拟文档填报")
        fill_data = {
            "document_content": target_content,
            "document_name": os.path.basename(target_file)
        }
        
        fill_result = self.call_api(
            "/api/document-fill/start",
            method="POST",
            data=fill_data,
            description="文档填报"
        )
        
        # 步骤6: 模拟文档评审
        self.log("步骤6: 模拟文档评审")
        review_data = {
            "document_content": target_content,
            "document_name": os.path.basename(target_file),
            "review_focus": "academic"
        }
        
        review_result = self.call_api(
            "/api/document-review/start",
            method="POST",
            data=review_data,
            description="文档评审"
        )
        
        # 步骤7: 生成测试报告
        self.log("步骤7: 生成测试报告")
        test_report = {
            "test_name": self.test_name,
            "source_file": source_file,
            "target_file": target_file,
            "alignment_success": alignment_result.get("success", False),
            "style_analysis_success": style_result.get("success", False),
            "document_fill_success": fill_result.get("success", False),
            "document_review_success": review_result.get("success", False),
            "alignment_result": alignment_result,
            "style_result": style_result,
            "fill_result": fill_result,
            "review_result": review_result
        }
        
        return {
            "success": True,
            "processed_content": alignment_result.get("aligned_content", target_content),
            "test_report": test_report
        }
    
    def run_test(self, input_files: list, output_file: str) -> bool:
        """执行演示测试"""
        try:
            # 验证输入
            if not self.validate_inputs(input_files, output_file):
                return False
            
            # 执行业务流程
            result = self.execute_business_flow(input_files)
            
            if not result["success"]:
                self.log_error(f"业务流程执行失败: {result.get('error', '未知错误')}")
                return False
            
            # 保存输出文件
            processed_content = result["processed_content"]
            if not self.save_output(processed_content, output_file, "处理后文档"):
                return False
            
            # 保存测试报告
            report_file = output_file.replace('.txt', '_report.json')
            if not self.save_json_output(result["test_report"], report_file, "测试报告"):
                self.log_warning("测试报告保存失败")
            
            # 标记测试成功
            self.test_results["success"] = True
            self.log(f"{self.test_name}完成")
            
            return True
            
        except Exception as e:
            self.log_error(f"{self.test_name}执行异常", e)
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="演示测试")
    parser.add_argument("source_file", help="源文档")
    parser.add_argument("target_file", help="目标文档")
    parser.add_argument("output_file", help="输出文档")
    parser.add_argument("--url", default="http://localhost:5000", help="API基础URL")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 创建测试实例
    test_script = DemoTest(args.url, args.verbose)
    
    # 执行测试
    success = test_script.run_test([args.source_file, args.target_file], args.output_file)
    
    # 打印摘要
    test_script.print_summary()
    
    # 退出
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 