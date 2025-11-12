# entrypoint-dev.ps1
# CodeArtifact 配置脚本 (Windows PowerShell 版本)

$ErrorActionPreference = "Stop"

$PROFILE_NAME = "oxsci-dev"
$DOMAIN = "oxsci-domain"
$DOMAIN_OWNER = "000373574646"
$REPOSITORY = "oxsci-pypi"
$REGION = "ap-southeast-1"

Write-Host "🔧 开始配置 AWS CodeArtifact 用于 Poetry..." -ForegroundColor Cyan

# 检查 AWS CLI 是否安装
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "❌ AWS CLI 未安装，请先安装 AWS CLI" -ForegroundColor Red
    exit 1
}

# 检查 Poetry 是否安装
if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Poetry 未安装，请先安装 Poetry" -ForegroundColor Red
    exit 1
}

# 检查 AWS Profile 是否存在
Write-Host "🔍 检查 AWS Profile: $PROFILE_NAME" -ForegroundColor Yellow
$profiles = aws configure list-profiles
if ($profiles -notcontains $PROFILE_NAME) {
    Write-Host "❌ AWS Profile '$PROFILE_NAME' 不存在" -ForegroundColor Red
    Write-Host ""
    Write-Host "请配置 AWS Profile，推荐使用 SSO："
    Write-Host "  aws configure sso --profile $PROFILE_NAME"
    exit 1
}

# 测试 Profile 是否有效
Write-Host "🔐 验证 AWS Profile 权限..." -ForegroundColor Yellow
try {
    $null = aws sts get-caller-identity --profile $PROFILE_NAME --output json 2>&1
    Write-Host "✅ AWS Profile 验证成功" -ForegroundColor Green
} catch {
    Write-Host "⚠️  AWS Profile '$PROFILE_NAME' 无法验证身份，尝试自动登录..." -ForegroundColor Yellow
    try {
        aws sso login --profile $PROFILE_NAME
        Write-Host "✅ SSO 登录成功" -ForegroundColor Green
    } catch {
        Write-Host "❌ SSO 登录失败，请手动执行：" -ForegroundColor Red
        Write-Host "  aws sso login --profile $PROFILE_NAME"
        exit 1
    }
}

# 获取 CodeArtifact 仓库 URL
Write-Host "🌐 获取 CodeArtifact 仓库端点..." -ForegroundColor Yellow
try {
    $REPO_URL = aws codeartifact get-repository-endpoint --profile $PROFILE_NAME --domain $DOMAIN --domain-owner $DOMAIN_OWNER --repository $REPOSITORY --format pypi --region $REGION --query repositoryEndpoint --output text
    
    if ([string]::IsNullOrEmpty($REPO_URL)) {
        throw "仓库端点为空"
    }
    
    Write-Host "✅ 仓库端点获取成功: $REPO_URL" -ForegroundColor Green
} catch {
    Write-Host "❌ 获取仓库端点失败，请检查权限和参数" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# 配置 Poetry 仓库
Write-Host "📦 配置 Poetry 仓库..." -ForegroundColor Yellow
try {
    poetry config repositories.oxsci-ca $REPO_URL
    Write-Host "✅ Poetry 仓库配置成功" -ForegroundColor Green
} catch {
    Write-Host "❌ Poetry 仓库配置失败" -ForegroundColor Red
    exit 1
}

# 获取认证令牌
Write-Host "🔑 获取认证令牌..." -ForegroundColor Yellow
try {
    $AUTH_TOKEN = aws codeartifact get-authorization-token --profile $PROFILE_NAME --domain $DOMAIN --domain-owner $DOMAIN_OWNER --region $REGION --query authorizationToken --output text
    
    if ([string]::IsNullOrEmpty($AUTH_TOKEN)) {
        throw "认证令牌为空"
    }
    
    Write-Host "✅ 认证令牌获取成功" -ForegroundColor Green
} catch {
    Write-Host "❌ 获取认证令牌失败" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# 配置 Poetry 认证（使用环境变量，绕过凭据管理器）
Write-Host "🔐 配置 Poetry 认证（使用环境变量）..." -ForegroundColor Yellow

# 方法 1: 尝试使用 Poetry 配置（禁用 keyring）
try {
    poetry config keyring.enabled false
    Write-Host "✅ Keyring 已禁用，将使用文件存储" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Keyring 配置失败，将使用环境变量方案" -ForegroundColor Yellow
}

# 方法 2: 设置环境变量（主要方案）
$env:POETRY_HTTP_BASIC_OXSCI_CA_USERNAME = "aws"
$env:POETRY_HTTP_BASIC_OXSCI_CA_PASSWORD = $AUTH_TOKEN
Write-Host "✅ 环境变量已设置（Token 长度: $($AUTH_TOKEN.Length) 字符）" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 CodeArtifact 配置完成！" -ForegroundColor Green
Write-Host "📋 配置信息：" -ForegroundColor Cyan
Write-Host "  - 仓库名称: oxsci-ca"
Write-Host "  - 仓库地址: $REPO_URL"
Write-Host "  - Profile: $PROFILE_NAME"
Write-Host "  - 令牌有效期: 12 小时"
Write-Host "  - 认证方式: 环境变量"
Write-Host ""

# 自动安装依赖
Write-Host "📦 开始安装依赖..." -ForegroundColor Cyan
try {
    poetry install
    Write-Host ""
    Write-Host "✅ 依赖安装成功！" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ 依赖安装失败" -ForegroundColor Red
    Write-Host "💡 Token 已配置到环境变量，你可以手动运行：" -ForegroundColor Yellow
    Write-Host "   poetry install"
    Write-Host ""
    Write-Host "⚠️  注意：关闭此 PowerShell 窗口后环境变量会失效" -ForegroundColor Yellow
    Write-Host "   如需重新安装，请重新运行此脚本" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "💡 提示：" -ForegroundColor Yellow
Write-Host "  - Token 有效期: 12 小时"
Write-Host "  - 环境变量仅在当前 PowerShell 窗口有效"
Write-Host "  - 关闭窗口后需要重新运行此脚本"
Write-Host "  - 如果 12 小时后 token 过期，需要重新运行此脚本"
Write-Host ""
Write-Host "🚀 现在可以开始开发了！" -ForegroundColor Green
