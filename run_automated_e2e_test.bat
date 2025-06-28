@echo off
chcp 65001 >nul
echo ========================================
echo 🤖 自动化端到端测试启动脚本
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

:: 显示Python版本
echo ℹ️ Python版本信息:
python --version

:: 检查虚拟环境
if not exist "venv" (
    echo ℹ️ 虚拟环境不存在，将在测试过程中自动创建
) else (
    echo ✅ 虚拟环境已存在
)

:: 检查Selenium
echo.
echo 🔍 检查Selenium依赖...
python -c "import selenium" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Selenium未安装，Web前端测试将跳过
    echo 💡 如需Web测试，请运行: pip install selenium
) else (
    echo ✅ Selenium已安装
)

:: 检查Chrome WebDriver
echo.
echo 🔍 检查Chrome WebDriver...
where chromedriver >nul 2>&1
if errorlevel 1 (
    echo ⚠️ ChromeDriver未找到，Web前端测试可能失败
    echo 💡 请下载ChromeDriver并添加到PATH: https://chromedriver.chromium.org/
) else (
    echo ✅ ChromeDriver已找到
)

:: 创建测试目录
echo.
echo 📁 创建测试目录...
if not exist "test_results" mkdir test_results
if not exist "temp" mkdir temp
if not exist "uploads" mkdir uploads
if not exist "output" mkdir output

:: 显示测试配置
echo.
echo ========================================
echo 📋 测试配置信息
echo ========================================
echo 测试脚本: automated_e2e_test.py
echo 服务器地址: http://localhost:5000
echo 测试页面: /enhanced-frontend-complete
echo 测试超时: 300秒
echo 日志文件: automated_e2e_test.log
echo 报告目录: test_results/
echo ========================================

:: 确认开始测试
echo.
echo ⚠️ 即将开始自动化端到端测试
echo 💡 测试过程将包括:
echo   1. 虚拟环境设置和依赖安装
echo   2. 后端服务启动
echo   3. CLI功能测试（API接口）
echo   4. Web前端自动化测试（Selenium）
echo   5. 业务流程贯通性验证
echo   6. 测试报告生成
echo.
set /p confirm="是否继续? (y/N): "
if /i not "%confirm%"=="y" (
    echo 测试已取消
    pause
    exit /b 0
)

:: 开始测试
echo.
echo 🚀 开始自动化端到端测试...
echo ⏰ 开始时间: %date% %time%
echo.

:: 运行测试脚本
python automated_e2e_test.py

:: 检查测试结果
if errorlevel 1 (
    echo.
    echo ❌ 自动化端到端测试失败
    echo 💡 请查看日志文件: automated_e2e_test.log
    echo 💡 请查看测试报告: test_results/
) else (
    echo.
    echo ✅ 自动化端到端测试成功完成
    echo 📊 测试报告已生成在: test_results/
)

:: 显示最新的测试报告
echo.
echo 📋 最新的测试报告:
for /f "delims=" %%i in ('dir /b /od test_results\*.txt 2^>nul') do set latest_report=%%i
if defined latest_report (
    echo 📄 %latest_report%
    echo.
    echo 📄 报告内容预览:
    echo ----------------------------------------
    type "test_results\%latest_report%"
    echo ----------------------------------------
) else (
    echo ⚠️ 未找到测试报告文件
)

echo.
echo 🎉 测试流程完成
echo 💡 详细报告请查看 test_results/ 目录
echo 💡 日志文件: automated_e2e_test.log
echo.
pause 