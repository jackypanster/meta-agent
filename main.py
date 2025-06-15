#!/usr/bin/env python3
"""
项目入口点

从项目根目录启动应用程序
"""

import sys
import os

# 确保src目录在Python路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入并运行主程序
from src.main import main

if __name__ == "__main__":
    main() 