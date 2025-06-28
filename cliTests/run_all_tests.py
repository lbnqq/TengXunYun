#!/usr/bin/env python3
"""
批量运行所有业务功能测试脚本
功能：依次执行所有业务场景的贯通性测试
"""

import os
import sys
import argparse
import subprocess
import time
import json
from pathlib import Path


class TestRunner:
    """测试运行器"""
    
    def __init__(self, base_url: str = "http://localhost:5000", verbose: bool = True):
        """初始化测试运行器"""
        self.base_url = base_url
        self.verbose = verbose
        self.start_time = time.time()
        self.test_results = []
        
        # 获取当前脚本所在目录
        self.cli_tests_dir = Path(__file__).parent
        
        # 测试配置
        self.test_configs = [
            {
                "name": "格式对齐测试",
                "script": str(self.cli_tests_dir / "test_format_alignment.py"),
                "args": ["test_data/format_alignment/source.txt", "test_data/format_alignment/target.txt"],
                "output": "test_results/format_alignment_output.txt"
            },
            {
                "name": "文风统一测试",
                "script": str(self.cli_tests_dir / "test_style_alignment.py"),
                "args": ["test_data/style_alignment/reference.txt", "test_data/style_alignment/target.txt"],
                "output": "test_results/style_alignment_output.txt"
            },
            {
                "name": "智能填报测试",
                "script": str(self.cli_tests_dir / "test_document_fill.py"),
                "args": ["test_data/document_fill/template.txt", "test_data/document_fill/data.json"],
                "output": "test_results/document_fill_output.txt"
            },
            {
                "name": "文档评审测试",
                "script": str(self.cli_tests_dir / "test_document_review.py"),
                "args": ["test_data/document_review/document.txt"],
                "output": "test_results/document_review_output.txt"
            },
            {
                "name": "表格填充测试",
                "script": str(self.cli_tests_dir / "test_table_fill.py"),
                "args": ["test_data/table_fill/table.json", "test_data/table_fill/data.json"],
                "output": "test_results/table_fill_output.json"
            }
        ]
    
    def create_test_data(self):
        """创建测试数据"""
        print("创建测试数据...")
        
        # 创建测试数据目录
        test_data_dir = Path("test_data")
        test_data_dir.mkdir(exist_ok=True)
        
        # 格式对齐测试数据
        format_dir = test_data_dir / "format_alignment"
        format_dir.mkdir(exist_ok=True)
        
        with open(format_dir / "source.txt", "w", encoding="utf-8") as f:
            f.write("""# 参考格式文档

## 标题格式
这是标准的标题格式，使用Markdown语法。

### 子标题
子标题使用三级标题格式。

## 段落格式
这是标准的段落格式，包含适当的空行和缩进。

### 列表格式
- 项目1
- 项目2
  - 子项目2.1
  - 子项目2.2
- 项目3

## 代码格式
```python
def example_function():
    return "这是代码示例"
```

## 表格格式
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
| 数据4 | 数据5 | 数据6 |
""")
        
        with open(format_dir / "target.txt", "w", encoding="utf-8") as f:
            f.write("""# 待处理文档

标题格式
这是不标准的标题格式，没有使用Markdown语法。

子标题
子标题格式也不标准。

段落格式
这是不标准的段落格式，缺少适当的空行和缩进。

列表格式
* 项目1
* 项目2
* 子项目2.1
* 子项目2.2
* 项目3

代码格式
def example_function():
    return "这是代码示例"

表格格式
列1 列2 列3
数据1 数据2 数据3
数据4 数据5 数据6
""")
        
        # 文风统一测试数据
        style_dir = test_data_dir / "style_alignment"
        style_dir.mkdir(exist_ok=True)
        
        with open(style_dir / "reference.txt", "w", encoding="utf-8") as f:
            f.write("""# 参考风格文档

## 学术风格
本文档采用正式的学术写作风格，语言严谨、客观，使用专业术语，避免主观表达。

### 研究方法
本研究采用定量分析方法，通过问卷调查收集数据，运用统计软件进行数据分析。

### 结论
基于上述分析，我们可以得出以下结论：该方案具有可行性和有效性。
""")
        
        with open(style_dir / "target.txt", "w", encoding="utf-8") as f:
            f.write("""# 待调整文档

## 内容分析
我觉得这个方案挺好的，应该可以解决问题。

### 方法说明
我们用了问卷调查，然后用软件算了一下数据。

### 总结
总的来说，这个方案不错，应该能用。
""")
        
        # 智能填报测试数据
        fill_dir = test_data_dir / "document_fill"
        fill_dir.mkdir(exist_ok=True)
        
        with open(fill_dir / "template.txt", "w", encoding="utf-8") as f:
            f.write("""# 项目申请书

## 项目基本信息
- 项目名称：{project_name}
- 申请人：{applicant_name}
- 申请日期：{application_date}
- 项目类型：{project_type}

## 项目描述
{project_description}

## 技术方案
{technical_solution}

## 预期成果
{expected_results}

## 预算信息
- 总预算：{total_budget}元
- 设备费用：{equipment_cost}元
- 人员费用：{personnel_cost}元
- 其他费用：{other_cost}元
""")
        
        with open(fill_dir / "data.json", "w", encoding="utf-8") as f:
            json.dump({
                "project_name": "智能文档处理系统",
                "applicant_name": "张三",
                "application_date": "2024-01-15",
                "project_type": "软件开发",
                "project_description": "开发一个基于AI的智能文档处理系统，支持多种文档格式的自动识别和处理。",
                "technical_solution": "采用深度学习技术，结合自然语言处理，实现文档的智能分析和处理。",
                "expected_results": "完成系统开发，提供完整的文档处理解决方案。",
                "total_budget": "500000",
                "equipment_cost": "200000",
                "personnel_cost": "250000",
                "other_cost": "50000"
            }, f, ensure_ascii=False, indent=2)
        
        # 文档评审测试数据
        review_dir = test_data_dir / "document_review"
        review_dir.mkdir(exist_ok=True)
        
        with open(review_dir / "document.txt", "w", encoding="utf-8") as f:
            f.write("""# 技术方案文档

## 项目概述
本项目旨在开发一个智能文档处理系统。

## 技术架构
系统采用前后端分离架构，前端使用Vue.js，后端使用Python Flask。

## 功能模块
1. 文档上传
2. 格式转换
3. 内容分析
4. 智能处理

## 技术选型
- 前端框架：Vue.js
- 后端框架：Flask
- 数据库：MySQL
- AI模型：BERT

## 项目计划
第一阶段：需求分析
第二阶段：系统设计
第三阶段：开发实现
第四阶段：测试部署

## 风险评估
技术风险：AI模型训练可能遇到困难
时间风险：开发周期可能延长
成本风险：硬件投入可能超预算
""")
        
        # 表格填充测试数据
        table_dir = test_data_dir / "table_fill"
        table_dir.mkdir(exist_ok=True)
        
        with open(table_dir / "table.json", "w", encoding="utf-8") as f:
            json.dump({
                "tables": [
                    {
                        "columns": ["姓名", "年龄", "职位", "部门"],
                        "data": [
                            ["张三", "", "", ""],
                            ["李四", "", "", ""],
                            ["王五", "", "", ""]
                        ]
                    },
                    {
                        "columns": ["项目名称", "负责人", "开始日期", "结束日期", "状态"],
                        "data": [
                            ["项目A", "", "", "", ""],
                            ["项目B", "", "", "", ""]
                        ]
                    }
                ]
            }, f, ensure_ascii=False, indent=2)
        
        with open(table_dir / "data.json", "w", encoding="utf-8") as f:
            json.dump({
                "fill_data": [
                    {"姓名": "张三", "年龄": "25", "职位": "工程师", "部门": "技术部"},
                    {"姓名": "李四", "年龄": "30", "职位": "经理", "部门": "管理部"},
                    {"姓名": "王五", "年龄": "28", "职位": "设计师", "部门": "设计部"},
                    {"项目名称": "项目A", "负责人": "张三", "开始日期": "2024-01-01", "结束日期": "2024-06-30", "状态": "进行中"},
                    {"项目名称": "项目B", "负责人": "李四", "开始日期": "2024-02-01", "结束日期": "2024-08-31", "状态": "计划中"}
                ]
            }, f, ensure_ascii=False, indent=2)
        
        print("测试数据创建完成")
    
    def run_single_test(self, config: dict) -> dict:
        """运行单个测试"""
        test_name = config["name"]
        script_path = config["script"]
        args = config["args"]
        output = config["output"]
        
        print(f"\n{'='*60}")
        print(f"开始执行: {test_name}")
        print(f"{'='*60}")
        
        # 构建命令
        cmd = [sys.executable, script_path] + args + [output, "--url", self.base_url]
        if self.verbose:
            cmd.append("--verbose")
        
        start_time = time.time()
        
        try:
            # 执行测试
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 分析结果
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            test_result = {
                "name": test_name,
                "script": script_path,
                "success": success,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "output_file": output
            }
            
            if success:
                print(f"✅ {test_name} - 成功 ({duration:.2f}秒)")
            else:
                print(f"❌ {test_name} - 失败 ({duration:.2f}秒)")
                if stderr:
                    print(f"错误信息: {stderr}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} - 超时")
            return {
                "name": test_name,
                "script": script_path,
                "success": False,
                "duration": 300,
                "return_code": -1,
                "stdout": "",
                "stderr": "测试超时",
                "output_file": output
            }
        except Exception as e:
            print(f"💥 {test_name} - 异常: {str(e)}")
            return {
                "name": test_name,
                "script": script_path,
                "success": False,
                "duration": 0,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "output_file": output
            }
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🚀 开始批量测试")
        print(f"API基础URL: {self.base_url}")
        print(f"详细输出: {self.verbose}")
        
        # 创建测试结果目录
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        # 创建测试数据
        self.create_test_data()
        
        # 运行所有测试
        for config in self.test_configs:
            result = self.run_single_test(config)
            self.test_results.append(result)
        
        # 生成测试报告
        self.generate_report()
        
        # 统计结果
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"\n{'='*60}")
        print("测试完成")
        print(f"{'='*60}")
        print(f"总测试数: {total_tests}")
        print(f"成功: {successful_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {successful_tests/total_tests*100:.1f}%")
        
        return failed_tests == 0
    
    def generate_report(self):
        """生成测试报告"""
        report = {
            "test_run": {
                "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time)),
                "end_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": time.time() - self.start_time,
                "base_url": self.base_url,
                "verbose": self.verbose
            },
            "summary": {
                "total_tests": len(self.test_results),
                "successful_tests": sum(1 for r in self.test_results if r["success"]),
                "failed_tests": sum(1 for r in self.test_results if not r["success"]),
                "success_rate": sum(1 for r in self.test_results if r["success"]) / len(self.test_results) * 100
            },
            "test_results": self.test_results
        }
        
        # 保存报告
        report_file = "test_results/batch_test_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试报告已保存: {report_file}")
        
        # 生成简化的HTML报告
        self.generate_html_report(report)
    
    def generate_html_report(self, report: dict):
        """生成HTML报告"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>业务功能贯通性测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
        .success {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
        .failure {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
        .details {{ margin-top: 10px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>业务功能贯通性测试报告</h1>
        <p>测试时间: {report['test_run']['start_time']}</p>
        <p>API地址: {report['test_run']['base_url']}</p>
    </div>
    
    <div class="summary">
        <h2>测试摘要</h2>
        <p>总测试数: {report['summary']['total_tests']}</p>
        <p>成功: {report['summary']['successful_tests']}</p>
        <p>失败: {report['summary']['failed_tests']}</p>
        <p>成功率: {report['summary']['success_rate']:.1f}%</p>
    </div>
    
    <div class="test-results">
        <h2>详细结果</h2>
"""
        
        for result in report['test_results']:
            status_class = "success" if result['success'] else "failure"
            status_icon = "✅" if result['success'] else "❌"
            
            html_content += f"""
        <div class="test-result {status_class}">
            <h3>{status_icon} {result['name']}</h3>
            <p>脚本: {result['script']}</p>
            <p>执行时间: {result['duration']:.2f}秒</p>
            <p>输出文件: {result['output_file']}</p>
            <div class="details">
                <strong>标准输出:</strong><br>
                <pre>{result['stdout'][:500]}{'...' if len(result['stdout']) > 500 else ''}</pre>
                {f"<strong>错误输出:</strong><br><pre>{result['stderr']}</pre>" if result['stderr'] else ''}
            </div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        html_file = "test_results/batch_test_report.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"HTML报告已保存: {html_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="批量运行所有业务功能测试")
    parser.add_argument("--url", default="http://localhost:5000", help="API基础URL")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--create-data-only", action="store_true", help="仅创建测试数据")
    
    args = parser.parse_args()
    
    runner = TestRunner(args.url, args.verbose)
    
    if args.create_data_only:
        runner.create_test_data()
        print("测试数据创建完成")
        return
    
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 