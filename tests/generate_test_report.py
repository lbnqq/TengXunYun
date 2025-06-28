#!/usr/bin/env python3
"""
测试报告生成脚本
生成全面的测试报告，包括覆盖率、性能、质量等指标

Author: AI Assistant
Date: 2025-01-28
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def generate_test_report():
    """生成测试报告"""
    print("📊 开始生成测试报告...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project": "office-doc-agent",
        "test_summary": {},
        "coverage": {},
        "quality": {},
        "performance": {},
        "mvp_tests": {},
        "recommendations": []
    }
    
    # 1. 运行单元测试
    print("🔍 运行单元测试...")
    success, stdout, stderr = run_command("pytest tests/ -v --tb=short")
    report["test_summary"]["unit_tests"] = {
        "success": success,
        "output": stdout,
        "error": stderr
    }
    
    # 2. 运行覆盖率测试
    print("🔍 运行覆盖率测试...")
    success, stdout, stderr = run_command("pytest tests/ --cov=src --cov-report=json --cov-report=html")
    report["test_summary"]["coverage_tests"] = {
        "success": success,
        "output": stdout,
        "error": stderr
    }
    
    # 3. 运行MVP功能测试
    print("🔍 运行MVP功能测试...")
    success, stdout, stderr = run_command("python tests/test_mvp_functionality.py")
    report["mvp_tests"] = {
        "success": success,
        "output": stdout,
        "error": stderr
    }
    
    # 4. 代码质量检查
    print("🔍 运行代码质量检查...")
    
    # Flake8检查
    success, stdout, stderr = run_command("flake8 src/ tests/ --max-line-length=120 --ignore=E203,W503")
    report["quality"]["flake8"] = {
        "success": success,
        "output": stdout,
        "error": stderr
    }
    
    # MyPy类型检查
    success, stdout, stderr = run_command("mypy src/ --ignore-missing-imports --no-strict-optional")
    report["quality"]["mypy"] = {
        "success": success,
        "output": stdout,
        "error": stderr
    }
    
    # 5. 安全检查
    print("🔍 运行安全检查...")
    success, stdout, stderr = run_command("bandit -r src/ -f json")
    report["quality"]["security"] = {
        "success": success,
        "output": stdout,
        "error": stderr
    }
    
    # 6. 桩子函数检测
    print("🔍 运行桩子函数检测...")
    success, stdout, stderr = run_command("python tools/stub_function_detector.py --json docs/stub_detection_result.json")
    report["quality"]["stub_detection"] = {
        "success": success,
        "output": stdout,
        "error": stderr
    }
    
    # 7. 生成建议
    recommendations = []
    
    if not report["mvp_tests"]["success"]:
        recommendations.append("MVP功能测试失败，需要修复相关功能")
    
    if not report["quality"]["flake8"]["success"]:
        recommendations.append("代码风格检查失败，需要修复代码格式问题")
    
    if not report["quality"]["mypy"]["success"]:
        recommendations.append("类型检查失败，需要修复类型注解问题")
    
    if not report["quality"]["security"]["success"]:
        recommendations.append("安全检查发现问题，需要修复安全漏洞")
    
    report["recommendations"] = recommendations
    
    # 8. 保存报告
    report_file = f"test_results/comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("test_results", exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 9. 生成HTML报告
    generate_html_report(report, report_file)
    
    print(f"✅ 测试报告已生成: {report_file}")
    return report

def generate_html_report(report, json_file):
    """生成HTML格式的测试报告"""
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Office Doc Agent - 测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .warning {{ color: orange; }}
        .code {{ background: #f5f5f5; padding: 10px; border-radius: 3px; font-family: monospace; }}
        .recommendation {{ background: #fff3cd; padding: 10px; border-radius: 3px; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Office Doc Agent - 测试报告</h1>
        <p>生成时间: {report['timestamp']}</p>
        <p>项目: {report['project']}</p>
    </div>
    
    <div class="section">
        <h2>测试摘要</h2>
        <p><strong>单元测试:</strong> <span class="{'success' if report['test_summary']['unit_tests']['success'] else 'error'}">
            {'✅ 通过' if report['test_summary']['unit_tests']['success'] else '❌ 失败'}
        </span></p>
        <p><strong>覆盖率测试:</strong> <span class="{'success' if report['test_summary']['coverage_tests']['success'] else 'error'}">
            {'✅ 通过' if report['test_summary']['coverage_tests']['success'] else '❌ 失败'}
        </span></p>
        <p><strong>MVP功能测试:</strong> <span class="{'success' if report['mvp_tests']['success'] else 'error'}">
            {'✅ 通过' if report['mvp_tests']['success'] else '❌ 失败'}
        </span></p>
    </div>
    
    <div class="section">
        <h2>代码质量</h2>
        <p><strong>Flake8检查:</strong> <span class="{'success' if report['quality']['flake8']['success'] else 'error'}">
            {'✅ 通过' if report['quality']['flake8']['success'] else '❌ 失败'}
        </span></p>
        <p><strong>MyPy类型检查:</strong> <span class="{'success' if report['quality']['mypy']['success'] else 'error'}">
            {'✅ 通过' if report['quality']['mypy']['success'] else '❌ 失败'}
        </span></p>
        <p><strong>安全检查:</strong> <span class="{'success' if report['quality']['security']['success'] else 'error'}">
            {'✅ 通过' if report['quality']['security']['success'] else '❌ 失败'}
        </span></p>
        <p><strong>桩子函数检测:</strong> <span class="{'success' if report['quality']['stub_detection']['success'] else 'error'}">
            {'✅ 通过' if report['quality']['stub_detection']['success'] else '❌ 失败'}
        </span></p>
    </div>
    
    <div class="section">
        <h2>建议</h2>
        {''.join([f'<div class="recommendation">💡 {rec}</div>' for rec in report['recommendations']])}
        {f'<p class="success">✅ 所有检查通过，代码质量良好！</p>' if not report['recommendations'] else ''}
    </div>
    
    <div class="section">
        <h2>详细信息</h2>
        <p>完整的JSON报告: <a href="{json_file}">{json_file}</a></p>
    </div>
</body>
</html>
    """
    
    html_file = json_file.replace('.json', '.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML报告已生成: {html_file}")

if __name__ == '__main__':
    report = generate_test_report()
    
    # 打印摘要
    print("\n" + "="*60)
    print("📊 测试报告摘要")
    print("="*60)
    
    print(f"单元测试: {'✅ 通过' if report['test_summary']['unit_tests']['success'] else '❌ 失败'}")
    print(f"覆盖率测试: {'✅ 通过' if report['test_summary']['coverage_tests']['success'] else '❌ 失败'}")
    print(f"MVP功能测试: {'✅ 通过' if report['mvp_tests']['success'] else '❌ 失败'}")
    print(f"代码质量检查: {'✅ 通过' if all(q['success'] for q in report['quality'].values()) else '❌ 失败'}")
    
    if report['recommendations']:
        print("\n💡 建议:")
        for rec in report['recommendations']:
            print(f"   - {rec}")
    else:
        print("\n✅ 所有检查通过！")
    
    sys.exit(0 if not report['recommendations'] else 1) 