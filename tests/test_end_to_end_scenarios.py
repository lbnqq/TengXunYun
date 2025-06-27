#!/usr/bin/env python3
"""
端到端测试场景
模拟真实用户的完整操作流程，验证系统的整体可用性

测试场景：
1. 新用户首次使用流程
2. 文档上传和分析完整流程
3. 文风分析完整流程
4. 格式对齐完整流程
5. 批量处理流程
6. 错误恢复流程
7. 多标签页切换流程
"""

import os
import sys
import json
import time
import requests
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
import threading

class EndToEndTestScenarios:
    """端到端测试场景类"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.server_process = None
        self.session = requests.Session()
        self.setup_test_environment()
        
    def setup_test_environment(self):
        """设置测试环境"""
        # 创建测试文件
        test_dir = Path("test_files")
        test_dir.mkdir(exist_ok=True)
        
        # 创建各种测试场景的文件
        test_files = {
            'user_manual.txt': """用户手册

第一章 系统介绍
本系统是一个智能办公文档处理平台，支持多种文档格式的处理和分析。

第二章 主要功能
1. 文档上传和解析
2. 智能内容分析
3. 文风特征提取
4. 格式自动对齐
5. 批量文档处理

第三章 使用指南
3.1 文档上传
用户可以通过拖拽或点击的方式上传文档。

3.2 分析结果查看
系统会自动分析文档并显示结果。

3.3 结果导出
用户可以导出分析结果和处理后的文档。

第四章 注意事项
- 支持的文件格式：TXT、PDF、DOCX
- 单个文件大小限制：10MB
- 批量处理最多支持50个文件

第五章 技术支持
如有问题，请联系技术支持团队。""",
            
            'meeting_notes.txt': """会议纪要

会议主题：产品功能优化讨论
时间：2024年6月25日 14:00-16:00
参会人员：张三、李四、王五、赵六

一、会议议程
1. 产品现状分析
2. 用户反馈汇总
3. 功能优化方案
4. 下一步计划

二、讨论内容
1. 产品现状分析
   - 用户活跃度较高
   - 核心功能稳定
   - 需要优化用户体验

2. 用户反馈汇总
   - 文件上传速度需要提升
   - 分析结果展示需要更直观
   - 希望增加批量处理功能

3. 功能优化方案
   - 优化文件上传机制
   - 改进结果展示界面
   - 开发批量处理功能
   - 增加用户引导功能

三、行动计划
1. 下周完成技术方案设计
2. 两周内完成开发工作
3. 一个月内完成测试和上线

四、会议总结
本次会议明确了产品优化方向，制定了具体的行动计划。""",
            
            'simple_text.txt': "这是一个简单的测试文档，用于验证基本功能。",
            
            'style_sample.txt': """商务邮件示例

尊敬的客户：

您好！

感谢您对我们产品的关注和支持。根据您的需求，我们为您推荐以下解决方案：

1. 基础版本：适合个人用户使用
2. 专业版本：适合小团队使用  
3. 企业版本：适合大型组织使用

如需了解更多详情，请随时联系我们。

此致
敬礼！

