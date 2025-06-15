# MCP 服务器配置目录

此目录包含 MCP (Model Context Protocol) 服务器的配置文件。

## 文件说明

### `mcp_servers.json`
主配置文件，定义了当前启用的 MCP 服务器。应用程序会读取此文件来加载 MCP 服务器。

### `mcp_servers_example.json`
示例配置文件，展示了如何配置各种类型的 MCP 服务器，包括：
- 时间服务器 (time)
- 网页抓取服务器 (fetch)
- 内存存储服务器 (memory)
- 文件系统服务器 (filesystem)
- 数据库服务器 (sqlite, postgres)
- API集成服务器 (github)
- 搜索引擎服务器 (brave_search)

### `mcp_servers_schema.json`
JSON Schema 文件，用于验证配置文件的格式和内容。

## 配置文件结构

```json
{
  "version": "1.0",
  "description": "配置文件描述",
  "servers": {
    "服务器名称": {
      "command": "启动命令",
      "args": ["命令参数"],
      "enabled": true,
      "description": "服务器描述",
      "category": "服务器分类",
      "timeout": 30,
      "env": {
        "环境变量名": "环境变量值"
      }
    }
  },
  "global_settings": {
    "default_timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "max_concurrent_servers": 10,
    "log_level": "INFO",
    "enable_hot_reload": true
  },
  "categories": {
    "分类名": {
      "description": "分类描述",
      "color": "颜色"
    }
  }
}
```

## 使用方法

### 1. 启用/禁用服务器
修改服务器配置中的 `enabled` 字段：
```json
{
  "servers": {
    "time": {
      "enabled": true   // 启用
    },
    "github": {
      "enabled": false  // 禁用
    }
  }
}
```

### 2. 添加新服务器
在 `servers` 对象中添加新的服务器配置：
```json
{
  "servers": {
    "my_custom_server": {
      "command": "npx",
      "args": ["-y", "@my/custom-mcp-server"],
      "enabled": true,
      "description": "我的自定义MCP服务器",
      "category": "custom",
      "timeout": 60
    }
  }
}
```

### 3. 配置环境变量
某些服务器需要API密钥或其他环境变量：
```json
{
  "servers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "enabled": true,
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-token"
      }
    }
  }
}
```

### 4. 调整全局设置
修改 `global_settings` 来调整全局行为：
```json
{
  "global_settings": {
    "default_timeout": 45,     // 默认超时时间
    "retry_attempts": 5,       // 重试次数
    "log_level": "DEBUG",      // 日志级别
    "enable_hot_reload": true  // 启用热重载
  }
}
```

## 服务器分类

- **utility**: 实用工具类服务 (时间、计算等)
- **network**: 网络访问类服务 (网页抓取、API调用等)
- **storage**: 数据存储类服务 (内存、文件系统等)
- **database**: 数据库操作类服务 (SQLite、PostgreSQL等)
- **api**: 第三方API集成服务 (GitHub、Twitter等)
- **search**: 搜索引擎类服务 (Brave、Google等)

## 热重载功能

当 `enable_hot_reload` 设置为 `true` 时，应用程序会监控配置文件的变化并自动重新加载配置，无需重启应用程序。

## 注意事项

1. **JSON格式**: 配置文件必须是有效的JSON格式
2. **服务器名称**: 服务器名称只能包含字母、数字、下划线和连字符，且必须以字母开头
3. **环境变量**: 敏感信息（如API密钥）应通过环境变量配置，而不是直接写在配置文件中
4. **超时设置**: 超时时间单位为秒，建议根据服务器响应时间合理设置
5. **依赖安装**: 确保相关的MCP服务器包已经安装（通过npm或其他包管理器）

## 故障排除

### 配置文件验证错误
使用 JSON Schema 验证工具检查配置文件格式：
```bash
# 使用在线工具或本地工具验证
jsonschema -i mcp_servers.json mcp_servers_schema.json
```

### 服务器启动失败
1. 检查命令和参数是否正确
2. 确认相关包已安装
3. 检查环境变量是否正确设置
4. 查看应用程序日志获取详细错误信息

### 热重载不工作
1. 确认 `enable_hot_reload` 设置为 `true`
2. 检查文件权限
3. 确认配置文件路径正确 