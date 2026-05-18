# Book Structure Design Decisions

> 2026-05-17 从 executive-agent-book 项目中提炼

## Chapter Numbering in Openers

**Decision:** Do NOT display any chapter numbers on chapter opener pages.

**Rationale:** Displaying "第一章" on the opener AND "第1章" in the TOC confuses readers. The TOC already shows chapter numbers via its list structure. Openers should display ONLY the title.

**How:** `generate_chapter_opener()` was simplified to remove ALL `opener-number` output. The `_cn_num()` helper and `opener-number` CSS class are no longer used by the opener flow.

## TOC: Prefaces vs Chapters

**Decision:** Prefaces ("前言", "序言", etc.) appear in a visually separate section of the TOC before the numbered chapters.

**Rationale:** Putting "前言" in the same numbered list as "第1章" makes the sequence confusing. Prefaces should be visually distinct.

**How:** `generate_toc_html()` splits items into `preface_items` and `chapter_items`, then concatenates them with `all_items = preface_items + chapter_items`. Preface items use CSS class `toc-preface` (italic, muted color, no bottom border).

## QR Code & Back Cover

**Decision:** QR code and avatar appear on a dedicated back cover page, styled consistently with the front cover. The back cover includes: rounded avatar (sloth-avatar-round.png), name "树懒老K（拙一）", tagline "30年企业服务经验 · 专注AI智能体与组织变革", and QR code with "扫码关注公众号" text.

**Rationale:** User explicitly requested a back cover with avatar and QR code. A full back cover feels more like a real book than a QR footer at the end of the last chapter.

**How:** `generate_back_cover_html()` creates a full-page back cover using the same gradient background as the front cover. Images are copied to the output directory with `_ensure_asset()` which returns an absolute `file://` path — this is critical because Playwright's `page.set_content()` has no base URL, so relative paths won't resolve. Assets are sourced from `~/Desktop/Sloth-MGO-Eido/assets/` (first priority), then `~/Desktop/Sloth-BookSmith-Den/assets/`, then the skill's own `assets/` directory.

**Image Loading Fix:** When using Playwright's `page.set_content()`, the page base URL is `about:blank`. Relative image paths like `src="qrcode.jpg"` will NOT load. The fix: copy assets to the output directory and use absolute `file://` paths. The `_ensure_asset()` helper function handles copying and returns the correct `file://` URL.

## Font Preference

**Decision:** Use PingFang SC for all body text and headings (sans-serif throughout).

**Rationale:** User explicitly prefers 苹方 over 宋体. Clean, modern, appropriate for business/tech books aimed at executives. Pre-installed on macOS.

## Cover Style Variants

Three cover styles available via `--cover-style`:
- `gradient` (default) — gradient background, decorative corner elements, border frame
- `solid` — solid background color, no decorations, clean
- `academic` — thin horizontal lines, restrained typography, smaller title
