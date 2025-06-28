#!/usr/bin/env python3
"""
检查docx文件内容的简单脚本
"""
import sys
import os
from docx import Document

def check_docx_content(file_path):
    """检查docx文件内容"""
    try:
        doc = Document(file_path)
        print(f"文档段落数: {len(doc.paragraphs)}")
        print("前10段内容:")
        for i, para in enumerate(doc.paragraphs[:10]):
            if para.text.strip():
                print(f"{i+1}: {para.text}")
        print("...")
        
        # 检查是否有风格调整报告
        for i, para in enumerate(doc.paragraphs):
            if "风格调整报告" in para.text:
                print(f"\n找到风格调整报告在第{i+1}段")
                break
                
    except Exception as e:
        print(f"读取docx文件失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python check_docx.py <docx_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    check_docx_content(file_path) 