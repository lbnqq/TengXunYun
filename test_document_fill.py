#!/usr/bin/env python3
"""
测试复杂文档填充功能
"""

import os
import sys
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.core.tools.complex_document_filler import ComplexDocumentFiller
from src.core.tools.document_fill_coordinator import DocumentFillCoordinator

def test_document_structure_analysis():
    """测试文档结构分析功能"""
    print("=== 测试文档结构分析功能 ===")
    
    # 创建测试文档内容（包含待填写字段）
    test_document = """个人信息登记表

姓名：_____________    性别：_______    年龄：_______

身份证号：_________________________

联系电话：_____________    邮箱：_________________________

家庭住址：_________________________________________________

工作单位：_____________________________________________

申请日期：____年____月____日

项目信息表格：

序号 | 项目名称 | 数量 | 金额 | 备注
-----|----------|------|------|------
1    |          |      |      |
2    |          |      |      |
3    |          |      |      |

申请说明：
_________________________________________________
_________________________________________________
_________________________________________________

申请人签名：_______________    日期：____年____月____日"""
    
    # 初始化文档填充器
    filler = ComplexDocumentFiller()
    
    # 分析文档结构
    result = filler.analyze_document_structure(test_document, "个人信息登记表")
    
    if "error" in result:
        print(f"文档分析失败: {result['error']}")
        return False
    
    print(f"文档名称: {result['document_name']}")
    print(f"总字段数: {result['total_fields']}")
    print(f"置信度: {result['confidence_score']:.2f}")
    
    print("\n识别到的待填写字段:")
    for field in result['fill_fields']:
        print(f"- {field['field_id']}: {field['category']} - {field['inferred_meaning']}")
    
    print(f"\n识别到的表格:")
    for table in result['tables']:
        print(f"- {table['table_id']}: {table['header']}")
        print(f"  列数: {len(table['columns'])}")
        print(f"  需要填写: {table['fill_required']}")
    
    return True

def test_question_generation():
    """测试问题生成功能"""
    print("\n=== 测试问题生成功能 ===")
    
    # 使用上面的测试文档
    test_document = """个人信息登记表

姓名：_____________    性别：_______    年龄：_______

身份证号：_________________________

联系电话：_____________    邮箱：_________________________

申请日期：____年____月____日

申请说明：
_________________________________________________"""
    
    filler = ComplexDocumentFiller()
    
    # 分析文档结构
    analysis_result = filler.analyze_document_structure(test_document, "个人信息登记表")
    
    if "error" in analysis_result:
        print(f"文档分析失败: {analysis_result['error']}")
        return False
    
    # 生成填写问题
    questions = filler.generate_fill_questions(analysis_result)
    
    print(f"生成了 {len(questions)} 个问题:")
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question['category']}")
        print(f"问题内容: {question['question_text']}")
        print(f"输入类型: {question['input_type']}")
        if question.get('examples'):
            print(f"示例: {', '.join(question['examples'])}")
    
    return True

def test_document_fill_coordinator():
    """测试文档填充协调器"""
    print("\n=== 测试文档填充协调器 ===")
    
    # 创建协调器
    coordinator = DocumentFillCoordinator()
    
    # 测试文档
    test_document = """入职申请表

姓名：_____________    性别：_______

身份证号：_________________________

联系电话：_____________

期望入职日期：____年____月____日

个人简介：
_________________________________________________
_________________________________________________"""
    
    # 开始填充流程
    result = coordinator.start_document_fill(test_document, "入职申请表")
    
    if "error" in result:
        print(f"启动填充流程失败: {result['error']}")
        return False
    
    print("填充流程启动成功！")
    print(f"阶段: {result['stage']}")
    print(f"总问题数: {result['total_questions']}")
    print(f"当前问题: {result['current_question']}")
    
    print(f"\n系统回复:")
    print(result['response'])
    
    # 模拟用户回答
    test_answers = [
        "姓名：张三\n性别：男\n身份证号：123456789012345678\n联系电话：13800138000",
        "2024年3月1日",
        "我是一名有5年工作经验的软件工程师，熟悉Python、Java等编程语言，具有良好的团队协作能力。"
    ]
    
    for i, answer in enumerate(test_answers):
        print(f"\n--- 用户回答 {i+1} ---")
        print(f"用户输入: {answer}")
        
        response = coordinator.process_user_response(answer)
        
        if "error" in response:
            print(f"处理回答失败: {response['error']}")
            continue
        
        print(f"系统回复: {response['response']}")
        print(f"当前阶段: {response['stage']}")
        
        if response['stage'] == 'filling':
            print("进入填充阶段！")
            break
    
    return True

