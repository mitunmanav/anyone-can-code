<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Linguagem simples → planejar → construir → verificar.</strong><br/>
  Plugin gratuito do Codex para quem não é engenheiro.<br/>
  Diga o que você quer. O ACC ajuda a planejar, construir e checar se funciona.
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
  <a href="https://anyone-can-code.vercel.app/#install"><strong>Instalar grátis</strong></a>
  ·
  <a href="../docs/FIRST_DAY.md">Primeiro dia</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">Reportar problema</a>
</p>

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

---

## O que é

**Anyone Can Code (ACC)** é um plugin gratuito e open-source para o [OpenAI Codex](https://openai.com/codex/).  
Não é um agente novo. Não é um IDE. **O Codex escreve o código.** O ACC dá um caminho claro.

| Etapa | O que você recebe |
|-------|-------------------|
| **Planejar** | Um caminho claro antes de mudanças grandes |
| **Construir** | Trabalho passo a passo no seu projeto |
| **Verificar** | Uma checagem real de “está pronto?” |
| **Lembrar** | **Desktop:** memória automática com hooks confiados. **CLI:** ainda não — use `$learn` / `$wiki` |

**Um plugin** para Desktop e CLI — mesmo nome: **Anyone Can Code**.

Beta aberto · Desktop **v2.0.0-beta.5** (memória automática) · CLI ainda com memória manual.

**Você precisa de:** [Codex](https://openai.com/codex/) (Desktop e/ou CLI) · Python 3

Eu sou o **Mitun**. Um produto que enviei com o ACC: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2).

---

## Instalar — Desktop

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Instalar Anyone Can Code no Codex Desktop" width="560"/>
</p>

1. Copie: `https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → cole
3. Instale **Anyone Can Code**
4. **Hooks** → ative + **confie em todos** os hooks do ACC (obrigatório)
5. Reinicie → abra uma pasta de projeto → `$setup` → diga o que quer

Vídeo: [site](https://anyone-can-code.vercel.app/#install) · [mp4](../docs/media/install-setup.mp4)

---

## Instalar — CLI

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

1. Na pasta do projeto: `codex`
2. `/plugins` → instale **Anyone Can Code** (mesmo plugin do Desktop)
3. `/hooks` → **confie** em todos os hooks do ACC
4. Novo chat → `$setup` → diga o que quer

---

## Memória

| Você usa | Memória automática? |
|----------|---------------------|
| **Codex Desktop** | **Sim** — depois de confiar nos hooks do ACC |
| **Codex CLI** | **Ainda não** — salve com `$learn` / `$wiki` / `$capture` |

No Desktop, o ACC pode lembrar metas, decisões e trabalho aberto no seu computador (em `.codex/anyone-can-code/`). Nada vai para servidores do ACC.

**Dica:** Depois de cada atualização do plugin, confie nos hooks de novo e reinicie.

---

## Uso no dia a dia

Você também pode só falar em linguagem simples.

| Digite | Quando |
|--------|--------|
| `$setup` | Primeira vez no projeto |
| `$status` / `$help` | Onde estou? O que vem depois? |
| `$resume` | Continuar depois de uma pausa |
| `$verify` | Está realmente pronto? |
| `$fix` | O mesmo erro volta |

Exemplo: *“Crie um rastreador de despesas simples e explique cada passo em linguagem simples.”*

Primeira sessão completa: **[docs/FIRST_DAY.md](../docs/FIRST_DAY.md)**

---

## Se algo falhar

| Problema | Correção |
|----------|----------|
| Marketplace não adiciona | Use a URL **completa** do GitHub acima |
| Nada funciona após instalar | **Confie em todos** os hooks do ACC, reinicie, chat novo |
| Esquece no Desktop | Hooks sem confiança (ou sem re-confiar após update) |
| Espera memória automática no CLI | Ainda não — use `$learn` / `$wiki`, ou use o Desktop |
| Pacote antigo “só CLI” | Remova **Anyone Can Code CLI**; instale **Anyone Can Code** uma vez |
| `$setup` silencioso | Abra primeiro uma **pasta de projeto** |

Ainda travado? [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discord](https://discord.gg/qgS29y7TqP) · [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)

---

## Links

[Site](https://anyone-can-code.vercel.app/) · [Roadmap](../ROADMAP.md) · [Primeiro dia](../docs/FIRST_DAY.md) · [Privacidade](../docs/PRIVACY.md) · [Termos](../docs/TERMS.md) · [Contribuir](../.github/CONTRIBUTING.md)

MIT · Feito por [Mitun](https://github.com/mitunmanav)
