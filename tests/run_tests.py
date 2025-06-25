#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试运行脚本
执行所有测试并生成详细的测试报告
"""

import unittest
import sys
import os
import time
import json
from io import StringIO
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入测试模块
from test_format_alignment import TestFormatAlignment
from test_writing_style import TestWritingStyle
from test_integration import TestIntegration

# 导入新增功能测试模块
try:
    from test_semantic_behavior_engine import TestSemanticUnitIdentifier, TestSemanticSpaceMapper, TestSemanticBehaviorAnalyzer
    SEMANTIC_TESTS_AVAILABLE = True
except ImportError:
    SEMANTIC_TESTS_AVAILABLE = False
    print("⚠️ 语义行为分析测试模块不可用")

try:
    from test_comprehensive_style_processor import TestQuantitativeFeatureExtractor, TestComprehensiveStyleProcessor
    COMPREHENSIVE_TESTS_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_TESTS_AVAILABLE = False
    print("⚠️ 综合文风处理测试模块不可用")

# 导入其他测试模块
try:
    from test_llm_clients import TestLLMClients
    LLM_TESTS_AVAILABLE = True
except ImportError:
    LLM_TESTS_AVAILABLE = False

try:
    from test_basic_functionality import TestBasicFunctionality
    BASIC_TESTS_AVAILABLE = True
except ImportError:
    BASIC_TESTS_AVAILABLE = False


class TestResult:
    """测试结果收集器"""
    
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "start_time": None,
            "end_time": None,
            "duration": 0,
            "test_details": [],
            "failures": [],
            "errors_list": []
        }
    
    def add_test_result(self, test_name, status, duration, error_msg=None):
        """添加测试结果"""
        self.results["total_tests"] += 1
        self.results[status] += 1
        
        test_detail = {
            "name": test_name,
            "status": status,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        if error_msg:
            test_detail["error"] = error_msg
            if status == "failed":
                self.results["failures"].append(test_detail)
            elif status == "errors":
                self.results["errors_list"].append(test_detail)
        
        self.results["test_details"].append(test_detail)
    
    def set_timing(self, start_time, end_time):
        """设置测试时间"""
        self.results["start_time"] = start_time
        self.results["end_time"] = end_time
        self.results["duration"] = end_time - start_time
    
    def get_summary(self):
        """获取测试摘要"""
        return {
            "total": self.results["total_tests"],
            "passed": self.results["passed"],
            "failed": self.results["failed"],
            "errors": self.results["errors"],
            "success_rate": (self.results["passed"] / self.results["total_tests"] * 100) if self.results["total_tests"] > 0 else 0,
            "duration": self.results["duration"]
        }


class CustomTestRunner:
    """自定义测试运行器"""
    
    def __init__(self, verbosity=2):
        self.verbosity = verbosity
        self.result_collector = TestResult()
    
    def run_test_suite(self, test_suite, suite_name):
        """运行测试套件"""
        print(f"\n{'='*60}")
        print(f"运行测试套件: {suite_name}")
        print(f"{'='*60}")
        
        # 创建字符串缓冲区来捕获输出
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=self.verbosity
        )
        
        suite_start_time = time.time()
        result = runner.run(test_suite)
        suite_end_time = time.time()
        
        # 处理测试结果
        for test, error in result.failures:
            test_name = f"{suite_name}.{test._testMethodName}"
            self.result_collector.add_test_result(
                test_name, "failed", 0, str(error)
            )
        
        for test, error in result.errors:
            test_name = f"{suite_name}.{test._testMethodName}"
            self.result_collector.add_test_result(
                test_name, "errors", 0, str(error)
            )
        
        # 计算通过的测试
        total_in_suite = result.testsRun
        failed_in_suite = len(result.failures) + len(result.errors)
        passed_in_suite = total_in_suite - failed_in_suite
        
        for i in range(passed_in_suite):
            self.result_collector.add_test_result(
                f"{suite_name}.test_{i}", "passed", 0
            )
        
        # 输出套件结果
        print(f"测试套件 {suite_name} 完成:")
        print(f"  总计: {total_in_suite}")
        print(f"  通过: {passed_in_suite}")
        print(f"  失败: {len(result.failures)}")
        print(f"  错误: {len(result.errors)}")
        print(f"  耗时: {suite_end_time - suite_start_time:.2f}秒")
        
        # 如果有失败或错误，显示详情
        if result.failures:
            print(f"\n失败的测试:")
            for test, error in result.failures:
                print(f"  - {test._testMethodName}: {error.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(f"\n错误的测试:")
            for test, error in result.errors:
                print(f"  - {test._testMethodName}: {error.split('Exception:')[-1].strip()}")
        
        return result
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始执行办公文档智能代理系统全面测试")
        print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        # 定义测试套件
        test_suites = [
            (unittest.TestLoader().loadTestsFromTestCase(TestFormatAlignment), "格式对齐测试"),
            (unittest.TestLoader().loadTestsFromTestCase(TestWritingStyle), "文风对齐测试"),
            (unittest.TestLoader().loadTestsFromTestCase(TestIntegration), "集成测试")
        ]

        # 添加新增功能测试
        if SEMANTIC_TESTS_AVAILABLE:
            test_suites.extend([
                (unittest.TestLoader().loadTestsFromTestCase(TestSemanticUnitIdentifier), "语义单元识别测试"),
                (unittest.TestLoader().loadTestsFromTestCase(TestSemanticSpaceMapper), "语义空间映射测试"),
                (unittest.TestLoader().loadTestsFromTestCase(TestSemanticBehaviorAnalyzer), "语义行为分析测试")
            ])
            print("✅ 已加载语义空间行为分析测试")

        if COMPREHENSIVE_TESTS_AVAILABLE:
            test_suites.extend([
                (unittest.TestLoader().loadTestsFromTestCase(TestQuantitativeFeatureExtractor), "量化特征提取测试"),
                (unittest.TestLoader().loadTestsFromTestCase(TestComprehensiveStyleProcessor), "综合文风处理测试")
            ])
            print("✅ 已加载综合文风处理测试")

        # 添加其他可用测试
        if LLM_TESTS_AVAILABLE:
            test_suites.append((unittest.TestLoader().loadTestsFromTestCase(TestLLMClients), "LLM客户端测试"))
            print("✅ 已加载LLM客户端测试")

        if BASIC_TESTS_AVAILABLE:
            test_suites.append((unittest.TestLoader().loadTestsFromTestCase(TestBasicFunctionality), "基础功能测试"))
            print("✅ 已加载基础功能测试")

        print(f"📊 总共加载了 {len(test_suites)} 个测试套件")
        
        # 运行每个测试套件
        all_results = []
        for suite, name in test_suites:
            try:
                result = self.run_test_suite(suite, name)
                all_results.append((name, result))
            except Exception as e:
                print(f"运行测试套件 {name} 时出错: {str(e)}")
                self.result_collector.add_test_result(
                    f"{name}.suite_error", "errors", 0, str(e)
                )
        
        end_time = time.time()
        self.result_collector.set_timing(start_time, end_time)
        
        # 生成最终报告
        self.generate_report()
        
        return self.result_collector.results
    
    def generate_report(self):
        """生成测试报告"""
        print(f"\n{'='*80}")
        print("测试报告")
        print(f"{'='*80}")
        
        summary = self.result_collector.get_summary()
        
        print(f"测试总结:")
        print(f"  总测试数: {summary['total']}")
        print(f"  通过: {summary['passed']}")
        print(f"  失败: {summary['failed']}")
        print(f"  错误: {summary['errors']}")
        print(f"  成功率: {summary['success_rate']:.1f}%")
        print(f"  总耗时: {summary['duration']:.2f}秒")
        
        # 保存详细报告到文件
        report_file = os.path.join(os.path.dirname(__file__), "test_report.json")
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.result_collector.results, f, ensure_ascii=False, indent=2)
            print(f"\n详细测试报告已保存到: {report_file}")
        except Exception as e:
            print(f"保存测试报告失败: {str(e)}")
        
        # 生成HTML报告
        self.generate_html_report()
    
    def generate_html_report(self):
        """生成HTML格式的测试报告"""
        try:
            html_content = self.create_html_report()
            report_file = os.path.join(os.path.dirname(__file__), "test_report.html")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML测试报告已保存到: {report_file}")
            
        except Exception as e:
            print(f"生成HTML报告失败: {str(e)}")
    
    def create_html_report(self):
        """创建HTML报告内容"""
        summary = self.result_collector.get_summary()
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>格式对齐和文风对齐功能测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ background-color: #d4edda; }}
        .failed {{ background-color: #f8d7da; }}
        .errors {{ background-color: #fff3cd; }}
        .test-details {{ margin-top: 20px; }}
        .test-item {{ padding: 10px; margin: 5px 0; border-left: 4px solid #007bff; background-color: #f8f9fa; }}
        .test-item.failed {{ border-left-color: #dc3545; }}
        .test-item.error {{ border-left-color: #ffc107; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>格式对齐和文风对齐功能测试报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>测试耗时: {summary['duration']:.2f}秒</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>总测试数</h3>
            <p style="font-size: 24px; margin: 0;">{summary['total']}</p>
        </div>
        <div class="metric passed">
            <h3>通过</h3>
            <p style="font-size: 24px; margin: 0;">{summary['passed']}</p>
        </div>
        <div class="metric failed">
            <h3>失败</h3>
            <p style="font-size: 24px; margin: 0;">{summary['failed']}</p>
        </div>
        <div class="metric errors">
            <h3>错误</h3>
            <p style="font-size: 24px; margin: 0;">{summary['errors']}</p>
        </div>
        <div class="metric">
            <h3>成功率</h3>
            <p style="font-size: 24px; margin: 0;">{summary['success_rate']:.1f}%</p>
        </div>
    </div>
    
    <div class="test-details">
        <h2>测试详情</h2>
        """
        
        for test in self.result_collector.results["test_details"]:
            status_class = test["status"]
            html += f"""
        <div class="test-item {status_class}">
            <strong>{test['name']}</strong> - {test['status'].upper()}
            <br><small>执行时间: {test['timestamp']}</small>
            """
            
            if test.get("error"):
                html += f"<br><pre style='color: red; font-size: 12px;'>{test['error'][:200]}...</pre>"
            
            html += "</div>"
        
        html += """
    </div>
</body>
</html>
        """
        
        return html


def main():
    """主函数"""
    print("格式对齐和文风对齐功能测试")
    print("=" * 50)
    
    # 检查测试环境
    print("检查测试环境...")
    
    # 创建测试运行器
    runner = CustomTestRunner(verbosity=2)
    
    # 运行所有测试
    results = runner.run_all_tests()
    
    # 根据测试结果设置退出码
    if results["failed"] > 0 or results["errors"] > 0:
        print(f"\n测试完成，但有 {results['failed']} 个失败和 {results['errors']} 个错误")
        sys.exit(1)
    else:
        print(f"\n所有测试通过！共 {results['passed']} 个测试")
        sys.exit(0)


if __name__ == '__main__':
    main()
