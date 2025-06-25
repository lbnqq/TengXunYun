#!/usr/bin/env python3
"""
测试优化功能的综合测试脚本
验证LLM效率、用户界面、批量处理和性能监控功能
"""

import os
import sys
import time
import json
import requests
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.monitoring import get_performance_monitor, PerformanceTimer
from src.core.tools.batch_processor import get_batch_processor
from src.llm_clients.multi_llm import EnhancedMultiLLMClient
from src.core.database import get_database_manager, PerformanceRepository

class OptimizationTester:
    """优化功能测试器"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
        
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行优化功能测试...")
        print("=" * 60)
        
        # 测试1: LLM客户端优化
        self.test_llm_optimizations()
        
        # 测试2: 性能监控
        self.test_performance_monitoring()
        
        # 测试3: 批量处理
        self.test_batch_processing()
        
        # 测试4: 用户界面API
        self.test_ui_apis()
        
        # 测试5: 数据库性能
        self.test_database_performance()
        
        # 生成测试报告
        self.generate_report()
    
    def test_llm_optimizations(self):
        """测试LLM客户端优化"""
        print("📊 测试LLM客户端优化...")
        
        try:
            # 创建增强的LLM客户端
            llm_client = EnhancedMultiLLMClient()
            
            # 测试缓存功能
            print("  - 测试缓存功能...")
            prompt = "这是一个测试提示"
            
            # 第一次调用
            start_time = time.time()
            response1 = llm_client.generate(prompt)
            first_call_time = time.time() - start_time
            
            # 第二次调用（应该使用缓存）
            start_time = time.time()
            response2 = llm_client.generate(prompt)
            second_call_time = time.time() - start_time
            
            cache_effective = second_call_time < first_call_time * 0.5
            
            # 测试性能报告
            print("  - 测试性能报告...")
            performance_report = llm_client.get_performance_report()
            
            # 测试健康状态
            print("  - 测试健康状态...")
            health_status = llm_client.get_health_status()
            
            self.test_results['llm_optimizations'] = {
                'cache_effective': cache_effective,
                'first_call_time': first_call_time,
                'second_call_time': second_call_time,
                'performance_report_available': bool(performance_report),
                'health_status_available': bool(health_status),
                'healthy_endpoints': len(health_status.get('healthy_endpoints', [])),
                'total_endpoints': health_status.get('total_endpoints', 0)
            }
            
            print(f"    ✅ 缓存效果: {'有效' if cache_effective else '无效'}")
            print(f"    ✅ 健康端点: {len(health_status.get('healthy_endpoints', []))}/{health_status.get('total_endpoints', 0)}")
            
        except Exception as e:
            print(f"    ❌ LLM优化测试失败: {e}")
            self.test_results['llm_optimizations'] = {'error': str(e)}
    
    def test_performance_monitoring(self):
        """测试性能监控"""
        print("📈 测试性能监控...")
        
        try:
            # 获取性能监控器
            monitor = get_performance_monitor()
            
            # 测试性能记录
            print("  - 测试性能记录...")
            with PerformanceTimer('test_operation') as timer:
                time.sleep(0.1)  # 模拟操作
            
            # 测试统计获取
            print("  - 测试统计获取...")
            current_stats = monitor.get_current_stats()
            operation_stats = monitor.get_operation_stats()
            
            # 测试时间序列数据
            print("  - 测试时间序列数据...")
            time_series = monitor.get_time_series_data()
            
            # 测试性能摘要
            print("  - 测试性能摘要...")
            summary = monitor.get_performance_summary()
            
            self.test_results['performance_monitoring'] = {
                'current_stats_available': bool(current_stats),
                'operation_stats_available': bool(operation_stats),
                'time_series_available': bool(time_series),
                'summary_available': bool(summary),
                'total_operations': summary.get('total_operations', 0),
                'success_rate': summary.get('success_rate', 0.0)
            }
            
            print(f"    ✅ 总操作数: {summary.get('total_operations', 0)}")
            print(f"    ✅ 成功率: {summary.get('success_rate', 0.0):.2%}")
            
        except Exception as e:
            print(f"    ❌ 性能监控测试失败: {e}")
            self.test_results['performance_monitoring'] = {'error': str(e)}
    
    def test_batch_processing(self):
        """测试批量处理"""
        print("🔄 测试批量处理...")
        
        try:
            # 获取批量处理器
            batch_processor = get_batch_processor()
            
            # 注册测试处理器
            def test_processor(file_path, config):
                time.sleep(0.5)  # 模拟处理时间
                return {'success': True, 'message': f'处理完成: {file_path}'}
            
            batch_processor.register_processor('test_operation', test_processor)
            
            # 创建测试文件
            test_files = []
            for i in range(3):
                test_file = f"test_file_{i}.txt"
                with open(test_file, 'w') as f:
                    f.write(f"测试文件内容 {i}")
                test_files.append(test_file)
            
            # 创建批量作业
            print("  - 创建批量作业...")
            job_id = batch_processor.create_batch_job(
                "测试批量作业",
                test_files,
                {'operation': 'test_operation'}
            )
            
            # 启动作业
            print("  - 启动批量作业...")
            success = batch_processor.start_batch_job(job_id)
            
            if success:
                # 等待作业完成
                print("  - 等待作业完成...")
                max_wait = 30  # 最多等待30秒
                start_wait = time.time()
                
                while time.time() - start_wait < max_wait:
                    status = batch_processor.get_job_status(job_id)
                    if status and status['status'] in ['completed', 'failed']:
                        break
                    time.sleep(1)
                
                final_status = batch_processor.get_job_status(job_id)
                
                self.test_results['batch_processing'] = {
                    'job_created': bool(job_id),
                    'job_started': success,
                    'final_status': final_status['status'] if final_status else 'unknown',
                    'total_files': final_status['total_files'] if final_status else 0,
                    'processed_files': final_status['progress']['processed'] if final_status else 0,
                    'successful_files': final_status['progress']['successful'] if final_status else 0
                }
                
                print(f"    ✅ 作业状态: {final_status['status'] if final_status else 'unknown'}")
                print(f"    ✅ 处理文件: {final_status['progress']['processed'] if final_status else 0}/{final_status['total_files'] if final_status else 0}")
            
            # 清理测试文件
            for test_file in test_files:
                if os.path.exists(test_file):
                    os.remove(test_file)
                    
        except Exception as e:
            print(f"    ❌ 批量处理测试失败: {e}")
            self.test_results['batch_processing'] = {'error': str(e)}
    
    def test_ui_apis(self):
        """测试用户界面API"""
        print("🖥️ 测试用户界面API...")
        
        try:
            # 测试性能统计API
            print("  - 测试性能统计API...")
            response = self.session.get(f"{self.base_url}/api/performance/stats")
            stats_available = response.status_code == 200
            
            # 测试API健康状态
            print("  - 测试API健康状态...")
            response = self.session.get(f"{self.base_url}/api/performance/health")
            health_available = response.status_code == 200
            
            # 测试操作分解统计
            print("  - 测试操作分解统计...")
            response = self.session.get(f"{self.base_url}/api/performance/operations")
            operations_available = response.status_code == 200
            
            # 测试批量作业列表
            print("  - 测试批量作业列表...")
            response = self.session.get(f"{self.base_url}/api/batch/jobs")
            batch_jobs_available = response.status_code == 200
            
            self.test_results['ui_apis'] = {
                'performance_stats_api': stats_available,
                'health_api': health_available,
                'operations_api': operations_available,
                'batch_jobs_api': batch_jobs_available,
                'all_apis_working': all([stats_available, health_available, operations_available, batch_jobs_available])
            }
            
            working_apis = sum([stats_available, health_available, operations_available, batch_jobs_available])
            print(f"    ✅ 可用API: {working_apis}/4")
            
        except Exception as e:
            print(f"    ❌ UI API测试失败: {e}")
            self.test_results['ui_apis'] = {'error': str(e)}
    
    def test_database_performance(self):
        """测试数据库性能"""
        print("💾 测试数据库性能...")
        
        try:
            # 获取数据库管理器
            db_manager = get_database_manager()
            
            # 测试数据库连接
            print("  - 测试数据库连接...")
            with db_manager.get_connection() as conn:
                result = conn.execute("SELECT 1").fetchone()
                db_connected = result[0] == 1
            
            # 测试性能仓库
            print("  - 测试性能仓库...")
            perf_repo = PerformanceRepository()
            stats = perf_repo.get_performance_stats()
            
            # 测试数据库统计
            print("  - 测试数据库统计...")
            db_stats = db_manager.get_database_stats()
            
            self.test_results['database_performance'] = {
                'connection_working': db_connected,
                'performance_repo_working': bool(stats),
                'database_stats_available': bool(db_stats),
                'total_tables': len([k for k in db_stats.keys() if k.endswith('_count')]) if db_stats else 0
            }
            
            print(f"    ✅ 数据库连接: {'正常' if db_connected else '异常'}")
            print(f"    ✅ 数据表数量: {len([k for k in db_stats.keys() if k.endswith('_count')]) if db_stats else 0}")
            
        except Exception as e:
            print(f"    ❌ 数据库性能测试失败: {e}")
            self.test_results['database_performance'] = {'error': str(e)}
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📋 测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if 'error' not in result)
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {total_tests - passed_tests}")
        print(f"成功率: {passed_tests/total_tests:.1%}")
        
        print("\n详细结果:")
        for test_name, result in self.test_results.items():
            status = "❌ 失败" if 'error' in result else "✅ 通过"
            print(f"  {test_name}: {status}")
            if 'error' in result:
                print(f"    错误: {result['error']}")
        
        # 保存详细报告到文件
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': total_tests - passed_tests,
                    'success_rate': passed_tests/total_tests
                },
                'detailed_results': self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n详细报告已保存到: {report_file}")

def main():
    """主函数"""
    print("🔧 Office-Doc-Agent 优化功能测试")
    print("=" * 60)
    
    # 检查是否需要启动Web服务器
    try:
        response = requests.get("http://localhost:5000/api/config", timeout=5)
        server_running = response.status_code == 200
    except:
        server_running = False
    
    if not server_running:
        print("⚠️  Web服务器未运行，请先启动服务器:")
        print("   python src/web_app.py")
        print("\n继续进行离线测试...")
    
    # 运行测试
    tester = OptimizationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
