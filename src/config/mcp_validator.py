"""
MCP配置验证器

提供MCP服务器配置的详细验证功能，包括：
- JSON Schema 结构验证
- 业务逻辑验证
- 配置完整性检查
- 友好的错误信息
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import jsonschema
from jsonschema import ValidationError

logger = logging.getLogger(__name__)


class MCPValidationError(Exception):
    """MCP配置验证错误"""
    
    def __init__(self, message: str, field_path: str = "", suggestions: List[str] = None):
        self.message = message
        self.field_path = field_path
        self.suggestions = suggestions or []
        super().__init__(message)
    
    def __str__(self):
        result = self.message
        if self.field_path:
            result = f"[{self.field_path}] {result}"
        if self.suggestions:
            result += f"\n建议: {'; '.join(self.suggestions)}"
        return result


class MCPConfigValidator:
    """MCP配置验证器
    
    提供多层次的配置验证：
    1. JSON Schema 结构验证
    2. 业务逻辑验证
    3. 配置完整性检查
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """初始化验证器
        
        Args:
            schema_path: JSON Schema文件路径
        """
        self.schema_path = Path(schema_path) if schema_path else None
        self._schema_cache: Optional[Dict[str, Any]] = None
        
        # 有效的命令列表
        self.valid_commands = {
            'npx', 'uvx', 'node', 'python', 'python3', 
            'pip', 'pipx', 'yarn', 'pnpm', 'bun'
        }
        
        # 有效的日志级别
        self.valid_log_levels = {
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        }
        
        # 服务器名称正则表达式
        self.server_name_pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*$')
        
        # 分类名称正则表达式
        self.category_name_pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*$')
    
    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """加载JSON Schema"""
        if self._schema_cache is None and self.schema_path and self.schema_path.exists():
            try:
                import json
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    self._schema_cache = json.load(f)
                logger.debug(f"已加载验证Schema: {self.schema_path}")
            except Exception as e:
                logger.warning(f"无法加载验证Schema: {e}")
                self._schema_cache = {}
        return self._schema_cache
    
    def validate_schema(self, config: Dict[str, Any]) -> None:
        """JSON Schema结构验证
        
        Args:
            config: 配置字典
            
        Raises:
            MCPValidationError: Schema验证失败
        """
        schema = self._load_schema()
        if not schema:
            logger.warning("未找到JSON Schema，跳过结构验证")
            return
        
        try:
            jsonschema.validate(config, schema)
            logger.debug("JSON Schema验证通过")
        except ValidationError as e:
            field_path = '.'.join(str(p) for p in e.absolute_path) if e.absolute_path else "根级别"
            
            # 生成友好的错误信息
            if "required" in e.message.lower():
                missing_field = e.message.split("'")[1] if "'" in e.message else "未知字段"
                message = f"缺少必需字段: {missing_field}"
                suggestions = [f"请在配置文件中添加 '{missing_field}' 字段"]
            elif "type" in e.message.lower():
                message = f"字段类型错误: {e.message}"
                suggestions = ["请检查字段的数据类型是否正确"]
            elif "enum" in e.message.lower():
                message = f"字段值不在允许范围内: {e.message}"
                suggestions = ["请检查字段值是否为有效选项"]
            else:
                message = f"配置格式错误: {e.message}"
                suggestions = ["请检查配置文件格式是否正确"]
            
            raise MCPValidationError(message, field_path, suggestions)
    
    def validate_version(self, config: Dict[str, Any]) -> None:
        """验证版本号格式
        
        Args:
            config: 配置字典
            
        Raises:
            MCPValidationError: 版本号格式错误
        """
        version = config.get('version', '')
        if not version:
            raise MCPValidationError(
                "版本号不能为空",
                "version",
                ["请设置有效的版本号，如 '1.0'"]
            )
        
        # 检查版本号格式 (x.y 或 x.y.z)
        version_pattern = re.compile(r'^\d+\.\d+(\.\d+)?$')
        if not version_pattern.match(version):
            raise MCPValidationError(
                f"版本号格式无效: {version}",
                "version",
                ["版本号应为 'x.y' 或 'x.y.z' 格式，如 '1.0' 或 '1.0.0'"]
            )
    
    def validate_servers(self, config: Dict[str, Any]) -> None:
        """验证服务器配置
        
        Args:
            config: 配置字典
            
        Raises:
            MCPValidationError: 服务器配置错误
        """
        servers = config.get('servers', {})
        if not servers:
            raise MCPValidationError(
                "至少需要配置一个MCP服务器",
                "servers",
                ["请添加至少一个服务器配置"]
            )
        
        for server_name, server_config in servers.items():
            self._validate_server_name(server_name)
            self._validate_server_config(server_name, server_config)
    
    def _validate_server_name(self, server_name: str) -> None:
        """验证服务器名称
        
        Args:
            server_name: 服务器名称
            
        Raises:
            MCPValidationError: 服务器名称无效
        """
        if not self.server_name_pattern.match(server_name):
            raise MCPValidationError(
                f"服务器名称格式无效: {server_name}",
                f"servers.{server_name}",
                [
                    "服务器名称必须以字母开头",
                    "只能包含字母、数字、下划线和连字符",
                    "示例: 'time_server', 'fetch-api', 'memory1'"
                ]
            )
    
    def _validate_server_config(self, server_name: str, server_config: Dict[str, Any]) -> None:
        """验证单个服务器配置
        
        Args:
            server_name: 服务器名称
            server_config: 服务器配置
            
        Raises:
            MCPValidationError: 服务器配置错误
        """
        # 验证必需字段
        required_fields = ['command', 'args']
        for field in required_fields:
            if field not in server_config:
                raise MCPValidationError(
                    f"服务器 '{server_name}' 缺少必需字段: {field}",
                    f"servers.{server_name}.{field}",
                    [f"请为服务器 '{server_name}' 添加 '{field}' 字段"]
                )
        
        # 验证命令
        command = server_config.get('command', '')
        if not command or not isinstance(command, str):
            raise MCPValidationError(
                f"服务器 '{server_name}' 的命令无效",
                f"servers.{server_name}.command",
                ["命令必须是非空字符串"]
            )
        
        # 检查命令是否为已知的有效命令
        if command not in self.valid_commands:
            logger.warning(f"服务器 '{server_name}' 使用了未知命令: {command}")
        
        # 验证参数
        args = server_config.get('args', [])
        if not isinstance(args, list):
            raise MCPValidationError(
                f"服务器 '{server_name}' 的参数必须是数组",
                f"servers.{server_name}.args",
                ["参数应为字符串数组，如 ['arg1', 'arg2']"]
            )
        
        for i, arg in enumerate(args):
            if not isinstance(arg, str):
                raise MCPValidationError(
                    f"服务器 '{server_name}' 的参数 {i} 必须是字符串",
                    f"servers.{server_name}.args[{i}]",
                    ["所有参数都必须是字符串类型"]
                )
        
        # 验证超时设置
        if 'timeout' in server_config:
            timeout = server_config['timeout']
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise MCPValidationError(
                    f"服务器 '{server_name}' 的超时设置无效: {timeout}",
                    f"servers.{server_name}.timeout",
                    ["超时时间必须是大于0的数字（秒）"]
                )
            
            if timeout > 300:  # 5分钟
                logger.warning(f"服务器 '{server_name}' 的超时时间过长: {timeout}秒")
        
        # 验证分类
        if 'category' in server_config:
            category = server_config['category']
            if not isinstance(category, str) or not category:
                raise MCPValidationError(
                    f"服务器 '{server_name}' 的分类无效",
                    f"servers.{server_name}.category",
                    ["分类必须是非空字符串"]
                )
        
        # 验证环境变量
        if 'env' in server_config:
            env = server_config['env']
            if not isinstance(env, dict):
                raise MCPValidationError(
                    f"服务器 '{server_name}' 的环境变量配置必须是对象",
                    f"servers.{server_name}.env",
                    ["环境变量应为键值对对象"]
                )
            
            for env_name, env_value in env.items():
                if not isinstance(env_name, str) or not env_name:
                    raise MCPValidationError(
                        f"服务器 '{server_name}' 的环境变量名无效: {env_name}",
                        f"servers.{server_name}.env",
                        ["环境变量名必须是非空字符串"]
                    )
                
                if not isinstance(env_value, str):
                    raise MCPValidationError(
                        f"服务器 '{server_name}' 的环境变量值必须是字符串: {env_name}",
                        f"servers.{server_name}.env.{env_name}",
                        ["环境变量值必须是字符串类型"]
                    )
    
    def validate_global_settings(self, config: Dict[str, Any]) -> None:
        """验证全局设置
        
        Args:
            config: 配置字典
            
        Raises:
            MCPValidationError: 全局设置错误
        """
        global_settings = config.get('global_settings', {})
        if not isinstance(global_settings, dict):
            raise MCPValidationError(
                "全局设置必须是对象",
                "global_settings",
                ["请确保 global_settings 是一个对象"]
            )
        
        # 验证默认超时
        if 'default_timeout' in global_settings:
            timeout = global_settings['default_timeout']
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise MCPValidationError(
                    f"默认超时时间无效: {timeout}",
                    "global_settings.default_timeout",
                    ["默认超时时间必须是大于0的数字（秒）"]
                )
        
        # 验证重试次数
        if 'retry_attempts' in global_settings:
            retry = global_settings['retry_attempts']
            if not isinstance(retry, int) or retry < 0:
                raise MCPValidationError(
                    f"重试次数无效: {retry}",
                    "global_settings.retry_attempts",
                    ["重试次数必须是非负整数"]
                )
        
        # 验证重试延迟
        if 'retry_delay' in global_settings:
            delay = global_settings['retry_delay']
            if not isinstance(delay, (int, float)) or delay < 0:
                raise MCPValidationError(
                    f"重试延迟无效: {delay}",
                    "global_settings.retry_delay",
                    ["重试延迟必须是非负数字（秒）"]
                )
        
        # 验证日志级别
        if 'log_level' in global_settings:
            log_level = global_settings['log_level']
            if log_level not in self.valid_log_levels:
                raise MCPValidationError(
                    f"日志级别无效: {log_level}",
                    "global_settings.log_level",
                    [f"有效的日志级别: {', '.join(self.valid_log_levels)}"]
                )
        
        # 验证最大并发服务器数
        if 'max_concurrent_servers' in global_settings:
            max_servers = global_settings['max_concurrent_servers']
            if not isinstance(max_servers, int) or max_servers <= 0:
                raise MCPValidationError(
                    f"最大并发服务器数无效: {max_servers}",
                    "global_settings.max_concurrent_servers",
                    ["最大并发服务器数必须是正整数"]
                )
    
    def validate_categories(self, config: Dict[str, Any]) -> None:
        """验证分类定义
        
        Args:
            config: 配置字典
            
        Raises:
            MCPValidationError: 分类定义错误
        """
        categories = config.get('categories', {})
        if not isinstance(categories, dict):
            raise MCPValidationError(
                "分类定义必须是对象",
                "categories",
                ["请确保 categories 是一个对象"]
            )
        
        for category_name, category_info in categories.items():
            if not self.category_name_pattern.match(category_name):
                raise MCPValidationError(
                    f"分类名称格式无效: {category_name}",
                    f"categories.{category_name}",
                    [
                        "分类名称必须以字母开头",
                        "只能包含字母、数字、下划线和连字符"
                    ]
                )
            
            if not isinstance(category_info, dict):
                raise MCPValidationError(
                    f"分类 '{category_name}' 的信息必须是对象",
                    f"categories.{category_name}",
                    ["分类信息应包含 description 等字段"]
                )
    
    def validate_consistency(self, config: Dict[str, Any]) -> None:
        """验证配置一致性
        
        Args:
            config: 配置字典
            
        Raises:
            MCPValidationError: 配置一致性错误
        """
        servers = config.get('servers', {})
        categories = config.get('categories', {})
        
        # 检查服务器引用的分类是否存在
        for server_name, server_config in servers.items():
            category = server_config.get('category')
            if category and category not in categories:
                raise MCPValidationError(
                    f"服务器 '{server_name}' 引用了不存在的分类: {category}",
                    f"servers.{server_name}.category",
                    [
                        f"请在 categories 中定义分类 '{category}'",
                        f"或者修改服务器 '{server_name}' 的分类为已存在的分类"
                    ]
                )
        
        # 检查是否有未使用的分类
        used_categories = set()
        for server_config in servers.values():
            category = server_config.get('category')
            if category:
                used_categories.add(category)
        
        unused_categories = set(categories.keys()) - used_categories
        if unused_categories:
            logger.warning(f"发现未使用的分类: {', '.join(unused_categories)}")
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """完整配置验证
        
        Args:
            config: 配置字典
            
        Returns:
            (是否验证通过, 错误信息列表)
        """
        errors = []
        
        try:
            # 1. JSON Schema结构验证
            self.validate_schema(config)
            
            # 2. 版本号验证
            self.validate_version(config)
            
            # 3. 服务器配置验证
            self.validate_servers(config)
            
            # 4. 全局设置验证
            self.validate_global_settings(config)
            
            # 5. 分类定义验证
            self.validate_categories(config)
            
            # 6. 配置一致性验证
            self.validate_consistency(config)
            
            logger.info("MCP配置验证通过")
            return True, []
            
        except MCPValidationError as e:
            errors.append(str(e))
            logger.error(f"MCP配置验证失败: {e}")
            return False, errors
        except Exception as e:
            error_msg = f"配置验证过程中发生未知错误: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
            return False, errors
    
    def get_validation_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取配置验证摘要
        
        Args:
            config: 配置字典
            
        Returns:
            验证摘要信息
        """
        servers = config.get('servers', {})
        enabled_servers = [name for name, cfg in servers.items() if cfg.get('enabled', True)]
        
        return {
            'total_servers': len(servers),
            'enabled_servers': len(enabled_servers),
            'disabled_servers': len(servers) - len(enabled_servers),
            'categories': len(config.get('categories', {})),
            'version': config.get('version', 'unknown'),
            'has_global_settings': 'global_settings' in config,
            'validation_timestamp': logger.handlers[0].formatter.formatTime(logger.makeRecord(
                'validator', logging.INFO, '', 0, '', (), None
            )) if logger.handlers else None
        } 