# Meta-Agent: Qwen-Agent MVP

基于官方Qwen-Agent框架的最简洁智能助手实现，专注于核心功能和极简设计。

## 🚀 核心特性

- **极简架构**: 零自定义系统提示词，完全依赖qwen-agent框架内置指令
- **模块化工具系统**: 支持MCP (Model Context Protocol) 服务器集成
- **多模型支持**: DeepSeek、OpenAI、Anthropic等主流LLM提供商
- **简单内存管理**: 基于文件的对话记忆系统
- **直观CLI界面**: 清晰的命令行交互体验
- **安全配置**: API密钥保护和敏感文件检测

## 📋 快速开始

### 环境要求
- Python 3.9+
- uv (推荐) 或 pip

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd meta-agent
```

2. **安装依赖**
```bash
# 使用uv (推荐)
uv sync

# 或使用pip
pip install -r requirements.txt
```

3. **配置API密钥**
```bash
# 复制环境变量模板
cp env.template .env

# 编辑.env文件，添加你的API密钥
# 至少需要一个LLM提供商的API密钥
```

4. **运行程序**
```bash
# 使用uv
uv run python src/main.py

# 或直接运行
python src/main.py
```

## 🛠️ 配置说明

### MCP服务器配置
编辑 `config/mcp_servers.json` 来配置MCP服务器：

```json
{
  "servers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "enabled": true,
      "description": "HTTP网页抓取服务"
    }
  }
}
```

### 环境变量
在 `.env` 文件中配置API密钥：

```bash
# DeepSeek (推荐)
DEEPSEEK_API_KEY=your_deepseek_api_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## 📚 文档

- [用户指南](docs/USER_GUIDE.md) - 详细使用说明
- [MCP配置系统](docs/MCP_CONFIGURATION_SYSTEM.md) - MCP服务器配置指南
- [安全指南](QUICK_SECURITY_GUIDE.md) - API密钥安全最佳实践

## ⚠️ 重要提醒

### SSE协议MCP服务器支持
**当前Qwen-Agent框架存在SSE协议支持bug**，详情请查看：
📋 **[SSE协议Bug跟踪文档](docs/QWEN_AGENT_SSE_BUG_TRACKING.md)**

- **影响**: 无法使用SSE协议的MCP服务器 (如某些K8S管理工具)
- **状态**: 官方正在修复中 ([PR #597](https://github.com/QwenLM/Qwen-Agent/pulls))
- **临时方案**: 使用命令行启动的MCP服务器

我们已经为将来的SSE支持做好了准备，一旦官方修复合并，即可立即启用SSE协议的MCP服务器。

## 🏗️ 项目结构

```
meta-agent/
├── src/                    # 主要源代码
│   ├── config/            # 配置管理模块
│   ├── tools/             # 工具和MCP集成
│   └── ui/                # 用户界面
├── config/                # 配置文件
│   ├── mcp_servers.json   # MCP服务器配置
│   └── mcp_servers_schema.json # 配置Schema
├── docs/                  # 项目文档
├── tests/                 # 测试文件
└── scripts/               # 工具脚本
```

## 🧪 测试

```bash
# 运行所有测试
uv run python -m pytest

# 运行特定测试
uv run python -m pytest tests/test_minimal_system.py -v

# 运行安全检查
./scripts/security-check.sh
```

## 🔒 安全

- API密钥自动保护 (gitignore)
- 敏感文件检测脚本
- 详细安全指南: [SECURITY.md](SECURITY.md)

## 📈 极简化成就

这个项目展示了**技术极简主义**的成功实践：

- **系统提示词**: 从800+ tokens优化到0 tokens (100%减少)
- **代码行数**: 减少1600+行冗余代码 (90%+减少)
- **配置复杂度**: 统一配置源，消除多层配置冲突
- **功能完整性**: 保持100%功能正常

> **核心发现**: qwen-agent框架的自动化能力完全足够，自定义提示词系统是100%冗余的

## 🤝 贡献

欢迎提交Issue和Pull Request！请查看：
- [开发指南](docs/CONTRIBUTING.md)
- [代码规范](.cursor/rules/)

## 📄 许可证

[MIT License](LICENSE)

---

**让AI助手回归简单和高效！** 🎯 