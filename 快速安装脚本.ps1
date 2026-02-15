# OpenAI Codex CLI 快速安装脚本
# 以管理员身份运行

param(
    [ValidateSet("auto", "install", "migrate")]
    [string]$Phase = "auto",
    [string]$DistroName = ""
)

function Invoke-Wsl {
    param([string[]]$Args)
    & wsl @Args
    if ($LASTEXITCODE -ne 0) {
        throw "wsl $($Args -join ' ') 执行失败，退出码 $LASTEXITCODE"
    }
}

Write-Host "=== OpenAI Codex CLI 安装脚本 ===" -ForegroundColor Green

if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "错误: 请以管理员身份运行此脚本!" -ForegroundColor Red
    pause
    exit 1
}

if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    Write-Host "错误: 未检测到 wsl 命令，请先更新系统后重试。" -ForegroundColor Red
    pause
    exit 1
}

if ($Phase -eq "auto") {
    $installedDistros = (
        & wsl -l -q 2>$null |
        ForEach-Object { $_.Trim() } |
        Where-Object {
            $_ -and
            $_ -notmatch '^docker-desktop' -and
            $_ -notmatch '^Windows Subsystem for Linux' -and
            $_ -notmatch '^There are no installed distributions'
        }
    )
    if (-not $installedDistros) {
        $Phase = "install"
    }
    else {
        $Phase = "migrate"
        if (-not $DistroName) {
            $DistroName = $installedDistros[0]
        }
    }
}

if ($Phase -eq "install") {
    Write-Host "`n=== 第一阶段: 安装 WSL ===" -ForegroundColor Cyan
    Write-Host "正在执行: wsl --install --no-launch" -ForegroundColor Yellow
    try {
        Invoke-Wsl -Args @("--install", "--no-launch")
        Write-Host "✅ WSL 安装命令已执行。" -ForegroundColor Green
        Write-Host "请重启系统，然后再次运行脚本（默认 auto 会自动进入 migrate 阶段）。" -ForegroundColor Yellow
    }
    catch {
        Write-Host "❌ 安装失败: $($_.Exception.Message)" -ForegroundColor Red
        pause
        exit 1
    }
    pause
    exit 0
}

Write-Host "`n=== 第二阶段: 迁移发行版到 D 盘 ===" -ForegroundColor Cyan

try {
    $distros = (
        & wsl -l -q 2>$null |
        ForEach-Object { $_.Trim() } |
        Where-Object {
            $_ -and
            $_ -notmatch '^docker-desktop' -and
            $_ -notmatch '^Windows Subsystem for Linux' -and
            $_ -notmatch '^There are no installed distributions'
        }
    )
    if (-not $distros) {
        throw "未找到可迁移的 Linux 发行版。请先运行一次 'wsl --install' 并完成初始化。"
    }

    if (-not $DistroName) {
        $DistroName = $distros[0]
    }
    if ($distros -notcontains $DistroName) {
        throw "未找到发行版 '$DistroName'。可用发行版: $($distros -join ', ')"
    }

    Write-Host "目标发行版: $DistroName" -ForegroundColor Yellow

    New-Item -ItemType Directory -Force -Path "D:\backup" | Out-Null
    New-Item -ItemType Directory -Force -Path "D:\wsl" | Out-Null

    $safeName = ($DistroName -replace '[^a-zA-Z0-9._-]', '_')
    $tarPath = "D:\backup\$safeName.tar"
    $installPath = "D:\wsl\$safeName"

    Write-Host "导出发行版..." -ForegroundColor Yellow
    Invoke-Wsl -Args @("--export", $DistroName, $tarPath)

    Write-Host "注销旧发行版..." -ForegroundColor Yellow
    Invoke-Wsl -Args @("--unregister", $DistroName)

    Write-Host "导入到 D 盘..." -ForegroundColor Yellow
    Invoke-Wsl -Args @("--import", $DistroName, $installPath, $tarPath, "--version", "2")

    Write-Host "设置默认发行版..." -ForegroundColor Yellow
    Invoke-Wsl -Args @("--set-default", $DistroName)

    # 尝试恢复默认用户（import 后可能回到 root）
    $findUserCmd = @'
getent passwd | awk -F: '$3 >= 1000 && $1 != "nobody" { print $1; exit }'
'@
    $detectedUser = (& wsl -d $DistroName -u root -- sh -lc $findUserCmd).Trim()
    if ($detectedUser) {
        $setDefaultUserCmd = @"
cat > /etc/wsl.conf <<'EOF'
[user]
default=$detectedUser
EOF
"@
        & wsl -d $DistroName -u root -- sh -lc $setDefaultUserCmd | Out-Null
        & wsl --terminate $DistroName | Out-Null
        Write-Host "✅ 已恢复默认用户: $detectedUser" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️ 未自动识别普通用户，首次进入后请手动配置 /etc/wsl.conf 的 [user] default。" -ForegroundColor Yellow
    }

    Write-Host "`n✅ 迁移完成: $DistroName -> $installPath" -ForegroundColor Green
}
catch {
    Write-Host "❌ 迁移失败: $($_.Exception.Message)" -ForegroundColor Red
    pause
    exit 1
}

$wslScript = @'
#!/bin/bash
set -euo pipefail

echo "=== WSL 环境配置开始 ==="

sudo apt update
sudo apt upgrade -y
sudo apt install -y curl wget git build-essential ca-certificates

if ! command -v nvm >/dev/null 2>&1; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
fi

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

nvm install --lts
nvm use --lts
nvm alias default node

npm install -g @openai/codex

mkdir -p ~/.codex
cat > ~/.codex/config.toml << 'EOF'
model = "gpt-5-codex"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
cli_auth_credentials_store = "auto"
EOF

echo "=== WSL 环境配置完成 ==="
echo "建议下一步: codex login --device-auth  （无浏览器或回调失败时）"
echo "常规登录: codex"
'@

$wslScript | Set-Content -Path "D:\wsl\setup-wsl.sh" -Encoding Ascii
Write-Host "✅ WSL 配置脚本已创建: D:\wsl\setup-wsl.sh" -ForegroundColor Green

Write-Host "`n下一步操作:" -ForegroundColor Cyan
Write-Host "1. 进入发行版: wsl -d $DistroName" -ForegroundColor White
Write-Host "2. 运行配置脚本: bash /mnt/d/wsl/setup-wsl.sh" -ForegroundColor White
Write-Host "3. 登录 Codex: codex 或 codex login --device-auth" -ForegroundColor White

pause
