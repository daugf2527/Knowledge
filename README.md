# OpenAI Codex CLI 安装方案

## 📁 文件说明

本目录包含了在你的 Windows 环境上安装和配置 OpenAI Codex CLI 的完整解决方案，特别针对 C 盘空间不足的情况进行了优化。

### 📄 核心文件

| 文件名 | 描述 | 用途 |
|--------|------|------|
| `OpenAI_Codex_CLI_安装方案.md` | 完整技术文档 | 详细的安装指南和配置说明 |
| `快速安装脚本.ps1` | 自动化安装脚本 | 分阶段完成 WSL 安装检测、D 盘迁移与配置脚本生成 |
| `维护脚本/backup-wsl.ps1` | 备份脚本 | 定期备份 WSL 环境 |
| `维护脚本/maintenance.sh` | 维护脚本 | WSL 环境日常维护 |

---

## 🚀 快速开始

### 第一步：运行安装脚本
```powershell
# 以管理员身份运行 PowerShell
# 导航到当前目录
cd D:\windsulf

# 运行安装脚本（默认 auto 模式）
.\快速安装脚本.ps1
```

### 第二步：重启计算机
脚本会提示你重启计算机，请按提示操作。

### 第三步：完成 WSL 配置
重启后再次运行脚本，然后执行：
```bash
# 进入 WSL
wsl -d <DistroName>

# 运行配置脚本
bash /mnt/d/wsl/setup-wsl.sh
```

### 第四步：启动 Codex
```bash
# 常规登录
codex

# 无浏览器 / 回调受限场景
codex login --device-auth
```

---

## 📋 环境要求

### ✅ 已满足
- Node.js v18.20.5
- npm 10.8.2
- Windows PowerShell

### 🔄 需要安装
- WSL (脚本可触发安装命令，需重启后继续)
- Linux 发行版 (首次安装后初始化)
- Codex CLI (通过 setup-wsl.sh 安装)

---

## 💾 磁盘空间规划

### 安装前空间需求
- **C 盘**: 临时空间 ~2GB (安装后释放)
- **D 盘**: 长期使用 ~5-10GB

### 安装后空间分布
```
D:\wsl\<DistroName>\    # WSL 主环境 (~3-5GB)
D:\backup\              # 备份文件 (~1-2GB)
D:\backup\wsl-backup\   # 定期备份 (~1-2GB)
```

---

## ⚙️ 配置说明

### Codex CLI 配置
位置: `~/.codex/config.toml`

```toml
model = "gpt-5-codex"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
cli_auth_credentials_store = "auto"
```

### WSL 配置
位置: `%USERPROFILE%\.wslconfig`

```ini
[wsl2]
memory=4GB
processors=2
swap=2GB
```

---

## 🔧 维护建议

### 每周维护
```bash
# 在 WSL 中运行
bash /mnt/d/windsulf/维护脚本/maintenance.sh
```

### 每月备份
```powershell
# 在 Windows PowerShell 中运行
.\维护脚本\backup-wsl.ps1
```

### 磁盘空间管理
```powershell
# 压缩 WSL 磁盘（在 Windows PowerShell）
wsl --shutdown
wsl --manage <DistroName> --compact

# 检查空间使用
wsl -l -v
```

---

## 🆘 故障排除

### 常见问题

1. **WSL 安装失败**
   - 确保以管理员身份运行
   - 检查 Windows 更新
   - 启用 Windows 虚拟化功能

2. **迁移到 D 盘失败**
   - 确保 D 盘有足够空间
   - 检查 D 盘权限
   - 手动创建目录

3. **Codex CLI 认证问题**
   - 检查网络连接
   - 验证 API Key
   - 清理认证缓存

### 获取帮助
- 查看完整文档: `OpenAI_Codex_CLI_安装方案.md`
- 官方文档: https://developers.openai.com/codex/cli
- 社区支持: GitHub Issues

---

## 📈 性能优化

### 系统优化
- 关闭不必要的后台程序
- 确保 SSD 有足够空间
- 定期进行磁盘碎片整理

### WSL 优化
- 将项目文件放在 WSL 文件系统中
- 避免频繁访问 `/mnt/c` 目录
- 使用 `.wslconfig` 调整资源限制

---

## 🔒 安全注意事项

1. **API Key 管理**
   - 不要在代码中硬编码 API Key
   - 使用环境变量存储
   - 定期轮换 API Key

2. **数据备份**
   - 定期备份重要项目
   - 使用 Git 进行版本控制
   - 加密敏感数据

3. **网络安全**
   - 确保网络连接安全
   - 使用 VPN (如需要)
   - 定期更新系统

---

## 📞 支持与反馈

如果你在使用过程中遇到问题：

1. 首先查看故障排除部分
2. 检查官方文档
3. 在 GitHub 提交 Issue
4. 联系技术支持

---

## 🎉 开始使用

安装完成后，你就可以开始使用 Codex CLI 了！

```bash
# 启动交互式会话
codex

# 请求帮助
codex "帮我创建一个 React 组件"

# 代码审查
codex "审查这个文件的代码质量"
```

祝你使用愉快！🚀
