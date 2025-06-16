#!/usr/bin/env python3
"""
提示词配置验证测试脚本
用于验证子任务14.1的完成情况
"""
import json
import os
from pathlib import Path
from jsonschema import validate, ValidationError
import pytest


class TestPromptConfigValidation:
    """测试提示词配置的验证功能"""
    
    @classmethod
    def setup_class(cls):
        """设置测试环境"""
        cls.project_root = Path(__file__).parent.parent
        cls.prompts_dir = cls.project_root / "config" / "prompts"
        cls.schema_file = cls.prompts_dir / "prompts_schema.json"
        
        # 加载schema
        with open(cls.schema_file, 'r', encoding='utf-8') as f:
            cls.schema = json.load(f)
    
    def test_directory_structure_exists(self):
        """验证目录结构是否创建完整"""
        required_dirs = [
            self.prompts_dir,
            self.prompts_dir / "templates",
            self.prompts_dir / "locales" / "en",
            self.prompts_dir / "locales" / "zh"
        ]
        
        for dir_path in required_dirs:
            assert dir_path.exists(), f"目录不存在: {dir_path}"
            assert dir_path.is_dir(), f"路径不是目录: {dir_path}"
    
    def test_required_files_exist(self):
        """验证所有必需文件是否存在"""
        required_files = [
            self.prompts_dir / "prompts_schema.json",
            self.prompts_dir / "system_prompts.json",
            self.prompts_dir / "README.md",
            self.prompts_dir / "templates" / "conversation.json",
            self.prompts_dir / "templates" / "tool_calling.json", 
            self.prompts_dir / "templates" / "error_handling.json",
            self.prompts_dir / "locales" / "en" / "system_prompts.json",
            self.prompts_dir / "locales" / "zh" / "system_prompts.json"
        ]
        
        for file_path in required_files:
            assert file_path.exists(), f"文件不存在: {file_path}"
            assert file_path.is_file(), f"路径不是文件: {file_path}"
    
    def test_main_config_validation(self):
        """验证主配置文件是否符合schema"""
        config_file = self.prompts_dir / "system_prompts.json"
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 验证schema
        try:
            validate(instance=config_data, schema=self.schema)
        except ValidationError as e:
            pytest.fail(f"主配置文件验证失败: {e.message}")
    
    def test_template_files_validation(self):
        """验证模板文件是否符合schema"""
        template_files = [
            "conversation.json",
            "tool_calling.json", 
            "error_handling.json"
        ]
        
        for template_file in template_files:
            file_path = self.prompts_dir / "templates" / template_file
            
            with open(file_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            try:
                validate(instance=template_data, schema=self.schema)
            except ValidationError as e:
                pytest.fail(f"模板文件 {template_file} 验证失败: {e.message}")
    
    def test_locale_files_validation(self):
        """验证多语言文件是否符合schema"""
        locale_files = [
            ("en", "system_prompts.json"),
            ("zh", "system_prompts.json")
        ]
        
        for locale, filename in locale_files:
            file_path = self.prompts_dir / "locales" / locale / filename
            
            with open(file_path, 'r', encoding='utf-8') as f:
                locale_data = json.load(f)
            
            try:
                validate(instance=locale_data, schema=self.schema)
            except ValidationError as e:
                pytest.fail(f"多语言文件 {locale}/{filename} 验证失败: {e.message}")
    
    def test_readme_content(self):
        """验证README文件内容是否存在"""
        readme_file = self.prompts_dir / "README.md"
        
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键内容是否存在
        required_sections = [
            "目录结构",
            "配置文件格式", 
            "变量替换",
            "使用示例",
            "验证规则"
        ]
        
        for section in required_sections:
            assert section in content, f"README缺少必需章节: {section}"
    
    def test_system_prompt_content_extracted(self):
        """验证系统提示词内容是否正确提取"""
        config_file = self.prompts_dir / "system_prompts.json"
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 检查是否包含原始系统提示词的关键内容
        system_base = config_data['prompts']['system_base']['content']
        
        key_phrases = [
            "友好的AI助手",
            "强大的推理能力", 
            "custom_save_info工具",
            "custom_recall_info工具",
            "code_interpreter工具",
            "MCP服务集成"
        ]
        
        for phrase in key_phrases:
            assert phrase in system_base, f"系统提示词缺少关键内容: {phrase}"


if __name__ == "__main__":
    # 运行验证测试
    test_instance = TestPromptConfigValidation()
    test_instance.setup_class()
    
    print("🧪 开始验证提示词配置...")
    
    try:
        test_instance.test_directory_structure_exists()
        print("✅ 目录结构验证通过")
        
        test_instance.test_required_files_exist()
        print("✅ 文件存在性验证通过")
        
        test_instance.test_main_config_validation()
        print("✅ 主配置文件schema验证通过")
        
        test_instance.test_template_files_validation()
        print("✅ 模板文件schema验证通过")
        
        test_instance.test_locale_files_validation()
        print("✅ 多语言文件schema验证通过")
        
        test_instance.test_readme_content()
        print("✅ README内容验证通过")
        
        test_instance.test_system_prompt_content_extracted()
        print("✅ 系统提示词内容验证通过")
        
        print("\n🎉 子任务14.1验收测试全部通过！")
        
    except AssertionError as e:
        print(f"❌ 验证失败: {e}")
    except Exception as e:
        print(f"❌ 测试过程出错: {e}") 