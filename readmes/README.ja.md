<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>言語：</strong>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  日本語 ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.hi.md">हिन्दी</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a>
</p>

<p align="center">
  <strong>エンジニアではない人のための Codex Desktop プラグイン。</strong><br/>
  ほしいことを普通の言葉で伝えてください。ACC が計画・構築・動作確認まで手伝います。
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-live-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/mitunmanav/anyone-can-code/validate.yml?branch=main&style=flat-square&label=CI" alt="CI"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/Windows%20·%20Codex-0078D4?style=flat-square" alt="Platform"/>
  <img src="https://img.shields.io/badge/beta-orange?style=flat-square" alt="Beta"/>
</p>

---

## これは何か

**Anyone Can Code (ACC)** は Windows 向け **Codex Desktop** の無料プラグインです。非技術者向けに作られています —— 私自身も含めて。

アイデア、修正、プロジェクトを普通の言葉で説明します。ACC は次の流れで案内します：

| ステップ | 得られるもの |
|----------|--------------|
| **計画** | 大きな変更の前に明確な道筋 |
| **構築** | プロジェクト内で一歩ずつ進める作業 |
| **確認** | 「見た目OK」ではなく、本当に「できたか」のチェック |

**ネイティブ Codex** プラグインです —— [Codex 公式ドキュメント](https://openai.com/codex/) から書いており、Claude、Cursor、他のエージェントからの移植ではありません。

私は **Mitun** です。自分でも ACC を使っています。これで出した実プロダクト：[Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2)。オープンベータ：**v1.1.0-beta.3**。

**必要なもの：** Windows · [Codex Desktop](https://openai.com/codex/) · Python

---

## インストール

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Codex Desktop に Anyone Can Code をインストール" width="640"/>
</p>

1. この URL をコピー：`https://github.com/mitunmanav/anyone-can-code`
2. Codex → **Plugins** → **+** → **Add a Marketplace** → URL を貼り付け
3. **Anyone Can Code** を探して **Install**
4. **Hooks** を開き、すべての ACC フックをオンにし、それぞれを **trust**（必須 —— Codex は自動では信頼しません）
5. Codex を **再起動**し、プラグインツールがオンか確認
6. プロジェクトフォルダを開く → `$setup` を実行 → 作りたいものを伝える

任意（マーケットプレイスのみ —— フック、再起動、`$setup` は必要）：

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

動画：[docs/media/install-setup.mp4](../docs/media/install-setup.mp4) · サイトの完全ガイド：[anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/#install)

---

## うまくいかないとき

| 表示 | 試すこと |
|------|----------|
| マーケット / インストール失敗 | 上の **完全な** GitHub URL を貼る（短い名前ではない） |
| インストール済みだが動かない | **すべての** ACC フックを信頼し、Codex を完全再起動 |
| `$setup` が何もしない | 先に **プロジェクトフォルダ** を開き、**新しいチャット** で `$setup` を再試行 |
| まだ詰まる | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) または [問題を報告](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

[Discord](https://discord.gg/qgS29y7TqP) は短い質問向け。壊れているときは Issues を使ってください。

---

## 便利なコマンド

普通の言葉でも話せます。はっきり切り替えたいときに：

| コマンド | 使うとき |
|----------|----------|
| `$setup` | プロジェクト初回 — 作業の準備 |
| `$orchestrator` | どこから始めるか分からないときの入口 |
| `$help` / `$status` | 今どこか、次は何か |
| `$resume` | 中断のあと続ける |
| `$verify` | 本当に完了したか確認 |
| `$fix` | 同じ失敗が続くとき |

---

## リンク

[ウェブサイト](https://anyone-can-code.vercel.app/) · [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) · [プライバシー](../docs/PRIVACY.md) · [利用規約](../docs/TERMS.md) · [コントリビュート](../.github/CONTRIBUTING.md)
