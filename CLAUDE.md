# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Quick Start:**
```bash
# Install dependencies
uv sync

# Create environment file (required)
cp env.template .env
# Edit .env to add your DEEPSEEK_API_KEY

# Run application
uv run python main.py
# or: make run
```

**Development Workflow:**
```bash
# Format code
make format  # black + isort
uv run black src/ tests/
uv run isort src/ tests/

# Type checking
make type-check  # mypy
uv run mypy src/

# Linting
make lint  # format + type-check + flake8
uv run flake8 src/ tests/

# Testing
make test  # all tests
uv run pytest
uv run pytest tests/unit/  # unit tests only
uv run pytest tests/integration/  # integration tests only
uv run pytest --cov=src --cov-report=html  # with coverage

# Pre-commit checks
make pre-commit  # length-check + lint + test

# Clean temporary files
make clean
```

**Single Test Execution:**
```bash
# Run specific test file
uv run pytest tests/test_fail_fast_validation.py -v

# Run specific test function
uv run pytest tests/unit/test_config.py::TestConfig::test_require_missing_key -v

# Run tests with specific markers
uv run pytest -m "unit"  # unit tests only
uv run pytest -m "integration"  # integration tests only
uv run pytest -m "e2e"  # end-to-end tests only
```

## Architecture Overview

This is a **Qwen-Agent MVP** - a command-line AI assistant built with **fail-fast architecture principles**. The system is designed to crash immediately on any error rather than handling exceptions gracefully.

**Core Design Principle: FAIL-FAST**
- Any configuration error → immediate crash
- Any API error → immediate crash  
- Any runtime error → immediate crash
- No exception handling, no fallbacks, no silent failures
- "Programs must either work correctly or crash immediately"

**Tech Stack:**
- **Framework**: Qwen-Agent (official framework)
- **LLM**: Multi-provider support
  - DeepSeek API (V3 stable or R1 reasoning models)
  - Qwen3-32B (local VLLM deployment)
- **Package Manager**: uv (preferred) 
- **UI**: Rich CLI interface
- **Testing**: pytest with markers (unit/integration/e2e)
- **Memory**: mem0ai for conversation memory
- **Protocols**: MCP (Model Context Protocol) for tool integration

## Project Structure

```
src/
├── main.py              # Main entry point (fail-fast design)
├── config/              # Configuration management  
│   ├── settings.py      # Environment config (no fallbacks)
│   ├── mcp_config.py    # MCP server configuration loader
│   ├── mcp_validator.py # Strict configuration validation
│   └── prompt_manager.py# External prompt management
├── tools/               # Tool modules
│   └── qwen_tools/      # Qwen-Agent compatible tools
│       ├── calculator_tool.py # Math calculator
│       └── memory_tools.py    # Memory management
└── ui/                  # User interface helpers
    └── helpers.py       # CLI helper functions

config/                  # External configuration files
├── mcp_servers.json     # MCP server definitions
├── mcp_servers_schema.json # Validation schema
└── prompts/             # Externalized system prompts
    ├── system_prompts.json
    └── locales/         # Multi-language support
        ├── en/system_prompts.json
        └── zh/system_prompts.json
```

**Key Architecture Decisions:**
- **Configuration External**: All prompts and MCP servers defined in config/ directory
- **No Exception Handling**: All errors bubble up to crash the program
- **Tool Discovery**: Tools are explicitly listed, not auto-discovered
- **Memory Simple**: Basic conversation history with mem0ai
- **Validation Strict**: JSON schema validation for all configurations

## Fail-Fast Implementation Details

**Configuration Loading (`src/config/settings.py:Config`):**
- `.env` file must exist (no default creation)
- Required keys missing → immediate ConfigError
- Malformed .env lines → immediate ConfigError  
- No environment variable fallbacks

**LLM Configuration (`src/main.py:create_llm_config`):**
- MODEL_NAME required via `config.require()` (deepseek-chat|deepseek-reasoner|qwen3-32b)
- Provider auto-detected from model name - no separate provider configuration needed
- DeepSeek models: DEEPSEEK_API_KEY required
- Qwen3 model: QWEN3_API_KEY and QWEN3_MODEL_SERVER required, QWEN3_ENABLE_THINKING optional
- Qwen3 thinking mode: Configures `extra_body.chat_template_kwargs.enable_thinking` for vLLM/SGLang
- No API connection pre-validation (fails on first actual call)
- Model-specific helper functions: `_create_deepseek_config()`, `_create_qwen3_config()`

**MCP Server Setup (`src/main.py:setup_mcp_servers`):**
- Loads from `config/mcp_servers.json`
- Schema validation via `config/mcp_servers_schema.json`
- Missing/invalid configs → immediate MCPConfigError
- Only enabled servers are loaded

**Tool Registration:**
- Explicit tool list in `create_tools_list()`
- No dynamic discovery mechanisms
- Custom tools: calculator, memory management
- MCP servers loaded dynamically from configuration

## Configuration Files

