"""
提示词管理器 - 加载、缓存、格式化系统提示词
"""
import json
from pathlib import Path
from string import Template
from typing import Dict, Any, Optional
from datetime import datetime


class PromptManagerError(Exception):
    """提示词管理器异常基类"""
    pass


class PromptNotFoundError(PromptManagerError):
    """提示词未找到异常"""
    pass


class PromptConfigError(PromptManagerError):
    """提示词配置错误异常"""
    pass


class PromptManager:
    """提示词管理器 - 负责加载、缓存、格式化和热重载提示词配置"""
    
    def __init__(self, config_dir: str = "config/prompts", locale: str = "zh"):
        """初始化提示词管理器"""
        self.config_dir = Path(config_dir)
        self.locale = locale
        self.prompts_cache: Dict[str, Any] = {}
        self.config_cache: Dict[str, Dict] = {}
        self.last_reload = datetime.now()
        
        if not self.config_dir.exists():
            raise PromptConfigError(f"配置目录不存在: {self.config_dir}")
        self.load_prompts()
    
    def load_prompts(self) -> None:
        """加载所有提示词配置文件"""
        try:
            self.prompts_cache.clear()
            self.config_cache.clear()
            
            self._load_config_file("system_prompts.json")
            
            templates_dir = self.config_dir / "templates"
            if templates_dir.exists():
                for template_file in templates_dir.glob("*.json"):
                    self._load_config_file(f"templates/{template_file.name}")
            
            locale_file = self.config_dir / "locales" / self.locale / "system_prompts.json"
            if locale_file.exists():
                self._load_config_file(f"locales/{self.locale}/system_prompts.json")
            
            self.last_reload = datetime.now()
        except Exception as e:
            raise PromptConfigError(f"加载配置失败: {e}")
    
    def _load_config_file(self, relative_path: str) -> None:
        """加载单个配置文件"""
        file_path = self.config_dir / relative_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.config_cache[relative_path] = config
            if 'prompts' in config:
                self.prompts_cache.update(config['prompts'])
        except json.JSONDecodeError as e:
            raise PromptConfigError(f"JSON解析错误 {file_path}: {e}")
        except Exception as e:
            raise PromptConfigError(f"读取文件失败 {file_path}: {e}")
    
    def get_prompt(self, prompt_key: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """获取格式化的提示词"""
        if prompt_key not in self.prompts_cache:
            raise PromptNotFoundError(f"提示词不存在: {prompt_key}")
        
        prompt_config = self.prompts_cache[prompt_key]
        if not prompt_config.get('enabled', True):
            raise PromptNotFoundError(f"提示词已禁用: {prompt_key}")
        
        content = prompt_config['content']
        if variables:
            try:
                template = Template(content)
                content = template.safe_substitute(variables)
            except Exception:
                pass
        return content
    
    def reload_prompts(self) -> None:
        """热重载提示词配置"""
        self.load_prompts()
    
    def get_available_prompts(self) -> Dict[str, str]:
        """获取所有可用提示词的描述"""
        return {
            key: config.get('description', '无描述')
            for key, config in self.prompts_cache.items()
            if config.get('enabled', True)
        }
    
    def validate_variables(self, prompt_key: str, variables: Dict[str, Any]) -> bool:
        """验证提供的变量是否符合提示词要求"""
        if prompt_key not in self.prompts_cache:
            return False
        
        required_vars = self.prompts_cache[prompt_key].get('variables', [])
        provided_vars = set(variables.keys()) if variables else set()
        missing_vars = set(required_vars) - provided_vars
        
        if missing_vars:
            return False
        return True 