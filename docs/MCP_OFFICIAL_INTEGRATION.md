# 官方Qwen-Agent MCP集成

## 概述

根据[Qwen-Agent官方文档](https://github.com/QwenLM/Qwen-Agent/blob/main/examples/assistant_qwen3.py)，我们已经成功集成了官方的MCP (Model Context Protocol) 支持。

## 🎯 集成的MCP服务

我们严格遵循官方标准，只集成以下三个MCP服务器：

### 1. Time服务器 ⏰
- **功能**: 获取当前时间信息
- **时区**: 亚洲/上海
- **配置**: 
```json
{
    "command": "uvx",
    "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"]
}
```
- **使用场景**: 当用户询问"现在几点"、"当前时间"时自动调用

### 2. Fetch服务器 🌐
- **功能**: 网页内容抓取
- **用途**: 获取实时网页信息
- **配置**:
```json
{
    "command": "uvx", 
    "args": ["mcp-server-fetch"]
}
```
- **使用场景**: 当用户要求"抓取网页"、"获取网页内容"时自动调用

### 3. Memory服务器 💾
- **功能**: 外部内存存储
- **用途**: 持久化数据存储
- **配置**:
```json
{
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
}
```
- **使用场景**: 当用户需要"外部存储"、"持久化数据"时自动调用

> **注意**: 我们已移除所有非标准MCP工具，确保系统的稳定性和兼容性。

## 🐍 内置工具

### Code Interpreter
- **功能**: Python代码执行
- **支持**: 数据分析、绘图、计算
- **自动调用**: 当用户需要代码执行时

## 🚀 使用示例

### 时间查询
```
用户: 现在几点了？
助手: [自动调用time服务器获取当前时间]
```

### 网页抓取
```
用户: 抓取网页 https://www.ruanyifeng.com/blog/
助手: [自动调用fetch服务器获取网页内容]
```

### 代码执行
```
用户: 用Python画一个正弦波图
助手: [自动调用code_interpreter执行绘图代码]
```

## 📋 技术实现

### Agent配置
```python
tools = [
    'custom_save_info', 
    'custom_recall_info', 
    'custom_math_calc',
    {
        'mcpServers': {  # 官方MCP配置格式
            'time': {
                'command': 'uvx',
                'args': ['mcp-server-time', '--local-timezone=Asia/Shanghai']
            },
            'fetch': {
                'command': 'uvx',
                'args': ['mcp-server-fetch']
            },
            'memory': {
                'command': 'npx',
                'args': ['-y', '@modelcontextprotocol/server-memory']
            }
        }
    },
    'code_interpreter',  # 内置代码解释器工具
]

agent = Assistant(
    llm=llm_cfg,
    system_message=system_message,
    function_list=tools,
    name='DeepSeek增强版AI助手',
    description='基于DeepSeek模型的智能助手，支持记忆、计算、MCP服务和代码执行功能'
)
```

## ✅ 优势

1. **官方支持**: 使用Qwen-Agent原生MCP支持，稳定可靠
2. **自动调用**: 根据用户需求智能选择合适的工具
3. **丰富功能**: 时间、网页、内存、代码执行全覆盖
4. **标准协议**: 遵循MCP标准，兼容性好

## 🔧 依赖要求

```bash
# 安装完整的Qwen-Agent功能包
uv add "qwen-agent[gui,rag,code_interpreter,mcp]"
```

## 📝 注意事项

- MCP服务器会根据需要自动启动
- 代码执行在沙盒环境中进行
- 网页抓取遵循robots.txt规则
- 时间服务器使用亚洲/上海时区

---

*基于Qwen-Agent官方示例实现，参考: https://github.com/QwenLM/Qwen-Agent/blob/main/examples/assistant_qwen3.py* 