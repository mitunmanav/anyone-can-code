<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Lenguaje simple → planificar → construir → comprobar.</strong><br/>
  Plugin gratuito de Codex para quienes no son ingenieros.<br/>
  Di lo que quieres. ACC te ayuda a planificar, construir y comprobar que funciona.
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
  <a href="https://anyone-can-code.vercel.app/#install"><strong>Instalar gratis</strong></a>
  ·
  <a href="../docs/FIRST_DAY.md">Primer día</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">Reportar un problema</a>
</p>

<p align="center">
  <strong>Idiomas:</strong>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  Español ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.hi.md">हिन्दी</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a>
</p>

---

## Qué es

**Anyone Can Code (ACC)** es un plugin gratuito y de código abierto para [OpenAI Codex](https://openai.com/codex/).  
No es un agente nuevo. No es un IDE. **Codex escribe el código.** ACC da un camino claro.

| Paso | Qué obtienes |
|------|----------------|
| **Planificar** | Un camino claro antes de cambios grandes |
| **Construir** | Trabajo paso a paso en tu proyecto |
| **Comprobar** | Una revisión real de “¿está listo?” |
| **Recordar** | **Desktop:** memoria automática si confías en los hooks. **CLI:** aún no — usa `$learn` / `$wiki` |

**Un plugin** para Desktop y CLI — mismo nombre: **Anyone Can Code**.

Beta abierta · Desktop **v2.0.0-beta.4** (memoria automática) · CLI aún con memoria manual.

**Necesitas:** [Codex](https://openai.com/codex/) (Desktop y/o CLI) · Python 3

Soy **Mitun**. Un producto que publiqué con ACC: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2).

---

## Instalar — Desktop

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Instalar Anyone Can Code en Codex Desktop" width="560"/>
</p>

1. Copia: `https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → pega
3. Instala **Anyone Can Code**
4. **Hooks** → activa + **confía en todos** los hooks de ACC (obligatorio)
5. Reinicia → abre una carpeta de proyecto → `$setup` → di lo que quieres

Vídeo: [web](https://anyone-can-code.vercel.app/#install) · [mp4](../docs/media/install-setup.mp4)

---

## Instalar — CLI

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

1. En la carpeta del proyecto: `codex`
2. `/plugins` → instala **Anyone Can Code** (el mismo plugin que Desktop)
3. `/hooks` → **confía** en todos los hooks de ACC
4. Hilo nuevo → `$setup` → di lo que quieres

---

## Memoria

| Usas | ¿Memoria automática? |
|------|----------------------|
| **Codex Desktop** | **Sí** — después de confiar en los hooks de ACC |
| **Codex CLI** | **Aún no** — guarda con `$learn` / `$wiki` / `$capture` |

En Desktop, ACC puede recordar metas, decisiones y trabajo abierto en tu máquina (en `.codex/anyone-can-code/`). Nada se envía a servidores de ACC.

**Consejo:** Tras cada actualización del plugin, confía otra vez en los hooks y reinicia.

---

## Uso diario

También puedes hablar en lenguaje simple.

| Escribe | Cuándo |
|---------|--------|
| `$setup` | Primera vez en un proyecto |
| `$status` / `$help` | ¿Dónde estoy? ¿Qué sigue? |
| `$resume` | Continuar después de una pausa |
| `$verify` | ¿Está realmente listo? |
| `$fix` | El mismo error se repite |

Ejemplo: *“Crea un rastreador de gastos simple y explica cada paso en lenguaje sencillo.”*

Primera sesión completa: **[docs/FIRST_DAY.md](../docs/FIRST_DAY.md)**

---

## Si algo falla

| Problema | Solución |
|----------|----------|
| El marketplace no añade | Usa la URL **completa** de GitHub de arriba |
| Nada funciona tras instalar | **Confía en todos** los hooks de ACC, reinicia, chat nuevo |
| Olvida en Desktop | Hooks sin confiar (o sin volver a confiar tras update) |
| Espera memoria automática en CLI | Aún no — usa `$learn` / `$wiki`, o usa Desktop |
| Paquete antiguo “solo CLI” | Desinstala **Anyone Can Code CLI**; instala **Anyone Can Code** una vez |
| `$setup` no responde | Abre primero una **carpeta de proyecto** |

¿Sigue fallando? [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discord](https://discord.gg/qgS29y7TqP) · [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)

---

## Enlaces

[Web](https://anyone-can-code.vercel.app/) · [Roadmap](../ROADMAP.md) · [Primer día](../docs/FIRST_DAY.md) · [Privacidad](../docs/PRIVACY.md) · [Términos](../docs/TERMS.md) · [Contribuir](../.github/CONTRIBUTING.md)

MIT · Hecho por [Mitun](https://github.com/mitunmanav)
