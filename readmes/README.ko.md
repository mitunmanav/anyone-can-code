<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

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

<p align="center">
  <strong>엔지니어가 아닌 사람을 위한 Codex Desktop 플러그인.</strong><br/>
  원하는 것을 평범한 말로 말하세요. ACC가 계획, 구축, 실제로 되는지 확인까지 돕습니다.
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

## 무엇인가요

**Anyone Can Code (ACC)**는 Windows용 **Codex Desktop** 무료 플러그인입니다. 비기술자를 위해 만들었습니다 — 저 포함.

아이디어, 수정, 프로젝트를 평범한 말로 설명하세요. ACC가 다음 단계로 안내합니다:

| 단계 | 얻는 것 |
|------|---------|
| **계획** | 큰 변경 전 명확한 경로 |
| **구축** | 프로젝트에서 한 걸음씩 작업 |
| **확인** | “괜찮아 보임”이 아닌 진짜 “끝났나?” 점검 |

**네이티브 Codex** 플러그인입니다 — [Codex 공식 문서](https://openai.com/codex/) 기준으로 작성했고, Claude·Cursor·다른 에이전트에서 이식한 것이 아닙니다.

저는 **Mitun**입니다. ACC를 직접 씁니다. 이걸로 낸 실제 제품: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2). 오픈 베타: **v1.1.0-beta.3**.

**필요:** Windows · [Codex Desktop](https://openai.com/codex/) · Python

---

## 설치

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Codex Desktop에 Anyone Can Code 설치" width="640"/>
</p>

1. 이 URL 복사: `https://github.com/mitunmanav/anyone-can-code`
2. Codex → **Plugins** → **+** → **Add a Marketplace** → URL 붙여넣기
3. **Anyone Can Code** 찾기 → **Install**
4. **Hooks** 열기 → 모든 ACC 훅 켜고 각각 **trust** (필수 — Codex는 자동 신뢰 안 함)
5. Codex **재시작** 후 플러그인 도구가 켜져 있는지 확인
6. 프로젝트 폴더 열기 → `$setup` 실행 → 만들고 싶은 것 말하기

선택 (마켓플레이스만 — 훅, 재시작, `$setup`은 여전히 필요):

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

영상: [docs/media/install-setup.mp4](../docs/media/install-setup.mp4) · 사이트 전체 안내: [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/#install)

---

## 문제가 생기면

| 보이는 것 | 시도할 것 |
|-----------|-----------|
| 마켓플레이스 / 설치 실패 | 위 **전체** GitHub URL 붙이기 (짧은 이름 말고) |
| 설치됐는데 안 됨 | **모든** ACC 훅 신뢰 후 Codex 완전 재시작 |
| `$setup`이 아무 것도 안 함 | 먼저 **프로젝트 폴더** 열고 **새 채팅**에서 `$setup` 다시 |
| 여전히 막힘 | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) 또는 [문제 신고](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

[Discord](https://discord.gg/qgS29y7TqP)는 빠른 질문용. 고장난 건 Issues로.

---

## 유용한 명령

평범한 말로도 됩니다. 분명히 전환하고 싶을 때:

| 명령 | 언제 |
|------|------|
| `$setup` | 프로젝트 처음 — 작업 준비 |
| `$orchestrator` | 어디서 시작할지 모를 때 메인 입구 |
| `$help` / `$status` | 지금 어디, 다음은 뭐 |
| `$resume` | 쉬었다가 이어하기 |
| `$verify` | 정말 끝났는지 확인 |
| `$fix` | 같은 실패가 반복될 때 |

---

## 링크

[웹사이트](https://anyone-can-code.vercel.app/) · [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) · [개인정보](../docs/PRIVACY.md) · [이용약관](../docs/TERMS.md) · [기여](../.github/CONTRIBUTING.md)
