#!/usr/bin/env python3
"""
开发环境设置脚本

自动配置项目开发环境，包括Git配置、Pre-commit hooks、
代码质量工具等，确保所有开发者使用统一的开发规范。

Author: AI Assistant (Claude)
Created: 2025-06-25
Last Modified: 2025-06-25
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any

class DevEnvironmentSetup:
    """
    开发环境设置器
    
    自动配置项目开发环境，确保所有开发者使用统一的规范和工具。
    
    Author: AI Assistant (Claude)
    Date: 2025-06-25
    AI Assisted: 是
    """
    
    def __init__(self, project_root: str = "."):
        """
        初始化开发环境设置器
        
        Args:
            project_root (str): 项目根目录
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        self.project_root = Path(project_root).resolve()
        self.setup_steps = []
        self.errors = []
        
    def run_command(self, command: List[str], description: str) -> bool:
        """
        运行命令
        
        Args:
            command (List[str]): 命令和参数
            description (str): 命令描述
            
        Returns:
            bool: 是否成功
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        try:
            print(f"🔧 {description}...")
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ {description} 完成")
            return True
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ {description} 失败: {e.stderr.strip() if e.stderr else str(e)}"
            print(error_msg)
            self.errors.append(error_msg)
            return False
        except FileNotFoundError:
            error_msg = f"❌ {description} 失败: 命令未找到 {command[0]}"
            print(error_msg)
            self.errors.append(error_msg)
            return False
    
    def check_python_version(self) -> bool:
        """
        检查Python版本
        
        Returns:
            bool: 版本是否符合要求
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        print("🐍 检查Python版本...")
        
        if sys.version_info < (3, 8):
            error_msg = f"❌ Python版本过低: {sys.version}，需要Python 3.8+"
            print(error_msg)
            self.errors.append(error_msg)
            return False
        
        print(f"✅ Python版本: {sys.version}")
        return True
    
    def setup_git_config(self) -> bool:
        """
        设置Git配置
        
        Returns:
            bool: 是否成功
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        print("📝 设置Git配置...")
        
        # 设置提交模板
        gitmessage_path = self.project_root / ".gitmessage"
        if gitmessage_path.exists():
            success = self.run_command(
                ["git", "config", "commit.template", str(gitmessage_path)],
                "设置Git提交模板"
            )
            if not success:
                return False
        
        # 设置其他Git配置
        git_configs = [
            ("core.autocrlf", "input"),
            ("core.safecrlf", "true"),
            ("pull.rebase", "false"),
            ("init.defaultBranch", "main")
        ]
        
        for key, value in git_configs:
            success = self.run_command(
                ["git", "config", key, value],
                f"设置Git配置 {key}={value}"
            )
            if not success:
                return False
        
        return True
    
    def install_python_dependencies(self) -> bool:
        """
        安装Python依赖
        
        Returns:
            bool: 是否成功
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        print("📦 安装Python依赖...")
        
        # 检查requirements.txt
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("⚠️ requirements.txt 不存在，跳过依赖安装")
            return True
        
        # 安装项目依赖
        success = self.run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            "安装项目依赖"
        )
        if not success:
            return False
        
        # 安装开发工具
        dev_packages = [
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pre-commit>=3.0",
            "isort>=5.12"
        ]
        
        for package in dev_packages:
            success = self.run_command(
                [sys.executable, "-m", "pip", "install", package],
                f"安装开发工具 {package}"
            )
            if not success:
                print(f"⚠️ 安装 {package} 失败，继续...")
        
        return True
    
    def setup_pre_commit(self) -> bool:
        """
        设置Pre-commit hooks
        
        Returns:
            bool: 是否成功
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        print("🪝 设置Pre-commit hooks...")
        
        # 检查配置文件
        config_file = self.project_root / ".pre-commit-config.yaml"
        if not config_file.exists():
            print("⚠️ .pre-commit-config.yaml 不存在，跳过Pre-commit设置")
            return True
        
        # 安装pre-commit hooks
        success = self.run_command(
            ["pre-commit", "install"],
            "安装Pre-commit hooks"
        )
        if not success:
            return False
        
        # 安装commit-msg hook
        success = self.run_command(
            ["pre-commit", "install", "--hook-type", "commit-msg"],
            "安装Commit-msg hook"
        )
        if not success:
            print("⚠️ 安装commit-msg hook失败，继续...")
        
        return True
    
    def setup_vscode_config(self) -> bool:
        """
        设置VSCode配置
        
        Returns:
            bool: 是否成功
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        print("💻 设置VSCode配置...")
        
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        # settings.json
        settings_content = '''{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "git.inputValidationLength": 72,
    "git.inputValidationSubjectLength": 50
}'''
        
        settings_file = vscode_dir / "settings.json"
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                f.write(settings_content)
            print("✅ VSCode settings.json 已创建")
        except IOError as e:
            print(f"⚠️ 创建VSCode配置失败: {e}")
        
        # extensions.json
        extensions_content = '''{
    "recommendations": [
        "ms-python.python",
        "ms-python.flake8",
        "ms-python.mypy-type-checker",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-vscode.vscode-json",
        "redhat.vscode-yaml",
        "esbenp.prettier-vscode",
        "ms-vscode.vscode-eslint",
        "bradlc.vscode-tailwindcss"
    ]
}'''
        
        extensions_file = vscode_dir / "extensions.json"
        try:
            with open(extensions_file, 'w', encoding='utf-8') as f:
                f.write(extensions_content)
            print("✅ VSCode extensions.json 已创建")
        except IOError as e:
            print(f"⚠️ 创建VSCode扩展配置失败: {e}")
        
        return True
    
    def create_dev_scripts(self) -> bool:
        """
        创建开发脚本
        
        Returns:
            bool: 是否成功
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        print("📜 创建开发脚本...")
        
        scripts_dir = self.project_root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # 代码质量检查脚本
        quality_check_script = '''#!/bin/bash
# 代码质量检查脚本
# Author: AI Assistant (Claude)
# Date: 2025-06-25

echo "🔍 运行代码质量检查..."

echo "📝 检查代码格式..."
black --check src/ || exit 1

echo "🔍 检查代码风格..."
flake8 src/ || exit 1

echo "🔍 检查类型注解..."
mypy src/ || exit 1

echo "🔍 检查导入排序..."
isort --check-only src/ || exit 1

echo "🧪 运行测试..."
pytest --cov=src --cov-report=html || exit 1

echo "✅ 所有检查通过！"
'''
        
        quality_script_file = scripts_dir / "quality_check.sh"
        try:
            with open(quality_script_file, 'w', encoding='utf-8') as f:
                f.write(quality_check_script)
            quality_script_file.chmod(0o755)
            print("✅ 代码质量检查脚本已创建")
        except IOError as e:
            print(f"⚠️ 创建质量检查脚本失败: {e}")
        
        # 测试脚本
        test_script = '''#!/bin/bash
# 测试运行脚本
# Author: AI Assistant (Claude)
# Date: 2025-06-25

echo "🧪 运行测试套件..."

# 运行单元测试
echo "📝 运行单元测试..."
pytest tests/unit/ -v

# 运行集成测试
echo "🔗 运行集成测试..."
pytest tests/integration/ -v

# 运行端到端测试
echo "🌐 运行端到端测试..."
pytest tests/e2e/ -v

# 生成覆盖率报告
echo "📊 生成覆盖率报告..."
pytest --cov=src --cov-report=html --cov-report=term

echo "✅ 测试完成！"
'''
        
        test_script_file = scripts_dir / "run_tests.sh"
        try:
            with open(test_script_file, 'w', encoding='utf-8') as f:
                f.write(test_script)
            test_script_file.chmod(0o755)
            print("✅ 测试脚本已创建")
        except IOError as e:
            print(f"⚠️ 创建测试脚本失败: {e}")
        
        return True
    
    def run_initial_checks(self) -> bool:
        """
        运行初始检查
        
        Returns:
            bool: 是否成功
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        print("🔍 运行初始检查...")
        
        # 检查文件头注释
        header_checker = self.project_root / "tools" / "check_file_headers.py"
        if header_checker.exists():
            success = self.run_command(
                [sys.executable, str(header_checker), "src/"],
                "检查文件头注释"
            )
            if not success:
                print("⚠️ 文件头注释检查失败，请修复后重新运行")
        
        # 运行项目状态检查
        status_checker = self.project_root / "tools" / "project_status_checker.py"
        if status_checker.exists():
            success = self.run_command(
                [sys.executable, str(status_checker)],
                "运行项目状态检查"
            )
            if not success:
                print("⚠️ 项目状态检查失败")
        
        return True
    
    def setup(self) -> bool:
        """
        运行完整的环境设置
        
        Returns:
            bool: 是否成功
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        print("🚀 开始设置开发环境...")
        print(f"📁 项目路径: {self.project_root}")
        print("=" * 60)
        
        # 执行设置步骤
        steps = [
            ("检查Python版本", self.check_python_version),
            ("设置Git配置", self.setup_git_config),
            ("安装Python依赖", self.install_python_dependencies),
            ("设置Pre-commit hooks", self.setup_pre_commit),
            ("设置VSCode配置", self.setup_vscode_config),
            ("创建开发脚本", self.create_dev_scripts),
            ("运行初始检查", self.run_initial_checks)
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            print(f"\n📋 步骤: {step_name}")
            if step_func():
                success_count += 1
            else:
                print(f"❌ 步骤失败: {step_name}")
        
        # 生成设置报告
        print("\n" + "=" * 60)
        print("📊 设置完成报告")
        print("=" * 60)
        print(f"✅ 成功步骤: {success_count}/{len(steps)}")
        
        if self.errors:
            print(f"❌ 失败步骤: {len(self.errors)}")
            print("\n错误详情:")
            for error in self.errors:
                print(f"  - {error}")
        
        if success_count == len(steps):
            print("\n🎉 开发环境设置完成！")
            print("\n📝 下一步:")
            print("  1. 运行 'python tools/project_status_checker.py' 检查项目状态")
            print("  2. 运行 'scripts/quality_check.sh' 进行代码质量检查")
            print("  3. 运行 'scripts/run_tests.sh' 执行测试套件")
            print("  4. 开始开发工作！")
            return True
        else:
            print("\n⚠️ 部分设置步骤失败，请检查错误信息并手动修复")
            return False

def main():
    """
    主函数
    
    Author: AI Assistant (Claude)
    Date: 2025-06-25
    AI Assisted: 是
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="开发环境设置脚本")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    
    args = parser.parse_args()
    
    # 运行设置
    setup = DevEnvironmentSetup(args.project_root)
    success = setup.setup()
    
    # 退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
