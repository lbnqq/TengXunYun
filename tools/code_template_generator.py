#!/usr/bin/env python3
"""
代码模板生成器

根据项目开发规范自动生成标准化的代码模板。
支持Python、JavaScript、HTML等多种文件类型的模板生成。

Author: AI Assistant (Claude)
Created: 2025-06-25
Last Modified: 2025-06-25
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class CodeTemplateGenerator:
    """
    代码模板生成器
    
    根据项目开发规范生成标准化的代码模板，确保所有代码文件
    都符合项目的格式和注释要求。
    
    Author: AI Assistant (Claude)
    Date: 2025-06-25
    AI Assisted: 是
    """
    
    def __init__(self, author_name: str = "开发者", ai_assisted: bool = False):
        """
        初始化模板生成器
        
        Args:
            author_name (str): 作者姓名
            ai_assisted (bool): 是否AI辅助开发
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        self.author_name = author_name
        self.ai_assisted = ai_assisted
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        
        # 模板配置
        self.templates = {
            'python_module': self._python_module_template,
            'python_class': self._python_class_template,
            'python_function': self._python_function_template,
            'javascript_module': self._javascript_module_template,
            'html_page': self._html_page_template,
            'markdown_doc': self._markdown_doc_template,
            'test_file': self._test_file_template
        }
    
    def _get_common_header(self, file_type: str, description: str) -> str:
        """
        生成通用文件头
        
        Args:
            file_type (str): 文件类型
            description (str): 文件描述
            
        Returns:
            str: 文件头内容
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        ai_info = "是 - Claude 3.5 Sonnet" if self.ai_assisted else "否"
        
        if file_type == 'python':
            return f'''#!/usr/bin/env python3
"""
{description}

