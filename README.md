# Qwen-Agent MVP

🤖 A command-line AI assistant built with the Qwen-Agent framework, DeepSeek LLM, official MCP servers (time/fetch/memory), and mem0 memory management.

## ✨ Features

- **Qwen-Agent Framework**: Core AI agent functionality
- **DeepSeek LLM**: Powerful language model integration via API
- **Official MCP Servers**: Time, fetch, and memory services via standard MCP protocol
- **Dynamic MCP Configuration**: External JSON-based configuration with hot reload
- **mem0 Memory Management**: Persistent memory for conversations
- **Rich CLI Interface**: Beautiful command-line interaction using Rich library
- **Async Architecture**: Non-blocking operations with aiohttp
- **Environment Configuration**: Secure API key management

## 🛠️ Requirements

- Python 3.11 or higher
- uv package manager (recommended) or pip
- DeepSeek API key
- Internet connection for MCP server communication

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd qwen-agent-mvp
```

### 2. Install Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual API keys
# Required:
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
# MCP服务器通过官方Qwen-Agent内置支持自动配置
# MEM0_API_KEY=your_mem0_api_key_here
```

### 4. Run the Application

```bash
# Using Python module
python -m src.main

# Or if installed as package
qwen-agent-mvp
```

## 📖 Usage

Once started, the application provides an interactive command-line interface:

```
🤖 Qwen-Agent MVP
Starting the AI assistant...

✅ Environment variables loaded
🔧 Initializing components...
🚀 Qwen-Agent MVP is ready!

Type 'quit' to exit, or any message to test the setup:
> Hello, how can you help me?
🤖 Hello! I'm an AI assistant powered by Qwen-Agent framework with DeepSeek's reasoning model. 
I can help you with various tasks including:
- Answering questions and having conversations
- Using external tools via official MCP servers (time, fetch, memory)
- Remembering our conversation history through mem0

> quit
👋 Goodbye!
```

## 🤖 Core Agent Features

The MVP now includes a fully integrated Qwen-Agent with the following capabilities:

### LLM Integration
- **DeepSeek-R1-0528 Model**: Advanced reasoning capabilities via the `deepseek-reasoner` model
- **Async Chat Completion**: Non-blocking message processing
- **Streaming Support**: Real-time response generation

### Tool Integration  
- **MCP Integration**: Official Qwen-Agent support for time, fetch, and memory MCP servers
- **Dynamic Tool Loading**: Tools are discovered at runtime and made available to the agent
- **Error Handling**: Graceful handling of tool failures with informative messages

### Memory Management
- **Conversation Memory**: Automatic extraction and storage of conversation facts
- **Context Retrieval**: Relevant memories are included in agent prompts
- **Persistent Storage**: Memories persist across sessions via mem0

### Agent Factory
- **Simple Creation**: Easy agent instantiation with `create_agent()` or `quick_chat()`
- **Configuration Management**: Centralized config through `ConfigManager`
- **Session Management**: Multiple conversation sessions with memory isolation

## 🏗️ Architecture

```
src/
├── agent/          # Qwen-Agent integration & core agent logic (✅ Completed)
│   ├── deepseek_client.py    # DeepSeek API integration
│   ├── llm_adapter.py        # DeepSeek to Qwen-Agent adapter
│   ├── tool_adapter.py       # MCP to Qwen-Agent tool adapter
│   ├── core_agent.py         # Main QwenAgentMVP class
│   ├── factory.py            # Agent factory and configuration
│   ├── function_calling.py   # Function calling support
│   └── models.py            # Agent data models
├── config/         # Configuration management (✅ Completed)
│   ├── mcp_config.py       # MCP configuration loader with caching
│   ├── mcp_validator.py    # Configuration validation system
│   └── mcp_watcher.py      # Dynamic configuration updates & hot reload
├── memory/         # mem0 memory management (✅ Completed)
│   ├── models.py           # Memory data models
│   ├── mem0_client.py      # mem0 API client wrapper
│   ├── manager.py          # Memory manager core
│   └── service.py          # High-level memory service
├── tools/          # MCP tools and utilities (✅ Completed)
│   ├── models.py           # MCP protocol models
│   ├── sse_parser.py       # SSE event parser
│   ├── mcp_client.py       # MCP SSE client
│   └── tool_manager.py     # Tool execution manager
├── main.py         # Application entry point with dynamic MCP loading
└── __init__.py

config/             # External configuration files
└── mcp_servers.json        # MCP server configurations

docs/               # Documentation
└── MCP_CONFIGURATION_SYSTEM.md  # Detailed MCP config system docs
```

