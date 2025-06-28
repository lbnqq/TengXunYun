#!/usr/bin/env python3
"""
模板保存修复端到端自动化测试
完整验证统一参数接口、模板格式标准化和错误处理增强功能
"""

import json
import requests
import sys
import os
import time
import unittest
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.tools.template_schema import TemplateSchema
from src.core.tools.error_handler import ErrorHandler

class TemplateFixesE2ETest(unittest.TestCase):
    """模板保存修复端到端测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": []
        }
        self.error_handler = ErrorHandler()
        
        # 等待服务启动
        self._wait_for_service()
    
    def _wait_for_service(self, timeout: int = 30):
        """等待服务启动"""
        print("⏳ 等待服务启动...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(f"{self.base_url}/api/health")
                if response.status_code == 200:
                    print("✅ 服务已启动")
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        raise Exception("服务启动超时")
    
    def _record_test_result(self, test_name: str, success: bool, error: Optional[str] = None):
        """记录测试结果"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed_tests"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results["failed_tests"] += 1
            self.test_results["errors"].append({
                "test": test_name,
                "error": error or "未知错误",
                "timestamp": datetime.now().isoformat()
            })
            print(f"❌ {test_name}: {error or '未知错误'}")
    
    def test_01_template_schema_validation(self):
        """测试模板Schema验证功能"""
        print("\n🔍 测试模板Schema验证功能...")
        
        # 测试格式模板验证 - 有效数据
        valid_format_template = {
            "template_id": "1234567890abcdef1234567890abcdef",
            "document_name": "测试格式模板",
            "structure_analysis": {
                "total_lines": 10,
                "headings": [],
                "paragraphs": [],
                "lists": [],
                "special_elements": [],
                "estimated_format": {},
                "analysis_confidence": 0.8
            },
            "format_rules": {
                "heading_formats": {},
                "paragraph_formats": {},
                "list_formats": {},
                "font_settings": {},
                "spacing_settings": {}
            },
            "format_prompt": "这是一个测试格式提示词"
        }
        
        result = TemplateSchema.validate_format_template(valid_format_template)
        self._record_test_result(
            "格式模板验证-有效数据",
            result["success"],
            result.get("error")
        )
        
        # 测试格式模板验证 - 无效数据
        invalid_format_template = {
            "document_name": "测试格式模板",
            # 缺少必需字段
        }
        
        result = TemplateSchema.validate_format_template(invalid_format_template)
        self._record_test_result(
            "格式模板验证-无效数据",
            not result["success"],  # 应该验证失败
            "验证应该失败但通过了"
        )
        
        # 测试文风模板验证 - 有效数据
        valid_style_template = {
            "template_id": "abcdef1234567890abcdef1234567890",
            "document_name": "测试文风模板",
            "style_features": {
                "sentence_structure": {},
                "vocabulary_choice": {},
                "expression_style": {},
                "text_organization": {},
                "language_habits": {}
            },
            "style_type": "business_professional",
            "style_prompt": "这是一个测试文风提示词"
        }
        
        result = TemplateSchema.validate_style_template(valid_style_template)
        self._record_test_result(
            "文风模板验证-有效数据",
            result["success"],
            result.get("error")
        )
        
        # 测试文风模板验证 - 无效数据
        invalid_style_template = {
            "document_name": "测试文风模板",
            "style_type": "invalid_style_type",  # 无效的文风类型
            "style_prompt": "这是一个测试文风提示词"
        }
        
        result = TemplateSchema.validate_style_template(invalid_style_template)
        self._record_test_result(
            "文风模板验证-无效数据",
            not result["success"],  # 应该验证失败
            "验证应该失败但通过了"
        )
    
    def test_02_template_normalization(self):
        """测试模板数据标准化功能"""
        print("\n🔍 测试模板数据标准化功能...")
        
        # 测试格式模板标准化
        raw_format_data = {
            "document_name": "测试标准化格式模板"
        }
        
        normalized = TemplateSchema.normalize_format_template(raw_format_data)
        
        # 验证必需字段是否存在
        required_fields = ["template_id", "document_name", "structure_analysis", "format_rules", "format_prompt", "created_time", "version"]
        missing_fields = [field for field in required_fields if field not in normalized]
        
        self._record_test_result(
            "格式模板标准化",
            len(missing_fields) == 0,
            f"缺少字段: {missing_fields}" if missing_fields else None
        )
        
        # 测试文风模板标准化
        raw_style_data = {
            "document_name": "测试标准化文风模板"
        }
        
        normalized = TemplateSchema.normalize_style_template(raw_style_data)
        
        # 验证必需字段是否存在
        required_fields = ["template_id", "document_name", "style_features", "style_type", "style_prompt", "analysis_time", "version"]
        missing_fields = [field for field in required_fields if field not in normalized]
        
        self._record_test_result(
            "文风模板标准化",
            len(missing_fields) == 0,
            f"缺少字段: {missing_fields}" if missing_fields else None
        )
    
    def test_03_error_handler(self):
        """测试错误处理功能"""
        print("\n🔍 测试错误处理功能...")
        
        # 测试验证错误处理
        try:
            raise ValueError("缺少必需字段: template_id")
        except Exception as e:
            result = self.error_handler.handle_error(e, {"context": "template_validation"})
            self._record_test_result(
                "验证错误处理",
                result.get("category") == "validation",
                f"错误分类不正确: {result.get('category')}"
            )
        
        # 测试API错误处理
        try:
            raise requests.RequestException("API调用失败")
        except Exception as e:
            result = self.error_handler.handle_error(e, {"context": "api_call"})
            self._record_test_result(
                "API错误处理",
                result.get("category") == "api",
                f"错误分类不正确: {result.get('category')}"
            )
        
        # 测试文件IO错误处理
        try:
            raise FileNotFoundError("模板文件不存在")
        except Exception as e:
            result = self.error_handler.handle_error(e, {"context": "file_operation"})
            self._record_test_result(
                "文件IO错误处理",
                result.get("category") == "file_io",
                f"错误分类不正确: {result.get('category')}"
            )
        
        # 测试错误ID生成
        try:
            raise Exception("测试错误")
        except Exception as e:
            result = self.error_handler.handle_error(e)
            self._record_test_result(
                "错误ID生成",
                "error_id" in result and len(result["error_id"]) == 8,
                "错误ID生成失败"
            )
    
    def test_04_format_template_api_format1(self):
        """测试格式模板保存API - 格式1"""
        print("\n🔍 测试格式模板保存API - 格式1...")
        
        format_data = {
            "template_name": f"E2E测试格式模板1_{int(time.time())}",
            "template_data": {
                "document_name": f"E2E测试格式模板1_{int(time.time())}",
                "structure_analysis": {
                    "total_lines": 15,
                    "headings": [
                        {"level": 1, "text": "标题1", "line_number": 0, "confidence": 0.9}
                    ],
                    "paragraphs": [
                        {"text": "这是第一段正文内容", "line_number": 1, "confidence": 0.8}
                    ],
                    "lists": [],
                    "special_elements": [],
                    "estimated_format": {},
                    "analysis_confidence": 0.85
                },
                "format_rules": {
                    "heading_formats": {
                        "level_1": {"font_family": "黑体", "font_size": "三号", "line_height": "1.5"}
                    },
                    "paragraph_formats": {
                        "font_family": "宋体", "font_size": "小四", "text_align": "左对齐"
                    },
                    "list_formats": {},
                    "font_settings": {},
                    "spacing_settings": {}
                },
                "format_prompt": "这是一个端到端测试的格式提示词"
            }
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/format-templates", json=format_data)
            result = response.json()
            
            success = response.status_code == 200 and result.get("success", False)
            template_id = result.get("template_id", "")
            
            self._record_test_result(
                "格式模板保存API-格式1",
                success,
                f"状态码: {response.status_code}, 响应: {result}" if not success else None
            )
            
            # 如果保存成功，测试获取模板
            if success and template_id:
                self._test_get_format_template(template_id)
                
        except Exception as e:
            self._record_test_result(
                "格式模板保存API-格式1",
                False,
                str(e)
            )
    
    def test_05_format_template_api_format2(self):
        """测试格式模板保存API - 格式2"""
        print("\n🔍 测试格式模板保存API - 格式2...")
        
        format_data = {
            "template_id": f"e2e_test_format_{int(time.time())}",
            "document_name": f"E2E测试格式模板2_{int(time.time())}",
            "structure_analysis": {
                "total_lines": 20,
                "headings": [
                    {"level": 1, "text": "主标题", "line_number": 0, "confidence": 0.9},
                    {"level": 2, "text": "子标题", "line_number": 2, "confidence": 0.8}
                ],
                "paragraphs": [
                    {"text": "这是第一段正文内容", "line_number": 1, "confidence": 0.8},
                    {"text": "这是第二段正文内容", "line_number": 3, "confidence": 0.8}
                ],
                "lists": [
                    {"text": "列表项1", "line_number": 4, "list_type": "bullet", "confidence": 0.7}
                ],
                "special_elements": [],
                "estimated_format": {},
                "analysis_confidence": 0.8
            },
            "format_rules": {
                "heading_formats": {
                    "level_1": {"font_family": "黑体", "font_size": "三号", "line_height": "1.5"},
                    "level_2": {"font_family": "黑体", "font_size": "四号", "line_height": "1.5"}
                },
                "paragraph_formats": {
                    "font_family": "宋体", "font_size": "小四", "text_align": "左对齐"
                },
                "list_formats": {
                    "bullet": {"font_family": "宋体", "font_size": "小四"}
                },
                "font_settings": {},
                "spacing_settings": {}
            },
            "format_prompt": "这是一个端到端测试的格式提示词-格式2"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/format-templates", json=format_data)
            result = response.json()
            
            success = response.status_code == 200 and result.get("success", False)
            template_id = result.get("template_id", "")
            
            self._record_test_result(
                "格式模板保存API-格式2",
                success,
                f"状态码: {response.status_code}, 响应: {result}" if not success else None
            )
            
            # 如果保存成功，测试获取模板
            if success and template_id:
                self._test_get_format_template(template_id)
                
        except Exception as e:
            self._record_test_result(
                "格式模板保存API-格式2",
                False,
                str(e)
            )
    
    def test_06_style_template_api_format1(self):
        """测试文风模板保存API - 格式1"""
        print("\n🔍 测试文风模板保存API - 格式1...")
        
        style_data = {
            "reference_content": """
            这是一个端到端测试的参考文档。
            
            本文档用于验证文风分析功能的正确性。文档采用了商务专业的写作风格，
            语言简洁明了，逻辑清晰，重点突出。
            
            主要特点包括：
            1. 使用正式的商务用语
            2. 段落结构清晰
            3. 逻辑关系明确
            4. 表达方式专业
            """,
            "reference_name": f"E2E测试文风文档_{int(time.time())}"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/writing-style/save-template", json=style_data)
            result = response.json()
            
            success = response.status_code == 200 and result.get("success", False)
            template_id = result.get("template_id", "")
            
            self._record_test_result(
                "文风模板保存API-格式1",
                success,
                f"状态码: {response.status_code}, 响应: {result}" if not success else None
            )
            
            # 如果保存成功，测试获取模板
            if success and template_id:
                self._test_get_style_template(template_id)
                
        except Exception as e:
            self._record_test_result(
                "文风模板保存API-格式1",
                False,
                str(e)
            )
    
    def test_07_style_template_api_format2(self):
        """测试文风模板保存API - 格式2"""
        print("\n🔍 测试文风模板保存API - 格式2...")
        
        style_data = {
            "template_id": f"e2e_test_style_{int(time.time())}",
            "document_name": f"E2E测试文风模板2_{int(time.time())}",
            "analysis_time": datetime.now().isoformat(),
            "analysis_method": "basic",
            "document_stats": {
                "total_words": 150,
                "total_sentences": 8,
                "total_paragraphs": 4,
                "average_sentence_length": 18.75
            },
            "style_features": {
                "sentence_structure": {
                    "average_sentence_length": 18.75,
                    "sentence_complexity": "medium",
                    "passive_voice_ratio": 0.1
                },
                "vocabulary_choice": {
                    "formality_level": "formal",
                    "technical_terms": 0.2,
                    "modifier_usage": "moderate"
                },
                "expression_style": {
                    "tone": "professional",
                    "person_usage": "third_person",
                    "emotion_intensity": "low"
                },
                "text_organization": {
                    "paragraph_structure": "clear",
                    "logical_connections": "strong",
                    "transition_style": "explicit"
                },
                "language_habits": {
                    "oral_style": "low",
                    "written_standard": "high",
                    "regional_features": "none"
                }
            },
            "style_type": "business_professional",
            "confidence_score": 0.85,
            "style_prompt": "这是一个端到端测试的文风提示词-格式2",
            "detailed_analysis": {
                "strengths": ["逻辑清晰", "表达专业", "结构合理"],
                "weaknesses": ["可读性有待提升"],
                "recommendations": ["增加具体案例", "优化段落长度"]
            },
            "writing_recommendations": [
                "保持商务专业的写作风格",
                "使用清晰的结构组织内容",
                "避免过于复杂的句式"
            ],
            "style_comparison": {
                "similar_styles": ["formal_official"],
                "different_styles": ["narrative_descriptive"]
            }
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/writing-style/save-template", json=style_data)
            result = response.json()
            
            success = response.status_code == 200 and result.get("success", False)
            template_id = result.get("template_id", "")
            
            self._record_test_result(
                "文风模板保存API-格式2",
                success,
                f"状态码: {response.status_code}, 响应: {result}" if not success else None
            )
            
            # 如果保存成功，测试获取模板
            if success and template_id:
                self._test_get_style_template(template_id)
                
        except Exception as e:
            self._record_test_result(
                "文风模板保存API-格式2",
                False,
                str(e)
            )
    
    def test_08_error_scenarios(self):
        """测试错误场景处理"""
        print("\n🔍 测试错误场景处理...")
        
        # 测试无效数据
        invalid_data = {
            "invalid_field": "invalid_value",
            "another_invalid": 123
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/format-templates", json=invalid_data)
            result = response.json()
            
            # 应该返回错误状态
            self._record_test_result(
                "无效数据处理",
                response.status_code != 200,
                f"应该返回错误但成功了: {response.status_code}"
            )
            
        except Exception as e:
            self._record_test_result(
                "无效数据处理",
                False,
                str(e)
            )
        
        # 测试空数据
        try:
            response = self.session.post(f"{self.base_url}/api/writing-style/save-template", json={})
            result = response.json()
            
            # 应该返回错误状态
            self._record_test_result(
                "空数据处理",
                response.status_code != 200,
                f"应该返回错误但成功了: {response.status_code}"
            )
            
        except Exception as e:
            self._record_test_result(
                "空数据处理",
                False,
                str(e)
            )
        
        # 测试缺少必需字段
        incomplete_data = {
            "document_name": "测试文档"
            # 缺少其他必需字段
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/format-templates", json=incomplete_data)
            result = response.json()
            
            # 应该返回错误状态
            self._record_test_result(
                "缺少必需字段处理",
                response.status_code != 200,
                f"应该返回错误但成功了: {response.status_code}"
            )
            
        except Exception as e:
            self._record_test_result(
                "缺少必需字段处理",
                False,
                str(e)
            )
    
    def test_09_template_listing(self):
        """测试模板列表功能"""
        print("\n🔍 测试模板列表功能...")
        
        # 测试格式模板列表
        try:
            response = self.session.get(f"{self.base_url}/api/format-templates")
            result = response.json()
            
            success = response.status_code == 200 and "templates" in result
            template_count = len(result.get("templates", []))
            
            self._record_test_result(
                "格式模板列表",
                success,
                f"状态码: {response.status_code}, 响应: {result}" if not success else None
            )
            
            print(f"   发现 {template_count} 个格式模板")
            
        except Exception as e:
            self._record_test_result(
                "格式模板列表",
                False,
                str(e)
            )
        
        # 测试文风模板列表
        try:
            response = self.session.get(f"{self.base_url}/api/writing-style/templates")
            result = response.json()
            
            success = response.status_code == 200 and "templates" in result
            template_count = len(result.get("templates", []))
            
            self._record_test_result(
                "文风模板列表",
                success,
                f"状态码: {response.status_code}, 响应: {result}" if not success else None
            )
            
            print(f"   发现 {template_count} 个文风模板")
            
        except Exception as e:
            self._record_test_result(
                "文风模板列表",
                False,
                str(e)
            )
    
    def _test_get_format_template(self, template_id: str):
        """测试获取格式模板"""
        try:
            response = self.session.get(f"{self.base_url}/api/format-templates/{template_id}")
            result = response.json()
            
            success = response.status_code == 200 and result.get("success", False)
            
            self._record_test_result(
                f"获取格式模板-{template_id[:8]}",
                success,
                f"状态码: {response.status_code}, 响应: {result}" if not success else None
            )
            
        except Exception as e:
            self._record_test_result(
                f"获取格式模板-{template_id[:8]}",
                False,
                str(e)
            )
    
    def _test_get_style_template(self, template_id: str):
        """测试获取文风模板"""
        try:
            response = self.session.get(f"{self.base_url}/api/writing-style/templates/{template_id}")
            result = response.json()
            
            success = response.status_code == 200 and result.get("success", False)
            
            self._record_test_result(
                f"获取文风模板-{template_id[:8]}",
                success,
                f"状态码: {response.status_code}, 响应: {result}" if not success else None
            )
            
        except Exception as e:
            self._record_test_result(
                f"获取文风模板-{template_id[:8]}",
                False,
                str(e)
            )
    
    def test_10_performance_test(self):
        """测试性能表现"""
        print("\n🔍 测试性能表现...")
        
        # 测试批量模板保存性能
        start_time = time.time()
        
        for i in range(3):
            format_data = {
                "template_name": f"性能测试模板_{i}_{int(time.time())}",
                "template_data": {
                    "document_name": f"性能测试模板_{i}_{int(time.time())}",
                    "structure_analysis": {
                        "total_lines": 10,
                        "headings": [],
                        "paragraphs": [],
                        "lists": [],
                        "special_elements": [],
                        "estimated_format": {},
                        "analysis_confidence": 0.8
                    },
                    "format_rules": {
                        "heading_formats": {},
                        "paragraph_formats": {},
                        "list_formats": {},
                        "font_settings": {},
                        "spacing_settings": {}
                    },
                    "format_prompt": f"性能测试格式提示词_{i}"
                }
            }
            
            try:
                response = self.session.post(f"{self.base_url}/api/format-templates", json=format_data)
                if response.status_code != 200:
                    raise Exception(f"保存失败: {response.status_code}")
            except Exception as e:
                self._record_test_result(
                    f"性能测试-模板{i}",
                    False,
                    str(e)
                )
                break
        else:
            end_time = time.time()
            duration = end_time - start_time
            avg_duration = duration / 3
            
            self._record_test_result(
                "批量模板保存性能",
                avg_duration < 2.0,  # 平均每个模板保存时间应小于2秒
                f"平均保存时间过长: {avg_duration:.2f}秒"
            )
            
            print(f"   平均保存时间: {avg_duration:.2f}秒")
    
    def tearDown(self):
        """测试后清理"""
        self.session.close()
    
    def generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        report = {
            "test_summary": {
                "total_tests": self.test_results["total_tests"],
                "passed_tests": self.test_results["passed_tests"],
                "failed_tests": self.test_results["failed_tests"],
                "success_rate": (self.test_results["passed_tests"] / self.test_results["total_tests"] * 100) if self.test_results["total_tests"] > 0 else 0
            },
            "test_details": {
                "errors": self.test_results["errors"]
            },
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "base_url": self.base_url,
                "python_version": sys.version
            }
        }
        
        return report

def run_e2e_tests():
    """运行端到端测试"""
    print("🚀 开始模板保存修复端到端自动化测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TemplateFixesE2ETest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 用已初始化的实例生成报告
    test_instance = test_suite._tests[0]
    report = test_instance.generate_test_report()
    
    # 打印测试报告
    print("\n" + "=" * 60)
    print("📊 测试报告")
    print("=" * 60)
    print(f"总测试数: {report['test_summary']['total_tests']}")
    print(f"通过测试: {report['test_summary']['passed_tests']}")
    print(f"失败测试: {report['test_summary']['failed_tests']}")
    print(f"成功率: {report['test_summary']['success_rate']:.1f}%")
    
    if report['test_details']['errors']:
        print("\n❌ 失败详情:")
        for error in report['test_details']['errors']:
            print(f"  - {error['test']}: {error['error']}")
    
    # 保存测试报告
    report_file = f"test_report_e2e_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 测试报告已保存: {report_file}")
    
    # 返回测试结果
    return report['test_summary']['success_rate'] >= 80.0

if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1) 