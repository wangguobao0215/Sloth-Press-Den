#!/usr/bin/env python3
"""
Press-Typeset v3.0 — Sloth-Press-Den 排版引擎
将 Markdown 书稿通过 Paged.js + Playwright 渲染为出版级 PDF。

架构：
  Markdown → [YAML主题] → HTML → [Paged.js分页] → Playwright → PDF

用法：
  python press-typeset.py --input manuscript.md --preset tech-modern --output book.pdf
"""

import os, re, sys, yaml
from pathlib import Path
from datetime import date
from xml.sax.saxutils import escape
import markdown
import qrcode

# ─── Paths ───────────────────────────────────────────────────────────────
SKILL_DIR = Path(__file__).parent.parent
PRESETS_DIR = SKILL_DIR / "presets"
ASSETS_DIR = SKILL_DIR / "assets"


# ─── Theme Loading ───────────────────────────────────────────────────────
def detect_fonts():
    """Detect platform fonts with professional CJK fallback chains."""
    import platform
    plat = platform.system()
    
    if plat == "Darwin":
        return {
            "heading": "'PingFang SC', 'Hiragino Sans GB', 'STZhongsong', 'SimHei', sans-serif",
            "body": "'Songti SC', 'STSong', 'SimSun', serif",
            "cjk": "'Songti SC', 'STSong', 'SimSun', serif",
            "cjk_bold": "'PingFang SC', 'STHeiti', 'SimHei', sans-serif",
            "kai": "'Kaiti SC', 'STKaiti', 'KaiTi', serif",
            "mono": "'Menlo', 'Monaco', 'Courier New', monospace",
            "latin": "'Georgia', 'Times New Roman', serif",
        }
    elif plat == "Windows":
        return {
            "heading": "'Microsoft YaHei', 'PingFang SC', 'SimHei', sans-serif",
            "body": "'SimSun', 'STSong', 'Songti SC', serif",
            "cjk": "'SimSun', 'STSong', 'Songti SC', serif",
            "cjk_bold": "'Microsoft YaHei', 'SimHei', 'PingFang SC', sans-serif",
            "kai": "'KaiTi', 'STKaiti', 'Kaiti SC', serif",
            "mono": "'Consolas', 'Courier New', monospace",
            "latin": "'Georgia', 'Times New Roman', serif",
        }
    else:
        return {
            "heading": "'Noto Sans CJK SC', 'WenQuanYi Micro Hei', sans-serif",
            "body": "'Noto Serif CJK SC', 'WenQuanYi Micro Hei', serif",
            "cjk": "'Noto Serif CJK SC', serif",
            "cjk_bold": "'Noto Sans CJK SC', sans-serif",
            "kai": "'AR PL UKai', serif",
            "mono": "'DejaVu Sans Mono', monospace",
            "latin": "'Liberation Serif', 'Georgia', serif",
        }


def load_preset(name):
    """Load a theme preset from YAML file."""
    preset_path = PRESETS_DIR / f"{name}.yaml"
    if not preset_path.exists():
        available = [f.stem for f in PRESETS_DIR.glob("*.yaml")]
        print(f"Error: Preset '{name}' not found.")
        print(f"Available: {available}")
        sys.exit(1)
    with open(preset_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ─── Markdown Parsing ────────────────────────────────────────────────────
def extract_frontmatter(md_text):
    """Extract YAML frontmatter from markdown."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', md_text, re.DOTALL)
    if match:
        try:
            fm = yaml.safe_load(match.group(1)) or {}
            body = md_text[match.end():]
            return fm, body
        except yaml.YAMLError:
            return {}, md_text
    return {}, md_text


def parse_markdown_structure(md_text):
    """Parse markdown into chapters with epigraph and sub-chapter support.
    
    Handles:
    - Code blocks: skips '#' inside ``` fences
    - Foreword/preface: treated as chapter 0
    - Standard '# 第X章' headings as chapter boundaries
    - Epigraph detection: > "quote" -- source
    """
    lines = md_text.split('\n')
    chapters = []
    current_chapter = None
    current_content = []
    in_code_block = False

    # All known book section prefixes (for startswith matching)
    KNOWN_SECTIONS = (
        '前言', '序言', '绪论', '导论', '引言', '自序', '序', '写在前面',
        '尾声', '后记', '跋',
        '献辞', '题辞', '献词',
        '凡例', '阅读指南', '使用说明',
        '参考文献', '参考书目',
        '附录', '附',
    )

    for line in lines:
        # Track code blocks (``` fences)
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            current_content.append(line)
            continue
        
        # Only process headings outside code blocks
        if not in_code_block and line.startswith('# '):
            title = line[2:].strip()
            
            # Determine if this is a chapter/section boundary
            is_chapter = bool(re.match(r'^第[\d一二三四五六七八九十百]+章', title))
            is_section = any(title == s or title.startswith(s + ' ') or title.startswith(s + '\u3000') for s in KNOWN_SECTIONS)
            # 附录A/B/C...（附录后直接跟编号字母/数字/中文数字）也应识别为章节边界
            if not is_section and re.match(r'^附录[ABCDEF\d一二三四五六七八九十]', title):
                is_section = True
            
            if is_chapter or is_section:
                # Save previous chapter if any
                if current_chapter is not None:
                    current_chapter['content'] = '\n'.join(current_content)
                    current_chapter['sub_chapters'] = _extract_sub_chapters(current_content, len(chapters))
                    chapters.append(current_chapter)
                
                # Start new chapter
                current_chapter = {
                    'title': title,
                    'content': '',
                    'epigraph': None,
                    'sub_chapters': [],
                }
                current_content = []
            else:
                # Not a recognized chapter/section heading — treat as content
                current_content.append(line)
            continue  # Always continue after H1 processing
        
        # Non-H1 lines: epigraph detection and content accumulation
        if not in_code_block and current_chapter is not None and current_chapter['epigraph'] is None:
            stripped = line.lstrip('>').strip()
            if line.startswith('> ') and ('--' in stripped or '\u2014' in stripped):
                parts = re.split(r'\s*[-\u2013\u2014]{2,}\s*', stripped, maxsplit=1)
                if len(parts) == 2:
                    current_chapter['epigraph'] = {
                        'text': parts[0].strip().strip('"').strip("'").strip(),
                        'source': parts[1].strip()
                    }
                    continue
        current_content.append(line)

    # Don't forget the last chapter
    if current_chapter is not None:
        current_chapter['content'] = '\n'.join(current_content)
        current_chapter['sub_chapters'] = _extract_sub_chapters(current_content, len(chapters))
        chapters.append(current_chapter)

    return chapters


def _extract_sub_chapters(content_lines, chapter_index=0):
    """Extract H2 headings from chapter content as sub-chapters with anchor IDs."""
    subs = []
    counter = 0
    for line in content_lines:
        if line.startswith('## '):
            counter += 1
            title = line[3:].strip()
            anchor = f'sub-ch{chapter_index}-{counter}'
            subs.append({'title': title, 'anchor': anchor})
    return subs


