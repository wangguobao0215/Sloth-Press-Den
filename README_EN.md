<p align="center">
  <img src="assets/sloth-avatar-round.png" width="120" />
</p>

<h1 align="center">Sloth-Press-Den — 深印 · 写书工坊</h1>

<p align="center">
  Complete pipeline from planning to print-ready PDF — Writing Engine × Typesetting Engine × Proofreading Engine.
</p>

<p align="center">
  <img src="assets/qrcode.jpg" width="140" /><br/>
  Follow <strong>树懒老K</strong> on WeChat · <em>Slow down, go deeper.</em>
</p>

---

## Brand Story

**Sloth-Press-Den** — "Press" stands for publishing & printing, "Den" is a workshop. A sloth writes books: no rushing, just depth — every book is a craftsman's book.

## Features

- **5-Stage Writing Engine**: Plan → Research → Write → Review → Build (based on lovstudio workflow)
- **Publishing-Grade Typesetting**: A5 book layout, 5 professional presets including Misty Blue, CJK best practices
- **Cover & Back Cover System**: Circular avatar + gradient background + WeChat QR code
- **Multi-Format Output**: PDF (Chrome native @page pagination), HTML, ePub, MOBI, AZW3
- **Knowledge Attachments**: Auto-generated table/figure numbering, cross-references, PDF bookmarks, chapter epigraphs
- **Auto-Proofreading**: Terminology consistency, citation standards, layout rule checks

## Quick Start

### Prerequisites

```bash
pip install markdown pygments pyyaml playwright qrcode Pillow
playwright install chromium
# Optional (for PDF bookmark injection):
pip install PyMuPDF
```

### Usage

After installing this skill in QoderWork, simply start a conversation:

- "Help me write a book" → Launch the 5-stage writing workflow
- "Typeset this manuscript into PDF" → Launch the typesetting engine
- "Proofread my manuscript" → Run auto-proofreading

## Version

Current version: **3.4.0**

See [CHANGELOG.md](CHANGELOG.md)

## License

[MIT License](LICENSE)
