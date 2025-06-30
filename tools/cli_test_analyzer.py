#!/usr/bin/env python3
"""
CLI测试分析器 - 基于项目宪法的工程可用性持续改进
功能：定期复盘测试报告，补充遗漏场景和边界用例，持续提升工程可用性
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict


class CLITestAnalyzer:
    """CLI测试分析器 - 工程可用性持续改进"""
    
    def __init__(self, test_results_dir: str = "cliTests/test_results"):
        """初始化分析器"""
        self.test_results_dir = Path(test_results_dir)
        self.analysis_results = {
            "analysis_time": datetime.now().isoformat(),
            "test_coverage": {},
            "failure_patterns": {},
            "performance_issues": {},
            "missing_scenarios": {},
            "recommendations": [],
            "improvement_plan": {}
        }
    
    def analyze_test_reports(self, days: int = 30) -> Dict[str, Any]:
        """分析指定天数内的测试报告"""
        print(f"🔍 分析最近 {days} 天的CLI测试报告...")
        
        # 查找测试报告文件
        report_files = self._find_test_reports(days)
        
        if not report_files:
            print("❌ 未找到测试报告文件")
            return self.analysis_results
        
        print(f"📊 找到 {len(report_files)} 个测试报告文件")
        
        # 分析每个报告
        all_test_results = []
        for report_file in report_files:
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    all_test_results.append(report)
            except Exception as e:
                print(f"⚠️ 读取报告文件失败 {report_file}: {e}")
        
        if not all_test_results:
            print("❌ 无法读取任何测试报告")
            return self.analysis_results
        
        # 执行分析
        self._analyze_test_coverage(all_test_results)
        self._analyze_failure_patterns(all_test_results)
        self._analyze_performance_issues(all_test_results)
        self._identify_missing_scenarios(all_test_results)
        self._generate_recommendations()
        self._create_improvement_plan()
        
        return self.analysis_results
    
    def _find_test_reports(self, days: int) -> List[Path]:
        """查找指定天数内的测试报告"""
        cutoff_date = datetime.now() - timedelta(days=days)
        report_files = []
        
        if not self.test_results_dir.exists():
            return report_files
        
        for file_path in self.test_results_dir.glob("batch_test_report_*.json"):
            try:
                # 从文件名提取日期
                file_date_str = file_path.stem.replace("batch_test_report_", "")
                file_date = datetime.strptime(file_date_str, "%Y%m%d_%H%M%S")
                
                if file_date >= cutoff_date:
                    report_files.append(file_path)
            except ValueError:
                # 如果文件名格式不匹配，检查文件修改时间
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime >= cutoff_date:
                    report_files.append(file_path)
        
        # 也检查最新的 batch_test_report.json
        latest_report = self.test_results_dir / "batch_test_report.json"
        if latest_report.exists():
            file_mtime = datetime.fromtimestamp(latest_report.stat().st_mtime)
            if file_mtime >= cutoff_date:
                report_files.append(latest_report)
        
        return sorted(report_files)
    
    def _analyze_test_coverage(self, reports: List[Dict]) -> None:
        """分析测试覆盖率"""
        print("📈 分析测试覆盖率...")
        
        coverage_stats = {
            "total_runs": len(reports),
            "test_categories": defaultdict(lambda: {"runs": 0, "passes": 0, "failures": 0}),
            "priority_distribution": defaultdict(lambda: {"runs": 0, "passes": 0, "failures": 0}),
            "success_rate_trend": []
        }
        
        for report in reports:
            if "tests" not in report:
                continue
            
            # 按类别统计
            for test in report["tests"]:
                category = test.get("category", "未知")
                priority = test.get("priority", "未知")
                
                coverage_stats["test_categories"][category]["runs"] += 1
                coverage_stats["priority_distribution"][priority]["runs"] += 1
                
                if test.get("success", False):
                    coverage_stats["test_categories"][category]["passes"] += 1
                    coverage_stats["priority_distribution"][priority]["passes"] += 1
                else:
                    coverage_stats["test_categories"][category]["failures"] += 1
                    coverage_stats["priority_distribution"][priority]["failures"] += 1
            
            # 成功率趋势
            if "test_run_info" in report:
                success_rate = report["test_run_info"].get("success_rate", 0)
                coverage_stats["success_rate_trend"].append({
                    "date": report["test_run_info"].get("start_time", ""),
                    "success_rate": success_rate
                })
        
        self.analysis_results["test_coverage"] = dict(coverage_stats)
    
    def _analyze_failure_patterns(self, reports: List[Dict]) -> None:
        """分析失败模式"""
        print("🔍 分析失败模式...")
        
        failure_patterns = {
            "common_errors": defaultdict(int),
            "failing_tests": defaultdict(int),
            "error_categories": defaultdict(int),
            "suggestion_frequency": defaultdict(int)
        }
        
        for report in reports:
            if "tests" not in report:
                continue
            
            for test in report["tests"]:
                if not test.get("success", True):
                    test_name = test.get("name", "未知")
                    error_msg = test.get("error", "")
                    suggestion = test.get("suggestion", "")
                    
                    failure_patterns["failing_tests"][test_name] += 1
                    failure_patterns["suggestion_frequency"][suggestion] += 1
                    
                    # 分析错误类型
                    error_lower = error_msg.lower()
                    if "import" in error_lower:
                        failure_patterns["error_categories"]["依赖导入错误"] += 1
                    elif "connection" in error_lower or "timeout" in error_lower:
                        failure_patterns["error_categories"]["网络连接错误"] += 1
                    elif "file not found" in error_lower:
                        failure_patterns["error_categories"]["文件路径错误"] += 1
                    elif "permission" in error_lower:
                        failure_patterns["error_categories"]["权限错误"] += 1
                    elif "json" in error_lower:
                        failure_patterns["error_categories"]["数据格式错误"] += 1
                    elif "api" in error_lower:
                        failure_patterns["error_categories"]["API接口错误"] += 1
                    else:
                        failure_patterns["error_categories"]["其他错误"] += 1
                    
                    # 记录常见错误
                    failure_patterns["common_errors"][error_msg] += 1
        
        self.analysis_results["failure_patterns"] = dict(failure_patterns)
    
    def _analyze_performance_issues(self, reports: List[Dict]) -> None:
        """分析性能问题"""
        print("⚡ 分析性能问题...")
        
        performance_issues = {
            "slow_tests": [],
            "performance_trends": [],
            "timeout_issues": 0,
            "avg_duration_by_test": defaultdict(list)
        }
        
        for report in reports:
            if "tests" not in report:
                continue
            
            for test in report["tests"]:
                test_name = test.get("name", "未知")
                duration = test.get("duration", 0)
                
                performance_issues["avg_duration_by_test"][test_name].append(duration)
                
                # 识别慢速测试
                if duration > 60:  # 超过1分钟
                    performance_issues["slow_tests"].append({
                        "test_name": test_name,
                        "duration": duration,
                        "date": report.get("test_run_info", {}).get("start_time", "")
                    })
                
                # 识别超时问题
                if "timeout" in test.get("error", "").lower():
                    performance_issues["timeout_issues"] += 1
        
        # 计算平均耗时
        for test_name, durations in performance_issues["avg_duration_by_test"].items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                performance_issues["performance_trends"].append({
                    "test_name": test_name,
                    "avg_duration": avg_duration,
                    "max_duration": max(durations),
                    "min_duration": min(durations)
                })
        
        self.analysis_results["performance_issues"] = performance_issues
    
    def _identify_missing_scenarios(self, reports: List[Dict]) -> None:
        """识别遗漏的测试场景"""
        print("🎯 识别遗漏的测试场景...")
        
        missing_scenarios = {
            "edge_cases": [],
            "boundary_tests": [],
            "integration_scenarios": [],
            "error_handling": [],
            "data_validation": []
        }
        
        # 基于项目宪法的业务场景要求
        required_scenarios = {
            "edge_cases": [
                "空文件处理",
                "超大文件处理",
                "特殊字符处理",
                "编码格式处理",
                "网络异常处理"
            ],
            "boundary_tests": [
                "数据边界值测试",
                "并发处理测试",
                "内存限制测试",
                "磁盘空间测试"
            ],
            "integration_scenarios": [
                "多模块集成测试",
                "端到端流程测试",
                "数据流完整性测试",
                "状态一致性测试"
            ],
            "error_handling": [
                "异常输入处理",
                "错误恢复测试",
                "日志记录测试",
                "错误报告测试"
            ],
            "data_validation": [
                "数据格式验证",
                "数据完整性检查",
                "数据一致性验证",
                "数据安全性检查"
            ]
        }
        
        # 检查现有测试覆盖情况
        existing_tests = set()
        for report in reports:
            if "tests" in report:
                for test in report["tests"]:
                    existing_tests.add(test.get("name", ""))
        
        # 识别缺失的场景
        for category, scenarios in required_scenarios.items():
            for scenario in scenarios:
                if not any(scenario.lower() in test.lower() for test in existing_tests):
                    missing_scenarios[category].append(scenario)
        
        self.analysis_results["missing_scenarios"] = missing_scenarios
    
    def _generate_recommendations(self) -> None:
        """生成改进建议"""
        print("💡 生成改进建议...")
        
        recommendations = []
        
        # 基于失败模式生成建议
        failure_patterns = self.analysis_results["failure_patterns"]
        if failure_patterns.get("failing_tests"):
            most_failing_test = max(failure_patterns["failing_tests"].items(), key=lambda x: x[1])
            recommendations.append(f"重点关注测试 '{most_failing_test[0]}'，已失败 {most_failing_test[1]} 次")
        
        # 基于性能问题生成建议
        performance_issues = self.analysis_results["performance_issues"]
        if performance_issues.get("slow_tests"):
            recommendations.append(f"发现 {len(performance_issues['slow_tests'])} 个慢速测试，建议优化性能")
        
        # 基于缺失场景生成建议
        missing_scenarios = self.analysis_results["missing_scenarios"]
        total_missing = sum(len(scenarios) for scenarios in missing_scenarios.values())
        if total_missing > 0:
            recommendations.append(f"发现 {total_missing} 个遗漏的测试场景，建议补充测试用例")
        
        # 基于项目宪法的建议
        recommendations.extend([
            "定期运行CLI测试，确保工程可用性",
            "建立测试失败快速响应机制",
            "持续优化测试性能，提高反馈速度",
            "加强边界用例和异常场景测试",
            "建立测试覆盖率监控机制"
        ])
        
        self.analysis_results["recommendations"] = recommendations
    
    def _create_improvement_plan(self) -> None:
        """创建改进计划"""
        print("📋 创建改进计划...")
        
        improvement_plan = {
            "immediate_actions": [],
            "short_term_goals": [],
            "long_term_objectives": [],
            "priority_tasks": []
        }
        
        # 立即行动
        failure_patterns = self.analysis_results["failure_patterns"]
        if failure_patterns.get("failing_tests"):
            improvement_plan["immediate_actions"].append("修复频繁失败的测试用例")
        
        if self.analysis_results["performance_issues"].get("slow_tests"):
            improvement_plan["immediate_actions"].append("优化慢速测试的性能")
        
        # 短期目标
        missing_scenarios = self.analysis_results["missing_scenarios"]
        if any(missing_scenarios.values()):
            improvement_plan["short_term_goals"].append("补充遗漏的测试场景")
        
        improvement_plan["short_term_goals"].extend([
            "建立测试自动化监控",
            "完善错误处理机制",
            "优化测试数据管理"
        ])
        
        # 长期目标
        improvement_plan["long_term_objectives"].extend([
            "实现100%测试覆盖率",
            "建立持续改进机制",
            "提升工程可用性到99.9%",
            "建立完整的测试生态"
        ])
        
        # 优先级任务
        improvement_plan["priority_tasks"] = [
            "修复P1优先级测试失败",
            "补充边界用例测试",
            "优化测试执行性能",
            "建立测试报告分析机制"
        ]
        
        self.analysis_results["improvement_plan"] = improvement_plan
    
    def generate_analysis_report(self, output_file: Optional[str] = None) -> str:
        """生成分析报告"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"cli_test_analysis_report_{timestamp}.json"
        
        output_path = self.test_results_dir / output_file
        
        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        return str(output_path)
    
    def generate_html_report(self, output_file: Optional[str] = None) -> str:
        """生成HTML分析报告"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"cli_test_analysis_report_{timestamp}.html"
        
        output_path = self.test_results_dir / output_file
        
        html_content = self._generate_html_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def _generate_html_content(self) -> str:
        """生成HTML内容"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CLI测试分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
        .section {{ background: #f8f9fa; margin: 20px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .metric {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .success {{ border-left-color: #28a745; }}
        .warning {{ border-left-color: #ffc107; }}
        .danger {{ border-left-color: #dc3545; }}
        .chart {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; }}
        .recommendation {{ background: #e7f3ff; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
        .priority {{ font-weight: bold; color: #dc3545; }}
        .improvement {{ background: #f0f8f0; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 CLI测试分析报告</h1>
        <p>基于项目宪法的工程可用性持续改进分析</p>
        <p>分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="section">
        <h2>📊 测试覆盖率分析</h2>
        <div class="metric">
            <h3>总体统计</h3>
            <p><strong>分析报告数:</strong> {self.analysis_results['test_coverage'].get('total_runs', 0)}</p>
        </div>
        
        <div class="chart">
            <h3>测试类别分布</h3>
            {self._generate_category_chart()}
        </div>
        
        <div class="chart">
            <h3>优先级分布</h3>
            {self._generate_priority_chart()}
        </div>
    </div>

    <div class="section">
        <h2>🔍 失败模式分析</h2>
        <div class="metric danger">
            <h3>常见错误类型</h3>
            {self._generate_error_chart()}
        </div>
        
        <div class="metric warning">
            <h3>频繁失败的测试</h3>
            {self._generate_failing_tests_chart()}
        </div>
    </div>

    <div class="section">
        <h2>⚡ 性能问题分析</h2>
        <div class="metric warning">
            <h3>慢速测试</h3>
            {self._generate_performance_chart()}
        </div>
    </div>

    <div class="section">
        <h2>🎯 遗漏场景识别</h2>
        <div class="metric">
            <h3>缺失的测试场景</h3>
            {self._generate_missing_scenarios_chart()}
        </div>
    </div>

    <div class="section">
        <h2>💡 改进建议</h2>
        {self._generate_recommendations_html()}
    </div>

    <div class="section">
        <h2>📋 改进计划</h2>
        {self._generate_improvement_plan_html()}
    </div>

    <div class="header">
        <h2>🎯 项目宪法合规性</h2>
        <p>本分析基于《AI编程项目终极实践手册》的工程可用性要求</p>
        <p>持续改进是项目宪法的核心原则</p>
    </div>
</body>
</html>
"""
    
    def _generate_category_chart(self) -> str:
        """生成类别分布图表"""
        categories = self.analysis_results.get("test_coverage", {}).get("test_categories", {})
        if not categories:
            return "<p>暂无数据</p>"
        
        html = "<ul>"
        for category, stats in categories.items():
            total = stats["runs"]
            passes = stats["passes"]
            success_rate = (passes / total * 100) if total > 0 else 0
            html += f"<li><strong>{category}:</strong> {passes}/{total} ({success_rate:.1f}%)</li>"
        html += "</ul>"
        return html
    
    def _generate_priority_chart(self) -> str:
        """生成优先级分布图表"""
        priorities = self.analysis_results.get("test_coverage", {}).get("priority_distribution", {})
        if not priorities:
            return "<p>暂无数据</p>"
        
        html = "<ul>"
        for priority, stats in priorities.items():
            total = stats["runs"]
            passes = stats["passes"]
            success_rate = (passes / total * 100) if total > 0 else 0
            status_class = "success" if success_rate >= 90 else "warning" if success_rate >= 70 else "danger"
            html += f"<li class='{status_class}'><strong>{priority}:</strong> {passes}/{total} ({success_rate:.1f}%)</li>"
        html += "</ul>"
        return html
    
    def _generate_error_chart(self) -> str:
        """生成错误类型图表"""
        error_categories = self.analysis_results.get("failure_patterns", {}).get("error_categories", {})
        if not error_categories:
            return "<p>暂无错误数据</p>"
        
        html = "<ul>"
        for error_type, count in sorted(error_categories.items(), key=lambda x: x[1], reverse=True):
            html += f"<li><strong>{error_type}:</strong> {count}次</li>"
        html += "</ul>"
        return html
    
    def _generate_failing_tests_chart(self) -> str:
        """生成失败测试图表"""
        failing_tests = self.analysis_results.get("failure_patterns", {}).get("failing_tests", {})
        if not failing_tests:
            return "<p>暂无失败测试数据</p>"
        
        html = "<ul>"
        for test_name, count in sorted(failing_tests.items(), key=lambda x: x[1], reverse=True)[:5]:
            html += f"<li><strong>{test_name}:</strong> 失败{count}次</li>"
        html += "</ul>"
        return html
    
    def _generate_performance_chart(self) -> str:
        """生成性能图表"""
        slow_tests = self.analysis_results.get("performance_issues", {}).get("slow_tests", [])
        if not slow_tests:
            return "<p>暂无慢速测试数据</p>"
        
        html = "<ul>"
        for test in slow_tests[:5]:
            html += f"<li><strong>{test['test_name']}:</strong> {test['duration']:.2f}秒</li>"
        html += "</ul>"
        return html
    
    def _generate_missing_scenarios_chart(self) -> str:
        """生成缺失场景图表"""
        missing_scenarios = self.analysis_results.get("missing_scenarios", {})
        if not any(missing_scenarios.values()):
            return "<p>暂无缺失场景</p>"
        
        html = "<ul>"
        for category, scenarios in missing_scenarios.items():
            if scenarios:
                html += f"<li><strong>{category}:</strong> {', '.join(scenarios)}</li>"
        html += "</ul>"
        return html
    
    def _generate_recommendations_html(self) -> str:
        """生成建议HTML"""
        recommendations = self.analysis_results.get("recommendations", [])
        if not recommendations:
            return "<p>暂无建议</p>"
        
        html = ""
        for rec in recommendations:
            html += f'<div class="recommendation">{rec}</div>'
        return html
    
    def _generate_improvement_plan_html(self) -> str:
        """生成改进计划HTML"""
        plan = self.analysis_results.get("improvement_plan", {})
        
        html = ""
        for section, items in plan.items():
            if items:
                html += f"<h3>{section.replace('_', ' ').title()}</h3>"
                html += "<ul>"
                for item in items:
                    html += f"<li>{item}</li>"
                html += "</ul>"
        
        return html


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="CLI测试分析器")
    parser.add_argument("--days", type=int, default=30, help="分析最近N天的测试报告")
    parser.add_argument("--output", help="输出文件名")
    parser.add_argument("--html", action="store_true", help="生成HTML报告")
    
    args = parser.parse_args()
    
    analyzer = CLITestAnalyzer()
    
    # 执行分析
    analysis_results = analyzer.analyze_test_reports(args.days)
    
    # 生成报告
    json_report = analyzer.generate_analysis_report(args.output)
    print(f"📄 JSON分析报告已生成: {json_report}")
    
    if args.html:
        html_report = analyzer.generate_html_report()
        print(f"📄 HTML分析报告已生成: {html_report}")
    
    # 输出关键发现
    print("\n🎯 关键发现:")
    if analysis_results["failure_patterns"].get("failing_tests"):
        most_failing = max(analysis_results["failure_patterns"]["failing_tests"].items(), key=lambda x: x[1])
        print(f"  最频繁失败的测试: {most_failing[0]} (失败{most_failing[1]}次)")
    
    if analysis_results["performance_issues"].get("slow_tests"):
        print(f"  发现 {len(analysis_results['performance_issues']['slow_tests'])} 个慢速测试")
    
    missing_count = sum(len(scenarios) for scenarios in analysis_results["missing_scenarios"].values())
    if missing_count > 0:
        print(f"  发现 {missing_count} 个遗漏的测试场景")
    
    print(f"\n💡 改进建议数量: {len(analysis_results['recommendations'])}")
    print("✅ 分析完成，请查看生成的报告文件")


if __name__ == "__main__":
    main() 