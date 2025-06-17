"""
Agent设置和工具配置模块

负责MCP服务器设置和工具列表配置
"""

from typing import Dict, List, Any

from src.config.mcp_config import get_mcp_config_loader
from src.exceptions import MCPConfigError


def setup_mcp_servers() -> Dict[str, Any]:
    """设置MCP服务器配置 - 失败时立即抛出异常
    
    从配置文件动态加载启用的MCP服务器，支持命令行、SSE和streamable-http三种协议
    
    Returns:
        MCP服务器配置字典，符合Qwen-Agent v0.0.26+格式
        
    Raises:
        MCPConfigError: MCP配置加载失败时立即抛出
    """
    # 获取MCP配置加载器
    config_loader = get_mcp_config_loader()
    
    # 获取启用的服务器
    enabled_servers = config_loader.get_enabled_servers()
    
    if not enabled_servers:
        raise MCPConfigError("❌ 未找到任何启用的MCP服务器")
    
    # 根据官方PR demo，新的配置格式使用mcpServers字典
    mcp_servers = {}
    
    print(f"📡 正在加载 {len(enabled_servers)} 个MCP服务器...")
    
    for name, server_config in enabled_servers.items():
        try:
            # 检查服务器类型并构建相应配置
            if server_config.get('type') == 'sse':
                # SSE协议服务器 (基于官方PR demo格式)
                config_url = server_config.get('config', {}).get('url')
                if not config_url:
                    raise MCPConfigError(f"❌ SSE服务器 '{name}' 缺少config.url字段")
                
                mcp_servers[name] = {
                    "type": "sse",
                    "url": config_url  # 新格式直接使用url字段
                }
                print(f"  ✅ {name} (类型: sse, URL: {config_url})")
                
            elif server_config.get('type') == 'streamable-http':
                # Streamable HTTP协议服务器 (基于官方PR demo格式)
                config_url = server_config.get('config', {}).get('url')
                if not config_url:
                    raise MCPConfigError(f"❌ Streamable-HTTP服务器 '{name}' 缺少config.url字段")
                
                mcp_servers[name] = {
                    "type": "streamable-http", 
                    "url": config_url
                }
                print(f"  ✅ {name} (类型: streamable-http, URL: {config_url})")
                
            else:
                # 传统命令行服务器 (保持兼容性)
                if 'command' not in server_config or 'args' not in server_config:
                    raise MCPConfigError(f"❌ 命令行服务器 '{name}' 缺少command或args字段")
                
                mcp_servers[name] = {
                    "command": server_config['command'],
                    "args": server_config['args']
                }
                category = server_config.get('category', 'unknown')
                print(f"  ✅ {name} (类型: command, 分类: {category})")
                
        except Exception as e:
            raise MCPConfigError(f"❌ 配置服务器 '{name}' 失败: {e}")
    
    # 根据官方PR demo格式，返回包装在mcpServers中的配置
    return [{
        "mcpServers": mcp_servers
    }]


def create_tools_list() -> List[Dict[str, Any]]:
    """创建工具列表 - 失败时立即抛出异常
    
    Returns:
        工具配置列表，包含MCP服务器配置
        
    Raises:
        MCPConfigError: MCP配置失败时立即抛出
    """
    # 设置MCP服务器
    mcp_config = setup_mcp_servers()
    
    # 返回工具列表 (根据官方demo，MCP配置直接作为工具列表)
    return mcp_config