# AI_Pytest7 项目使用指南

## 🎉 项目已成功修复并可正常运行！

### 问题解决总结
✅ **Python虚拟环境** - 已配置并激活  
✅ **依赖安装** - 所有146个依赖包已安装  
✅ **pytest配置** - 测试框架正常工作  
✅ **导入问题** - 所有核心模块可正常导入  
✅ **Web应用** - Flask应用可正常启动  

## 🚀 快速开始

### 方法1: 使用启动脚本（推荐）
```powershell
# Windows
cd aiDoc
start.bat

# Linux/Mac
cd aiDoc
chmod +x start.sh
./start.sh
```

### 方法2: 手动命令

#### 运行测试
```powershell
cd aiDoc
.\venv_ci_test\Scripts\python.exe -m pytest tests/ -v
```

#### 启动Web应用
```powershell
cd aiDoc
.\venv_ci_test\Scripts\python.exe run_app.py
```
然后访问: http://localhost:5000

#### 测试导入功能
```powershell
cd aiDoc\src
..\venv_ci_test\Scripts\python.exe test_imports.py
```

## 📊 测试结果
- **总测试数**: 12个
- **通过率**: 100% ✅
- **代码覆盖率**: 8% (基础功能已覆盖)

### 测试详情
```
tests/test_basic.py::test_basic_functionality ✅
tests/test_basic.py::test_imports ✅
tests/test_basic.py::test_flask_import ✅
tests/test_basic.py::test_pandas_import ✅
tests/test_basic.py::test_doc_processor_import ✅
tests/test_web_app.py::test_app_creation ✅
tests/test_web_app.py::test_health_endpoint ✅
tests/test_web_app.py::test_main_page ✅
tests/test_web_app.py::test_upload_endpoint_structure ✅
tests/test_web_app.py::test_config_loading ✅
tests/test_web_app.py::test_ocr_engine_import ✅
tests/test_web_app.py::test_document_processor_import ✅
```

## 🛠️ 常用命令

### 测试相关
```powershell
# 运行所有测试
.\venv_ci_test\Scripts\python.exe -m pytest tests/ -v

# 运行特定测试文件
.\venv_ci_test\Scripts\python.exe -m pytest tests/test_basic.py -v

# 运行带覆盖率的测试
.\venv_ci_test\Scripts\python.exe -m pytest tests/ --cov=src --cov-report=html

# 运行特定标记的测试
.\venv_ci_test\Scripts\python.exe -m pytest -m unit tests/
```

### 应用相关
```powershell
# 启动Web应用
.\venv_ci_test\Scripts\python.exe run_app.py

# 测试应用启动
.\venv_ci_test\Scripts\python.exe test_app_startup.py

# 检查Python版本
.\venv_ci_test\Scripts\python.exe --version

# 查看已安装包
.\venv_ci_test\Scripts\python.exe -m pip list
```

## 📁 重要文件说明

### 核心文件
- `src/web_app.py` - Flask Web应用主文件
- `src/main.py` - 项目主入口
- `src/doc_processor.py` - 文档处理核心逻辑
- `config/config.yaml` - 项目配置文件
- `requirements.txt` - Python依赖列表

### 测试文件
- `tests/test_basic.py` - 基础功能测试
- `tests/test_web_app.py` - Web应用测试
- `pytest.ini` - pytest配置文件

### 辅助文件
- `run_app.py` - 应用启动脚本
- `test_app_startup.py` - 启动测试脚本
- `start.bat` / `start.sh` - 便捷启动脚本
- `PROJECT_STATUS.md` - 项目状态详细报告

## 🔧 环境信息
- **Python版本**: 3.12.7
- **pytest版本**: 8.4.1
- **Flask版本**: 3.1.1
- **虚拟环境**: `venv_ci_test`
- **项目路径**: `f:\Tools2\AI_Pytest7\aiDoc`

## 🎯 下一步建议
1. **增加测试覆盖率** - 当前覆盖率8%，建议提升到80%以上
2. **完善API文档** - 为Web API添加详细文档
3. **添加集成测试** - 测试完整的业务流程
4. **性能优化** - 优化OCR和文档处理性能
5. **部署配置** - 配置生产环境部署

## ❓ 常见问题

### Q: 如何重新安装依赖？
```powershell
.\venv_ci_test\Scripts\python.exe -m pip install -r requirements.txt --upgrade
```

### Q: 如何添加新的测试？
在 `tests/` 目录下创建新的 `test_*.py` 文件，pytest会自动发现并运行。

### Q: 如何修改Web应用端口？
编辑 `run_app.py` 或 `src/web_app.py` 中的端口配置。

### Q: 如何查看详细的错误信息？
```powershell
.\venv_ci_test\Scripts\python.exe -m pytest tests/ -v --tb=long
```

## 📞 技术支持
如果遇到问题，请检查：
1. Python虚拟环境是否正确激活
2. 所有依赖是否已安装
3. 配置文件是否存在
4. 查看 `PROJECT_STATUS.md` 获取详细状态信息

---
**项目状态**: ✅ 正常运行  
**最后更新**: 2025-07-07  
**测试状态**: 12/12 通过
