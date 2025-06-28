#!/usr/bin/env python3
"""
智能填报测试脚本
功能：测试文档智能填报功能
参数：template_file data_file output_file
"""

import argparse
import sys
import os
import json
from base_test_script import BaseTestScript


class DocumentFillTest(BaseTestScript):
    """智能填报功能测试"""
    
    def __init__(self, base_url: str = "http://localhost:5000", verbose: bool = True):
        super().__init__(base_url, verbose)
        self.test_name = "智能填报功能测试"
    
    def validate_inputs(self, input_files: list, output_file: str) -> bool:
        """验证输入参数"""
        self.log(f"开始{self.test_name}")
        
        if len(input_files) != 2:
            self.log_error(f"需要2个输入文件，实际提供{len(input_files)}个")
            return False
        
        template_file, data_file = input_files
        
        # 验证输入文件
        if not self.validate_file_exists(template_file, "文档模板"):
            return False
        if not self.validate_file_exists(data_file, "数据源文件"):
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
    
    def read_json_data(self, file_path: str) -> dict:
        """读取JSON数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.log(f"JSON数据读取成功: {file_path}")
            return data
        except Exception as e:
            self.log_error(f"读取JSON数据失败: {file_path}", e)
            return {}
    
    def execute_business_flow(self, input_files: list) -> dict:
        """执行智能填报业务流程"""
        template_file, data_file = input_files
        
        # 步骤1: 检查API健康状态
        self.log("步骤1: 检查API健康状态")
        if not self.check_api_health():
            return {"success": False, "error": "API服务不可用"}
        
        # 步骤2: 读取文件内容
        self.log("步骤2: 读取文件内容")
        template_content = self.read_file_content(template_file)
        data_content = self.read_json_data(data_file)
        
        if not template_content:
            return {"success": False, "error": "模板文件内容读取失败"}
        
        if not data_content:
            return {"success": False, "error": "数据文件内容读取失败"}
        
        # 步骤3: 启动文档填报流程
        self.log("步骤3: 启动文档填报流程")
        start_data = {
            "document_content": template_content,
            "document_name": os.path.basename(template_file)
        }
        
        start_result = self.call_api(
            "/api/document-fill/start",
            method="POST",
            data=start_data,
            description="启动文档填报"
        )
        
        if not start_result:
            self.log_error("启动文档填报API调用失败")
            return {"success": False, "error": "启动文档填报API调用失败"}
        
        if not start_result.get("success", False):
            error_msg = start_result.get("error", "启动文档填报失败")
            self.log_error(f"启动文档填报失败: {error_msg}")
            return {"success": False, "error": error_msg}
        
        # 获取会话ID
        session_id = start_result.get("session_id", "")
        if not session_id:
            self.log_error("未获取到会话ID")
            return {"success": False, "error": "未获取到会话ID"}
        
        self.log(f"文档填报会话已启动: {session_id}")
        
        # 步骤4: 自动匹配数据
        self.log("步骤4: 自动匹配数据")
        # 将数据转换为API期望的格式
        data_sources = []
        if isinstance(data_content, dict):
            # 如果是字典，转换为文本格式
            data_text = json.dumps(data_content, ensure_ascii=False, indent=2)
            data_sources.append({
                "type": "text",
                "content": data_text,
                "name": os.path.basename(data_file)
            })
        elif isinstance(data_content, list):
            # 如果是列表，每个元素作为一个数据源
            for i, item in enumerate(data_content):
                data_sources.append({
                    "type": "text",
                    "content": json.dumps(item, ensure_ascii=False),
                    "name": f"{os.path.basename(data_file)}_item_{i}"
                })
        else:
            # 其他格式，直接转换为文本
            data_sources.append({
                "type": "text",
                "content": str(data_content),
                "name": os.path.basename(data_file)
            })
        
        auto_match_data = {
            "session_id": session_id,
            "data_sources": data_sources
        }
        
        auto_match_result = self.call_api(
            "/api/document-fill/auto-match",
            method="POST",
            data=auto_match_data,
            description="自动匹配数据"
        )
        
        if not auto_match_result:
            self.log_error("自动匹配数据API调用失败")
            return {"success": False, "error": "自动匹配数据API调用失败"}
        
        if not auto_match_result.get("success", False):
            error_msg = auto_match_result.get("error", "自动匹配数据失败")
            self.log_error(f"自动匹配数据失败: {error_msg}")
            return {"success": False, "error": error_msg}
        
        # 处理匹配结果
        matched_fields = auto_match_result.get("matched_fields", {})
        unmatched_fields = auto_match_result.get("unmatched_fields", [])
        conflicts = auto_match_result.get("conflicts", [])
        
        self.log(f"自动匹配完成: 匹配字段{len(matched_fields)}个, 未匹配字段{len(unmatched_fields)}个")
        
        # 步骤5: 处理冲突（如果有）
        if conflicts:
            self.log("步骤5: 处理数据冲突")
            conflict_resolutions = {}
            for conflict in conflicts:
                # 简单处理：选择第一个值
                field_id = conflict.get("field_id", "")
                values = conflict.get("values", [])
                if values:
                    conflict_resolutions[field_id] = values[0]
                    self.log(f"解决冲突: 字段{field_id} -> {values[0]}")
            
            if conflict_resolutions:
                resolve_data = {
                    "resolutions": conflict_resolutions
                }
                
                resolve_result = self.call_api(
                    f"/api/document-fill/auto-match/conflicts/{session_id}",
                    method="PATCH",
                    data=resolve_data,
                    description="解决数据冲突"
                )
                
                if not resolve_result:
                    self.log_warning("解决冲突API调用失败")
                elif not resolve_result.get("success", False):
                    self.log_warning(f"解决冲突失败: {resolve_result.get('error', '未知错误')}")
        
        # 步骤6: 获取填报结果
        self.log("步骤6: 获取填报结果")
        result_data = {
            "session_id": session_id
        }
        
        fill_result = self.call_api(
            "/api/document-fill/result",
            method="GET",
            data=result_data,
            description="获取填报结果"
        )
        
        if not fill_result:
            self.log_error("获取填报结果API调用失败")
            return {"success": False, "error": "获取填报结果API调用失败"}
        
        # 处理填报结果
        filled_content = ""
        if isinstance(fill_result, dict):
            filled_content = fill_result.get("document_content", "")
            if not filled_content:
                filled_content = fill_result.get("filled_document", "")
        else:
            filled_content = str(fill_result)
        
        if not filled_content:
            self.log_warning("填报结果为空，使用原始模板内容")
            filled_content = template_content
        
        # 步骤7: 下载填报文档
        self.log("步骤7: 下载填报文档")
        download_data = {
            "session_id": session_id
        }
        
        download_result = self.call_api(
            "/api/document-fill/download",
            method="GET",
            data=download_data,
            description="下载填报文档"
        )
        
        if download_result and isinstance(download_result, dict):
            download_content = download_result.get("document_content", "")
            if download_content:
                filled_content = download_content
                self.log("使用下载的文档内容")
        
        # 步骤8: 生成测试报告
        self.log("步骤8: 生成测试报告")
        test_report = {
            "test_name": self.test_name,
            "template_file": template_file,
            "data_file": data_file,
            "start_success": start_result.get("success", False),
            "auto_match_success": auto_match_result.get("success", False),
            "session_id": session_id,
            "matched_fields_count": len(matched_fields),
            "unmatched_fields_count": len(unmatched_fields),
            "conflicts_count": len(conflicts),
            "filled_content_length": len(filled_content),
            "start_result": start_result,
            "auto_match_result": auto_match_result,
            "fill_result": fill_result
        }
        
        return {
            "success": True,
            "filled_content": filled_content,
            "test_report": test_report
        }
    
    def run_test(self, input_files: list, output_file: str) -> bool:
        """执行智能填报测试"""
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
            filled_content = result["filled_content"]
            if not self.save_output(filled_content, output_file, "填报后文档"):
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
    parser = argparse.ArgumentParser(description="智能填报功能测试")
    parser.add_argument("template_file", help="文档模板")
    parser.add_argument("data_file", help="数据源文件")
    parser.add_argument("output_file", help="填报后文档")
    parser.add_argument("--url", default="http://localhost:5000", help="API基础URL")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 创建测试实例
    test_script = DocumentFillTest(args.url, args.verbose)
    
    # 执行测试
    success = test_script.run_test([args.template_file, args.data_file], args.output_file)
    
    # 打印摘要
    test_script.print_summary()
    
    # 退出
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 