## 📦 Dependencies

### Core Dependencies
- **qwen-agent**: AI agent framework (>= 0.0.10)
- **httpx**: HTTP client for API calls (>= 0.25.0)
- **python-dotenv**: Environment variable management (>= 1.0.0)
- **mem0ai**: Memory management system (>= 0.0.20)
- **rich**: Rich text and beautiful formatting (>= 13.7.0)
- **aiohttp**: Async HTTP client/server (>= 3.9.0)
- **sseclient-py**: Server-Sent Events client (>= 1.8.0)

### Development Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **coverage**: Test coverage

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with:

```env
# Required: DeepSeek API key for LLM access (DeepSeek-R1-0528 model)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Required: mem0 API key for memory management
MEM0_API_KEY=your_mem0_api_key_here

# Optional: Customize behavior
LOG_LEVEL=INFO
DEEPSEEK_MODEL=deepseek-reasoner  # DeepSeek-R1-0528 reasoning model
```

### MCP Server Configuration

The application now uses an external JSON configuration file for MCP servers:

**File**: `config/mcp_servers.json`

```json
{
  "version": "1.0",
  "servers": {
    "time": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-time"],
      "enabled": true,
      "description": "Time and date operations",
      "category": "utility"
    },
    "fetch": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-fetch"],
      "enabled": true,
      "description": "HTTP fetch operations",
      "category": "network"
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "enabled": true,
      "description": "Memory storage operations",
      "category": "storage"
    }
  },
  "global_settings": {
    "default_timeout": 30,
    "default_retry_attempts": 3,
    "log_level": "INFO"
  }
}
```

**Key Features**:
- 🔄 **Hot Reload**: Configuration changes are detected and applied automatically
- ✅ **Validation**: Comprehensive validation with helpful error messages
- 🎛️ **Dynamic Control**: Enable/disable servers without code changes
- 📁 **External Config**: Configuration separated from code for better maintainability
- 🔒 **Fallback**: Automatic fallback to default configuration if file is missing

For detailed information about the MCP configuration system, see [docs/MCP_CONFIGURATION_SYSTEM.md](docs/MCP_CONFIGURATION_SYSTEM.md).

### API Keys Setup

1. **DeepSeek API**: Get your API key from [DeepSeek Platform](https://platform.deepseek.com/api_keys) for DeepSeek-R1-0528 model access
2. **MCP Servers**: Configured via external JSON file (`config/mcp_servers.json`) - no API keys needed for official servers
3. **mem0 API**: Get your API key from [mem0.ai](https://mem0.ai/) for memory management

## 🧪 Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Sort imports
uv run isort src/ tests/

# Type checking
uv run mypy src/
```

### Project Structure Development

This is an MVP implementation with the following development roadmap:

1. ✅ **Project Setup & Configuration** (Completed)
2. ✅ **DeepSeek LLM Integration** (Completed)
3. ✅ **MCP SSE Client Implementation** (Completed)
4. ✅ **Memory Management (mem0)** (Completed)
5. ✅ **Qwen-Agent Core Integration** (Completed)
6. ✅ **External MCP Configuration System** (Completed - Task 13)
   - Dynamic JSON-based configuration
   - Hot reload functionality
   - Comprehensive validation system
   - Graceful fallback mechanisms
7. 🔄 **CLI Interface Enhancement** (Current: Task 7)
8. 🔄 **Error Handling & Logging** (Task 8)
9. 🔄 **Documentation & Examples** (Task 9)
10. 🔄 **Complete Testing Suite** (Task 10)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `uv run pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Qwen-Agent Documentation](https://github.com/QwenLM/Qwen-Agent)
- [DeepSeek API Documentation](https://platform.deepseek.com/docs)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [mem0 Documentation](https://docs.mem0.ai)

## 📞 Support

If you encounter any issues or have questions:

1. Check the [documentation](#-usage)
2. Review [common issues](#-troubleshooting)
3. Open an issue on GitHub
4. Contact the development team

---

**Note**: This is an MVP (Minimum Viable Product) implementation. Features will be progressively added and enhanced based on the development roadmap outlined above. 