<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Idiomas:</strong>
  <a href="README.md">English</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  Español ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.hi.md">हिन्दी</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a>
</p>

<p align="center">
  <strong>Un plugin de Codex Desktop para quienes no son ingenieros.</strong><br/>
  Di lo que quieres en palabras simples. ACC te ayuda a planificar, construir y comprobar que de verdad funciona.
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

## Qué es

**Anyone Can Code (ACC)** es un plugin gratis para **Codex Desktop** en Windows. Está hecho para personas no técnicas — incluido yo.

Describes una idea, una corrección o un proyecto con palabras normales. ACC te guía por:

| Paso | Qué obtienes |
|------|--------------|
| **Planificar** | Un camino claro antes de cambios grandes |
| **Construir** | Trabajo hecho paso a paso en tu proyecto |
| **Comprobar** | Una pasada real de “¿está listo?”, no solo “se ve bien” |

Es un plugin **nativo de Codex** — escrito desde la [documentación oficial de Codex](https://openai.com/codex/), no portado de Claude, Cursor u otros agentes.

Soy **Mitun**. Uso ACC yo mismo. Un producto real que publiqué con él: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2). Beta abierta: **v1.1.0-beta.3**.

**Necesitas:** Windows · [Codex Desktop](https://openai.com/codex/) · Python

---

## Instalar

<p align="center">
  <img src="docs/media/install-setup.gif" alt="Instalar Anyone Can Code en Codex Desktop" width="640"/>
</p>

1. Copia esta URL: `https://github.com/mitunmanav/anyone-can-code`
2. En Codex → **Plugins** → **+** → **Add a Marketplace** → pega la URL
3. Busca **Anyone Can Code** → **Install**
4. Abre **Hooks** → activa todos los hooks de ACC y **confía** en cada uno (obligatorio — Codex no confía solo)
5. **Reinicia** Codex y confirma que las herramientas del plugin están activas
6. Abre una carpeta de proyecto → ejecuta `$setup` → di lo que quieres construir

Opcional (solo marketplace — aún necesitas hooks, reinicio y `$setup`):

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Vídeo: [docs/media/install-setup.mp4](docs/media/install-setup.mp4) · Guía completa en el sitio: [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/#install)

---

## Si algo falla

| Lo que ves | Qué probar |
|------------|------------|
| Fallo de marketplace / instalación | Pega la URL **completa** de GitHub de arriba, no un nombre corto |
| Plugin instalado pero no hace nada | Confía en **todos** los hooks de ACC y reinicia Codex por completo |
| `$setup` no hace nada | Abre primero una **carpeta de proyecto**, inicia un **chat nuevo**, prueba `$setup` otra vez |
| Sigues atascado | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) o [reporta un problema](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

[Discord](https://discord.gg/qgS29y7TqP) vale para preguntas rápidas. Usa Issues cuando algo esté roto.

---

## Comandos útiles

También puedes hablar en lenguaje simple. Estos ayudan cuando quieres un atajo claro:

| Comando | Cuándo usarlo |
|---------|---------------|
| `$setup` | Primera vez en un proyecto — prepararte para trabajar |
| `$orchestrator` | Puerta principal cuando no sabes por dónde empezar |
| `$help` / `$status` | Dónde estás y qué sigue |
| `$resume` | Continuar después de una pausa |
| `$verify` | Comprobar que el trabajo está de verdad listo |
| `$fix` | Cuando lo mismo falla una y otra vez |

---

## Enlaces

[Sitio web](https://anyone-can-code.vercel.app/) · [Discusiones](https://github.com/mitunmanav/anyone-can-code/discussions) · [Privacidad](docs/PRIVACY.md) · [Términos](docs/TERMS.md) · [Contribuir](.github/CONTRIBUTING.md)

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/anyone-can-code&type=Date)](https://star-history.com/#mitunmanav/anyone-can-code&Date)
