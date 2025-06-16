#!/bin/bash

# 安全检查脚本
# 用于验证敏感文件是否被正确保护

set -e

echo "🔐 开始安全检查..."

# 检查必需的敏感文件是否被gitignore忽略
echo "📋 检查敏感文件gitignore状态..."

SENSITIVE_FILES=(.env .cursor/mcp.json)
MISSING_IGNORE=()

for file in "${SENSITIVE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        if ! git check-ignore "$file" &>/dev/null; then
            MISSING_IGNORE+=("$file")
        else
            echo "✅ $file 已被正确忽略"
        fi
    fi
done

if [[ ${#MISSING_IGNORE[@]} -gt 0 ]]; then
    echo "❌ 以下敏感文件未被gitignore忽略:"
    printf "   %s\n" "${MISSING_IGNORE[@]}"
    echo "请将这些文件添加到.gitignore中!"
    exit 1
fi

# 检查是否有敏感文件被意外暂存
echo "📋 检查暂存区中的敏感文件..."
STAGED_SENSITIVE=$(git diff --cached --name-only | grep -E '\.(env|key|secret)$|mcp\.json$' || true)

if [[ -n "$STAGED_SENSITIVE" ]]; then
    echo "❌ 发现暂存区中有敏感文件:"
    echo "$STAGED_SENSITIVE"
    echo "请移除这些文件从暂存区: git reset HEAD <file>"
    exit 1
fi

# 扫描暂存区中是否有API密钥模式
echo "📋 扫描暂存区中的潜在API密钥..."
POTENTIAL_KEYS=$(git diff --cached | grep -i "api[_-]key\|secret\|token" | grep -v "your_.*_key_here\|placeholder\|template\|example" || true)

if [[ -n "$POTENTIAL_KEYS" ]]; then
    echo "⚠️  发现可能的API密钥模式:"
    echo "$POTENTIAL_KEYS"
    echo "请确认这些不是真实的API密钥!"
    echo "如果是真实密钥，请立即移除并撤销密钥!"
    # 不自动失败，让用户手动确认
fi

# 检查必需的模板文件是否存在
echo "📋 检查安全模板文件..."
REQUIRED_TEMPLATES=(env.template .cursor/mcp.json.template SECURITY.md)
MISSING_TEMPLATES=()

for template in "${REQUIRED_TEMPLATES[@]}"; do
    if [[ ! -f "$template" ]]; then
        MISSING_TEMPLATES+=("$template")
    else
        echo "✅ $template 存在"
    fi
done

if [[ ${#MISSING_TEMPLATES[@]} -gt 0 ]]; then
    echo "⚠️  以下模板文件缺失:"
    printf "   %s\n" "${MISSING_TEMPLATES[@]}"
    echo "建议创建这些模板文件以帮助其他开发者"
fi

# 检查模板文件中是否包含真实密钥
echo "📋 检查模板文件安全性..."
for template in env.template .cursor/mcp.json.template; do
    if [[ -f "$template" ]]; then
        # 查找可能的真实API密钥模式 (sk-, 长字符串等)
        REAL_KEYS=$(grep -E "sk-[a-zA-Z0-9]{32,}|[a-f0-9]{40,}" "$template" || true)
        if [[ -n "$REAL_KEYS" ]]; then
            echo "❌ 模板文件 $template 可能包含真实API密钥:"
            echo "$REAL_KEYS"
            echo "请将其替换为占位符!"
            exit 1
        fi
    fi
done

echo ""
echo "🎉 安全检查通过!"
echo "✅ 所有敏感文件都被正确保护"
echo "✅ 暂存区没有敏感内容"
echo "✅ 模板文件安全"
echo "" 