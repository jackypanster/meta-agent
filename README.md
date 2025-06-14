# Qwen-Agent MVP

🤖 A command-line AI assistant built with the Qwen-Agent framework, DeepSeek LLM, Context7 MCP Server, and mem0 memory management.

## ✨ Features

- **Qwen-Agent Framework**: Core AI agent functionality
- **DeepSeek LLM**: Powerful language model integration via API
- **Context7 MCP Server**: Server-side event streaming for real-time context
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
# MCP_SERVER_URL=https://mcp.context7.com/sse
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
📝 You said: Hello, how can you help me?
🤖 [AI response will appear here once LLM integration is complete]

> quit
👋 Goodbye!
```

## 🏗️ Architecture

```
src/
├── agent/          # Qwen-Agent integration & LLM clients
│   ├── deepseek_client.py    # DeepSeek API integration
│   ├── function_calling.py   # Function calling support
│   └── models.py            # Agent data models
├── config/         # Configuration management
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
├── main.py         # Application entry point
└── __init__.py
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
# Required: DeepSeek API key for LLM access
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Required: Context7 MCP server URL
MCP_SERVER_URL=https://mcp.context7.com/sse

# Optional: Customize behavior
LOG_LEVEL=INFO
MEMORY_COLLECTION_NAME=qwen_agent_conversations
```

### API Keys Setup

1. **DeepSeek API**: Get your API key from [DeepSeek Platform](https://platform.deepseek.com)
2. **Context7 MCP**: Access via the provided server URL (no additional key needed)

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
5. 🔄 **Qwen-Agent Core Integration** (Current: Task 6)
6. 🔄 **CLI Interface Enhancement** (Task 7)
7. 🔄 **Error Handling & Logging** (Task 8)
8. 🔄 **Documentation & Examples** (Task 9)
9. 🔄 **Complete Testing Suite** (Task 10)

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
- [Context7 MCP Server](https://mcp.context7.com)
- [mem0 Documentation](https://docs.mem0.ai)

## 📞 Support

If you encounter any issues or have questions:

1. Check the [documentation](#-usage)
2. Review [common issues](#-troubleshooting)
3. Open an issue on GitHub
4. Contact the development team

---

**Note**: This is an MVP (Minimum Viable Product) implementation. Features will be progressively added and enhanced based on the development roadmap outlined above. 