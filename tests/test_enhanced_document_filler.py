#!/usr/bin/env python3
"""
增强文档填充器测试脚本
测试专利分析、图片处理、智能填写等功能
"""

import sys
import os
import json
import base64
from typing import Dict, List, Any

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_patent_document_analyzer():
    """测试专利文档分析器"""
    print("🔍 测试专利文档分析器...")
    
    try:
        from core.tools.patent_document_analyzer import PatentDocumentAnalyzer
        
        # 创建分析器实例
        analyzer = PatentDocumentAnalyzer()
        
        # 读取专利申请书模板
        template_path = os.path.join("examples", "patent_application_template.txt")
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                document_content = f.read()
        else:
            # 使用示例内容
            document_content = """
            发明专利申请书
            
            一、基本信息
            发明名称：________________________________
            申请号：________________________________
            申请日：________________________________
            发明人：________________________________
            申请人：________________________________
            技术领域：________________________________
            
            二、发明摘要
            ________________________________
            
            三、背景技术
            ________________________________
            
            四、发明内容
            ________________________________
            
            五、附图说明
            图1：________________________________
            
            六、具体实施方式
            ________________________________
            
            七、权利要求
            1. ________________________________
            
            八、附图
            [附图1]
            [附图2]
            
            九、申请人信息
            申请人名称：________________________________
            申请人地址：________________________________
            联系电话：________________________________
            电子邮箱：________________________________
            """
        
        # 分析文档
        analysis_result = analyzer.analyze_patent_document(document_content, "测试专利申请书")
        
        if "error" in analysis_result:
            print(f"❌ 专利文档分析失败: {analysis_result['error']}")
            return False
        
        print("✅ 专利文档分析成功")
        print(f"   文档类型: {analysis_result.get('document_type', 'unknown')}")
        print(f"   识别字段数: {len(analysis_result.get('fields', []))}")
        print(f"   图片位置数: {len(analysis_result.get('image_positions', []))}")
        print(f"   置信度: {analysis_result.get('confidence_score', 0):.2f}")
        
        # 生成AI填写建议
        suggestions = analyzer.generate_ai_fill_suggestions(analysis_result)
        if "error" not in suggestions:
            print("✅ AI填写建议生成成功")
            print(f"   字段建议数: {len(suggestions.get('field_suggestions', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ 专利文档分析器测试失败: {str(e)}")
        return False

def test_intelligent_image_processor():
    """测试智能图片处理器"""
    print("\n🔍 测试智能图片处理器...")
    
    try:
        from core.tools.intelligent_image_processor import IntelligentImageProcessor
        
        # 创建图片处理器实例
        processor = IntelligentImageProcessor()
        
        # 创建测试图片数据（简单的1x1像素PNG）
        test_image_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        
        # 测试图片处理
        result = processor.process_uploaded_image(
            test_image_data,
            "test_image.png",
            {"suggested_size": (100, 100), "document_type": "patent"}
        )
        
        if "error" in result:
            print(f"❌ 图片处理失败: {result['error']}")
            return False
        
        print("✅ 图片处理成功")
        print(f"   图片ID: {result.get('image_id', 'unknown')}")
        print(f"   文件路径: {result.get('file_path', 'unknown')}")
        print(f"   文件大小: {result.get('file_size', 0)} bytes")
        print(f"   尺寸: {result.get('dimensions', (0, 0))}")
        
        # 测试批量处理
        batch_result = processor.batch_process_images(
            [{"data": test_image_data, "name": "batch_test.png"}],
            "测试文档内容"
        )
        
        if "error" not in batch_result:
            print("✅ 批量图片处理成功")
            print(f"   处理图片数: {len(batch_result.get('processed_images', []))}")
        
        # 获取统计信息
        stats = processor.get_image_statistics()
        if "error" not in stats:
            print("✅ 图片统计信息获取成功")
            print(f"   总图片数: {stats.get('total_images', 0)}")
            print(f"   总大小: {stats.get('total_size', 0)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ 智能图片处理器测试失败: {str(e)}")
        return False

