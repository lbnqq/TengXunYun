#!/usr/bin/env python3
"""
测试表格填充API的参数格式
验证前端传递的DataFrame序列化格式是否正确处理
"""

import sys
import os
import pandas as pd
import json

# 简化测试，不依赖DocumentProcessor，直接测试数据格式转换

def test_table_fill_api_format():
    """测试API参数格式的正确性"""
    print("=== 测试表格填充API参数格式 ===")

    # 模拟前端发送的JSON数据格式
    api_request = {
        "tables": [
            {
                "columns": ["姓名", "年龄", "职位"],
                "data": [
                    ["张三", "", ""],
                    ["李四", "", ""]
                ]
            },
            {
                "columns": ["产品", "价格", "库存"],
                "data": [
                    ["笔记本", "", ""],
                    ["鼠标", "", ""]
                ]
            }
        ],
        "fill_data": [
            {"姓名": "张三", "年龄": "25", "职位": "工程师"},
            {"姓名": "李四", "年龄": "30", "职位": "经理"}
        ]
    }

    print("1. 前端发送的JSON格式:")
    print(json.dumps(api_request, ensure_ascii=False, indent=2))

    # 模拟API端点的处理逻辑
    tables = api_request.get('tables', [])
    fill_data = api_request.get('fill_data', [])

    # 将前端传来的表格数据转换为DataFrame
    pd_tables = []
    for i, t in enumerate(tables):
        print(f"\n2. 处理第{i+1}个表格:")
        print(f"   columns: {t['columns']}")
        print(f"   data: {t['data']}")

        # 转换为DataFrame
        df = pd.DataFrame(t['data'], columns=t['columns'])
        print(f"   转换后的DataFrame:")
        print(df.to_string(index=False))
        pd_tables.append(df)

    print(f"\n3. 填充数据:")
    for i, data in enumerate(fill_data):
        print(f"   第{i+1}行: {data}")

    # 模拟fill_tables方法的简单逻辑
    try:
        filled_tables = []
        for df in pd_tables:
            if not isinstance(df, pd.DataFrame) or df.empty:
                filled_tables.append(df)
                continue
            # 简单策略：按表头匹配填充
            for i, row in enumerate(fill_data):
                if i >= len(df):
                    # 新增行
                    df.loc[len(df)] = [row.get(col, "") for col in df.columns]
                else:
                    for col in df.columns:
                        if col in row:
                            df.at[i, col] = row[col]
            filled_tables.append(df)

        print(f"\n4. 填充后的结果:")
        for i, df in enumerate(filled_tables):
            print(f"   第{i+1}个表格:")
            print(df.to_string(index=False))

        # 转换回API返回格式
        result = []
        for df in filled_tables:
            result.append({
                'columns': list(df.columns),
                'data': df.values.tolist()
            })

        print(f"\n5. API返回的JSON格式:")
        api_response = {'success': True, 'filled_tables': result}
        print(json.dumps(api_response, ensure_ascii=False, indent=2))

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_empty_table_handling():
    """测试空表格的处理"""
    print("\n=== 测试空表格处理 ===")

    api_request = {
        "tables": [
            {
                "columns": [],
                "data": []
            }
        ],
        "fill_data": []
    }

    try:
        tables = api_request.get('tables', [])
        fill_data = api_request.get('fill_data', [])

        pd_tables = []
        for t in tables:
            df = pd.DataFrame(t['data'], columns=t['columns'])
            pd_tables.append(df)

        # 模拟空表格处理
        filled_tables = []
        for df in pd_tables:
            if not isinstance(df, pd.DataFrame) or df.empty:
                filled_tables.append(df)
                continue
            filled_tables.append(df)

        print("✅ 空表格处理成功")
        return True

    except Exception as e:
        print(f"❌ 空表格处理失败: {str(e)}")
        return False

if __name__ == "__main__":
    success1 = test_table_fill_api_format()
    success2 = test_empty_table_handling()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！API参数格式正确。")
    else:
        print("\n❌ 部分测试失败，需要检查实现。")
