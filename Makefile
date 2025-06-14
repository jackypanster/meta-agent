# Qwen-Agent MVP Makefile
# 提供便捷的开发命令

.PHONY: help install test lint format type-check clean dev run pre-commit

# 默认目标
help:
	@echo "🤖 Qwen-Agent MVP 开发命令"
	@echo ""
	@echo "📦 安装和设置:"
	@echo "  install     - 安装依赖"
	@echo "  dev         - 安装开发依赖并设置开发环境"
	@echo ""
	@echo "🧪 测试:"
	@echo "  test        - 运行所有测试"
	@echo "  test-unit   - 运行单元测试"
	@echo "  test-integration - 运行集成测试"
	@echo "  test-e2e    - 运行端到端测试"
	@echo "  test-cov    - 运行测试并生成覆盖率报告"
	@echo ""
	@echo "🔍 代码质量:"
	@echo "  lint        - 运行所有代码检查"
	@echo "  format      - 格式化代码"
	@echo "  type-check  - 类型检查"
	@echo "  pre-commit  - 运行提交前检查"
	@echo ""
	@echo "🚀 运行:"
	@echo "  run         - 运行应用程序"
	@echo ""
	@echo "🧹 清理:"
	@echo "  clean       - 清理临时文件"

# 安装依赖
install:
	@echo "📦 安装依赖..."
	uv sync

# 开发环境设置
dev: install
	@echo "🔧 设置开发环境..."
	@if [ ! -f .env ]; then \
		echo "📝 创建 .env 文件..."; \
		cp .env.example .env; \
		echo "⚠️  请编辑 .env 文件并配置您的API密钥"; \
	fi

# 运行应用
run:
	@echo "🚀 启动 Qwen-Agent MVP..."
	uv run python -m src.main

# 测试相关
test:
	@echo "🧪 运行所有测试..."
	uv run pytest

test-unit:
	@echo "🧪 运行单元测试..."
	uv run pytest -m unit

test-integration:
	@echo "🧪 运行集成测试..."
	uv run pytest -m integration

test-e2e:
	@echo "🧪 运行端到端测试..."
	uv run pytest -m e2e

test-cov:
	@echo "📊 运行测试并生成覆盖率报告..."
	uv run pytest --cov=src --cov-report=html --cov-report=term

# 代码质量
format:
	@echo "🎨 格式化代码..."
	uv run black src/ tests/
	uv run isort src/ tests/

type-check:
	@echo "🔍 类型检查..."
	uv run mypy src/

lint: format type-check
	@echo "🔍 代码检查..."
	uv run flake8 src/ tests/

# 文件长度检查
check-length:
	@echo "📏 检查文件长度..."
	@find src/ -name "*.py" -type f | while read file; do \
		lines=$$(wc -l < "$$file"); \
		if [ "$$lines" -gt 100 ]; then \
			echo "❌ $$file 超过100行 ($$lines 行)"; \
			exit 1; \
		fi; \
	done
	@echo "✅ 所有文件长度符合要求"

# 提交前检查
pre-commit: check-length lint test
	@echo "✅ 提交前检查完成！"

# 清理
clean:
	@echo "🧹 清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "✅ 清理完成" 