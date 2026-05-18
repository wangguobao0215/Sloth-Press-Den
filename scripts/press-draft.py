#!/usr/bin/env python3
"""
Press-Draft v3.0 — Sloth-Press-Den 写作引擎
实现 lovstudio-write-professional-book 5阶段写作工作流。

用法：
  python press-draft.py --init my-book    # Phase 1: 初始化新书
  python press-draft.py --research 1      # Phase 2: 研究第1章
  python press-draft.py --write 1         # Phase 3: 写作第1章
  python press-draft.py --review          # Phase 4: 审校全书
"""

import os, sys, yaml, json, re
from pathlib import Path
from datetime import date


def create_book(book_dir, title, author, subtitle="", chapters=10):
    """Phase 1: Initialize a new book project with complete structure."""
    book_path = Path(book_dir).expanduser().resolve()
    
    # Step 1: Create directory structure
    dirs = [
        book_path,
        book_path / "src" / "chapter-01",
        book_path / "assets" / "images",
        book_path / "references",
        book_path / "scripts",
        book_path / "output",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        (d / ".gitkeep").touch()
    
    # Step 2: Write OUTLINE.md
    outline = f"""# {title}

> {subtitle}

**作者：** {author}
**状态：** ⬜ 规划中
**章节数：** {chapters} 章
**创建日期：** {date.today()}

---

## 全书概览

[全书核心论点和结构概述]

## 章节大纲

"""
    for i in range(1, chapters + 1):
        outline += f"""### 第{i}章 [标题]
- **字数：** ~5000字
- **依赖：** [前置章节]
- **核心概念：** [概念1]、[概念2]
- **案例：** [案例描述]

"""

    (book_path / "OUTLINE.md").write_text(outline, encoding="utf-8")
    
    # Step 3: Write BOOK_SUMMARY.md
    summary = f"""# Book Summary — {title}

> 自动维护 · 每章完成后更新

"""
    for i in range(1, chapters + 1):
        summary += f"""## 第{i}章 [标题]
Status: ⬜ Not started
Word count: ~0
Key points:
- 
New terms: 

"""
    (book_path / "BOOK_SUMMARY.md").write_text(summary, encoding="utf-8")

    # Step 4: Write glossary.md
    glossary = f"""# 术语表 — {title}

| 术语 | 英文 | 定义 |
|------|------|------|
"""
    (book_path / "glossary.md").write_text(glossary, encoding="utf-8")

    # Step 5: Create chapter placeholder files
    for i in range(1, chapters + 1):
        ch_dir = book_path / "src" / f"chapter-{i:02d}"
        ch_dir.mkdir(exist_ok=True)
        
        readme = f"""# 第{i}章 [标题]

## 章节状态
- 大纲：⬜
- 写作：⬜
- 审校：⬜

## 参考文献
- 

## 术语
- 
"""
        (ch_dir / "README.md").write_text(readme, encoding="utf-8")
        (ch_dir / "refs.md").write_text("# 参考文献\n\n", encoding="utf-8")

    # Step 5.5: Write SUMMARY.md for merge-book.py compatibility
    summary_lines = [f"# {title}", "", "[前言](src/foreword.md)", ""]
    for i in range(1, chapters + 1):
        summary_lines.append(f"- [第{i}章 [标题]](src/chapter-{i:02d}/README.md)")
    (book_path / "src" / "SUMMARY.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    # Step 6: Write book.toml for mdBook (optional)
    book_toml = f"""[book]
title = "{title}"
authors = ["{author}"]
language = "zh-CN"

[output.html]
smart_punctuation = true

[preprocessor.index]

[preprocessor.links]
"""
    (book_path / "book.toml").write_text(book_toml, encoding="utf-8")

    # Step 7: Create build scripts
    build_sh = f"""#!/bin/bash
# Build PDF
python3 scripts/press-typeset.py \\
    --input merged-manuscript.md \\
    --preset publishing-classic \\
    --output output/book.pdf
"""
    (book_path / "scripts" / "build-pdf.sh").write_text(build_sh, encoding="utf-8")

    # Step 8: Create references/core-papers.md placeholder
    core_papers = f"""# 核心参考文献

> Phase 2 研究中补充完善

## 行业报告
-

## 学术论文
-

## 官方文档
-
"""
    (book_path / "references" / "core-papers.md").write_text(core_papers, encoding="utf-8")

    # Step 9: Create .github/workflows directory placeholder
    workflows_dir = book_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n✅ Book initialized: {book_path}")
    print(f"   Title: {title}")
    print(f"   Chapters: {chapters}")
    print(f"\n   Next steps:")
    print(f"   1. Edit OUTLINE.md — fill in chapter titles and descriptions")
    print(f"   2. Run: press-draft.py --research 1  (research chapter 1)")
    print(f"   3. Run: press-draft.py --write 1     (write chapter 1)")

    return book_path


def research_chapter(book_dir, chapter_num):
    """Phase 2: Research phase — prepare refs.md for a chapter.
    
    This is a placeholder that generates the references file structure.
    The actual web search should be done by the AI agent in the writing session.
    """
    book_path = Path(book_dir).expanduser().resolve()
    ch_dir = book_path / "src" / f"chapter-{chapter_num:02d}"
    
    if not ch_dir.exists():
        print(f"Error: Chapter directory not found: {ch_dir}")
        return
    
    refs = f"""# 第{chapter_num}章 — 参考文献

> 研究日期：{date.today()}

## 核心资料

1. [论文/文档标题](url) — 作者, 年份. 一句话摘要.
2. [论文/文档标题](url) — 作者, 年份. 一句话摘要.

## 案例参考

- [案例名称] — 关键启示

## 官方文档

- [文档标题](url) — 访问日期: {date.today()}

---
*在写作前完善此文件，确保每部分都有可靠来源。*
"""
    (ch_dir / "refs.md").write_text(refs, encoding="utf-8")
    print(f"✅ Research template created for Chapter {chapter_num}")
    print(f"   File: {ch_dir / 'refs.md'}")


def write_chapter(book_dir, chapter_num, content):
    """Phase 3: Write a chapter. 
    
    Args:
        book_dir: Book project directory
        chapter_num: Chapter number (1-indexed)
        content: Full markdown content for the chapter
    
    This function:
    1. Writes the chapter content to section-01.md
    2. Updates BOOK_SUMMARY.md
    3. Updates glossary.md
    """
    book_path = Path(book_dir).expanduser().resolve()
    ch_dir = book_path / "src" / f"chapter-{chapter_num:02d}"
    
    if not ch_dir.exists():
        print(f"Error: Chapter directory not found: {ch_dir}")
        return
    
    # Write chapter content
    ch_file = ch_dir / "section-01.md"
    ch_file.write_text(content, encoding="utf-8")
    
    # Update chapter README
    readme = f"""# 第{chapter_num}章 [标题]

## 章节状态
- 大纲：✅
- 写作：✅
- 审校：⬜
"""
    (ch_dir / "README.md").write_text(readme, encoding="utf-8")
    
    print(f"✅ Chapter {chapter_num} written")
    print(f"   File: {ch_file}")
    print(f"   ⚠️  Please update BOOK_SUMMARY.md and glossary.md")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Press-Draft — Book Writing Engine")
    parser.add_argument("--init", help="Initialize a new book (provide book directory)")
    parser.add_argument("--title", default="Untitled", help="Book title")
    parser.add_argument("--author", default="", help="Book author")
    parser.add_argument("--subtitle", default="", help="Book subtitle")
    parser.add_argument("--chapters", type=int, default=10, help="Number of chapters")
    parser.add_argument("--research", type=int, help="Research chapter number")
    parser.add_argument("--write", type=int, help="Write chapter number")
    parser.add_argument("--book-dir", default=".", help="Book project directory")

    args = parser.parse_args()

    if args.init:
        create_book(args.init, args.title, args.author, args.subtitle, args.chapters)
    elif args.research:
        research_chapter(args.book_dir, args.research)
    else:
        print("Usage examples:")
        print("  python press-draft.py --init my-book --title 'My Book' --author 'Me'")
        print("  python press-draft.py --research 1 --book-dir my-book")
