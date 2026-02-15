# WSL 环境备份脚本
# 用于定期备份 WSL 环境到 D 盘

param(
    [string]$BackupPath = "D:\backup\wsl-backup",
    [string]$DistroName = ""
)

# 创建备份目录
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupFile = "$BackupPath-$timestamp.tar"

Write-Host "=== WSL 环境备份脚本 ===" -ForegroundColor Green
Write-Host "备份目标: $backupFile" -ForegroundColor Yellow

if (-not $DistroName) {
    $DistroName = (& wsl -l -q 2>$null | ForEach-Object { $_.Trim() } | Where-Object { $_ -and $_ -notmatch '^docker-desktop' } | Select-Object -First 1)
}

if (-not $DistroName) {
    Write-Host "❌ 未检测到可备份的 Linux 发行版" -ForegroundColor Red
    exit 1
}

Write-Host "目标发行版: $DistroName" -ForegroundColor Cyan

# 检查 WSL 是否运行
$wslRunning = wsl --list --running 2>$null
if ($wslRunning) {
    Write-Host "检测到 WSL 正在运行，正在关闭..." -ForegroundColor Yellow
    wsl --shutdown
    Start-Sleep -Seconds 5
}

# 创建备份目录
New-Item -ItemType Directory -Force -Path (Split-Path $backupFile) | Out-Null

# 执行备份
Write-Host "开始备份 WSL 环境..." -ForegroundColor Yellow
try {
    wsl --export $DistroName $backupFile
    Write-Host "✅ 备份完成: $backupFile" -ForegroundColor Green
    
    # 显示文件大小
    $fileInfo = Get-Item $backupFile
    Write-Host "备份文件大小: $([math]::Round($fileInfo.Length / 1GB, 2)) GB" -ForegroundColor Cyan
}
catch {
    Write-Host "❌ 备份失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 清理旧备份 (保留最近5个)
Write-Host "清理旧备份文件..." -ForegroundColor Yellow
$backupDir = Split-Path $backupFile
$oldBackups = Get-ChildItem "$backupDir\wsl-backup-*.tar" | Sort-Object CreationTime -Descending | Select-Object -Skip 5

if ($oldBackups) {
    foreach ($oldBackup in $oldBackups) {
        Remove-Item $oldBackup.FullName -Force
        Write-Host "已删除: $($oldBackup.Name)" -ForegroundColor Gray
    }
}

Write-Host "✅ 备份任务完成!" -ForegroundColor Green
