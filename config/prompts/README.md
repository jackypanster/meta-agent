# 系统提示词配置说明

## 目录结构

```
config/prompts/
├── README.md                    # 本说明文档
├── prompts_schema.json          # JSON Schema 验证规则
├── system_prompts.json          # 主系统提示词配置
├── templates/                   # 提示词模板
│   ├── conversation.json        # 对话相关提示词
│   ├── tool_calling.json        # 工具调用提示词
│   └── error_handling.json      # 错误处理提示词
└── locales/                     # 多语言支持
    ├── en/                      # 英文版本
    │   └── system_prompts.json
    └── zh/                      # 中文版本
        └── system_prompts.json
```

## 配置文件格式

### 主要字段说明

- `version`: 配置文件版本号，使用语义化版本控制
- `default_locale`: 默认语言环境
- `prompts`: 提示词定义对象
- `metadata`: 配置文件元数据

### 提示词定义格式

```json
{
  "prompt_key": {
    "content": "提示词内容，支持 $variable 变量替换",
    "description": "提示词用途说明",
    "variables": ["variable1", "variable2"],
    "category": "system|tool_calling|memory|error_handling|conversation",
    "enabled": true,
    "version": "1.0.0",
    "tags": ["tag1", "tag2"]
  }
}
```

## 变量替换

提示词支持使用 `$variable_name` 语法进行变量替换：

- `$user_name`: 用户名称
- `$context`: 上下文信息
- `$available_tools`: 可用工具列表
- `$tool_name`: 工具名称
- `$tool_result`: 工具执行结果
- `$error_message`: 错误消息

## 分类说明

- `system`: 系统级提示词，定义AI助手的基本行为
- `tool_calling`: 工具调用相关的提示词
- `memory`: 记忆管理相关提示词
- `error_handling`: 错误处理提示词
- `conversation`: 对话流程相关提示词

## 使用示例

```python
from qwen_agent_mvp.config.prompt_manager import PromptManager

# 初始化提示词管理器
prompt_manager = PromptManager("config/prompts")

# 获取基本系统提示词
system_prompt = prompt_manager.get_prompt("system_base")

# 获取带变量的提示词
personalized_prompt = prompt_manager.get_prompt("system_with_user_context", {
    "user_name": "张三",
    "context": "正在进行数据分析任务"
})

# 热重载配置
prompt_manager.reload_prompts()
```

## 验证规则

配置文件需要通过 JSON Schema 验证：

1. 所有必需字段必须存在
2. 版本号必须符合语义化版本格式
3. 变量名必须符合标识符规范
4. 分类必须为预定义值之一
5. 内容长度必须满足最小要求

## 最佳实践

1. **版本控制**: 修改提示词时更新版本号
2. **变量命名**: 使用描述性的变量名
3. **分类组织**: 按功能分类组织提示词
4. **多语言支持**: 为不同语言环境提供对应版本
5. **文档更新**: 修改后及时更新说明文档

## 配置验证

可以使用以下命令验证配置文件格式：

```bash
# 验证主配置文件
uv run python -m json.validator config/prompts/prompts_schema.json config/prompts/system_prompts.json

# 验证模板文件
uv run python -m json.validator config/prompts/prompts_schema.json config/prompts/templates/conversation.json
``` 