<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>ふつうの言葉 → 計画 → 構築 → 確認。</strong><br/>
  エンジニアではない人向けの無料 Codex プラグイン。<br/>
  ほしいことを伝えてください。ACC が計画・構築・動作確認まで手伝います。
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
  <a href="https://anyone-can-code.vercel.app/#install"><strong>無料でインストール</strong></a>
  ·
  <a href="../docs/FIRST_DAY.md">初日</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">問題を報告</a>
</p>

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

---

## これは何か

**Anyone Can Code (ACC)** は [OpenAI Codex](https://openai.com/codex/) 向けの無料オープンソースプラグインです。  
新しいエージェントでも IDE でもありません。**コードは Codex が書きます。** ACC は作業に道筋をつけます。

| ステップ | 得られること |
|----------|--------------|
| **計画** | 大きな変更の前に明確な道筋 |
| **構築** | プロジェクト内で一歩ずつ進める |
| **確認** | 「できた？」を本当に確かめる |
| **記憶** | **Desktop：** hooks を信頼すると自動記憶。**CLI：** まだ — `$learn` / `$wiki` |

**プラグインは1つ** — Desktop と CLI で同じ名前：**Anyone Can Code**。

公開ベータ · Desktop **v2.0.0-beta.4**（自動記憶）· CLI の記憶は当面マニュアル。

**必要なもの：** [Codex](https://openai.com/codex/)（Desktop および/または CLI）· Python 3

**Mitun** です。ACC で出した製品の一例：[Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2)。

---

## インストール — Desktop

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Codex Desktop に Anyone Can Code を入れる" width="560"/>
</p>

1. コピー：`https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → 貼り付け
3. **Anyone Can Code** をインストール
4. **Hooks** → 有効化 + ACC の hooks を **すべて信頼**（必須）
5. 再起動 → プロジェクトフォルダを開く → `$setup` → ほしいことを伝える

動画：[サイト](https://anyone-can-code.vercel.app/#install) · [mp4](../docs/media/install-setup.mp4)

---

## インストール — CLI

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

1. プロジェクトフォルダで：`codex`
2. `/plugins` → **Anyone Can Code** をインストール（Desktop と同じ）
3. `/hooks` → ACC の hooks を **すべて信頼**
4. 新しいスレッド → `$setup` → ほしいことを伝える

---

## 記憶

| 使うもの | 自動記憶？ |
|----------|------------|
| **Codex Desktop** | **はい** — ACC hooks を信頼したあと |
| **Codex CLI** | **まだ** — `$learn` / `$wiki` / `$capture` で保存 |

Desktop では、目標・決定・途中の作業を自分の PC に残せます（`.codex/anyone-can-code/`）。ACC のサーバーには送りません。

**ヒント：** プラグイン更新のたびに、hooks を再度信頼してから再起動。

---

## 日常の使い方

ふつうの言葉で話すだけでも大丈夫です。

| 入力 | いつ |
|------|------|
| `$setup` | プロジェクトで初めて |
| `$status` / `$help` | 今どこ？次は？ |
| `$resume` | 休憩のあと続きから |
| `$verify` | 本当にできた？ |
| `$fix` | 同じエラーが続くとき |

例：*「簡単な家計簿を作って、各ステップをやさしい言葉で説明して。」*

初日の流れ：**[docs/FIRST_DAY.md](../docs/FIRST_DAY.md)**

---

## うまくいかないとき

| 問題 | 対処 |
|------|------|
| Marketplace が追加できない | 上の GitHub URL を **フル** で使う |
| 入れたのに動かない | ACC hooks を **すべて信頼**、再起動、新しいチャット |
| Desktop で忘れる | hooks 未信頼（更新後の再信頼忘れ） |
| CLI で自動記憶を期待 | まだ — `$learn` / `$wiki`、または Desktop |
| 古い「CLI 専用」 | **Anyone Can Code CLI** を削除し、**Anyone Can Code** を1回だけ入れる |
| `$setup` が無反応 | 先に **プロジェクトフォルダ** を開く |

まだ困ったら？ [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discord](https://discord.gg/qgS29y7TqP) · [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)

---

## リンク

[サイト](https://anyone-can-code.vercel.app/) · [ロードマップ](../ROADMAP.md) · [初日](../docs/FIRST_DAY.md) · [プライバシー](../docs/PRIVACY.md) · [利用規約](../docs/TERMS.md) · [コントリビュート](../.github/CONTRIBUTING.md)

MIT · Built by [Mitun](https://github.com/mitunmanav)
