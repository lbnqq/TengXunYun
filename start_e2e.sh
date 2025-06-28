#!/bin/bash

# 端到端自动化测试启动脚本
# 适用于Linux/Mac环境

set -e  # 遇到错误立即退出

echo "========================================"
echo "🚀 端到端自动化测试启动脚本"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    echo "请先安装Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "ℹ️ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败"
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
echo "🔍 检查项目依赖..."
if ! python -c "import flask, requests" &> /dev/null; then
    echo "ℹ️ 依赖未安装，正在安装..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装成功"
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p uploads output temp test_results

# 启动服务
echo "🚀 启动后端服务..."
echo
echo "💡 服务启动后会自动打开浏览器"
echo "💡 按 Ctrl+C 停止服务"
echo

python start_e2e_service.py 