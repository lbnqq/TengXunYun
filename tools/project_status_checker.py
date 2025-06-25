#!/usr/bin/env python3
"""
项目状态检测工具

基于时间戳进行增量检测，生成项目状态报告。
符合项目开发规范要求的状态检测工具。

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
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

class ProjectStatusChecker:
    """
    项目状态检测器
    
    用于检测项目文件变更、依赖更新、配置修改等状态信息。
    支持增量检测和完整状态报告生成。
    
    Author: AI Assistant (Claude)
    Date: 2025-06-25
    AI Assisted: 是
    """
    
    def __init__(self, project_root: str = "."):
        """
        初始化项目状态检测器
        
        Args:
            project_root (str): 项目根目录路径
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        self.project_root = Path(project_root).resolve()
        self.status_file = self.project_root / ".project_status.json"
        self.ignore_patterns = {
            "__pycache__", ".git", ".venv", "venv", "node_modules",
            ".pytest_cache", ".coverage", "*.pyc", "*.pyo", "*.log"
        }
        
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path (Path): 文件路径
            
        Returns:
            Dict[str, Any]: 文件信息字典
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        try:
            stat = file_path.stat()
            
            # 计算文件哈希（仅对小于10MB的文件）
            file_hash = None
            if stat.st_size < 10 * 1024 * 1024:  # 10MB
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                except (PermissionError, UnicodeDecodeError):
                    pass
            
            return {
                "path": str(file_path.relative_to(self.project_root)),
                "size": stat.st_size,
                "modified_time": stat.st_mtime,
                "hash": file_hash,
                "extension": file_path.suffix.lower()
            }
        except (OSError, PermissionError):
            return None
    
    def should_ignore(self, path: Path) -> bool:
        """
        检查是否应该忽略该路径
        
        Args:
            path (Path): 文件或目录路径
            
        Returns:
            bool: 是否应该忽略
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern in path_str or path.name.startswith('.'):
                return True
        return False
    
    def scan_project(self) -> Dict[str, Any]:
        """
        扫描项目文件
        
        Returns:
            Dict[str, Any]: 项目文件信息
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        files_info = {}
        stats = {
            "total_files": 0,
            "total_size": 0,
            "file_types": {},
            "scan_time": datetime.now().isoformat()
        }
        
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if not self.should_ignore(root_path / d)]
            
            for file in files:
                file_path = root_path / file
                
                if self.should_ignore(file_path):
                    continue
                
                file_info = self.get_file_info(file_path)
                if file_info:
                    files_info[file_info["path"]] = file_info
                    stats["total_files"] += 1
                    stats["total_size"] += file_info["size"]
                    
                    # 统计文件类型
                    ext = file_info["extension"]
                    stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
        
        return {
            "files": files_info,
            "statistics": stats
        }
    
    def load_previous_status(self) -> Optional[Dict[str, Any]]:
        """
        加载上次的状态信息
        
        Returns:
            Optional[Dict[str, Any]]: 上次的状态信息，如果不存在则返回None
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        if not self.status_file.exists():
            return None
        
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def save_current_status(self, status: Dict[str, Any]) -> None:
        """
        保存当前状态信息
        
        Args:
            status (Dict[str, Any]): 当前状态信息
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"警告: 无法保存状态文件: {e}")
    
    def detect_changes(self, current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测文件变更
        
        Args:
            current (Dict[str, Any]): 当前状态
            previous (Dict[str, Any]): 之前状态
            
        Returns:
            Dict[str, Any]: 变更信息
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        changes = {
            "added": [],
            "modified": [],
            "deleted": [],
            "summary": {}
        }
        
        current_files = current.get("files", {})
        previous_files = previous.get("files", {})
        
        # 检测新增和修改的文件
        for path, info in current_files.items():
            if path not in previous_files:
                changes["added"].append(path)
            elif (info.get("hash") != previous_files[path].get("hash") or
                  info.get("modified_time") != previous_files[path].get("modified_time")):
                changes["modified"].append(path)
        
        # 检测删除的文件
        for path in previous_files:
            if path not in current_files:
                changes["deleted"].append(path)
        
        # 生成摘要
        changes["summary"] = {
            "total_changes": len(changes["added"]) + len(changes["modified"]) + len(changes["deleted"]),
            "added_count": len(changes["added"]),
            "modified_count": len(changes["modified"]),
            "deleted_count": len(changes["deleted"]),
            "check_time": datetime.now().isoformat()
        }
        
        return changes
    
    def generate_report(self, current: Dict[str, Any], changes: Optional[Dict[str, Any]] = None) -> str:
        """
        生成状态报告
        
        Args:
            current (Dict[str, Any]): 当前状态
            changes (Optional[Dict[str, Any]]): 变更信息
            
        Returns:
            str: 格式化的状态报告
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        stats = current.get("statistics", {})
        
        report = f"""# 项目状态检测报告

## 📊 基本信息
- **检测时间**: {stats.get('scan_time', 'N/A')}
- **项目路径**: {self.project_root}
- **总文件数**: {stats.get('total_files', 0):,}
- **总大小**: {self._format_size(stats.get('total_size', 0))}

## 📁 文件类型分布
"""
        
        file_types = stats.get("file_types", {})
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            ext_name = ext if ext else "无扩展名"
            report += f"- **{ext_name}**: {count} 个文件\n"
        
        if changes:
            summary = changes.get("summary", {})
            report += f"""
## 🔄 变更信息
- **总变更数**: {summary.get('total_changes', 0)}
- **新增文件**: {summary.get('added_count', 0)}
- **修改文件**: {summary.get('modified_count', 0)}
- **删除文件**: {summary.get('deleted_count', 0)}

### 详细变更
"""
            
            if changes.get("added"):
                report += "\n**新增文件**:\n"
                for file in changes["added"][:10]:  # 最多显示10个
                    report += f"- ✅ {file}\n"
                if len(changes["added"]) > 10:
                    report += f"- ... 还有 {len(changes['added']) - 10} 个文件\n"
            
            if changes.get("modified"):
                report += "\n**修改文件**:\n"
                for file in changes["modified"][:10]:  # 最多显示10个
                    report += f"- 📝 {file}\n"
                if len(changes["modified"]) > 10:
                    report += f"- ... 还有 {len(changes['modified']) - 10} 个文件\n"
            
            if changes.get("deleted"):
                report += "\n**删除文件**:\n"
                for file in changes["deleted"][:10]:  # 最多显示10个
                    report += f"- ❌ {file}\n"
                if len(changes["deleted"]) > 10:
                    report += f"- ... 还有 {len(changes['deleted']) - 10} 个文件\n"
        
        report += f"""
---
**报告生成**: AI Assistant (Claude)  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**工具版本**: v1.0
"""
        
        return report
    
    def _format_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes (int): 字节数
            
        Returns:
            str: 格式化的大小字符串
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def run_check(self, save_status: bool = True) -> str:
        """
        运行完整的状态检测
        
        Args:
            save_status (bool): 是否保存当前状态
            
        Returns:
            str: 状态报告
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        print("🔍 开始项目状态检测...")
        
        # 扫描当前项目状态
        current_status = self.scan_project()
        
        # 加载之前的状态
        previous_status = self.load_previous_status()
        
        # 检测变更
        changes = None
        if previous_status:
            changes = self.detect_changes(current_status, previous_status)
            print(f"📊 检测到 {changes['summary']['total_changes']} 个变更")
        else:
            print("📊 首次检测，无历史状态对比")
        
        # 生成报告
        report = self.generate_report(current_status, changes)
        
        # 保存当前状态
        if save_status:
            self.save_current_status(current_status)
            print("💾 状态信息已保存")
        
        return report

def main():
    """
    主函数
    
    Author: AI Assistant (Claude)
    Date: 2025-06-25
    AI Assisted: 是
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="项目状态检测工具")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--no-save", action="store_true", help="不保存状态信息")
    parser.add_argument("--output", help="输出报告到文件")
    
    args = parser.parse_args()
    
    # 创建检测器
    checker = ProjectStatusChecker(args.project_root)
    
    # 运行检测
    report = checker.run_check(save_status=not args.no_save)
    
    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 报告已保存到: {args.output}")
    else:
        print("\n" + "="*60)
        print(report)

if __name__ == "__main__":
    main()
