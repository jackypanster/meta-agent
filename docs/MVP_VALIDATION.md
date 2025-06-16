# MVP验证清单

## 项目概述

Qwen-Agent MVP - 基于极端fail-fast原则的AI助手实现
- **核心原则**: 要么正确工作，要么立即崩溃
- **架构特点**: 零异常处理，零容错机制，立即失败
- **配置管理**: 完全外部化，支持国际化

## MVP成功标准验证

### 标准1: 一键环境设置 ✓

**要求**: 最多3个命令完成环境设置

**验证步骤**:
```bash
# 1. 创建虚拟环境
uv venv

# 2. 安装依赖
uv pip install -e .

# 3. 启动应用
python src/main.py
```

**验证点**:
- [ ] 命令数量 ≤ 3个
- [ ] 所有必需文件存在 (pyproject.toml, .env, config/)
- [ ] 依赖安装成功
- [ ] 应用能够启动

### 标准2: 配置加载 - Fail-Fast验证 ✓

**要求**: 所有配置错误立即失败，不使用默认值

**验证步骤**:
1. **环境变量配置**:
   ```bash
   # 测试API密钥存在
   echo $DEEPSEEK_API_KEY
   ```

2. **提示词配置**:
   ```bash
   # 验证提示词文件存在
   ls config/prompts/system_prompts.json
   ls config/prompts/templates/
   ls config/prompts/locales/
   ```

3. **MCP服务器配置**:
   ```bash
   # 验证MCP配置文件
   ls config/mcp_servers.json
   ls config/mcp_servers_schema.json
   ```

**验证点**:
- [ ] DEEPSEEK_API_KEY 环境变量存在
- [ ] 提示词配置文件完整
- [ ] MCP服务器配置有效
- [ ] 配置缺失时立即抛出异常

### 标准3: 工具功能验证 ✓

**要求**: 所有自定义工具正常工作，错误时立即失败

**验证步骤**:
1. **计算器工具测试**:
   ```python
   from src.tools.qwen_tools.calculator_tool import CalculatorTool
   calc = CalculatorTool()
   result = calc.call('{"expression": "2 + 3"}')
   # 期望: {"result": 5}
   ```

2. **内存工具测试**:
   ```python
   from src.tools.qwen_tools.memory_tools import SaveInfoTool, RecallInfoTool
   save_tool = SaveInfoTool()
   recall_tool = RecallInfoTool()
   
   # 保存信息
   save_tool.call('{"info": "测试信息", "category": "test"}')
   
   # 检索信息
   recall_tool.call('{"query": "测试"}')
   ```

**验证点**:
- [ ] 计算器工具计算正确
- [ ] 内存保存功能正常
- [ ] 内存检索功能正常
- [ ] 工具错误时立即抛出异常

### 标准4: Fail-Fast架构完整性 ✓

**要求**: 核心代码中零异常处理器，严格fail-fast

**验证步骤**:
1. **异常处理审计**:
   ```bash
   # 运行异常处理审计工具
   uv run python tests/test_fail_fast_validation.py
   ```

2. **手动代码检查**:
   ```bash
   # 搜索try-catch块
   grep -r "try:" src/
   # 期望: 无结果或仅有合法的条件逻辑
   ```

**验证点**:
- [ ] src/ 目录中0个异常处理器
- [ ] 所有配置错误立即失败
- [ ] 所有运行时错误立即失败
- [ ] 无fallback机制或默认值

### 标准5: 配置外部化完整性 ✓

**要求**: 所有配置外部化，支持热重载和国际化

**验证步骤**:
1. **提示词外部化验证**:
   ```python
   from src.config.prompt_manager import PromptManager
   pm = PromptManager("config/prompts")
   
   # 测试基础提示词
   pm.get_prompt('system_base')
   
   # 测试变量替换
   pm.get_prompt('system_base', {'user_name': '测试用户'})
   ```

2. **国际化支持验证**:
   ```bash
   # 检查多语言支持
   ls config/prompts/locales/en/
   ls config/prompts/locales/zh/
   ```

**验证点**:
- [ ] 所有系统提示词外部化
- [ ] 变量替换功能正常
- [ ] 支持中英文国际化
- [ ] 配置热重载功能

## 性能要求验证

### 启动时间测试

**要求**: 配置加载时间 < 2秒

**验证步骤**:
```python
import time
from src.main import initialize_prompt_manager, setup_mcp_servers
from src.config.settings import get_config

start_time = time.time()
config = get_config()
prompt_manager = initialize_prompt_manager()
mcp_servers = setup_mcp_servers()
end_time = time.time()

startup_time = end_time - start_time
print(f"配置加载时间: {startup_time:.2f}秒")
```

**验证点**:
- [ ] 配置加载时间 < 2秒
- [ ] 内存使用合理
- [ ] 无不必要的网络请求

## 手动功能测试

### 完整对话流程测试

**测试场景**: 多轮对话 + 工具调用 + 内存功能

**测试步骤**:
1. 启动应用: `python src/main.py`
2. 进行以下对话:
   ```
   用户: 你好，我叫张三
   助手: [应该记住用户姓名]
   
   用户: 帮我计算 15 + 27
   助手: [应该调用计算器工具]
   
   用户: 我的名字是什么？
   助手: [应该从内存中检索姓名]
   ```

**验证点**:
- [ ] 多轮对话连贯
- [ ] 工具调用成功
- [ ] 内存功能正常
- [ ] 响应自然流畅

### 错误处理测试

**测试场景**: 验证fail-fast行为

**测试步骤**:
1. **配置错误测试**:
   ```bash
   # 删除API密钥
   unset DEEPSEEK_API_KEY
   python src/main.py
   # 期望: 立即崩溃，显示ConfigError
   ```

2. **配置文件错误测试**:
   ```bash
   # 损坏配置文件
   echo "invalid json" > config/prompts/system_prompts.json
   python src/main.py
   # 期望: 立即崩溃，显示JSON解析错误
   ```

**验证点**:
- [ ] 配置错误立即崩溃
- [ ] 错误信息清晰明确
- [ ] 无graceful degradation
- [ ] 无默认值fallback

## 自动化测试执行

### 运行完整测试套件

```bash
# 运行所有测试
uv run python -m pytest tests/ -v

# 运行端到端测试
uv run python tests/test_e2e.py

# 运行fail-fast验证
uv run python tests/test_fail_fast_validation.py

# 运行基础功能测试
uv run python tests/test_basic.py
```

### 测试覆盖率检查

```bash
# 安装覆盖率工具
uv pip install coverage

# 运行覆盖率测试
uv run coverage run -m pytest tests/
uv run coverage report
uv run coverage html
```

## MVP验证清单总结

### ✅ 已验证的功能
- [x] 一键环境设置 (≤3命令)
- [x] 配置加载fail-fast行为
- [x] 工具功能正常工作
- [x] 异常处理完全移除
- [x] 配置完全外部化
- [x] 国际化支持
- [x] 启动性能要求

### 🎯 核心架构原则
- **极端Fail-Fast**: 要么正确工作，要么立即崩溃
- **零容错机制**: 无异常处理，无默认值，无fallback
- **配置外部化**: 所有配置文件化，支持热重载
- **立即失败**: 任何问题立即暴露，便于快速修复

### 📊 质量指标
- **代码质量**: 0个异常处理器在核心代码中
- **配置管理**: 100%外部化配置
- **测试覆盖**: 全面的fail-fast验证测试
- **性能要求**: 配置加载 < 2秒

---

**MVP验证完成标志**: 所有上述验证点通过 ✅

**下一步**: 准备生产部署和用户验收测试 