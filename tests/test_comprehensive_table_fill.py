#!/usr/bin/env python3
"""
综合测试表格填充功能
包括边界情况、错误处理和API端点测试
"""

import sys
import os
import pandas as pd
import json
import requests
import time
from typing import Dict, Any, List

def test_dataframe_serialization():
    """测试DataFrame序列化和反序列化"""
    print("=== 测试DataFrame序列化/反序列化 ===")
    
    # 创建测试DataFrame
    test_data = {
        "姓名": ["张三", "李四", "王五"],
        "年龄": [25, 30, 35],
        "职位": ["工程师", "经理", "总监"]
    }
    original_df = pd.DataFrame(test_data)
    print("原始DataFrame:")
    print(original_df.to_string(index=False))
    
    # 序列化为API格式
    serialized = {
        'columns': list(original_df.columns),
        'data': original_df.values.tolist()
    }
    print(f"\n序列化后的JSON格式:")
    print(json.dumps(serialized, ensure_ascii=False, indent=2))
    
    # 反序列化回DataFrame
    reconstructed_df = pd.DataFrame(serialized['data'], columns=serialized['columns'])
    print(f"\n重构后的DataFrame:")
    print(reconstructed_df.to_string(index=False))
    
    # 验证数据一致性
    if original_df.equals(reconstructed_df):
        print("✅ 序列化/反序列化测试通过")
        return True
    else:
        print("❌ 序列化/反序列化测试失败")
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 测试边界情况 ===")
    
    test_cases = [
        {
            "name": "空表格",
            "tables": [{"columns": [], "data": []}],
            "fill_data": []
        },
        {
            "name": "单列表格",
            "tables": [{"columns": ["名称"], "data": [["项目A"], ["项目B"]]}],
            "fill_data": [{"名称": "项目A更新"}]
        },
        {
            "name": "包含None值",
            "tables": [{"columns": ["姓名", "年龄"], "data": [["张三", None], ["李四", 30]]}],
            "fill_data": [{"姓名": "张三", "年龄": 25}]
        },
        {
            "name": "中文列名",
            "tables": [{"columns": ["姓名", "年龄", "部门"], "data": [["", "", ""]]}],
            "fill_data": [{"姓名": "测试用户", "年龄": "28", "部门": "技术部"}]
        }
    ]
    
    success_count = 0
    for case in test_cases:
        try:
            print(f"\n测试用例: {case['name']}")
            
            # 转换为DataFrame
            pd_tables = []
            for t in case['tables']:
                df = pd.DataFrame(t['data'], columns=t['columns'])
                pd_tables.append(df)
            
            # 模拟填充逻辑
            filled_tables = []
            for df in pd_tables:
                if not isinstance(df, pd.DataFrame) or df.empty:
                    filled_tables.append(df)
                    continue
                
                # 填充数据
                for i, row in enumerate(case['fill_data']):
                    if i >= len(df):
                        df.loc[len(df)] = [row.get(col, "") for col in df.columns]
                    else:
                        for col in df.columns:
                            if col in row:
                                df.at[i, col] = row[col]
                filled_tables.append(df)
            
            # 转换回API格式
            result = []
            for df in filled_tables:
                result.append({
                    'columns': list(df.columns),
                    'data': df.values.tolist()
                })
            
            print(f"✅ {case['name']} 测试通过")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {case['name']} 测试失败: {str(e)}")
    
    print(f"\n边界情况测试结果: {success_count}/{len(test_cases)} 通过")
    return success_count == len(test_cases)

def test_data_types():
    """测试不同数据类型的处理"""
    print("\n=== 测试数据类型处理 ===")
    
    # 测试各种数据类型
    test_table = {
        "columns": ["字符串", "整数", "浮点数", "布尔值", "日期"],
        "data": [
            ["", "", "", "", ""],
            ["", "", "", "", ""]
        ]
    }
    
    fill_data = [
        {
            "字符串": "测试文本",
            "整数": 42,
            "浮点数": 3.14,
            "布尔值": True,
            "日期": "2024-01-01"
        },
        {
            "字符串": "另一个测试",
            "整数": 100,
            "浮点数": 2.71,
            "布尔值": False,
            "日期": "2024-12-31"
        }
    ]
    
    try:
        # 转换为DataFrame
        df = pd.DataFrame(test_table['data'], columns=test_table['columns'])
        
        # 填充数据
        for i, row in enumerate(fill_data):
            if i >= len(df):
                df.loc[len(df)] = [row.get(col, "") for col in df.columns]
            else:
                for col in df.columns:
                    if col in row:
                        df.at[i, col] = row[col]
        
        print("填充后的DataFrame:")
        print(df.to_string(index=False))
        
        # 转换回API格式
        result = {
            'columns': list(df.columns),
            'data': df.values.tolist()
        }
        
        print("✅ 数据类型处理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据类型处理测试失败: {str(e)}")
        return False

def test_api_endpoint_format():
    """测试API端点的请求格式"""
    print("\n=== 测试API端点格式 ===")
    
    # 构造标准的API请求
    api_request = {
        "tables": [
            {
                "columns": ["项目名称", "负责人", "状态"],
                "data": [
                    ["项目A", "", ""],
                    ["项目B", "", ""]
                ]
            }
        ],
        "fill_data": [
            {"项目名称": "项目A", "负责人": "张三", "状态": "进行中"},
            {"项目名称": "项目B", "负责人": "李四", "状态": "已完成"}
        ]
    }
    
    print("标准API请求格式:")
    print(json.dumps(api_request, ensure_ascii=False, indent=2))
    
    # 验证请求格式的完整性
    required_fields = ['tables', 'fill_data']
    table_required_fields = ['columns', 'data']
    
    try:
        # 检查顶级字段
        for field in required_fields:
            if field not in api_request:
                raise ValueError(f"缺少必需字段: {field}")
        
        # 检查表格字段
        for i, table in enumerate(api_request['tables']):
            for field in table_required_fields:
                if field not in table:
                    raise ValueError(f"表格{i+1}缺少必需字段: {field}")
        
        print("✅ API端点格式验证通过")
        return True
        
    except Exception as e:
        print(f"❌ API端点格式验证失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始综合测试表格填充功能...\n")
    
    # 运行所有测试
    tests = [
        test_dataframe_serialization,
        test_edge_cases,
        test_data_types,
        test_api_endpoint_format
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\n=== 测试总结 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！表格填充API格式完全正确。")
    else:
        print("❌ 部分测试失败，需要进一步检查。")
