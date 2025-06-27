#!/usr/bin/env python3
"""
完整的端到端测试运行器
包含真实web_app.py集成测试的完整测试套件
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# 导入所有测试模块
from test_e2e_api import run_api_endpoint_tests
from test_e2e_frontend import run_frontend_integration_tests
from test_e2e_workflow import run_workflow_tests
from test_e2e_performance import run_performance_tests
from test_e2e_complete_system import run_complete_system_tests
from test_real_webapp import run_real_webapp_test

class CompleteE2ETestRunner:
    """完整端到端测试运行器"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有端到端测试"""
        print("🚀 开始完整的端到端测试套件（包含真实Web应用集成）")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # 定义测试套件
        test_suites = [
            ("真实Web应用集成测试", run_real_webapp_test),
            ("API端点测试", run_api_endpoint_tests),
            ("前端集成测试", run_frontend_integration_tests),
            ("完整工作流测试", run_workflow_tests),
            ("完整系统测试", run_complete_system_tests),
            ("性能压力测试", run_performance_tests),
        ]
        
        # 运行每个测试套件
        for suite_name, test_func in test_suites:
            print(f"\n📋 运行测试套件: {suite_name}")
            print("-" * 60)
            
            suite_start_time = time.time()
            
            try:
                success = test_func()
                suite_end_time = time.time()
                suite_duration = suite_end_time - suite_start_time
                
                self.test_results[suite_name] = {
                    "success": success,
                    "duration": suite_duration,
                    "status": "PASS" if success else "FAIL",
                    "timestamp": datetime.now().isoformat()
                }
                
                status_icon = "✅" if success else "❌"
                print(f"{status_icon} {suite_name} - {'通过' if success else '失败'} ({suite_duration:.2f}秒)")
                
            except Exception as e:
                suite_end_time = time.time()
                suite_duration = suite_end_time - suite_start_time
                
                self.test_results[suite_name] = {
                    "success": False,
                    "duration": suite_duration,
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"💥 {suite_name} - 异常: {str(e)} ({suite_duration:.2f}秒)")
        
        self.end_time = time.time()
        
        # 生成综合报告
        return self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合测试报告"""
        total_duration = self.end_time - self.start_time
        total_suites = len(self.test_results)
        passed_suites = len([r for r in self.test_results.values() if r["success"]])
        failed_suites = len([r for r in self.test_results.values() if r["status"] == "FAIL"])
        error_suites = len([r for r in self.test_results.values() if r["status"] == "ERROR"])
        
        report = {
            "summary": {
                "total_suites": total_suites,
                "passed_suites": passed_suites,
                "failed_suites": failed_suites,
                "error_suites": error_suites,
                "success_rate": (passed_suites / total_suites * 100) if total_suites > 0 else 0,
                "total_duration": total_duration,
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.end_time).isoformat()
            },
            "test_suites": self.test_results,
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd()
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def print_comprehensive_summary(self, report: Dict[str, Any]):
        """打印综合测试摘要"""
        summary = report["summary"]
        
        print("\n" + "=" * 80)
        print("📊 完整端到端测试综合报告")
        print("=" * 80)
        
        print(f"🕐 测试时间: {summary['start_time']} - {summary['end_time']}")
        print(f"⏱️  总耗时: {summary['total_duration']:.2f}秒")
        print(f"📦 测试套件总数: {summary['total_suites']}")
        print(f"✅ 通过: {summary['passed_suites']}")
        print(f"❌ 失败: {summary['failed_suites']}")
        print(f"💥 错误: {summary['error_suites']}")
        print(f"📈 成功率: {summary['success_rate']:.1f}%")
        
        print("\n📋 详细结果:")
        print("-" * 80)
        
        for suite_name, result in self.test_results.items():
            status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥"}[result["status"]]
            print(f"{status_icon} {suite_name:<30} {result['status']:<6} ({result['duration']:.2f}s)")
            
            if "error" in result:
                print(f"   错误: {result['error']}")
        
        print("\n" + "=" * 80)
        
        # 总体结论
        if summary['success_rate'] == 100:
            print("🎉 所有测试套件都通过了！系统完全正常，包括真实Web应用集成。")
        elif summary['success_rate'] >= 80:
            print("⚠️  大部分测试通过，系统基本正常，但有一些问题需要关注。")
        elif summary['success_rate'] >= 60:
            print("🔧 系统存在一些问题，需要进行修复。")
        else:
            print("🚨 系统存在严重问题，需要立即修复。")
        
        # 特别说明真实Web应用集成状态
        real_webapp_result = self.test_results.get("真实Web应用集成测试")
        if real_webapp_result and real_webapp_result["success"]:
            print("🌟 特别说明: 真实Web应用集成测试通过，系统可以使用接近生产环境的配置运行。")
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """保存测试报告到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"complete_e2e_test_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"📄 完整测试报告已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存报告失败: {str(e)}")

def main():
    """主函数"""
    print("🚀 启动完整端到端测试套件（包含真实Web应用集成）")
    
    # 检查依赖
    missing_deps = []
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
    
    try:
        import flask
    except ImportError:
        missing_deps.append("flask")
    
    if missing_deps:
        print(f"❌ 缺少依赖包: {', '.join(missing_deps)}")
        print("请运行: pip install " + " ".join(missing_deps))
        return False
    
    # 创建测试运行器
    runner = CompleteE2ETestRunner()
    
    try:
        # 运行所有测试
        report = runner.run_all_tests()
        
        # 打印综合摘要
        runner.print_comprehensive_summary(report)
        
        # 保存报告
        runner.save_report(report)
        
        # 返回测试结果
        return report["summary"]["success_rate"] == 100.0
        
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
        return False
    except Exception as e:
        print(f"\n💥 测试运行异常: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 所有完整端到端测试完成并通过！")
        print("🌟 系统已准备好投入生产使用，包括真实Web应用集成。")
        sys.exit(0)
    else:
        print("\n❌ 完整端到端测试未完全通过，请检查问题。")
        sys.exit(1)
