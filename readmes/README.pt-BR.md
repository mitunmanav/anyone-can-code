<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Idiomas:</strong>
  <a href="../README.md">English</a> ·
  Português ·
  <a href="README.es.md">Español</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.hi.md">हिन्दी</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a>
</p>

<p align="center">
  <strong>Um plugin do Codex Desktop para quem não é engenheiro.</strong><br/>
  Diga o que você quer em linguagem simples. O ACC ajuda a planejar, construir e verificar se realmente funciona.
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

## O que é

**Anyone Can Code (ACC)** é um plugin gratuito para o **Codex Desktop** no Windows. Foi feito para pessoas não técnicas — inclusive eu.

Você descreve uma ideia, uma correção ou um projeto com palavras normais. O ACC te guia por:

| Etapa | O que você recebe |
|-------|-------------------|
| **Planejar** | Um caminho claro antes de mudanças grandes |
| **Construir** | Trabalho feito passo a passo no seu projeto |
| **Verificar** | Uma checagem real de “está pronto?”, não só “parece ok” |

É um plugin **nativo do Codex** — escrito a partir da [documentação oficial do Codex](https://openai.com/codex/), não portado de Claude, Cursor ou outros agentes.

Eu sou o **Mitun**. Uso o ACC eu mesmo. Um produto real que enviei com ele: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2). Beta aberto: **v1.1.0-beta.3**.

**Você precisa de:** Windows · [Codex Desktop](https://openai.com/codex/) · Python

---

## Instalar

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Instalar Anyone Can Code no Codex Desktop" width="640"/>
</p>

1. Copie esta URL: `https://github.com/mitunmanav/anyone-can-code`
2. No Codex → **Plugins** → **+** → **Add a Marketplace** → cole a URL
3. Encontre **Anyone Can Code** → **Install**
4. Abra **Hooks** → ative todos os hooks do ACC e **confie** em cada um (obrigatório — o Codex não confia sozinho)
5. **Reinicie** o Codex e confirme que as ferramentas do plugin estão ligadas
6. Abra uma pasta de projeto → rode `$setup` → diga o que quer construir

Opcional (só marketplace — ainda precisa de hooks, reinício e `$setup`):

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Vídeo: [docs/media/install-setup.mp4](../docs/media/install-setup.mp4) · Guia completo no site: [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/#install)

---

## Se algo falhar

| O que você vê | O que tentar |
|---------------|--------------|
| Marketplace / instalação falha | Cole a URL **completa** do GitHub acima, não um nome curto |
| Plugin instalado mas nada funciona | Confie em **todos** os hooks do ACC e reinicie o Codex por completo |
| `$setup` não faz nada | Abra primeiro uma **pasta de projeto**, inicie um **chat novo**, tente `$setup` de novo |
| Ainda travado | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) ou [reporte um problema](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

[Discord](https://discord.gg/qgS29y7TqP) serve para perguntas rápidas. Use Issues quando algo estiver quebrado.

---

## Comandos úteis

Você também pode só falar em linguagem simples. Estes ajudam quando quiser um atalho claro:

| Comando | Quando usar |
|---------|-------------|
| `$setup` | Primeira vez no projeto — preparar para trabalhar |
| `$orchestrator` | Porta principal quando não sabe por onde começar |
| `$help` / `$status` | Onde você está e o que vem depois |
| `$resume` | Continuar depois de uma pausa |
| `$verify` | Checar se o trabalho realmente está pronto |
| `$fix` | Quando a mesma coisa falha de novo |

---

## Links

[Site](https://anyone-can-code.vercel.app/) · [Discussões](https://github.com/mitunmanav/anyone-can-code/discussions) · [Privacidade](../docs/PRIVACY.md) · [Termos](../docs/TERMS.md) · [Contribuir](../.github/CONTRIBUTING.md)
