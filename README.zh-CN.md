<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>语言：</strong>
  <a href="README.md">English</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.es.md">Español</a> ·
  简体中文 ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.hi.md">हिन्दी</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a>
</p>

<p align="center">
  <strong>面向非工程师的 Codex Desktop 插件。</strong><br/>
  用普通话说出你想要的。ACC 帮你规划、构建，并检查是否真正可用。
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-live-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/mitunmanav/anyone-can-code/validate.yml?branch=main&style=flat-square&label=CI" alt="CI"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/Windows%20·%20Codex-0078D4?style=flat-square" alt="Platform"/>
  <img src="https://img.shields.io/badge/beta-orange?style=flat-square" alt="Beta"/>
</p>

---

## 是什么

**Anyone Can Code (ACC)** 是 Windows 上 **Codex Desktop** 的免费插件。为非技术人员打造 —— 包括我自己。

你用日常语言描述想法、修复或项目。ACC 会带你完成：

| 步骤 | 你会得到 |
|------|----------|
| **规划** | 大改动前的清晰路径 |
| **构建** | 在项目里一步步完成工作 |
| **检查** | 真正的「做完了吗？」验证，而不只是「看起来行」 |

它是 **原生 Codex** 插件 —— 按 [Codex 官方文档](https://openai.com/codex/) 编写，不是从 Claude、Cursor 或其他代理移植来的。

我是 **Mitun**。我自己也用 ACC。用它发布的真实产品：[Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2)。公开测试版：**v1.1.0-beta.3**。

**你需要：** Windows · [Codex Desktop](https://openai.com/codex/) · Python

---

## 安装

<p align="center">
  <img src="docs/media/install-setup.gif" alt="在 Codex Desktop 中安装 Anyone Can Code" width="640"/>
</p>

1. 复制此 URL：`https://github.com/mitunmanav/anyone-can-code`
2. 在 Codex → **Plugins** → **+** → **Add a Marketplace** → 粘贴 URL
3. 找到 **Anyone Can Code** → **Install**
4. 打开 **Hooks** → 打开所有 ACC hook 并对每个 **信任**（必须 —— Codex 不会自动信任）
5. **重启** Codex，确认插件工具已开启
6. 打开项目文件夹 → 运行 `$setup` → 说出你想构建的内容

可选（仅 marketplace —— 仍需 hooks、重启，然后 `$setup`）：

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

视频：[docs/media/install-setup.mp4](docs/media/install-setup.mp4) · 完整说明见网站：[anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/#install)

---

## 出问题了怎么办

| 你看到的 | 可以尝试 |
|----------|----------|
| Marketplace / 安装失败 | 粘贴上面的 **完整** GitHub URL，不要用短名称 |
| 插件已装但没用 | 信任 **所有** ACC hooks，然后完整重启 Codex |
| `$setup` 没反应 | 先打开 **项目文件夹**，开 **新聊天**，再试 `$setup` |
| 还是卡住 | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) 或 [报告问题](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

[Discord](https://discord.gg/qgS29y7TqP) 适合快速提问。东西坏了请用 Issues。

---

## 常用命令

也可以直接用普通话。想明确切换时用这些：

| 命令 | 何时用 |
|------|--------|
| `$setup` | 项目第一次 —— 准备开始工作 |
| `$orchestrator` | 不确定从哪开始时的主入口 |
| `$help` / `$status` | 你在哪、下一步是什么 |
| `$resume` | 休息后继续 |
| `$verify` | 检查工作是否真正完成 |
| `$fix` | 同一问题反复失败时 |

---

## 链接

[网站](https://anyone-can-code.vercel.app/) · [讨论](https://github.com/mitunmanav/anyone-can-code/discussions) · [隐私](docs/PRIVACY.md) · [条款](docs/TERMS.md) · [贡献](.github/CONTRIBUTING.md)

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/anyone-can-code&type=Date)](https://star-history.com/#mitunmanav/anyone-can-code&Date)
