# OpenAI Codex CLI 完整安装方案

## 📋 环境检查结果

### ✅ 当前环境状态
- **操作系统**: Windows (PowerShell 5.1)
- **Node.js**: v18.20.5 ✅ (满足要求 v18+)
- **npm**: 10.8.2 ✅ (正常工作)
- **WSL**: 未安装 ❌
- **Codex CLI**: 未安装 ❌
- **API Key**: 未设置 ❌

### 🎯 安装目标
- 长期使用 Codex CLI
- 解决 C 盘空间不足问题
- 优化开发环境配置

---

## 🛠️ 推荐安装方案：WSL2 + D盘迁移

### 方案优势
- ✅ 解决 C 盘空间问题
- ✅ 提供更好的 Linux 兼容性
- ✅ 长期维护成本低
- ✅ 支持完整功能

---

## 📝 详细安装步骤

### 第一阶段：WSL2 基础安装

```powershell
# 1. 以管理员身份打开 PowerShell
# 右键点击 PowerShell -> "以管理员身份运行"

# 2. 安装 WSL2
wsl --install

# 3. 重启计算机完成安装
# 重启后 WSL 会自动完成 Ubuntu 设置

# 4. 验证安装
wsl --list --verbose
```

### 第二阶段：迁移 WSL2 到 D 盘

```powershell
# 1. 创建备份目录
mkdir D:\backup

# 2. 查看发行版名称（示例可能是 Ubuntu 或 Ubuntu-24.04）
wsl --list --verbose

# 3. 导出发行版（将 <DistroName> 替换为实际名称）
wsl --export <DistroName> D:\backup\distro.tar

# 4. 注销 C 盘版本
wsl --unregister <DistroName>

# 5. 在 D 盘创建 WSL 目录
mkdir D:\wsl

# 6. 导入到 D 盘新位置（建议显式指定 WSL2）
wsl --import <DistroName> D:\wsl\<DistroName> D:\backup\distro.tar --version 2

# 7. 设置默认发行版
wsl --set-default <DistroName>

# 8. 验证迁移成功
wsl -l -v
```

> 说明：`wsl --import` 后默认用户可能变成 `root`。推荐在发行版内通过 `/etc/wsl.conf` 配置：

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[user]
default=<your_linux_user>
EOF
exit
```

然后在 Windows PowerShell 执行：

```powershell
wsl --shutdown
```

### 第三阶段：WSL2 环境配置

```bash
# 进入 WSL 环境
wsl

# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装必要的开发工具
sudo apt install -y curl wget git build-essential

# 安装 Node.js 版本管理器
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash

# 重新加载 bash 配置
source ~/.bashrc

# 安装最新 LTS Node.js
nvm install --lts
nvm use --lts
nvm alias default node

# 验证安装
node --version
npm --version
```

### 第四阶段：安装 Codex CLI

```bash
# 在 WSL 环境中安装 Codex CLI
npm install -g @openai/codex

# 验证安装
codex --version
```

### 第五阶段：身份验证配置

#### 选项 A：使用 ChatGPT 账户 (推荐订阅用户)

```bash
# 启动 Codex
codex

# 首次运行会提示登录：
# 1. 选择 "Sign in with ChatGPT"
# 2. 浏览器会自动打开
# 3. 完成 ChatGPT 登录流程
# 4. 返回终端确认登录成功
```

#### 选项 B：使用 API Key (适合按量付费)

```bash
# 设置 API Key 环境变量
export OPENAI_API_KEY="your-api-key-here"

# 可选：仅当前会话使用（更安全）
# 若必须持久化，建议使用凭据管理方案而非明文写入 shell 配置

# 启动 Codex
codex
```

---

## ⚙️ 配置优化

### Codex CLI 配置文件

```bash
# 创建配置目录
mkdir -p ~/.codex

# 创建配置文件
cat > ~/.codex/config.toml << 'EOF'
# Codex CLI 配置
model = "gpt-5-codex"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
cli_auth_credentials_store = "auto"
EOF
```

### VS Code 集成 (可选)

```bash
# 在 WSL 中安装 VS Code Server
# 从 WSL 内启动 VS Code
code .

# 安装推荐扩展
# - OpenAI ChatGPT
# - WSL
# - Docker (如果需要)
```

---

## 🚀 使用指南

### 基本使用命令

```bash
# 启动交互式会话
codex

