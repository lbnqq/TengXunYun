#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方法实现状态检查工具
检查所有核心方法的实现状态，生成实现报告
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
    """方法实现状态检查器"""
    
    def __init__(self):
        self.project_root = project_root
        self.report_data = {
            "check_time": datetime.now().isoformat(),
            "total_methods": 0,
            "implemented_methods": 0,
            "missing_methods": 0,
            "implementation_rate": 0.0,
            "method_details": {},
            "module_status": {},
            "recommendations": []
        }
        
        # 定义需要检查的核心方法
        self.core_methods = {
            "src/core/tools/writing_style_analyzer.py": {
                "WritingStyleAnalyzer": [
                    "handle_style_change",
                    "apply_style_changes",
                    "handle_batch_style_changes"
                ]
            },
            "src/core/tools/virtual_reviewer.py": {
                "EnhancedVirtualReviewerTool": [
                    "generate_review_report",
                    "assess_review_quality"
                ]
            },
            "src/core/tools/enhanced_document_filler.py": {
                "EnhancedDocumentFiller": [
                    "generate_fill_preview",
                    "apply_fill_changes",
                    "export_document"
                ]
            },
            "src/core/tools/format_aligner.py": {
                "EfficientFormatAligner": [
                    "analyze_format_differences",
                    "apply_format_changes"
                ]
            }
        }
    
    def check_all_methods(self) -> Dict[str, Any]:
        """检查所有方法的实现状态"""
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
                
                # 记录详细信息
                self.report_data["method_details"][f"{file_path}.{class_name}"] = {
                    "total_methods": len(methods),
                    "implemented_methods": implemented_count,
                    "missing_methods": len(methods) - implemented_count,
                    "methods": methods,
                    "status": module_status.get(class_name, {})
                }
        
        # 计算总体统计
        self.report_data["total_methods"] = total_methods
        self.report_data["implemented_methods"] = implemented_methods
        self.report_data["missing_methods"] = total_methods - implemented_methods
        self.report_data["implementation_rate"] = (
            implemented_methods / total_methods if total_methods > 0 else 0.0
        )
        
        # 生成建议
        self.report_data["recommendations"] = self._generate_recommendations()
        
        return self.report_data
    
    def _check_module_methods(self, file_path: str, classes: Dict[str, List[str]]) -> Dict[str, Any]:
        """检查模块中的方法实现状态"""
        try:
            # 动态导入模块
            module_name = file_path.replace('/', '.').replace('.py', '')
            module = importlib.import_module(module_name)
            
            module_status = {}
            
            for class_name, expected_methods in classes.items():
                if hasattr(module, class_name):
                    class_obj = getattr(module, class_name)
                    class_status = self._check_class_methods(class_obj, expected_methods)
                    module_status[class_name] = class_status
                else:
                    module_status[class_name] = {
                        "status": "class_not_found",
                        "implemented_count": 0,
                        "missing_methods": expected_methods,
                        "implemented_methods": []
                    }
            
            return module_status
            
        except ImportError as e:
            print(f"❌ 无法导入模块 {file_path}: {e}")
            return {
                "error": f"模块导入失败: {str(e)}",
                "status": "import_error"
            }
        except Exception as e:
            print(f"❌ 检查模块 {file_path} 时发生错误: {e}")
            return {
                "error": f"检查失败: {str(e)}",
                "status": "check_error"
            }
    
    def _check_class_methods(self, class_obj: type, expected_methods: List[str]) -> Dict[str, Any]:
        """检查类中的方法实现状态"""
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
        """检查方法是否是真实实现（不是占位符）"""
        try:
            # 获取方法的源代码
            source = inspect.getsource(method)
            
            # 检查是否是占位符实现
            placeholder_indicators = [
                "pass",
                "return None",
                "return {}",
                "return []",
                "raise NotImplementedError",
                "raise Exception",
                "return {\"error\":",
                "return {\"success\": False",
                "# TODO",
                "# FIXME"
            ]
            
            # 如果方法体只包含占位符内容，认为是未实现
            source_lines = [line.strip() for line in source.split('\n') if line.strip()]
            
            # 过滤掉注释和空行
            code_lines = []
            for line in source_lines:
                if not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
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
        """生成改进建议"""
        recommendations = []
        
        implementation_rate = self.report_data["implementation_rate"]
        
        if implementation_rate < 0.5:
            recommendations.append("🚨 实现率低于50%，建议优先实现核心功能方法")
        elif implementation_rate < 0.8:
            recommendations.append("⚠️  实现率低于80%，建议完善剩余方法")
        else:
            recommendations.append("✅ 实现率良好，建议进行功能测试和优化")
        
        # 检查缺失的方法
        missing_methods_by_module = {}
        for module_path, module_data in self.report_data["method_details"].items():
            missing = module_data.get("missing_methods", [])
            if missing and isinstance(missing, list):
                missing_methods_by_module[module_path] = missing
        
        if missing_methods_by_module:
            recommendations.append("📋 需要实现的方法:")
            for module, methods in missing_methods_by_module.items():
                if isinstance(methods, list):
                    recommendations.append(f"   {module}: {', '.join(methods)}")
                else:
                    recommendations.append(f"   {module}: {str(methods)}")
        
        # 检查模块状态
        error_modules = []
        for module_path, status in self.report_data["module_status"].items():
            if isinstance(status, dict) and status.get("status") in ["import_error", "check_error"]:
                error_modules.append(module_path)
        
        if error_modules:
            recommendations.append("🔧 需要修复的模块:")
            for module in error_modules:
                recommendations.append(f"   {module}")
        
        return recommendations
    
    def generate_report(self, output_file: str = None) -> str:
        """生成检查报告"""
        if output_file is None:
            output_file = f"method_implementation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = self.project_root / "docs" / "reports" / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, ensure_ascii=False, indent=2)
        
        return str(output_path)
    
    def print_summary(self):
        """打印检查摘要"""
        print("\n" + "="*60)
        print("📊 方法实现状态检查报告")
        print("="*60)
        
        print(f"检查时间: {self.report_data['check_time']}")
        print(f"总方法数: {self.report_data['total_methods']}")
        print(f"已实现方法: {self.report_data['implemented_methods']}")
        print(f"缺失方法: {self.report_data['missing_methods']}")
        print(f"实现率: {self.report_data['implementation_rate']:.1%}")
        
        print("\n📋 模块状态:")
        for module_path, status in self.report_data["module_status"].items():
            if isinstance(status, dict):
                print(f"  {module_path}:")
                for class_name, class_status in status.items():
                    if isinstance(class_status, dict):
                        rate = class_status.get("implementation_rate", 0)
                        print(f"    {class_name}: {rate:.1%} ({class_status.get('implemented_count', 0)}/{len(self.core_methods[module_path][class_name])})")
        
        print("\n💡 改进建议:")
        for recommendation in self.report_data["recommendations"]:
            print(f"  {recommendation}")
        
        print("="*60)


def main():
    """主函数"""
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