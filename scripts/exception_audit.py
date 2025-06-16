#!/usr/bin/env python3
"""
异常处理审计工具
使用AST分析项目中所有Python文件的异常处理模式，生成详细报告
"""

import ast
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ExceptionHandler:
    """异常处理信息"""
    file_path: str
    line_number: int
    column: int
    handler_type: str  # 'try-except', 'try-finally', 'try-except-finally', 'context-manager'
    exception_types: List[str]
    has_bare_except: bool
    has_finally: bool
    code_snippet: str
    function_name: Optional[str] = None
    class_name: Optional[str] = None


@dataclass
class FallbackPattern:
    """Fallback模式信息"""
    file_path: str
    line_number: int
    column: int
    pattern_type: str  # 'default-assignment', 'conditional-fallback', 'optional-return'
    code_snippet: str
    function_name: Optional[str] = None
    class_name: Optional[str] = None


class ExceptionAuditVisitor(ast.NodeVisitor):
    """AST访问器，用于识别异常处理模式"""
    
    def __init__(self, file_path: str, source_code: str):
        self.file_path = file_path
        self.source_lines = source_code.splitlines()
        self.exception_handlers: List[ExceptionHandler] = []
        self.fallback_patterns: List[FallbackPattern] = []
        self.current_function = None
        self.current_class = None
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """访问函数定义"""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """访问异步函数定义"""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
        
    def visit_ClassDef(self, node: ast.ClassDef):
        """访问类定义"""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_Try(self, node: ast.Try):
        """访问try语句"""
        # 确定异常处理类型
        handler_type = "try"
        if node.handlers:
            handler_type += "-except"
        if node.finalbody:
            handler_type += "-finally"
        if node.orelse:
            handler_type += "-else"
            
        # 收集异常类型
        exception_types = []
        has_bare_except = False
        
        for handler in node.handlers:
            if handler.type is None:
                has_bare_except = True
                exception_types.append("Exception (bare except)")
            else:
                exception_types.append(self._get_exception_name(handler.type))
                
        # 获取代码片段
        code_snippet = self._get_code_snippet(node.lineno, node.end_lineno or node.lineno)
        
        # 创建异常处理记录
        exception_handler = ExceptionHandler(
            file_path=self.file_path,
            line_number=node.lineno,
            column=node.col_offset,
            handler_type=handler_type,
            exception_types=exception_types,
            has_bare_except=has_bare_except,
            has_finally=bool(node.finalbody),
            code_snippet=code_snippet,
            function_name=self.current_function,
            class_name=self.current_class
        )
        
        self.exception_handlers.append(exception_handler)
        self.generic_visit(node)
        
    def visit_With(self, node: ast.With):
        """访问with语句（上下文管理器）"""
        # 检查是否用于异常抑制
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                if isinstance(item.context_expr.func, ast.Name):
                    if item.context_expr.func.id in ['suppress', 'contextlib.suppress']:
                        code_snippet = self._get_code_snippet(node.lineno, node.end_lineno or node.lineno)
                        
                        exception_handler = ExceptionHandler(
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            handler_type="context-manager-suppress",
                            exception_types=["suppressed"],
                            has_bare_except=False,
                            has_finally=False,
                            code_snippet=code_snippet,
                            function_name=self.current_function,
                            class_name=self.current_class
                        )
                        
                        self.exception_handlers.append(exception_handler)
                        
        self.generic_visit(node)
        
    def visit_Assign(self, node: ast.Assign):
        """访问赋值语句，查找fallback模式"""
        # 检查默认值赋值模式
        if isinstance(node.value, ast.IfExp):  # 三元表达式
            code_snippet = self._get_code_snippet(node.lineno, node.lineno)
            
            fallback = FallbackPattern(
                file_path=self.file_path,
                line_number=node.lineno,
                column=node.col_offset,
                pattern_type="conditional-fallback",
                code_snippet=code_snippet,
                function_name=self.current_function,
                class_name=self.current_class
            )
            
            self.fallback_patterns.append(fallback)
            
        self.generic_visit(node)
        
    def visit_Return(self, node: ast.Return):
        """访问return语句，查找Optional返回模式"""
        if node.value and isinstance(node.value, ast.IfExp):
            code_snippet = self._get_code_snippet(node.lineno, node.lineno)
            
            fallback = FallbackPattern(
                file_path=self.file_path,
                line_number=node.lineno,
                column=node.col_offset,
                pattern_type="optional-return",
                code_snippet=code_snippet,
                function_name=self.current_function,
                class_name=self.current_class
            )
            
            self.fallback_patterns.append(fallback)
            
        self.generic_visit(node)
        
    def _get_exception_name(self, node: ast.AST) -> str:
        """获取异常类型名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_exception_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Tuple):
            return f"({', '.join(self._get_exception_name(elt) for elt in node.elts)})"
        else:
            return "Unknown"
            
    def _get_code_snippet(self, start_line: int, end_line: int) -> str:
        """获取代码片段"""
        try:
            if start_line <= len(self.source_lines):
                if end_line <= len(self.source_lines):
                    lines = self.source_lines[start_line-1:end_line]
                else:
                    lines = self.source_lines[start_line-1:start_line]
                return '\n'.join(lines).strip()
        except (IndexError, TypeError):
            pass
        return "Unable to extract code snippet"


class ExceptionAuditor:
    """异常处理审计器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.all_handlers: List[ExceptionHandler] = []
        self.all_fallbacks: List[FallbackPattern] = []
        
    def scan_directories(self, directories: List[str]) -> None:
        """扫描指定目录中的所有Python文件"""
        for directory in directories:
            dir_path = self.project_root / directory
            if dir_path.exists():
                print(f"🔍 扫描目录: {dir_path}")
                self._scan_directory(dir_path)
            else:
                print(f"⚠️ 目录不存在: {dir_path}")
                
    def _scan_directory(self, directory: Path) -> None:
        """递归扫描目录"""
        for file_path in directory.rglob("*.py"):
            if self._should_skip_file(file_path):
                continue
                
            try:
                self._analyze_file(file_path)
            except Exception as e:
                print(f"❌ 分析文件失败 {file_path}: {e}")
                
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            "venv",
            ".venv",
            "node_modules",
            ".git"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
        
    def _analyze_file(self, file_path: Path) -> None:
        """分析单个Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                
            # 解析AST
            tree = ast.parse(source_code, filename=str(file_path))
            
            # 创建访问器并遍历AST
            visitor = ExceptionAuditVisitor(str(file_path), source_code)
            visitor.visit(tree)
            
            # 收集结果
            self.all_handlers.extend(visitor.exception_handlers)
            self.all_fallbacks.extend(visitor.fallback_patterns)
            
            if visitor.exception_handlers or visitor.fallback_patterns:
                print(f"📄 {file_path.relative_to(self.project_root)}: "
                      f"{len(visitor.exception_handlers)} 异常处理, "
                      f"{len(visitor.fallback_patterns)} fallback模式")
                      
        except SyntaxError as e:
            print(f"⚠️ 语法错误 {file_path}: {e}")
        except Exception as e:
            print(f"❌ 处理文件失败 {file_path}: {e}")
            
    def generate_report(self, output_file: str = "exception_audit_report.json") -> Dict[str, Any]:
        """生成审计报告"""
        report = {
            "audit_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "summary": {
                "total_exception_handlers": len(self.all_handlers),
                "total_fallback_patterns": len(self.all_fallbacks),
                "files_with_exceptions": len(set(h.file_path for h in self.all_handlers)),
                "files_with_fallbacks": len(set(f.file_path for f in self.all_fallbacks))
            },
            "exception_handlers": [asdict(h) for h in self.all_handlers],
            "fallback_patterns": [asdict(f) for f in self.all_fallbacks],
            "statistics": self._generate_statistics()
        }
        
        # 保存报告
        output_path = self.project_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📊 报告已保存到: {output_path}")
        return report
        
    def _generate_statistics(self) -> Dict[str, Any]:
        """生成统计信息"""
        handler_types = {}
        exception_types = {}
        fallback_types = {}
        
        # 统计异常处理类型
        for handler in self.all_handlers:
            handler_types[handler.handler_type] = handler_types.get(handler.handler_type, 0) + 1
            for exc_type in handler.exception_types:
                exception_types[exc_type] = exception_types.get(exc_type, 0) + 1
                
        # 统计fallback类型
        for fallback in self.all_fallbacks:
            fallback_types[fallback.pattern_type] = fallback_types.get(fallback.pattern_type, 0) + 1
            
        return {
            "handler_types": handler_types,
            "exception_types": exception_types,
            "fallback_types": fallback_types,
            "bare_except_count": sum(1 for h in self.all_handlers if h.has_bare_except),
            "finally_block_count": sum(1 for h in self.all_handlers if h.has_finally)
        }
        
    def print_summary(self) -> None:
        """打印审计摘要"""
        print("\n" + "="*60)
        print("🔍 异常处理审计摘要")
        print("="*60)
        
        print(f"📊 总计异常处理: {len(self.all_handlers)}")
        print(f"📊 总计fallback模式: {len(self.all_fallbacks)}")
        print(f"📊 涉及文件数: {len(set(h.file_path for h in self.all_handlers))}")
        
        if self.all_handlers:
            print("\n🚨 发现的异常处理类型:")
            handler_types = {}
            for handler in self.all_handlers:
                handler_types[handler.handler_type] = handler_types.get(handler.handler_type, 0) + 1
                
            for handler_type, count in sorted(handler_types.items()):
                print(f"  - {handler_type}: {count}")
                
        if self.all_fallbacks:
            print("\n⚠️ 发现的fallback模式:")
            fallback_types = {}
            for fallback in self.all_fallbacks:
                fallback_types[fallback.pattern_type] = fallback_types.get(fallback.pattern_type, 0) + 1
                
            for fallback_type, count in sorted(fallback_types.items()):
                print(f"  - {fallback_type}: {count}")
                
        bare_except_count = sum(1 for h in self.all_handlers if h.has_bare_except)
        if bare_except_count > 0:
            print(f"\n🚨 发现 {bare_except_count} 个bare except语句!")
            
        print("\n" + "="*60)


def main():
    """主函数"""
    print("🔍 开始异常处理审计...")
    
    # 获取项目根目录
    project_root = os.getcwd()
    print(f"📁 项目根目录: {project_root}")
    
    # 创建审计器
    auditor = ExceptionAuditor(project_root)
    
    # 扫描目录
    directories_to_scan = ["src", "tests", "scripts"]
    auditor.scan_directories(directories_to_scan)
    
    # 生成报告
    report = auditor.generate_report()
    
    # 打印摘要
    auditor.print_summary()
    
    return report


if __name__ == "__main__":
    main() 