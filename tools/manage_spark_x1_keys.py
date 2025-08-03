#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星火X1密钥管理工具

提供命令行界面来管理星火X1 API密钥，包括查看、更新、测试等功能。

使用方法:
    python tools/manage_spark_x1_keys.py --help
    python tools/manage_spark_x1_keys.py --list
    python tools/manage_spark_x1_keys.py --update "新密钥"
    python tools/manage_spark_x1_keys.py --test

Author: AI Assistant
Created: 2025-08-03
License: MIT
"""

import sys
import os
import argparse
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='星火X1密钥管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  查看当前密钥信息:
    python tools/manage_spark_x1_keys.py --list
    
  更新主密钥:
    python tools/manage_spark_x1_keys.py --update "AK:SK"
    
  测试密钥有效性:
    python tools/manage_spark_x1_keys.py --test
    
  查看配置文件路径:
    python tools/manage_spark_x1_keys.py --config-path
        """
    )
    
    parser.add_argument('--list', '-l', action='store_true',
                       help='列出所有配置的密钥信息')
    
    parser.add_argument('--update', '-u', type=str, metavar='KEY',
                       help='更新主密钥 (格式: AK:SK)')
    
    parser.add_argument('--test', '-t', action='store_true',
                       help='测试当前主密钥是否有效')
    
    parser.add_argument('--config-path', '-p', action='store_true',
                       help='显示配置文件路径')
    
    parser.add_argument('--module', '-m', type=str,
                       help='指定模块名称 (smart_fill, style_alignment, format_alignment, document_review)')
    
    args = parser.parse_args()
    
    # 如果没有提供任何参数，显示帮助
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    try:
        # 导入密钥管理器
        from src.core.config.spark_x1_key_manager import key_manager
        
        if args.config_path:
            show_config_path(key_manager)
        
        if args.list:
            list_keys(key_manager)
        
        if args.update:
            update_key(key_manager, args.update)
        
        if args.test:
            test_key(key_manager, args.module)
            
    except ImportError as e:
        print(f"❌ 导入密钥管理器失败: {e}")
        print("请确保项目依赖已正确安装")
    except Exception as e:
        print(f"❌ 执行失败: {e}")

def show_config_path(key_manager):
    """显示配置文件路径"""
    print("📁 配置文件信息:")
    print(f"   路径: {key_manager.config_path}")
    print(f"   存在: {'是' if os.path.exists(key_manager.config_path or '') else '否'}")
    print()

def list_keys(key_manager):
    """列出所有密钥信息"""
    print("🔑 当前密钥配置:")
    print("=" * 50)
    
    try:
        keys_info = key_manager.list_all_keys()
        
        # 显示主密钥
        if 'primary' in keys_info:
            primary = keys_info['primary']
            print(f"📌 主密钥:")
            print(f"   密钥: {primary['key']}")
            print(f"   描述: {primary['description']}")
            print(f"   状态: {primary['status']}")
            print()
        
        # 显示备用密钥
        if 'backup' in keys_info and keys_info['backup']:
            print(f"🔄 备用密钥:")
            for key_name, key_info in keys_info['backup'].items():
                print(f"   {key_name}:")
                print(f"     密钥: {key_info['key']}")
                print(f"     描述: {key_info['description']}")
                print(f"     状态: {key_info['status']}")
            print()
        
        # 显示模块配置
        print(f"📋 模块配置:")
        modules = key_manager.config.get('modules', {})
        for module_name, module_config in modules.items():
            use_key = module_config.get('use_key', 'primary')
            print(f"   {module_name}: 使用 {use_key}")
        
    except Exception as e:
        print(f"❌ 获取密钥信息失败: {e}")

def update_key(key_manager, new_key):
    """更新主密钥"""
    print(f"🔄 更新主密钥...")
    
    # 验证密钥格式
    if ':' not in new_key:
        print("❌ 密钥格式错误，应为 AK:SK 格式")
        return
    
    try:
        success = key_manager.update_primary_key(new_key, "通过管理工具更新")
        
        if success:
            print("✅ 主密钥更新成功")
            print(f"   新密钥: {new_key[:20]}...")
        else:
            print("❌ 主密钥更新失败")
            
    except Exception as e:
        print(f"❌ 更新密钥失败: {e}")

def test_key(key_manager, module_name=None):
    """测试密钥有效性"""
    print(f"🧪 测试密钥有效性...")
    
    try:
        if module_name:
            print(f"   模块: {module_name}")
            key = key_manager.get_api_key(module_name)
        else:
            print("   使用主密钥")
            key = key_manager.get_api_key()
        
        print(f"   密钥: {key[:20]}...")
        
        # 测试密钥
        is_valid = key_manager.test_key(key)
        
        if is_valid:
            print("✅ 密钥格式验证通过")
            print("ℹ️  注意: 这只是格式验证，实际API调用可能需要额外测试")
        else:
            print("❌ 密钥验证失败")
            
    except Exception as e:
        print(f"❌ 测试密钥失败: {e}")

if __name__ == "__main__":
    main()
