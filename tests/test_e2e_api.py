#!/usr/bin/env python3
"""
API端点端到端测试
测试所有关键API端点的完整功能
"""

import sys
import os
import json
import time
from test_e2e_framework import E2ETestFramework

class APIEndpointTests:
    """API端点测试集合"""
    
    def __init__(self, framework: E2ETestFramework):
        self.framework = framework
        self.api_tester = framework.api_tester
    
    def test_table_fill_basic(self) -> bool:
        """基本表格填充测试"""
        tables = [
            {
                "columns": ["姓名", "年龄", "职位"],
                "data": [
                    ["张三", "", ""],
                    ["李四", "", ""]
                ]
            }
        ]
        
        fill_data = [
            {"姓名": "张三", "年龄": "25", "职位": "工程师"},
            {"姓名": "李四", "年龄": "30", "职位": "经理"}
        ]
        
        success, result = self.api_tester.test_table_fill_api(tables, fill_data)
        
        if not success:
            print(f"   API调用失败: {result}")
            return False
        
        # 验证返回结果
        filled_tables = result.get('filled_tables', [])
        if len(filled_tables) != 1:
            print(f"   返回表格数量错误: 期望1，实际{len(filled_tables)}")
            return False
        
        table = filled_tables[0]
        expected_data = [
            ["张三", "25", "工程师"],
            ["李四", "30", "经理"]
        ]
        
        if table['data'] != expected_data:
            print(f"   填充结果错误:")
            print(f"   期望: {expected_data}")
            print(f"   实际: {table['data']}")
            return False
        
        return True
    
    def test_table_fill_multiple_tables(self) -> bool:
        """多表格填充测试"""
        tables = [
            {
                "columns": ["产品", "价格"],
                "data": [["笔记本", ""], ["鼠标", ""]]
            },
            {
                "columns": ["员工", "部门"],
                "data": [["", "技术部"], ["", "市场部"]]
            }
        ]
        
        fill_data = [
            {"产品": "笔记本", "价格": "5000", "员工": "张三", "部门": "技术部"},
            {"产品": "鼠标", "价格": "100", "员工": "李四", "部门": "市场部"}
        ]
        
        success, result = self.api_tester.test_table_fill_api(tables, fill_data)
        
        if not success:
            print(f"   多表格API调用失败: {result}")
            return False
        
        filled_tables = result.get('filled_tables', [])
        if len(filled_tables) != 2:
            print(f"   返回表格数量错误: 期望2，实际{len(filled_tables)}")
            return False
        
        # 验证第一个表格
        table1 = filled_tables[0]
        expected_data1 = [["笔记本", "5000"], ["鼠标", "100"]]
        if table1['data'] != expected_data1:
            print(f"   第一个表格填充错误: {table1['data']}")
            return False
        
        # 验证第二个表格
        table2 = filled_tables[1]
        expected_data2 = [["张三", "技术部"], ["李四", "市场部"]]
        if table2['data'] != expected_data2:
            print(f"   第二个表格填充错误: {table2['data']}")
            return False
        
        return True
    
    def test_table_fill_empty_table(self) -> bool:
        """空表格处理测试"""
        tables = [
            {
                "columns": [],
                "data": []
            }
        ]
        
        fill_data = []
        
        success, result = self.api_tester.test_table_fill_api(tables, fill_data)
        
        if not success:
            print(f"   空表格API调用失败: {result}")
            return False
        
        filled_tables = result.get('filled_tables', [])
        if len(filled_tables) != 1:
            print(f"   空表格返回数量错误: {len(filled_tables)}")
            return False
        
        return True
    
    def test_table_fill_partial_fill(self) -> bool:
        """部分填充测试"""
        tables = [
            {
                "columns": ["项目", "状态", "负责人"],
                "data": [
                    ["项目A", "进行中", ""],
                    ["项目B", "", "李四"]
                ]
            }
        ]
        
        fill_data = [
            {"项目": "项目A", "负责人": "张三"},
            {"项目": "项目B", "状态": "已完成"}
        ]
        
        success, result = self.api_tester.test_table_fill_api(tables, fill_data)
        
        if not success:
            print(f"   部分填充API调用失败: {result}")
            return False
        
        filled_tables = result.get('filled_tables', [])
        table = filled_tables[0]
        
        expected_data = [
            ["项目A", "进行中", "张三"],
            ["项目B", "已完成", "李四"]
        ]
        
        if table['data'] != expected_data:
            print(f"   部分填充结果错误:")
            print(f"   期望: {expected_data}")
            print(f"   实际: {table['data']}")
            return False
        
        return True
    
    def test_table_fill_data_types(self) -> bool:
        """数据类型测试"""
        tables = [
            {
                "columns": ["名称", "数量", "价格", "有效"],
                "data": [["", "", "", ""]]
            }
        ]
        
        fill_data = [
            {
                "名称": "测试产品",
                "数量": 42,
                "价格": 99.99,
                "有效": True
            }
        ]
        
        success, result = self.api_tester.test_table_fill_api(tables, fill_data)
        
        if not success:
            print(f"   数据类型API调用失败: {result}")
            return False
        
        filled_tables = result.get('filled_tables', [])
        table = filled_tables[0]
        
        # 验证数据类型保持正确
        data_row = table['data'][0]
        if (data_row[0] != "测试产品" or 
            data_row[1] != 42 or 
            data_row[2] != 99.99 or 
            data_row[3] != True):
            print(f"   数据类型保持错误: {data_row}")
            return False
        
        return True
    
    def test_table_fill_error_handling(self) -> bool:
        """错误处理测试"""
        # 测试无效的请求格式
        invalid_requests = [
            # 缺少tables字段
            {"fill_data": []},
            # 缺少fill_data字段
            {"tables": []},
            # tables不是数组
            {"tables": "invalid", "fill_data": []},
            # 表格缺少columns
            {"tables": [{"data": []}], "fill_data": []},
            # 表格缺少data
            {"tables": [{"columns": []}], "fill_data": []}
        ]
        
        for i, invalid_request in enumerate(invalid_requests):
            try:
                response = self.api_tester.session.post(
                    f"{self.api_tester.base_url}/api/table-fill",
                    json=invalid_request,
                    timeout=10
                )
                
                # 应该返回错误状态
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', False):
                        print(f"   错误请求{i+1}应该失败但成功了: {invalid_request}")
                        return False
                
            except Exception as e:
                # 网络错误等异常是可以接受的
                continue
        
        return True

def run_api_endpoint_tests():
    """运行API端点测试"""
    print("🚀 开始API端点端到端测试")
    
    framework = E2ETestFramework(port=5001)  # 使用不同端口避免冲突
    
    try:
        if not framework.setup():
            print("❌ 测试环境设置失败")
            return False
        
        # 创建测试实例
        api_tests = APIEndpointTests(framework)
        
        # 定义测试用例
        test_cases = [
            ("基本表格填充", api_tests.test_table_fill_basic),
            ("多表格填充", api_tests.test_table_fill_multiple_tables),
            ("空表格处理", api_tests.test_table_fill_empty_table),
            ("部分填充", api_tests.test_table_fill_partial_fill),
            ("数据类型处理", api_tests.test_table_fill_data_types),
            ("错误处理", api_tests.test_table_fill_error_handling),
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
    success = run_api_endpoint_tests()
    sys.exit(0 if success else 1)
