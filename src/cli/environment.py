"""环境变量管理模块"""

import os
from pathlib import Path
from typing import Tuple

from dotenv import load_dotenv
from rich.console import Console

console = Console()


def load_environment() -> bool:
    """加载环境变量从.env文件.
    
    Returns:
        bool: 如果环境变量成功加载且配置完整则返回True
    """
    # 查找项目根目录下的.env文件
    env_path = Path(__file__).parent.parent.parent / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        console.print("✅ Environment variables loaded", style="green")
    else:
        console.print(
            "⚠️ No .env file found. Please copy .env.example to .env and configure it.", 
            style="yellow"
        )
        return False
    
    return _validate_required_variables()


def _validate_required_variables() -> bool:
    """验证必需的环境变量是否已配置.
    
    Returns:
        bool: 如果所有必需变量都已正确配置则返回True
    """
    required_vars = ["DEEPSEEK_API_KEY", "MCP_SERVER_URL"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            missing_vars.append(var)
    
    if missing_vars:
        console.print(
            f"❌ Missing or not configured: {', '.join(missing_vars)}", 
            style="red"
        )
        return False
    
    return True


def show_setup_instructions() -> None:
    """显示环境配置说明."""
    console.print("\n💡 Setup instructions:")
    console.print("1. Copy .env.example to .env: cp .env.example .env")
    console.print("2. Edit .env with your actual API keys")
    console.print("3. Restart the application") 