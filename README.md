# Qwen-Agent MVP

🤖 **极简AI助手** - 基于Qwen-Agent框架的命令行AI助手，采用fail-fast架构设计，确保快速失败和问题暴露。

## ✨ 核心特性

- **🚀 Fail-Fast架构**: 任何错误立即失败，无异常掩盖，快速暴露问题
- **🤖 Qwen-Agent框架**: 官方Qwen-Agent框架集成，支持工具调用
- **🧠 DeepSeek LLM**: 集成DeepSeek-R1推理模型，强大的语言理解能力
- **🔧 MCP工具集成**: 支持计算器和内存管理工具
- **💾 内存管理**: 简单的对话记忆功能
- **🎨 Rich CLI**: 美观的命令行界面
- **⚡ 零容错**: 配置错误、API错误、连接错误都立即失败

## 🛠️ 系统要求

- **Python 3.8+** (推荐3.11+)
- **uv包管理器** ([安装指南](https://github.com/astral-sh/uv))
- **DeepSeek API密钥** ([获取地址](https://platform.deepseek.com/))
- **稳定的网络连接**

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd meta-agent
```

### 2. 安装依赖

```bash
# 使用uv (推荐)
uv sync

# 或使用pip
pip install -e .
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp env.template .env

# 编辑.env文件，添加你的API密钥
# DEEPSEEK_API_KEY=your_actual_api_key_here
```

### 4. 运行应用

```bash
# 方式1: 使用uv运行
uv run python main.py

# 方式2: 直接运行
python main.py

# 方式3: 作为模块运行
python -m src.main
```

## 📖 使用示例

### 基本对话

```
🤖 Qwen-Agent MVP - 简洁直观实现
基于官方Qwen-Agent框架，使用最新DeepSeek-R1-0528推理模型

✅ 配置加载成功
🔧 工具初始化完成
🚀 Qwen-Agent MVP 已就绪！

输入 'help' 查看帮助，'quit' 退出程序
> 你好，我叫张三
🤖 你好张三！很高兴认识你。我是基于Qwen-Agent框架的AI助手，可以帮你进行对话、计算和记忆管理。有什么我可以帮助你的吗？

> 我的名字是什么？
🤖 你的名字是张三。

> 计算 2 + 3 * 4
🤖 让我为你计算一下...
计算结果：2 + 3 * 4 = 14
```

### 可用命令

- `help` - 显示帮助信息和使用示例
- `memory` - 查看保存的记忆内容
- `clear` - 清屏
- `quit` / `exit` - 退出程序

### 工具功能

- **🧮 计算器**: 支持基本数学运算和函数
- **🧠 记忆管理**: 自动保存和回忆用户信息
- **💬 对话历史**: 维护对话上下文

## 🏗️ 项目架构

```
meta-agent/
├── src/                    # 源代码目录
│   ├── main.py            # 主程序入口 (fail-fast设计)
│   ├── config/            # 配置管理模块
│   │   ├── settings.py    # 环境配置 (无fallback)
│   │   ├── mcp_config.py  # MCP配置加载器
│   │   ├── mcp_validator.py # 配置验证 (严格验证)
│   │   └── prompt_manager.py # 提示词管理
│   ├── tools/             # 工具模块
│   │   └── qwen_tools/    # Qwen-Agent工具
│   │       ├── calculator_tool.py # 计算器工具
│   │       └── memory_tools.py    # 内存管理工具
│   └── ui/                # 用户界面
│       └── helpers.py     # UI帮助函数
├── config/                # 配置文件
│   ├── mcp_servers.json   # MCP服务器配置
│   ├── mcp_servers_schema.json # 配置验证模式
│   └── prompts/           # 提示词模板
├── tests/                 # 测试文件
│   └── test_fail_fast_validation.py # Fail-fast验证测试
├── scripts/               # 工具脚本
│   └── exception_audit.py # 异常处理审计工具
├── main.py               # 项目入口点
├── .env                  # 环境变量 (需要创建)
├── env.template          # 环境变量模板
└── README.md             # 项目文档
```

## ⚡ Fail-Fast设计原则

本项目严格遵循**fail-fast**设计原则：

### ✅ 立即失败场景
- **配置错误**: 缺失.env文件或API密钥 → 立即崩溃
- **网络错误**: API连接失败 → 立即崩溃  
- **输入错误**: 无效的工具参数 → 立即崩溃
- **系统错误**: 文件不存在、权限错误 → 立即崩溃

### ❌ 禁止的模式
- ~~异常捕获和默认值~~
- ~~错误恢复和重试机制~~
- ~~静默失败和日志掩盖~~
- ~~优雅降级和容错处理~~

### 🎯 设计理念
> **程序要么正确工作，要么立即崩溃** - 没有中间地带

这确保了：
- 问题立即暴露，便于快速修复
- 避免隐藏的错误状态
- 提高代码可靠性和可预测性

## 🔧 配置说明

### 环境变量

在项目根目录创建`.env`文件：

```env
# 必需: DeepSeek API密钥
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 可选: OpenRouter API密钥 (备用)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# 可选: MCP服务器URL
MCP_SERVER_URL=https://mcp.context7.com/sse

# 可选: 是否使用DeepSeek R1推理模型
USE_DEEPSEEK_R1=false
```

### MCP服务器配置

编辑`config/mcp_servers.json`来配置MCP服务器：

```json
{
  "version": "1.0",
  "servers": {
    "time": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-time"],
      "enabled": true
    }
  }
}
```

## 🧪 测试

### 运行测试套件

```bash
# 运行所有测试
uv run python -m pytest tests/ -v

# 运行fail-fast验证测试
uv run python -m pytest tests/test_fail_fast_validation.py -v

# 运行异常处理审计
uv run python scripts/exception_audit.py
```

### 测试覆盖

- **配置模块**: 测试环境变量加载、配置验证
- **工具模块**: 测试计算器和内存工具
- **Fail-Fast行为**: 验证各种错误场景的立即失败
- **异常传播**: 确保异常正确传播到顶层

## 🚨 故障排除

### 常见错误及解决方案

#### "ConfigError: .env file not found"
```bash
# 创建.env文件
cp env.template .env
# 编辑.env文件添加API密钥
```

#### "ConfigError: DEEPSEEK_API_KEY is required"
```bash
# 在.env文件中添加有效的API密钥
echo "DEEPSEEK_API_KEY=your_key_here" >> .env
```

#### "ModuleNotFoundError: No module named 'qwen_agent'"
```bash
# 重新安装依赖
uv sync
# 或
pip install -e .
```

#### 程序立即崩溃
这是**正常行为**！Fail-fast设计意味着任何配置或运行时错误都会导致立即崩溃。检查错误信息并修复根本问题。

## 📊 性能指标

- **启动时间**: < 2秒 (不包括网络延迟)
- **响应时间**: < 3秒 (取决于API延迟)
- **内存使用**: < 50MB (基础运行)
- **工具调用**: < 100ms (本地计算)

## 🔮 未来计划

- [ ] 支持更多LLM提供商 (OpenAI, Claude等)
- [ ] Web界面支持
- [ ] 持久化内存存储
- [ ] 更多MCP工具集成
- [ ] 多用户会话支持
- [ ] 插件系统

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

**注意**: 所有贡献必须遵循fail-fast设计原则，禁止添加异常处理和fallback机制。

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 🙏 致谢

- [Qwen-Agent](https://github.com/QwenLM/Qwen-Agent) - 核心AI框架
- [DeepSeek](https://platform.deepseek.com/) - 强大的语言模型
- [Rich](https://github.com/Textualize/rich) - 美观的CLI界面
- [uv](https://github.com/astral-sh/uv) - 快速的Python包管理器

---

**⚡ 记住**: 这是一个fail-fast系统 - 错误是好事，崩溃是特性！🚀 