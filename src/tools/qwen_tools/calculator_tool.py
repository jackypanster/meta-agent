"""
计算器工具

提供安全的数学计算功能。
"""

import json
import math

from qwen_agent.tools.base import BaseTool, register_tool


@register_tool('custom_math_calc')
class CalculatorTool(BaseTool):
    """计算器工具"""
    description = '执行数学计算'
    parameters = [{
        'name': 'expression',
        'type': 'string',
        'description': '数学表达式，如 "2 + 3" 或 "sin(3.14/2)"',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        data = json.loads(params)
        expression = data['expression']
        
        # 安全计算 - 只允许数学运算
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round})
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        return json.dumps({
            'expression': expression,
            'result': result
        }, ensure_ascii=False) 