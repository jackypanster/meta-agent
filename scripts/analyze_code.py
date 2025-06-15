#!/usr/bin/env python3
"""
代码分析脚本

用于检测项目中未使用的代码、导入和潜在的清理目标
"""

import os
import sys
import subprocess
import ast
from pathlib import Path
from typing import List, Dict, Set


def run_vulture():
    """运行vulture检测未使用的代码"""
    print("🔍 运行vulture检测未使用的代码...")
    
    cmd = ["vulture", "src/", "--min-confidence", "80"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Vulture输出:\n{result.stdout}")
        if result.stderr:
            print(f"Vulture错误:\n{result.stderr}")
        return result.stdout
    except Exception as e:
        print(f"运行vulture失败: {e}")
        return None


def run_pyflakes():
    """运行pyflakes检测导入问题"""
    print("🔍 运行pyflakes检测导入问题...")
    
    cmd = ["pyflakes", "src/"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Pyflakes输出:\n{result.stdout}")
        if result.stderr:
            print(f"Pyflakes错误:\n{result.stderr}")
        return result.stdout
    except Exception as e:
        print(f"运行pyflakes失败: {e}")
        return None


def analyze_imports(file_path: Path) -> Dict[str, List[str]]:
    """分析文件中的导入语句"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = {'import': [], 'from_import': []}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports['import'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports['from_import'].append(f"{node.module}.{alias.name}")
        
        return imports
    except Exception as e:
        print(f"分析 {file_path} 导入失败: {e}")
        return {'import': [], 'from_import': []}


def find_python_files(directory: Path) -> List[Path]:
    """查找目录中的所有Python文件"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # 跳过虚拟环境和缓存目录
        dirs[:] = [d for d in dirs if d not in {'.venv', '__pycache__', '.git', '.pytest_cache'}]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files


def find_unused_files():
    """查找可能未使用的文件"""
    print("🔍 查找可能未使用的文件...")
    
    # 查找根目录下的demo/example文件
    root_files = list(Path('.').glob('*.py'))
    demo_files = []
    
    for file in root_files:
        if any(keyword in file.name.lower() for keyword in ['demo', 'example', 'test_', 'simple', 'basic']):
            demo_files.append(file)
    
    if demo_files:
        print("🗑️  发现可能的demo/example文件:")
        for file in demo_files:
            print(f"  - {file}")
    
    return demo_files


def check_import_usage(src_dir: Path) -> Dict[str, List[str]]:
    """检查导入的使用情况"""
    print("🔍 检查导入使用情况...")
    
    all_files = find_python_files(src_dir)
    unused_imports = {}
    
    for file_path in all_files:
        imports = analyze_imports(file_path)
        # 这里简化处理，实际应该检查导入是否被使用
        if imports['import'] or imports['from_import']:
            unused_imports[str(file_path)] = imports
    
    return unused_imports


def main():
    """主函数"""
    print("🚀 开始代码分析...")
    
    # 确保在项目根目录
    if not Path('src').exists():
        print("❌ 请在项目根目录运行此脚本")
        return
    
    # 创建分析报告
    report = {
        'vulture_output': run_vulture(),
        'pyflakes_output': run_pyflakes(),
        'unused_files': find_unused_files(),
        'import_analysis': check_import_usage(Path('src'))
    }
    
    # 生成报告
    print("\n" + "="*50)
    print("📊 代码分析报告")
    print("="*50)
    
    if report['unused_files']:
        print(f"\n🗑️  发现 {len(report['unused_files'])} 个可能未使用的文件")
    
    if report['vulture_output']:
        print(f"\n🔍 Vulture发现了潜在的未使用代码")
    
    if report['pyflakes_output']:
        print(f"\n⚠️  Pyflakes发现了导入问题")
    
    print("\n✅ 分析完成！")


if __name__ == "__main__":
    main() 