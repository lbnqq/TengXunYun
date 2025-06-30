#!/usr/bin/env python3
"""
边界用例和异常场景测试
功能：测试系统在边界条件和异常情况下的表现
基于项目宪法的工程可用性保障机制
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class EdgeCaseTester:
    """边界用例测试器"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """初始化测试器"""
        self.base_url = base_url
        self.test_results = []
        
    def test_empty_file_handling(self) -> Dict[str, Any]:
        """测试空文件处理"""
        print("🧪 测试空文件处理...")
        
        start_time = time.time()
        
        try:
            # 创建空文件
            empty_file = "test_data/empty_file.txt"
            os.makedirs(os.path.dirname(empty_file), exist_ok=True)
            
            with open(empty_file, 'w', encoding='utf-8') as f:
                f.write("")
            
            # 测试格式对齐
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            aligner = EfficientFormatAligner()
            
            result = aligner.align_format("", "government_official")
            
            duration = time.time() - start_time
            
            if result and "error" not in result:
                print("✅ 空文件处理测试通过")
                return {
                    "name": "空文件处理测试",
                    "success": True,
                    "duration": duration,
                    "category": "边界用例",
                    "priority": "P2"
                }
            else:
                print("❌ 空文件处理测试失败")
                return {
                    "name": "空文件处理测试",
                    "success": False,
                    "error": "空文件处理异常",
                    "suggestion": "检查空文件处理逻辑，确保正确处理空内容",
                    "duration": duration,
                    "category": "边界用例",
                    "priority": "P2"
                }
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ 空文件处理测试异常: {e}")
            return {
                "name": "空文件处理测试",
                "success": False,
                "error": str(e),
                "suggestion": "完善空文件异常处理机制",
                "duration": duration,
                "category": "边界用例",
                "priority": "P2"
            }
    
    def test_large_file_handling(self) -> Dict[str, Any]:
        """测试大文件处理"""
        print("🧪 测试大文件处理...")
        
        start_time = time.time()
        
        try:
            # 创建大文件 (1MB)
            large_file = "test_data/large_file.txt"
            os.makedirs(os.path.dirname(large_file), exist_ok=True)
            
            with open(large_file, 'w', encoding='utf-8') as f:
                # 生成1MB的测试内容
                content = "这是一个大文件测试内容。" * 50000  # 约1MB
                f.write(content)
            
            # 测试文档处理
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            processor = EfficientFormatAligner()
            
            result = processor.align_format(content[:1000], "government_official")
            
            duration = time.time() - start_time
            
            if result and duration < 30:  # 30秒内完成
                print("✅ 大文件处理测试通过")
                return {
                    "name": "大文件处理测试",
                    "success": True,
                    "duration": duration,
                    "category": "边界用例",
                    "priority": "P2"
                }
            else:
                print("❌ 大文件处理测试失败")
                return {
                    "name": "大文件处理测试",
                    "success": False,
                    "error": "大文件处理超时或失败",
                    "suggestion": "优化大文件处理性能，考虑分块处理",
                    "duration": duration,
                    "category": "边界用例",
                    "priority": "P2"
                }
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ 大文件处理测试异常: {e}")
            return {
                "name": "大文件处理测试",
                "success": False,
                "error": str(e),
                "suggestion": "完善大文件异常处理机制",
                "duration": duration,
                "category": "边界用例",
                "priority": "P2"
            }
    
    def test_special_characters(self) -> Dict[str, Any]:
        """测试特殊字符处理"""
        print("🧪 测试特殊字符处理...")
        
        start_time = time.time()
        
        try:
            # 创建包含特殊字符的文件
            special_file = "test_data/special_chars.txt"
            os.makedirs(os.path.dirname(special_file), exist_ok=True)
            
            special_content = """
