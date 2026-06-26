#!/usr/bin/env python3
"""Generate book cover PNGs from HTML template for website/about page.

Usage:
  python scripts/gen-website-covers.py

Reads BOOKS list, generates 600x800 cover PNGs to output_dir.
Edit the BOOKS list below to customize.
"""

import pathlib
from playwright.sync_api import sync_playwright

# ── EDIT YOUR BOOKS HERE ──────────────────────────────────
BOOKS = [
    {
        "id": "token-ledger",
        "series": "企业AI转型书系",
        "title": "Token账本",
        "subtitle": "AI转型，文化是最后的ROI",
        "accent": "#2C4A6E",
        "accent2": "#5B9BC8",
    },
    {
        "id": "medicine-wholesale-ai",
        "series": "行业AI转型实战书系",
        "title": "医药批发企业AI转型实战",
        "subtitle": "从传统批发到智慧供应链",
        "accent": "#3A6B5C",
        "accent2": "#5DA88A",
    },
    {
        "id": "ai-leader-path",
        "series": "企业AI转型书系",
        "title": "AI领导者之路",
        "subtitle": "从执行到决策",
        "accent": "#4A3F6B",
        "accent2": "#7B6DA8",
    },
    {
        "id": "knowledge-flywheel",
        "series": "企业AI转型书系",
        "title": "知识飞轮",
        "subtitle": "AI时代的企业知识管理新范式",
        "accent": "#6B5A3A",
        "accent2": "#A8905D",
    },
    {
        "id": "skill-engineering",
        "series": "实战技能书系",
        "title": "Skill工程实战",
        "subtitle": "从想法到第一个AI助手",
        "accent": "#5A3A6B",
        "accent2": "#8D6DA8",
    },
    {
        "id": "executive-agent",
        "series": "企业AI转型书系",
        "title": "AI智能体",
        "subtitle": "高管的第一本决策书",
        "accent": "#3A506B",
        "accent2": "#5B8DB8",
    },
]
# ── END CONFIG ──────────────────────────────────────────

OUTPUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "assets" / "website-covers"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def make_html(b):
    a1, a2 = b["accent"], b["accent2"]
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  width:600px; height:800px; overflow:hidden;
  font-family:"PingFang SC","Noto Sans SC",-apple-system,sans-serif;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  background:#FAF7F0; position:relative;
}}
.top-line {{ position:absolute; top:0; left:0; right:0; height:6px;
  background:linear-gradient(90deg,{a1} 0%,{a2} 50%,{a1} 100%); }}
.bottom-bar {{ position:absolute; bottom:0; left:0; right:0; height:60px; background:{a1}; }}
.bottom-bar-text {{ position:absolute; bottom:18px; left:0; right:0; text-align:center;
  color:#B4CDE1; font-size:11px; letter-spacing:3px; }}
.content {{ padding:60px; text-align:center; flex:1;
  display:flex; flex-direction:column; align-items:center; justify-content:center; }}
.series-text {{ font-size:13px; color:#8A7F6E; letter-spacing:4px; margin-bottom:30px; font-weight:400; }}
.title {{ font-size:32px; font-weight:700; color:#1a2a3a; line-height:1.3; letter-spacing:4px; margin-bottom:12px; }}
.subtitle {{ font-size:16px; color:#5A6B7C; font-weight:400; letter-spacing:3px; margin-bottom:40px; }}
.divider {{ width:50px; height:2px; background:{a2}; margin-bottom:36px; }}
.author {{ font-size:14px; color:#6B7C8D; letter-spacing:3px; font-weight:500; }}
.tagline {{ font-size:11px; color:#A0A8B0; letter-spacing:2px; margin-top:18px; font-weight:300; }}
</style></head>
<body>
<div class="top-line"></div>
<div class="content">
  <div class="series-text">{b["series"]}</div>
  <div class="title">{b["title"]}</div>
  <div class="subtitle">{b["subtitle"]}</div>
  <div class="divider"></div>
  <div class="author">树懒老K（拙一）</div>
  <div class="tagline">慢一点，深一度</div>
</div>
<div class="bottom-bar"><div class="bottom-bar-text">扫一扫 · 获取更多AI转型方法论</div></div>
</body></html>"""


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 600, "height": 800})
        for book in BOOKS:
            page = ctx.new_page()
            page.set_content(make_html(book))
            page.wait_for_timeout(500)
            out = OUTPUT_DIR / f"{book['id']}.png"
            page.screenshot(path=str(out), full_page=False)
            page.close()
            kb = out.stat().st_size // 1024
            print(f"  {book['id']:30s} {kb}KB")
        ctx.close()
        browser.close()
    print(f"\nDone! {len(BOOKS)} covers -> {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
