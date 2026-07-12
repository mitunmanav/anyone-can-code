<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>भाषाएँ:</strong>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  हिन्दी ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a>
</p>

<p align="center">
  <strong>इंजीनियर न होने वालों के लिए Codex Desktop प्लगिन।</strong><br/>
  साधारण भाषा में बताएँ आप क्या चाहते हैं। ACC प्लान, बिल्ड और असली जाँच में मदद करता है।
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

## यह क्या है

**Anyone Can Code (ACC)** Windows पर **Codex Desktop** का मुफ़्त प्लगिन है। गैर-तकनीकी लोगों के लिए बना है — मेरे लिए भी।

आप सामान्य शब्दों में आइडिया, फिक्स या प्रोजेक्ट बताते हैं। ACC आपको इन चरणों से ले जाता है:

| चरण | आपको मिलता है |
|-----|---------------|
| **प्लान** | बड़े बदलाव से पहले साफ़ रास्ता |
| **बिल्ड** | प्रोजेक्ट में कदम-दर-कदम काम |
| **चेक** | असली “हो गया?” जाँच, सिर्फ़ “ठीक लगता है” नहीं |

यह **नेटिव Codex** प्लगिन है — [Codex आधिकारिक दस्तावेज़](https://openai.com/codex/) से लिखा, Claude, Cursor या अन्य एजेंट से पोर्ट नहीं।

मैं **Mitun** हूँ। खुद ACC इस्तेमाल करता हूँ। इससे भेजा एक असली प्रोडक्ट: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2)। ओपन बीटा: **v1.1.0-beta.3**।

**ज़रूरी:** Windows · [Codex Desktop](https://openai.com/codex/) · Python

---

## इंस्टॉल

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Codex Desktop में Anyone Can Code इंस्टॉल" width="640"/>
</p>

1. यह URL कॉपी करें: `https://github.com/mitunmanav/anyone-can-code`
2. Codex → **Plugins** → **+** → **Add a Marketplace** → URL पेस्ट करें
3. **Anyone Can Code** ढूँढें → **Install**
4. **Hooks** खोलें → सारे ACC hooks ऑन करें और हर एक को **trust** करें (ज़रूरी — Codex खुद trust नहीं करता)
5. Codex **रीस्टार्ट** करें और प्लगिन टूल्स ऑन हों, पुष्टि करें
6. प्रोजेक्ट फ़ोल्डर खोलें → `$setup` चलाएँ → बताएँ क्या बनाना है

वैकल्पिक (सिर्फ़ marketplace — hooks, restart, `$setup` फिर भी चाहिए):

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

वीडियो: [docs/media/install-setup.mp4](../docs/media/install-setup.mp4) · पूरी गाइड साइट पर: [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/#install)

---

## अगर कुछ फेल हो

| जो दिखे | क्या आज़माएँ |
|---------|--------------|
| Marketplace / इंस्टॉल फेल | ऊपर वाला **पूरा** GitHub URL पेस्ट करें, छोटा नाम नहीं |
| प्लगिन लगा पर कुछ काम नहीं | **सारे** ACC hooks trust करें, Codex पूरी तरह restart |
| `$setup` कुछ नहीं करता | पहले **प्रोजेक्ट फ़ोल्डर** खोलें, **नया चैट**, फिर `$setup` |
| फिर भी अटके | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) या [समस्या रिपोर्ट](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

[Discord](https://discord.gg/qgS29y7TqP) तेज़ सवालों के लिए ठीक। टूटा हो तो Issues।

---

## उपयोगी कमांड

साधारण भाषा में भी बात कर सकते हैं। साफ़ स्विच चाहिए तो:

| कमांड | कब |
|-------|-----|
| `$setup` | प्रोजेक्ट पहली बार — काम की तैयारी |
| `$orchestrator` | पता न हो कहाँ से शुरू — मुख्य दरवाज़ा |
| `$help` / `$status` | आप कहाँ हैं, आगे क्या |
| `$resume` | ब्रेक के बाद जारी |
| `$verify` | काम सच में पूरा है या नहीं |
| `$fix` | वही चीज़ बार-बार फेल हो |

---

## लिंक

[वेबसाइट](https://anyone-can-code.vercel.app/) · [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) · [प्राइवेसी](../docs/PRIVACY.md) · [नियम](../docs/TERMS.md) · [योगदान](../.github/CONTRIBUTING.md)