销售团队
2024年6月25日"""
        }
        
        self.test_files = {}
        for filename, content in test_files.items():
            file_path = test_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.test_files[filename] = str(file_path)
    
    def log_scenario(self, scenario_name, status, details=None, error=None):
        """记录测试场景结果"""
        result = {
            'scenario': scenario_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'error': str(error) if error else None
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
        print(f"{status_icon} 场景: {scenario_name} - {status}")
        if details:
            print(f"   详情: {details}")
        if error:
            print(f"   错误: {error}")
        print()
    
    def start_server(self):
        """启动测试服务器"""
        try:
            python_path = "venv/Scripts/python.exe" if os.name == 'nt' else "venv/bin/python"
            if not os.path.exists(python_path):
                python_path = "python"
            
            self.server_process = subprocess.Popen(
                [python_path, "src/web_app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # 等待服务器启动
            for i in range(30):
                try:
                    response = self.session.get(f"{self.base_url}/api/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ 测试服务器启动成功")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ 测试服务器启动超时")
            return False
            
        except Exception as e:
            print(f"❌ 启动测试服务器失败: {e}")
            return False
    
    def stop_server(self):
        """停止测试服务器"""
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
    
    def scenario_new_user_first_time(self):
        """场景1: 新用户首次使用流程"""
        try:
            # 1. 访问首页
            response = self.session.get(self.base_url)
            if response.status_code != 200:
                raise Exception(f"首页访问失败: {response.status_code}")
            
            # 2. 检查健康状态
            health_response = self.session.get(f"{self.base_url}/api/health")
            if health_response.status_code != 200:
                raise Exception("健康检查失败")
            
            # 3. 获取配置信息
            config_response = self.session.get(f"{self.base_url}/api/config")
            if config_response.status_code != 200:
                raise Exception("配置获取失败")
            
            # 4. 获取可用模型
            models_response = self.session.get(f"{self.base_url}/api/models")
            if models_response.status_code != 200:
                raise Exception("模型列表获取失败")
            
            self.log_scenario("新用户首次使用流程", "PASS", "所有初始化步骤成功完成")
            return True
            
        except Exception as e:
            self.log_scenario("新用户首次使用流程", "FAIL", error=e)
            return False
    
    def scenario_document_upload_and_analysis(self):
        """场景2: 文档上传和分析完整流程"""
        try:
            # 1. 上传文档
            with open(self.test_files['user_manual.txt'], 'rb') as f:
                files = {'file': ('user_manual.txt', f, 'text/plain')}
                data = {'api_type': 'mock', 'model_name': 'mock-model'}
                
                upload_response = self.session.post(
                    f"{self.base_url}/api/upload",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if upload_response.status_code != 200:
                raise Exception(f"文档上传失败: {upload_response.status_code}")
            
            # 2. 检查分析结果
            result = upload_response.json()
            required_fields = ['file_id', 'analysis', 'document_type']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                raise Exception(f"分析结果缺少字段: {missing_fields}")
            
            # 3. 验证分析质量
            analysis = result.get('analysis', {})
            if not analysis.get('key_entities') and not analysis.get('summary'):
                raise Exception("分析结果质量不足")
            
            self.log_scenario("文档上传和分析完整流程", "PASS", 
                            f"文档类型: {result.get('document_type', 'unknown')}")
            return True
            
        except Exception as e:
            self.log_scenario("文档上传和分析完整流程", "FAIL", error=e)
            return False
    
    def scenario_writing_style_analysis(self):
        """场景3: 文风分析完整流程"""
        try:
            # 1. 上传文风样本
            with open(self.test_files['style_sample.txt'], 'rb') as f:
                files = {'file': ('style_sample.txt', f, 'text/plain')}
                data = {'analysis_type': 'style', 'api_type': 'mock'}
                
                style_response = self.session.post(
                    f"{self.base_url}/api/analyze_style",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if style_response.status_code != 200:
                raise Exception(f"文风分析失败: {style_response.status_code}")
            
            # 2. 检查文风分析结果
            result = style_response.json()
            if 'style_features' not in result and 'analysis' not in result:
                raise Exception("文风分析结果格式不正确")
            
            self.log_scenario("文风分析完整流程", "PASS", "文风分析成功完成")
            return True
            
        except Exception as e:
            self.log_scenario("文风分析完整流程", "FAIL", error=e)
            return False
    
    def scenario_format_alignment(self):
        """场景4: 格式对齐完整流程"""
        try:
            # 1. 准备源文档和目标文档
            with open(self.test_files['meeting_notes.txt'], 'rb') as source, \
                 open(self.test_files['style_sample.txt'], 'rb') as target:
                
                files = {
                    'source_file': ('meeting_notes.txt', source, 'text/plain'),
                    'target_file': ('style_sample.txt', target, 'text/plain')
                }
                data = {'api_type': 'mock', 'alignment_type': 'format'}
                
                alignment_response = self.session.post(
                    f"{self.base_url}/api/format_alignment",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if alignment_response.status_code != 200:
                raise Exception(f"格式对齐失败: {alignment_response.status_code}")
            
            # 2. 检查对齐结果
            result = alignment_response.json()
            if 'aligned_content' not in result and 'alignment_result' not in result:
                raise Exception("格式对齐结果格式不正确")
            
            self.log_scenario("格式对齐完整流程", "PASS", "格式对齐成功完成")
            return True
            
        except Exception as e:
            self.log_scenario("格式对齐完整流程", "FAIL", error=e)
            return False
    
    def scenario_batch_processing(self):
        """场景5: 批量处理流程"""
        try:
            # 1. 批量上传多个文件
            files = []
            for filename in ['simple_text.txt', 'meeting_notes.txt']:
                with open(self.test_files[filename], 'rb') as f:
                    files.append(('files', (filename, f.read(), 'text/plain')))
            
            data = {'batch_upload': 'true', 'api_type': 'mock'}
            
            batch_response = self.session.post(
                f"{self.base_url}/api/upload",
                files=files,
                data=data,
                timeout=60
            )
            
            if batch_response.status_code != 200:
                raise Exception(f"批量上传失败: {batch_response.status_code}")
            
            # 2. 检查批量处理结果
            result = batch_response.json()
            if 'batch_id' not in result and 'uploaded_files' not in result:
                raise Exception("批量处理结果格式不正确")
            
            self.log_scenario("批量处理流程", "PASS", "批量处理成功完成")
            return True
            
        except Exception as e:
            self.log_scenario("批量处理流程", "FAIL", error=e)
            return False
    
    def scenario_error_recovery(self):
        """场景6: 错误恢复流程"""
        try:
            # 1. 故意触发错误（上传不支持的文件）
            files = {'file': ('test.exe', b'fake exe', 'application/octet-stream')}
            data = {'api_type': 'mock'}
            
            error_response = self.session.post(
                f"{self.base_url}/api/upload",
                files=files,
                data=data
            )
            
            # 2. 验证错误处理
            if error_response.status_code != 400:
                raise Exception("错误处理不正确")
            
            error_result = error_response.json()
            if 'error' not in error_result:
                raise Exception("错误响应格式不正确")
            
            # 3. 验证系统恢复（正常请求应该仍然工作）
            health_response = self.session.get(f"{self.base_url}/api/health")
            if health_response.status_code != 200:
                raise Exception("系统未能从错误中恢复")
            
            self.log_scenario("错误恢复流程", "PASS", "错误处理和系统恢复正常")
            return True
            
        except Exception as e:
            self.log_scenario("错误恢复流程", "FAIL", error=e)
            return False
    
    def run_all_scenarios(self):
        """运行所有端到端测试场景"""
        print("=" * 80)
        print("🎭 开始端到端测试场景")
        print("=" * 80)
        
        # 启动服务器
        if not self.start_server():
            print("❌ 无法启动测试服务器，测试终止")
            return False
        
        try:
            # 运行所有场景
            scenarios = [
                self.scenario_new_user_first_time,
                self.scenario_document_upload_and_analysis,
                self.scenario_writing_style_analysis,
                self.scenario_format_alignment,
                self.scenario_batch_processing,
                self.scenario_error_recovery,
            ]
            
            for scenario in scenarios:
                try:
                    scenario()
                    time.sleep(1)  # 场景间隔
                except Exception as e:
                    self.log_scenario(scenario.__name__, "FAIL", error=e)
                    
        finally:
            # 停止服务器
            self.stop_server()
        
        # 生成测试报告
        self.generate_report()
        
        # 返回测试结果
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        total = len(self.test_results)
        
        print("=" * 80)
        print(f"🏁 端到端测试完成: {passed}/{total} 场景通过")
        print("=" * 80)
        
        return passed == total
    
    def generate_report(self):
        """生成测试报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_type': 'end_to_end_scenarios',
            'summary': {
                'total': len(self.test_results),
                'passed': sum(1 for r in self.test_results if r['status'] == 'PASS'),
                'failed': sum(1 for r in self.test_results if r['status'] == 'FAIL'),
                'skipped': sum(1 for r in self.test_results if r['status'] == 'SKIP')
            },
            'scenarios': self.test_results
        }
        
        report_file = f"e2e_scenarios_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📊 端到端测试报告已保存: {report_file}")

if __name__ == "__main__":
    test = EndToEndTestScenarios()
    success = test.run_all_scenarios()
    sys.exit(0 if success else 1)
