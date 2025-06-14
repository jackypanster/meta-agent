#!/bin/bash
# Pre-commit hook for Qwen-Agent MVP
# 确保提交前代码质量符合标准

set -e

echo "🔍 运行代码质量检查..."

# 检查文件长度
echo "📏 检查文件长度..."
find src/ -name "*.py" -type f | while read file; do
    lines=$(wc -l < "$file")
    if [ "$lines" -gt 100 ]; then
        echo "❌ 错误: $file 超过100行 (当前: $lines 行)"
        echo "请将此文件拆分为更小的模块"
        exit 1
    fi
done

# 运行代码格式化
echo "🎨 运行代码格式化..."
uv run black src/ tests/ --check
if [ $? -ne 0 ]; then
    echo "❌ 代码格式不符合规范，正在自动修复..."
    uv run black src/ tests/
    echo "✅ 代码已格式化，请重新提交"
    exit 1
fi

# 运行导入排序
echo "📋 检查导入排序..."
uv run isort src/ tests/ --check-only
if [ $? -ne 0 ]; then
    echo "❌ 导入排序不符合规范，正在自动修复..."
    uv run isort src/ tests/
    echo "✅ 导入已排序，请重新提交"
    exit 1
fi

# 运行类型检查
echo "🔍 运行类型检查..."
uv run mypy src/
if [ $? -ne 0 ]; then
    echo "❌ 类型检查失败，请修复类型错误"
    exit 1
fi

# 运行代码检查
echo "🔍 运行代码检查..."
uv run flake8 src/ tests/
if [ $? -ne 0 ]; then
    echo "❌ 代码检查发现问题，请修复"
    exit 1
fi

# 运行测试
echo "🧪 运行测试..."
uv run pytest -m "not slow and not api" --tb=short
if [ $? -ne 0 ]; then
    echo "❌ 测试失败，请修复失败的测试"
    exit 1
fi

# 检查测试覆盖率
echo "📊 检查测试覆盖率..."
uv run pytest --cov=src --cov-report=term --cov-fail-under=90 -m "not slow and not api" --quiet
if [ $? -ne 0 ]; then
    echo "❌ 测试覆盖率低于90%，请添加更多测试"
    exit 1
fi

echo "✅ 所有检查通过！代码质量符合标准"
echo "🚀 准备提交..." 