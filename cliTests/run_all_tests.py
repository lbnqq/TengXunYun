#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有测试
"""

import os
import sys
import argparse
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import requests


class TestRunner:
    def __init__(self, base_url=None, verbose=False):
        self.base_url = base_url
        self.verbose = verbose
        self.start_time = time.time()
        self.test_results = []
        
        # 获取当前脚本所在目录
        self.cli_tests_dir = Path(__file__).parent
        
        # 测试配置 - 基于项目宪法的业务场景覆盖
        self.test_configs = [
            {
                "name": "格式对齐测试",
                "description": "测试文档格式对齐功能的贯通性",
                "script": str(self.cli_tests_dir / "test_format_alignment.py"),
                "args": ["test_data/format_alignment/source.txt", "test_data/format_alignment/target.txt", "test_results/format_alignment_output.txt"],
                "output": "test_results/format_alignment_output.txt",
                "priority": "P1",
                "category": "核心业务场景"
            },
            {
                "name": "文风统一测试",
                "description": "测试文风统一功能的贯通性",
                "script": str(self.cli_tests_dir / "test_style_alignment.py"),
                "args": ["test_data/style_alignment/reference.txt", "test_data/style_alignment/target.txt", "test_results/style_alignment_output.txt"],
                "output": "test_results/style_alignment_output.txt",
                "priority": "P1",
                "category": "核心业务场景"
            },
            {
                "name": "智能填报测试",
                "description": "测试智能文档填报功能的贯通性",
                "script": str(self.cli_tests_dir / "test_document_fill.py"),
                "args": ["test_data/document_fill/template.txt", "test_data/document_fill/data.json", "test_results/document_fill_output.txt"],
                "output": "test_results/document_fill_output.txt",
                "priority": "P1",
                "category": "核心业务场景"
            },
            {
                "name": "文档评审测试",
                "description": "测试文档评审功能的贯通性",
                "script": str(self.cli_tests_dir / "test_document_review.py"),
                "args": ["test_data/document_review/document.txt", "test_results/document_review_output.txt"],
                "output": "test_results/document_review_output.txt",
                "priority": "P1",
                "category": "核心业务场景"
            },
            {
                "name": "表格填充测试",
                "description": "测试表格填充功能的贯通性",
                "script": str(self.cli_tests_dir / "test_table_fill.py"),
                "args": ["test_data/table_fill/table.json", "test_data/table_fill/data.json", "test_results/table_fill_output.json"],
                "output": "test_results/table_fill_output.json",
                "priority": "P1",
                "category": "核心业务场景"
            },
            {
                "name": "边界用例测试",
                "description": "测试系统在边界条件和异常情况下的表现",
                "script": str(self.cli_tests_dir / "test_edge_cases_simple.py"),
                "args": ["--output", "test_results/edge_cases_output.json"],
                "output": "test_results/edge_cases_output.json",
                "priority": "P2",
                "category": "边界用例"
            }
        ]
    
    def create_test_data(self):
        # 示例方法体
        pass
    
    def run_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        test_name = config["name"]
        script_path = config["script"]
        args = config["args"]
        
        print(f"\n🚀 开始执行: {test_name}")
        print(f"   描述: {config['description']}")
        print(f"   优先级: {config['priority']}")
        print(f"   分类: {config['category']}")
        
        start_time = time.time()
        
        try:
            # 检查脚本文件是否存在
            if not os.path.exists(script_path):
                error_msg = f"测试脚本不存在: {script_path}"
                print(f"❌ {error_msg}")
                return {
                    "name": test_name,
                    "success": False,
                    "error": error_msg,
                    "suggestion": "请检查脚本文件路径是否正确，或重新生成测试脚本",
                    "duration": time.time() - start_time,
                    "category": config["category"],
                    "priority": config["priority"]
                }
            
            # 检查输入文件是否存在
            missing_files = []
            for arg in args:
                if arg.startswith("test_data/") and not os.path.exists(arg):
                    missing_files.append(arg)
            
            if missing_files:
                error_msg = f"测试数据文件缺失: {', '.join(missing_files)}"
                print(f"❌ {error_msg}")
                return {
                    "name": test_name,
                    "success": False,
                    "error": error_msg,
                    "suggestion": "请先运行 create_test_data() 创建测试数据",
                    "duration": time.time() - start_time,
                    "category": config["category"],
                    "priority": config["priority"]
                }
            
            # 执行测试脚本
            cmd = [sys.executable, script_path] + args
            if self.verbose:
                print(f"   执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ {test_name} 执行成功 (耗时: {duration:.2f}秒)")
                return {
                    "name": test_name,
                    "success": True,
                    "output": result.stdout,
                    "duration": duration,
                    "category": config["category"],
                    "priority": config["priority"]
                }
            else:
                error_msg = f"测试执行失败: {result.stderr}"
                print(f"❌ {test_name} 执行失败")
                print(f"   错误信息: {error_msg}")
                
                # 根据错误类型提供具体建议
                suggestion = self._generate_suggestion(error_msg, test_name)
                
                return {
                    "name": test_name,
                    "success": False,
                    "error": error_msg,
                    "suggestion": suggestion,
                    "duration": duration,
                    "category": config["category"],
                    "priority": config["priority"]
                }
                
        except subprocess.TimeoutExpired:
            error_msg = "测试执行超时 (超过5分钟)"
            print(f"❌ {test_name} 执行超时")
            return {
                "name": test_name,
                "success": False,
                "error": error_msg,
                "suggestion": "检查测试脚本是否存在死循环或性能问题，考虑优化测试逻辑",
                "duration": time.time() - start_time,
                "category": config["category"],
                "priority": config["priority"]
            }
        except Exception as e:
            error_msg = f"测试执行异常: {str(e)}"
            print(f"❌ {test_name} 执行异常: {error_msg}")
            return {
                "name": test_name,
                "success": False,
                "error": error_msg,
                "suggestion": "检查测试环境配置和依赖项是否正确安装",
                "duration": time.time() - start_time,
                "category": config["category"],
                "priority": config["priority"]
            }
    
    def _generate_suggestion(self, error_msg: str, test_name: str) -> str:
        print("🔍 检查API服务健康状态...")
        
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ API服务健康检查通过")
                print(f"   状态: {health_data.get('status', 'unknown')}")
                print(f"   时间戳: {health_data.get('timestamp', 'unknown')}")
                
                # 检查API状态
                api_status = health_data.get('api_status', {})
                for api_name, status_info in api_status.items():
                    status = status_info.get('status', 'unknown')
                    mock_mode = status_info.get('mock_mode', False)
                    print(f"   {api_name}: {status} {'(MOCK)' if mock_mode else ''}")
                
                return True
            else:
                print(f"❌ API服务健康检查失败: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到API服务 (ConnectionError)")
            print("   请确保API服务已启动: python src/web_app.py")
            return False
        except requests.exceptions.Timeout:
            print("❌ API服务响应超时 (Timeout)")
            return False
        except Exception as e:
            print(f"❌ API服务健康检查异常: {e}")
            return False

    def run_tests(self) -> Dict[str, Any]:
        if test_results is None:
            print("⚠️ 未传入测试结果，无法生成报告")
            return
        # 统计
        total = len(test_results)
        passed = sum(1 for r in test_results if r["success"])
        failed = total - passed
        success_rate = (passed / total) * 100 if total > 0 else 0.0
        print(f"[报告] 总数: {total} 通过: {passed} 失败: {failed} 成功率: {success_rate:.1f}% 总耗时: {duration or 0:.2f}秒")

    def generate_summary(self, test_results: List[Dict[str, Any]], duration: float) -> Dict[str, Any]:
        parser = argparse.ArgumentParser(description="CLI业务场景贯通性测试")
        parser.add_argument("--report", action="store_true", help="生成详细报告")
        parser.add_argument("--verbose", action="store_true", help="详细输出")
        parser.add_argument("--create-data", action="store_true", help="仅创建测试数据")
        
        args = parser.parse_args()
        
        runner = TestRunner(verbose=args.verbose)
        
        if args.create_data:
            runner.create_test_data()
            print("✅ 测试数据创建完成")
            return
        
        success = runner.run_tests()
        
        if not success.get("success", False):
            print(f"\n❌ CLI业务场景测试失败，工程可用性验证未通过")
            print("请根据上述错误信息和建议进行修复后重新测试")
            sys.exit(1)
        else:
            print(f"\n✅ CLI业务场景测试成功，工程可用性验证通过")
            sys.exit(0)


if __name__ == "__main__":
    main()