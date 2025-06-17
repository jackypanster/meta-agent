#!/usr/bin/env python3
"""
Qwen-Agent MVP - 主程序入口

基于官方Qwen-Agent框架的最简洁实现：
- 直接使用Assistant类
- 模块化工具系统
- 简单的内存管理
- 直观的CLI界面
- 支持多种LLM模型提供商
"""

from typing import NoReturn

from src.app_core import create_agent, run_conversation_loop
from src.ui import show_welcome


def main() -> NoReturn:
    """主函数 - 专注于程序流程控制，失败时立即崩溃
    
    Raises:
        ConfigError: 配置加载失败时立即抛出
        MCPConfigError: MCP配置失败时立即抛出
        Exception: 任何其他异常都会立即传播导致程序崩溃
    """
    # 1. 显示欢迎界面
    show_welcome()
    
    # 2. 创建并配置Agent
    agent = create_agent()
    
    # 3. 运行对话循环
    run_conversation_loop(agent)


if __name__ == "__main__":
    main()