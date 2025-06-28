#!/usr/bin/env python3
"""
配置检查脚本 - 帮助诊断API配置问题
"""

import os
from dotenv import load_dotenv

def check_api_configuration():
    """检查API配置状态"""
    print("=" * 60)
    print("API配置检查")
    print("=" * 60)
    
    # 加载环境变量
    load_dotenv()
    
    # 检查各个API的配置
    api_configs = {
        '讯飞星火 (Xingcheng)': {
            'key': os.getenv('XINGCHENG_API_KEY'),
            'secret': os.getenv('XINGCHENG_API_SECRET'),
            'required': ['key', 'secret']
        },
        '七牛云 DeepSeek': {
            'key': os.getenv('QINIU_API_KEY'),
            'required': ['key']
        },
        'Together.ai': {
            'key': os.getenv('TOGETHER_API_KEY'),
            'required': ['key']
        },
        'OpenRouter': {
            'key': os.getenv('OPENROUTER_API_KEY'),
            'required': ['key']
        }
    }
    
    print("📋 API配置状态:")
    print("-" * 60)
    
    working_apis = []
    for api_name, config in api_configs.items():
        missing = []
        for required in config['required']:
            if not config.get(required):
                missing.append(required)
        
        if missing:
            print(f"❌ {api_name}: 缺少 {', '.join(missing)}")
        else:
            print(f"✅ {api_name}: 配置完整")
            working_apis.append(api_name)
    
    print("-" * 60)
    print(f"📊 总计: {len(working_apis)}/{len(api_configs)} 个API配置完整")
    
    if not working_apis:
        print("\n⚠️  警告: 没有配置任何API密钥")
        print("💡 建议:")
        print("   1. 复制 config.env.example 为 .env")
        print("   2. 在 .env 文件中填入您的API密钥")
        print("   3. 或者使用模拟模式进行测试")
    else:
        print(f"\n✅ 可用的API: {', '.join(working_apis)}")
    
    return working_apis

def check_environment():
    """检查环境配置"""
    print("\n" + "=" * 60)
    print("环境配置检查")
    print("=" * 60)
    
    # 检查.env文件
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ .env 文件存在: {env_file}")
    else:
        print(f"❌ .env 文件不存在: {env_file}")
        print("💡 建议: 复制 config.env.example 为 .env")
    
    # 检查项目结构
    required_dirs = ['src', 'templates', 'static', 'uploads', 'output']
    print("\n📁 项目结构检查:")
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ 目录存在")
        else:
            print(f"❌ {dir_name}/ 目录不存在")
    
    # 检查Python依赖
    print("\n🐍 Python依赖检查:")
    try:
        import flask
        print("✅ Flask 已安装")
    except ImportError:
        print("❌ Flask 未安装")
    
    try:
        import requests
        print("✅ Requests 已安装")
    except ImportError:
        print("❌ Requests 未安装")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv 已安装")
    except ImportError:
        print("❌ python-dotenv 未安装")

def provide_solutions():
    """提供解决方案"""
    print("\n" + "=" * 60)
    print("解决方案")
    print("=" * 60)
    
    print("🔧 如果遇到网络错误，请尝试以下解决方案:")
    print()
    print("1. 使用模拟模式:")
    print("   - 在Web界面中选择 '模拟模式'")
    print("   - 无需API密钥即可测试功能")
    print()
    print("2. 配置API密钥:")
    print("   - 复制 config.env.example 为 .env")
    print("   - 在 .env 文件中填入您的API密钥")
    print("   - 重启Web服务器")
    print()
    print("3. 检查网络连接:")
    print("   - 确保能够访问外部API服务")
    print("   - 检查防火墙设置")
    print()
    print("4. 使用多API自动选择:")
    print("   - 在Web界面中选择 '多API自动选择'")
    print("   - 系统会自动尝试可用的API服务")
    print()
    print("5. 查看详细错误信息:")
    print("   - 检查浏览器开发者工具的控制台")
    print("   - 查看服务器日志输出")

def main():
    """主函数"""
    print("🔍 办公文档智能代理 - 配置检查工具")
    print("=" * 60)
    
    # 检查API配置
    working_apis = check_api_configuration()
    
    # 检查环境配置
    check_environment()
    
    # 提供解决方案
    provide_solutions()
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)
    
    if working_apis:
        print("🎉 您的系统已配置好，可以正常使用!")
    else:
        print("⚠️  请配置API密钥或使用模拟模式")

if __name__ == "__main__":
    main() 