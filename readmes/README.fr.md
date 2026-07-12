<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

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

<p align="center">
  <strong>Un plugin Codex Desktop pour les non-ingénieurs.</strong><br/>
  Dites ce que vous voulez en langage simple. ACC aide à planifier, construire et vérifier que ça marche vraiment.
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

## C’est quoi

**Anyone Can Code (ACC)** est un plugin gratuit pour **Codex Desktop** sur Windows. Fait pour les non-techniques — y compris moi.

Vous décrivez une idée, un correctif ou un projet en mots normaux. ACC vous guide :

| Étape | Ce que vous obtenez |
|-------|---------------------|
| **Planifier** | Un chemin clair avant les gros changements |
| **Construire** | Du travail pas à pas dans votre projet |
| **Vérifier** | Un vrai « c’est fini ? », pas juste « ça a l’air bien » |

C’est un plugin **natif Codex** — écrit d’après la [doc officielle Codex](https://openai.com/codex/), pas porté depuis Claude, Cursor ou d’autres agents.

Je suis **Mitun**. J’utilise ACC moi-même. Un vrai produit livré avec : [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2). Bêta ouverte : **v1.1.0-beta.3**.

**Il vous faut :** Windows · [Codex Desktop](https://openai.com/codex/) · Python

---

## Installer

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Installer Anyone Can Code dans Codex Desktop" width="640"/>
</p>

1. Copiez cette URL : `https://github.com/mitunmanav/anyone-can-code`
2. Dans Codex → **Plugins** → **+** → **Add a Marketplace** → collez l’URL
3. Trouvez **Anyone Can Code** → **Install**
4. Ouvrez **Hooks** → activez tous les hooks ACC et **faites confiance** à chacun (obligatoire — Codex ne fait pas confiance tout seul)
5. **Redémarrez** Codex et confirmez que les outils du plugin sont actifs
6. Ouvrez un dossier projet → lancez `$setup` → dites ce que vous voulez construire

Optionnel (marketplace seul — hooks, redémarrage et `$setup` restent nécessaires) :

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Vidéo : [docs/media/install-setup.mp4](../docs/media/install-setup.mp4) · Guide complet sur le site : [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/#install)

---

## Si ça échoue

| Ce que vous voyez | À essayer |
|-------------------|-----------|
| Échec marketplace / install | Collez l’URL GitHub **complète** ci-dessus, pas un nom court |
| Plugin installé mais rien ne marche | Faites confiance à **tous** les hooks ACC, redémarrez Codex complètement |
| `$setup` ne fait rien | Ouvrez d’abord un **dossier projet**, démarrez un **nouveau chat**, réessayez `$setup` |
| Toujours bloqué | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) ou [signaler un problème](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

[Discord](https://discord.gg/qgS29y7TqP) pour les questions rapides. Issues quand c’est cassé.

---

## Commandes utiles

Vous pouvez aussi parler en langage simple. Celles-ci aident pour un basculement clair :

| Commande | Quand l’utiliser |
|----------|------------------|
| `$setup` | Première fois dans un projet — se préparer |
| `$orchestrator` | Porte principale quand on ne sait pas par où commencer |
| `$help` / `$status` | Où vous êtes et la suite |
| `$resume` | Continuer après une pause |
| `$verify` | Vérifier que le travail est vraiment fini |
| `$fix` | Quand la même chose échoue encore |

---

## Liens

[Site](https://anyone-can-code.vercel.app/) · [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) · [Confidentialité](../docs/PRIVACY.md) · [Conditions](../docs/TERMS.md) · [Contribuer](../.github/CONTRIBUTING.md)

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/anyone-can-code&type=Date)](https://star-history.com/#mitunmanav/anyone-can-code&Date)
