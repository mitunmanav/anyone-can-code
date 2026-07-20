<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Einfache Sprache → planen → bauen → prüfen.</strong><br/>
  Kostenloses Codex-Plugin für Menschen, die keine Ingenieure sind.<br/>
  Sag, was du willst. ACC hilft planen, bauen und prüfen, ob es funktioniert.
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
  <a href="https://anyone-can-code.vercel.app/#install"><strong>Kostenlos installieren</strong></a>
  ·
  <a href="../docs/FIRST_DAY.md">Erster Tag</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">Problem melden</a>
</p>

<p align="center">
  <strong>Sprachen:</strong>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.hi.md">हिन्दी</a> ·
  <a href="README.fr.md">Français</a> ·
  Deutsch
</p>

---

## Was es ist

**Anyone Can Code (ACC)** ist ein kostenloses Open-Source-Plugin für [OpenAI Codex](https://openai.com/codex/).  
Kein neuer Agent. Keine IDE. **Codex schreibt den Code.** ACC gibt dem Arbeitspfad Klarheit.

| Schritt | Was du bekommst |
|---------|-----------------|
| **Planen** | Ein klarer Weg vor großen Änderungen |
| **Bauen** | Schritt für Schritt in deinem Projekt |
| **Prüfen** | Echte „ist es fertig?“-Kontrolle |
| **Merken** | **Desktop:** Auto-Gedächtnis bei vertrauenswürdigen Hooks. **CLI:** noch nicht — `$learn` / `$wiki` |

**Ein Plugin** für Desktop und CLI — gleicher Name: **Anyone Can Code**.

Offene Beta · Desktop **v2.0.0-beta.4** (Auto-Gedächtnis) · CLI-Gedächtnis noch manuell.

**Du brauchst:** [Codex](https://openai.com/codex/) (Desktop und/oder CLI) · Python 3

Ich bin **Mitun**. Ein Produkt, das ich mit ACC ausgeliefert habe: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2).

---

## Installieren — Desktop

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Anyone Can Code in Codex Desktop installieren" width="560"/>
</p>

1. Kopieren: `https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → einfügen
3. **Anyone Can Code** installieren
4. **Hooks** → aktivieren + **allen ACC-Hooks vertrauen** (Pflicht)
5. Neu starten → Projektordner öffnen → `$setup` → sagen, was du willst

Video: [Website](https://anyone-can-code.vercel.app/#install) · [mp4](../docs/media/install-setup.mp4)

---

## Installieren — CLI

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

1. Im Projektordner: `codex`
2. `/plugins` → **Anyone Can Code** installieren (gleich wie Desktop)
3. `/hooks` → **allen** ACC-Hooks vertrauen
4. Neuer Thread → `$setup` → sagen, was du willst

---

## Gedächtnis

| Du nutzt | Auto-Gedächtnis? |
|----------|------------------|
| **Codex Desktop** | **Ja** — nach Vertrauen in ACC-Hooks |
| **Codex CLI** | **Noch nicht** — speichern mit `$learn` / `$wiki` / `$capture` |

Auf dem Desktop kann ACC Ziele, Entscheidungen und offene Arbeit auf deinem Rechner behalten (unter `.codex/anyone-can-code/`). Nichts geht an ACC-Server.

**Tipp:** Nach jedem Plugin-Update Hooks erneut vertrauen, dann neu starten.

---

## Alltag

Du kannst auch einfach in einfacher Sprache sprechen.

| Eingabe | Wann |
|---------|------|
| `$setup` | Erstes Mal im Projekt |
| `$status` / `$help` | Wo bin ich? Was als Nächstes? |
| `$resume` | Nach einer Pause weiter |
| `$verify` | Wirklich fertig? |
| `$fix` | Derselbe Fehler kommt wieder |

Beispiel: *„Baue einen einfachen Ausgaben-Tracker und erkläre jeden Schritt in einfacher Sprache.“*

Erster voller Durchlauf: **[docs/FIRST_DAY.md](../docs/FIRST_DAY.md)**

---

## Wenn etwas scheitert

| Problem | Fix |
|---------|-----|
| Marketplace nimmt nicht an | Die **volle** GitHub-URL oben nutzen |
| Nach Install nichts geht | **Allen** ACC-Hooks vertrauen, neu starten, neuer Chat |
| Desktop vergisst | Hooks nicht vertraut (oder nach Update nicht erneut) |
| Erwartet Auto-Gedächtnis in CLI | Noch nicht — `$learn` / `$wiki`, oder Desktop |
| Altes „nur CLI“-Paket | **Anyone Can Code CLI** entfernen; **Anyone Can Code** einmal installieren |
| `$setup` stumm | Zuerst einen **Projektordner** öffnen |

Immer noch stecken? [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discord](https://discord.gg/qgS29y7TqP) · [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)

---

## Links

[Website](https://anyone-can-code.vercel.app/) · [Roadmap](../ROADMAP.md) · [Erster Tag](../docs/FIRST_DAY.md) · [Datenschutz](../docs/PRIVACY.md) · [Nutzungsbedingungen](../docs/TERMS.md) · [Mitwirken](../.github/CONTRIBUTING.md)

MIT · Built by [Mitun](https://github.com/mitunmanav)
