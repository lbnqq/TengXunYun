#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试导出问题的脚本

Author: AI Assistant
Created: 2025-08-03
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_coordinator():
    """调试协调器状态"""
    try:
        from src.llm_clients.spark_x1_client import SparkX1Client
        from src.core.tools.style_alignment_coordinator import StyleAlignmentCoordinator
        
        print("🔍 初始化协调器...")
        spark_x1_client = SparkX1Client('NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh')
        coordinator = StyleAlignmentCoordinator(spark_x1_client)
        
        print("📋 当前活跃任务:")
        print(f"   任务数量: {len(coordinator.active_tasks)}")
        for task_id, task_data in coordinator.active_tasks.items():
            print(f"   任务ID: {task_id}")
            print(f"   任务类型: {task_data.get('type', 'unknown')}")
            print(f"   状态: {task_data.get('status', 'unknown')}")
            print(f"   数据键: {list(task_data.keys())}")
            if 'generated_content' in task_data:
                content_length = len(task_data['generated_content'])
                print(f"   内容长度: {content_length}")
                if content_length > 0:
                    print(f"   内容预览: {task_data['generated_content'][:100]}...")
            print("   ---")
        
        print("📊 任务进度:")
        print(f"   进度数量: {len(coordinator.task_progress)}")
        for task_id, progress in coordinator.task_progress.items():
            print(f"   任务ID: {task_id}")
            print(f"   进度: {progress.get('progress', 0)}%")
            print(f"   状态: {progress.get('status', 'unknown')}")
            print("   ---")
        
        # 如果有任务，测试导出
        if coordinator.active_tasks:
            first_task_id = list(coordinator.active_tasks.keys())[0]
            print(f"🧪 测试导出第一个任务: {first_task_id}")
            
            # 测试获取任务结果
            task_result = coordinator.get_task_result(first_task_id)
            print(f"📋 任务结果获取: {task_result.get('success')}")
            if task_result.get('success'):
                data = task_result.get('data', {})
                print(f"📊 数据键: {list(data.keys())}")
                content = data.get('generated_content', '')
                print(f"📝 内容长度: {len(content)}")
                
                # 测试导出
                export_result = coordinator.export_result(first_task_id, 'txt')
                print(f"📤 导出结果: {export_result.get('success')}")
                if not export_result.get('success'):
                    print(f"❌ 导出错误: {export_result.get('error')}")
                else:
                    print(f"✅ 导出成功: {export_result.get('filename')}")
            else:
                print(f"❌ 任务结果获取失败: {task_result.get('error')}")
        else:
            print("ℹ️ 没有活跃任务可供测试")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_coordinator()