def convert_md_to_html(md_text):
    """Convert markdown text to HTML with extensions."""
    md = markdown.Markdown(extensions=[
        'tables',
        'fenced_code',
        'toc',
        'smarty',
        'footnotes',
        'codehilite',
    ])
    return md.convert(md_text)


def process_body_html(html, chapter_index=0, output_dir=None):
    """Post-process HTML: figure/table numbering, sidebars, footnotes, cross-references."""
    # ── Cross-reference detection: 参见/参阅/参考/见 第X章 → clickable links
    def replace_crossref(m):
        prefix = m.group(1)  # 参见/参阅/参考/见
        ch_num = m.group(2)  # X (digit or Chinese)
        # Map Chinese numbers to digits
        cn_map = {'一':'1','二':'2','三':'3','四':'4','五':'5',
                  '六':'6','七':'7','八':'8','九':'9','十':'10'}
        num = cn_map.get(ch_num, ch_num)
        return f'{prefix}<a href="#ch-{int(num)-1}" class="cross-ref">第{ch_num}章</a>'
    
    html = re.sub(
        r'(参见|参阅|参考|见)\s*第([一二三四五六七八九十\d]+)章',
        replace_crossref, html
    )
    
    # ── Figure numbering ──
    fig_counter = 0
    def replace_img_figure(m):
        nonlocal fig_counter
        fig_counter += 1
        tag = m.group(0)
        img_match = re.search(r'<img[^>]+/>|<img[^>]+>', tag)
        if not img_match:
            return tag
        img_tag = img_match.group(0)
        src_match = re.search(r'src="([^"]+)"', img_tag)
        src = src_match.group(1) if src_match else ''
        alt_match = re.search(r'alt="([^"]*)"', img_tag)
        alt = alt_match.group(1) if alt_match else ''
        # Extract italic caption if present (from markdown *caption*)
        cap_match = re.search(r'<em>([^<]*)</em>', tag)
        caption = cap_match.group(1).strip().strip('—').strip('-').strip() if cap_match else ''
        cap_text = caption if caption else alt
        return (
            f'<figure><img src="{src}" alt="{alt}" style="max-height:140mm;width:auto;height:auto;"/>'
            f'<figcaption>\u56fe {chapter_index + 1}-{fig_counter}  {cap_text}</figcaption></figure>'
        )
    # Match <p> containing <img> (possibly followed by <em> caption)
    html = re.sub(r'<p>\s*(<img[^>]+/>)\s*(?:<em>([^<]*)</em>)?\s*</p>', replace_img_figure, html)

    # ── Table numbering ──
    table_counter = 0
    def replace_table(m):
        nonlocal table_counter
        table_counter += 1
        table_html = m.group(0)
        return (
            f'<div class="table-wrapper">'
            f'<div class="table-caption">\u8868 {chapter_index + 1}-{table_counter}</div>'
            f'{table_html}</div>'
        )
    html = re.sub(r'<table>.*?</table>', replace_table, html, flags=re.DOTALL)

    # ── Sidebar / callout detection (BookSmith pattern) ──
    # Also inject QR code if sidebar contains 配套资源/二维码/扫码
    qr_html = ''
    if output_dir:
        try:
            qr_src = _ensure_asset(output_dir, "qrcode.jpg")
            qr_html = f'<div class="sidebar-qr"><img src="{qr_src}" width="70" height="70" class="sidebar-qr-img" alt="公众号二维码"/><p class="sidebar-qr-text">扫码获取配套资源</p></div>'
        except Exception:
            qr_html = ''
    
    def replace_blockquote(m):
        inner = m.group(1)
        match = re.search(r'<p><strong>([^<]+)</strong>[:：]?\s*(.*?)</p>', inner)
        if match:
            label = match.group(1)
            rest = match.group(2)
            new_inner = inner.replace(
                match.group(0),
                f'<p class="sidebar-title">{label}</p><p>{rest}</p>',
                1
            )
            # Inject QR code for resource sections, strip placeholder text
            if '配套资源' in label or '二维码' in label or '扫码' in label:
                cleaned = re.sub(r'<p>（此处放置[^<]*）</p>\s*', '', new_inner)
                cleaned = re.sub(r'<p>扫码获取[^<]*</p>\s*', '', cleaned)
                return f'<aside class="sidebar">{cleaned}{qr_html}</aside>'
            return f'<aside class="sidebar">{new_inner}</aside>'
        # Fallback: standalone blockquote with QR placeholder text
        if '此处放置' in inner:
            cleaned = re.sub(r'<p>（此处放置[^<]*）</p>\s*', '', inner)
            cleaned = re.sub(r'<p>扫码获取[^<]*</p>\s*', '', cleaned)
            return f'<aside class="sidebar">{cleaned}{qr_html}</aside>'
        return m.group(0)
    
    html = re.sub(r'<blockquote>(.*?)</blockquote>', replace_blockquote, html, flags=re.DOTALL)

    return html


# ─── HTML Generators ─────────────────────────────────────────────────────
def generate_cover_html(config, output_dir="."):
    """Generate cover page HTML with brand logo (centered) + title + subtitle + three QR codes at bottom.
    
    Styles: gradient (default), solid, academic
    Three QR codes (website / WeChat / 公众号) sit at the bottom of the cover.
    """
    colors = config['colors']
    fonts = config['fonts']
    sizes = config['sizes']
    
    title = escape(config.get('title', '无标题'))
    subtitle = escape(config.get('subtitle', ''))
    author = escape(config.get('author', ''))
    cover_style = config.get('cover_style', 'gradient')
    
    subtitle_html = f'<p class="cover-subtitle">{subtitle}</p>' if subtitle else ''
    slogan = escape(config.get('slogan', ''))
    slogan_html = f'<p class="cover-slogan">{slogan}</p>' if slogan else ''
    author_html = f'<p class="cover-author">{author}</p>' if author else ''
    
    # Brand logo (transparent) — centered
    logo_src = _ensure_asset(output_dir, "logo-transparent.png")
    logo_html = f'<img src="{logo_src}" width="100" height="100" class="cover-avatar"/>'

    # Three QR codes at the bottom
    qr_website = _ensure_asset(output_dir, "website_qr.png")
    qr_wechat = _ensure_asset(output_dir, "wechat_qr.png")
    qr_gzh = _ensure_asset(output_dir, "gongzhonghao_qr.png")
    
    qr_row = f'''<div class="cover-qr-row">
      <div class="cover-qr-item">
        <img src="{qr_website}" width="60" height="60" class="cover-qr-img"/>
        <p class="cover-qr-label">个人网站</p>
      </div>
      <div class="cover-qr-item">
        <img src="{qr_wechat}" width="60" height="60" class="cover-qr-img"/>
        <p class="cover-qr-label">个人微信</p>
      </div>
      <div class="cover-qr-item">
        <img src="{qr_gzh}" width="60" height="60" class="cover-qr-img"/>
        <p class="cover-qr-label">公众号</p>
      </div>
    </div>'''

    if cover_style == 'solid':
        bg = f'background: {colors["cover_gradient_end"]};'
        return f'''<section class="cover-page">
  <div class="cover-bg" style="{bg}"></div>
  <div class="cover-content">
    {logo_html}
    <h1 class="cover-title">{title}</h1>
    {subtitle_html}
    {slogan_html}
    <div class="cover-ornament"></div>
    {author_html}
  </div>
  {qr_row}
</section>'''

    elif cover_style == 'academic':
        bg = f'background: {colors["cover_gradient_end"]};'
        return f'''<section class="cover-page">
  <div class="cover-bg" style="{bg}"></div>
  <div style="width: 60px; height: 3px; background: {colors['cover_accent']}; margin: 0 auto 2em;"></div>
  <h1 class="cover-title" style="font-size: {sizes['cover_title'] - 4}pt;">{title}</h1>
  {subtitle_html}
  {slogan_html}
  {logo_html}
  <div style="width: 40px; height: 1px; background: {colors['cover_accent']}; opacity: 0.4; margin: 2em auto;"></div>
  {author_html}
  {qr_row}
</section>'''

    else:
        # gradient (default) — logo centered, three QR codes at bottom
        og = f"background: linear-gradient(135deg, {colors['cover_gradient_start']} 0%, {colors['cover_gradient_end']} 100%);"
        return f'''<section class="cover-page">
  <div class="cover-bg" style="{og}"></div>
  <div class="cover-content">
    {logo_html}
    <h1 class="cover-title">{title}</h1>
    {subtitle_html}
    {slogan_html}
    <div class="cover-ornament"></div>
    {author_html}
  </div>
  {qr_row}
</section>'''


