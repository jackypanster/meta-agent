"""
LLM配置管理模块

负责创建和配置不同模型提供商的LLM配置
支持DeepSeek V3/R1和Qwen3-32B模型
"""

from typing import Dict, Any

from src.config.settings import get_config
from src.exceptions import ModelConfigError


def create_llm_config() -> Dict[str, Any]:
    """创建LLM配置 - 根据模型名称自动检测提供商，失败时立即抛出异常
    
    支持的模型:
    - deepseek-chat: DeepSeek V3 稳定模型
    - deepseek-reasoner: DeepSeek R1 推理模型  
    - qwen3-32b: 本地部署的Qwen3-32B模型
    
    Returns:
        LLM配置字典
        
    Raises:
        ConfigError: 配置加载或API密钥验证失败时立即抛出
        ModelConfigError: 模型配置错误时立即抛出
    """
    
    config = get_config()
    
    # 获取模型名称配置 - 必需字段
    model_name = config.require('MODEL_NAME').lower()
    
    if model_name in ['deepseek-chat', 'deepseek-reasoner']:
        return _create_deepseek_config(config, model_name)
    elif model_name == 'qwen3-32b':
        return _create_qwen3_config(config)
    else:
        raise ModelConfigError(
            f"❌ 不支持的模型: {model_name}\n"
            f"支持的模型: deepseek-chat, deepseek-reasoner, qwen3-32b\n"
            f"请在.env文件中设置 MODEL_NAME=deepseek-chat 或其他支持的模型"
        )


def _create_deepseek_config(config, model_name: str) -> Dict[str, Any]:
    """创建DeepSeek配置
    
    Args:
        config: 配置实例
        model_name: 模型名称 (deepseek-chat 或 deepseek-reasoner)
        
    Returns:
        DeepSeek LLM配置字典
        
    Raises:
        ConfigError: DeepSeek配置错误时立即抛出
    """
    # 检查DeepSeek API密钥 - 失败时立即抛出异常
    api_key = config.require('DEEPSEEK_API_KEY')
    
    print("🔍 检测到DeepSeek API密钥")
    
    base_url = 'https://api.deepseek.com/v1'
    
    if model_name == 'deepseek-reasoner':
        model = 'deepseek-reasoner'  # R1-0528推理模型
        display_name = "DeepSeek R1-0528 推理模型"
    else:  # deepseek-chat
        model = 'deepseek-chat'  # V3-0324 稳定模型
        display_name = "DeepSeek V3 稳定模型"
    
    print(f"⚡ 使用{display_name}")
    
    return {
        'model': model,
        'model_server': base_url,
        'api_key': api_key,
        'generate_cfg': {
            'top_p': 0.8,
            'max_tokens': 2000,
            'temperature': 0.7
        }
    }


def _create_qwen3_config(config) -> Dict[str, Any]:
    """创建Qwen3-32B配置 - 支持思考模式配置
    
    Args:
        config: 配置实例
        
    Returns:
        Qwen3 LLM配置字典，包含vLLM/SGLang兼容配置
        
    Raises:
        ConfigError: Qwen3配置错误时立即抛出
    """
    # 检查Qwen3 API密钥 - 通常是"EMPTY"
    api_key = config.require('QWEN3_API_KEY')
    
    # 检查Qwen3服务器地址
    model_server = config.require('QWEN3_MODEL_SERVER')
    
    # 检查是否启用思考模式 - 可选配置，默认为false
    enable_thinking = config.get_bool_optional('QWEN3_ENABLE_THINKING', default=False)
    
    print("🔍 检测到Qwen3-32B配置")
    print(f"📡 服务器地址: {model_server}")
    print(f"🧠 思考模式: {'启用' if enable_thinking else '禁用'}")
    
    # Qwen3-32B模型名称（根据官方示例）
    model = 'Qwen/Qwen3-32B'
    model_name = "Qwen3-32B 本地部署模型"
    
    print(f"⚡ 使用{model_name}")
    
    # 构建generate_cfg配置
    generate_cfg = {
        'top_p': 0.8,
        'max_tokens': 2000,
        'temperature': 0.7,
        'extra_body': {
            'chat_template_kwargs': {
                'enable_thinking': enable_thinking
            }
        }
    }
    
    return {
        'model': model,
        'model_server': model_server,
        'api_key': api_key,
        'generate_cfg': generate_cfg
    }


def get_model_display_name() -> str:
    """获取模型显示名称用于UI展示
    
    Returns:
        模型显示名称字符串
    """
    config = get_config()
    model_name = config.require('MODEL_NAME').lower()
    
    if model_name == 'deepseek-chat':
        return "DeepSeek-V3稳定模型"
    elif model_name == 'deepseek-reasoner':
        return "DeepSeek-R1推理模型"
    elif model_name == 'qwen3-32b':
        enable_thinking = config.get_bool_optional('QWEN3_ENABLE_THINKING', default=False)
        thinking_suffix = "(思考模式)" if enable_thinking else "(标准模式)"
        return f"Qwen3-32B本地部署模型{thinking_suffix}"
    else:
        return f"未知模型({model_name})"