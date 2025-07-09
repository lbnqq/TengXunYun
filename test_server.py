#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务器是否运行
"""

import requests
import time
import threading
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def start_server():
    """在后台启动服务器"""
    try:
        from web_app import app
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"服务器启动失败: {e}")

def test_server():
    """测试服务器响应"""
    base_url = "http://127.0.0.1:5000"
    
    print("等待服务器启动...")
    time.sleep(3)
    
    # 测试各个端点
    endpoints = [
        ('/', '主页'),
        ('/api/health', '健康检查'),
        ('/dashboard', '仪表板')
    ]
    
    print("\n=== 测试服务器响应 ===")
    
    for endpoint, name in endpoints:
        try:
            print(f"\n测试 {name} ({endpoint})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {name} 响应正常 (状态码: {response.status_code})")
                
                # 如果是JSON响应，显示内容
                if 'application/json' in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        print(f"   响应数据: {data}")
                    except:
                        pass
                else:
                    print(f"   内容长度: {len(response.text)} 字符")
            else:
                print(f"❌ {name} 响应异常 (状态码: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} 连接失败 - 服务器可能未启动")
        except requests.exceptions.Timeout:
            print(f"❌ {name} 请求超时")
        except Exception as e:
            print(f"❌ {name} 测试失败: {e}")

if __name__ == '__main__':
    print("=== 服务器测试工具 ===")
    
    # 在后台线程启动服务器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 测试服务器
    test_server()
    
    print("\n=== 测试完成 ===")
    print("如果所有测试都通过，说明服务器正常运行")
    print("您可以在浏览器中访问: http://127.0.0.1:5000")
    
    # 保持程序运行一段时间
    print("\n服务器将继续运行30秒...")
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\n服务器已停止")
