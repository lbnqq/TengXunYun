#!/usr/bin/env python3
"""
完整系统端到端测试
涵盖文档处理、OCR、表格解析、智能填充等完整业务流程
"""

import sys
import os
import json
import time
import requests
from typing import Dict, Any, List, Tuple
from test_e2e_framework import E2ETestFramework

class CompleteSystemTests:
    """完整系统测试"""
    
    def __init__(self, framework: E2ETestFramework):
        self.framework = framework
        self.api_tester = framework.api_tester
    
    def test_document_upload_and_parse_workflow(self) -> bool:
        """测试文档上传和解析工作流"""
        print("   测试文档上传和解析工作流")
        
        # 创建测试文档
        test_content = """
        办公文档智能代理测试文档
        
        员工信息表格：
        姓名: 张三, 年龄: 28, 职位: 工程师
        姓名: 李四, 年龄: 32, 职位: 经理
        姓名: 王五, 年龄: 35, 职位: 总监
        
        项目信息：
        项目A - 进行中
        项目B - 已完成
        项目C - 计划中
        """
        
        test_file = self.framework.create_test_file("test_document.txt", test_content)
        
        try:
            # 步骤1: 上传文档
            print("     步骤1: 上传文档")
            success, upload_result = self.api_tester.test_upload_api(test_file)
            
            if not success:
                print(f"     文档上传失败: {upload_result}")
                return False
            
            print(f"     文档上传成功: {upload_result.get('filename')}")
            
            # 步骤2: 解析文档
            print("     步骤2: 解析文档")
            
            # 使用文档解析API
            import requests
            with open(test_file, 'rb') as f:
                files = {'file': (os.path.basename(test_file), f, 'text/plain')}
                response = requests.post(
                    f"{self.api_tester.base_url}/api/document/parse",
                    files=files,
                    timeout=30
                )
            
            if response.status_code != 200:
                print(f"     文档解析失败: {response.status_code}")
                return False
            
            parse_result = response.json()
            if not parse_result.get('success'):
                print(f"     文档解析失败: {parse_result}")
                return False
            
            print(f"     文档解析成功，提取到 {len(parse_result.get('tables', []))} 个表格")
            
            # 验证解析结果
            if 'document_id' not in parse_result:
                print("     缺少document_id")
                return False
            
            if 'text' not in parse_result:
                print("     缺少文本内容")
                return False
            
            return True
            
        except Exception as e:
            print(f"     文档上传解析异常: {str(e)}")
            return False
    
    def test_table_extraction_and_intelligent_fill(self) -> bool:
        """测试表格提取和智能填充"""
        print("   测试表格提取和智能填充")
        
        try:
            # 步骤1: 模拟从文档中提取的表格
            extracted_tables = [
                {
                    "columns": ["姓名", "年龄", "职位"],
                    "data": [
                        ["张三", "", ""],
                        ["李四", "", ""],
                        ["王五", "", ""]
                    ]
                }
            ]
            
            # 步骤2: 准备智能填充数据
            fill_data = [
                {"姓名": "张三", "年龄": "28", "职位": "高级工程师"},
                {"姓名": "李四", "年龄": "32", "职位": "产品经理"},
                {"姓名": "王五", "年龄": "35", "职位": "技术总监"}
            ]
            
            print("     步骤1: 表格提取完成")
            print(f"     提取到表格: {len(extracted_tables)} 个")
            
            # 步骤3: 执行智能填充
            print("     步骤2: 执行智能填充")
            success, result = self.api_tester.test_table_fill_api(extracted_tables, fill_data)
            
            if not success:
                print(f"     智能填充失败: {result}")
                return False
            
            # 验证填充结果
            filled_tables = result.get('filled_tables', [])
            if len(filled_tables) != 1:
                print(f"     填充表格数量错误: 期望1，实际{len(filled_tables)}")
                return False
            
            table = filled_tables[0]
            expected_data = [
                ["张三", "28", "高级工程师"],
                ["李四", "32", "产品经理"],
                ["王五", "35", "技术总监"]
            ]
            
            if table['data'] != expected_data:
                print(f"     填充结果错误:")
                print(f"     期望: {expected_data}")
                print(f"     实际: {table['data']}")
                return False
            
            print("     智能填充成功")
            return True
            
        except Exception as e:
            print(f"     表格提取填充异常: {str(e)}")
            return False
    
    def test_document_intelligent_fill_workflow(self) -> bool:
        """测试文档智能填充工作流"""
        print("   测试文档智能填充工作流")
        
        try:
            # 步骤1: 创建测试文档
            test_content = "这是一个需要智能填充的测试文档"
            test_file = self.framework.create_test_file("fill_test.txt", test_content)
            
            # 步骤2: 上传并解析文档
            print("     步骤1: 上传并解析文档")
            import requests
            with open(test_file, 'rb') as f:
                files = {'file': (os.path.basename(test_file), f, 'text/plain')}
                response = requests.post(
                    f"{self.api_tester.base_url}/api/document/parse",
                    files=files,
                    timeout=30
                )
            
            parse_result = response.json()
            if not parse_result.get('success'):
                print(f"     文档解析失败: {parse_result}")
                return False
            
            document_id = parse_result.get('document_id')
            
            # 步骤3: 执行智能填充
            print("     步骤2: 执行智能填充")
            fill_request = {
                'document_id': document_id,
                'fill_data': [
                    '智能填充内容1',
                    '智能填充内容2',
                    '智能填充内容3'
                ]
            }
            
            response = requests.post(
                f"{self.api_tester.base_url}/api/document/fill",
                json=fill_request,
                timeout=30
            )
            
            fill_result = response.json()
            if not fill_result.get('success'):
                print(f"     文档填充失败: {fill_result}")
                return False
            
            print("     文档智能填充成功")
            return True
            
        except Exception as e:
            print(f"     文档智能填充异常: {str(e)}")
            return False
    
    def test_style_analysis_workflow(self) -> bool:
        """测试文风分析工作流"""
        print("   测试文风分析工作流")
        
        try:
            # 测试文本
            test_text = """
            尊敬的各位领导和同事：
            
            根据公司发展战略和业务需求，现将本季度工作总结汇报如下。
            在过去的三个月中，我们团队严格按照既定计划执行各项任务，
            取得了显著的成果。具体表现在以下几个方面：
            
            一、项目进展情况良好，按时完成了预定目标。
            二、团队协作效率显著提升，沟通机制日趋完善。
            三、客户满意度持续改善，业务拓展取得新突破。
            """
            
            # 执行文风分析
            style_request = {'text': test_text}
            
            response = requests.post(
                f"{self.api_tester.base_url}/api/style/analyze",
                json=style_request,
                timeout=30
            )
            
            style_result = response.json()
            if not style_result.get('success'):
                print(f"     文风分析失败: {style_result}")
                return False
            
            # 验证分析结果
            style_features = style_result.get('style_features', {})
            if not style_features:
                print("     文风分析结果为空")
                return False
            
            required_features = ['formality', 'complexity', 'tone']
            for feature in required_features:
                if feature not in style_features:
                    print(f"     缺少文风特征: {feature}")
                    return False
            
            print(f"     文风分析成功: {style_result.get('style_type')}")
            return True
            
        except Exception as e:
            print(f"     文风分析异常: {str(e)}")
            return False
    
    def test_complete_business_workflow(self) -> bool:
        """测试完整业务工作流"""
        print("   测试完整业务工作流")
        
        try:
            # 步骤1: 文档上传和解析
            print("     步骤1: 文档上传和解析")
            if not self.test_document_upload_and_parse_workflow():
                return False
            
            # 步骤2: 表格提取和智能填充
            print("     步骤2: 表格提取和智能填充")
            if not self.test_table_extraction_and_intelligent_fill():
                return False
            
            # 步骤3: 文档智能填充
            print("     步骤3: 文档智能填充")
            if not self.test_document_intelligent_fill_workflow():
                return False
            
            # 步骤4: 文风分析
            print("     步骤4: 文风分析")
            if not self.test_style_analysis_workflow():
                return False
            
            print("     完整业务工作流测试通过")
            return True
            
        except Exception as e:
            print(f"     完整业务工作流异常: {str(e)}")
            return False
    
    def test_system_integration(self) -> bool:
        """测试系统集成"""
        print("   测试系统集成")
        
        try:
            # 测试所有API端点的可用性
            endpoints = [
                '/api/upload',
                '/api/table-fill',
                '/api/document/parse',
                '/api/document/fill',
                '/api/style/analyze',
                '/health'
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{self.api_tester.base_url}{endpoint}", timeout=5)
                    # 对于GET请求，405是可接受的（表示端点存在但方法不对）
                    if response.status_code not in [200, 405]:
                        print(f"     端点 {endpoint} 不可用: {response.status_code}")
                        return False
                except Exception as e:
                    print(f"     端点 {endpoint} 连接失败: {str(e)}")
                    return False
            
            print("     系统集成测试通过")
            return True
            
        except Exception as e:
            print(f"     系统集成测试异常: {str(e)}")
            return False

def run_complete_system_tests():
    """运行完整系统测试"""
    print("🚀 开始完整系统端到端测试")
    
    framework = E2ETestFramework(port=5005)  # 使用不同端口
    
    try:
        if not framework.setup():
            print("❌ 测试环境设置失败")
            return False
        
        # 创建测试实例
        system_tests = CompleteSystemTests(framework)
        
        # 定义测试用例
        test_cases = [
            ("文档上传解析工作流", system_tests.test_document_upload_and_parse_workflow),
            ("表格提取智能填充", system_tests.test_table_extraction_and_intelligent_fill),
            ("文档智能填充工作流", system_tests.test_document_intelligent_fill_workflow),
            ("文风分析工作流", system_tests.test_style_analysis_workflow),
            ("完整业务工作流", system_tests.test_complete_business_workflow),
            ("系统集成测试", system_tests.test_system_integration),
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
    success = run_complete_system_tests()
    sys.exit(0 if success else 1)
