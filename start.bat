@echo off
chcp 65001 >nul
echo ========================================
echo AI文档处理项目启动脚本
echo ========================================
echo.

:menu
echo 请选择操作:
echo 1. 运行所有测试
echo 2. 启动Web应用
echo 3. 测试导入功能
echo 4. 查看项目状态
echo 5. 安装/更新依赖
echo 6. 退出
echo.
set /p choice=请输入选择 (1-6): 

if "%choice%"=="1" goto run_tests
if "%choice%"=="2" goto start_web
if "%choice%"=="3" goto test_imports
if "%choice%"=="4" goto show_status
if "%choice%"=="5" goto install_deps
if "%choice%"=="6" goto exit
echo 无效选择，请重新输入
goto menu

:run_tests
echo.
echo 正在运行测试...
.\venv_ci_test\Scripts\python.exe -m pytest tests/ -v
echo.
pause
goto menu

:start_web
echo.
echo 正在启动Web应用...
echo 应用将在 http://localhost:5000 启动
echo 按 Ctrl+C 停止服务器
.\venv_ci_test\Scripts\python.exe run_app.py
goto menu

:test_imports
echo.
echo 正在测试导入功能...
cd src
..\venv_ci_test\Scripts\python.exe test_imports.py
cd ..
echo.
pause
goto menu

:show_status
echo.
echo 项目状态:
echo - Python版本: 
.\venv_ci_test\Scripts\python.exe --version
echo - pytest版本:
.\venv_ci_test\Scripts\python.exe -m pytest --version
echo - 已安装包数量:
.\venv_ci_test\Scripts\python.exe -m pip list | find /c ""
echo.
echo 详细状态请查看 PROJECT_STATUS.md 文件
pause
goto menu

:install_deps
echo.
echo 正在安装/更新依赖...
.\venv_ci_test\Scripts\python.exe -m pip install -r requirements.txt --upgrade
echo.
pause
goto menu

:exit
echo 再见！
exit /b 0
