# 🔐 快速安全指南

## 立即开始

### 🚨 首次设置（必做）
```bash
# 1. 创建环境变量文件
cp env.template .env
# 然后编辑 .env 文件，填入真实API密钥

# 2. 创建MCP配置（如果使用Cursor）
cp .cursor/mcp.json.template .cursor/mcp.json
# 然后编辑 .cursor/mcp.json 文件，填入真实API密钥
```

### 🔍 提交前检查
```bash
# 运行安全检查（推荐每次提交前执行）
./scripts/security-check.sh
```

## ⚠️ 重要提醒

### 🚫 绝对不要提交的文件
- `.env` - 包含API密钥
- `.cursor/mcp.json` - 包含MCP服务器API密钥

### ✅ 安全提交的文件
- `env.template` - 环境变量模板
- `.cursor/mcp.json.template` - MCP配置模板
- [SECURITY.md](SECURITY.md) - 完整安全指南

## 🆘 紧急情况

如果意外提交了API密钥：
1. **立即**在API提供商控制台撤销密钥
2. 生成新密钥
3. 联系项目维护者清理git历史

更多详情请参阅：[完整安全指南](SECURITY.md) 