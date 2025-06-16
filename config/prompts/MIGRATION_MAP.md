# 提示词迁移映射文档

本文档记录了从硬编码提示词到配置文件的迁移映射关系。

## 迁移概览

迁移日期：2025-06-16
版本：1.0.0
状态：✅ 已完成

## 主要系统提示词

### 主系统提示词
- **原位置**: `src/main.py:245-273`
- **新位置**: `config/prompts/system_prompts.json`
- **配置键**: `main_system_prompt` -> `system_base`
- **描述**: 主要的系统提示词，定义AI助手的核心功能和行为准则
- **变量支持**: 无
- **状态**: ✅ 已迁移

### Agent配置

#### Agent名称
- **原位置**: `src/main.py:278`
- **新位置**: `config/prompts/system_prompts.json`
- **配置键**: `agent_name`
- **内容**: `"DeepSeek增强版AI助手"`
- **变量支持**: 无
- **状态**: ✅ 已迁移

#### Agent描述
- **原位置**: `src/main.py:279`
- **新位置**: `config/prompts/system_prompts.json` 
- **配置键**: `agent_description`
- **内容**: `"基于DeepSeek模型的智能助手，支持记忆、计算、MCP服务和代码执行功能"`
- **变量支持**: 无
- **状态**: ✅ 已迁移

## 错误处理提示词

### 网络错误
- **原位置**: `src/main.py:361`
- **新位置**: `config/prompts/templates/error_handling.json`
- **配置键**: `network_error`
- **变量支持**: `error_details`
- **状态**: ✅ 已迁移

### API错误
- **原位置**: `src/main.py:363`
- **新位置**: `config/prompts/templates/error_handling.json`
- **配置键**: `api_error`
- **变量支持**: `error_details`
- **状态**: ✅ 已迁移

### DeepSeek R1模型错误
- **原位置**: `src/main.py:369`
- **新位置**: `config/prompts/templates/error_handling.json`
- **配置键**: `deepseek_r1_error`
- **变量支持**: 无
- **状态**: ✅ 已迁移

### 通用错误
- **原位置**: `src/main.py:374`
- **新位置**: `config/prompts/templates/error_handling.json`
- **配置键**: `generic_error`
- **变量支持**: `error_message`
- **状态**: ✅ 已迁移

### 模型配置错误
- **原位置**: `src/main.py:232`
- **新位置**: `config/prompts/templates/error_handling.json`
- **配置键**: `model_config_error`
- **变量支持**: `error_details`
- **状态**: ✅ 已迁移

### Agent创建错误
- **原位置**: `src/main.py:284`
- **新位置**: `config/prompts/templates/error_handling.json`
- **配置键**: `agent_creation_error`
- **变量支持**: `error_details`
- **状态**: ✅ 已迁移

### 初始化错误
- **原位置**: `src/main.py:234`
- **新位置**: `config/prompts/templates/error_handling.json`
- **配置键**: `initialization_error`
- **变量支持**: `error_details`
- **状态**: ✅ 已迁移

### 程序退出错误
- **原位置**: `src/main.py:389-394`
- **新位置**: `config/prompts/templates/error_handling.json`
- **配置键**: `program_exit_error`
- **变量支持**: `error_details`
- **状态**: ✅ 已迁移

## 用户界面消息

### 欢迎界面
- **原位置**: `src/ui/helpers.py:23`
- **新位置**: `config/prompts/templates/ui_messages.json`
- **配置键**: `welcome_title`
- **内容**: `"🤖 Qwen-Agent MVP - DeepSeek 增强版"`
- **状态**: ✅ 已迁移

### 欢迎副标题
- **原位置**: `src/ui/helpers.py:25`
- **新位置**: `config/prompts/templates/ui_messages.json`
- **配置键**: `welcome_subtitle`
- **变量支持**: `model_info`
- **状态**: ✅ 已迁移

### 功能列表
- **原位置**: `src/ui/helpers.py:27-31`
- **新位置**: `config/prompts/templates/ui_messages.json`
- **配置键**: `features_list`
- **状态**: ✅ 已迁移

### DeepSeek R1提示
- **原位置**: `src/ui/helpers.py:33`
- **新位置**: `config/prompts/templates/ui_messages.json`
- **配置键**: `deepseek_r1_hint`
- **状态**: ✅ 已迁移

### 示例对话
- **原位置**: `src/ui/helpers.py:35-42`
- **新位置**: `config/prompts/templates/ui_messages.json`
- **配置键**: `example_conversations`
- **状态**: ✅ 已迁移

### 帮助命令
- **原位置**: `src/ui/helpers.py:48-51`
- **新位置**: `config/prompts/templates/ui_messages.json`
- **配置键**: `help_commands`
- **状态**: ✅ 已迁移

### AI功能介绍
- **原位置**: `src/ui/helpers.py:52-55`
- **新位置**: `config/prompts/templates/ui_messages.json`
- **配置键**: `ai_features`
- **状态**: ✅ 已迁移

### 对话开始
- **原位置**: `src/main.py:294`
- **新位置**: `config/prompts/templates/ui_messages.json`
- **配置键**: `conversation_start`
- **变量支持**: `model_display`
- **状态**: ✅ 已迁移

### 加载提示
- **原位置**: 
  - `src/main.py:227` (AI加载)
  - `src/main.py:240` (MCP加载)
- **新位置**: `config/prompts/templates/ui_messages.json`
- **配置键**: `ai_loading`, `mcp_loading`
- **状态**: ✅ 已迁移

### 成功提示
- **原位置**: `src/main.py:282`
- **新位置**: `config/prompts/templates/ui_messages.json`
- **配置键**: `ai_success`
- **状态**: ✅ 已迁移

### 其他UI元素
- **原位置**: 
  - `src/main.py:324` (AI回复前缀)
  - `src/main.py:298,310` (告别消息)
  - `src/main.py:387` (中断消息)
- **新位置**: `config/prompts/templates/ui_messages.json`
- **配置键**: `ai_response_prefix`, `goodbye_message`, `interrupt_message`
- **状态**: ✅ 已迁移

## 变量替换支持

以下配置项支持变量替换：

1. `system_with_user_context` - 支持 `user_name`, `context`
2. `welcome_subtitle` - 支持 `model_info`
3. `conversation_start` - 支持 `model_display`
4. 所有错误处理提示词 - 支持相应的错误详情变量

## 使用示例

```python
from src.config.prompt_manager import PromptManager

# 初始化管理器
pm = PromptManager()

# 获取系统提示词
system_prompt = pm.get_prompt("system_base")

# 获取带变量的提示词
welcome = pm.get_prompt("welcome_subtitle", {"model_info": "DeepSeek-V3"})

# 获取错误提示词
error_msg = pm.get_prompt("network_error", {"error_details": "连接超时"})
```

## 验证清单

- [x] 所有硬编码字符串已识别并记录
- [x] 主要系统提示词已迁移到配置文件
- [x] 错误处理消息已分类迁移
- [x] 用户界面文本已提取
- [x] 变量替换功能已配置
- [x] 迁移映射已记录
- [x] 配置文件结构符合Schema规范
- [x] 所有配置项都包含适当的元数据

## 后续步骤

1. 更新应用代码以使用PromptManager
2. 移除原始硬编码字符串
3. 测试所有功能正常工作
4. 验证变量替换功能
5. 更新文档和示例 