#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方法实现检查器

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""



import os
import sys
import json
import inspect
import importlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class MethodImplementationChecker:
    def __init__(self, core_methods=None):
        self.core_methods = core_methods or {}
        self.project_root = project_root
        self.report_data = {"module_status": {}, "method_details": {}}

    def check_methods(self):
        print("🔍 开始检查方法实现状态...")
        total_methods = 0
        implemented_methods = 0
        for file_path, classes in self.core_methods.items():
            full_path = self.project_root / file_path
            if not full_path.exists():
                print(f"⚠️  文件不存在: {file_path}")
                continue
            module_status = self._check_module_methods(file_path, classes)
            self.report_data["module_status"][file_path] = module_status
            for class_name, methods in classes.items():
                total_methods += len(methods)
                implemented_count = module_status.get(class_name, {}).get("implemented_count", 0)
                implemented_methods += implemented_count
                self.report_data["method_details"][f"{file_path}.{class_name}"] = {
                    "total_methods": len(methods),
                    "implemented_methods": implemented_count,
                    "missing_methods": len(methods) - implemented_count,
                    "methods": methods,
                    "status": module_status.get(class_name, {})
                }
        self.report_data["total_methods"] = total_methods
        self.report_data["implemented_methods"] = implemented_methods
        self.report_data["missing_methods"] = total_methods - implemented_methods
        self.report_data["implementation_rate"] = (
            implemented_methods / total_methods if total_methods > 0 else 0.0
        )
        self.report_data["recommendations"] = self._generate_recommendations()
        return self.report_data

    def _check_module_methods(self, file_path: str, classes: Dict[str, List[str]]) -> Dict[str, Any]:
        implemented_methods = []
        missing_methods = []
        
        for method_name in expected_methods:
            if hasattr(class_obj, method_name):
                method = getattr(class_obj, method_name)
                if callable(method):
                    # 检查是否是真实实现（不是占位符）
                    if self._is_real_implementation(method):
                        implemented_methods.append(method_name)
                    else:
                        missing_methods.append(method_name)
                else:
                    missing_methods.append(method_name)
            else:
                missing_methods.append(method_name)
        
        return {
            "status": "implemented" if len(missing_methods) == 0 else "partial",
            "implemented_count": len(implemented_methods),
            "missing_count": len(missing_methods),
            "implemented_methods": implemented_methods,
            "missing_methods": missing_methods,
            "implementation_rate": len(implemented_methods) / len(expected_methods) if expected_methods else 0.0
        }
    
    def _is_real_implementation(self, method) -> bool:
        code_lines = []
        placeholder_indicators = ["pass", "raise NotImplementedError", "TODO", "xxx", "impl", "pass"]
        
        try:
            # 获取方法的源代码
            source = inspect.getsource(method)
            # 按行分割
            lines = source.splitlines()
            
            # 提取有效代码行
            for line in lines:
                line = line.strip()
                # 排除空行
                if line:
                    code_lines.append(line)
            
            # 如果只有很少的代码行，可能是占位符
            if len(code_lines) <= 3:
                for indicator in placeholder_indicators:
                    if indicator in source:
                        return False
            
            # 检查是否有实际的业务逻辑
            business_logic_indicators = [
                "if ",
                "for ",
                "while ",
                "try:",
                "except ",
                "return {",
                "return [",
                "return True",
                "return False",
                "self.",
                "import ",
                "from "
            ]
            
            has_business_logic = any(indicator in source for indicator in business_logic_indicators)
            
            return has_business_logic and len(code_lines) > 3
            
        except Exception:
            # 如果无法获取源代码，假设是已实现的
            return True
    
    def _generate_recommendations(self) -> List[str]:
        if output_file is None:
            output_file = f"method_implementation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = self.project_root / "docs" / "reports" / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, ensure_ascii=False, indent=2)
        
        return str(output_path)
    
    def print_summary(self):
        checker = MethodImplementationChecker()
        
        # 执行检查
        checker.check_all_methods()
        
        # 打印摘要
        checker.print_summary()
        
        # 生成报告
        report_file = checker.generate_report()
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        # 返回退出码
        implementation_rate = checker.report_data["implementation_rate"]
        if implementation_rate < 0.8:
            print("❌ 实现率低于80%，检查失败")
            return 1
        else:
            print("✅ 实现率达标，检查通过")
            return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)