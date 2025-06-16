"""
内存管理工具

包含用户信息保存和回忆功能的工具类。
"""

import json
import time
from typing import Dict

from qwen_agent.tools.base import BaseTool, register_tool

# 简单的内存存储 - 直接用字典，不搞复杂的
MEMORY_STORE = {
    'facts': [],      # 用户事实信息
    'preferences': [], # 用户偏好
    'history': []     # 对话历史
}


@register_tool('custom_save_info')
class SaveInfoTool(BaseTool):
    """保存用户信息工具"""
    description = '保存用户提到的重要信息，如姓名、兴趣爱好、工作等'
    parameters = [{
        'name': 'info',
        'type': 'string', 
        'description': '要保存的信息内容',
        'required': True
    }, {
        'name': 'type',
        'type': 'string',
        'description': '信息类型：fact(事实) 或 preference(偏好)',
        'required': False
    }]

    def call(self, params: str, **kwargs) -> str:
        data = json.loads(params)
        info = data['info']
        info_type = data.get('type', 'fact')
        
        # 简单保存到内存
        entry = {
            'content': info,
            'timestamp': time.time(),
            'time_str': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if info_type == 'preference':
            MEMORY_STORE['preferences'].append(entry)
        else:
            MEMORY_STORE['facts'].append(entry)
        
        return json.dumps({
            'status': 'saved',
            'message': f'已保存{info_type}: {info}'
        }, ensure_ascii=False)


@register_tool('custom_recall_info') 
class RecallInfoTool(BaseTool):
    """回忆用户信息工具"""
    description = '搜索之前保存的用户信息'
    parameters = [{
        'name': 'query',
        'type': 'string',
        'description': '要搜索的关键词，如"姓名"、"爱好"等',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        data = json.loads(params)
        query = data['query'].lower()
        
        # 简单的关键词搜索
        results = []
        
        for fact in MEMORY_STORE['facts']:
            if query in fact['content'].lower():
                results.append(fact)
                
        for pref in MEMORY_STORE['preferences']:
            if query in pref['content'].lower():
                results.append(pref)
        
        if results:
            return json.dumps({
                'found': True,
                'count': len(results),
                'results': results[-3:]  # 最近3条
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'found': False,
                'message': '没有找到相关信息'
            })


def get_memory_store() -> Dict:
    """获取内存存储的引用，供外部模块使用"""
    return MEMORY_STORE 