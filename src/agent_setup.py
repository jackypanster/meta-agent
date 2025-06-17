"""
Agent设置和工具配置模块

负责MCP服务器设置和工具列表配置
"""

from typing import Dict, List, Any

from src.config.mcp_config import get_mcp_config_loader
from src.exceptions import MCPConfigError


def setup_mcp_servers() -> Dict[str, Any]:
    """设置MCP服务器配置 - 失败时立即抛出异常
    
    从配置文件动态加载启用的MCP服务器
    
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
    
    # This function intentionally only uses a subset of the MCP server
    # configuration (command, args, env) for the agent's tool setup.
    # Other fields in mcp_servers.json might be for the server
    # processes themselves or other administrative purposes.
    for server_name in enabled_servers:
        server_config = config_loader.get_server_config(server_name)
        if not server_config:
            raise MCPConfigError(f"❌ 服务器 '{server_name}' 配置不存在")
        
        # 转换为Qwen-Agent期望的格式
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
        print(f"✓ 加载MCP服务器: {server_name} (分类: {category})")
    
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
        'custom_save_info', 
        'custom_recall_info', 
        'custom_math_calc',
        {
            'mcpServers': mcp_servers  # 使用动态加载的MCP配置
        },
        'code_interpreter',  # 内置代码解释器工具
    ]
    
    return tools