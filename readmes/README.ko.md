<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>쉬운 말 → 계획 → 만들기 → 확인.</strong><br/>
  엔지니어가 아닌 사람을 위한 무료 Codex 플러그인.<br/>
  원하는 것을 말하세요. ACC가 계획, 구축, 동작 확인까지 돕습니다.
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
  <a href="https://anyone-can-code.vercel.app/#install"><strong>무료 설치</strong></a>
  ·
  <a href="../docs/FIRST_DAY.md">첫날</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">문제 신고</a>
</p>

<p align="center">
  <strong>언어:</strong>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  한국어 ·
  <a href="README.hi.md">हिन्दी</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a>
</p>

---

## 무엇인가

**Anyone Can Code (ACC)** 는 [OpenAI Codex](https://openai.com/codex/) 용 무료 오픈소스 플러그인입니다.  
새 에이전트가 아닙니다. IDE도 아닙니다. **코드는 Codex가 씁니다.** ACC는 작업에 길을 줍니다.

| 단계 | 얻는 것 |
|------|---------|
| **계획** | 큰 변경 전에 분명한 길 |
| **만들기** | 프로젝트에서 한 걸음씩 |
| **확인** | “끝났나?”를 진짜로 점검 |
| **기억** | **Desktop:** hooks 신뢰 시 자동 기억. **CLI:** 아직 — `$learn` / `$wiki` |

**플러그인 하나** — Desktop과 CLI 같은 이름: **Anyone Can Code**.

공개 베타 · Desktop **v2.0.0-beta.5** · Desktop + CLI · 훅 신뢰 후 자동 기억.

**필요:** [Codex](https://openai.com/codex/) (Desktop 및/또는 CLI) · Python 3

**Mitun** 입니다. ACC로 낸 제품 하나: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2).

---

## 설치 — Desktop

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Codex Desktop에 Anyone Can Code 설치" width="560"/>
</p>

1. 복사: `https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → 붙여넣기
3. **Anyone Can Code** 설치
4. **Hooks** → 켜고 ACC hooks를 **모두 신뢰** (필수)
5. 재시작 → 프로젝트 폴더 열기 → `$setup` → 원하는 것 말하기

영상: [웹사이트](https://anyone-can-code.vercel.app/#install) · [mp4](../docs/media/install-setup.mp4)

---

## 설치 — CLI

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

1. 프로젝트 폴더에서: `codex`
2. `/plugins` → **Anyone Can Code** 설치 (Desktop과 동일)
3. `/hooks` → ACC hooks **모두 신뢰**
4. 새 스레드 → `$setup` → 원하는 것 말하기

---

## 기억

| 사용 | 자동 기억? |
|------|------------|
| **Codex Desktop** | **예** — ACC hooks 신뢰 후 |
| **Codex CLI** | **아직** — `$learn` / `$wiki` / `$capture` 로 저장 |

Desktop에서는 목표, 결정, 미완료 작업을 내 PC에 남길 수 있습니다 (`.codex/anyone-can-code/`). ACC 서버로 보내지 않습니다.

**팁:** 플러그인 업데이트마다 hooks를 다시 신뢰한 뒤 재시작하세요.

---

## 일상 사용

쉬운 말로 말해도 됩니다.

| 입력 | 언제 |
|------|------|
| `$setup` | 프로젝트 처음 |
| `$status` / `$help` | 어디? 다음? |
| `$resume` | 쉬었다가 이어서 |
| `$verify` | 진짜 끝났나? |
| `$fix` | 같은 오류가 반복될 때 |

예: *“간단한 가계부를 만들고 각 단계를 쉬운 말로 설명해 줘.”*

첫 세션 전체: **[docs/FIRST_DAY.md](../docs/FIRST_DAY.md)**

---

## 안 될 때

| 문제 | 해결 |
|------|------|
| Marketplace 추가 실패 | 위 GitHub URL을 **전체**로 사용 |
| 설치 후 동작 없음 | ACC hooks **모두 신뢰**, 재시작, 새 채팅 |
| Desktop에서 잊음 | hooks 미신뢰 (또는 업데이트 후 재신뢰 안 함) |
| CLI 자동 기억 기대 | 아직 — `$learn` / `$wiki`, 또는 Desktop |
| 예전 “CLI 전용” 패키지 | **Anyone Can Code CLI** 제거 후 **Anyone Can Code** 한 번 설치 |
| `$setup` 무반응 | 먼저 **프로젝트 폴더** 열기 |

계속 막히면? [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discord](https://discord.gg/qgS29y7TqP) · [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)

---

## 링크

[웹사이트](https://anyone-can-code.vercel.app/) · [로드맵](../ROADMAP.md) · [첫날](../docs/FIRST_DAY.md) · [개인정보](../docs/PRIVACY.md) · [약관](../docs/TERMS.md) · [기여](../.github/CONTRIBUTING.md)

MIT · Built by [Mitun](https://github.com/mitunmanav)
