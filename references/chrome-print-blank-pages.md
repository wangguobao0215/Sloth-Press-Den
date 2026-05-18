# Chrome Native @print: Named Pages & Blank Page Debug

> Documented: 2026-05-18 | Chromium 130+ (Playwright)

## Problem

Using `@page xxx { content: none; }` named-page rules in CSS causes Chrome to
insert blank transitional pages between different named page contexts, and
also between certain named→default page transitions.

## Symptom

PDF structure shows:
```
p1:  Cover
p2:  BLANK (only page number)
p3:  Copyright
p4:  BLANK (only page number)
p5:  TOC
p6+: Content
```

## Root Cause (systematically proven)

A series of minimal HTML tests was run through Playwright Chromium,
generating PDFs and checking each page for content vs. blank.

### Test Matrix Results

| Test | Named Pages | `break-after` on Cover | Result |
|------|-------------|----------------------|--------|
| No named pages, just `break-after` on cover | None | Yes | ⚠️ p2 blank |
| No named pages, no `break-after` on cover | None | No | ✅ No blanks |
| `@page cover { margin:0; @top-center:none; }` + `page:cover` class | Cover | Yes | ⚠️ blanks |
| `@page cover { margin:0; @top-center:none; }` + `page:cover` class | Cover | No | ⚠️ blanks |
| `@page cover { @top-center { content: "BOOK"; } }` (real text!) | Cover (with content) | Yes | ✅ No blanks |
| `@page cover { @top-center { content: ""; } }` (empty string) | Cover | Yes | ⚠️ p2 blank |
| `@page cover { }` (empty rule) | Cover (empty) | Yes | ⚠️ p2 blank |
| No `@page` rule, just `page: cover` on class | Class-only | Yes | ✅ No blanks |
| `@page copyright { @top-center:none; }` | Copyright | No | ⚠️ blanks at each transition |
| Default `@page` only, no named rules | None | No | ✅ Perfect, no blanks |

### Key Insight

The blank page is caused by `content: none` (or empty `content: ""`) inside a
named `@page` rule combined with the named page transition. Chrome 130+
interprets `content: none` as "this page-margin box should not exist" and
inserts a blank transitional page when switching to/from such a named page.

Even an **empty** `@page cover { }` rule (no content directives at all) still
triggers the blank page when a class uses `page: cover`. The safest approach
is to simply not define any named `@page` CSS rules.

### The `break-after: page` Interaction

Separate from the named-page issue: putting both `min-height: 100vh` AND
`break-after: page` on the cover element causes Chrome to produce an extra
blank page. The cover already fills the full viewport naturally, so
`break-after: page` triggers a redundant page break.

**Fix**: Remove `break-after: page` from `.cover-page`. Keep `min-height: 100vh`.

## Verified Working Setup

```css
@page {
    size: A5;
    margin: 22mm;
    @top-center { content: "Book Title"; ... }
    @bottom-center { content: counter(page); ... }
}

/* Do NOT add @page cover, @page copyright, @page toc, @page chapter-opener */

.cover-page {
    /* NO page: cover */
    /* NO break-after: page */
    min-height: 100vh;
    ...
}

.copyright-page {
    break-after: page;
    ...
}

.toc-page {
    break-after: page;
    ...
}

.chapter-opener {
    break-before: page;
    break-after: page;
    ...
}

.back-cover {
    break-before: page;
    min-height: 100vh;
    ...
}
```

**Trade-off**: Cover and chapter openers show the book title as a running
header (inherited from the default `@page`). This is visually acceptable;
blank pages are not.

## What NOT to Do

- ❌ `@page cover { margin:0; @top-center: none; ... }` — blank transition pages
- ❌ `@page copyright { @top-center: none; }` — blank pages at copyright→TOC→chapter transitions  
- ❌ `@page chapter-opener { @top-center: none; }` — blank pages at every chapter transition
- ❌ `.cover-page { break-after: page; }` when also using `min-height: 100vh`
- ❌ Any `@page` named rule with `content: ""` or `content: none`
- ❌ Any `@page` named rule at all — even empty `@page xxx { }` triggers the bug

## Verification

After building a PDF, check pages 1-6 with PyMuPDF:

```python
import fitz
doc = fitz.open("output.pdf")
for i in range(min(6, doc.page_count)):
    lines = [l.strip() for l in doc[i].get_text().split("\n") if l.strip()]
    meaningful = [l for l in lines if l not in ["BookTitle", str(i+1), f"{i+1}", ""]]
    is_blank = len(meaningful) < 1
    print(f"p{i+1}: {'⚠️ BLANK' if is_blank else '✅ OK'}")
```

Expected: p1=Cover, p2=Copyright, p3=TOC, p4+=Content — no blank pages.