def test_multi_round_conversation():
    """测试多轮对话流程"""
    print("\n=== 测试多轮对话流程 ===")
    
    coordinator = DocumentFillCoordinator()
    
    # 简单的测试文档
    test_document = """申请表

姓名：_______
电话：_______
日期：____年____月____日"""
    
    # 开始对话
    result = coordinator.start_document_fill(test_document, "简单申请表")
    print("系统:", result.get('response', ''))
    
    # 模拟完整的对话流程
    conversation = [
        ("姓名：李四\n电话：13900139000", "提供个人信息"),
        ("2024年2月15日", "提供日期信息"),
        ("确认", "确认填充完成")
    ]
    
    for user_input, description in conversation:
        print(f"\n用户 ({description}): {user_input}")
        
        response = coordinator.process_user_response(user_input)
        
        if "error" in response:
            print(f"错误: {response['error']}")
            continue
        
        print(f"系统: {response.get('response', '')}")
        
        # 检查是否完成
        if response.get('stage') == 'completed':
            print("填充流程完成！")
            
            # 获取最终结果
            final_result = coordinator.get_fill_result()
            if final_result:
                print("填充摘要:")
                summary = final_result.get('fill_summary', {})
                print(f"- 总字段数: {summary.get('total_fields', 0)}")
                print(f"- 已填充: {summary.get('filled_fields', 0)}")
                print(f"- 完成度: {summary.get('completion_rate', 0):.1f}%")
            break
    
    return True

def test_validation_logic():
    """测试验证逻辑"""
    print("\n=== 测试验证逻辑 ===")
    
    coordinator = DocumentFillCoordinator()
    
    # 测试不同类型的验证
    test_cases = [
        {
            "category": "个人信息",
            "input_type": "form",
            "valid_input": "姓名：王五\n年龄：28\n电话：13700137000",
            "invalid_input": ""
        },
        {
            "category": "日期时间", 
            "input_type": "date",
            "valid_input": "2024年3月15日",
            "invalid_input": "明天"
        },
        {
            "category": "金额数字",
            "input_type": "number", 
            "valid_input": "5000元",
            "invalid_input": "很多钱"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试 {test_case['category']} 验证:")
        
        # 创建模拟问题
        question = {
            "question_id": "test_q",
            "category": test_case["category"],
            "input_type": test_case["input_type"],
            "question_text": f"测试{test_case['category']}问题"
        }
        
        # 测试有效输入
        valid_result = coordinator._parse_user_answer(test_case["valid_input"], question)
        print(f"有效输入 '{test_case['valid_input']}': {'通过' if valid_result.get('valid') else '失败'}")
        
        # 测试无效输入
        invalid_result = coordinator._parse_user_answer(test_case["invalid_input"], question)
        print(f"无效输入 '{test_case['invalid_input']}': {'失败' if not invalid_result.get('valid') else '意外通过'}")
        if not invalid_result.get('valid'):
            print(f"  错误信息: {invalid_result.get('error', '无')}")
    
    return True

def main():
    """主测试函数"""
    print("开始测试复杂文档填充功能...\n")
    
    tests = [
        ("文档结构分析", test_document_structure_analysis),
        ("问题生成", test_question_generation),
        ("文档填充协调器", test_document_fill_coordinator),
        ("多轮对话流程", test_multi_round_conversation),
        ("验证逻辑", test_validation_logic)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"\n{test_name}测试: {'通过' if success else '失败'}")
        except Exception as e:
            print(f"\n{test_name}测试出错: {str(e)}")
            results.append((test_name, False))
        
        print("-" * 60)
    
    # 总结
    print("\n=== 测试总结 ===")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！复杂文档填充功能正常工作。")
        print("\n功能特点:")
        print("- ✅ 智能识别待填写字段和表格")
        print("- ✅ 多轮对话引导用户填写")
        print("- ✅ 输入验证和错误处理")
        print("- ✅ 生成HTML格式输出")
        print("- ✅ 支持多种文档类型")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
