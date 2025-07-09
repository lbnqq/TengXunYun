#!/bin/bash

echo "========================================"
echo "AI文档处理项目启动脚本"
echo "========================================"
echo

show_menu() {
    echo "请选择操作:"
    echo "1. 运行所有测试"
    echo "2. 启动Web应用"
    echo "3. 测试导入功能"
    echo "4. 查看项目状态"
    echo "5. 安装/更新依赖"
    echo "6. 退出"
    echo
}

while true; do
    show_menu
    read -p "请输入选择 (1-6): " choice
    
    case $choice in
        1)
            echo
            echo "正在运行测试..."
            ./venv_ci_test/Scripts/python.exe -m pytest tests/ -v
            echo
            read -p "按回车键继续..."
            ;;
        2)
            echo
            echo "正在启动Web应用..."
            echo "应用将在 http://localhost:5000 启动"
            echo "按 Ctrl+C 停止服务器"
            ./venv_ci_test/Scripts/python.exe run_app.py
            ;;
        3)
            echo
            echo "正在测试导入功能..."
            cd src
            ../venv_ci_test/Scripts/python.exe test_imports.py
            cd ..
            echo
            read -p "按回车键继续..."
            ;;
        4)
            echo
            echo "项目状态:"
            echo -n "- Python版本: "
            ./venv_ci_test/Scripts/python.exe --version
            echo -n "- pytest版本: "
            ./venv_ci_test/Scripts/python.exe -m pytest --version
            echo -n "- 已安装包数量: "
            ./venv_ci_test/Scripts/python.exe -m pip list | wc -l
            echo
            echo "详细状态请查看 PROJECT_STATUS.md 文件"
            read -p "按回车键继续..."
            ;;
        5)
            echo
            echo "正在安装/更新依赖..."
            ./venv_ci_test/Scripts/python.exe -m pip install -r requirements.txt --upgrade
            echo
            read -p "按回车键继续..."
            ;;
        6)
            echo "再见！"
            exit 0
            ;;
        *)
            echo "无效选择，请重新输入"
            ;;
    esac
done
