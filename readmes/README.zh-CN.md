<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>普通话 → 规划 → 构建 → 检查。</strong><br/>
  面向非工程师的免费 Codex 插件。<br/>
  说出你想要的。ACC 帮你规划、构建，并检查是否真的可用。
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-live-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/mitunmanav/anyone-can-code/validate.yml?branch=main&style=flat-square&label=CI" alt="CI"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/beta-orange?style=flat-square" alt="Beta"/>
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/#install"><strong>免费安装</strong></a>
  ·
  <a href="../docs/FIRST_DAY.md">第一天</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">反馈问题</a>
</p>

<p align="center">
  <strong>语言：</strong>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.es.md">Español</a> ·
  简体中文 ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.hi.md">हिन्दी</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a>
</p>

---

## 是什么

**Anyone Can Code (ACC)** 是面向 [OpenAI Codex](https://openai.com/codex/) 的免费开源插件。  
不是新的代理，也不是 IDE。**代码由 Codex 编写。** ACC 给工作一条清晰路径。

| 步骤 | 你得到什么 |
|------|------------|
| **规划** | 大改之前有清晰路径 |
| **构建** | 在项目里一步步完成 |
| **检查** | 真正的“做完了吗？”而不只是“看起来行” |
| **记忆** | **Desktop：** 信任 hooks 后自动记忆。**CLI：** 尚未 — 用 `$learn` / `$wiki` |

**一个插件** 同时支持 Desktop 与 CLI — 名称相同：**Anyone Can Code**。

公开测试 · Desktop **v2.0.0-beta.5**（Desktop + CLI 钩子信任后自动记忆）· CLI 目前仍为手动记忆。

**需要：** [Codex](https://openai.com/codex/)（Desktop 和/或 CLI）· Python 3

我是 **Mitun**。用 ACC 发布过的产品之一：[Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2)。

---

## 安装 — Desktop

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="在 Codex Desktop 中安装 Anyone Can Code" width="560"/>
</p>

1. 复制：`https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → 粘贴
3. 安装 **Anyone Can Code**
4. **Hooks** → 启用并 **信任所有** ACC hooks（必须）
5. 重启 → 打开项目文件夹 → `$setup` → 说出你想要的

视频：[网站](https://anyone-can-code.vercel.app/#install) · [mp4](../docs/media/install-setup.mp4)

---

## 安装 — CLI

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

1. 在项目文件夹中：`codex`
2. `/plugins` → 安装 **Anyone Can Code**（与 Desktop 相同）
3. `/hooks` → **信任** 所有 ACC hooks
4. 新对话 → `$setup` → 说出你想要的

---

## 记忆

| 你使用 | 自动记忆？ |
|--------|------------|
| **Codex Desktop** | **是** — 信任 ACC hooks 之后 |
| **Codex CLI** | **尚未** — 用 `$learn` / `$wiki` / `$capture` 保存 |

在 Desktop 上，ACC 可在本机记住目标、决定与未完成工作（目录 `.codex/anyone-can-code/`）。不会发送到 ACC 服务器。

**提示：** 每次插件更新后，请重新信任 hooks 并重启。

---

## 日常使用

也可以直接用普通话说。

| 输入 | 何时 |
|------|------|
| `$setup` | 项目第一次使用 |
| `$status` / `$help` | 我在哪？下一步？ |
| `$resume` | 休息后继续 |
| `$verify` | 真的做完了吗？ |
| `$fix` | 同一错误反复出现 |

示例：*“做一个简单的记账工具，并用普通解释每一步。”*

完整首次会话：**[docs/FIRST_DAY.md](../docs/FIRST_DAY.md)**

---

## 出问题了

| 问题 | 处理 |
|------|------|
| 无法添加 marketplace | 使用上面的 **完整** GitHub 链接 |
| 装好后没反应 | **信任所有** ACC hooks，重启，新对话 |
| Desktop 会忘 | hooks 未信任（或更新后未重新信任） |
| CLI 期望自动记忆 | 尚未 — 用 `$learn` / `$wiki`，或改用 Desktop |
| 旧的“仅 CLI”包 | 卸载 **Anyone Can Code CLI**；只装一次 **Anyone Can Code** |
| `$setup` 无反应 | 先打开 **项目文件夹** |

仍卡住？[FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discord](https://discord.gg/qgS29y7TqP) · [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)

---

## 链接

[网站](https://anyone-can-code.vercel.app/) · [路线图](../ROADMAP.md) · [第一天](../docs/FIRST_DAY.md) · [隐私](../docs/PRIVACY.md) · [条款](../docs/TERMS.md) · [贡献](../.github/CONTRIBUTING.md)

MIT · 由 [Mitun](https://github.com/mitunmanav) 构建
