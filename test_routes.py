#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web应用路由
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_routes():
    """测试所有路由"""
    print("=== 测试Web应用路由 ===")
    
    try:
        from web_app import app
        
        # 创建测试客户端
        with app.test_client() as client:
            
            # 测试主页
            print("\n1. 测试主页 (/)")
            response = client.get('/')
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ 主页访问成功")
                print(f"   内容长度: {len(response.data)} 字节")
            else:
                print("   ❌ 主页访问失败")
            
            # 测试健康检查
            print("\n2. 测试健康检查 (/api/health)")
            response = client.get('/api/health')
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ 健康检查成功")
                try:
                    data = response.get_json()
                    print(f"   响应: {data}")
                except:
                    print("   响应数据解析失败")
            else:
                print("   ❌ 健康检查失败")
            
            # 测试仪表板
            print("\n3. 测试仪表板 (/dashboard)")
            response = client.get('/dashboard')
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ 仪表板访问成功")
                try:
                    data = response.get_json()
                    print(f"   响应: {data}")
                except:
                    print("   响应数据解析失败")
            else:
                print("   ❌ 仪表板访问失败")
            
            # 测试上传端点（GET请求，应该返回405）
            print("\n4. 测试上传端点 (/api/upload)")
            response = client.get('/api/upload')
            print(f"   状态码: {response.status_code}")
            if response.status_code == 405:
                print("   ✅ 上传端点正确拒绝GET请求")
            else:
                print(f"   ⚠️  上传端点返回状态码: {response.status_code}")
            
            # 测试不存在的路由
            print("\n5. 测试不存在的路由 (/nonexistent)")
            response = client.get('/nonexistent')
            print(f"   状态码: {response.status_code}")
            if response.status_code == 404:
                print("   ✅ 正确返回404错误")
            else:
                print(f"   ⚠️  意外的状态码: {response.status_code}")
        
        print("\n=== 路由测试完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 路由测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_available_routes():
    """显示所有可用路由"""
    print("\n=== 可用路由列表 ===")
    
    try:
        from web_app import app
        
        routes = []
        for rule in app.url_map.iter_rules():
            methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
            routes.append(f"{rule.rule} [{methods}]")
        
        routes.sort()
        for i, route in enumerate(routes, 1):
            print(f"{i:2d}. {route}")
            
    except Exception as e:
        print(f"❌ 获取路由列表失败: {e}")

if __name__ == '__main__':
    print("Web应用路由测试工具")
    print("=" * 50)
    
    # 显示可用路由
    show_available_routes()
    
    # 测试路由
    success = test_routes()
    
    if success:
        print("\n🎉 所有路由测试完成！")
        print("\n使用方法:")
        print("1. 启动应用: python run_app.py")
        print("2. 访问主页: http://localhost:5000/")
        print("3. 健康检查: http://localhost:5000/api/health")
        print("4. 仪表板: http://localhost:5000/dashboard")
    else:
        print("\n❌ 路由测试失败，请检查应用配置")