def generate_copyright_html(config):
    """Generate copyright page."""
    title = escape(config.get('title', '无标题'))
    author = escape(config.get('author', ''))
    publisher = config.get('publisher', '树懒老K')
    year = config.get('year', date.today().year)
    isbn = config.get('isbn', '')
    
    isbn_line = f'<p>ISBN: {isbn}</p>' if isbn else ''

    return f'''<section class="copyright-page">
  <div class="copyright-content">
    <p class="copyright-title">{title}</p>
    <p class="copyright-author">{author}</p>
    <div class="copyright-divider"></div>
    <div class="copyright-details">
      <p>作者：{author}</p>
      <p>出版：{publisher}</p>
      <p>年份：{year}</p>
      {isbn_line}
    </div>
    <p class="copyright-notice">版权所有 · 未经许可不得转载</p>
  </div>
</section>'''


def generate_qr_html(output_dir):
    """Copy existing QR code image from Sloth assets, return HTML img tag."""
    qr_src = _ensure_asset(output_dir, "qrcode.jpg")
    return f'<img src="{qr_src}" width="80" height="80" alt="公众号二维码"/>'


def _ensure_asset(output_dir, filename):
    """Copy an asset file to output directory and return its absolute file:// path.
    
    Searches: Sloth-MGO-Eido > BookSmith-Den > skill assets > generated fallback.
    """
    import shutil
    os.makedirs(output_dir, exist_ok=True)
    dst = os.path.join(output_dir, filename)
    
    # Search order
    search_paths = [
        os.path.expanduser(f"~/Desktop/Sloth-MGO-Eido/assets/{filename}"),
        os.path.expanduser(f"~/Desktop/Sloth-BookSmith-Den/assets/{filename}"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', filename),
    ]
    
    copied = False
    for src in search_paths:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            copied = True
            break
    
    if not copied and filename == "qrcode.jpg":
        # Fallback: generate QR code
        import qrcode
        qr = qrcode.QRCode(border=2, box_size=8)
        qr.add_data("https://mp.weixin.qq.com/s?__biz=MzkxNjMwODc3MA==")
        qr.make(fit=True)
        img = qr.make_image(fill_color="#2C3E50", back_color="#FAF7F0")
        img.save(dst, format="PNG")
    
    return f"file://{os.path.abspath(dst)}"


def generate_back_cover_html(config, output_dir):
    """Generate back cover with brand logo + three QR codes (website / WeChat / 公众号)."""
    colors = config['colors']
    fonts = config['fonts']
    
    logo_src = _ensure_asset(output_dir, "logo-transparent-large.png")
    qr_website = _ensure_asset(output_dir, "website_qr.png")
    qr_wechat = _ensure_asset(output_dir, "wechat_qr.png")
    qr_gzh = _ensure_asset(output_dir, "gongzhonghao_qr.png")
    
    return f'''<section class="back-cover">
  <div class="back-cover-gradient" style="background: linear-gradient(135deg, {colors['cover_gradient_start']} 0%, {colors['cover_gradient_end']} 100%);"></div>
  <div class="back-cover-content">
    <img src="{logo_src}" width="100" height="100" class="back-avatar"/>
    <p class="back-name">树懒老K（拙一）</p>
    <p class="back-desc">30年企业服务经验 · 专注AI智能体与组织变革</p>
    <div class="back-qr-grid">
      <div class="back-qr-item">
        <img src="{qr_website}" width="90" height="90" class="back-qrcode"/>
        <p class="back-qr-label">个人网站</p>
      </div>
      <div class="back-qr-item">
        <img src="{qr_wechat}" width="90" height="90" class="back-qrcode"/>
        <p class="back-qr-label">个人微信</p>
      </div>
      <div class="back-qr-item">
        <img src="{qr_gzh}" width="90" height="90" class="back-qrcode"/>
        <p class="back-qr-label">公众号</p>
      </div>
    </div>
    <p class="back-tagline">慢一点，深一度</p>
  </div>
</section>'''


def generate_toc_html(chapters, config):
    """Generate table of contents.
    
    Separates prefaces from numbered chapters to avoid "第2章 第1章" confusion.
    """
    colors = config['colors']
    fonts = config['fonts']
    
    preface_titles = ('前言', '序言', '绪论', '导论', '引言', '自序', '序', '写在前面', '尾声', '后记', '献辞', '题辞', '凡例', '阅读指南', '参考文献')
    
    items = []
    chapter_items = []
    
    for i, ch in enumerate(chapters):
        title = ch['title']
        is_preface = title in preface_titles
        
        if is_preface:
            items.append(f'<li class="toc-item toc-preface"><a href="#ch-body-{i}">{title}</a></li>')
        else:
            chapter_items.append(f'<li class="toc-item"><a href="#ch-body-{i}">{title}</a></li>')
            for sub in ch.get('sub_chapters', []):
                chapter_items.append(f'<li class="toc-item toc-sub"><a href="#{sub["anchor"]}">{sub["title"]}</a></li>')
    
    all_items = items + chapter_items

    return f'''<section class="toc-page">
  <h2 class="toc-heading">目 录</h2>
  <div class="toc-divider"></div>
  <ul class="toc-list">
    {''.join(all_items)}
  </ul>
</section>'''


def generate_chapter_opener(chapter, index, config):
    """Generate chapter opener (扉页) — no chapter number to avoid confusion with TOC."""
    colors = config['colors']
    fonts = config['fonts']
    
    epigraph_html = ''
    if chapter.get('epigraph'):
        e = chapter['epigraph']
        epigraph_html = f'''<div class="chapter-epigraph">
          <blockquote>{escape(e['text'])}</blockquote>
          <p class="epigraph-source">—— {escape(e['source'])}</p>
        </div>'''

    return f'''<div class="chapter-opener">
    <h1 class="opener-title">{escape(chapter['title'])}</h1>
    <div class="opener-divider"></div>
    {epigraph_html}
  </div>'''


def _cn_num(n):
    """Convert integer to Chinese number (1-20)."""
    nums = ['零','一','二','三','四','五','六','七','八','九','十',
            '十一','十二','十三','十四','十五','十六','十七','十八','十九','二十']
    return nums[n] if 1 <= n <= 20 else str(n)


def generate_body_html(chapters, config, output_dir="."):
    """Generate full body HTML with chapters."""
    parts = []
    for i, chapter in enumerate(chapters):
        parts.append(f'<section class="chapter" id="ch-{i}">')
        parts.append(generate_chapter_opener(chapter, i, config))

        # Inject invisible markers before H2 headings for page lookup
        content_lines = chapter['content'].split('\n')
        marked_lines = []
        sub_counter = 0
        for line in content_lines:
            if line.startswith('## '):
                sub_counter += 1
                marker = f'<span style="font-size:0.5pt;">§TOC{i}-{sub_counter}§</span>'
                marked_lines.append(marker)
            marked_lines.append(line)

        chapter_html = convert_md_to_html('\n'.join(marked_lines))
        chapter_html = process_body_html(chapter_html, chapter_index=i, output_dir=output_dir)

        clean = re.sub(r'<div class="page-break"></div>', '', chapter_html)
        clean = re.sub(r'\s', '', clean)
        if clean:
            parts.append(f'<div class="chapter-body" id="ch-body-{i}">{chapter_html}</div>')
        parts.append('</section>')

    body = '\n'.join(parts)
    
    # Watermark
    watermark = config.get('watermark', '')
    if watermark:
        body += f'\n<div class="watermark">{watermark}</div>'
    
    return body

# ─── 
# ─── CSS Generator ───────────────────────────────────────────────────────
def generate_css(config):
    """Generate complete CSS with professional book typography."""
    colors = config['colors']
    fonts = config['fonts']
    sizes = config['sizes']
    margins = config['page_margins']
    lh = config['line_height']
    indent = config['first_line_indent']
    para_sp = config['paragraph_spacing']
    # Dynamic line-height based on body size
    body_size = sizes['body']
    if body_size <= 10:
        computed_lh = 1.8
    elif body_size <= 11:
        computed_lh = 1.75
    else:
        computed_lh = 1.65

    top_m = margins.get('top', 25)
    bottom_m = margins.get('bottom', 25)
    inner_m = margins.get('inner', 20)
    outer_m = margins.get('outer', 18)
    page_size = config.get('page_size', 'A5')
    
    # Static page header (book title) — Chrome native @page doesn't support running elements
    book_title = config.get('title', '')
    header_text = book_title[:40] if book_title else ''

    drop_cap_css = ''
    if config.get('drop_cap', False):
        drop_cap_css = f'''
.chapter-body:first-child p:first-child:first-letter {{
  float: left;
  font-size: 3.2em;
  line-height: 0.85;
  font-weight: 700;
  margin-right: 0.15em;
  color: {colors['accent']};
  font-family: {fonts['heading']};
}}'''

    return f'''/* ═══════════════════════════════════════════════════════════════════════
   Sloth-Press-Den v3.0 -- Professional Book Typography
   ═══════════════════════════════════════════════════════════════════════ */

/* ─── Page Setup ─── */
@page {{
    size: {page_size};
    margin-top: {top_m}mm;
    margin-bottom: {bottom_m}mm;
    margin-left: {inner_m}mm;
    margin-right: {outer_m}mm;
    @top-center {{
        content: "{header_text}";
        font-family: {fonts['cjk']};
        font-size: 8.5pt;
        color: {colors['text_faded']};
        border-bottom: 0.5pt solid {colors['border']};
        padding-bottom: 0.5mm;
        vertical-align: bottom;
    }}
    @bottom-center {{
        content: counter(page);
        font-family: {fonts['cjk']};
        font-size: 9pt;
        color: {colors['text_faded']};
    }}
}}

/* ─── Page Setup ─── */
/* Named pages cause blank transitional pages in Chrome 130+ when transitioning
   between DIFFERENT named pages. Solution: cover, copyright, and back cover
   all use @page cover (SAME named page) to avoid transitions.
   All other pages use the default @page (no named page). */
@page cover {{ margin: 0; @top-center {{ content: none; }} @bottom-center {{ content: none; }} }}

/* ─── Base ─── */
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

html {{
    font-family: {fonts['body']};
    font-size: {body_size}pt;
    line-height: {computed_lh};
    color: {colors['text']};
    text-align: left;
    word-break: break-word;
    orphans: 3;
    widows: 3;
}}

body {{
    font-size: {body_size}pt;
    line-height: {computed_lh};
}}

/* ─── Cover Page ─── */
.cover-page {{
    page: cover;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    min-height: 100vh;
    color: {colors['cover_text']};
}}

.cover-bg {{
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: 0;
}}

.cover-corner {{
    position: absolute;
    width: 100px;
    height: 100px;
    z-index: 1;
}}

.cover-corner.top-left {{ top: 20px; left: 20px; }}
.cover-corner.bottom-right {{ bottom: 20px; right: 20px; }}

.cover-border {{
    position: absolute;
    top: 30px; left: 30px; right: 30px; bottom: 30px;
    border: 1px solid rgba(255,255,255,0.12);
    padding: 12px;
    z-index: 1;
}}

.cover-border-inner {{
    width: 100%; height: 100%;
    border: 1px solid rgba(255,255,255,0.08);
}}

.cover-content {{
    position: relative;
    z-index: 2;
    max-width: 78%;
}}

.cover-avatar {{
    border-radius: 50%;
    margin-bottom: 1.5em;
}}

.cover-publisher {{
    font-size: 10pt;
    letter-spacing: 0.15em;
    color: {colors['cover_accent']};
    opacity: 0.85;
    margin-bottom: 3em;
}}

.cover-title {{
    font-family: {fonts['heading']};
    font-size: {sizes['cover_title']}pt;
    font-weight: 700;
    letter-spacing: 0.02em;
    line-height: 1.25;
    margin-bottom: 0.6em;
    word-break: keep-all;
    overflow-wrap: break-word;
}}

.cover-subtitle {{
    font-size: 13pt;
    color: {colors['cover_accent']};
    opacity: 0.9;
    font-weight: 400;
    margin-bottom: 1.8em;
    line-height: 1.5;
}}

.cover-slogan {{
    font-size: 11pt;
    color: {colors['cover_accent']};
    opacity: 0.75;
    font-weight: 400;
    letter-spacing: 0.05em;
    margin-bottom: 1.2em;
    font-style: italic;
}}

.cover-ornament {{
    width: 45px;
    height: 2px;
    background: {colors['cover_accent']};
    opacity: 0.6;
    margin: 0 auto;
}}

.cover-author {{
    font-size: 11pt;
    letter-spacing: 0.3em;
    margin-top: 2.5em;
    color: {colors['cover_text']};
    opacity: 0.9;
}}

/* ─── Cover QR Codes (three at bottom) ─── */
.cover-qr-row {{
    position: absolute;
    bottom: 25px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1.5em;
    z-index: 20;
}}

.cover-qr-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}}

.cover-qr-img {{
    display: block;
    border-radius: 4px;
    border: 2px solid rgba(255,255,255,0.15);
}}

.cover-qr-label {{
    font-size: 7pt;
    color: {colors['cover_text']};
    opacity: 0.6;
    letter-spacing: 1px;
    white-space: nowrap;
}}

/* ─── Copyright Page ─── */
.copyright-page {{
    page: cover;
    padding: {top_m}mm {outer_m}mm {bottom_m}mm {inner_m}mm;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
}}

.copyright-content {{ max-width: 65%; }}

.copyright-title {{
    font-family: {fonts['heading']};
    font-size: 15pt;
    font-weight: 700;
    margin-bottom: 0.3em;
}}

.copyright-author {{
    font-size: 10.5pt;
    color: {colors['text_faded']};
    margin-bottom: 1.8em;
}}

.copyright-divider {{
    width: 30px;
    height: 1px;
    background: {colors['border']};
    margin-bottom: 1.2em;
}}

.copyright-details {{
    font-size: 9pt;
    line-height: 1.9;
    color: {colors['text_faded']};
}}

.copyright-notice {{
    font-size: 8pt;
    font-style: italic;
    margin-top: 0.4em;
}}

/* ─── TOC ─── */
.toc-page {{
    break-after: page;
}}

.toc-heading {{
    font-family: {fonts['heading']};
    font-size: 22pt;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.4em;
    letter-spacing: 0.15em;
}}

.toc-divider {{
    width: 28px;
    height: 2px;
    background: {colors['accent']};
    margin: 0 auto 2.5em;
}}

.toc-list {{
    list-style: none;
    max-width: 78%;
    margin: 0 auto;
}}

.toc-item {{
    margin-bottom: 0.6em;
    font-size: 10.5pt;
    line-height: 1.5;
    border-bottom: 1px dotted {colors['border']};
    padding-bottom: 0.2em;
}}

.toc-item a {{
    color: {colors['text']};
    text-decoration: none;
}}

.toc-item a::after {{
    content: "  ·  " target-counter(attr(href), page);
    color: {colors['text_faded']};
    font-size: 9pt;
}}

.toc-sub {{
    padding-left: 1.5em;
    font-size: 9.5pt;
    margin-bottom: 0.3em;
    border-bottom: none;
}}

.toc-preface {{
    font-style: italic;
    font-size: 10pt;
    margin-bottom: 0.8em;
    border-bottom: none;
    color: {colors['text_faded']};
}} 

/* ─── Chapter Opener ─── */
.chapter-opener {{
    break-before: page;
    break-after: page;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4em 0;
    text-align: center;
}}

.opener-number {{
    font-family: {fonts['heading']};
    font-size: 12pt;
    color: {colors['accent']};
    letter-spacing: 0.08em;
    margin-bottom: 1em;
}}

.opener-title {{
    font-family: {fonts['heading']};
    font-size: {sizes['chapter_title']}pt;
    font-weight: 700;
    line-height: 1.3;
    margin-bottom: 0.6em;
}}

.opener-divider {{
    width: 36px;
    height: 2px;
    background: {colors['accent']};
    opacity: 0.5;
    margin-bottom: 1.5em;
}}

.chapter-epigraph {{
    max-width: 65%;
}}

.chapter-epigraph blockquote {{
    font-style: italic;
    font-size: 10pt;
    color: {colors['text_faded']};
    line-height: 1.6;
    border-left: 2px solid {colors['accent']};
    padding-left: 1em;
    margin-bottom: 0.5em;
}}

.epigraph-source {{
    font-size: 9pt;
    color: {colors['text_faded']};
    opacity: 0.8;
}}

/* ─── Chapter Body ─── */
.chapter-body {{
    break-before: page;
}}

.chapter-body h1 {{
    font-family: {fonts['heading']};
    font-size: {sizes['h1']}pt;
    font-weight: 700;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    color: {colors['text']};
    page-break-after: avoid;
    line-height: 1.4;
}}

.chapter-body h2 {{
    font-family: {fonts['heading']};
    font-size: {sizes['h2']}pt;
    font-weight: 700;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
    color: {colors['text']};
    page-break-after: avoid;
    line-height: 1.4;
}}

.chapter-body h3 {{
    font-family: {fonts['heading']};
    font-size: {sizes['h3']}pt;
    font-weight: 700;
    margin-top: 1em;
    margin-bottom: 0.3em;
    color: {colors['text']};
    page-break-after: avoid;
    line-height: 1.4;
}}

.chapter-body p {{
    text-indent: {indent};
    margin-bottom: {para_sp};
    orphans: 3;
    widows: 3;
    font-size: {body_size}pt;
    line-height: {computed_lh};
}}

.chapter-body ul, .chapter-body ol {{
    margin: 0.5em 0 0.5em 1.5em;
    padding: 0;
    font-size: {body_size}pt;
    line-height: {computed_lh};
}}

.chapter-body li {{
    margin-bottom: 0.3em;
    line-height: 1.6;
    font-size: {body_size}pt;
}}

/* ─── Code ─── */
.chapter-body code {{
    font-family: {fonts['mono']};
    font-size: {sizes['code']}pt;
    background: {colors['code_bg']};
    padding: 0.15em 0.4em;
    border-radius: 3px;
    word-break: break-all;
}}

.chapter-body pre {{
    background: {colors['code_bg']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    padding: 1em;
    margin: 0.8em 0;
    overflow-x: auto;
    page-break-inside: avoid;
    font-size: {sizes['code']}pt;
    line-height: 1.5;
    white-space: pre;
}}

.chapter-body pre code {{
    background: none;
    padding: 0;
    font-size: inherit;
    line-height: inherit;
    white-space: pre;
    word-break: keep-all;
}}

/* ─── Tables ─── */
.table-wrapper {{
    margin: 1em 0;
    page-break-inside: avoid;
}}

.table-caption {{
    font-size: 9pt;
    color: {colors['text_faded']};
    margin-bottom: 0.3em;
}}

.chapter-body table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 9.5pt;
}}

.chapter-body th {{
    background: {colors['table_header']};
    color: {colors['table_header_text']};
    padding: 0.5em 0.6em;
    text-align: left;
    font-weight: 600;
}}

.chapter-body td {{
    padding: 0.4em 0.6em;
    border-bottom: 1px solid {colors['border']};
}}

.chapter-body tr:nth-child(even) td {{
    background: {colors['table_alt_row']};
}}

/* ─── Blockquotes & Sidebars ─── */
.chapter-body blockquote {{
    border-left: 3px solid {colors['blockquote_border']};
    padding: 0.5em 1em;
    margin: 0.8em 0;
    background: {colors['sidebar_bg']};
    font-style: italic;
    color: {colors['text_faded']};
    font-size: {body_size}pt;
    line-height: {computed_lh};
}}

.chapter-body blockquote p {{
    text-indent: 0;
}}

.chapter-body aside.sidebar {{
    border-left: 3px solid {colors['accent']};
    padding: 0.8em 1em;
    margin: 0.8em 0;
    background: {colors['sidebar_bg']};
    page-break-inside: avoid;
}}

.chapter-body aside.sidebar p {{
    text-indent: 0;
    font-size: 9.5pt;
    line-height: 1.6;
}}

/* ─── Sidebar ─── */
.sidebar-title {{
    font-weight: 700;
    color: {colors['accent']};
    font-size: 10pt;
    margin-bottom: 0.3em;
}}

.sidebar-qr {{
    display: flex;
    align-items: center;
    gap: 0.8em;
    margin-top: 1em;
    padding-top: 0.8em;
    border-top: 1px solid {colors['border']};
}}

.sidebar-qr-img {{
    border-radius: 4px;
}}

.sidebar-qr-text {{
    font-size: 8.5pt;
    color: {colors['text_faded']};
    font-style: normal;
    margin: 0 !important;
    text-indent: 0;
}}

/* ─── Figures ─── */
.chapter-body figure {{
    margin: 1em 0;
    text-align: center;
    page-break-inside: avoid;
}}

/* Constrain tall SVG figures to fit within one page — prevents cross-page truncation */
.chapter-body figure img {{
    max-width: 85%;
    max-height: 150mm;
    width: auto;
    height: auto;
    object-fit: contain;
}}

.chapter-body figcaption {{
    font-size: 9pt;
    color: {colors['text_faded']};
    margin-top: 0.3em;
}}

/* ─── Links ─── */
.chapter-body a {{
    color: {colors['link']};
    text-decoration: none;
    border-bottom: 1px dotted {colors['link']};
}}

.chapter-body a.cross-ref {{
    color: {colors['accent']};
    border-bottom: 1px dotted {colors['accent']};
}}

/* ─── Back Cover ─── */
.back-cover {{
    page: cover;
    break-before: page;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    color: {colors['cover_text']};
}}

.back-cover-gradient {{
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
}}

.back-cover-content {{
    position: relative;
    z-index: 1;
    text-align: center;
    max-width: 75%;
}}

.back-avatar {{
    border-radius: 50%;
    margin-bottom: 0.8em;
}}

.back-name {{
    font-family: {fonts['heading']};
    font-size: 16pt;
    font-weight: 600;
    margin-bottom: 0.2em;
}}

.back-desc {{
    font-size: 9pt;
    color: {colors['cover_accent']};
    opacity: 0.85;
    margin-bottom: 2em;
}}

/* Three QR codes in a horizontal grid */
.back-qr-grid {{
    display: flex;
    justify-content: center;
    align-items: flex-start;
    gap: 2em;
    margin-bottom: 2em;
}}

.back-qr-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}}

.back-qrcode {{
    border-radius: 6px;
    border: 2px solid rgba(255,255,255,0.15);
}}

.back-qr-label {{
    font-size: 8pt;
    color: {colors['cover_text']};
    opacity: 0.7;
    letter-spacing: 1px;
}}

.back-tagline {{
    font-size: 9pt;
    font-style: italic;
    opacity: 0.7;
    margin-top: 0.5em;
}}
.qr-footer {{
    margin-top: 2em;
    padding: 1.5em 0;
    border-top: 1px solid {colors['border']};
    page-break-inside: avoid;
}}

.qr-footer-content {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1em;
}}

.qr-footer-text p {{
    margin: 0;
    font-size: 10pt;
    color: {colors['text']};
    text-indent: 0;
}}

.qr-footer-text .qr-tagline {{
    font-size: 8.5pt;
    font-style: italic;
    color: {colors['text_faded']};
    margin-top: 0.3em;
}}

/* ─── Watermark ─── */
.watermark {{
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 80pt;
    color: {colors['text']};
    opacity: 0.03;
    transform: rotate(-30deg);
    pointer-events: none;
    z-index: 9999;
    overflow: hidden;
}}

/* ─── Footnotes ─── */
.chapter-body .footnote {{
    font-size: {sizes['footnote']}pt;
    color: {colors['text_faded']};
}}

.chapter-body .footnote-ref {{
    font-size: 8pt;
    vertical-align: super;
}}

/* ─── Print Helpers ─── */
.page-break {{ break-before: page; }}
.no-break {{ page-break-inside: avoid; }}
{drop_cap_css}
'''


# ─── Book Builder ────────────────────────────────────────────────────────
def build_book(input_md, config, output_dir="."):
    """Parse markdown, apply config, build all book fragments."""
    print(f"Reading: {input_md}")
    with open(input_md, "r", encoding="utf-8") as f:
        md_text = f.read()

    frontmatter, body = extract_frontmatter(md_text)
    for k, v in frontmatter.items():
        if k not in config:
            config[k] = v

    # Auto-detect book title
    title = config.get('title', '')
    if title.startswith(('序言', '前言', '绪论', '导论', '引言')):
        m = re.search(r'\*\*《(.+?)》\*\*', body)
        if m:
            config['cover_title'] = m.group(1)
        else:
            config['cover_title'] = title
    else:
        config['cover_title'] = title

    chapters = parse_markdown_structure(body)
    print(f"Found {len(chapters)} chapters")

    # Merge detected system fonts with preset preferences (preset wins)
    detected = detect_fonts()
    preset_fonts = config.get('fonts', {})
    merged_fonts = dict(detected)
    merged_fonts.update(preset_fonts)
    config['fonts'] = merged_fonts

    print("Building layout...")
    cover = generate_cover_html(config, output_dir)
    copyright_page = generate_copyright_html(config)
    toc = generate_toc_html(chapters, config)
    body_html = generate_body_html(chapters, config, output_dir)
    back_cover = generate_back_cover_html(config, output_dir)

    return {
        'config': config,
        'chapters': chapters,
        'cover': cover,
        'copyright_page': copyright_page,
        'toc': toc,
        'body_html': body_html,
        'back_cover': back_cover,
    }


def assemble_full_html(book, mode='pdf'):
    """Assemble complete HTML for PDF or HTML output.
    
    No Paged.js dependency — uses Chrome's native @page + @media print.
    """
    config = book['config']
    css = generate_css(config)
    
    # Chrome native print handles @page, page-break, page numbers
    # Mermaid for inline diagrams (loaded async from CDN)
    mermaid_script = '''
<script>
(function() {
    var s = document.createElement("script");
    s.src = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js";
    s.onload = function() {
        mermaid.initialize({ startOnLoad: true, theme: "neutral",
            fontFamily: "PingFang SC, sans-serif",
            flowchart: { useMaxWidth: true, htmlLabels: true }
        });
    };
    document.head.appendChild(s);
})();
</script>'''

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{config.get('title', 'Untitled')}</title>
<style>
{css}
</style>
{mermaid_script}
</head>
<body>
{book['cover']}
{book['copyright_page']}
{book['toc']}
{book['body_html']}
{book['back_cover']}
</body>
</html>'''


def add_bookmarks(pdf_path, chapters, config):
    """Add PDF bookmarks / outline using PyMuPDF."""
    try:
        import fitz
    except ImportError:
        print("Note: PyMuPDF not installed, skipping PDF bookmarks.")
        return

    try:
        doc = fitz.open(pdf_path)
        
        # Find the TOC page (contains '目 录' or '目 录' heading)
        # Bookmarks should start searching AFTER the TOC page
        toc_page = -1
        for page_num in range(min(10, doc.page_count)):
            page = doc[page_num]
            text = page.get_text()
            if '目 录' in text or '目  录' in text or '目\n录' in text:
                toc_page = page_num
                break
        
        # Start searching from the page after TOC (or after cover+copyright if no TOC found)
        search_start = toc_page + 1 if toc_page >= 0 else 2
        
        toc = []
        min_page = search_start  # Track minimum page to search from

        for i, ch in enumerate(chapters):
            title = ch['title']
            search_title = re.sub(r'[#*_`]', '', title).strip()

            # Search for the chapter title text starting from min_page
            found_page = None
            if search_title:
                # Normalize: remove line breaks and smart quotes that PDF inserts
                norm_title = search_title.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")
                for page_num in range(min_page, doc.page_count):
                    page = doc[page_num]
                    raw_text = page.get_text()
                    # Remove newlines so multi-line PDF text can match
                    text = raw_text.replace('\n', '')
                    text = text.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")
                    if norm_title[:20] in text:
                        found_page = page_num + 1  # 1-indexed
                        min_page = page_num  # Next chapter must be on same or later page
                        break

            if found_page is None:
                found_page = min_page + 1 if min_page + 1 <= doc.page_count else search_start + 1

            toc.append([1, title, found_page])

            # Add sub-chapters as level-2 bookmarks
            for sub in ch.get('sub_chapters', []):
                sub_title = re.sub(r'[#*_`]', '', sub['title']).strip()
                sub_page = None
                if sub_title:
                    norm_sub = sub_title.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")
                    for page_num in range(min_page, doc.page_count):
                        page = doc[page_num]
                        raw_text = page.get_text()
                        text = raw_text.replace('\n', '')
                        text = text.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")
                        if norm_sub[:20] in text:
                            sub_page = page_num + 1
                            min_page = page_num  # Advance min_page to prevent backward jumps
                            break
                if sub_page is None:
                    sub_page = found_page
                toc.append([2, sub_title, sub_page])

        doc.set_toc(toc)
        doc.save(pdf_path, incremental=True, encryption=0)
        print(f"  PDF bookmarks added ({len(chapters)} chapters)")
        doc.close()
    except Exception as e:
        print(f"Warning: Could not add PDF bookmarks: {e}")


def generate_pdf(input_md, output_pdf, config):
    """Generate PDF from markdown via Playwright + Paged.js."""
    print("\n=== Sloth-Press-Den v3.0 — Professional Book Typesetting ===")
    print("=" * 55)

    os.makedirs(os.path.dirname(output_pdf) or '.', exist_ok=True)
    output_dir = os.path.dirname(os.path.abspath(output_pdf))

    print(f"Rendering PDF: {output_pdf}")
    page_size = config.get('page_size', 'A5')
    margins = config.get('page_margins', {})
    top_m = margins.get('top', 25)
    bottom_m = margins.get('bottom', 25)
    inner_m = margins.get('inner', 20)
    outer_m = margins.get('outer', 18)

    book = build_book(input_md, config, output_dir)
    full_html = assemble_full_html(book, mode='pdf')

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page()
        
        # Write HTML to temp file and load via goto(), NOT set_content().
        # set_content() loads from about:blank — Chrome blocks file:// image
        # requests from a null origin, so cover/back-cover images never render.
        # goto('file:///...') gives the page a file:// origin, allowing local images.
        html_path = os.path.join(output_dir, "_temp_book.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(full_html)
        page.goto(f"file://{html_path}", wait_until="load")
        page.wait_for_timeout(10000)  # Wait for mermaid + fonts to render

        page.pdf(
            path=output_pdf,
            format=page_size,
            # CRITICAL: Set Playwright margins to 0. CSS @page handles margins.
            # Setting margins here ADDS to CSS @page margins, creating white
            # borders that can't be overridden — the root cause of covers
            # and back covers not being full-bleed.
            margin={"top": "0mm", "bottom": "0mm",
                    "left": "0mm", "right": "0mm"},
            print_background=True,
            prefer_css_page_size=True,
        )
        browser.close()

    add_bookmarks(output_pdf, book['chapters'], book['config'])

    pdf_size = os.path.getsize(output_pdf)
    print(f"\nDone! {output_pdf}")
    print(f"  Size: {pdf_size / 1024 / 1024:.1f} MB")
    print(f"  Pages: rendering complete")
    print(f"  Theme: {config.get('name', 'custom')}")


def generate_html_output(input_md, output_html, config):
    """Generate standalone HTML file (screen-friendly)."""
    print("\n=== Sloth-Press-Den v3.0 — HTML Export ===")
    print("=" * 55)

    book = build_book(input_md, config)
    full_html = assemble_full_html(book, mode='html')

    os.makedirs(os.path.dirname(output_html) or '.', exist_ok=True)
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(full_html)

    html_size = os.path.getsize(output_html)
    print(f"\nDone! {output_html}")
    print(f"  Size: {html_size / 1024:.1f} KB")


# ─── ePub Generation ──────────────────────────────────────────────────────
def generate_epub(input_md, output_epub, config):
    """Generate ePub 2.0 using standard-library zipfile + XML."""
    import zipfile
    import uuid
    from xml.sax.saxutils import escape

    print("\n=== Sloth-Press-Den v3.0 — ePub Export ===")
    print("=" * 55)

    book = build_book(input_md, config)
    cfg = book['config']
    chapters = book['chapters']
    title = escape(cfg.get('title', 'Untitled'))
    author = escape(cfg.get('author', ''))
    desc = escape(cfg.get('description', cfg.get('subtitle', '')))
    lang = 'zh-CN'
    uid = str(uuid.uuid4())

    os.makedirs(os.path.dirname(output_epub) or '.', exist_ok=True)

    # Build ePub CSS (no @page, no Paged.js)
    epub_css = generate_css(cfg)
    epub_css = re.sub(r'@page[^{]*\{[^}]*\}', '', epub_css, flags=re.DOTALL)
    epub_css = re.sub(r'@page[^{]*\{[^}]*\{[^}]*\}[^}]*\}', '', epub_css, flags=re.DOTALL)
    epub_css = f'/* ePub-friendly base */\nhtml {{ -webkit-text-size-adjust: 100%; }}\nbody {{ margin: 0; padding: 0; }}\n' + epub_css

    def xhtml_wrapper(content):
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}">
<head>
<meta charset="UTF-8"/>
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{content}
</body>
</html>'''

    with zipfile.ZipFile(output_epub, 'w', zipfile.ZIP_DEFLATED) as zf:
        # mimetype must be first and uncompressed
        zf.writestr('mimetype', 'application/epub+zip', zipfile.ZIP_STORED)
        
        # META-INF/container.xml
        zf.writestr('META-INF/container.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>''')

        # Write CSS
        zf.writestr('OEBPS/style.css', epub_css)

        # Write cover, copyright, toc
        zf.writestr('OEBPS/cover.xhtml', xhtml_wrapper(book['cover']))
        zf.writestr('OEBPS/copyright.xhtml', xhtml_wrapper(book['copyright_page']))
        zf.writestr('OEBPS/toc.xhtml', xhtml_wrapper(book['toc']))

        manifest_items = [
            ('cover', 'cover.xhtml', 'application/xhtml+xml'),
            ('copyright', 'copyright.xhtml', 'application/xhtml+xml'),
            ('toc', 'toc.xhtml', 'application/xhtml+xml'),
        ]
        spine_items = ['cover', 'copyright', 'toc']
        nav_points = []

        for i, ch in enumerate(chapters):
            ch_id = f'chapter{i+1:03d}'
            ch_file = f'{ch_id}.xhtml'
            opener = generate_chapter_opener(ch, i, cfg)
            body_html = convert_md_to_html(ch['content'])
            body_html = process_body_html(body_html, chapter_index=i)
            ch_html = xhtml_wrapper(
                f'<section class="chapter">{opener}'
                f'<div class="chapter-body">{body_html}</div></section>'
            )
            zf.writestr(f'OEBPS/{ch_file}', ch_html)
            manifest_items.append((ch_id, ch_file, 'application/xhtml+xml'))
            spine_items.append(ch_id)
            nav_points.append(
                f'    <navPoint id="navpoint-{i+1}" playOrder="{i+1}">\n'
                f'      <navLabel><text>{escape(ch["title"])}</text></navLabel>\n'
                f'      <content src="{ch_file}"/>\n'
                f'    </navPoint>'
            )

        # content.opf
        manifest_items.append(('style', 'style.css', 'text/css'))
        manifest_xml = '\n'.join(
            f'    <item id="{item_id}" href="{href}" media-type="{mt}" />'
            for item_id, href, mt in manifest_items
        )
        spine_xml = '\n'.join(f'    <itemref idref="{sid}" />' for sid in spine_items)
        desc_tag = f'<dc:description>{desc}</dc:description>' if desc else ''

        opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package version="2.0" xmlns="http://www.idpf.org/2007/opf">
  <metadata>
    <dc:title>{title}</dc:title>
    <dc:creator>{author}</dc:creator>
    <dc:language>{lang}</dc:language>
    {desc_tag}
    <dc:identifier id="bookid">urn:uuid:{uid}</dc:identifier>
  </metadata>
  <manifest>
{manifest_xml}
  </manifest>
  <spine toc="ncx">
{spine_xml}
  </spine>
</package>'''
        zf.writestr('OEBPS/content.opf', opf)

        # toc.ncx
        ncx = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head>
    <meta name="dtb:uid" content="urn:uuid:{uid}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{title}</text></docTitle>
  <navMap>
{chr(10).join(nav_points)}
  </navMap>
</ncx>'''
        zf.writestr('OEBPS/toc.ncx', ncx)

    epub_size = os.path.getsize(output_epub)
    print(f"Done! {output_epub}")
    print(f"  Size: {epub_size / 1024:.1f} KB")
    print(f"  Chapters: {len(chapters)}")


# ─── MOBI / AZW3 Export (via Calibre ebook-convert) ───────────────────────
def generate_mobi(input_md, output_path, config, fmt='mobi'):
    """Generate MOBI or AZW3 by first creating an ePub, then converting via Calibre."""
    import tempfile
    ebook_convert = 'ebook-convert'
    if sys.platform == 'win32':
        for path in [
            r'C:\Program Files\Calibre2\ebook-convert.exe',
            r'C:\Program Files (x86)\Calibre2\ebook-convert.exe',
        ]:
            if os.path.exists(path):
                ebook_convert = path
                break

    print(f"\n=== Sloth-Press-Den v3.0 — {fmt.upper()} Export ===")
    print("=" * 55)

    # First generate an ePub in temp dir
    with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp:
        epub_path = tmp.name
    generate_epub(input_md, epub_path, config)

    # Convert via Calibre
    print(f"Converting to {fmt.upper()} via Calibre...")
    result = os.system(f'"{ebook_convert}" "{epub_path}" "{output_path}" 2>/dev/null')
    os.unlink(epub_path)

    if result == 0:
        out_size = os.path.getsize(output_path)
        print(f"Done! {output_path}")
        print(f"  Size: {out_size / 1024:.1f} KB")
    else:
        print(f"Warning: Calibre conversion failed (exit code {result}).")
        print("  Install Calibre from https://calibre-ebook.com/")
        print(f"  ePub already generated at: {epub_path}")


# ─── CLI Entry Point ─────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sloth-Press-Den — Professional Book Typesetting")
    parser.add_argument("--input", "-i", required=True, help="Input Markdown file")
    parser.add_argument("--output", "-o", default="output.pdf", help="Output file path")
    parser.add_argument("--preset", "-p", default="mist-blue", help="Theme preset")
    parser.add_argument("--format", "-f", default="pdf", choices=["pdf", "html", "epub", "mobi", "azw3"], help="Output format")
    parser.add_argument("--title", help="Book title (overrides frontmatter)")
    parser.add_argument("--author", help="Book author (overrides frontmatter)")
    parser.add_argument("--subtitle", help="Book subtitle (overrides frontmatter)")
    parser.add_argument("--slogan", help="Cover slogan line (optional, e.g. '让机器读懂业务，让AI不再胡说')")
    parser.add_argument("--watermark", help="Watermark text")
    parser.add_argument("--cover-style", default="gradient", choices=["gradient", "solid", "academic"],
                        help="Cover page style")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    config = load_preset(args.preset)
    
    # CLI overrides
    if args.title:
        config['title'] = args.title
    if args.author:
        config['author'] = args.author
    if args.subtitle:
        config['subtitle'] = args.subtitle
    if args.slogan:
        config['slogan'] = args.slogan
    if args.watermark:
        config['watermark'] = args.watermark
    if args.cover_style:
        config['cover_style'] = args.cover_style

    if args.format == "pdf":
        generate_pdf(args.input, args.output, config)
    elif args.format == "html":
        generate_html_output(args.input, args.output, config)
    elif args.format == "epub":
        generate_epub(args.input, args.output, config)
    elif args.format in ("mobi", "azw3"):
        generate_mobi(args.input, args.output, config, fmt=args.format)


if __name__ == "__main__":
    main()
