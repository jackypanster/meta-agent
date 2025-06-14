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

import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from cli.environment import load_environment, show_setup_instructions
from cli.interface import (
    handle_startup_error,
    run_interactive_loop,
    show_ready_message,
    show_startup_message,
    show_welcome,
)


def main() -> None:
    """Main entry point for the Qwen-Agent MVP."""
    show_welcome()
    
    # Load environment configuration
    if not load_environment():
        show_setup_instructions()
        sys.exit(1)
    
    try:
        # Import and initialize components
        show_startup_message()
        
        # TODO: Initialize Qwen-Agent framework
        # TODO: Initialize DeepSeek LLM client
        # TODO: Initialize MCP SSE client for Context7
        # TODO: Initialize mem0 memory management
        # TODO: Start CLI interaction loop
        
        show_ready_message()
        run_interactive_loop()
                
    except Exception as e:
        handle_startup_error(e)


if __name__ == "__main__":
    main() 