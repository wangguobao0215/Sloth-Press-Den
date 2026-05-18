#!/usr/bin/env python3
"""
Press-Review v3.0 — Sloth-Press-Den 审校引擎
检查全书一致性：术语、引用、章节衔接、排版规范。

用法：
  python press-review.py --book-dir my-book          # 审校全书
  python press-review.py --book-dir my-book --chapter 3  # 只审校第3章
"""

import os, re, sys
from pathlib import Path


def collect_all_chapters(book_dir):
    """Collect all chapter markdown files from the book directory."""
    book_path = Path(book_dir).expanduser().resolve()
    chapters = []
    
    # Try to read OUTLINE.md for chapter structure
    outline_file = book_path / "OUTLINE.md"
    if outline_file.exists():
        text = outline_file.read_text(encoding="utf-8")
        ch_pattern = re.findall(r'###\s+第(\d+)章\s+(.+?)$', text, re.MULTILINE)
        for num, title in ch_pattern:
            ch_dir = book_path / "src" / f"chapter-{int(num):02d}"
            chapters.append({'num': int(num), 'title': title.strip(), 'dir': ch_dir})
    
    # Fallback: scan chapter directories
    if not chapters:
        for d in sorted((book_path / "src").glob("chapter-*")):
            num_match = re.search(r'chapter-(\d+)', d.name)
            if num_match:
                chapters.append({'num': int(num_match.group(1)), 'title': '', 'dir': d})
    
    return book_path, chapters


def check_glossary_terms(book_path, chapters):
    """Check that glossary terms are used consistently in all chapters."""
    glossary_file = book_path / "glossary.md"
    if not glossary_file.exists():
        return [], ["glossary.md not found"]
    
    glossary_text = glossary_file.read_text(encoding="utf-8")
    
    # Extract terms from glossary
    terms = re.findall(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', glossary_text)
    # Skip header row
    terms = [(t.strip(), e.strip()) for t, e in terms if t.strip() and t != '术语']
    
    issues = []
    for term, english in terms:
        # Check if term appears in each chapter
        for ch in chapters:
            for md_file in ch['dir'].glob("*.md"):
                if md_file.name in ('README.md', 'refs.md'):
                    continue
                text = md_file.read_text(encoding="utf-8")
                # Check for inconsistent usage
                if term not in text:
                    issues.append({
                        'type': 'term_missing',
                        'chapter': ch['num'],
                        'term': term,
                        'file': str(md_file.relative_to(book_path)),
                        'message': f"术语「{term}」({english}) 未在章节中使用"
                    })
    
    return issues, []


def check_references(book_path, chapters):
    """Check that all citations have corresponding references."""
    issues = []
    
    for ch in chapters:
        refs_file = ch['dir'] / "refs.md"
        refs = []
        if refs_file.exists():
            ref_text = refs_file.read_text(encoding="utf-8")
            refs = re.findall(r'^(\d+)\.\s+', ref_text, re.MULTILINE)
        
        for md_file in ch['dir'].glob("*.md"):
            if md_file.name in ('README.md', 'refs.md'):
                continue
            text = md_file.read_text(encoding="utf-8")
            citations = re.findall(r'\[\^(\d+)\]', text)
            
            for cite in citations:
                if cite not in refs:
                    issues.append({
                        'type': 'missing_ref',
                        'chapter': ch['num'],
                        'file': str(md_file.relative_to(book_path)),
                        'message': f"引用 [^{cite}] 在 refs.md 中无对应条目"
                    })
    
    return issues, []


def check_cross_references(book_path, chapters):
    """Check cross-references between chapters."""
    issues = []
    
    for ch in chapters:
        for md_file in ch['dir'].glob("*.md"):
            if md_file.name in ('README.md', 'refs.md'):
                continue
            text = md_file.read_text(encoding="utf-8")
            
            # Check "参见第X章" / "见第X章" references
            xrefs = re.findall(r'(?:参见|见|参考)\s*第(\d+)章', text)
            for target_num in xrefs:
                target = int(target_num)
                valid = any(c['num'] == target for c in chapters)
                if not valid:
                    issues.append({
                        'type': 'broken_xref',
                        'chapter': ch['num'],
                        'file': str(md_file.relative_to(book_path)),
                        'message': f"引用第{target}章但该章不存在"
                    })
    
    return issues, []


def check_typography(book_path, chapters):
    """Check common typography issues in CJK text."""
    issues = []
    
    patterns = [
        (r'[\u4e00-\u9fff][A-Za-z]', '中英文之间缺少空格'),
        (r'[A-Za-z][\u4e00-\u9fff]', '中英文之间缺少空格'),
        (r'[\u4e00-\u9fff]\d', '中文与数字之间建议加空格'),
        (r'\d[\u4e00-\u9fff]', '数字与中文之间建议加空格'),
        (r'《[^》]*《', '嵌套书名号'),
        (r'"[^"]*"', '应使用中文引号「」或""，而不是直引号'),
        (r"'[^']*'", '应使用中文引号，而不是单直引号'),
        (r'\.{2,}', '省略号应为……'),
    ]
    
    for ch in chapters:
        for md_file in ch['dir'].glob("*.md"):
            if md_file.name in ('README.md', 'refs.md'):
                continue
            text = md_file.read_text(encoding="utf-8")
            
            for pattern, msg in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    issues.append({
                        'type': 'typography',
                        'chapter': ch['num'],
                        'file': str(md_file.relative_to(book_path)),
                        'message': f"{msg} (发现 {len(matches)} 处)",
                        'examples': matches[:3],
                    })
    
    return issues, []


def review_book(book_dir, chapter_num=None):
    """Run all review checks."""
    book_path, chapters = collect_all_chapters(book_dir)
    
    if chapter_num:
        chapters = [c for c in chapters if c['num'] == chapter_num]
    
    if not chapters:
        print(f"Error: No chapters found in {book_dir}")
        return
    
    print(f"\n=== Sloth-Press-Den — Book Review ===")
    print(f"Book: {book_path.name}")
    print(f"Chapters: {', '.join(str(c['num']) for c in chapters)}")
    print("=" * 50)
    
    all_issues = []
    all_warnings = []
    
    # Run checks
    checks = [
        ("术语一致性", check_glossary_terms),
        ("引用完整性", check_references),
        ("跨章引用", check_cross_references),
        ("排版规范", check_typography),
    ]
    
    for name, check_fn in checks:
        issues, warnings = check_fn(book_path, chapters)
        all_issues.extend(issues)
        all_warnings.extend(warnings)
        status = "✅" if not issues else f"⚠️  {len(issues)} issues"
        print(f"\n  {name}: {status}")
        for issue in issues[:5]:
            print(f"    - Ch{issue['chapter']}: {issue['message']}")
        if len(issues) > 5:
            print(f"    ... and {len(issues) - 5} more")
    
    totals = {}
    for issue in all_issues:
        t = issue['type']
        totals[t] = totals.get(t, 0) + 1
    
    print(f"\n{'=' * 50}")
    print(f"Summary: {len(all_issues)} issues found")
    for t, c in sorted(totals.items()):
        print(f"  {t}: {c}")
    
    return all_issues


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Press-Review — Book Review Engine")
    parser.add_argument("--book-dir", required=True, help="Book project directory")
    parser.add_argument("--chapter", type=int, help="Specific chapter to review")
    
    args = parser.parse_args()
    review_book(args.book_dir, args.chapter)
