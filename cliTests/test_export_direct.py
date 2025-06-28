#!/usr/bin/env python3
"""
直接测试export_styled_document方法
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.tools.writing_style_analyzer import WritingStyleAnalyzer

def test_export_direct():
    """直接测试导出功能"""
    try:
        # 初始化分析器
        analyzer = WritingStyleAnalyzer()
        
        # 使用一个已知的session_id
        session_id = "0c550b84-924f-4dde-aa4f-bb4fa996763e"  # 从之前的测试中获取
        
        print(f"测试导出session: {session_id}")
        
        # 直接调用导出方法
        result = analyzer.export_styled_document(session_id)
        
        print(f"导出结果类型: {type(result)}")
        print(f"导出结果键: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if "error" in result:
            print(f"导出失败: {result['error']}")
            return False
        
        if "docx_content" in result:
            docx_content = result["docx_content"]
            print(f"docx_content类型: {type(docx_content)}")
            print(f"docx_content长度: {len(docx_content)}")
            print(f"docx_content前20字节: {docx_content[:20]}")
            
            # 保存到文件
            output_file = f"test_export_direct_{session_id}.docx"
            with open(output_file, 'wb') as f:
                f.write(docx_content)
            print(f"已保存到: {output_file}")
            
            return True
        else:
            print(f"没有找到docx_content，结果: {result}")
            return False
            
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export_direct()
    print(f"测试结果: {'成功' if success else '失败'}") 