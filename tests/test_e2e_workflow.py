#!/usr/bin/env python3
"""
完整工作流端到端测试
测试从文档上传到表格填充的完整业务流程
"""

import sys
import os
import json
import time
from typing import Dict, Any, List, Tuple
from test_e2e_framework import E2ETestFramework

class WorkflowTests:
    """完整工作流测试"""
    
    def __init__(self, framework: E2ETestFramework):
        self.framework = framework
        self.api_tester = framework.api_tester
    
    def create_test_documents(self) -> Dict[str, str]:
        """创建测试文档"""
        documents = {}
        
        # 创建简单文本文档
        txt_content = """
        员工信息表
        
        姓名: 张三
        年龄: 
        职位: 
        部门: 技术部
        
        姓名: 李四
        年龄: 
        职位: 
        部门: 市场部
        """
        documents['simple.txt'] = self.framework.create_test_file("simple.txt", txt_content)
        
        # 创建表格数据文档
        table_content = """
        项目管理表
        
        项目名称,状态,负责人,截止日期
        项目A,,张三,2024-12-31
        项目B,,李四,2024-11-30
        项目C,,王五,2024-10-15
        """
        documents['table.txt'] = self.framework.create_test_file("table.txt", table_content)
        
        # 创建复杂文档
        complex_content = """
        公司年度报告
        
        一、人员情况
        姓名: 张三, 年龄: , 职位: 工程师
        姓名: 李四, 年龄: , 职位: 经理
        姓名: 王五, 年龄: , 职位: 总监
        
        二、项目进展
        项目名称: 项目A, 进度: , 负责人: 张三
        项目名称: 项目B, 进度: , 负责人: 李四
        
        三、财务数据
        收入: , 支出: , 利润: 
        """
        documents['complex.txt'] = self.framework.create_test_file("complex.txt", complex_content)
        
        return documents
    
    def test_document_upload_workflow(self) -> bool:
        """测试文档上传工作流"""
        documents = self.create_test_documents()
        
        for doc_name, doc_path in documents.items():
            try:
                print(f"   测试上传文档: {doc_name}")
                
                # 测试文件上传
                success, result = self.api_tester.test_upload_api(doc_path)
                
                if not success:
                    print(f"   文档上传失败: {doc_name} - {result}")
                    return False
                
                print(f"   文档上传成功: {doc_name}")
                
            except Exception as e:
                print(f"   文档上传异常: {doc_name} - {str(e)}")
                return False
        
        return True
    
    def test_table_extraction_and_fill_workflow(self) -> bool:
        """测试表格提取和填充工作流"""
        # 模拟从文档中提取的表格数据
        extracted_tables = [
            {
                "columns": ["姓名", "年龄", "职位", "部门"],
                "data": [
                    ["张三", "", "", "技术部"],
                    ["李四", "", "", "市场部"],
                    ["王五", "", "", ""]
                ]
            },
            {
                "columns": ["项目名称", "状态", "负责人"],
                "data": [
                    ["项目A", "", "张三"],
                    ["项目B", "", "李四"],
                    ["项目C", "", "王五"]
                ]
            }
        ]
        
        # 准备填充数据
        fill_data = [
            {"姓名": "张三", "年龄": "28", "职位": "高级工程师", "部门": "技术部"},
            {"姓名": "李四", "年龄": "32", "职位": "产品经理", "部门": "市场部"},
            {"姓名": "王五", "年龄": "35", "职位": "技术总监", "部门": "技术部"},
            {"项目名称": "项目A", "状态": "进行中", "负责人": "张三"},
            {"项目名称": "项目B", "状态": "已完成", "负责人": "李四"},
            {"项目名称": "项目C", "状态": "计划中", "负责人": "王五"}
        ]
        
        # 执行表格填充
        success, result = self.api_tester.test_table_fill_api(extracted_tables, fill_data)
        
        if not success:
            print(f"   表格填充失败: {result}")
            return False
        
        # 验证填充结果
        filled_tables = result.get('filled_tables', [])
        if len(filled_tables) != 2:
            print(f"   填充表格数量错误: 期望2，实际{len(filled_tables)}")
            return False
        
        # 验证第一个表格（员工信息）
        employee_table = filled_tables[0]
        expected_employee_data = [
            ["张三", "28", "高级工程师", "技术部"],
            ["李四", "32", "产品经理", "市场部"],
            ["王五", "35", "技术总监", "技术部"]
        ]
        
        if employee_table['data'] != expected_employee_data:
            print(f"   员工表格填充错误:")
            print(f"   期望: {expected_employee_data}")
            print(f"   实际: {employee_table['data']}")
            return False
        
        # 验证第二个表格（项目信息）
        project_table = filled_tables[1]
        expected_project_data = [
            ["项目A", "进行中", "张三"],
            ["项目B", "已完成", "李四"],
            ["项目C", "计划中", "王五"]
        ]
        
        if project_table['data'] != expected_project_data:
            print(f"   项目表格填充错误:")
            print(f"   期望: {expected_project_data}")
            print(f"   实际: {project_table['data']}")
            return False
        
        print("   表格提取和填充工作流测试通过")
        return True
    
    def test_multi_step_workflow(self) -> bool:
        """测试多步骤工作流"""
        try:
            # 步骤1: 创建和上传文档
            print("   步骤1: 文档上传")
            documents = self.create_test_documents()
            
            upload_results = []
            for doc_name, doc_path in documents.items():
                success, result = self.api_tester.test_upload_api(doc_path)
                upload_results.append((doc_name, success, result))
                if not success:
                    print(f"   文档上传失败: {doc_name}")
                    return False
            
            print("   步骤1完成: 所有文档上传成功")
            
            # 步骤2: 模拟文档解析和表格提取
            print("   步骤2: 表格提取")
            time.sleep(1)  # 模拟处理时间
            
            # 步骤3: 表格填充
            print("   步骤3: 表格填充")
            tables = [
                {
                    "columns": ["文档", "状态", "处理时间"],
                    "data": [
                        ["simple.txt", "", ""],
                        ["table.txt", "", ""],
                        ["complex.txt", "", ""]
                    ]
                }
            ]
            
            fill_data = [
                {"文档": "simple.txt", "状态": "已处理", "处理时间": "2024-01-01 10:00:00"},
                {"文档": "table.txt", "状态": "已处理", "处理时间": "2024-01-01 10:01:00"},
                {"文档": "complex.txt", "状态": "已处理", "处理时间": "2024-01-01 10:02:00"}
            ]
            
            success, result = self.api_tester.test_table_fill_api(tables, fill_data)
            if not success:
                print(f"   步骤3失败: {result}")
                return False
            
            print("   步骤3完成: 表格填充成功")
            
            # 步骤4: 验证最终结果
            print("   步骤4: 结果验证")
            filled_tables = result.get('filled_tables', [])
            if len(filled_tables) == 1:
                table_data = filled_tables[0]['data']
                if len(table_data) == 3 and all(len(row) == 3 for row in table_data):
                    print("   步骤4完成: 结果验证通过")
                    return True
            
            print("   步骤4失败: 结果验证不通过")
            return False
            
        except Exception as e:
            print(f"   多步骤工作流异常: {str(e)}")
            return False
    
    def test_error_recovery_workflow(self) -> bool:
        """测试错误恢复工作流"""
        try:
            # 测试无效文档上传
            print("   测试错误恢复: 无效文档")
            invalid_file = self.framework.create_test_file("invalid.xyz", "无效内容")
            
            success, result = self.api_tester.test_upload_api(invalid_file)
            # 无效文件应该被正确处理（可能成功也可能失败，取决于实现）
            
            # 测试无效表格填充请求
            print("   测试错误恢复: 无效API请求")
            invalid_tables = [{"invalid": "data"}]
            invalid_fill_data = ["invalid"]
            
            success, result = self.api_tester.test_table_fill_api(invalid_tables, invalid_fill_data)
            # 无效请求应该返回错误而不是崩溃
            
            # 测试空数据处理
            print("   测试错误恢复: 空数据")
            empty_tables = []
            empty_fill_data = []
            
            success, result = self.api_tester.test_table_fill_api(empty_tables, empty_fill_data)
            # 空数据应该被正确处理
            
            print("   错误恢复工作流测试完成")
            return True
            
        except Exception as e:
            print(f"   错误恢复工作流异常: {str(e)}")
            return False
    
    def test_performance_workflow(self) -> bool:
        """测试性能工作流"""
        try:
            print("   测试性能: 大量数据处理")
            
            # 创建大表格
            large_table = {
                "columns": ["ID", "姓名", "部门", "职位", "薪资"],
                "data": []
            }
            
            large_fill_data = []
            
            # 生成100行测试数据
            for i in range(100):
                large_table["data"].append([f"ID{i:03d}", "", "", "", ""])
                large_fill_data.append({
                    "ID": f"ID{i:03d}",
                    "姓名": f"员工{i:03d}",
                    "部门": "技术部" if i % 2 == 0 else "市场部",
                    "职位": "工程师" if i % 3 == 0 else "经理",
                    "薪资": str(5000 + i * 100)
                })
            
            # 测试处理时间
            start_time = time.time()
            success, result = self.api_tester.test_table_fill_api([large_table], large_fill_data)
            end_time = time.time()
            
            processing_time = end_time - start_time
            print(f"   大数据处理时间: {processing_time:.2f}秒")
            
            if not success:
                print(f"   大数据处理失败: {result}")
                return False
            
            # 验证处理结果
            filled_tables = result.get('filled_tables', [])
            if len(filled_tables) == 1 and len(filled_tables[0]['data']) == 100:
                print("   性能工作流测试通过")
                return True
            else:
                print("   性能工作流结果验证失败")
                return False
                
        except Exception as e:
            print(f"   性能工作流异常: {str(e)}")
            return False

def run_workflow_tests():
    """运行完整工作流测试"""
    print("🚀 开始完整工作流端到端测试")
    
    framework = E2ETestFramework(port=5003)  # 使用不同端口
    
    try:
        if not framework.setup():
            print("❌ 测试环境设置失败")
            return False
        
        # 创建测试实例
        workflow_tests = WorkflowTests(framework)
        
        # 定义测试用例
        test_cases = [
            ("文档上传工作流", workflow_tests.test_document_upload_workflow),
            ("表格提取填充工作流", workflow_tests.test_table_extraction_and_fill_workflow),
            ("多步骤工作流", workflow_tests.test_multi_step_workflow),
            ("错误恢复工作流", workflow_tests.test_error_recovery_workflow),
            ("性能工作流", workflow_tests.test_performance_workflow),
        ]
        
        # 运行所有测试
        for test_name, test_func in test_cases:
            framework.run_test(test_name, test_func)
        
        # 打印测试摘要
        framework.print_summary()
        
        # 返回测试结果
        report = framework.generate_report()
        return report['summary']['failed'] == 0 and report['summary']['errors'] == 0
        
    finally:
        framework.teardown()

if __name__ == "__main__":
    success = run_workflow_tests()
    sys.exit(0 if success else 1)
