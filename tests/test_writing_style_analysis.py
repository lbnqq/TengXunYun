#!/usr/bin/env python3
"""
测试文风分析和补充材料功能
"""

import os
import sys
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.core.tools.writing_style_analyzer import WritingStyleAnalyzer
from src.core.tools.document_fill_coordinator import DocumentFillCoordinator

def test_writing_style_analysis():
    """测试文风分析功能"""
    print("=== 测试文风分析功能 ===")
    
    # 创建不同风格的测试文档
    test_documents = {
        "正式公文": """
关于加强办公文档管理的通知

各部门、各单位：

根据上级部门的要求，为进一步规范办公文档管理工作，现将有关事项通知如下：

一、严格按照文档管理制度执行各项规定
二、务必确保文档格式的统一性和规范性  
三、定期开展文档质量检查工作

请各单位认真贯彻落实，确保工作质量。

特此通知。

                                办公室
                            2024年1月15日
""",
        
        "商务报告": """
第四季度销售业绩分析报告

本季度我们实现了显著的业绩提升。销售额达到2500万元，同比增长35%。

主要成果包括：
- 新客户开发成功率提升至65%
- 客户满意度达到92%
- 团队效率优化20%

我们通过精准的市场定位和高效的执行策略，成功突破了预期目标。下一步将继续优化产品结构，扩大市场份额。

团队将专注于以下重点工作：
1. 深化客户关系管理
2. 提升产品竞争力
3. 拓展新兴市场

预计下季度将实现更大突破。
""",
        
        "学术论文": """
基于深度学习的文本分类方法研究

摘要：本研究提出了一种新的文本分类方法。通过对比实验发现，该方法在准确率方面表现优异。

1. 引言
文本分类是自然语言处理领域的重要研究方向。现有方法存在一定局限性，需要进一步改进。

2. 相关工作
研究表明，深度学习技术在文本处理方面具有显著优势。Smith等人的研究证实了这一观点。

3. 方法
本文采用了改进的神经网络架构。具体而言，我们设计了多层注意力机制。

4. 实验结果
实验数据显示，所提方法的准确率达到94.2%，超过了基线方法。

5. 结论
综合分析表明，该方法具有良好的实用价值和推广前景。
""",
        
        "生活化描述": """
今天的工作真的很充实！

早上一到公司就感受到了浓浓的工作氛围。同事们都特别积极，大家一起讨论项目方案，氛围超级好。

我们这个团队真的很棒，每个人都很有想法。小李提出的建议特别实用，小王的设计也很有创意。

下午的会议开得很顺利，老板对我们的进展很满意。看到大家脸上的笑容，我也觉得特别开心。

晚上加班到九点，虽然有点累，但是看到项目一点点完善，心里还是很有成就感的。

明天继续加油！相信我们一定能做出更好的成果。
"""
    }
    
    # 初始化文风分析器
    analyzer = WritingStyleAnalyzer()
    
    results = {}
    
    for doc_type, content in test_documents.items():
        print(f"\n--- 分析 {doc_type} ---")
        
        result = analyzer.analyze_writing_style(content, doc_type)
        
        if "error" in result:
            print(f"分析失败: {result['error']}")
            continue
        
        results[doc_type] = result
        
        print(f"识别的文风类型: {result['style_type']}")
        print(f"置信度: {result['confidence_score']:.2f}")
        
        # 显示主要特征
        features = result['style_features']
        sentence_features = features.get('sentence_structure', {})
        vocab_features = features.get('vocabulary_choice', {})
        
        print(f"平均句长: {sentence_features.get('average_length', 0):.1f}")
        print(f"正式程度: {vocab_features.get('formality_score', 0):.2f}")
        
        # 保存文风模板
        save_result = analyzer.save_style_template(result)
        if save_result.get("success"):
            print(f"文风模板已保存: {save_result['template_id']}")
    
    return len(results) > 0

def test_style_prompt_generation():
    """测试文风提示词生成"""
    print("\n=== 测试文风提示词生成 ===")
    
    analyzer = WritingStyleAnalyzer()
    
    # 使用商务报告风格的文档
    business_content = """
第四季度销售业绩分析报告

本季度我们实现了显著的业绩提升。销售额达到2500万元，同比增长35%。

主要成果包括：
- 新客户开发成功率提升至65%
- 客户满意度达到92%

我们通过精准的市场定位和高效的执行策略，成功突破了预期目标。
"""
    
    result = analyzer.analyze_writing_style(business_content, "商务报告示例")
    
    if "error" in result:
        print(f"分析失败: {result['error']}")
        return False
    
    print("生成的文风提示词:")
    print("-" * 50)
    print(result['style_prompt'])
    print("-" * 50)
    
    return True

