@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 端到端自动化测试启动脚本
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist "venv" (
    echo ℹ️ 虚拟环境不存在，正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
)

:: 激活虚拟环境
echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat

:: 检查依赖
echo 🔍 检查项目依赖...
python -c "import flask, requests" >nul 2>&1
if errorlevel 1 (
    echo ℹ️ 依赖未安装，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖安装成功
)

:: 创建必要目录
echo 📁 创建必要目录...
if not exist "uploads" mkdir uploads
if not exist "output" mkdir output
if not exist "temp" mkdir temp
if not exist "test_results" mkdir test_results

:: 启动服务
echo 🚀 启动后端服务...
echo.
echo 💡 服务启动后会自动打开浏览器
echo 💡 按 Ctrl+C 停止服务
echo.

python start_e2e_service.py

pause 