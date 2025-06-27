#!/usr/bin/env python3
"""
AI思考提示演示启动脚本
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

def start_demo_server():
    """启动演示服务器"""
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    demo_file = project_root / "tests" / "test_ai_thinking_demo.html"
    
    if not demo_file.exists():
        print("❌ 演示文件不存在:", demo_file)
        return False
    
    # 切换到项目根目录
    os.chdir(project_root)
    
    # 设置端口
    PORT = 8080
    
    # 创建自定义处理器
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # 添加CORS头
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def do_OPTIONS(self):
            self.send_response(200)
            self.end_headers()
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print(f"🚀 AI思考提示演示服务器已启动")
            print(f"📁 服务目录: {project_root}")
            print(f"🌐 访问地址: http://localhost:{PORT}/tests/test_ai_thinking_demo.html")
            print(f"📝 演示文件: {demo_file}")
            print("\n" + "="*60)
            print("🎯 功能说明:")
            print("• 🧠 体验AI思考过程 - 展示文思泉涌的动画效果")
            print("• 📝 智能文档填充 - 模拟文档填充过程")
            print("• 💡 AI填写建议 - 展示AI建议生成")
            print("• ⚠️ 错误处理演示 - 展示错误状态处理")
            print("="*60)
            print("\n💡 提示: 按 Ctrl+C 停止服务器")
            
            # 自动打开浏览器
            try:
                webbrowser.open(f"http://localhost:{PORT}/tests/test_ai_thinking_demo.html")
                print("🌐 已自动打开浏览器...")
            except:
                print("⚠️ 无法自动打开浏览器，请手动访问上述地址")
            
            # 启动服务器
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {PORT} 已被占用，请尝试其他端口")
        else:
            print(f"❌ 启动服务器失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🤖 AI智能写作助手 - 思考提示演示")
    print("="*40)
    
    # 检查依赖
    required_files = [
        "tests/test_ai_thinking_demo.html",
        "static/css/enhanced-ui.css"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n请确保在项目根目录下运行此脚本")
        return False
    
    print("✅ 所有必要文件检查通过")
    print()
    
    # 启动演示服务器
    return start_demo_server()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 