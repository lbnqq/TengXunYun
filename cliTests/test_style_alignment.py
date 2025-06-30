#!/usr/bin/env python3
"""
文风对齐测试脚本
功能：测试文风对齐功能
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


class StyleAlignmentTest(BaseTestScript):
    """文风统一功能测试"""
    
    def __init__(self, base_url: str = "http://localhost:5000", verbose: bool = True):
        super().__init__(base_url, verbose)
        self.test_name = "文风统一功能测试"
    
    def validate_inputs(self, input_files: list, output_file: str) -> bool:
        """验证输入参数"""
        self.log(f"开始{self.test_name}")
        
        if len(input_files) != 2:
            self.log_error(f"需要2个输入文件，实际提供{len(input_files)}个")
            return False
        
        reference_file, target_file = input_files
        
        # 验证输入文件
        if not self.validate_file_exists(reference_file, "参考风格文档"):
            return False
        if not self.validate_file_exists(target_file, "待调整文档"):
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
            # 检查文件扩展名
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.docx':
                # 对于docx文件，我们不需要读取内容，直接使用文件路径
                # 因为API会处理docx文件
                self.log(f"检测到docx文件: {file_path}，将直接使用文件路径")
                return f"[DOCX_FILE:{file_path}]"
            else:
                # 对于文本文件，正常读取
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.log(f"文件内容读取成功: {file_path} ({len(content)}字符)")
                return content
        except Exception as e:
            self.log_error(f"读取文件内容失败: {file_path}", e)
            return ""
    
    def execute_business_flow(self, input_files: list, output_file: str) -> dict:
        """执行文风统一业务流程"""
        reference_file, target_file = input_files
        
        # 步骤1: 检查API健康状态
        self.log("步骤1: 检查API健康状态")
        if not self.check_api_health():
            return {"success": False, "error": "API服务不可用"}
        
        # 步骤2: 读取文件内容
        self.log("步骤2: 读取文件内容")
        reference_content = self.read_file_content(reference_file)
        target_content = self.read_file_content(target_file)
        
        if not reference_content or not target_content:
            return {"success": False, "error": "文件内容读取失败"}
        
        # 步骤3: 分析参考文档风格
        self.log("步骤3: 分析参考文档风格")
        
        # 使用multipart/form-data格式上传文件
        style_analysis_result = self.call_api_with_file(
            "/api/writing-style/analyze",
            method="POST",
            file_path=reference_file,
            file_field="file",
            description="风格分析"
        )
        
        if not style_analysis_result:
            self.log_error("风格分析API调用失败")
            return {"success": False, "error": "风格分析API调用失败"}
        
        if not style_analysis_result.get("success", False):
            error_msg = style_analysis_result.get("error", "风格分析失败")
            self.log_error(f"风格分析失败: {error_msg}")
            return {"success": False, "error": error_msg}
        
        # 获取风格模板ID
        style_template_id = style_analysis_result.get("template_id", "")
        if not style_template_id:
            self.log_warning("未获取到风格模板ID，尝试使用默认模板")
            # 尝试获取可用的风格模板
            templates_result = self.call_api(
                "/api/writing-style/templates",
                method="GET",
                description="获取风格模板列表"
            )
            
            if templates_result and templates_result.get("templates"):
                style_template_id = templates_result["templates"][0].get("id", "")
                self.log(f"使用默认风格模板: {style_template_id}")
            else:
                self.log_error("无法获取风格模板")
                return {"success": False, "error": "无法获取风格模板"}
        
        # 步骤4: 预览风格变化
        self.log("步骤4: 预览风格变化")
        
        # 检查目标文件类型
        target_file_ext = os.path.splitext(target_file)[1].lower()
        
        if target_file_ext == '.docx':
            # 对于docx文件，使用文件上传
            preview_result = self.call_api_with_file(
                "/api/style-alignment/preview",
                method="POST",
                file_path=target_file,
                file_field="file",
                data={
                    "style_template_id": style_template_id
                },
                description="风格变化预览(docx文件)"
            )
        else:
            # 对于文本文件，使用内容传递
            preview_data = {
                "document_content": target_content,
                "document_name": os.path.basename(target_file),
                "style_template_id": style_template_id
            }
            
            preview_result = self.call_api(
                "/api/style-alignment/preview",
                method="POST",
                data=preview_data,
                description="风格变化预览"
            )
        
        if not preview_result:
            self.log_error("风格变化预览API调用失败")
            return {"success": False, "error": "风格变化预览API调用失败"}
        
        if not preview_result.get("success", False):
            error_msg = preview_result.get("error", "风格变化预览失败")
            self.log_error(f"风格变化预览失败: {error_msg}")
            return {"success": False, "error": error_msg}
        
        # 获取会话ID和预览数据
        session_id = preview_result.get("session_id", "")
        preview_data = preview_result.get("preview_data", {})
        
        if not session_id:
            self.log_error("未获取到会话ID")
            return {"success": False, "error": "未获取到会话ID"}
        
        # 步骤5: 接受所有风格变化
        self.log("步骤5: 接受所有风格变化")
        accept_data = {
            "action": "accept_all"
        }
        
        accept_result = self.call_api(
            f"/api/style-alignment/changes/{session_id}/batch",
            method="PATCH",
            data=accept_data,
            description="接受所有风格变化"
        )
        
        if not accept_result:
            self.log_error("接受风格变化API调用失败")
            return {"success": False, "error": "接受风格变化API调用失败"}
        
        if not accept_result.get("success", False):
            error_msg = accept_result.get("error", "接受风格变化失败")
            self.log_error(f"接受风格变化失败: {error_msg}")
            return {"success": False, "error": error_msg}
        
        # 步骤6: 导出统一风格文档
        self.log("步骤6: 导出统一风格文档")
        
        # 调用导出API，支持文件流
        export_url = f"{self.base_url}/api/style-alignment/export/{session_id}"
        self.log(f"调用API: GET {export_url}")
        
        try:
            response = self.session.get(export_url, stream=True, timeout=30)
            self.log(f"响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                self.log_error(f"导出失败，状态码: {response.status_code}")
                return {"success": False, "error": f"导出失败，状态码: {response.status_code}"}
            
            # 根据Content-Type处理响应
            content_type = response.headers.get("Content-Type", "")
            self.log(f"响应Content-Type: {content_type}")
            
            if content_type.startswith("application/vnd.openxmlformats-officedocument.wordprocessingml.document"):
                # 保存docx文件
                docx_filename = response.headers.get("Content-Disposition", "").split("filename=")[-1].strip('"') if "filename=" in response.headers.get("Content-Disposition", "") else f"styled_document_{session_id}.docx"
                docx_path = output_file.replace('.txt', '.docx')
                
                with open(docx_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.log(f"导出docx成功: {docx_path}")
                styled_content = f"[DOCX文件已保存: {docx_path}]"
                
            elif content_type.startswith("text/html"):
                # 保存HTML文件
                html_content = response.text
                html_path = output_file.replace('.txt', '.html')
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                self.log(f"导出HTML成功: {html_path}")
                styled_content = html_content
                
            elif content_type.startswith("application/json"):
                # 解析JSON响应
                try:
                    export_result = response.json()
                    if "error" in export_result:
                        self.log_error(f"导出失败: {export_result['error']}")
                        return {"success": False, "error": export_result['error']}
                    
                    styled_content = export_result.get("document_content", "")
                    if not styled_content:
                        self.log_warning("导出结果为空，使用原始内容")
                        styled_content = target_content
                        
                except json.JSONDecodeError as e:
                    self.log_error(f"解析响应JSON失败: {e}")
                    return {"success": False, "error": f"解析响应JSON失败: {e}"}
                    
            else:
                # 其他类型，直接保存为文本
                styled_content = response.text
                self.log(f"导出文本内容，长度: {len(styled_content)}")
                
        except Exception as e:
            self.log_error(f"导出统一风格文档API调用失败: {e}")
            return {"success": False, "error": f"导出统一风格文档API调用失败: {e}"}
        
        # 步骤7: 生成测试报告
        self.log("步骤7: 生成测试报告")
        test_report = {
            "test_name": self.test_name,
            "reference_file": reference_file,
            "target_file": target_file,
            "style_analysis_success": style_analysis_result.get("success", False),
            "preview_success": preview_result.get("success", False),
            "accept_success": accept_result.get("success", False),
            "export_success": bool(styled_content),
            "style_template_id": style_template_id,
            "session_id": session_id,
            "styled_content_length": len(styled_content),
            "style_analysis_result": style_analysis_result,
            "preview_result": preview_result,
            "accept_result": accept_result
        }
        
        return {
            "success": True,
            "styled_content": styled_content,
            "test_report": test_report
        }
    
    def run_test(self, input_files: list, output_file: str) -> bool:
        """执行文风统一测试"""
        try:
            # 验证输入
            if not self.validate_inputs(input_files, output_file):
                return False
            
            # 执行业务流程
            result = self.execute_business_flow(input_files, output_file)
            
            if not result["success"]:
                self.log_error(f"业务流程执行失败: {result.get('error', '未知错误')}")
                return False
            
            # 保存输出文件
            styled_content = result["styled_content"]
            # 如果styled_content是[DOCX文件已保存: ...]，则不再写入，避免覆盖二进制docx
            if isinstance(styled_content, str) and styled_content.startswith("[DOCX文件已保存:"):
                self.log("已由导出API保存docx文件，无需再次写入")
            else:
                if not self.save_output(styled_content, output_file, "统一风格文档"):
                    return False
            
            # 保存测试报告
            if output_file.endswith('.docx'):
                report_file = output_file.replace('.docx', '_report.json')
            elif output_file.endswith('.txt'):
                report_file = output_file.replace('.txt', '_report.json')
            else:
                report_file = f"{output_file}_report.json"
            
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
    parser = argparse.ArgumentParser(description="文风统一功能测试")
    parser.add_argument("reference_file", help="参考风格文档")
    parser.add_argument("target_file", help="待调整文档")
    parser.add_argument("output_file", help="统一风格后文档")
    parser.add_argument("--url", default="http://localhost:5000", help="API基础URL")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 创建测试实例
    test_script = StyleAlignmentTest(args.url, args.verbose)
    
    # 执行测试
    success = test_script.run_test([args.reference_file, args.target_file], args.output_file)
    
    # 打印摘要
    test_script.print_summary()
    
    # 退出
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 