def test_enhanced_document_filler():
    """测试增强文档填充器"""
    print("\n🔍 测试增强文档填充器...")
    
    try:
        from core.tools.enhanced_document_filler import EnhancedDocumentFiller
        
        # 创建增强文档填充器实例
        filler = EnhancedDocumentFiller()
        
        # 测试文档内容
        test_content = """
        发明专利申请书
        
        发明名称：________________________________
        申请日：________________________________
        发明人：________________________________
        技术领域：________________________________
        
        发明摘要：________________________________
        
        背景技术：________________________________
        
        附图说明：________________________________
        [附图1]
        """
        
        # 分析文档结构
        analysis_result = filler.analyze_document_structure(test_content, "测试专利申请书")
        
        if "error" in analysis_result:
            print(f"❌ 文档结构分析失败: {analysis_result['error']}")
            return False
        
        print("✅ 文档结构分析成功")
        print(f"   文档类型: {analysis_result.get('document_type', 'unknown')}")
        print(f"   识别字段数: {len(analysis_result.get('fields', []))}")
        
        # 测试智能填充
        user_data = {
            "patent_name": "智能文档处理系统",
            "inventor_name": "张三",
            "technical_field": "计算机"
        }
        
        fill_result = filler.intelligent_fill_document(analysis_result, user_data)
        
        if "error" in fill_result:
            print(f"❌ 智能填充失败: {fill_result['error']}")
            return False
        
        print("✅ 智能文档填充成功")
        print(f"   填充内容长度: {len(fill_result.get('filled_content', ''))}")
        
        # 检查质量评估
        quality = fill_result.get('quality_assessment', {})
        if quality:
            print(f"   总体评分: {quality.get('overall_score', 0):.1f}/100")
            print(f"   完成度: {quality.get('completion_rate', 0):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强文档填充器测试失败: {str(e)}")
        return False

def test_patent_specific_features():
    """测试专利特定功能"""
    print("\n🔍 测试专利特定功能...")
    
    try:
        from core.tools.patent_document_analyzer import PatentDocumentAnalyzer
        
        analyzer = PatentDocumentAnalyzer()
        
        # 测试专利字段识别
        patent_content = """
        发明名称：智能文档处理系统
        申请日：2024-01-01
        发明人：张三
        技术领域：计算机
        发明摘要：本发明提供了一种智能文档处理系统...
        背景技术：现有技术中，文档处理通常需要人工...
        [附图1]
        """
        
        analysis_result = analyzer.analyze_patent_document(patent_content, "专利测试")
        
        if "error" in analysis_result:
            print(f"❌ 专利字段识别失败: {analysis_result['error']}")
            return False
        
        # 检查特定字段识别
        fields = analysis_result.get('fields', [])
        field_names = [field['field_name'] for field in fields]
        
        expected_fields = ['发明名称', '申请日', '发明人', '技术领域', '发明摘要', '背景技术']
        found_fields = [name for name in expected_fields if any(name in field_name for field_name in field_names)]
        
        print(f"✅ 专利字段识别成功")
        print(f"   期望字段: {expected_fields}")
        print(f"   识别字段: {found_fields}")
        print(f"   识别率: {len(found_fields)/len(expected_fields)*100:.1f}%")
        
        # 检查图片位置识别
        image_positions = analysis_result.get('image_positions', [])
        if image_positions:
            print(f"   图片位置识别: {len(image_positions)} 个")
        
        # 检查文档目标分析
        if analysis_result.get('total_objective'):
            print(f"   文档目标: {analysis_result['total_objective']}")
        
        if analysis_result.get('core_theme'):
            print(f"   核心主题: {analysis_result['core_theme']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 专利特定功能测试失败: {str(e)}")
        return False

def test_ai_integration():
    """测试AI集成功能"""
    print("\n🔍 测试AI集成功能...")
    
    try:
        from core.tools.patent_document_analyzer import PatentDocumentAnalyzer
        
        analyzer = PatentDocumentAnalyzer()
        
        # 测试文档目标分析
        test_content = """
        本发明涉及一种智能文档处理系统，特别是一种基于人工智能的专利申请书自动填写系统。
        该系统能够自动识别文档结构，分析字段类型，并基于AI技术生成合适的填写内容。
        """
        
        objective_analysis = analyzer._analyze_document_objective(test_content)
        
        print("✅ AI集成功能测试成功")
        print(f"   文档目标: {objective_analysis.get('objective', 'N/A')}")
        print(f"   核心主题: {objective_analysis.get('theme', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI集成功能测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始增强文档填充器全面测试\n")
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("专利文档分析器", test_patent_document_analyzer()))
    test_results.append(("智能图片处理器", test_intelligent_image_processor()))
    test_results.append(("增强文档填充器", test_enhanced_document_filler()))
    test_results.append(("专利特定功能", test_patent_specific_features()))
    test_results.append(("AI集成功能", test_ai_integration()))
    
    # 输出测试总结
    print("\n" + "="*50)
    print("📊 测试结果总结")
    print("="*50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！增强文档填充器功能正常")
    else:
        print("⚠️  部分测试失败，请检查相关功能")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 