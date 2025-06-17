# Qwen-Agent SSE协议MCP支持Bug跟踪文档

## 📋 问题概述

**发现日期**: 2025年1月17日  
**问题类型**: Qwen-Agent框架SSE协议MCP服务器支持bug  
**影响范围**: 无法使用SSE协议连接MCP服务器  
**状态**: 🔴 待修复 (官方正在开发修复)

## 🚨 核心问题

### 问题描述
Qwen-Agent框架的MCP管理器(`qwen_agent.tools.mcp_manager.py`)假设所有MCP服务器都使用命令行启动方式，导致在处理SSE协议的MCP服务器时出现`KeyError: 'command'`错误。

### 错误信息
```python
KeyError: 'command'
File "qwen_agent/tools/mcp_manager.py", line XXX
server_params = StdioServerParameters(command=mcp_server['command'], ...)
```

### 根本原因
- **命令行MCP服务器**: 使用`command`和`args`字段
- **SSE协议MCP服务器**: 使用`type: "sse"`和`config: {url: "..."}`字段
- **框架bug**: MCPManager只处理命令行格式，不支持SSE格式

## 🔍 我们的发现过程

### 1. 初始尝试 (失败)
```json
{
  "k8s-mcp": {
    "type": "sse",
    "config": {
      "url": "http://ncpdev.gf.com.cn:31455/sse"
    },
    "enabled": true,
    "description": "Kubernetes集群管理MCP服务，基于SSE协议",
    "category": "kubernetes"
  }
}
```

**结果**: JSON Schema验证失败，因为Schema只支持命令行格式

### 2. 扩展JSON Schema (成功)
我们扩展了`config/mcp_servers_schema.json`以支持两种格式：
- 命令行格式: `command` + `args` (oneOf第一个选项)
- SSE格式: `type` + `config` (oneOf第二个选项)

### 3. 修改代码逻辑 (部分成功)
在`src/agent_setup.py`中添加了SSE协议支持逻辑：
```python
if server_config.get('type') == 'sse':
    # SSE服务器配置
    config_url = server_config.get('config', {}).get('url')
    if not config_url:
        raise MCPConfigError(f"❌ SSE服务器 '{name}' 缺少config.url字段")
    
    mcp_servers[name] = {
        "type": "sse",
        "config": {"url": config_url}
    }
else:
    # 传统命令行服务器配置  
    mcp_servers[name] = {
        "command": server_config['command'],
        "args": server_config['args']
    }
```

### 4. 发现框架内部bug (关键发现!)
即使我们的配置正确，Qwen-Agent框架内部的`MCPManager`仍然假设所有服务器都有`command`字段，导致SSE服务器配置失败。

## 🌍 社区验证

### 相同问题在多个项目中被报告

1. **Amazon Q Developer CLI** - [Issue #1663](https://github.com/aws/amazon-q-developer-cli/issues/1663)
   - 错误: "missing field `command`" 
   - 问题: Q fails to work with MCP servers running in SSE mode

2. **Langflow** - [Issue #8429](https://github.com/langflow-ai/langflow/issues/8429)
   - 错误: "Error connecting MCP server via SSE transport"
   - 状态码: 405 (Method Not Allowed)

3. **n8n Community** - 多个报告
   - "Could not connect to your MCP server"
   - "MCP error -32001: Request timed out"
   - 解决方案: 禁用gzip压缩

4. **Microsoft Copilot Studio**
   - 已知问题: "SSE full uri response known issue"
   - 要求: 完全限定的URI而不是相对路径

### 官方修复进展

**🎯 关键发现**: [Qwen-Agent PR #597](https://github.com/QwenLM/Qwen-Agent/pulls)
- 标题: "feat: add a demo for sse or streamable-http mcp"
- 状态: 开发中
- 说明: 官方正在积极修复SSE协议支持

## 📝 技术细节

### 正确的SSE配置格式 (根据官方文档)
```json
{
  "type": "sse",
  "config": {
    "url": "http://localhost:8080/sse"
  }
}
```

### Qwen-Agent期望的配置格式
```python
# 当前框架期望 (仅支持命令行)
{
  "command": "uvx",
  "args": ["mcp-server-fetch"]
}

# 应该支持但目前不支持 (SSE协议)
{
  "type": "sse", 
  "config": {"url": "http://localhost:8080/sse"}
}
```

## 🛠️ 我们的临时解决方案

### 1. 扩展了JSON Schema
- ✅ 为将来的SSE支持做好准备
- ✅ 保持向后兼容性
- ✅ 支持两种配置格式

### 2. 增强了配置加载逻辑
- ✅ 能够识别和处理SSE配置
- ✅ 提供清晰的错误信息
- ✅ 支持混合配置 (命令行 + SSE)

### 3. 暂时移除SSE配置
- ✅ 避免程序崩溃
- ✅ 保持现有功能正常
- ✅ 等待官方修复

## 📅 跟踪计划

### 短期行动 (1-2周)
- [ ] 每周检查 [PR #597](https://github.com/QwenLM/Qwen-Agent/pulls) 状态
- [ ] 关注Qwen-Agent发布说明
- [ ] 测试新版本的SSE支持

### 中期行动 (1-2月)
- [ ] 一旦修复合并，立即测试k8s-mcp配置
- [ ] 验证我们的JSON Schema扩展与官方修复的兼容性
- [ ] 更新文档和配置示例

### 长期行动 (持续)
- [ ] 监控SSE协议在AI生态系统中的采用情况
- [ ] 评估是否需要向Qwen-Agent项目贡献代码
- [ ] 分享经验给社区

## 🔗 相关链接

### 官方资源
- [Qwen-Agent GitHub](https://github.com/QwenLM/Qwen-Agent)
- [PR #597 - SSE支持](https://github.com/QwenLM/Qwen-Agent/pulls)
- [MCP官方规范](https://modelcontextprotocol.io/)

### 社区问题报告
- [Amazon Q CLI Issue #1663](https://github.com/aws/amazon-q-developer-cli/issues/1663)
- [Langflow Issue #8429](https://github.com/langflow-ai/langflow/issues/8429)
- [n8n Community SSE问题](https://community.n8n.io/t/error-could-not-connect-to-your-mcp-server-when-integrating-external-tool-via-sse-in-ai-agent/100957)

### 技术参考
- [SSE协议规范](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [MCP Streamable HTTP](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http)

## 💡 经验总结

### 关键洞察
1. **SSE协议是MCP的未来方向** - 更安全、更高效、更易扩展
2. **框架内部假设很危险** - 应该支持多种传输协议
3. **社区验证很重要** - 我们的发现得到了广泛验证
4. **提前准备很有价值** - 我们的Schema扩展为将来做好了准备

### 技术教训
1. **fail-fast原则的价值** - 立即暴露配置问题，避免隐藏错误
2. **模块化设计的重要性** - 配置、验证、加载分离使问题定位更容易
3. **社区调研的必要性** - 避免重复造轮子，学习他人经验

---

**最后更新**: 2025年1月17日  
**下次检查**: 2025年1月24日  
**负责人**: AI助手 + 用户协作团队 