# 私有K8S MCP服务器配置指南

## 🔒 安全配置说明

本文档说明如何安全地配置私有化部署的Kubernetes MCP服务器，避免在公共代码仓库中暴露内网地址。

## 📋 配置步骤

### 1. 环境变量配置

在项目根目录的 `.env` 文件中添加你的私有K8S MCP服务器地址：

```bash
# 私有K8S MCP服务器配置
K8S_MCP=http://your-internal-k8s-cluster:31455/sse
```

**重要**: `.env` 文件已被gitignore保护，不会提交到远程仓库。

### 2. MCP服务器配置

在 `config/mcp_servers.json` 中添加K8S MCP服务器配置：

```json
{
  "servers": {
    "k8s-mcp": {
      "type": "sse",
      "config": {
        "url": "http://your-internal-k8s-cluster:31455/sse"
      },
      "enabled": true,
      "description": "私有Kubernetes集群管理MCP服务",
      "category": "kubernetes"
    }
  }
}
```

### 3. 动态配置加载 (推荐)

为了更好的安全性，可以使用环境变量动态加载：

```json
{
  "servers": {
    "k8s-mcp": {
      "type": "sse", 
      "config": {
        "url": "${K8S_MCP}"
      },
      "enabled": true,
      "description": "私有Kubernetes集群管理MCP服务",
      "category": "kubernetes"
    }
  }
}
```

## 🛡️ 安全最佳实践

### ✅ 已实施的安全措施

1. **`.env` 文件保护**
   - 已添加到 `.gitignore`
   - 不会被提交到远程仓库
   - 包含所有敏感配置

2. **示例文件清理**
   - 所有示例配置使用 `example.com` 占位符
   - 文档中使用通用地址示例
   - 避免真实内网地址泄露

3. **模板化配置**
   - 提供 `env.template` 模板文件
   - 开发者可复制并填入真实配置
   - 保持代码仓库清洁

### 🔍 安全检查清单

- [ ] 确认 `.env` 文件在 `.gitignore` 中
- [ ] 检查所有配置文件中无真实内网地址
- [ ] 验证环境变量正确加载
- [ ] 测试MCP服务器连接

## 🚀 启用步骤

### 当前状态 (等待Qwen-Agent修复)

目前Qwen-Agent框架尚未完全支持SSE协议，需要等待官方PR #597合并。

### 准备就绪后的启用步骤

1. **更新Qwen-Agent**
   ```bash
   uv add qwen-agent@latest
   ```

2. **配置环境变量**
   ```bash
   echo "K8S_MCP=http://your-internal-k8s:31455/sse" >> .env
   ```

3. **启用MCP服务器**
   在 `config/mcp_servers.json` 中设置 `"enabled": true`

4. **测试连接**
   ```bash
   uv run python src/main.py
   ```

## 📝 配置示例

### SSE协议配置
```json
{
  "k8s-mcp-sse": {
    "type": "sse",
    "config": {
      "url": "${K8S_MCP}"
    },
    "enabled": true,
    "description": "K8S集群管理 (SSE协议)",
    "category": "kubernetes"
  }
}
```

### Streamable HTTP协议配置  
```json
{
  "k8s-mcp-http": {
    "type": "streamable-http",
    "config": {
      "url": "${K8S_MCP_HTTP}"
    },
    "enabled": true,
    "description": "K8S集群管理 (HTTP协议)",
    "category": "kubernetes"
  }
}
```

## 🔗 相关文档

- [MCP配置系统文档](MCP_CONFIGURATION_SYSTEM.md)
- [SSE Bug跟踪文档](QWEN_AGENT_SSE_BUG_TRACKING.md)
- [安全指南](../SECURITY.md)

---

**注意**: 本文档中的所有地址都是示例，请替换为你的实际内网地址。确保不要将真实的内网地址提交到公共代码仓库。 