#!/usr/bin/env python3
"""
格式对齐测试脚本
功能：测试格式对齐功能
"""

import argparse
import sys
import os
import json
import time
from typing import Dict, Optional

# 修复导入路径
try:
    from .base_test_script import BaseTestScript
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from cliTests.base_test_script import BaseTestScript


class FormatAlignmentTest(BaseTestScript):
    """格式对齐功能测试"""
    
    def __init__(self, base_url: str = "http://localhost:5000", verbose: bool = True):
        super().__init__(base_url, verbose)
        self.test_name = "格式对齐功能测试"
    
    def validate_inputs(self, input_files: list, output_file: str) -> bool:
        """验证输入参数"""
        self.log(f"开始{self.test_name}")
        
        if len(input_files) != 2:
            self.log_error(f"需要2个输入文件，实际提供{len(input_files)}个")
            return False
        
        source_file, target_file = input_files
        
        # 验证输入文件
        if not self.validate_file_exists(source_file, "参考格式文档"):
            return False
        if not self.validate_file_exists(target_file, "待处理文档"):
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
        """执行格式对齐业务流程"""
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
        
        # 步骤3: 调用格式对齐API
        self.log("步骤3: 调用格式对齐API")
        alignment_data = {
            "source_content": source_content,
            "source_name": os.path.basename(source_file),
            "target_content": target_content,
            "target_name": os.path.basename(target_file)
        }
        
        # 尝试直接调用格式对齐API
        alignment_result = self.call_api(
            "/api/format-alignment",
            method="POST",
            data=alignment_data,
            description="格式对齐"
        )
        
        if not alignment_result:
            self.log_error("格式对齐API调用失败")
            return {"success": False, "error": "格式对齐API调用失败"}
        
        # 检查响应格式
        if not self.validate_response(alignment_result, ["success"]):
            return {"success": False, "error": "格式对齐响应格式错误"}
        
        if not alignment_result.get("success", False):
            error_msg = alignment_result.get("error", "格式对齐失败")
            self.log_error(f"格式对齐失败: {error_msg}")
            return {"success": False, "error": error_msg}
        
        # 步骤4: 处理对齐结果
        self.log("步骤4: 处理对齐结果")
        aligned_content = alignment_result.get("aligned_content", "")
        alignment_details = alignment_result.get("alignment_result", {})
        
        if not aligned_content:
            self.log_warning("对齐结果为空")
            aligned_content = target_content  # 使用原始内容作为备选
        
        # 步骤5: 生成测试报告
        self.log("步骤5: 生成测试报告")
        test_report = {
            "test_name": self.test_name,
            "source_file": source_file,
            "target_file": target_file,
            "alignment_success": alignment_result.get("success", False),
            "aligned_content_length": len(aligned_content),
            "alignment_details": alignment_details,
            "api_response": alignment_result
        }
        
        return {
            "success": True,
            "aligned_content": aligned_content,
            "test_report": test_report
        }
    
    def run_test(self, input_files: list, output_file: str) -> bool:
        """执行格式对齐测试"""
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
            aligned_content = result["aligned_content"]
            if not self.save_output(aligned_content, output_file, "对齐后文档"):
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
    parser = argparse.ArgumentParser(description="格式对齐功能测试")
    parser.add_argument("source_file", help="参考格式文档")
    parser.add_argument("target_file", help="待处理文档")
    parser.add_argument("output_file", help="对齐后文档")
    parser.add_argument("--url", default="http://localhost:5000", help="API基础URL")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 创建测试实例
    test_script = FormatAlignmentTest(args.url, args.verbose)
    
    # 执行测试
    success = test_script.run_test([args.source_file, args.target_file], args.output_file)
    
    # 打印摘要
    test_script.print_summary()
    
    # 退出
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 