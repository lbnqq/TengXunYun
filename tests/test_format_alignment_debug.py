#!/usr/bin/env python3
"""
格式对齐功能调试测试脚本
"""

import requests
import json
import sys
import os

def test_format_alignment_api():
    """测试格式对齐API"""
    base_url = "http://localhost:5000"
    
    print("🔍 格式对齐功能调试测试")
    print("=" * 50)
    
    # 测试数据
    test_source_content = """
一、项目概述
本项目旨在开发一个智能文档处理系统。

二、技术方案
1. 使用Python开发后端
2. 使用JavaScript开发前端
3. 集成AI技术

三、实施计划
第一阶段：需求分析
第二阶段：系统设计
第三阶段：开发实施
"""

    test_target_content = """
# 项目报告

## 1. 背景介绍
这是一个重要的技术项目。

## 2. 解决方案
- 采用现代化技术栈
- 确保系统稳定性
- 提供良好用户体验

## 3. 时间安排
- 第一周：准备工作
- 第二周：核心开发
- 第三周：测试优化
"""

    test_instruction = "让源文档的格式与目标文档对齐"
    
    # 第一步：测试API连通性
    print("1️⃣ 测试API连通性...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API服务正常")
        else:
            print(f"❌ API服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接API服务: {e}")
        return False
    
    # 第二步：测试格式模板列表
    print("\n2️⃣ 测试格式模板列表...")
    try:
        response = requests.get(f"{base_url}/api/format-templates", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 模板列表获取成功，共 {data.get('count', 0)} 个模板")
            if data.get('templates'):
                for template in data['templates'][:3]:  # 显示前3个
                    print(f"   - {template.get('name', 'Unknown')}: {template.get('description', 'No description')}")
        else:
            print(f"❌ 模板列表获取失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 模板列表请求异常: {e}")
    
    # 第三步：测试格式对齐请求
    print("\n3️⃣ 测试格式对齐请求...")
    try:
        payload = {
            "user_input": test_instruction,
            "uploaded_files": {
                "source.txt": test_source_content,
                "target.txt": test_target_content
            }
        }
        
        print(f"   发送请求数据:")
        print(f"   - 指令: {test_instruction}")
        print(f"   - 源文档长度: {len(test_source_content)} 字符")
        print(f"   - 目标文档长度: {len(test_target_content)} 字符")
        
        response = requests.post(
            f"{base_url}/api/format-alignment",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 格式对齐请求成功")
            
            # 检查响应结构
            if 'success' in data:
                if data.get('success'):
                    print("   ✅ 处理成功")
                    print(f"   - 源文档: {data.get('source_document', 'Unknown')}")
                    print(f"   - 目标文档: {data.get('target_document', 'Unknown')}")
                    print(f"   - 模板ID: {data.get('template_id', 'Unknown')}")
                    if data.get('format_prompt'):
                        print(f"   - 格式提示词长度: {len(data['format_prompt'])} 字符")
                    if data.get('html_output'):
                        print(f"   - HTML输出长度: {len(data['html_output'])} 字符")
                else:
                    print("   ❌ 处理失败")
                    print(f"   错误信息: {data.get('error', 'Unknown error')}")
            else:
                print("   ⚠️ 响应格式异常")
                print(f"   响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
                
        else:
            print(f"❌ 格式对齐请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误信息: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   响应内容: {response.text}")
                
    except Exception as e:
        print(f"❌ 格式对齐请求异常: {e}")
        import traceback
        print(f"   详细错误: {traceback.format_exc()}")
    
    # 第四步：测试核心组件
    print("\n4️⃣ 测试核心组件...")
    try:
        # 测试FormatAlignmentCoordinator
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.core.tools.format_alignment_coordinator import FormatAlignmentCoordinator
        
        coordinator = FormatAlignmentCoordinator()
        print("✅ FormatAlignmentCoordinator 初始化成功")
        
        # 测试意图分析
        intent = coordinator._analyze_user_intent(test_instruction)
        print(f"   意图分析结果: {intent['intent']} (置信度: {intent['confidence']})")
        
        # 测试文档引用提取
        if intent['entities'].get('documents'):
            docs = intent['entities']['documents']
            print(f"   文档引用: 源={docs.get('source')}, 目标={docs.get('target')}")
        
    except Exception as e:
        print(f"❌ 核心组件测试失败: {e}")
        import traceback
        print(f"   详细错误: {traceback.format_exc()}")
    
    # 第五步：测试DocumentFormatExtractor
    print("\n5️⃣ 测试DocumentFormatExtractor...")
    try:
        from src.core.tools.document_format_extractor import DocumentFormatExtractor
        
        extractor = DocumentFormatExtractor()
        print("✅ DocumentFormatExtractor 初始化成功")
        
        # 测试格式提取
        format_result = extractor.extract_format_from_document(test_target_content, "test_target.txt")
        
        if 'error' in format_result:
            print(f"❌ 格式提取失败: {format_result['error']}")
        else:
            print("✅ 格式提取成功")
            print(f"   模板ID: {format_result.get('template_id')}")
            print(f"   标题数量: {len(format_result.get('structure_analysis', {}).get('headings', []))}")
            print(f"   段落数量: {len(format_result.get('structure_analysis', {}).get('paragraphs', []))}")
            
            # 测试格式提示词生成
            if format_result.get('format_prompt'):
                print(f"   格式提示词: {format_result['format_prompt'][:100]}...")
        
    except Exception as e:
        print(f"❌ DocumentFormatExtractor 测试失败: {e}")
        import traceback
        print(f"   详细错误: {traceback.format_exc()}")
    
    print("\n" + "=" * 50)
    print("🔍 调试测试完成")
    
    return True

if __name__ == "__main__":
    test_format_alignment_api()
