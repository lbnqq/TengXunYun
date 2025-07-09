#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简化后的智能填报模块

Author: AI Assistant (Claude)
Created: 2025-07-08
"""

import sys
import os
import requests
import json
import time

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simplified_smart_fill():
    """测试简化后的智能填报模块"""
    base_url = "http://localhost:5000"
    
    print("=== 测试简化后的智能填报模块 ===")
    
    # 1. 测试系统状态
    print("\n1. 测试系统状态...")
    try:
        response = requests.get(f"{base_url}/api/smart-fill/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 系统状态API调用成功")
            status = data['data']
            print(f"   星火X1可用: {status.get('spark_x1_available', False)}")
            print(f"   核心组件可用: {status.get('core_components_available', False)}")
            print(f"   支持类型: {status.get('supported_types', [])}")
            
            # 验证只支持年度总结和简历
            supported_types = status.get('supported_types', [])
            if set(supported_types) == {'summary', 'resume'}:
                print("✅ 支持类型正确：仅包含年度总结和简历")
            else:
                print(f"⚠️  支持类型异常：{supported_types}")
        else:
            print(f"❌ 系统状态检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 系统状态检查异常: {e}")
        return False
    
    # 2. 测试年度总结生成
    print("\n2. 测试年度总结生成...")
    try:
        payload = {
            "content": "今年我主要负责了AI项目开发，完成了智能填报模块的优化工作。",
            "api_password": "NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh"
        }
        
        response = requests.post(
            f"{base_url}/api/smart-fill/generate-summary", 
            json=payload, 
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ 年度总结生成成功")
                filename = data.get('filename')
                print(f"   文件名: {filename}")
                
                if filename:
                    # 测试文件下载
                    print("   测试文件下载...")
                    download_response = requests.get(
                        f"{base_url}/api/smart-fill/download/{filename}",
                        timeout=30
                    )
                    
                    if download_response.status_code == 200:
                        print(f"✅ 年度总结下载成功 ({len(download_response.content)} 字节)")
                    else:
                        print(f"❌ 年度总结下载失败: {download_response.status_code}")
                else:
                    print("⚠️  生成成功但没有返回文件名")
            else:
                print(f"❌ 年度总结生成失败: {data['error']}")
        else:
            print(f"❌ 年度总结生成API调用失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 年度总结生成测试异常: {e}")
    
    # 3. 测试简历生成
    print("\n3. 测试简历生成...")
    try:
        payload = {
            "content": "李四，电话139xxxx9999，邮箱lisi@email.com，清华大学软件工程专业毕业，有3年开发经验。",
            "api_password": "NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh"
        }
        
        response = requests.post(
            f"{base_url}/api/smart-fill/generate-resume", 
            json=payload, 
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ 简历生成成功")
                filename = data.get('filename')
                print(f"   文件名: {filename}")
                
                if filename:
                    # 测试文件下载
                    print("   测试文件下载...")
                    download_response = requests.get(
                        f"{base_url}/api/smart-fill/download/{filename}",
                        timeout=30
                    )
                    
                    if download_response.status_code == 200:
                        print(f"✅ 简历下载成功 ({len(download_response.content)} 字节)")
                    else:
                        print(f"❌ 简历下载失败: {download_response.status_code}")
                else:
                    print("⚠️  生成成功但没有返回文件名")
            else:
                print(f"❌ 简历生成失败: {data['error']}")
        else:
            print(f"❌ 简历生成API调用失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 简历生成测试异常: {e}")
    
    print("\n=== 简化测试完成 ===")
    return True

def test_direct_manager():
    """直接测试简化管理器"""
    print("\n=== 直接测试简化管理器 ===")
    
    try:
        from core.tools.simple_smart_fill_manager import SimpleSmartFillManager
        
        # 创建管理器
        config = {
            'spark_x1_api_password': 'NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh'
        }
        manager = SimpleSmartFillManager(config)
        print("✅ 简化智能填报管理器创建成功")
        
        # 测试状态
        status = manager.get_status()
        print(f"   星火X1可用: {status.get('spark_x1_available', False)}")
        print(f"   核心组件可用: {status.get('core_components_available', False)}")
        print(f"   支持类型: {status.get('supported_types', [])}")
        
        # 验证支持类型
        supported_types = status.get('supported_types', [])
        if set(supported_types) == {'summary', 'resume'}:
            print("✅ 支持类型正确：仅包含年度总结和简历")
        else:
            print(f"⚠️  支持类型异常：{supported_types}")
        
        # 测试年度总结生成
        if status.get('spark_x1_available', False):
            print("   测试年度总结生成...")
            result = manager.intelligent_fill_document(
                'summary', 
                '今年完成了智能填报模块的简化工作。'
            )
            
            if result['success']:
                print("   ✅ 年度总结生成成功")
                print(f"   处理方式: {result.get('handler', 'N/A')}")
                print(f"   文件: {result.get('filename', 'N/A')}")
            else:
                print(f"   ❌ 年度总结生成失败: {result['error']}")
        
    except ImportError as e:
        print(f"❌ 导入简化管理器失败: {e}")
    except Exception as e:
        print(f"❌ 直接测试异常: {e}")

if __name__ == '__main__':
    print("智能填报模块简化测试工具")
    print("=" * 50)
    
    # 检查服务器是否运行
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Web服务器正在运行")
            
            # 运行简化测试
            test_simplified_smart_fill()
        else:
            print("❌ Web服务器未响应，尝试直接测试管理器")
            test_direct_manager()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Web服务器，尝试直接测试管理器")
        test_direct_manager()
    except Exception as e:
        print(f"❌ 测试异常: {e}")
    
    print("\n简化说明:")
    print("✅ 已删除通用智能填报模块")
    print("✅ 仅保留年度总结生成功能")
    print("✅ 仅保留简历生成功能")
    print("✅ 界面更加简洁专注")
    print("✅ 后端逻辑更加清晰")