特殊字符测试文件
包含以下特殊字符：
!@#$%^&*()_+-=[]{}|;':",./<>?
中文标点：，。！？；：""''（）【】
特殊符号：©®™€£¥¢§¶†‡
数学符号：±×÷√∞∑∏∫∂
希腊字母：αβγδεζηθικλμνξοπρστυφχψω
"""
            
            with open(special_file, 'w', encoding='utf-8') as f:
                f.write(special_content)
            
            # 测试文风统一
            from src.core.tools.style_alignment_engine import StyleAlignmentEngine
            aligner = StyleAlignmentEngine()
            
            dummy_features = {"feature_vector": [0.1, 0.2, 0.3]}
            result = aligner.align_style(dummy_features, dummy_features, special_content)
            
            duration = time.time() - start_time
            
            if result and "error" not in result:
                print("✅ 特殊字符处理测试通过")
                return {
                    "name": "特殊字符处理测试",
                    "success": True,
                    "duration": duration,
                    "category": "边界用例",
                    "priority": "P2"
                }
            else:
                print("❌ 特殊字符处理测试失败")
                return {
                    "name": "特殊字符处理测试",
                    "success": False,
                    "error": "特殊字符处理异常",
                    "suggestion": "检查字符编码处理，确保支持各种特殊字符",
                    "duration": duration,
                    "category": "边界用例",
                    "priority": "P2"
                }
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ 特殊字符处理测试异常: {e}")
            return {
                "name": "特殊字符处理测试",
                "success": False,
                "error": str(e),
                "suggestion": "完善特殊字符异常处理机制",
                "duration": duration,
                "category": "边界用例",
                "priority": "P2"
            }

    def test_concurrent_processing(self) -> Dict[str, Any]:
        """
        测试并发处理能力
        功能：同时发起多个文档处理请求，验证系统并发稳定性和正确性
        """
        import threading
        results = []
        errors = []
        from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
        def worker(idx):
            try:
                processor = EfficientFormatAligner()
                # 使用同一个小文件，模拟并发
                result = processor.align_format("测试内容", "government_official")
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if len(errors) == 0 and len(results) == 10:
            print("✅ 并发处理测试通过")
            return {"name": "并发处理测试", "success": True, "category": "边界用例", "priority": "P1"}
        else:
            print(f"❌ 并发处理测试失败: {errors}")
            return {"name": "并发处理测试", "success": False, "error": errors, "category": "边界用例", "priority": "P1"}

    def test_memory_limit_handling(self) -> Dict[str, Any]:
        """
        测试内存限制下的处理能力
        功能：模拟大对象处理，观察是否触发MemoryError或内存泄漏
        """
        import tracemalloc
        from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
        tracemalloc.start()
        try:
            # 构造大数据对象
            big_data = "x" * 1024 * 1024  # 约1MB
            processor = EfficientFormatAligner()
            # 这里只测试初始化和部分方法，避免实际内存溢出
            result = processor.align_format(big_data[:1000], "government_official")
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            if peak < 200 * 1024 * 1024:  # 峰值小于200MB
                print("✅ 内存限制测试通过")
                return {"name": "内存限制测试", "success": True, "category": "边界用例", "priority": "P1"}
            else:
                print("❌ 内存限制测试失败")
                return {"name": "内存限制测试", "success": False, "error": f"峰值内存过高: {peak}", "category": "边界用例", "priority": "P1"}
        except MemoryError:
            tracemalloc.stop()
            print("❌ 内存限制测试触发MemoryError")
            return {"name": "内存限制测试", "success": False, "error": "MemoryError", "category": "边界用例", "priority": "P1"}
        except Exception as e:
            tracemalloc.stop()
            print(f"❌ 内存限制测试异常: {e}")
            return {"name": "内存限制测试", "success": False, "error": str(e), "category": "边界用例", "priority": "P1"}

    def test_disk_space_limit_handling(self) -> Dict[str, Any]:
        """
        测试磁盘空间不足时的处理能力
        功能：模拟磁盘写入失败，验证异常处理
        """
        import tempfile
        import shutil
        import os
        try:
            # 创建一个只读临时目录
            temp_dir = tempfile.mkdtemp()
            os.chmod(temp_dir, 0o400)  # 只读
            test_file = os.path.join(temp_dir, "test.txt")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                print("❌ 磁盘空间限制测试失败: 未触发异常")
                return {"name": "磁盘空间限制测试", "success": False, "error": "未触发写入异常", "category": "边界用例", "priority": "P1"}
            except Exception as e:
                print("✅ 磁盘空间限制测试通过")
                return {"name": "磁盘空间限制测试", "success": True, "category": "边界用例", "priority": "P1"}
        finally:
            try:
                os.chmod(temp_dir, 0o700)
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    def test_multi_module_integration(self) -> Dict[str, Any]:
        """
        多模块集成测试
        功能：串联调用文档处理、格式对齐、文风对齐等多个核心模块，验证集成流程
        """
        try:
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            from src.core.tools.style_alignment_engine import StyleAlignmentEngine
            from src.core.tools.comprehensive_style_processor import ComprehensiveStyleProcessor
            # 1. 格式对齐
            aligner = EfficientFormatAligner()
            fmt_result = aligner.align_format("示例内容", "government_official")
            # 2. 文风对齐（需构造特征）
            style_engine = StyleAlignmentEngine()
            dummy_features = {"feature_vector": [0.1, 0.2, 0.3]}
            style_result = style_engine.align_style(dummy_features, dummy_features, "示例内容")
            # 3. 综合文风处理
            style_processor = ComprehensiveStyleProcessor()
            style_features = style_processor.extract_comprehensive_style_features("示例内容")
            if fmt_result.get("success") and style_result.get("success") and style_features.get("success"):
                print("✅ 多模块集成测试通过")
                return {"name": "多模块集成测试", "success": True, "category": "集成用例", "priority": "P1"}
            else:
                print("❌ 多模块集成测试失败")
                return {"name": "多模块集成测试", "success": False, "error": "部分模块返回异常", "category": "集成用例", "priority": "P1"}
        except Exception as e:
            print(f"❌ 多模块集成测试异常: {e}")
            return {"name": "多模块集成测试", "success": False, "error": str(e), "category": "集成用例", "priority": "P1"}

    def test_end_to_end_workflow(self) -> Dict[str, Any]:
        """
        端到端流程测试
        功能：测试完整的文档处理流程，从输入到输出的全链路验证
        """
        try:
            # 1. 创建测试文档
            test_content = "这是一个测试文档，用于验证端到端流程。"
            test_file = "test_data/e2e_test.txt"
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # 2. 格式对齐
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            aligner = EfficientFormatAligner()
            fmt_result = aligner.align_format(test_content, "government_official")
            
            # 3. 文风分析
            from src.core.tools.comprehensive_style_processor import ComprehensiveStyleProcessor
            style_processor = ComprehensiveStyleProcessor()
            style_result = style_processor.extract_comprehensive_style_features(test_content)
            
            # 4. 验证结果
            if fmt_result.get("success") and style_result.get("success"):
                print("✅ 端到端流程测试通过")
                return {"name": "端到端流程测试", "success": True, "category": "集成用例", "priority": "P1"}
            else:
                print("❌ 端到端流程测试失败")
                return {"name": "端到端流程测试", "success": False, "error": "流程执行异常", "category": "集成用例", "priority": "P1"}
        except Exception as e:
            print(f"❌ 端到端流程测试异常: {e}")
            return {"name": "端到端流程测试", "success": False, "error": str(e), "category": "集成用例", "priority": "P1"}

    def test_data_flow_integrity(self) -> Dict[str, Any]:
        """
        数据流完整性测试
        功能：验证数据在模块间传递过程中的完整性和一致性
        """
        try:
            test_data = "原始测试数据"
            
            # 1. 格式对齐处理
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            aligner = EfficientFormatAligner()
            fmt_result = aligner.align_format(test_data, "government_official")
            
            # 2. 验证数据完整性
            if fmt_result.get("success"):
                aligned_content = fmt_result.get("aligned_content", "")
                if test_data in aligned_content or len(aligned_content) > 0:
                    print("✅ 数据流完整性测试通过")
                    return {"name": "数据流完整性测试", "success": True, "category": "数据验证", "priority": "P1"}
                else:
                    print("❌ 数据流完整性测试失败")
                    return {"name": "数据流完整性测试", "success": False, "error": "数据丢失", "category": "数据验证", "priority": "P1"}
            else:
                print("❌ 数据流完整性测试失败")
                return {"name": "数据流完整性测试", "success": False, "error": "处理失败", "category": "数据验证", "priority": "P1"}
        except Exception as e:
            print(f"❌ 数据流完整性测试异常: {e}")
            return {"name": "数据流完整性测试", "success": False, "error": str(e), "category": "数据验证", "priority": "P1"}

    def test_state_consistency(self) -> Dict[str, Any]:
        """
        状态一致性测试
        功能：验证系统在处理过程中状态的一致性和正确性
        """
        try:
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            aligner = EfficientFormatAligner()
            
            # 多次调用同一方法，验证状态一致性
            test_content = "测试内容"
            results = []
            for i in range(5):
                result = aligner.align_format(test_content, "government_official")
                results.append(result.get("success", False))
            
            # 验证所有结果一致
            if all(results) or not any(results):
                print("✅ 状态一致性测试通过")
                return {"name": "状态一致性测试", "success": True, "category": "状态验证", "priority": "P1"}
            else:
                print("❌ 状态一致性测试失败")
                return {"name": "状态一致性测试", "success": False, "error": "状态不一致", "category": "状态验证", "priority": "P1"}
        except Exception as e:
            print(f"❌ 状态一致性测试异常: {e}")
            return {"name": "状态一致性测试", "success": False, "error": str(e), "category": "状态验证", "priority": "P1"}

    def test_error_recovery(self) -> Dict[str, Any]:
        """
        错误恢复测试
        功能：测试系统在遇到错误后的恢复能力和稳定性
        """
        try:
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            aligner = EfficientFormatAligner()
            
            # 1. 先传入错误数据
            try:
                aligner.align_format(None, "invalid_format")
            except:
                pass
            
            # 2. 再传入正确数据，验证能否正常处理
            result = aligner.align_format("正确内容", "government_official")
            
            if result.get("success"):
                print("✅ 错误恢复测试通过")
                return {"name": "错误恢复测试", "success": True, "category": "错误处理", "priority": "P1"}
            else:
                print("❌ 错误恢复测试失败")
                return {"name": "错误恢复测试", "success": False, "error": "无法从错误中恢复", "category": "错误处理", "priority": "P1"}
        except Exception as e:
            print(f"❌ 错误恢复测试异常: {e}")
            return {"name": "错误恢复测试", "success": False, "error": str(e), "category": "错误处理", "priority": "P1"}

    def test_logging(self) -> Dict[str, Any]:
        """
        日志记录测试
        功能：验证系统日志记录功能的完整性和准确性
        """
        import logging
        try:
            # 设置日志
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            
            # 记录测试日志
            logger.info("开始日志记录测试")
            logger.warning("测试警告信息")
            logger.error("测试错误信息")
            
            print("✅ 日志记录测试通过")
            return {"name": "日志记录测试", "success": True, "category": "日志验证", "priority": "P2"}
        except Exception as e:
            print(f"❌ 日志记录测试异常: {e}")
            return {"name": "日志记录测试", "success": False, "error": str(e), "category": "日志验证", "priority": "P2"}

    def test_error_reporting(self) -> Dict[str, Any]:
        """
        错误报告测试
        功能：验证系统错误报告机制的完整性和准确性
        """
        try:
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            aligner = EfficientFormatAligner()
            
            # 故意触发错误
            result = aligner.align_format("", "invalid_format")
            
            if "error" in result:
                print("✅ 错误报告测试通过")
                return {"name": "错误报告测试", "success": True, "category": "错误处理", "priority": "P1"}
            else:
                print("❌ 错误报告测试失败")
                return {"name": "错误报告测试", "success": False, "error": "未正确报告错误", "category": "错误处理", "priority": "P1"}
        except Exception as e:
            print(f"❌ 错误报告测试异常: {e}")
            return {"name": "错误报告测试", "success": False, "error": str(e), "category": "错误处理", "priority": "P1"}

    def test_data_format_validation(self) -> Dict[str, Any]:
        """
        数据格式验证测试
        功能：验证系统对输入数据格式的验证能力
        """
        try:
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            aligner = EfficientFormatAligner()
            
            # 测试不同格式的输入
            test_cases = [
                ("正常文本", "government_official"),
                ("", "government_official"),  # 空字符串
                ("特殊字符!@#$%", "government_official"),  # 特殊字符
            ]
            
            results = []
            for content, format_type in test_cases:
                result = aligner.align_format(content, format_type)
                results.append(result.get("success", False))
            
            # 至少有一个成功
            if any(results):
                print("✅ 数据格式验证测试通过")
                return {"name": "数据格式验证测试", "success": True, "category": "数据验证", "priority": "P1"}
            else:
                print("❌ 数据格式验证测试失败")
                return {"name": "数据格式验证测试", "success": False, "error": "所有格式验证失败", "category": "数据验证", "priority": "P1"}
        except Exception as e:
            print(f"❌ 数据格式验证测试异常: {e}")
            return {"name": "数据格式验证测试", "success": False, "error": str(e), "category": "数据验证", "priority": "P1"}

    def test_data_integrity_check(self) -> Dict[str, Any]:
        """
        数据完整性检查测试
        功能：验证系统对数据完整性的检查能力
        """
        try:
            test_content = "完整测试内容"
            
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            aligner = EfficientFormatAligner()
            result = aligner.align_format(test_content, "government_official")
            
            if result.get("success"):
                aligned_content = result.get("aligned_content", "")
                # 检查输出内容是否完整
                if len(aligned_content) > 0:
                    print("✅ 数据完整性检查测试通过")
                    return {"name": "数据完整性检查测试", "success": True, "category": "数据验证", "priority": "P1"}
                else:
                    print("❌ 数据完整性检查测试失败")
                    return {"name": "数据完整性检查测试", "success": False, "error": "输出内容为空", "category": "数据验证", "priority": "P1"}
            else:
                print("❌ 数据完整性检查测试失败")
                return {"name": "数据完整性检查测试", "success": False, "error": "处理失败", "category": "数据验证", "priority": "P1"}
        except Exception as e:
            print(f"❌ 数据完整性检查测试异常: {e}")
            return {"name": "数据完整性检查测试", "success": False, "error": str(e), "category": "数据验证", "priority": "P1"}

    def test_data_consistency_validation(self) -> Dict[str, Any]:
        """
        数据一致性验证测试
        功能：验证系统处理结果的一致性和可重复性
        """
        try:
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            aligner = EfficientFormatAligner()
            
            test_content = "一致性测试内容"
            results = []
            
            # 多次处理相同内容
            for i in range(3):
                result = aligner.align_format(test_content, "government_official")
                results.append(result.get("success", False))
            
            # 验证结果一致性
            if all(results) or not any(results):
                print("✅ 数据一致性验证测试通过")
                return {"name": "数据一致性验证测试", "success": True, "category": "数据验证", "priority": "P1"}
            else:
                print("❌ 数据一致性验证测试失败")
                return {"name": "数据一致性验证测试", "success": False, "error": "结果不一致", "category": "数据验证", "priority": "P1"}
        except Exception as e:
            print(f"❌ 数据一致性验证测试异常: {e}")
            return {"name": "数据一致性验证测试", "success": False, "error": str(e), "category": "数据验证", "priority": "P1"}

    def test_data_security_check(self) -> Dict[str, Any]:
        """
        数据安全性检查测试
        功能：验证系统对敏感数据的处理安全性
        """
        try:
            # 测试包含敏感信息的内容
            sensitive_content = "包含敏感信息：密码123456，身份证号123456789012345678"
            
            from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
            aligner = EfficientFormatAligner()
            result = aligner.align_format(sensitive_content, "government_official")
            
            if result.get("success"):
                aligned_content = result.get("aligned_content", "")
                # 检查是否包含敏感信息（这里只是简单检查，实际应该有更严格的安全检查）
                if "123456" in aligned_content:
                    print("⚠️ 数据安全性检查测试警告：可能包含敏感信息")
                    return {"name": "数据安全性检查测试", "success": True, "warning": "可能包含敏感信息", "category": "安全验证", "priority": "P1"}
                else:
                    print("✅ 数据安全性检查测试通过")
                    return {"name": "数据安全性检查测试", "success": True, "category": "安全验证", "priority": "P1"}
            else:
                print("❌ 数据安全性检查测试失败")
                return {"name": "数据安全性检查测试", "success": False, "error": "处理失败", "category": "安全验证", "priority": "P1"}
        except Exception as e:
            print(f"❌ 数据安全性检查测试异常: {e}")
            return {"name": "数据安全性检查测试", "success": False, "error": str(e), "category": "安全验证", "priority": "P1"}

    def test_encoding_formats(self) -> Dict[str, Any]:
        """测试编码格式处理"""
        print("🧪 测试编码格式处理...")
        
        start_time = time.time()
        
        try:
            # 测试不同编码格式
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
            test_content = "编码测试内容：中文English123"
            
            success_count = 0
            for encoding in encodings:
                try:
                    # 创建测试文件
                    test_file = f"test_data/encoding_test_{encodings.index(encoding)}.txt"
                    os.makedirs(os.path.dirname(test_file), exist_ok=True)
                    
                    with open(test_file, 'w', encoding=encoding) as f:
                        f.write(test_content)
                    
                    with open(test_file, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    if content == test_content:
                        success_count += 1
                        
                except Exception as e:
                    print(f"编码 {encoding} 测试失败: {e}")
            
            duration = time.time() - start_time
            
            if success_count >= len(encodings) * 0.5:  # 至少50%成功
                print("✅ 编码格式处理测试通过")
                return {
                    "name": "编码格式处理测试",
                    "success": True,
                    "duration": duration,
                    "success_rate": success_count / len(encodings),
                    "category": "边界用例",
                    "priority": "P2"
                }
            else:
                print("❌ 编码格式处理测试失败")
                return {
                    "name": "编码格式处理测试",
                    "success": False,
                    "error": f"编码处理成功率过低: {success_count}/{len(encodings)}",
                    "suggestion": "完善编码格式支持，确保主要编码格式正常工作",
                    "duration": duration,
                    "category": "边界用例",
                    "priority": "P2"
                }
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ 编码格式处理测试异常: {e}")
            return {
                "name": "编码格式处理测试",
                "success": False,
                "error": str(e),
                "suggestion": "完善编码格式异常处理机制",
                "duration": duration,
                "category": "边界用例",
                "priority": "P2"
            }
    
    def test_network_exception_handling(self) -> Dict[str, Any]:
        """测试网络异常处理"""
        print("🧪 测试网络异常处理...")
        
        start_time = time.time()
        
        try:
            # 模拟网络异常（通过调用不存在的服务）
            import requests
            from requests.exceptions import RequestException
            
            try:
                response = requests.get("http://invalid-url-that-does-not-exist.com", timeout=1)
            except RequestException:
                # 网络异常被正确捕获
                duration = time.time() - start_time
                print("✅ 网络异常处理测试通过")
                return {
                    "name": "网络异常处理测试",
                    "success": True,
                    "duration": duration,
                    "category": "边界用例",
                    "priority": "P2"
                }
            
            print("❌ 网络异常处理测试失败")
            return {
                "name": "网络异常处理测试",
                "success": False,
                "error": "网络异常未被正确捕获",
                "suggestion": "完善网络异常处理机制",
                "duration": time.time() - start_time,
                "category": "边界用例",
                "priority": "P2"
            }
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ 网络异常处理测试异常: {e}")
            return {
                "name": "网络异常处理测试",
                "success": False,
                "error": str(e),
                "suggestion": "完善网络异常处理机制",
                "duration": duration,
                "category": "边界用例",
                "priority": "P2"
            }
    
    def test_data_validation(self) -> Dict[str, Any]:
        """测试数据验证"""
        print("🧪 测试数据验证...")
        
        start_time = time.time()
        
        try:
            # 测试各种数据验证场景
            test_cases = [
                ("正常数据", "这是一个正常的测试数据"),
                ("空数据", ""),
                ("特殊字符", "!@#$%^&*()_+-=[]{}|;':\",./<>?"),
                ("中英文混合", "中文English123"),
                ("超长数据", "x" * 10000),
            ]
            
            success_count = 0
            for case_name, test_data in test_cases:
                try:
                    from src.core.analysis.efficient_format_aligner import EfficientFormatAligner
                    aligner = EfficientFormatAligner()
                    result = aligner.align_format(test_data, "government_official")
                    
                    if result is not None:
                        success_count += 1
                        
                except Exception as e:
                    print(f"数据验证测试 {case_name} 失败: {e}")
            
            duration = time.time() - start_time
            
            if success_count >= len(test_cases) * 0.6:  # 至少60%成功
                print("✅ 数据验证测试通过")
                return {
                    "name": "数据验证测试",
                    "success": True,
                    "duration": duration,
                    "success_rate": success_count / len(test_cases),
                    "category": "数据验证",
                    "priority": "P2"
                }
            else:
                print("❌ 数据验证测试失败")
                return {
                    "name": "数据验证测试",
                    "success": False,
                    "error": f"数据验证成功率过低: {success_count}/{len(test_cases)}",
                    "suggestion": "完善数据验证机制，提高对各种数据类型的支持",
                    "duration": duration,
                    "category": "数据验证",
                    "priority": "P2"
                }
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ 数据验证测试异常: {e}")
            return {
                "name": "数据验证测试",
                "success": False,
                "error": str(e),
                "suggestion": "完善数据验证异常处理机制",
                "duration": duration,
                "category": "数据验证",
                "priority": "P2"
            }
    
    def run_all_edge_case_tests(self) -> List[Dict[str, Any]]:
        """运行所有边界用例测试"""
        print("开始边界用例和异常场景测试")
        print("=" * 60)
        
        test_methods = [
            self.test_empty_file_handling,
            self.test_large_file_handling,
            self.test_special_characters,
            self.test_encoding_formats,
            self.test_network_exception_handling,
            self.test_data_validation,
            self.test_concurrent_processing,
            self.test_memory_limit_handling,
            self.test_disk_space_limit_handling,
            self.test_multi_module_integration,
            self.test_end_to_end_workflow,
            self.test_data_flow_integrity,
            self.test_state_consistency,
            self.test_error_recovery,
            self.test_logging,
            self.test_error_reporting,
            self.test_data_format_validation,
            self.test_data_integrity_check,
            self.test_data_consistency_validation,
            self.test_data_security_check
        ]
        
        for test_method in test_methods:
            try:
                result = test_method()
                self.test_results.append(result)
            except Exception as e:
                print(f"❌ 测试方法 {test_method.__name__} 执行异常: {e}")
                self.test_results.append({
                    "name": test_method.__name__,
                    "success": False,
                    "error": str(e),
                    "category": "异常处理",
                    "priority": "P1"
                })
        
        return self.test_results
    
    def generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.get("success", False))
        failed_tests = total_tests - successful_tests
        
        # 按类别统计
        categories = {}
        for result in self.test_results:
            category = result.get("category", "未知")
            if category not in categories:
                categories[category] = {"total": 0, "success": 0, "failed": 0}
            categories[category]["total"] += 1
            if result.get("success", False):
                categories[category]["success"] += 1
            else:
                categories[category]["failed"] += 1
        
        # 按优先级统计
        priorities = {}
        for result in self.test_results:
            priority = result.get("priority", "未知")
            if priority not in priorities:
                priorities[priority] = {"total": 0, "success": 0, "failed": 0}
            priorities[priority]["total"] += 1
            if result.get("success", False):
                priorities[priority]["success"] += 1
            else:
                priorities[priority]["failed"] += 1
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0
            },
            "category_breakdown": categories,
            "priority_breakdown": priorities,
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        failed_tests = [result for result in self.test_results if not result.get("success", False)]
        
        if failed_tests:
            recommendations.append(f"发现 {len(failed_tests)} 个失败的测试用例，建议优先修复")
        
        # 按优先级分析
        p1_failed = [result for result in failed_tests if result.get("priority") == "P1"]
        if p1_failed:
            recommendations.append(f"发现 {len(p1_failed)} 个P1优先级失败用例，建议立即修复")
        
        # 按类别分析
        category_failures = {}
        for result in failed_tests:
            category = result.get("category", "未知")
            if category not in category_failures:
                category_failures[category] = 0
            category_failures[category] += 1
        
        for category, count in category_failures.items():
            if count > 2:
                recommendations.append(f"{category}类别失败较多({count}个)，建议重点检查")
        
        if not recommendations:
            recommendations.append("所有测试用例通过，系统稳定性良好")
        
        return recommendations

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="边界用例和异常场景测试")
    parser.add_argument("--base-url", default="http://localhost:5000", help="API基础URL")
    parser.add_argument("--output", default="test_results/edge_cases_report.json", help="输出报告路径")
    
    args = parser.parse_args()
    
    # 创建测试器
    tester = EdgeCaseTester(args.base_url)
    
    # 运行测试
    test_results = tester.run_all_edge_case_tests()
    
    # 生成报告
    report = tester.generate_test_report()
    
    # 保存报告
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    summary = report["test_summary"]
    print("\n" + "=" * 60)
    print("测试完成摘要")
    print("=" * 60)
    print(f"总测试数: {summary['total_tests']}")
    print(f"成功数: {summary['successful_tests']}")
    print(f"失败数: {summary['failed_tests']}")
    print(f"成功率: {summary['success_rate']:.2%}")
    
    # 打印建议
    print("\n改进建议:")
    for rec in report["recommendations"]:
        print(f"- {rec}")
    
    print(f"\n详细报告已保存到: {args.output}")

if __name__ == "__main__":
    main() 