Author: {self.author_name}
Created: {self.current_date}
Last Modified: {self.current_date}
Modified By: {self.author_name}
AI Assisted: {ai_info}
Version: v1.0
License: MIT
"""'''
        
        elif file_type == 'javascript':
            return f'''/**
 * {description}
 * 
 * @author {self.author_name}
 * @date {self.current_date}
 * @ai_assisted {ai_info}
 * @version v1.0
 * @license MIT
 */'''
        
        elif file_type == 'html':
            return f'''<!--
{description}

Author: {self.author_name}
Created: {self.current_date}
AI Assisted: {ai_info}
Version: v1.0
-->'''
        
        return f"# {description}\n\n**Author**: {self.author_name}  \n**Date**: {self.current_date}  \n**AI Assisted**: {ai_info}"
    
    def _python_module_template(self, module_name: str, description: str, **kwargs) -> str:
        """
        生成Python模块模板
        
        Args:
            module_name (str): 模块名称
            description (str): 模块描述
            
        Returns:
            str: Python模块模板
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        header = self._get_common_header('python', description)
        
        return f'''{header}

import os
import sys
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

class {module_name.replace('_', '').title()}:
    """
    {description}
    
    这是一个示例类，展示了项目规范要求的代码结构和注释格式。
    请根据实际需求修改类名、方法和属性。
    
    Attributes:
        attribute_name (type): 属性描述
    
    Author: {self.author_name}
    Date: {self.current_date}
    AI Assisted: {"是" if self.ai_assisted else "否"}
    """
    
    def __init__(self, param: str):
        """
        初始化{module_name.replace('_', '').title()}
        
        Args:
            param (str): 初始化参数描述
            
        Author: {self.author_name}
        Date: {self.current_date}
        AI Assisted: {"是" if self.ai_assisted else "否"}
        """
        self.param = param
        logger.info(f"{module_name.replace('_', '').title()} initialized with param: {{param}}")
    
    def example_method(self, input_data: Any) -> Dict[str, Any]:
        """
        示例方法
        
        详细描述方法的功能、算法逻辑和使用场景。
        
        Args:
            input_data (Any): 输入数据描述
        
        Returns:
            Dict[str, Any]: 返回值描述
        
        Raises:
            ValueError: 异常情况的描述
            
        Example:
            >>> obj = {module_name.replace('_', '').title()}("test")
            >>> result = obj.example_method("data")
            >>> print(result)
            {{'status': 'success', 'data': 'processed_data'}}
            
        Note:
            特殊说明或注意事项
            
        Author: {self.author_name}
        Date: {self.current_date}
        AI Assisted: {"是" if self.ai_assisted else "否"}
        """
        try:
            # ==================== 主要处理逻辑 ====================
            # 作者: {self.author_name}
            # 日期: {self.current_date}
            # AI辅助: {"是" if self.ai_assisted else "否"}
            # 描述: 在这里实现具体的业务逻辑
            
            processed_data = f"processed_{{input_data}}"
            
            return {{
                'status': 'success',
                'data': processed_data,
                'timestamp': datetime.now().isoformat()
            }}
            
        except Exception as e:
            logger.error(f"Error in example_method: {{e}}")
            raise ValueError(f"处理失败: {{e}}")

def main():
    """
    主函数
    
    Author: {self.author_name}
    Date: {self.current_date}
    AI Assisted: {"是" if self.ai_assisted else "否"}
    """
    # 示例用法
    obj = {module_name.replace('_', '').title()}("example")
    result = obj.example_method("test_data")
    print(f"Result: {{result}}")

if __name__ == "__main__":
    main()
'''
    
    def _python_class_template(self, class_name: str, description: str, **kwargs) -> str:
        """
        生成Python类模板
        
        Args:
            class_name (str): 类名
            description (str): 类描述
            
        Returns:
            str: Python类模板
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        return f'''class {class_name}:
    """
    {description}
    
    详细描述类的功能、用途和主要特性。
    
    Attributes:
        attribute_name (type): 属性描述
    
    Author: {self.author_name}
    Date: {self.current_date}
    AI Assisted: {"是" if self.ai_assisted else "否"}
    """
    
    def __init__(self, param: str):
        """
        初始化{class_name}
        
        Args:
            param (str): 参数描述
            
        Author: {self.author_name}
        Date: {self.current_date}
        AI Assisted: {"是" if self.ai_assisted else "否"}
        """
        self.param = param
    
    def method_name(self, input_param: Any) -> Any:
        """
        方法描述
        
        Args:
            input_param (Any): 参数描述
            
        Returns:
            Any: 返回值描述
            
        Author: {self.author_name}
        Date: {self.current_date}
        AI Assisted: {"是" if self.ai_assisted else "否"}
        """
        # TODO: 实现方法逻辑 - {self.author_name} {self.current_date}
        pass
'''
    
    def _javascript_module_template(self, module_name: str, description: str, **kwargs) -> str:
        """
        生成JavaScript模块模板
        
        Args:
            module_name (str): 模块名称
            description (str): 模块描述
            
        Returns:
            str: JavaScript模块模板
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        header = self._get_common_header('javascript', description)
        
        return f'''{header}

class {module_name.replace('_', '').title()} {{
  /**
   * 构造函数
   * @param {{string}} param - 参数描述
   * @author {self.author_name}
   * @date {self.current_date}
   * @ai_assisted {"是" if self.ai_assisted else "否"}
   */
  constructor(param) {{
    this.param = param;
    this.init();
  }}
  
  /**
   * 初始化方法
   * @author {self.author_name}
   * @date {self.current_date}
   * @ai_assisted {"是" if self.ai_assisted else "否"}
   */
  init() {{
    // TODO: 实现初始化逻辑 - {self.author_name} {self.current_date}
    console.log(`{module_name.replace('_', '').title()} initialized`);
  }}
  
  /**
   * 示例方法
   * @param {{any}} inputData - 输入数据
   * @returns {{Object}} 处理结果
   * @author {self.author_name}
   * @date {self.current_date}
   * @ai_assisted {"是" if self.ai_assisted else "否"}
   */
  exampleMethod(inputData) {{
    try {{
      // ==================== 主要处理逻辑 ====================
      // 作者: {self.author_name}
      // 日期: {self.current_date}
      // AI辅助: {"是" if self.ai_assisted else "否"}
      // 描述: 在这里实现具体的业务逻辑
      
      const processedData = `processed_${{inputData}}`;
      
      return {{
        status: 'success',
        data: processedData,
        timestamp: new Date().toISOString()
      }};
      
    }} catch (error) {{
      console.error('Error in exampleMethod:', error);
      throw new Error(`处理失败: ${{error.message}}`);
    }}
  }}
}}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = {module_name.replace('_', '').title()};
}}
'''
    
    def _html_page_template(self, page_name: str, description: str, **kwargs) -> str:
        """
        生成HTML页面模板
        
        Args:
            page_name (str): 页面名称
            description (str): 页面描述
            
        Returns:
            str: HTML页面模板
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        header = self._get_common_header('html', description)
        
        return f'''{header}
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_name} - Office-Doc-Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="static/css/enhanced-ui.css" rel="stylesheet">
    <style>
        /* 页面特定样式 */
        .custom-style {{
            /* TODO: 添加自定义样式 - {self.author_name} {self.current_date} */
        }}
    </style>
</head>
<body class="bg-gray-50">
    <!-- 导航栏 -->
    <nav class="bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <i class="fas fa-file-alt text-white text-2xl mr-3"></i>
                    <h1 class="text-white text-xl font-bold">{page_name}</h1>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="/" class="text-white hover:text-gray-200 transition-colors">
                        <i class="fas fa-home mr-2"></i>返回主页
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- 主要内容 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-semibold text-gray-900 mb-6">
                <i class="fas fa-cog mr-2 text-blue-600"></i>{description}
            </h2>
            
            <!-- TODO: 添加页面内容 - {self.author_name} {self.current_date} -->
            <div class="text-center text-gray-500 py-8">
                <i class="fas fa-construction text-4xl mb-4"></i>
                <p>页面内容开发中...</p>
            </div>
        </div>
    </div>

    <!-- 页面脚本 -->
    <script>
        /**
         * 页面初始化
         * @author {self.author_name}
         * @date {self.current_date}
         * @ai_assisted {"是" if self.ai_assisted else "否"}
         */
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('{page_name} page loaded');
            // TODO: 添加页面初始化逻辑 - {self.author_name} {self.current_date}
        }});
    </script>
</body>
</html>
'''
    
    def _markdown_doc_template(self, doc_name: str, description: str, **kwargs) -> str:
        """
        生成Markdown文档模板
        
        Args:
            doc_name (str): 文档名称
            description (str): 文档描述
            
        Returns:
            str: Markdown文档模板
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        header = self._get_common_header('markdown', description)
        
        return f'''{header}

# {doc_name}

## 📋 文档信息
- **创建时间**: {self.current_date}
- **创建人**: {self.author_name}
- **最后更新**: {self.current_date}
- **更新人**: {self.author_name}
- **版本**: v1.0
- **状态**: 草稿
- **AI辅助**: {"是" if self.ai_assisted else "否"}

## 🎯 目标和范围

<!-- TODO: 描述文档的目标和适用范围 - {self.author_name} {self.current_date} -->

## 📖 内容概述

<!-- TODO: 添加文档主要内容 - {self.author_name} {self.current_date} -->

### 1. 章节标题

内容描述...

### 2. 章节标题

内容描述...

## 📊 图表和示例

<!-- TODO: 添加相关图表和代码示例 - {self.author_name} {self.current_date} -->

## 🔗 相关链接

- [相关文档1](链接地址)
- [相关文档2](链接地址)

## 📝 更新日志

| 版本 | 日期 | 更新人 | 更新内容 |
|------|------|--------|----------|
| v1.0 | {self.current_date} | {self.author_name} | 初始版本 |

---

**审核人**: 待指定  
**审核时间**: 待审核  
**审核状态**: 待审核
'''
    
    def _test_file_template(self, test_name: str, description: str, **kwargs) -> str:
        """
        生成测试文件模板
        
        Args:
            test_name (str): 测试名称
            description (str): 测试描述
            
        Returns:
            str: 测试文件模板
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        header = self._get_common_header('python', f"{description} - 测试文件")
        
        return f'''{header}

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# TODO: 导入要测试的模块 - {self.author_name} {self.current_date}
# from src.module_name import ClassName

class Test{test_name.replace('_', '').title()}(unittest.TestCase):
    """
    {description}测试类
    
    测试{description}的各种功能和边界情况。
    
    Author: {self.author_name}
    Date: {self.current_date}
    AI Assisted: {"是" if self.ai_assisted else "否"}
    """
    
    def setUp(self):
        """
        测试前置条件
        
        在每个测试方法执行前调用，用于准备测试环境。
        
        Author: {self.author_name}
        Date: {self.current_date}
        AI Assisted: {"是" if self.ai_assisted else "否"}
        """
        # TODO: 初始化测试对象和数据 - {self.author_name} {self.current_date}
        pass
    
    def tearDown(self):
        """
        测试后清理
        
        在每个测试方法执行后调用，用于清理测试环境。
        
        Author: {self.author_name}
        Date: {self.current_date}
        AI Assisted: {"是" if self.ai_assisted else "否"}
        """
        # TODO: 清理测试数据和资源 - {self.author_name} {self.current_date}
        pass
    
    def test_example_function(self):
        """
        测试示例功能
        
        使用Given-When-Then模式编写测试用例。
        
        Author: {self.author_name}
        Date: {self.current_date}
        AI Assisted: {"是" if self.ai_assisted else "否"}
        """
        # Given: 准备测试数据
        test_input = "test_data"
        expected_output = "expected_result"
        
        # When: 执行测试操作
        # TODO: 调用被测试的函数 - {self.author_name} {self.current_date}
        # actual_output = function_to_test(test_input)
        
        # Then: 验证结果
        # self.assertEqual(actual_output, expected_output)
        # self.assertTrue(condition)
        # self.assertIsNotNone(result)
        
        # 临时通过，等待实现
        self.assertTrue(True, "测试用例待实现")
    
    def test_edge_cases(self):
        """
        测试边界情况
        
        测试各种边界条件和异常情况。
        
        Author: {self.author_name}
        Date: {self.current_date}
        AI Assisted: {"是" if self.ai_assisted else "否"}
        """
        # TODO: 测试空输入、None值、异常情况等 - {self.author_name} {self.current_date}
        pass
    
    @patch('module_name.external_dependency')
    def test_with_mock(self, mock_dependency):
        """
        使用Mock的测试示例
        
        演示如何使用Mock对象进行单元测试。
        
        Args:
            mock_dependency: Mock对象
            
        Author: {self.author_name}
        Date: {self.current_date}
        AI Assisted: {"是" if self.ai_assisted else "否"}
        """
        # 配置Mock对象
        mock_dependency.return_value = "mocked_result"
        
        # TODO: 执行测试并验证Mock调用 - {self.author_name} {self.current_date}
        # result = function_that_uses_dependency()
        # mock_dependency.assert_called_once()
        pass

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
'''
    
    def generate_template(self, template_type: str, name: str, description: str, **kwargs) -> str:
        """
        生成指定类型的模板
        
        Args:
            template_type (str): 模板类型
            name (str): 名称
            description (str): 描述
            **kwargs: 其他参数
            
        Returns:
            str: 生成的模板内容
            
        Raises:
            ValueError: 不支持的模板类型
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        if template_type not in self.templates:
            available_types = ', '.join(self.templates.keys())
            raise ValueError(f"不支持的模板类型: {template_type}。可用类型: {available_types}")
        
        return self.templates[template_type](name, description, **kwargs)
    
    def save_template(self, template_content: str, file_path: str) -> None:
        """
        保存模板到文件
        
        Args:
            template_content (str): 模板内容
            file_path (str): 文件路径
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"✅ 模板已保存到: {file_path}")

def main():
    """
    主函数 - 命令行工具入口
    
    Author: AI Assistant (Claude)
    Date: 2025-06-25
    AI Assisted: 是
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="代码模板生成器")
    parser.add_argument("type", choices=['python_module', 'python_class', 'python_function', 
                                        'javascript_module', 'html_page', 'markdown_doc', 'test_file'],
                       help="模板类型")
    parser.add_argument("name", help="名称")
    parser.add_argument("description", help="描述")
    parser.add_argument("--author", default="开发者", help="作者姓名")
    parser.add_argument("--ai-assisted", action="store_true", help="AI辅助开发")
    parser.add_argument("--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = CodeTemplateGenerator(args.author, args.ai_assisted)
    
    # 生成模板
    template_content = generator.generate_template(args.type, args.name, args.description)
    
    # 输出或保存
    if args.output:
        generator.save_template(template_content, args.output)
    else:
        print(template_content)

if __name__ == "__main__":
    main()
