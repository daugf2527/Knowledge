# AGENTS 约定（Git 协作）

## 当前环境
- 仓库位于 Windows 物理盘：`D:\...`（在 WSL 中路径为 `/mnt/d/...`）。
- Codex 在 WSL2 终端执行命令（`bash`）。
- 当前仓库：`/mnt/d/windsulf`，是有效 Git 仓库。

## 运行方式约定
- 项目运行/调试优先在 Windows 物理机上的 GUI 工具中进行（例如 DevEco Studio、浏览器、IDE）。
- WSL 侧主要用于命令行协作（改代码、Git、脚本、检查）。
- 非用户明确要求时，不主动建议将当前仓库迁移到 WSL 内盘。

## Git 操作约定
- 默认在 WSL 中执行 Git 命令：`git status`、`git add`、`git commit`、`git branch`、`git pull`、`git push`。
- 不使用破坏性命令（如 `git reset --hard`、`git checkout --`）除非用户明确要求。
- 不回滚用户已有未指示的改动。
- 涉及完成声明前，先跑验证命令并基于结果说明状态。

## 身份认证约定（私有仓库）
- Windows 里的 GitHub 登录态不会自动传入 WSL。
- 访问私有仓库时，在 WSL 中单独配置认证：
  - 推荐：`export GITHUB_TOKEN=...`
  - 或使用 `gh auth login`（若已安装 gh）。

## 换行符与跨平台
- 建议统一 LF，避免 CRLF/LF 混乱：
  - `git config core.autocrlf false`
  - 仓库使用 `.gitattributes` 统一行尾策略（如 `* text=auto eol=lf`）。
