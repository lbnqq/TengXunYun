#!/usr/bin/env python3
"""
性能和压力端到端测试
测试API在不同负载下的性能表现
"""

import sys
import os
import time
import json
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Tuple
from test_e2e_framework import E2ETestFramework

class PerformanceTests:
    """性能测试"""
    
    def __init__(self, framework: E2ETestFramework):
        self.framework = framework
        self.api_tester = framework.api_tester
    
    def measure_api_response_time(self, tables: List[Dict], fill_data: List[Dict], iterations: int = 10) -> Dict[str, float]:
        """测量API响应时间"""
        response_times = []
        
        for i in range(iterations):
            start_time = time.time()
            success, result = self.api_tester.test_table_fill_api(tables, fill_data)
            end_time = time.time()
            
            if success:
                response_times.append(end_time - start_time)
            else:
                print(f"   第{i+1}次请求失败: {result}")
        
        if not response_times:
            return {"error": "所有请求都失败"}
        
        return {
            "min": min(response_times),
            "max": max(response_times),
            "avg": statistics.mean(response_times),
            "median": statistics.median(response_times),
            "std": statistics.stdev(response_times) if len(response_times) > 1 else 0,
            "success_rate": len(response_times) / iterations * 100
        }
    
    def test_small_table_performance(self) -> bool:
        """测试小表格性能"""
        print("   测试小表格性能 (10行数据)")
        
        tables = [{
            "columns": ["ID", "姓名", "部门"],
            "data": [[f"ID{i:02d}", "", ""] for i in range(10)]
        }]
        
        fill_data = [
            {"ID": f"ID{i:02d}", "姓名": f"员工{i:02d}", "部门": "技术部" if i % 2 == 0 else "市场部"}
            for i in range(10)
        ]
        
        metrics = self.measure_api_response_time(tables, fill_data, iterations=20)
        
        if "error" in metrics:
            print(f"   小表格性能测试失败: {metrics['error']}")
            return False
        
        print(f"   小表格性能指标:")
        print(f"     平均响应时间: {metrics['avg']:.3f}秒")
        print(f"     最小响应时间: {metrics['min']:.3f}秒")
        print(f"     最大响应时间: {metrics['max']:.3f}秒")
        print(f"     成功率: {metrics['success_rate']:.1f}%")
        
        # 性能标准：小表格平均响应时间应小于1秒
        return metrics['avg'] < 1.0 and metrics['success_rate'] >= 95.0
    
    def test_medium_table_performance(self) -> bool:
        """测试中等表格性能"""
        print("   测试中等表格性能 (100行数据)")
        
        tables = [{
            "columns": ["ID", "姓名", "部门", "职位", "薪资"],
            "data": [[f"ID{i:03d}", "", "", "", ""] for i in range(100)]
        }]
        
        fill_data = [
            {
                "ID": f"ID{i:03d}",
                "姓名": f"员工{i:03d}",
                "部门": "技术部" if i % 2 == 0 else "市场部",
                "职位": "工程师" if i % 3 == 0 else "经理",
                "薪资": str(5000 + i * 100)
            }
            for i in range(100)
        ]
        
        metrics = self.measure_api_response_time(tables, fill_data, iterations=10)
        
        if "error" in metrics:
            print(f"   中等表格性能测试失败: {metrics['error']}")
            return False
        
        print(f"   中等表格性能指标:")
        print(f"     平均响应时间: {metrics['avg']:.3f}秒")
        print(f"     最小响应时间: {metrics['min']:.3f}秒")
        print(f"     最大响应时间: {metrics['max']:.3f}秒")
        print(f"     成功率: {metrics['success_rate']:.1f}%")
        
        # 性能标准：中等表格平均响应时间应小于3秒
        return metrics['avg'] < 3.0 and metrics['success_rate'] >= 90.0
    
    def test_large_table_performance(self) -> bool:
        """测试大表格性能"""
        print("   测试大表格性能 (500行数据)")
        
        tables = [{
            "columns": ["ID", "姓名", "部门", "职位", "薪资", "入职日期"],
            "data": [[f"ID{i:04d}", "", "", "", "", ""] for i in range(500)]
        }]
        
        fill_data = [
            {
                "ID": f"ID{i:04d}",
                "姓名": f"员工{i:04d}",
                "部门": ["技术部", "市场部", "财务部", "人事部"][i % 4],
                "职位": ["工程师", "经理", "总监", "专员"][i % 4],
                "薪资": str(5000 + i * 50),
                "入职日期": f"2024-{(i % 12) + 1:02d}-01"
            }
            for i in range(500)
        ]
        
        metrics = self.measure_api_response_time(tables, fill_data, iterations=5)
        
        if "error" in metrics:
            print(f"   大表格性能测试失败: {metrics['error']}")
            return False
        
        print(f"   大表格性能指标:")
        print(f"     平均响应时间: {metrics['avg']:.3f}秒")
        print(f"     最小响应时间: {metrics['min']:.3f}秒")
        print(f"     最大响应时间: {metrics['max']:.3f}秒")
        print(f"     成功率: {metrics['success_rate']:.1f}%")
        
        # 性能标准：大表格平均响应时间应小于10秒
        return metrics['avg'] < 10.0 and metrics['success_rate'] >= 80.0
    
    def test_concurrent_requests(self) -> bool:
        """测试并发请求性能"""
        print("   测试并发请求性能 (10个并发请求)")
        
        tables = [{
            "columns": ["ID", "数据", "时间戳"],
            "data": [["1", "", ""], ["2", "", ""], ["3", "", ""]]
        }]
        
        fill_data = [
            {"ID": "1", "数据": "测试数据1", "时间戳": "2024-01-01 10:00:00"},
            {"ID": "2", "数据": "测试数据2", "时间戳": "2024-01-01 10:01:00"},
            {"ID": "3", "数据": "测试数据3", "时间戳": "2024-01-01 10:02:00"}
        ]
        
        def single_request():
            start_time = time.time()
            success, result = self.api_tester.test_table_fill_api(tables, fill_data)
            end_time = time.time()
            return success, end_time - start_time
        
        # 执行并发请求
        concurrent_requests = 10
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(single_request) for _ in range(concurrent_requests)]
            results = []
            
            for future in as_completed(futures):
                try:
                    success, response_time = future.result()
                    results.append((success, response_time))
                except Exception as e:
                    results.append((False, 0))
        
        total_time = time.time() - start_time
        
        # 分析结果
        successful_requests = sum(1 for success, _ in results if success)
        response_times = [rt for success, rt in results if success]
        
        if not response_times:
            print("   并发请求测试失败: 所有请求都失败")
            return False
        
        success_rate = successful_requests / concurrent_requests * 100
        avg_response_time = statistics.mean(response_times)
        throughput = successful_requests / total_time
        
        print(f"   并发请求性能指标:")
        print(f"     成功请求数: {successful_requests}/{concurrent_requests}")
        print(f"     成功率: {success_rate:.1f}%")
        print(f"     平均响应时间: {avg_response_time:.3f}秒")
        print(f"     总执行时间: {total_time:.3f}秒")
        print(f"     吞吐量: {throughput:.2f} 请求/秒")
        
        # 性能标准：并发成功率应大于80%，平均响应时间小于2秒
        return success_rate >= 80.0 and avg_response_time < 2.0
    
    def test_memory_usage(self) -> bool:
        """测试内存使用情况"""
        print("   测试内存使用情况")
        
        try:
            import psutil
            
            # 获取当前进程信息
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            print(f"   初始内存使用: {initial_memory:.2f} MB")
            
            # 执行多次大数据请求
            large_tables = [{
                "columns": ["ID"] + [f"数据{i}" for i in range(10)],
                "data": [[f"ROW{j:04d}"] + [f"数据{j}_{i}" for i in range(10)] for j in range(200)]
            }]

            large_fill_data = [
                dict({"ID": f"ROW{j:04d}"}, **{f"数据{i}": f"填充值{j}_{i}" for i in range(10)})
                for j in range(200)
            ]
            
            # 执行5次大数据请求
            for i in range(5):
                success, result = self.api_tester.test_table_fill_api(large_tables, large_fill_data)
                if not success:
                    print(f"   第{i+1}次大数据请求失败")
                
                current_memory = process.memory_info().rss / 1024 / 1024
                print(f"   第{i+1}次请求后内存: {current_memory:.2f} MB")
            
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = final_memory - initial_memory
            
            print(f"   最终内存使用: {final_memory:.2f} MB")
            print(f"   内存增长: {memory_increase:.2f} MB")
            
            # 内存标准：内存增长应小于100MB
            return memory_increase < 100.0
            
        except ImportError:
            print("   psutil未安装，跳过内存测试")
            return True
        except Exception as e:
            print(f"   内存测试异常: {str(e)}")
            return False

def run_performance_tests():
    """运行性能测试"""
    print("🚀 开始性能和压力端到端测试")
    
    framework = E2ETestFramework(port=5004)  # 使用不同端口
    
    try:
        if not framework.setup():
            print("❌ 测试环境设置失败")
            return False
        
        # 创建测试实例
        perf_tests = PerformanceTests(framework)
        
        # 定义测试用例
        test_cases = [
            ("小表格性能", perf_tests.test_small_table_performance),
            ("中等表格性能", perf_tests.test_medium_table_performance),
            ("大表格性能", perf_tests.test_large_table_performance),
            ("并发请求性能", perf_tests.test_concurrent_requests),
            ("内存使用测试", perf_tests.test_memory_usage),
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
    success = run_performance_tests()
    sys.exit(0 if success else 1)
