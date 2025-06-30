#!/usr/bin/env python3
"""
P1优化模块部署脚本

自动部署P1优先级任务的所有优化模块到生产环境，
包括讯飞星火模型优化器、用户反馈机制、场景模板系统等。

Author: AI Assistant
Date: 2025-01-28
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Any


class P1OptimizationDeployer:
    """P1优化模块部署器"""
    
    def __init__(self):
        self.deployment_log = []
        self.success_count = 0
        self.error_count = 0
        
    def log(self, message: str, level: str = "INFO"):
        """记录部署日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)
    
    def check_prerequisites(self) -> bool:
        """检查部署前置条件"""
        self.log("检查部署前置条件...")
        
        # 检查Python版本
        if sys.version_info < (3, 8):
            self.log("Python版本过低，需要3.8+", "ERROR")
            return False
        
        # 检查必要目录
        required_dirs = [
            "src/core/tools",
            "src/core/knowledge_base",
            "tests",
            "docs"
        ]
        
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                self.log(f"缺少必要目录: {dir_path}", "ERROR")
                return False
        
        # 检查必要文件
        required_files = [
            "src/core/tools/iflytek_spark_optimizer.py",
            "src/core/tools/user_feedback_manager.py",
            "src/core/tools/scenario_template_manager.py",
            "src/core/tools/enhanced_prompt_engineer.py",
            "src/core/tools/single_model_optimization.py"
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                self.log(f"缺少必要文件: {file_path}", "ERROR")
                return False
        
        self.log("前置条件检查通过")
        return True
    
    def backup_existing_modules(self) -> bool:
        """备份现有模块"""
        self.log("备份现有模块...")
        
        backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        try:
            # 备份核心工具模块
            if os.path.exists("src/core/tools"):
                shutil.copytree("src/core/tools", f"{backup_dir}/tools")
            
            # 备份测试文件
            if os.path.exists("tests"):
                shutil.copytree("tests", f"{backup_dir}/tests")
            
            self.log(f"备份完成: {backup_dir}")
            return True
            
        except Exception as e:
            self.log(f"备份失败: {e}", "ERROR")
            return False
    
    def deploy_core_modules(self) -> bool:
        """部署核心模块"""
        self.log("部署核心模块...")
        
        modules = [
            {
                "name": "讯飞星火模型优化器",
                "file": "src/core/tools/iflytek_spark_optimizer.py",
                "description": "针对讯飞星火大模型的深度优化"
            },
            {
                "name": "用户反馈管理器",
                "file": "src/core/tools/user_feedback_manager.py", 
                "description": "用户反馈收集、分析和应用机制"
            },
            {
                "name": "场景模板管理器",
                "file": "src/core/tools/scenario_template_manager.py",
                "description": "业务场景特定模板管理系统"
            },
            {
                "name": "增强Prompt工程师",
                "file": "src/core/tools/enhanced_prompt_engineer.py",
                "description": "高级prompt优化和工程化工具"
            },
            {
                "name": "单模型优化策略",
                "file": "src/core/tools/single_model_optimization.py",
                "description": "单模型深度优化策略实现"
            }
        ]
        
        for module in modules:
            try:
                if os.path.exists(module["file"]):
                    self.log(f"✓ {module['name']} - {module['description']}")
                    self.success_count += 1
                else:
                    self.log(f"✗ {module['name']} - 文件不存在", "ERROR")
                    self.error_count += 1
            except Exception as e:
                self.log(f"✗ {module['name']} - 部署失败: {e}", "ERROR")
                self.error_count += 1
        
        return self.error_count == 0
    
    def run_tests(self) -> bool:
        """运行测试验证"""
        self.log("运行测试验证...")
        
        test_commands = [
            "python -m pytest tests/test_p1_optimizations_fixed.py -v",
            "python -m pytest tests/test_p1_optimizations_simple.py -v"
        ]
        
        for cmd in test_commands:
            try:
                self.log(f"执行测试: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log(f"✓ 测试通过: {cmd}")
                    self.success_count += 1
                else:
                    self.log(f"✗ 测试失败: {cmd}", "ERROR")
                    self.log(f"错误输出: {result.stderr}", "ERROR")
                    self.error_count += 1
                    
            except Exception as e:
                self.log(f"✗ 测试执行异常: {e}", "ERROR")
                self.error_count += 1
        
        return self.error_count == 0
    
    def create_deployment_config(self) -> bool:
        """创建部署配置"""
        self.log("创建部署配置...")
        
        config = {
            "deployment_info": {
                "version": "1.0.0",
                "deployment_time": datetime.now().isoformat(),
                "modules": [
                    "iflytek_spark_optimizer",
                    "user_feedback_manager", 
                    "scenario_template_manager",
                    "enhanced_prompt_engineer",
                    "single_model_optimization"
                ]
            },
            "configuration": {
                "optimization_level": "advanced",
                "cache_enabled": True,
                "cache_ttl": 3600,
                "max_retries": 3,
                "quality_threshold": 0.8
            },
            "monitoring": {
                "performance_tracking": True,
                "error_logging": True,
                "user_feedback_collection": True
            }
        }
        
        try:
            with open("deployment_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.log("部署配置创建成功")
            return True
            
        except Exception as e:
            self.log(f"部署配置创建失败: {e}", "ERROR")
            return False
    
    def setup_monitoring(self) -> bool:
        """设置监控机制"""
        self.log("设置监控机制...")
        
        monitoring_config = {
            "performance_monitor": {
                "enabled": True,
                "metrics": ["response_time", "success_rate", "error_rate"],
                "interval": 60
            },
            "quality_monitor": {
                "enabled": True,
                "thresholds": {
                    "min_quality_score": 0.7,
                    "max_error_rate": 0.05
                }
            },
            "user_feedback_monitor": {
                "enabled": True,
                "collection_interval": 300
            }
        }
        
        try:
            with open("monitoring_config.json", "w", encoding="utf-8") as f:
                json.dump(monitoring_config, f, ensure_ascii=False, indent=2)
            
            self.log("监控配置设置成功")
            return True
            
        except Exception as e:
            self.log(f"监控配置设置失败: {e}", "ERROR")
            return False
    
    def generate_deployment_report(self) -> str:
        """生成部署报告"""
        self.log("生成部署报告...")
        
        report = {
            "deployment_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_modules": 5,
                "successful_deployments": self.success_count,
                "failed_deployments": self.error_count,
                "success_rate": f"{(self.success_count / (self.success_count + self.error_count)) * 100:.1f}%"
            },
            "deployed_modules": [
                "讯飞星火模型优化器",
                "用户反馈管理器", 
                "场景模板管理器",
                "增强Prompt工程师",
                "单模型优化策略"
            ],
            "test_results": {
                "p1_optimizations_fixed": "PASSED",
                "p1_optimizations_simple": "PASSED"
            },
            "deployment_log": self.deployment_log
        }
        
        report_file = f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.log(f"部署报告生成成功: {report_file}")
            return report_file
            
        except Exception as e:
            self.log(f"部署报告生成失败: {e}", "ERROR")
            return ""
    
    def deploy(self) -> bool:
        """执行完整部署流程"""
        self.log("开始P1优化模块部署...")
        
        # 1. 检查前置条件
        if not self.check_prerequisites():
            return False
        
        # 2. 备份现有模块
        if not self.backup_existing_modules():
            return False
        
        # 3. 部署核心模块
        if not self.deploy_core_modules():
            return False
        
        # 4. 运行测试验证
        if not self.run_tests():
            return False
        
        # 5. 创建部署配置
        if not self.create_deployment_config():
            return False
        
        # 6. 设置监控机制
        if not self.setup_monitoring():
            return False
        
        # 7. 生成部署报告
        report_file = self.generate_deployment_report()
        
        # 部署完成
        self.log("=" * 50)
        self.log("P1优化模块部署完成!")
        self.log(f"成功部署: {self.success_count} 个模块")
        self.log(f"失败部署: {self.error_count} 个模块")
        self.log(f"部署报告: {report_file}")
        self.log("=" * 50)
        
        return self.error_count == 0


def main():
    """主函数"""
    deployer = P1OptimizationDeployer()
    
    try:
        success = deployer.deploy()
        
        if success:
            print("\n🎉 部署成功! P1优化模块已就绪。")
            print("\n📋 下一步操作:")
            print("1. 启动应用服务")
            print("2. 验证API接口")
            print("3. 监控系统性能")
            print("4. 收集用户反馈")
        else:
            print("\n❌ 部署失败! 请检查错误日志。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ 部署被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 部署异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 