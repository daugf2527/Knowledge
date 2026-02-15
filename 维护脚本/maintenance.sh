#!/bin/bash
# WSL 环境维护脚本
# 定期维护 WSL 和 Codex CLI 环境

set -euo pipefail

green='\033[32m'
yellow='\033[33m'
cyan='\033[36m'
red='\033[31m'
reset='\033[0m'

printf "%b=== WSL 环境维护脚本 ===%b\n" "$green" "$reset"
printf "%b开始时间: %s%b\n" "$cyan" "$(date)" "$reset"

# 检查网络连接
printf "%b检查网络连接...%b\n" "$yellow" "$reset"
if curl -s --head https://api.openai.com > /dev/null; then
    printf "%b✅ 网络连接正常%b\n" "$green" "$reset"
else
    printf "%b❌ 网络连接异常%b\n" "$red" "$reset"
    exit 1
fi

# 更新系统包
printf "\n%b更新系统包...%b\n" "$yellow" "$reset"
sudo apt update
sudo apt upgrade -y

# 更新 npm 全局包
printf "\n%b更新 npm 全局包...%b\n" "$yellow" "$reset"
npm update -g

# 检查 Codex CLI 版本
printf "\n%b检查 Codex CLI 版本...%b\n" "$yellow" "$reset"
if command -v codex &> /dev/null; then
    codex_version=$(codex --version 2>/dev/null || echo "未知")
    printf "%b当前版本: %s%b\n" "$cyan" "$codex_version" "$reset"
else
    printf "%b❌ Codex CLI 未安装%b\n" "$red" "$reset"
    printf "%b正在安装...%b\n" "$yellow" "$reset"
    npm install -g @openai/codex
fi

# 清理 npm 缓存
printf "\n%b清理 npm 缓存...%b\n" "$yellow" "$reset"
npm cache clean --force

# 清理系统包缓存
printf "\n%b清理系统包缓存...%b\n" "$yellow" "$reset"
sudo apt autoremove -y
sudo apt autoclean

# 检查磁盘使用情况
printf "\n%b=== 磁盘使用情况 ===%b\n" "$green" "$reset"
df -h /

# 检查内存使用情况
printf "\n%b=== 内存使用情况 ===%b\n" "$green" "$reset"
free -h

# 检查 Codex 配置
printf "\n%b检查 Codex 配置...%b\n" "$yellow" "$reset"
if [ -f ~/.codex/config.toml ]; then
    printf "%b✅ 配置文件存在%b\n" "$green" "$reset"
    printf "%b配置内容:%b\n" "$cyan" "$reset"
    cat ~/.codex/config.toml
else
    printf "%b❌ 配置文件不存在，创建默认配置...%b\n" "$red" "$reset"
    mkdir -p ~/.codex
    cat > ~/.codex/config.toml << 'EOF'
model = "gpt-5-codex"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
cli_auth_credentials_store = "auto"
EOF
    printf "%b✅ 默认配置已创建%b\n" "$green" "$reset"
fi

# 检查认证状态
printf "\n%b检查认证状态...%b\n" "$yellow" "$reset"
if [ -f ~/.codex/auth.json ]; then
    printf "%b✅ 认证文件存在%b\n" "$green" "$reset"
else
    printf "%b❌ 未找到认证信息，请运行 'codex login --device-auth' 或 'codex' 登录%b\n" "$red" "$reset"
fi

# 性能检查
printf "\n%b=== 性能检查 ===%b\n" "$green" "$reset"
printf "%bCPU 使用率最高的进程:%b\n" "$cyan" "$reset"
ps aux --sort=-%cpu | head -5

printf "\n%b内存使用率最高的进程:%b\n" "$cyan" "$reset"
ps aux --sort=-%mem | head -5

# 建议和提醒
printf "\n%b=== 维护建议 ===%b\n" "$green" "$reset"
printf "%b1. 定期运行此脚本 (建议每月一次)%b\n" "$cyan" "$reset"
printf "%b2. 监控磁盘空间；压缩 VHD 请在 Windows PowerShell 执行: wsl --shutdown && wsl --manage <DistroName> --compact%b\n" "$cyan" "$reset"
printf "%b3. 保持 Codex CLI 更新到最新版本%b\n" "$cyan" "$reset"
printf "%b4. 定期备份重要项目%b\n" "$cyan" "$reset"

printf "\n%b维护完成时间: %s%b\n" "$green" "$(date)" "$reset"
printf "%b✅ WSL 环境维护完成!%b\n" "$green" "$reset"
