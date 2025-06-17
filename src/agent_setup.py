"""
Agent设置和工具配置模块

负责MCP服务器设置和工具列表配置
"""

from typing import Dict, List, Any

from src.config.mcp_config import get_mcp_config_loader
from src.exceptions import MCPConfigError


def setup_mcp_servers() -> Dict[str, Any]:
    """设置MCP服务器配置 - 失败时立即抛出异常
    
    从配置文件动态加载启用的MCP服务器，支持命令行和SSE两种协议
    
    Returns:
        MCP服务器配置字典，符合Qwen-Agent格式
        
    Raises:
        MCPConfigError: MCP配置加载失败时立即抛出
    """
    # 获取MCP配置加载器
    config_loader = get_mcp_config_loader()
    
    # 获取启用的服务器
    enabled_servers = config_loader.get_enabled_servers()
    
    if not enabled_servers:
        raise MCPConfigError("❌ 未找到任何启用的MCP服务器")
    
    # 构建Qwen-Agent格式的MCP配置
    mcp_servers = {}
    
    # This function supports two types of MCP servers:
    # 1. Command-line servers: require 'command' and 'args' fields
    # 2. SSE servers: require 'type' and 'config' fields
    for server_name in enabled_servers:
        server_config = config_loader.get_server_config(server_name)
        if not server_config:
            raise MCPConfigError(f"❌ 服务器 '{server_name}' 配置不存在")
        
        # 根据服务器类型处理配置
        if server_config.get('type') == 'sse':
            # SSE协议服务器
            if 'config' not in server_config or 'url' not in server_config['config']:
                raise MCPConfigError(f"❌ SSE服务器 '{server_name}' 缺少必需的config.url字段")
            
            qwen_config = {
                'type': 'sse',
                'config': server_config['config']
            }
            
        else:
            # 传统命令行服务器
            if 'command' not in server_config or 'args' not in server_config:
                raise MCPConfigError(f"❌ 命令行服务器 '{server_name}' 缺少必需的command/args字段")
            
            qwen_config = {
                'command': server_config['command'],
                'args': server_config['args']
            }
            
            # 添加环境变量（如果有）
            if 'env' in server_config:
                qwen_config['env'] = server_config['env']
        
        mcp_servers[server_name] = qwen_config
        
        # 显示加载的服务器信息
        category = server_config.get('category', '未分类')
        server_type = server_config.get('type', 'command')
        print(f"✓ 加载MCP服务器: {server_name} (类型: {server_type}, 分类: {category})")
    
    print(f"📡 成功加载 {len(mcp_servers)} 个MCP服务器")
    return mcp_servers


def create_tools_list() -> List[Any]:
    """创建工具列表 - 失败时立即抛出异常
    
    动态构建包含MCP服务器的工具列表
    
    Returns:
        工具列表，包含自定义工具和MCP服务器配置
        
    Raises:
        MCPConfigError: MCP配置失败时立即抛出
    """
    # 设置MCP服务器
    mcp_servers = setup_mcp_servers()
    
    # 构建工具列表
    # These tools are explicitly listed to ensure their availability to the agent.
    # Relying on potential auto-discovery mechanisms of the Qwen framework
    # is not currently implemented or confirmed for this project.
    tools = [
        # 'custom_save_info', 
        # 'custom_recall_info', 
        # 'custom_math_calc',
        {
            'mcpServers': mcp_servers  # 使用动态加载的MCP配置
        },
        # 'code_interpreter',  # 内置代码解释器工具
    ]
    
    return tools