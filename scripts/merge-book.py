#!/usr/bin/env python3
"""
Merge chapters from an mdBook project into a single Markdown file,
suitable for input to press-typeset.py.

Usage:
  python merge-book.py ~/Desktop/sloth-books/ai-agent-handbook
"""

import os, re, sys
from pathlib import Path


def merge_book(book_dir, output_name="merged-manuscript.md"):
    """Merge all chapters from an mdBook project into a single file."""
    book_path = Path(book_dir).expanduser().resolve()
    summary_path = book_path / "src" / "SUMMARY.md"
    
    if not summary_path.exists():
        print(f"Error: SUMMARY.md not found at {summary_path}")
        return
    
    summary_text = summary_path.read_text(encoding="utf-8")
    
    # Extract markdown file paths from SUMMARY.md
    # Format: [title](path/to/file.md)
    md_files = re.findall(r'\(([^)]+\.md)\)', summary_text)
    
    # Read frontmatter from the book.toml if available
    book_toml = book_path / "book.toml"
    title = "Untitled"
    author = ""
    if book_toml.exists():
        toml_text = book_toml.read_text(encoding="utf-8")
        title_match = re.search(r'title\s*=\s*"([^"]+)"', toml_text)
        author_match = re.search(r'authors\s*=\s*\["([^"]+)"\]', toml_text)
        if title_match:
            title = title_match.group(1)
        if author_match:
            author = author_match.group(1)
    
    # Output
    output_path = book_path / output_name
    with open(output_path, "w", encoding="utf-8") as out:
        # Frontmatter
        out.write("---\n")
        out.write(f"title: {title}\n")
        out.write(f"author: {author}\n")
        out.write(f"date: {os.popen('date +%Y-%m-%d').read().strip()}\n")
        out.write("---\n\n")
        
        chapter_count = 0
        for rel_path in md_files:
            # Handle paths: some are like "src/foreword.md" (from SUMMARY.md)
            # or just "foreword.md"
            full_path = book_path / rel_path
            if not full_path.exists():
                # Try without the src/ prefix if it was included
                alt_path = book_path / "src" / rel_path
                if alt_path.exists():
                    full_path = alt_path
                else:
                    print(f"  ⚠️  Skipping (not found): {rel_path}")
                    continue
            
            text = full_path.read_text(encoding="utf-8")
            
            # Skip placeholder README.md files, but KEEP ones with chapter headings
            if full_path.name == "README.md":
                if not re.search(r'^#\s+第', text, re.MULTILINE):
                    continue  # placeholder, skip
            
            # For foreword, output as-is (may not have # heading)
            # For chapter files, they may or may not have # heading
            # Add the content
            out.write(text)
            out.write("\n\n")
            chapter_count += 1
            print(f"  + {rel_path}")
        
        print(f"\nMerged {chapter_count} files into {output_path}")
        size = os.path.getsize(output_path)
        print(f"Size: {size/1024:.0f} KB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python merge-book.py <book-dir> [output-name]")
        sys.exit(1)
    
    book_dir = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else "merged-manuscript.md"
    merge_book(book_dir, output_name)
