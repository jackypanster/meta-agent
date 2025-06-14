"""命令行交互界面模块"""

import sys
from typing import Optional

from rich.console import Console
from rich.text import Text

console = Console()


def show_welcome() -> None:
    """显示欢迎界面."""
    console.print(Text("🤖 Qwen-Agent MVP", style="bold blue"))
    console.print("Starting the AI assistant...\n")


def show_ready_message() -> None:
    """显示应用就绪消息."""
    console.print("🚀 Qwen-Agent MVP is ready!", style="green bold")
    console.print(
        "This is a placeholder implementation. "
        "Core functionality will be added in upcoming tasks."
    )


def show_startup_message() -> None:
    """显示组件初始化消息."""
    console.print("🔧 Initializing components...")


def run_interactive_loop() -> None:
    """运行交互式命令循环."""
    console.print("\nType 'quit' to exit, or any message to test the setup:")
    
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("👋 Goodbye!", style="blue")
                break
            elif user_input:
                console.print(f"📝 You said: {user_input}", style="cyan")
                console.print(
                    "🤖 [This is a placeholder response. LLM integration coming soon!]", 
                    style="green"
                )
        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!", style="blue")
            break
        except EOFError:
            break


def handle_startup_error(error: Exception) -> None:
    """处理启动错误.
    
    Args:
        error: 启动时发生的异常
    """
    console.print(f"❌ Error: {error}", style="red")
    sys.exit(1) 