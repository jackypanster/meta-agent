# Qwen-Agent MVP 用户指南

## 📖 目录

1. [项目简介](#项目简介)
2. [核心特性](#核心特性)
3. [技术架构](#技术架构)
4. [系统要求](#系统要求)
5. [快速开始](#快速开始)
6. [详细配置](#详细配置)
7. [功能使用指南](#功能使用指南)
8. [故障排除](#故障排除)
9. [高级配置](#高级配置)
10. [API参考](#api参考)
11. [最佳实践](#最佳实践)
12. [更新和维护](#更新和维护)

---

## 项目简介

### 🎯 项目概述

**Qwen-Agent MVP** 是一个基于官方Qwen-Agent框架的极简命令行AI助手，采用严格的fail-fast架构设计。项目的核心理念是"要么正确工作，要么立即崩溃"，确保任何问题都能被快速发现和修复。

### 🚀 项目目标

- **快速原型验证**：提供一个最小可行产品(MVP)来验证Qwen-Agent框架的核心功能
- **fail-fast架构示范**：展示如何在AI应用中实现严格的fail-fast设计原则
- **开发者友好**：为开发者提供一个清晰、可扩展的AI助手基础框架
- **生产就绪**：虽然是MVP，但代码质量和架构设计都达到生产环境标准

### 🎨 设计哲学

本项目严格遵循以下设计原则：

1. **极端Fail-Fast**：任何异常都立即抛出，绝不掩盖错误
2. **零容错机制**：禁止使用try-catch、默认值、fallback等容错机制
3. **配置外部化**：所有配置都通过外部文件管理，支持热重载
4. **模块化设计**：清晰的模块边界，单一职责原则
5. **类型安全**：完整的类型注解和静态类型检查

---

## 核心特性

### 🏗️ 架构特性

#### ⚡ Fail-Fast架构
- **立即失败**：配置错误、API错误、网络错误都立即崩溃
- **零异常处理**：核心代码中不存在任何try-catch块
- **问题暴露**：错误立即暴露，便于快速定位和修复
- **可预测性**：程序行为完全可预测，不存在隐藏状态

#### 🔧 配置管理系统
- **外部化配置**：所有设置通过配置文件管理
- **热重载支持**：配置文件变更自动检测和重载
- **严格验证**：配置格式和内容的严格JSON Schema验证
- **国际化支持**：多语言提示词模板系统

#### 🛠️ MCP集成
- **标准协议**：完整支持Model Context Protocol (MCP)
- **工具扩展**：支持自定义工具开发和集成
- **服务器管理**：动态MCP服务器配置和管理
- **类型安全**：完整的MCP消息类型定义

### 🤖 AI功能特性

#### 🧠 智能对话
- **DeepSeek集成**：支持DeepSeek-R1推理模型
- **上下文管理**：智能对话历史管理
- **多轮对话**：支持复杂的多轮对话场景
- **推理展示**：可选的推理过程展示

#### 🔧 工具系统
- **计算器工具**：支持复杂数学表达式计算
- **内存管理**：智能信息存储和检索
- **工具链调用**：支持多工具协作
- **自定义工具**：简单的工具开发接口

#### 💾 记忆功能
- **自动保存**：对话中的重要信息自动保存
- **智能检索**：基于语义的信息检索
- **持久化存储**：记忆数据持久化保存
- **隐私保护**：本地存储，数据安全

### 🎨 用户体验特性

#### 💻 命令行界面
- **Rich UI**：美观的命令行界面
- **实时反馈**：操作状态实时显示
- **颜色编码**：不同类型信息的颜色区分
- **进度指示**：长时间操作的进度显示

#### 🌐 国际化
- **多语言支持**：中英文界面切换
- **本地化提示**：本地化的错误信息和提示
- **文化适配**：符合不同文化习惯的交互方式

---

## 技术架构

### 🏛️ 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Qwen-Agent MVP                           │
├─────────────────────────────────────────────────────────────┤
│  User Interface Layer (CLI)                                │
│  ├── Rich Terminal UI                                      │
│  ├── Command Parser                                        │
│  └── Internationalization                                  │
├─────────────────────────────────────────────────────────────┤
│  Application Layer                                         │
│  ├── Main Application (main.py)                           │
│  ├── Conversation Manager                                  │
│  └── Tool Orchestrator                                     │
├─────────────────────────────────────────────────────────────┤
│  Service Layer                                             │
│  ├── Qwen-Agent Framework                                  │
│  ├── MCP Client                                           │
│  └── Memory Manager                                        │
├─────────────────────────────────────────────────────────────┤
│  Tool Layer                                                │
│  ├── Calculator Tool                                       │
│  ├── Memory Tools                                          │
│  └── Custom Tools Interface                                │
├─────────────────────────────────────────────────────────────┤
│  Configuration Layer                                       │
│  ├── Settings Manager                                      │
│  ├── MCP Configuration                                     │
│  ├── Prompt Manager                                        │
│  └── Schema Validator                                      │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                      │
│  ├── File System                                          │
│  ├── Network (HTTP/WebSocket)                             │
│  └── Process Management                                    │
└─────────────────────────────────────────────────────────────┘
```

### 📁 目录结构

```
meta-agent/
├── 📁 src/                          # 源代码目录
│   ├── 📄 main.py                   # 主程序入口
│   ├── 📁 config/                   # 配置管理模块
│   │   ├── 📄 settings.py           # 环境配置管理
│   │   ├── 📄 mcp_config.py         # MCP配置加载器
│   │   ├── 📄 mcp_validator.py      # 配置验证器
│   │   ├── 📄 mcp_watcher.py        # 配置文件监控
│   │   └── 📄 prompt_manager.py     # 提示词管理器
│   ├── 📁 tools/                    # 工具模块
│   │   └── 📁 qwen_tools/           # Qwen-Agent工具
│   │       ├── 📄 calculator_tool.py # 计算器工具
│   │       └── 📄 memory_tools.py    # 内存管理工具
│   └── 📁 ui/                       # 用户界面
│       └── 📄 helpers.py            # UI帮助函数
├── 📁 config/                       # 配置文件目录
│   ├── 📄 mcp_servers.json          # MCP服务器配置
│   ├── 📄 mcp_servers_schema.json   # 配置验证模式
│   └── 📁 prompts/                  # 提示词模板
│       ├── 📄 system_prompts.json   # 系统提示词
│       └── 📁 locales/              # 国际化文件
├── 📁 tests/                        # 测试文件
│   ├── 📄 test_basic.py             # 基础功能测试
│   ├── 📄 test_e2e.py               # 端到端测试
│   └── 📄 test_fail_fast_validation.py # Fail-fast验证
├── 📁 scripts/                      # 工具脚本
│   ├── 📄 exception_audit.py        # 异常处理审计
│   └── 📄 security-check.sh         # 安全检查脚本
├── 📁 docs/                         # 文档目录
│   ├── 📄 USER_GUIDE.md             # 用户指南
│   ├── 📄 prd.md                    # 产品需求文档
│   └── 📄 MVP_VALIDATION.md         # MVP验证文档
├── 📄 main.py                       # 项目入口点
├── 📄 pyproject.toml                # 项目配置
├── 📄 .env                          # 环境变量(需创建)
├── 📄 env.template                  # 环境变量模板
└── 📄 README.md                     # 项目说明
```

### 🔄 数据流

```
用户输入 → CLI解析 → 应用层处理 → Qwen-Agent框架 → 工具调用 → 结果返回
    ↑                                                              ↓
配置管理 ← 配置文件监控 ← 配置验证 ← MCP服务器 ← 工具执行 ← 工具选择
```

### 🧩 核心组件

#### 1. 配置管理系统
- **Settings Manager**: 环境变量和基础配置管理
- **MCP Config Loader**: MCP服务器配置加载和管理
- **Schema Validator**: JSON Schema配置验证
- **File Watcher**: 配置文件变更监控
- **Prompt Manager**: 多语言提示词管理

#### 2. 工具系统
- **Tool Registry**: 工具注册和发现机制
- **Tool Executor**: 工具执行和结果处理
- **MCP Client**: MCP协议客户端实现
- **Custom Tool Interface**: 自定义工具开发接口

#### 3. AI服务层
- **Qwen-Agent Integration**: 官方框架集成
- **Conversation Manager**: 对话状态管理
- **Memory Service**: 智能记忆功能
- **Model Adapter**: 多模型适配器

---

## 系统要求

### 💻 硬件要求

#### 最低配置
- **CPU**: 双核处理器 (2GHz+)
- **内存**: 4GB RAM
- **存储**: 1GB可用空间
- **网络**: 稳定的互联网连接

#### 推荐配置
- **CPU**: 四核处理器 (3GHz+)
- **内存**: 8GB+ RAM
- **存储**: 5GB+ 可用空间 (SSD推荐)
- **网络**: 高速宽带连接

### 🖥️ 软件要求

#### 操作系统
- **Linux**: Ubuntu 20.04+, CentOS 8+, Debian 11+
- **macOS**: macOS 11.0+ (Big Sur)
- **Windows**: Windows 10+ (WSL2推荐)

#### Python环境
- **Python版本**: 3.8.1+ (推荐3.11+)
- **包管理器**: uv (推荐) 或 pip
- **虚拟环境**: 强烈推荐使用虚拟环境

#### 必需工具
- **Git**: 版本控制 (2.0+)
- **curl**: HTTP客户端 (用于API测试)
- **Node.js**: 16+ (某些MCP服务器需要)

### 🔑 API要求

#### 必需的API密钥
- **DeepSeek API**: 主要LLM服务提供商
  - 获取地址: [https://platform.deepseek.com/](https://platform.deepseek.com/)
  - 免费额度: 每月一定量的免费调用

#### 可选的API密钥
- **OpenRouter API**: 备用LLM服务
  - 获取地址: [https://openrouter.ai/](https://openrouter.ai/)
  - 支持多种模型选择

### 🌐 网络要求

#### 网络连接
- **稳定性**: 稳定的互联网连接
- **带宽**: 最低1Mbps上下行
- **延迟**: <500ms到API服务器
- **防火墙**: 允许HTTPS出站连接

#### 域名访问
- `api.deepseek.com` - DeepSeek API服务
- `openrouter.ai` - OpenRouter API服务
- `github.com` - 代码仓库访问
- `pypi.org` - Python包下载

### 🔒 安全要求

#### 文件权限
- 项目目录需要读写权限
- 配置文件需要适当的权限设置
- 日志目录需要写入权限

#### API密钥安全
- API密钥必须安全存储
- 不要将密钥提交到版本控制
- 定期轮换API密钥

---

## 兼容性说明

### ✅ 已测试环境

| 操作系统 | Python版本 | 状态 | 备注 |
|---------|------------|------|------|
| Ubuntu 22.04 | 3.11 | ✅ 完全支持 | 推荐环境 |
| macOS 13 | 3.10 | ✅ 完全支持 | 开发环境 |
| Windows 11 | 3.9 | ✅ 基本支持 | WSL2推荐 |
| CentOS 8 | 3.8 | ⚠️ 有限支持 | 最低要求 |

### ⚠️ 已知限制

- **Python 3.7**: 不支持，需要3.8.1+
- **Windows原生**: 部分功能可能受限，推荐WSL2
- **ARM架构**: 基本支持，但某些依赖可能需要编译

### 🔄 版本兼容性

- **向后兼容**: 配置文件格式保持向后兼容
- **API版本**: 支持多个API版本
- **依赖更新**: 定期更新依赖包版本

---

## 快速开始

### 🚀 5分钟快速体验

按照以下步骤，您可以在5分钟内运行Qwen-Agent MVP：

#### 步骤1: 环境准备

```bash
# 检查Python版本 (需要3.8.1+)
python --version

# 安装uv包管理器 (推荐)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或者使用pip安装uv
pip install uv
```

#### 步骤2: 获取项目

```bash
# 克隆项目
git clone https://github.com/your-username/meta-agent.git
cd meta-agent

# 或者下载ZIP包并解压
# wget https://github.com/your-username/meta-agent/archive/main.zip
# unzip main.zip && cd meta-agent-main
```

#### 步骤3: 安装依赖

```bash
# 使用uv安装依赖 (推荐)
uv sync

# 或者使用pip安装
pip install -e .
```

#### 步骤4: 配置API密钥

```bash
# 复制环境变量模板
cp env.template .env

# 编辑.env文件，添加您的DeepSeek API密钥
# 使用您喜欢的编辑器，例如：
nano .env
# 或者
vim .env
# 或者
code .env
```

在`.env`文件中添加：
```env
DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
```

#### 步骤5: 运行应用

```bash
# 使用uv运行 (推荐)
uv run python main.py

# 或者直接运行
python main.py
```

### 📋 详细安装指南

#### 1. 环境要求检查

在开始之前，请确保您的系统满足以下要求：

```bash
# 检查Python版本
python --version
# 输出应该是: Python 3.8.1 或更高版本

# 检查pip版本
pip --version

# 检查Git版本
git --version

# 检查网络连接
curl -I https://api.deepseek.com
# 应该返回HTTP 200状态码
```

#### 2. 获取DeepSeek API密钥

1. **注册DeepSeek账户**
   - 访问 [https://platform.deepseek.com/](https://platform.deepseek.com/)
   - 点击"注册"创建新账户
   - 完成邮箱验证

2. **获取API密钥**
   - 登录后进入"API Keys"页面
   - 点击"Create new secret key"
   - 复制生成的API密钥（以`sk-`开头）
   - **重要**: 立即保存密钥，页面关闭后无法再次查看

3. **验证API密钥**
   ```bash
   # 测试API密钥是否有效
   curl -H "Authorization: Bearer your_api_key_here" \
        https://api.deepseek.com/v1/models
   ```

#### 3. 项目安装

##### 方式1: 使用uv (推荐)

```bash
# 1. 安装uv包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 重新加载shell配置
source ~/.bashrc  # 或 source ~/.zshrc

# 3. 克隆项目
git clone https://github.com/your-username/meta-agent.git
cd meta-agent

# 4. 创建虚拟环境并安装依赖
uv sync

# 5. 激活虚拟环境 (如果需要)
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

##### 方式2: 使用pip

```bash
# 1. 克隆项目
git clone https://github.com/your-username/meta-agent.git
cd meta-agent

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 4. 升级pip
pip install --upgrade pip

# 5. 安装项目依赖
pip install -e .
```

##### 方式3: 开发模式安装

```bash
# 克隆项目
git clone https://github.com/your-username/meta-agent.git
cd meta-agent

# 安装开发依赖
uv sync --group dev

# 或者使用pip
pip install -e ".[dev]"
```

#### 4. 环境配置

##### 创建环境变量文件

```bash
# 复制模板文件
cp env.template .env

# 查看模板内容
cat env.template
```

##### 配置必需的环境变量

编辑`.env`文件，添加以下配置：

```env
# 必需: DeepSeek API密钥
DEEPSEEK_API_KEY=sk-your-actual-deepseek-api-key-here

# 可选: OpenRouter API密钥 (备用LLM服务)
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here

# 可选: 是否使用DeepSeek R1推理模型
USE_DEEPSEEK_R1=false

# 可选: MCP服务器URL
MCP_SERVER_URL=https://mcp.context7.com/sse

# 可选: 日志级别
LOG_LEVEL=INFO
```

##### 验证配置

```bash
# 检查环境变量是否正确加载
uv run python -c "
from src.config.settings import Settings
config = Settings()
print('✅ 配置加载成功')
print(f'DeepSeek API密钥: {config.get(\"DEEPSEEK_API_KEY\")[:10]}...')
"
```

#### 5. 首次运行

##### 基本运行

```bash
# 使用uv运行 (推荐)
uv run python main.py

# 或者激活虚拟环境后运行
source .venv/bin/activate
python main.py

# 或者作为模块运行
uv run python -m src.main
```

##### 预期输出

成功启动后，您应该看到类似以下的输出：

```
🤖 Qwen-Agent MVP - 简洁直观实现
基于官方Qwen-Agent框架，使用最新DeepSeek-R1-0528推理模型

✅ 配置加载成功
🔧 工具初始化完成
🚀 Qwen-Agent MVP 已就绪！

输入 'help' 查看帮助，'quit' 退出程序
> 
```

##### 基本测试

```bash
# 测试基本对话
> 你好

# 测试计算功能
> 计算 2 + 3 * 4

# 测试记忆功能
> 我的名字是张三
> 我的名字是什么？

# 查看帮助
> help

# 退出程序
> quit
```

### 🔧 安装验证

#### 运行测试套件

```bash
# 运行基本功能测试
uv run python -m pytest tests/test_basic.py -v

# 运行端到端测试
uv run python -m pytest tests/test_e2e.py -v

# 运行完整测试套件
uv run python -m pytest tests/ -v

# 运行fail-fast验证测试
uv run python -m pytest tests/test_fail_fast_validation.py -v
```

#### 预期测试结果

```
tests/test_basic.py::test_environment_setup PASSED
tests/test_basic.py::test_config_loading PASSED
tests/test_basic.py::test_tool_functionality PASSED
tests/test_e2e.py::test_mvp_success_criteria_1 PASSED
tests/test_e2e.py::test_mvp_success_criteria_2 PASSED
tests/test_e2e.py::test_mvp_success_criteria_3 PASSED

========================= 6 passed in 2.34s =========================
```

#### 功能验证清单

- [ ] ✅ Python环境正确 (3.8.1+)
- [ ] ✅ 依赖包安装成功
- [ ] ✅ API密钥配置正确
- [ ] ✅ 应用程序正常启动
- [ ] ✅ 基本对话功能正常
- [ ] ✅ 计算器工具工作正常
- [ ] ✅ 内存管理功能正常
- [ ] ✅ 测试套件全部通过

### 🚨 常见安装问题

#### 问题1: Python版本过低

**错误信息**:
```
ERROR: This package requires Python >=3.8.1
```

**解决方案**:
```bash
# 安装Python 3.11 (推荐)
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv

# macOS (使用Homebrew)
brew install python@3.11

# 或者使用pyenv管理Python版本
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0
```

#### 问题2: uv安装失败

**错误信息**:
```
curl: command not found
```

**解决方案**:
```bash
# 方式1: 使用pip安装uv
pip install uv

# 方式2: 手动下载安装
wget https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz
tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
sudo mv uv /usr/local/bin/
```

#### 问题3: API密钥无效

**错误信息**:
```
ConfigError: DEEPSEEK_API_KEY is required but not found
```

**解决方案**:
```bash
# 1. 检查.env文件是否存在
ls -la .env

# 2. 检查API密钥格式
grep DEEPSEEK_API_KEY .env

# 3. 验证API密钥
curl -H "Authorization: Bearer your_api_key" \
     https://api.deepseek.com/v1/models
```

#### 问题4: 网络连接问题

**错误信息**:
```
ConnectionError: Failed to connect to api.deepseek.com
```

**解决方案**:
```bash
# 1. 检查网络连接
ping api.deepseek.com

# 2. 检查防火墙设置
curl -I https://api.deepseek.com

# 3. 使用代理 (如果需要)
export https_proxy=http://your-proxy:port
export http_proxy=http://your-proxy:port
```

#### 问题5: 权限错误

**错误信息**:
```
PermissionError: [Errno 13] Permission denied
```

**解决方案**:
```bash
# 1. 检查文件权限
ls -la .env

# 2. 修复权限
chmod 600 .env
chmod +x main.py

# 3. 检查目录权限
chmod 755 .
```

### 📱 不同平台的特殊说明

#### Linux (Ubuntu/Debian)

```bash
# 安装系统依赖
sudo apt update
sudo apt install python3-pip python3-venv git curl

# 如果使用Python 3.8
sudo apt install python3.8-venv python3.8-dev
```

#### macOS

```bash
# 安装Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install python git

# 如果遇到SSL证书问题
/Applications/Python\ 3.x/Install\ Certificates.command
```

#### Windows

```powershell
# 使用PowerShell (管理员模式)

# 安装Python (如果未安装)
# 从 https://python.org 下载并安装

# 安装Git
# 从 https://git-scm.com 下载并安装

# 克隆项目
git clone https://github.com/your-username/meta-agent.git
cd meta-agent

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -e .
```

#### WSL2 (推荐Windows用户使用)

```bash
# 在WSL2中按照Linux指南操作
# 安装WSL2: https://docs.microsoft.com/en-us/windows/wsl/install

# 更新WSL2
wsl --update

# 安装Ubuntu
wsl --install -d Ubuntu

# 在WSL2中运行
wsl
cd /mnt/c/path/to/meta-agent
```

### 🎯 下一步

安装完成后，您可以：

1. **阅读功能使用指南** → [功能使用指南](#功能使用指南)
2. **了解详细配置** → [详细配置](#详细配置)
3. **查看示例用例** → [最佳实践](#最佳实践)
4. **开发自定义工具** → [高级配置](#高级配置)

---

## 详细配置

### 🎯 配置文件

Qwen-Agent MVP的配置文件主要包括以下几个部分：

1. **环境配置**：包括系统环境变量和基础配置
2. **MCP配置**：包括MCP服务器配置和相关参数
3. **提示词配置**：包括多语言提示词模板和系统参数
4. **工具配置**：包括工具注册和发现机制

### 🎯 配置示例

以下是一个完整的配置文件示例：

```json
{
  "environment": {
    "DEEPSEEK_API_KEY": "sk-your-actual-deepseek-api-key-here",
    "OPENROUTER_API_KEY": "sk-or-v1-your-openrouter-key-here",
    "USE_DEEPSEEK_R1": false,
    "MCP_SERVER_URL": "https://mcp.context7.com/sse",
    "LOG_LEVEL": "INFO"
  },
  "mcp_servers": {
    "mcp_servers": [
      {
        "name": "DeepSeek",
        "url": "https://api.deepseek.com"
      },
      {
        "name": "OpenRouter",
        "url": "https://openrouter.ai"
      }
    ]
  },
  "prompts": {
    "system_prompts": {
      "en": "You are a helpful assistant.",
      "zh": "你是一个有帮助的助手。"
    },
    "locales": {
      "en": "English",
      "zh": "中文"
    }
  }
}
```

### 🎯 配置管理

Qwen-Agent MVP的配置管理主要包括以下几个部分：

1. **Settings Manager**：负责环境变量和基础配置管理
2. **MCP Config Loader**：负责MCP服务器配置加载和管理
3. **Schema Validator**：负责JSON Schema配置验证
4. **File Watcher**：负责配置文件变更监控
5. **Prompt Manager**：负责多语言提示词管理和系统参数设置

### 🎯 配置验证

Qwen-Agent MVP的配置验证主要包括以下几个部分：

1. **配置文件验证**：通过JSON Schema验证配置文件的格式和内容
2. **环境变量验证**：通过脚本检查环境变量的正确性
3. **API密钥验证**：通过脚本测试API密钥的有效性

---

## 功能使用指南

### 🎯 功能概述

Qwen-Agent MVP的主要功能包括：

1. **对话功能**：支持与AI助手进行自然语言对话
2. **工具功能**：支持多种工具的使用和集成
3. **记忆功能**：支持对话历史管理和记忆数据持久化
4. **多语言支持**：支持中英文界面切换和本地化提示

### 🎯 功能示例

以下是一个简单的功能示例：

1. **对话功能**：

```bash
# 与AI助手对话
> 你好

# 获取帮助
> help
```

2. **工具功能**：

```bash
# 使用计算器工具
> 计算 2 + 3 * 4
```

3. **记忆功能**：

```bash
# 保存对话历史
> 我的名字是张三

# 获取记忆
> 我的名字是什么？
```

### 🎯 功能使用步骤

1. **安装和配置**：按照[快速开始](#快速开始)部分进行安装和配置
2. **启动应用**：使用命令行启动Qwen-Agent MVP
3. **使用功能**：根据需要使用对话、工具和记忆功能

---

## 故障排除

### 🎯 常见问题

1. **安装问题**：
   - **错误信息**：`ERROR: This package requires Python >=3.8.1`
   - **解决方案**：安装Python 3.11或更高版本

2. **网络问题**：
   - **错误信息**：`ConnectionError: Failed to connect to api.deepseek.com`
   - **解决方案**：检查网络连接和防火墙设置

3. **权限问题**：
   - **错误信息**：`PermissionError: [Errno 13] Permission denied`
   - **解决方案**：检查文件权限和目录权限

### 🎯 解决方案

1. **安装问题**：
   - **解决方案**：安装Python 3.11或更高版本

2. **网络问题**：
   - **解决方案**：检查网络连接和防火墙设置

3. **权限问题**：
   - **解决方案**：检查文件权限和目录权限

---

## 高级配置

### 🎯 自定义工具

Qwen-Agent MVP支持自定义工具的开发和集成。以下是一个简单的自定义工具示例：

```python
# 自定义工具示例
def custom_tool(input_data):
    # 实现自定义工具逻辑
    return "自定义工具返回结果"

# 将自定义工具添加到工具系统
tool_registry.add_tool("custom_tool", custom_tool)
```

### 🎯 多语言支持

Qwen-Agent MVP支持多语言界面和本地化提示。以下是一个简单的多语言示例：

```python
# 多语言示例
def get_prompt(language):
    if language == "en":
        return "You are a helpful assistant."
    elif language == "zh":
        return "你是一个有帮助的助手。"
    else:
        raise ValueError("Unsupported language")

# 将多语言功能集成到系统中
prompt_manager.add_prompt("system_prompts", get_prompt)
```

### 🎯 配置验证

Qwen-Agent MVP的配置验证主要包括以下几个部分：

1. **配置文件验证**：通过JSON Schema验证配置文件的格式和内容
2. **环境变量验证**：通过脚本检查环境变量的正确性
3. **API密钥验证**：通过脚本测试API密钥的有效性

---

## API参考

### 🎯 API概述

Qwen-Agent MVP提供了以下API接口：

1. **对话API**：用于与AI助手进行对话
2. **工具API**：用于调用和集成自定义工具
3. **记忆API**：用于管理和检索对话历史

### 🎯 API示例

以下是一个简单的API示例：

1. **对话API**：

```bash
# 与AI助手对话
> 你好

# 获取帮助
> help
```

2. **工具API**：

```bash
# 使用计算器工具
> 计算 2 + 3 * 4
```

3. **记忆API**：

```bash
# 保存对话历史
> 我的名字是张三

# 获取记忆
> 我的名字是什么？
```

### 🎯 API使用步骤

1. **安装和配置**：按照[快速开始](#快速开始)部分进行安装和配置
2. **使用API**：根据需要使用对话、工具和记忆API

---

## 最佳实践

### 🎯 示例用例

以下是一个简单的示例用例：

1. **对话用例**：

```bash
# 与AI助手对话
> 你好

# 获取帮助
> help
```

2. **工具用例**：

```bash
# 使用计算器工具
> 计算 2 + 3 * 4
```

3. **记忆用例**：

```bash
# 保存对话历史
> 我的名字是张三

# 获取记忆
> 我的名字是什么？
```

### 🎯 最佳实践步骤

1. **安装和配置**：按照[快速开始](#快速开始)部分进行安装和配置
2. **使用示例用例**：根据需要使用示例用例

---

## 更新和维护

### 🎯 版本更新

Qwen-Agent MVP的版本更新主要包括以下几个部分：

1. **功能更新**：定期添加新功能和改进现有功能
2. **性能优化**：定期优化系统性能和响应速度
3. **安全更新**：定期修复安全漏洞和提升系统安全性

### 🎯 维护步骤

1. **安装和配置**：按照[快速开始](#快速开始)部分进行安装和配置
2. **定期更新**：定期检查和更新系统依赖包
3. **故障排查**：定期检查和解决系统故障

---

## 更新和维护

### 🎯 版本更新

Qwen-Agent MVP的版本更新主要包括以下几个部分：

1. **功能更新**：定期添加新功能和改进现有功能
2. **性能优化**：定期优化系统性能和响应速度
3. **安全更新**：定期修复安全漏洞和提升系统安全性

### 🎯 维护步骤

1. **安装和配置**：按照[快速开始](#快速开始)部分进行安装和配置
2. **定期更新**：定期检查和更新系统依赖包
3. **故障排查**：定期检查和解决系统故障

--- 