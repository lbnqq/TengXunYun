#!/usr/bin/env python3
"""
表格填充测试脚本
功能：测试智能表格批量填充功能
参数：table_file data_file output_file
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


class TableFillTest(BaseTestScript):
    """表格填充功能测试"""
    
    def __init__(self, base_url: str = "http://localhost:5000", verbose: bool = True):
        super().__init__(base_url, verbose)
        self.test_name = "表格填充功能测试"
    
    def validate_inputs(self, input_files: list, output_file: str) -> bool:
        """验证输入参数"""
        self.log(f"开始{self.test_name}")
        
        if len(input_files) != 2:
            self.log_error(f"需要2个输入文件，实际提供{len(input_files)}个")
            return False
        
        table_file, data_file = input_files
        
        # 验证输入文件
        if not self.validate_file_exists(table_file, "表格定义文件"):
            return False
        if not self.validate_file_exists(data_file, "填充数据文件"):
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
    
    def validate_table_structure(self, table_data: dict) -> bool:
        """验证表格结构"""
        if not isinstance(table_data, dict):
            self.log_error("表格数据必须是字典格式")
            return False
        
        if "tables" not in table_data:
            self.log_error("表格数据缺少'tables'字段")
            return False
        
        tables = table_data["tables"]
        if not isinstance(tables, list):
            self.log_error("'tables'字段必须是列表格式")
            return False
        
        for i, table in enumerate(tables):
            if not isinstance(table, dict):
                self.log_error(f"表格{i}必须是字典格式")
                return False
            
            if "columns" not in table:
                self.log_error(f"表格{i}缺少'columns'字段")
                return False
            
            if "data" not in table:
                self.log_error(f"表格{i}缺少'data'字段")
                return False
            
            columns = table["columns"]
            data = table["data"]
            
            if not isinstance(columns, list):
                self.log_error(f"表格{i}的'columns'必须是列表格式")
                return False
            
            if not isinstance(data, list):
                self.log_error(f"表格{i}的'data'必须是列表格式")
                return False
            
            # 验证每行数据的列数是否与列定义一致
            for j, row in enumerate(data):
                if not isinstance(row, list):
                    self.log_error(f"表格{i}第{j}行数据必须是列表格式")
                    return False
                
                if len(row) != len(columns):
                    self.log_error(f"表格{i}第{j}行数据列数({len(row)})与列定义({len(columns)})不一致")
                    return False
        
        self.log(f"表格结构验证通过: {len(tables)}个表格")
        return True
    
    def validate_fill_data(self, fill_data: dict) -> bool:
        """验证填充数据"""
        if not isinstance(fill_data, dict):
            self.log_error("填充数据必须是字典格式")
            return False
        
        if "fill_data" not in fill_data:
            self.log_error("填充数据缺少'fill_data'字段")
            return False
        
        data_list = fill_data["fill_data"]
        if not isinstance(data_list, list):
            self.log_error("'fill_data'字段必须是列表格式")
            return False
        
        for i, item in enumerate(data_list):
            if not isinstance(item, dict):
                self.log_error(f"填充数据第{i}项必须是字典格式")
                return False
        
        self.log(f"填充数据验证通过: {len(data_list)}条数据")
        return True
    
    def execute_business_flow(self, input_files: list) -> dict:
        """执行表格填充业务流程"""
        table_file, data_file = input_files
        
        # 步骤1: 检查API健康状态
        self.log("步骤1: 检查API健康状态")
        if not self.check_api_health():
            return {"success": False, "error": "API服务不可用"}
        
        # 步骤2: 读取文件内容
        self.log("步骤2: 读取文件内容")
        table_data = self.read_json_data(table_file)
        fill_data = self.read_json_data(data_file)
        
        if not table_data:
            return {"success": False, "error": "表格定义文件读取失败"}
        
        if not fill_data:
            return {"success": False, "error": "填充数据文件读取失败"}
        
        # 步骤3: 验证数据结构
        self.log("步骤3: 验证数据结构")
        if not self.validate_table_structure(table_data):
            return {"success": False, "error": "表格结构验证失败"}
        
        if not self.validate_fill_data(fill_data):
            return {"success": False, "error": "填充数据验证失败"}
        
        # 步骤4: 调用表格填充API
        self.log("步骤4: 调用表格填充API")
        api_data = {
            "tables": table_data["tables"],
            "fill_data": fill_data["fill_data"]
        }
        
        fill_result = self.call_api(
            "/api/table-fill",
            method="POST",
            data=api_data,
            description="表格填充"
        )
        
        if not fill_result:
            self.log_error("表格填充API调用失败")
            return {"success": False, "error": "表格填充API调用失败"}
        
        if not fill_result.get("success", False):
            error_msg = fill_result.get("error", "表格填充失败")
            self.log_error(f"表格填充失败: {error_msg}")
            return {"success": False, "error": error_msg}
        
        # 步骤5: 处理填充结果
        self.log("步骤5: 处理填充结果")
        filled_tables = fill_result.get("filled_tables", [])
        
        if not filled_tables:
            self.log_warning("填充结果为空")
            filled_tables = table_data["tables"]  # 使用原始表格作为备选
        
        # 步骤6: 生成填充结果报告
        self.log("步骤6: 生成填充结果报告")
        fill_report = {
            "original_tables_count": len(table_data["tables"]),
            "filled_tables_count": len(filled_tables),
            "fill_data_count": len(fill_data["fill_data"]),
            "fill_success": fill_result.get("success", False),
            "original_tables": table_data["tables"],
            "filled_tables": filled_tables,
            "fill_data": fill_data["fill_data"]
        }
        
        # 步骤7: 生成测试报告
        self.log("步骤7: 生成测试报告")
        test_report = {
            "test_name": self.test_name,
            "table_file": table_file,
            "data_file": data_file,
            "fill_success": fill_result.get("success", False),
            "original_tables_count": len(table_data["tables"]),
            "filled_tables_count": len(filled_tables),
            "fill_data_count": len(fill_data["fill_data"]),
            "fill_result": fill_result,
            "fill_report": fill_report
        }
        
        return {
            "success": True,
            "filled_tables": filled_tables,
            "fill_report": fill_report,
            "test_report": test_report
        }
    
    def save_filled_tables(self, filled_tables: list, output_file: str) -> bool:
        """保存填充后的表格"""
        try:
            output_data = {
                "filled_tables": filled_tables,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "table_count": len(filled_tables)
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            self.log(f"填充后表格保存成功: {output_file}")
            return True
            
        except Exception as e:
            self.log_error(f"保存填充后表格失败", e)
            return False
    
    def run_test(self, input_files: list, output_file: str) -> bool:
        """执行表格填充测试"""
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
            filled_tables = result["filled_tables"]
            if not self.save_filled_tables(filled_tables, output_file):
                return False
            
            # 保存填充报告
            fill_report_file = output_file.replace('.json', '_fill_report.json')
            if not self.save_json_output(result["fill_report"], fill_report_file, "填充报告"):
                self.log_warning("填充报告保存失败")
            
            # 保存测试报告
            test_report_file = output_file.replace('.json', '_test_report.json')
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
    parser = argparse.ArgumentParser(description="表格填充功能测试")
    parser.add_argument("table_file", help="表格定义文件(JSON)")
    parser.add_argument("data_file", help="填充数据文件(JSON)")
    parser.add_argument("output_file", help="填充后表格文件(JSON)")
    parser.add_argument("--url", default="http://localhost:5000", help="API基础URL")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 创建测试实例
    test_script = TableFillTest(args.url, args.verbose)
    
    # 执行测试
    success = test_script.run_test([args.table_file, args.data_file], args.output_file)
    
    # 打印摘要
    test_script.print_summary()
    
    # 退出
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 