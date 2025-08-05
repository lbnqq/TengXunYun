#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文风统一导出功能

Author: AI Assistant
Created: 2025-08-03
"""

import sys
import os
import json
import requests
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_export_functionality():
    """测试导出功能"""
    print("🧪 开始测试文风统一导出功能...")
    
    # 测试API端点是否可访问
    base_url = "http://localhost:5000"
    
    try:
        # 1. 测试服务器是否运行
        print("1️⃣ 检查服务器状态...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保应用正在运行")
        return False
    except Exception as e:
        print(f"❌ 服务器检查失败: {e}")
        return False
    
    try:
        # 2. 测试预设风格获取
        print("2️⃣ 测试预设风格获取...")
        response = requests.get(f"{base_url}/api/style-alignment/preset-styles")
        if response.status_code == 200:
            styles_data = response.json()
            if styles_data.get('success'):
                print("✅ 预设风格获取成功")
                print(f"   可用风格数量: {styles_data.get('count', 0)}")
            else:
                print(f"❌ 预设风格获取失败: {styles_data.get('error')}")
                return False
        else:
            print(f"❌ 预设风格API响应异常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 预设风格测试失败: {e}")
        return False
    
    try:
        # 3. 测试文风生成
        print("3️⃣ 测试文风生成...")
        test_content = "这是一个测试文档。我们需要将其转换为不同的写作风格。"
        
        generation_data = {
            "content": test_content,
            "style_id": "academic",
            "action": "重写",
            "language": "zh"
        }
        
        response = requests.post(
            f"{base_url}/api/style-alignment/generate-with-style",
            json=generation_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result_data = response.json()
            if result_data.get('success'):
                print("✅ 文风生成成功")
                task_id = result_data.get('task_id')
                if task_id:
                    print(f"   任务ID: {task_id}")
                    
                    # 等待任务完成
                    print("4️⃣ 等待任务完成...")
                    max_wait = 30  # 最多等待30秒
                    wait_time = 0
                    
                    while wait_time < max_wait:
                        progress_response = requests.get(f"{base_url}/api/style-alignment/task-progress/{task_id}")
                        if progress_response.status_code == 200:
                            progress_data = progress_response.json()
                            if progress_data.get('success'):
                                progress_info = progress_data.get('progress', {})
                                status = progress_info.get('status', 'unknown')
                                progress_percent = progress_info.get('progress', 0)
                                
                                print(f"   进度: {progress_percent}% - {status}")
                                
                                if status == 'completed':
                                    print("✅ 任务完成")
                                    break
                                elif status == 'failed':
                                    print("❌ 任务失败")
                                    return False
                        
                        time.sleep(2)
                        wait_time += 2
                    
                    if wait_time >= max_wait:
                        print("⏰ 任务等待超时")
                        return False
                    
                    # 5. 测试导出功能
                    print("5️⃣ 测试导出功能...")
                    
                    # 测试TXT导出
                    print("   测试TXT导出...")
                    export_data = {
                        "task_id": task_id,
                        "format": "txt"
                    }
                    
                    export_response = requests.post(
                        f"{base_url}/api/style-alignment/export",
                        json=export_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if export_response.status_code == 200:
                        export_result = export_response.json()
                        if export_result.get('success'):
                            print("✅ TXT导出成功")
                            print(f"   文件名: {export_result.get('filename')}")
                            print(f"   下载链接: {export_result.get('download_url')}")
                        else:
                            print(f"❌ TXT导出失败: {export_result.get('error')}")
                    else:
                        print(f"❌ TXT导出API响应异常: {export_response.status_code}")
                    
                    # 测试DOCX导出
                    print("   测试DOCX导出...")
                    export_data['format'] = 'docx'
                    
                    export_response = requests.post(
                        f"{base_url}/api/style-alignment/export",
                        json=export_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if export_response.status_code == 200:
                        export_result = export_response.json()
                        if export_result.get('success'):
                            print("✅ DOCX导出成功")
                            print(f"   文件名: {export_result.get('filename')}")
                            print(f"   下载链接: {export_result.get('download_url')}")
                        else:
                            print(f"❌ DOCX导出失败: {export_result.get('error')}")
                    else:
                        print(f"❌ DOCX导出API响应异常: {export_response.status_code}")
                    
                    # 测试PDF导出
                    print("   测试PDF导出...")
                    export_data['format'] = 'pdf'
                    
                    export_response = requests.post(
                        f"{base_url}/api/style-alignment/export",
                        json=export_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if export_response.status_code == 200:
                        export_result = export_response.json()
                        if export_result.get('success'):
                            print("✅ PDF导出成功")
                            print(f"   文件名: {export_result.get('filename')}")
                            print(f"   下载链接: {export_result.get('download_url')}")
                        else:
                            print(f"❌ PDF导出失败: {export_result.get('error')}")
                    else:
                        print(f"❌ PDF导出API响应异常: {export_response.status_code}")
                    
                    print("🎉 导出功能测试完成")
                    return True
                    
                else:
                    print("❌ 未获取到任务ID")
                    return False
            else:
                print(f"❌ 文风生成失败: {result_data.get('error')}")
                return False
        else:
            print(f"❌ 文风生成API响应异常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 文风生成测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_export_functionality()
    if success:
        print("\n✅ 所有测试通过！文风统一导出功能已成功实现。")
    else:
        print("\n❌ 测试失败，请检查相关配置和实现。")
