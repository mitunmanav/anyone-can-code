<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Sprachen:</strong>
  <a href="README.md">English</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.hi.md">हिन्दी</a> ·
  <a href="README.fr.md">Français</a> ·
  Deutsch
</p>

<p align="center">
  <strong>Ein Codex-Desktop-Plugin für Menschen, die keine Ingenieure sind.</strong><br/>
  Sag in einfachen Worten, was du willst. ACC hilft planen, bauen und prüfen, ob es wirklich funktioniert.
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

## Was es ist

**Anyone Can Code (ACC)** ist ein kostenloses Plugin für **Codex Desktop** unter Windows. Für Nicht-Techniker gebaut — inklusive mir.

Du beschreibst eine Idee, einen Fix oder ein Projekt in normalen Worten. ACC führt dich durch:

| Schritt | Was du bekommst |
|---------|-----------------|
| **Planen** | Klarer Weg vor großen Änderungen |
| **Bauen** | Arbeit Schritt für Schritt im Projekt |
| **Prüfen** | Echter „fertig?“-Check, nicht nur „sieht gut aus“ |

Es ist ein **natives Codex**-Plugin — geschrieben nach der [offiziellen Codex-Doku](https://openai.com/codex/), nicht von Claude, Cursor oder anderen Agenten portiert.

Ich bin **Mitun**. Ich nutze ACC selbst. Ein echtes Produkt damit: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2). Offene Beta: **v1.1.0-beta.3**.

**Du brauchst:** Windows · [Codex Desktop](https://openai.com/codex/) · Python

---

## Installieren

<p align="center">
  <img src="docs/media/install-setup.gif" alt="Anyone Can Code in Codex Desktop installieren" width="640"/>
</p>

1. Diese URL kopieren: `https://github.com/mitunmanav/anyone-can-code`
2. In Codex → **Plugins** → **+** → **Add a Marketplace** → URL einfügen
3. **Anyone Can Code** finden → **Install**
4. **Hooks** öffnen → alle ACC-Hooks an und jeweils **trust** (pflicht — Codex vertraut nicht automatisch)
5. Codex **neu starten** und prüfen, dass Plugin-Tools an sind
6. Projektordner öffnen → `$setup` ausführen → sagen, was du bauen willst

Optional (nur Marketplace — Hooks, Neustart und `$setup` bleiben nötig):

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Video: [docs/media/install-setup.mp4](docs/media/install-setup.mp4) · Voller Guide auf der Seite: [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/#install)

---

## Wenn etwas schiefgeht

| Was du siehst | Was versuchen |
|---------------|---------------|
| Marketplace / Install scheitert | Die **volle** GitHub-URL oben einfügen, keinen Kurznamen |
| Plugin installiert, nichts läuft | **Alle** ACC-Hooks trusten, Codex komplett neu starten |
| `$setup` macht nichts | Zuerst **Projektordner** öffnen, **neuen Chat**, `$setup` erneut |
| Immer noch stecken | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) oder [Problem melden](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

[Discord](https://discord.gg/qgS29y7TqP) für schnelle Fragen. Issues wenn etwas kaputt ist.

---

## Nützliche Befehle

Du kannst auch einfach in Alltagssprache reden. Diese helfen für klaren Wechsel:

| Befehl | Wann |
|--------|------|
| `$setup` | Erste Mal im Projekt — bereit machen |
| `$orchestrator` | Haupttür wenn unklar, wo starten |
| `$help` / `$status` | Wo du bist und was als Nächstes |
| `$resume` | Nach Pause weiter |
| `$verify` | Prüfen ob Arbeit wirklich fertig |
| `$fix` | Wenn dasselbe immer wieder scheitert |

---

## Links

[Website](https://anyone-can-code.vercel.app/) · [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) · [Datenschutz](docs/PRIVACY.md) · [Bedingungen](docs/TERMS.md) · [Mitwirken](.github/CONTRIBUTING.md)

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/anyone-can-code&type=Date)](https://star-history.com/#mitunmanav/anyone-can-code&Date)