**Required Environment Variables (`.env`):**
```env
# Required: Model selection (automatically detects provider)
MODEL_NAME=deepseek-chat  # Options: deepseek-chat, deepseek-reasoner, qwen3-32b

# === DeepSeek Configuration (when using deepseek-* models) ===
# Required: DeepSeek API key
DEEPSEEK_API_KEY=your_api_key_here

# === Qwen3-32B Configuration (when using qwen3-32b model) ===
# Required: Qwen3 API key (usually "EMPTY" for local VLLM)
QWEN3_API_KEY=EMPTY
# Required: Qwen3 server URL
QWEN3_MODEL_SERVER=http://localhost:8000/v1
# Optional: Enable thinking mode (default: false)
QWEN3_ENABLE_THINKING=false

# === Optional Configuration ===
OPENROUTER_API_KEY=your_key_here
MCP_SERVER_URL=https://mcp.context7.com/sse
```

**MCP Server Configuration (`config/mcp_servers.json`):**
- JSON schema validated against `config/mcp_servers_schema.json`
- Each server requires: `command`, `args`, `enabled`
- Optional fields: `description`, `category`, `env`, `timeout`
- Only enabled servers are loaded by the agent

**System Prompts (`config/prompts/system_prompts.json`):**
- Externalized prompt templates with variable substitution
- Supports multiple locales (en/zh)
- Used throughout `src/main.py` via PromptManager

## Test Organization

**Test Structure:**
```
tests/
├── test_basic.py                    # Basic functionality
├── test_e2e.py                     # End-to-end scenarios  
├── test_fail_fast_validation.py    # Fail-fast behavior validation
├── test_prompt_config_validation.py # Prompt configuration tests
├── unit/                           # Unit tests
│   ├── test_config.py              # Configuration module tests
│   ├── test_mcp_config.py          # MCP configuration tests
│   ├── test_mcp_validator.py       # MCP validation tests
│   └── test_mcp_watcher.py         # MCP file watcher tests
└── integration/                    # Integration tests  
    └── test_mcp_integration.py     # MCP integration tests
```

**Test Markers (pytest.ini):**
- `@pytest.mark.unit` - Unit tests for individual functions
- `@pytest.mark.integration` - Module interaction tests  
- `@pytest.mark.e2e` - Complete user scenario tests
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.api` - Tests requiring network connectivity

## Error Handling Philosophy

**What This Codebase Does NOT Do:**
- ❌ Try/catch exception handling
- ❌ Default values for missing config
- ❌ Graceful degradation
- ❌ Error recovery mechanisms
- ❌ Silent failure with logging
- ❌ Retry logic for failed operations

**What This Codebase DOES Do:**
- ✅ Immediate crashes on any error
- ✅ Explicit configuration requirements
- ✅ Fast failure detection
- ✅ Clear error messages before crashing
- ✅ Zero hidden error states

**Exception Types:**
- `ConfigError` - Configuration loading/validation failures
- `PromptManagerError` - Prompt template failures  
- `MCPConfigError` - MCP configuration failures
- `APIConnectionError` - LLM API failures
- `ModelConfigError` - Model setup failures

## Development Guidelines

**Code Style:**
- Line length: 88 characters (Black formatter)
- Type hints required (mypy strict mode)
- Import sorting with isort
- File length limit: 100 lines (enforced in Makefile)

**Adding New Features:**
1. Follow fail-fast principles - no exception handling
2. Add type hints for all functions
3. Update relevant schema files if adding config
4. Add appropriate test markers (@pytest.mark.unit/integration/e2e)
5. Run `make pre-commit` before committing

**Adding New Tools:**
1. Create tool in `src/tools/qwen_tools/`
2. Add to explicit tool list in `src/main.py:create_tools_list()`
3. Follow Qwen-Agent tool interface conventions
4. No auto-discovery - tools must be explicitly registered

**Configuration Changes:**
1. Update schema files first (`config/*_schema.json`)
2. Update loading logic in respective config modules
3. Maintain fail-fast behavior (no fallbacks)
4. Add validation tests

**Model Configuration:**
- Set `MODEL_NAME=deepseek-chat` for DeepSeek V3 stable model
- Set `MODEL_NAME=deepseek-reasoner` for DeepSeek R1 reasoning model  
- Set `MODEL_NAME=qwen3-32b` for local Qwen3-32B VLLM deployment
- Provider automatically detected from model name - no separate provider setting needed
- Model validation occurs at startup - invalid models crash immediately

**Qwen3 Thinking Mode:**
- Set `QWEN3_ENABLE_THINKING=true` to enable thinking mode (chain-of-thought)
- Set `QWEN3_ENABLE_THINKING=false` for standard response mode (default)
- Thinking mode configures vLLM/SGLang `chat_template_kwargs.enable_thinking` parameter
- Model name uses official format: `Qwen/Qwen3-32B` (not `-Instruct` suffix)

This codebase prioritizes immediate failure over error resilience - embrace the crashes as features, not bugs.