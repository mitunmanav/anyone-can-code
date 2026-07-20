<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Langage simple → planifier → construire → vérifier.</strong><br/>
  Plugin Codex gratuit pour les non-ingénieurs.<br/>
  Dites ce que vous voulez. ACC aide à planifier, construire et vérifier que ça marche.
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
  <a href="https://anyone-can-code.vercel.app/#install"><strong>Installer gratuitement</strong></a>
  ·
  <a href="../docs/FIRST_DAY.md">Premier jour</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">Signaler un problème</a>
</p>

<p align="center">
  <strong>Langues :</strong>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.hi.md">हिन्दी</a> ·
  Français ·
  <a href="README.de.md">Deutsch</a>
</p>

---

## Qu’est-ce que c’est

**Anyone Can Code (ACC)** est un plugin gratuit et open source pour [OpenAI Codex](https://openai.com/codex/).  
Pas un nouvel agent. Pas un IDE. **Codex écrit le code.** ACC donne un chemin clair.

| Étape | Ce que vous obtenez |
|-------|---------------------|
| **Planifier** | Un chemin clair avant les gros changements |
| **Construire** | Le travail pas à pas dans votre projet |
| **Vérifier** | Un vrai « c’est fini ? », pas seulement « ça a l’air bien » |
| **Se souvenir** | **Desktop :** mémoire auto si les hooks sont de confiance. **CLI :** pas encore — `$learn` / `$wiki` |

**Un seul plugin** pour Desktop et CLI — même nom : **Anyone Can Code**.

Bêta ouverte · Desktop **v2.0.0-beta.4** (mémoire auto) · mémoire CLI encore manuelle.

**Il faut :** [Codex](https://openai.com/codex/) (Desktop et/ou CLI) · Python 3

Je suis **Mitun**. Un produit sorti avec ACC : [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2).

---

## Installer — Desktop

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Installer Anyone Can Code dans Codex Desktop" width="560"/>
</p>

1. Copiez : `https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → collez
3. Installez **Anyone Can Code**
4. **Hooks** → activez + **faites confiance à tous** les hooks ACC (obligatoire)
5. Redémarrez → ouvrez un dossier projet → `$setup` → dites ce que vous voulez

Vidéo : [site](https://anyone-can-code.vercel.app/#install) · [mp4](../docs/media/install-setup.mp4)

---

## Installer — CLI

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

1. Dans le dossier projet : `codex`
2. `/plugins` → installez **Anyone Can Code** (même plugin que Desktop)
3. `/hooks` → **faites confiance** à tous les hooks ACC
4. Nouveau fil → `$setup` → dites ce que vous voulez

---

## Mémoire

| Vous utilisez | Mémoire auto ? |
|---------------|----------------|
| **Codex Desktop** | **Oui** — après confiance aux hooks ACC |
| **Codex CLI** | **Pas encore** — enregistrez avec `$learn` / `$wiki` / `$capture` |

Sur Desktop, ACC peut retenir objectifs, décisions et travail en cours sur votre machine (dans `.codex/anyone-can-code/`). Rien n’est envoyé aux serveurs ACC.

**Astuce :** Après chaque mise à jour du plugin, refaites confiance aux hooks, puis redémarrez.

---

## Usage quotidien

Vous pouvez aussi parler en langage simple.

| Tapez | Quand |
|-------|-------|
| `$setup` | Première fois dans un projet |
| `$status` / `$help` | Où en suis-je ? Ensuite ? |
| `$resume` | Reprendre après une pause |
| `$verify` | C’est vraiment fini ? |
| `$fix` | La même erreur revient |

Exemple : *« Crée un suivi de dépenses simple et explique chaque étape en langage simple. »*

Première session complète : **[docs/FIRST_DAY.md](../docs/FIRST_DAY.md)**

---

## Si quelque chose échoue

| Problème | Correction |
|----------|------------|
| Marketplace refuse d’ajouter | Utilisez l’URL GitHub **complète** ci-dessus |
| Rien ne marche après install | **Faites confiance à tous** les hooks ACC, redémarrez, nouveau chat |
| Oublie sur Desktop | Hooks non de confiance (ou pas re-confiance après update) |
| Attend la mémoire auto en CLI | Pas encore — `$learn` / `$wiki`, ou utilisez Desktop |
| Ancien paquet « CLI seul » | Désinstallez **Anyone Can Code CLI** ; installez **Anyone Can Code** une fois |
| `$setup` silencieux | Ouvrez d’abord un **dossier projet** |

Toujours bloqué ? [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discord](https://discord.gg/qgS29y7TqP) · [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)

---

## Liens

[Site](https://anyone-can-code.vercel.app/) · [Feuille de route](../ROADMAP.md) · [Premier jour](../docs/FIRST_DAY.md) · [Confidentialité](../docs/PRIVACY.md) · [Conditions](../docs/TERMS.md) · [Contribuer](../.github/CONTRIBUTING.md)

MIT · Built by [Mitun](https://github.com/mitunmanav)