# 非交互式执行任务
codex "帮我分析这个项目的结构"

# 查看帮助
codex --help

# 登录（无浏览器或回调受限环境推荐）
codex login --device-auth
```

### 项目工作流

```bash
# 1. 进入项目目录
cd ~/code/your-project

# 2. 启动 Codex
codex

# 3. 常用任务示例
codex "重构这个组件，使用 TypeScript"
codex "为这个 API 编写单元测试"
codex "优化性能，减少加载时间"
```

---

## 🔧 故障排除

### 常见问题解决

#### 1. WSL 性能优化

```bash
# 检查 WSL 版本
wsl --version

# 更新到最新版本
wsl --update

# 优化内存使用 (在 Windows 中)
# 在 %USERPROFILE%\.wslconfig 创建配置文件
```

#### 2. 磁盘空间管理

```powershell
# 先关闭 WSL，再压缩 VHD（在 Windows PowerShell 中执行）
wsl --shutdown
wsl --manage <DistroName> --compact

# 查看发行版信息
wsl --list --verbose
```

#### 3. 网络连接问题

```bash
# 检查网络连接
curl -I https://api.openai.com
```

#### 4. 权限问题

```bash
# 修复文件权限
sudo chown -R $USER:$USER ~/.codex
chmod 600 ~/.codex/auth.json
```

---

## 📊 维护建议

### 定期维护任务

```bash
# 每月执行的维护脚本
#!/bin/bash
# maintenance.sh

echo "开始 WSL 维护..."

# 更新系统
sudo apt update && sudo apt upgrade -y

# 更新 Node.js 包
npm update -g

# 清理 npm 缓存
npm cache clean --force

echo "维护完成！"
```

WSL 磁盘压缩请在 Windows PowerShell 中执行：

```powershell
wsl --shutdown
wsl --manage <DistroName> --compact
```

### 备份策略

```powershell
# 定期备份 WSL 环境
# 创建备份脚本 backup-wsl.ps1

$backupPath = "D:\backup\wsl-backup-$(Get-Date -Format 'yyyyMMdd').tar"
wsl --export <DistroName> $backupPath
Write-Host "WSL 备份完成: $backupPath"
```

---

## 📈 性能监控

### 资源使用监控

```bash
# 监控脚本 monitor.sh
#!/bin/bash

echo "=== WSL 资源使用情况 ==="
echo "磁盘使用:"
df -h /

echo -e "\n内存使用:"
free -h

echo -e "\n进程监控:"
ps aux --sort=-%cpu | head -10
```

---

## 🎯 长期使用建议

### 1. 项目组织
- 在 `~/code/` 目录组织项目
- 使用 Git 进行版本控制
- 定期备份重要项目

### 2. 环境隔离
- 为不同项目创建独立的 Node.js 版本
- 使用虚拟环境隔离依赖
- 配置项目特定的 Codex 设置

### 3. 安全考虑
- 定期更新系统和依赖
- 妥善保管 API Key
- 使用 Git 检查点保护代码

---

## 📞 支持资源

### 官方文档
- [OpenAI Codex CLI 文档](https://developers.openai.com/codex/cli)
- [WSL 官方文档](https://learn.microsoft.com/en-us/windows/wsl/)
- [Node.js 文档](https://nodejs.org/docs/)

### 社区支持
- GitHub Issues: [openai/codex](https://github.com/openai/codex)
- Stack Overflow: 标签 `openai-codex`
- Reddit: r/wsl2, r/openai

---

## ✅ 安装验证清单

完成安装后，请验证以下项目：

- [ ] WSL2 正常运行 (`wsl -l -v`)
- [ ] Node.js v18+ 已安装 (`node --version`)
- [ ] Codex CLI 已安装 (`codex --version`)
- [ ] 身份验证完成（执行过 `codex` 或 `codex login --device-auth`）
- [ ] 配置文件已创建 (`~/.codex/config.toml`)
- [ ] VS Code 集成正常 (可选)
- [ ] 网络连接正常
- [ ] 磁盘空间充足 (`df -h /`)

---

## 🎉 结语

按照此方案，你将获得：
- 🚀 高性能的 Codex CLI 环境
- 💾 优化的磁盘空间管理
- 🔧 稳定的长期使用体验
- 🛡️ 安全的开发环境

如有任何问题，请参考故障排除部分或查阅官方文档。祝你使用愉快！
