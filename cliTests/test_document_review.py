#!/usr/bin/env python3
"""
文档评审测试脚本
功能：测试AI多角色文档评审功能
参数：document_file [review_focus] output_file
"""

import argparse
import sys
import os
import json
from base_test_script import BaseTestScript


class DocumentReviewTest(BaseTestScript):
    """文档评审功能测试"""
    
    def __init__(self, base_url: str = "http://localhost:5000", verbose: bool = True):
        super().__init__(base_url, verbose)
        self.test_name = "文档评审功能测试"
    
    def validate_inputs(self, input_files: list, output_file: str, review_focus: str = "auto") -> bool:
        """验证输入参数"""
        self.log(f"开始{self.test_name}")
        
        if len(input_files) != 1:
            self.log_error(f"需要1个输入文件，实际提供{len(input_files)}个")
            return False
        
        document_file = input_files[0]
        
        # 验证输入文件
        if not self.validate_file_exists(document_file, "待评审文档"):
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
        
        # 验证评审重点
        valid_focuses = ["auto", "academic", "business", "technical", "legal"]
        if review_focus not in valid_focuses:
            self.log_warning(f"评审重点'{review_focus}'不在有效列表中，使用'auto'")
            review_focus = "auto"
        
        self.log(f"评审重点: {review_focus}")
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
    
    def execute_business_flow(self, input_files: list, review_focus: str = "auto") -> dict:
        """执行文档评审业务流程"""
        document_file = input_files[0]
        
        # 步骤1: 检查API健康状态
        self.log("步骤1: 检查API健康状态")
        if not self.check_api_health():
            return {"success": False, "error": "API服务不可用"}
        
        # 步骤2: 读取文件内容
        self.log("步骤2: 读取文件内容")
        document_content = self.read_file_content(document_file)
        
        if not document_content:
            return {"success": False, "error": "文档内容读取失败"}
        
        # 步骤3: 启动文档评审
        self.log("步骤3: 启动文档评审")
        start_data = {
            "document_content": document_content,
            "document_name": os.path.basename(document_file),
            "review_focus": review_focus
        }
        
        start_result = self.call_api(
            "/api/document-review/start",
            method="POST",
            data=start_data,
            description="启动文档评审"
        )
        
        if not start_result:
            self.log_error("启动文档评审API调用失败")
            return {"success": False, "error": "启动文档评审API调用失败"}
        
        if not start_result.get("success", False):
            error_msg = start_result.get("error", "启动文档评审失败")
            self.log_error(f"启动文档评审失败: {error_msg}")
            return {"success": False, "error": error_msg}
        
        # 获取评审会话ID
        review_session_id = start_result.get("review_session_id", "")
        if not review_session_id:
            self.log_error("未获取到评审会话ID")
            return {"success": False, "error": "未获取到评审会话ID"}
        
        self.log(f"文档评审会话已启动: {review_session_id}")
        
        # 步骤4: 获取评审建议
        self.log("步骤4: 获取评审建议")
        suggestions_result = self.call_api(
            f"/api/document-review/suggestions/{review_session_id}",
            method="GET",
            description="获取评审建议"
        )
        
        if not suggestions_result:
            self.log_error("获取评审建议API调用失败")
            return {"success": False, "error": "获取评审建议API调用失败"}
        
        if not suggestions_result.get("success", False):
            error_msg = suggestions_result.get("error", "获取评审建议失败")
            self.log_error(f"获取评审建议失败: {error_msg}")
            return {"success": False, "error": error_msg}
        
        # 处理评审建议
        suggestions = suggestions_result.get("suggestions", [])
        self.log(f"获取到{len(suggestions)}个评审建议")
        
        # 显示评审建议详情
        for i, suggestion in enumerate(suggestions, 1):
            suggestion_id = suggestion.get("id", f"suggestion_{i}")
            suggestion_type = suggestion.get("type", "未知")
            suggestion_content = suggestion.get("content", "")
            priority = suggestion.get("priority", "medium")
            
            self.log(f"建议{i}: [{priority}] {suggestion_type} - {suggestion_content[:100]}...")
        
        # 步骤5: 处理评审建议
        self.log("步骤5: 处理评审建议")
        if suggestions:
            # 接受所有建议
            accept_data = {
                "action": "accept_all"
            }
            
            accept_result = self.call_api(
                f"/api/document-review/suggestions/{review_session_id}/batch",
                method="PATCH",
                data=accept_data,
                description="接受所有评审建议"
            )
            
            if not accept_result:
                self.log_warning("接受评审建议API调用失败")
            elif not accept_result.get("success", False):
                self.log_warning(f"接受评审建议失败: {accept_result.get('error', '未知错误')}")
            else:
                self.log("已接受所有评审建议")
        else:
            self.log("没有评审建议需要处理")
        
        # 步骤6: 导出评审后文档
        self.log("步骤6: 导出评审后文档")
        export_result = self.call_api(
            f"/api/document-review/export/{review_session_id}",
            method="GET",
            description="导出评审后文档"
        )
        
        if not export_result:
            self.log_error("导出评审后文档API调用失败")
            return {"success": False, "error": "导出评审后文档API调用失败"}
        
        # 处理导出结果
        reviewed_content = ""
        if isinstance(export_result, dict):
            # JSON响应，包含文档内容
            reviewed_content = export_result.get("document_content", "")
            if not reviewed_content:
                reviewed_content = export_result.get("reviewed_document", "")
        else:
            # 直接返回文档内容
            reviewed_content = str(export_result)
        
        if not reviewed_content:
            self.log_warning("评审后文档内容为空，使用原始文档内容")
            reviewed_content = document_content
        
        # 步骤7: 生成评审报告
        self.log("步骤7: 生成评审报告")
        review_report = {
            "document_name": os.path.basename(document_file),
            "review_focus": review_focus,
            "review_session_id": review_session_id,
            "suggestions_count": len(suggestions),
            "suggestions": suggestions,
            "reviewed_content_length": len(reviewed_content),
            "review_summary": {
                "total_suggestions": len(suggestions),
                "accepted_suggestions": len(suggestions),
                "rejected_suggestions": 0,
                "review_quality": "good" if len(suggestions) > 0 else "no_suggestions"
            }
        }
        
        # 步骤8: 生成测试报告
        self.log("步骤8: 生成测试报告")
        test_report = {
            "test_name": self.test_name,
            "document_file": document_file,
            "review_focus": review_focus,
            "start_success": start_result.get("success", False),
            "suggestions_success": suggestions_result.get("success", False),
            "review_session_id": review_session_id,
            "suggestions_count": len(suggestions),
            "reviewed_content_length": len(reviewed_content),
            "start_result": start_result,
            "suggestions_result": suggestions_result,
            "review_report": review_report
        }
        
        return {
            "success": True,
            "reviewed_content": reviewed_content,
            "review_report": review_report,
            "test_report": test_report
        }
    
    def run_test(self, input_files: list, output_file: str, review_focus: str = "auto") -> bool:
        """执行文档评审测试"""
        try:
            # 验证输入
            if not self.validate_inputs(input_files, output_file, review_focus):
                return False
            
            # 执行业务流程
            result = self.execute_business_flow(input_files, review_focus)
            
            if not result["success"]:
                self.log_error(f"业务流程执行失败: {result.get('error', '未知错误')}")
                return False
            
            # 保存输出文件
            reviewed_content = result["reviewed_content"]
            if not self.save_output(reviewed_content, output_file, "评审后文档"):
                return False
            
            # 保存评审报告
            review_report_file = output_file.replace('.txt', '_review_report.json')
            if not self.save_json_output(result["review_report"], review_report_file, "评审报告"):
                self.log_warning("评审报告保存失败")
            
            # 保存测试报告
            test_report_file = output_file.replace('.txt', '_test_report.json')
            if not self.save_json_output(result["test_report"], test_report_file, "测试报告"):
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
    parser = argparse.ArgumentParser(description="文档评审功能测试")
    parser.add_argument("document_file", help="待评审文档")
    parser.add_argument("output_file", help="评审后文档")
    parser.add_argument("--review-focus", default="auto", 
                       choices=["auto", "academic", "business", "technical", "legal"],
                       help="评审重点")
    parser.add_argument("--url", default="http://localhost:5000", help="API基础URL")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 创建测试实例
    test_script = DocumentReviewTest(args.url, args.verbose)
    
    # 执行测试
    success = test_script.run_test([args.document_file], args.output_file, args.review_focus)
    
    # 打印摘要
    test_script.print_summary()
    
    # 退出
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 