#!/usr/bin/env python3
"""
综合测试运行器
整合所有测试套件，提供完整的测试覆盖

测试套件包括：
1. 集成测试 - 基本功能验证
2. API测试 - 接口正确性验证
3. 前端测试 - 用户界面验证
4. 端到端测试 - 完整流程验证
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

class ComprehensiveTestRunner:
    """综合测试运行器"""
    
    def __init__(self):
        self.test_results = {}
        self.overall_success = True
        self.start_time = datetime.now()
        
    def log_suite_result(self, suite_name, success, details=None):
        """记录测试套件结果"""
        self.test_results[suite_name] = {
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        if not success:
            self.overall_success = False
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {suite_name}: {'通过' if success else '失败'}")
        if details:
            print(f"   详情: {details}")
        print()
    
    def run_integration_tests(self):
        """运行集成测试"""
        print("🔧 运行集成测试...")
        try:
            result = subprocess.run(
                [sys.executable, "test_comprehensive_integration.py"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            details = f"返回码: {result.returncode}"
            if result.stdout:
                details += f", 输出长度: {len(result.stdout)} 字符"
            if result.stderr:
                details += f", 错误: {result.stderr[:200]}..."
            
            self.log_suite_result("集成测试", success, details)
            return success
            
        except subprocess.TimeoutExpired:
            self.log_suite_result("集成测试", False, "测试超时")
            return False
        except Exception as e:
            self.log_suite_result("集成测试", False, f"执行异常: {e}")
            return False
    
    def run_api_tests(self):
        """运行API测试"""
        print("🌐 运行API测试...")
        try:
            result = subprocess.run(
                [sys.executable, "test_api_comprehensive.py"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            details = f"返回码: {result.returncode}"
            if result.stdout:
                details += f", 输出长度: {len(result.stdout)} 字符"
            if result.stderr:
                details += f", 错误: {result.stderr[:200]}..."
            
            self.log_suite_result("API测试", success, details)
            return success
            
        except subprocess.TimeoutExpired:
            self.log_suite_result("API测试", False, "测试超时")
            return False
        except Exception as e:
            self.log_suite_result("API测试", False, f"执行异常: {e}")
            return False
    
    def run_frontend_tests(self):
        """运行前端测试"""
        print("🖥️ 运行前端测试...")
        try:
            result = subprocess.run(
                [sys.executable, "test_frontend_integration.py"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            details = f"返回码: {result.returncode}"
            if result.stdout:
                details += f", 输出长度: {len(result.stdout)} 字符"
            if result.stderr:
                details += f", 错误: {result.stderr[:200]}..."
            
            self.log_suite_result("前端测试", success, details)
            return success
            
        except subprocess.TimeoutExpired:
            self.log_suite_result("前端测试", False, "测试超时")
            return False
        except Exception as e:
            self.log_suite_result("前端测试", False, f"执行异常: {e}")
            return False
    
    def run_e2e_tests(self):
        """运行端到端测试"""
        print("🎭 运行端到端测试...")
        try:
            result = subprocess.run(
                [sys.executable, "test_end_to_end_scenarios.py"],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            success = result.returncode == 0
            details = f"返回码: {result.returncode}"
            if result.stdout:
                details += f", 输出长度: {len(result.stdout)} 字符"
            if result.stderr:
                details += f", 错误: {result.stderr[:200]}..."
            
            self.log_suite_result("端到端测试", success, details)
            return success
            
        except subprocess.TimeoutExpired:
            self.log_suite_result("端到端测试", False, "测试超时")
            return False
        except Exception as e:
            self.log_suite_result("端到端测试", False, f"执行异常: {e}")
            return False
    
    def check_environment(self):
        """检查测试环境"""
        print("🔍 检查测试环境...")
        
        checks = {
            'Python版本': sys.version_info >= (3, 7),
            'requirements.txt存在': os.path.exists('requirements.txt'),
            'src目录存在': os.path.exists('src'),
            'templates目录存在': os.path.exists('templates'),
            'static目录存在': os.path.exists('static'),
            'uploads目录存在': os.path.exists('uploads') or True,  # 可以自动创建
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            status_icon = "✅" if passed else "❌"
            print(f"  {status_icon} {check_name}")
            if not passed:
                all_passed = False
        
        if not all_passed:
            print("⚠️ 环境检查发现问题，可能影响测试结果")
        else:
            print("✅ 环境检查通过")
        
        print()
        return all_passed
    
    def create_test_directories(self):
        """创建必要的测试目录"""
        directories = ['uploads', 'output', 'test_files']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        print("📁 测试目录已创建")
    
    def run_all_tests(self):
        """运行所有测试套件"""
        print("=" * 80)
        print("🧪 开始综合测试套件")
        print(f"⏰ 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 检查环境
        env_ok = self.check_environment()
        
        # 创建必要目录
        self.create_test_directories()
        
        # 运行测试套件
        test_suites = [
            ("集成测试", self.run_integration_tests),
            ("API测试", self.run_api_tests),
            ("前端测试", self.run_frontend_tests),
            ("端到端测试", self.run_e2e_tests),
        ]
        
        for suite_name, test_func in test_suites:
            print(f"🚀 开始 {suite_name}...")
            try:
                test_func()
            except Exception as e:
                self.log_suite_result(suite_name, False, f"运行异常: {e}")
            
            # 测试间隔
            time.sleep(2)
        
        # 生成综合报告
        self.generate_comprehensive_report()
        
        # 显示最终结果
        self.show_final_results()
        
        return self.overall_success
    
    def generate_comprehensive_report(self):
        """生成综合测试报告"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            'test_run_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'overall_success': self.overall_success
            },
            'environment': {
                'python_version': sys.version,
                'platform': sys.platform,
                'working_directory': os.getcwd()
            },
            'test_suites': self.test_results,
            'summary': {
                'total_suites': len(self.test_results),
                'passed_suites': sum(1 for r in self.test_results.values() if r['success']),
                'failed_suites': sum(1 for r in self.test_results.values() if not r['success'])
            }
        }
        
        # 保存报告
        report_file = f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📊 综合测试报告已保存: {report_file}")
        
        # 生成简化的文本报告
        text_report_file = f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(text_report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("综合测试报告\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"测试时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%H:%M:%S')}\n")
            f.write(f"测试时长: {duration.total_seconds():.1f} 秒\n")
            f.write(f"总体结果: {'✅ 全部通过' if self.overall_success else '❌ 存在失败'}\n\n")
            
            f.write("测试套件结果:\n")
            f.write("-" * 40 + "\n")
            for suite_name, result in self.test_results.items():
                status = "✅ 通过" if result['success'] else "❌ 失败"
                f.write(f"{suite_name}: {status}\n")
                if result.get('details'):
                    f.write(f"  详情: {result['details']}\n")
            
            f.write("\n" + "=" * 80 + "\n")
        
        print(f"📝 测试摘要已保存: {text_report_file}")
    
    def show_final_results(self):
        """显示最终测试结果"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("=" * 80)
        print("🏁 综合测试完成")
        print("=" * 80)
        
        print(f"⏰ 测试时长: {duration.total_seconds():.1f} 秒")
        print(f"📊 测试套件: {len(self.test_results)} 个")
        
        passed = sum(1 for r in self.test_results.values() if r['success'])
        failed = len(self.test_results) - passed
        
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        
        if self.overall_success:
            print("\n🎉 所有测试套件通过！系统可用性得到验证。")
        else:
            print("\n⚠️ 存在测试失败，需要进一步调查和修复。")
            print("\n失败的测试套件:")
            for suite_name, result in self.test_results.items():
                if not result['success']:
                    print(f"  ❌ {suite_name}: {result.get('details', '无详细信息')}")
        
        print("=" * 80)

def main():
    """主函数"""
    runner = ComprehensiveTestRunner()
    success = runner.run_all_tests()
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
