#!/usr/bin/env python3
"""
测试Web应用修复的功能
Test script for Web App Bug Fixes
"""

import requests
import json
import os
import sys
import time
from io import BytesIO

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_endpoints():
    """测试API端点"""
    
    base_url = "http://localhost:5000"
    
    print("🚀 测试Web应用API端点")
    print("=" * 50)
    
    # 测试健康检查
    print("📊 测试健康检查端点...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查成功: {data['status']}")
            print(f"   API状态: {data.get('api_status', {})}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    print()
    
    # 测试配置端点
    print("⚙️ 测试配置端点...")
    try:
        response = requests.get(f"{base_url}/api/config", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 配置获取成功")
            print(f"   支持的API类型: {data.get('api_types', [])}")
            print(f"   支持的文件格式: {data.get('allowed_extensions', [])}")
            print(f"   模拟模式可用: {data.get('mock_mode_available', False)}")
        else:
            print(f"❌ 配置获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 配置获取异常: {e}")
    
    print()
    
    # 测试模型端点
    print("🤖 测试模型端点...")
    try:
        response = requests.get(f"{base_url}/api/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 模型获取成功")
            models = data.get('models', {})
            for api_type, model_list in models.items():
                print(f"   {api_type}: {model_list}")
        else:
            print(f"❌ 模型获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 模型获取异常: {e}")

def test_file_upload():
    """测试文件上传功能"""
    
    base_url = "http://localhost:5000"
    
    print(f"\n📤 测试文件上传功能")
    print("=" * 50)
    
    # 创建测试文件
    test_content = """# 测试文档

这是一个用于测试Web应用修复的示例文档。

## 内容概述
本文档包含以下内容：
1. 项目背景
2. 技术方案
3. 实施计划

## 项目背景
我们正在开发一个智能文档处理系统，旨在提高办公效率。

## 技术方案
系统采用AI技术进行文档分析和处理。

## 实施计划
分三个阶段实施：
- 第一阶段：基础功能开发
- 第二阶段：AI功能集成
- 第三阶段：系统优化和部署

这是一个完整的测试文档。
"""
    
    # 测试不同的API类型
    api_types = ['mock', 'xingcheng', 'multi']
    
    for api_type in api_types:
        print(f"\n🔧 测试API类型: {api_type}")
        print("-" * 30)
        
        try:
            # 准备文件数据
            files = {
                'file': ('test_document.txt', BytesIO(test_content.encode('utf-8')), 'text/plain')
            }
            
            data = {
                'api_type': api_type,
                'model_name': ''  # 自动选择
            }
            
            # 发送上传请求
            response = requests.post(
                f"{base_url}/api/upload",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 上传处理成功")
                    print(f"   文件名: {result.get('filename', 'unknown')}")
                    print(f"   API类型: {result.get('api_type', 'unknown')}")
                    print(f"   处理时间: {result.get('processed_at', 'unknown')}")
                    
                    # 检查处理结果
                    processing_result = result.get('result', {})
                    if processing_result:
                        print(f"   文档类型: {processing_result.get('scenario_analysis', {}).get('document_type', 'unknown')}")
                        print(f"   字符数: {processing_result.get('structure_info', {}).get('characters', 0)}")
                        print(f"   模拟模式: {processing_result.get('mock_mode', False)}")
                        
                        if processing_result.get('error'):
                            print(f"   ⚠️ 处理错误: {processing_result['error']}")
                    
                    if result.get('note'):
                        print(f"   📝 备注: {result['note']}")
                        
                else:
                    print(f"❌ 处理失败: {result.get('error', 'unknown error')}")
            else:
                print(f"❌ 上传失败: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   错误信息: {error_data.get('error', 'unknown error')}")
                except:
                    print(f"   响应内容: {response.text[:200]}...")
                    
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时")
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接错误 - 请确保Web服务器正在运行")
        except Exception as e:
            print(f"❌ 上传异常: {e}")

def test_error_scenarios():
    """测试错误场景"""
    
    base_url = "http://localhost:5000"
    
    print(f"\n🚨 测试错误场景")
    print("=" * 50)
    
    # 测试无文件上传
    print("📤 测试无文件上传...")
    try:
        response = requests.post(f"{base_url}/api/upload", data={'api_type': 'mock'}, timeout=10)
        if response.status_code == 400:
            print("✅ 正确处理无文件错误")
        else:
            print(f"❌ 未正确处理无文件错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试异常: {e}")
    
    # 测试不支持的文件类型
    print("\n📤 测试不支持的文件类型...")
    try:
        files = {
            'file': ('test.exe', BytesIO(b'fake executable'), 'application/octet-stream')
        }
        data = {'api_type': 'mock'}
        
        response = requests.post(f"{base_url}/api/upload", files=files, data=data, timeout=10)
        if response.status_code == 400:
            print("✅ 正确处理不支持文件类型错误")
        else:
            print(f"❌ 未正确处理文件类型错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def main():
    """主测试函数"""
    
    print("🔧 Web应用修复测试")
    print("=" * 60)
    print("请确保Web服务器正在运行 (python src/web_app.py)")
    print("=" * 60)
    
    # 等待用户确认
    input("按Enter键开始测试...")
    
    # 执行测试
    test_api_endpoints()
    test_file_upload()
    test_error_scenarios()
    
    print(f"\n🎉 测试完成!")
    print("如果所有测试都通过，说明Web应用修复成功。")

if __name__ == "__main__":
    main()