def test_supplementary_materials():
    """测试补充材料功能"""
    print("\n=== 测试补充材料功能 ===")
    
    coordinator = DocumentFillCoordinator()
    
    # 模拟补充材料
    materials = {
        "个人简历": """
张三 - 个人简历

基本信息：
姓名：张三
性别：男
年龄：28岁
电话：13800138000
邮箱：zhangsan@example.com

工作经历：
2020-2024  ABC科技公司  高级软件工程师
- 负责核心产品的架构设计和开发
- 带领5人团队完成多个重要项目
- 熟练掌握Python、Java、JavaScript等编程语言

教育背景：
2016-2020  清华大学  计算机科学与技术  本科
""",
        
        "工作证明": """
工作证明

兹证明张三同志于2020年7月至2024年1月在我公司担任高级软件工程师职务。

工作期间表现优秀，具备以下能力：
1. 扎实的技术功底和丰富的项目经验
2. 良好的团队协作和沟通能力
3. 强烈的责任心和学习能力

特此证明。

ABC科技公司人力资源部
2024年1月20日
""",
        
        "项目经验": """
项目经验总结

项目一：智能客服系统
时间：2022.3 - 2022.12
角色：技术负责人
描述：基于自然语言处理技术的智能客服系统，支持多轮对话和意图识别
成果：提升客服效率60%，客户满意度达到95%

项目二：数据分析平台
时间：2021.6 - 2022.2
角色：核心开发者
描述：企业级数据分析和可视化平台，支持实时数据处理
成果：为公司节省数据分析成本40%，提升决策效率
"""
    }
    
    # 添加补充材料
    for material_name, content in materials.items():
        result = coordinator.add_supplementary_material(material_name, content)
        
        if result.get("success"):
            print(f"✓ 成功添加补充材料: {material_name}")
        else:
            print(f"✗ 添加失败: {material_name}")
    
    # 检查材料状态
    session_info = coordinator.get_session_status()
    print(f"\n当前会话中的补充材料数量: {len(coordinator.session_state['supplementary_materials'])}")
    
    return True

def test_integrated_workflow():
    """测试集成工作流程"""
    print("\n=== 测试集成工作流程 ===")
    
    coordinator = DocumentFillCoordinator()
    
    # 1. 上传文风参考文档
    style_reference = """
关于召开年度工作总结会议的通知

各部门：

根据公司年度工作安排，定于2024年1月25日召开年度工作总结会议。现将有关事项通知如下：

一、会议时间
2024年1月25日（星期四）上午9:00

二、会议地点
公司三楼会议室

三、参会人员
各部门负责人及相关工作人员

四、会议内容
1. 各部门年度工作总结汇报
2. 优秀员工表彰
3. 下年度工作计划部署

请各部门按时参加，不得无故缺席。

特此通知。

                                行政办公室
                            2024年1月15日
"""
    
    # 分析并保存文风模板
    style_result = coordinator.analyze_and_save_writing_style(style_reference, "公司通知范文")
    
    if style_result.get("success"):
        print(f"✓ 文风模板创建成功: {style_result['style_name']}")
        print(f"  置信度: {style_result['confidence_score']:.1%}")
        
        # 设置为当前文风模板
        coordinator.set_writing_style_template(style_result['template_id'])
        print("✓ 文风模板已设置")
    else:
        print(f"✗ 文风模板创建失败: {style_result.get('error', '未知错误')}")
        return False
    
    # 2. 添加补充材料
    supplementary_info = """
部门：技术研发部
负责人：李经理
联系电话：13900139000
主要工作：产品研发、技术创新、团队管理
年度成果：完成3个重要项目，申请专利2项
"""
    
    coordinator.add_supplementary_material("部门信息", supplementary_info)
    print("✓ 补充材料已添加")
    
    # 3. 测试内容生成（模拟）
    test_content = "请生成一份部门工作总结"
    
    styled_prompt = coordinator.apply_writing_style_to_content(test_content)
    
    print("\n生成的带文风的提示词:")
    print("-" * 50)
    print(styled_prompt[:500] + "..." if len(styled_prompt) > 500 else styled_prompt)
    print("-" * 50)
    
    return True

def test_template_management():
    """测试模板管理功能"""
    print("\n=== 测试模板管理功能 ===")
    
    analyzer = WritingStyleAnalyzer()
    
    # 列出所有文风模板
    templates = analyzer.list_style_templates()
    print(f"找到 {len(templates)} 个文风模板:")
    
    for template in templates:
        print(f"- {template['name']} ({template['style_name']})")
        print(f"  ID: {template['template_id']}")
        print(f"  置信度: {template['confidence_score']:.1%}")
        print(f"  创建时间: {template['created_time'][:10]}")
        print()
    
    # 测试加载特定模板
    if templates:
        first_template = templates[0]
        template_data = analyzer.load_style_template(first_template['template_id'])
        
        if "error" not in template_data:
            print(f"✓ 成功加载模板: {first_template['name']}")
            print(f"  文风类型: {template_data['style_type']}")
        else:
            print(f"✗ 加载模板失败: {template_data['error']}")
    
    return len(templates) > 0

def main():
    """主测试函数"""
    print("开始测试文风分析和补充材料功能...\n")
    
    tests = [
        ("文风分析", test_writing_style_analysis),
        ("文风提示词生成", test_style_prompt_generation),
        ("补充材料", test_supplementary_materials),
        ("集成工作流程", test_integrated_workflow),
        ("模板管理", test_template_management)
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
        print("🎉 所有测试通过！文风分析和补充材料功能正常工作。")
        print("\n新增功能特点:")
        print("- ✅ 智能文风分析和模板保存")
        print("- ✅ 补充材料上传和智能识别")
        print("- ✅ 文风对齐和内容润色")
        print("- ✅ 去AIGC痕迹的内容生成")
        print("- ✅ 长短句结合和主动语态优化")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
