<p align="center">
  <img src="../plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>साधारण भाषा → प्लान → बिल्ड → जाँच।</strong><br/>
  इंजीनियर न होने वालों के लिए मुफ़्त Codex प्लगिन।<br/>
  बताएँ आप क्या चाहते हैं। ACC प्लान, बिल्ड और असली जाँच में मदद करता है।
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
  <a href="https://anyone-can-code.vercel.app/#install"><strong>मुफ़्त इंस्टॉल</strong></a>
  ·
  <a href="../docs/FIRST_DAY.md">पहला दिन</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">समस्या बताएँ</a>
</p>

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

---

## यह क्या है

**Anyone Can Code (ACC)** [OpenAI Codex](https://openai.com/codex/) के लिए मुफ़्त ओपन-सोर्स प्लगिन है।  
नया एजेंट नहीं। IDE नहीं। **कोड Codex लिखता है।** ACC काम को साफ़ रास्ता देता है।

| कदम | आपको क्या मिलता है |
|-----|---------------------|
| **प्लान** | बड़े बदलाव से पहले साफ़ रास्ता |
| **बिल्ड** | प्रोजेक्ट में कदम-दर-कदम काम |
| **जाँच** | असली “हो गया?” — सिर्फ़ “ठीक लगता है” नहीं |
| **याद** | **Desktop:** hooks भरोसे के बाद ऑटो मेमोरी। **CLI:** अभी नहीं — `$learn` / `$wiki` |

**एक प्लगिन** Desktop और CLI दोनों के लिए — एक ही नाम: **Anyone Can Code**।

ओपन बीटा · Desktop **v2.0.0-beta.4** (ऑटो मेमोरी) · CLI मेमोरी अभी मैन्युअल।

**ज़रूरी:** [Codex](https://openai.com/codex/) (Desktop और/या CLI) · Python 3

मैं **Mitun** हूँ। ACC से शिप किया एक प्रॉडक्ट: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2)।

---

## इंस्टॉल — Desktop

<p align="center">
  <img src="../docs/media/install-setup.gif" alt="Codex Desktop में Anyone Can Code इंस्टॉल" width="560"/>
</p>

1. कॉपी करें: `https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → पेस्ट
3. **Anyone Can Code** इंस्टॉल करें
4. **Hooks** → चालू करें + ACC के **सभी hooks पर भरोसा** (ज़रूरी)
5. रीस्टार्ट → प्रोजेक्ट फ़ोल्डर खोलें → `$setup` → बताएँ क्या चाहिए

वीडियो: [वेबसाइट](https://anyone-can-code.vercel.app/#install) · [mp4](../docs/media/install-setup.mp4)

---

## इंस्टॉल — CLI

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

1. प्रोजेक्ट फ़ोल्डर में: `codex`
2. `/plugins` → **Anyone Can Code** इंस्टॉल (Desktop जैसा ही)
3. `/hooks` → ACC के **सभी hooks पर भरोसा**
4. नया थ्रेड → `$setup` → बताएँ क्या चाहिए

---

## मेमोरी

| आप उपयोग करते हैं | ऑटो मेमोरी? |
|-------------------|-------------|
| **Codex Desktop** | **हाँ** — ACC hooks पर भरोसा के बाद |
| **Codex CLI** | **अभी नहीं** — `$learn` / `$wiki` / `$capture` से सेव करें |

Desktop पर ACC लक्ष्य, फ़ैसले और अधूरा काम आपके मशीन पर रख सकता है (`.codex/anyone-can-code/`)। ACC सर्वर पर कुछ नहीं जाता।

**टिप:** हर प्लगिन अपडेट के बाद hooks फिर भरोसे से जोड़ें, फिर रीस्टार्ट करें।

---

## रोज़ का उपयोग

साधारण भाषा में भी बात कर सकते हैं।

| टाइप करें | कब |
|-----------|-----|
| `$setup` | प्रोजेक्ट में पहली बार |
| `$status` / `$help` | मैं कहाँ हूँ? आगे क्या? |
| `$resume` | ब्रेक के बाद जारी |
| `$verify` | सच में हो गया? |
| `$fix` | वही गलती बार-बार |

उदाहरण: *“एक सरल खर्च ट्रैकर बनाओ और हर कदम साधारण भाषा में समझाओ।”*

पूरा पहला सेशन: **[docs/FIRST_DAY.md](../docs/FIRST_DAY.md)**

---

## अगर कुछ फेल हो

| समस्या | ठीक कैसे |
|--------|----------|
| Marketplace नहीं जुड़ता | ऊपर वाला **पूरा** GitHub URL इस्तेमाल करें |
| इंस्टॉल के बाद कुछ नहीं | **सभी** ACC hooks भरोसे से जोड़ें, रीस्टार्ट, नया चैट |
| Desktop भूल जाता है | hooks भरोसे में नहीं (या अपडेट के बाद फिर नहीं) |
| CLI पर ऑटो मेमोरी उम्मीद | अभी नहीं — `$learn` / `$wiki`, या Desktop |
| पुराना “केवल CLI” पैकेज | **Anyone Can Code CLI** हटाएँ; **Anyone Can Code** एक बार लगाएँ |
| `$setup` चुप | पहले **प्रोजेक्ट फ़ोल्डर** खोलें |

अभी भी अटके? [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discord](https://discord.gg/qgS29y7TqP) · [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)

---

## लिंक

[वेबसाइट](https://anyone-can-code.vercel.app/) · [रोडमैप](../ROADMAP.md) · [पहला दिन](../docs/FIRST_DAY.md) · [प्राइवेसी](../docs/PRIVACY.md) · [नियम](../docs/TERMS.md) · [योगदान](../.github/CONTRIBUTING.md)

MIT · Built by [Mitun](https://github.com/mitunmanav)
