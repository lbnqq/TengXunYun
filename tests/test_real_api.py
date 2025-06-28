#!/usr/bin/env python3
"""
测试真实web_app.py的API功能
"""

import requests
import json

def test_real_webapp_api():
    """测试真实web_app.py的API"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 测试真实web_app.py的API功能...")
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ 健康检查: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   响应: {health_data}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False
    
    # 测试表格填充API
    try:
        test_data = {
            "tables": [
                {
                    "columns": ["姓名", "年龄"],
                    "data": [["张三", ""], ["李四", ""]]
                }
            ],
            "fill_data": [
                {"姓名": "张三", "年龄": "25"},
                {"姓名": "李四", "年龄": "30"}
            ]
        }
        
        response = requests.post(
            f"{base_url}/api/table-fill",
            json=test_data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"✅ 表格填充API: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   成功: {result.get('success')}")
            if result.get('success'):
                filled_tables = result.get('filled_tables', [])
                print(f"   填充结果: {filled_tables}")
        else:
            print(f"   错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 表格填充API失败: {e}")
        return False
    
    print("🎉 真实web_app.py API测试完成！")
    return True

if __name__ == "__main__":
    test_real_webapp_api()
