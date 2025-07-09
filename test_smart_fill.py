#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能填报模块测试脚本

Author: AI Assistant (Claude)
Created: 2025-07-08
Last Modified: 2025-07-08
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

import sys
import os
import requests
import json
import time

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_smart_fill_api():
    """测试智能填报API"""
    base_url = "http://localhost:5000"
    
    print("=== 智能填报模块测试 ===")
    
    # 1. 测试状态检查
    print("\n1. 测试状态检查...")
    try:
        response = requests.get(f"{base_url}/api/smart-fill/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 状态检查成功")
            print(f"   星火X1可用: {data['data']['spark_x1_available']}")
            print(f"   支持功能: {data['data']['supported_functions']}")
            if 'api_connection' in data['data']:
                print(f"   API连接: {data['data']['api_connection']}")
        else:
            print(f"❌ 状态检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 状态检查异常: {e}")
        return False
    
    # 2. 测试年度总结生成
    print("\n2. 测试年度总结生成...")
    summary_content = """
今年我主要负责了公司核心产品的技术升级工作，成功完成了从单体架构到微服务架构的转型。
在项目管理方面，我带领5人团队完成了3个重要项目，项目按时交付率达到100%。
技术方面，我深入学习了云原生技术，包括Docker、Kubernetes等。
遇到的主要挑战是系统迁移过程中的数据一致性问题，通过设计分布式事务方案得到解决。
明年计划继续深化在AI和大数据方向的技术能力。
"""
    
    try:
        payload = {
            "content": summary_content.strip(),
            "api_password": "NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh"
        }
        
        print("   正在调用星火X1生成年度总结...")
        response = requests.post(
            f"{base_url}/api/smart-fill/generate-summary", 
            json=payload, 
            timeout=180
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ 年度总结生成成功")
                print(f"   文件名: {data['data']['filename']}")
                print(f"   内容长度: {len(data['data']['content'])} 字符")
                if 'usage' in data['data']:
                    usage = data['data']['usage']
                    print(f"   Token使用: {usage.get('total_tokens', 'N/A')}")
                
                # 测试文件下载
                filename = data['data']['filename']
                print(f"\n   测试文件下载: {filename}")
                download_response = requests.get(f"{base_url}/api/smart-fill/download/{filename}")
                if download_response.status_code == 200:
                    print("✅ 文件下载成功")
                    print(f"   文件大小: {len(download_response.content)} 字节")
                else:
                    print(f"❌ 文件下载失败: {download_response.status_code}")
            else:
                print(f"❌ 年度总结生成失败: {data['error']}")
        else:
            print(f"❌ 年度总结API调用失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 年度总结测试异常: {e}")
    
    # 3. 测试简历生成
    print("\n3. 测试简历生成...")
    resume_content = """
张三，联系电话：138xxxx8888，邮箱：zhangsan@email.com

教育背景：
2018-2022年就读于北京大学计算机科学与技术专业，获得学士学位

工作经验：
2022年7月至今在腾讯科技有限公司担任软件工程师
主要负责微信支付系统的后端开发和维护
使用Java、Spring Boot、MySQL、Redis等技术栈

项目经验：
支付风控系统（2023.3-2023.8）
担任核心开发工程师，负责实时风险识别模块
技术栈：Java、Kafka、Elasticsearch
实现毫秒级风险评估，降低欺诈交易率30%

专业技能：
编程语言：Java、Python、JavaScript
框架：Spring Boot、Django、React
数据库：MySQL、Redis、MongoDB
工具：Git、Docker、Jenkins
"""
    
    try:
        payload = {
            "content": resume_content.strip(),
            "api_password": "NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh"
        }
        
        print("   正在调用星火X1生成简历...")
        response = requests.post(
            f"{base_url}/api/smart-fill/generate-resume", 
            json=payload, 
            timeout=180
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ 简历生成成功")
                print(f"   文件名: {data['data']['filename']}")
                resume_data = data['data']['resume_data']
                print(f"   姓名: {resume_data.get('姓名', 'N/A')}")
                print(f"   电话: {resume_data.get('电话', 'N/A')}")
                print(f"   邮箱: {resume_data.get('邮箱', 'N/A')}")
                if 'usage' in data['data']:
                    usage = data['data']['usage']
                    print(f"   Token使用: {usage.get('total_tokens', 'N/A')}")
                
                # 测试文件下载
                filename = data['data']['filename']
                print(f"\n   测试文件下载: {filename}")
                download_response = requests.get(f"{base_url}/api/smart-fill/download/{filename}")
                if download_response.status_code == 200:
                    print("✅ 文件下载成功")
                    print(f"   文件大小: {len(download_response.content)} 字节")
                else:
                    print(f"❌ 文件下载失败: {download_response.status_code}")
            else:
                print(f"❌ 简历生成失败: {data['error']}")
        else:
            print(f"❌ 简历API调用失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 简历测试异常: {e}")
    
    print("\n=== 测试完成 ===")
    return True

def test_direct_client():
    """直接测试星火X1客户端"""
    print("\n=== 直接测试星火X1客户端 ===")
    
    try:
        from llm_clients.spark_x1_client import SparkX1Client
        
        # 创建客户端
        client = SparkX1Client(api_password="NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh")
        print("✅ 星火X1客户端创建成功")
        
        # 测试健康检查
        print("   测试API连接...")
        is_available = client.is_available()
        print(f"   API可用性: {is_available}")
        
        if is_available:
            # 测试简单生成
            print("   测试简单文本生成...")
            test_content = "我今年完成了重要的技术项目，学习了新技术。"
            result = client.generate_summary(test_content)
            
            if result['success']:
                print("✅ 文本生成测试成功")
                print(f"   生成内容长度: {len(result['content'])} 字符")
                print(f"   文件: {result['filename']}")
            else:
                print(f"❌ 文本生成失败: {result['error']}")
        
    except ImportError as e:
        print(f"❌ 导入星火X1客户端失败: {e}")
    except Exception as e:
        print(f"❌ 直接测试异常: {e}")

if __name__ == '__main__':
    print("智能填报模块测试工具")
    print("=" * 50)
    
    # 检查服务器是否运行
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Web服务器正在运行")
            
            # 运行API测试
            test_smart_fill_api()
        else:
            print("❌ Web服务器未响应，尝试直接测试客户端")
            test_direct_client()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Web服务器，尝试直接测试客户端")
        test_direct_client()
    except Exception as e:
        print(f"❌ 测试异常: {e}")
    
    print("\n使用说明:")
    print("1. 启动Web服务器: python run_app.py")
    print("2. 年度总结API: POST /api/smart-fill/generate-summary")
    print("3. 简历生成API: POST /api/smart-fill/generate-resume")
    print("4. 文件下载API: GET /api/smart-fill/download/<filename>")
    print("5. 状态检查API: GET /api/smart-fill/status")
