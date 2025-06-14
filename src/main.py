#!/usr/bin/env python3
"""
Qwen-Agent MVP - Main Entry Point

A command-line AI assistant based on the Qwen-Agent framework.
This MVP integrates DeepSeek LLM, Context7 MCP Server, and mem0 memory management.

Usage:
    python -m src.main
    # or after installation:
    qwen-agent-mvp
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
from rich.console import Console
from rich.text import Text

console = Console()


def load_environment():
    """Load environment variables from .env file."""
    # Look for .env file in project root (parent of src)
    env_path = Path(__file__).parent.parent / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        console.print("✅ Environment variables loaded", style="green")
    else:
        console.print("⚠️ No .env file found. Please copy .env.example to .env and configure it.", style="yellow")
        return False
    
    # Check for required environment variables
    required_vars = ["DEEPSEEK_API_KEY", "MCP_SERVER_URL"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here":
            missing_vars.append(var)
    
    if missing_vars:
        console.print(f"❌ Missing or not configured: {', '.join(missing_vars)}", style="red")
        return False
    
    return True


def main():
    """Main entry point for the Qwen-Agent MVP."""
    console.print(Text("🤖 Qwen-Agent MVP", style="bold blue"))
    console.print("Starting the AI assistant...\n")
    
    # Load environment configuration
    if not load_environment():
        console.print("\n💡 Setup instructions:")
        console.print("1. Copy .env.example to .env: cp .env.example .env")
        console.print("2. Edit .env with your actual API keys")
        console.print("3. Restart the application")
        sys.exit(1)
    
    try:
        # Import and initialize components
        console.print("🔧 Initializing components...")
        
        # TODO: Initialize Qwen-Agent framework
        # TODO: Initialize DeepSeek LLM client
        # TODO: Initialize MCP SSE client for Context7
        # TODO: Initialize mem0 memory management
        # TODO: Start CLI interaction loop
        
        console.print("🚀 Qwen-Agent MVP is ready!", style="green bold")
        console.print("This is a placeholder implementation. Core functionality will be added in upcoming tasks.")
        
        # Placeholder interactive loop
        console.print("\nType 'quit' to exit, or any message to test the setup:")
        while True:
            try:
                user_input = input("> ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    console.print("👋 Goodbye!", style="blue")
                    break
                elif user_input:
                    console.print(f"📝 You said: {user_input}", style="cyan")
                    console.print("🤖 [This is a placeholder response. LLM integration coming soon!]", style="green")
            except KeyboardInterrupt:
                console.print("\n👋 Goodbye!", style="blue")
                break
            except EOFError:
                break
                
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main() 