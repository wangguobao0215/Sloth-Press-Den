# 能力审计 — lovstudio-write-professional-book + Sloth-BookSmith-Den

> 生成时间: 2026-05-17
> 为 sloth-press-den v3.1 质量验收而做

## 审计方法

1. 解密 lovstudio-write-professional-book 完整 SKILL.md + workflow.md
2. 克隆并研读 Sloth-BookSmith-Den 完整代码库（1,980行 booksmith.py）
3. 逐一对照能力清单并标注状态

---

## lovstudio-write-professional-book 能力审计

| # | 能力 | 是否实现 | 说明 |
|---|------|---------|------|
| 1 | Phase 1: 规划 — OUTLINE.md + 目录骨架 + book.toml | ✅ press-draft.py --init | 完整实现 |
| 2 | Phase 1: GitHub repo 创建 | ⚠️ 用 monorepo(sloth-books) 而非每书一仓 | 设计取舍，非缺陷 |
| 3 | Phase 1: README 含封面图+进度表 | ❌ 未实现 | 低优先级 |
| 4 | Phase 2: 研究 — 每章搜索参考文献 → refs.md | ✅ press-draft.py --research + 实际执行 | 已为 ai-agent-handbook 执行 |
| 5 | Phase 2: bibliography.md 全书参考文献 | ✅ 创建 bibliography.md（27条） | 覆盖学术/行业/文档/博客 |
| 6 | Phase 3: 写作 — 一章一次会话 + 用户确认小节大纲 | ✅ 遵循 lovstudio 策略 | 已内化到 SKILL.md |
| 7 | Phase 3: BOOK_SUMMARY.md 上下文桥 | ✅ 内容自动更新流程 | 在 SKILL.md 中强调 |
| 8 | Phase 4: 审校 — 术语一致性 | ✅ press-review.py | 已实现 |
| 9 | Phase 4: 引用完整性检查 | ✅ press-review.py | 已实现 |
| 10 | Phase 4: 跨章衔接检查 | ✅ press-review.py | 已实现 |
| 11 | Phase 5: 构建 — 多格式输出 | ✅ press-typeset.py | PDF/HTML/ePub/MOBI/AZW3 |

## Sloth-BookSmith-Den 能力审计

| # | 能力 | BookSmith实现 | 我们的实现 | 状态 |
|---|------|--------------|-----------|------|
| 1 | YAML 主题预设 | 6套完整主题 | 5套（含雾霁蓝） | ✅ |
| 2 | Paged.js CSS 分页 | v0.4.3 | v0.4.3 | ✅ 复用同一版本 |
| 3 | CJK 三平台字体检测 | detect_fonts() | detect_fonts() | ✅ 完全移植 |
| 4 | @page 命名页系统 | cover/copyright/toc/chapter-opener | 同上 + qr-page | ✅ 多一个qr-page |
| 5 | running headers/footers | @top-center + @bottom-center | 同上 | ✅ |
| 6 | 封面（渐变版） | generate_cover_html() | 同架构 | ✅ |
| 7 | 封面（solid/image/texture/academic） | 5种cover_style | ❌ 仅gradient | 低优先级 |
| 8 | 版权页 | generate_copyright_html() | 同架构 | ✅ |
| 9 | 目录（H1+H2） | generate_toc_html() | 同架构，含sub-chapters | ✅ |
| 10 | PDF 书签 | add_bookmarks() | 同架构 | ✅ |
| 11 | TOC 页码目标引用 | target-counter CSS | 同CSS | ✅ 依赖Paged.js渲染 |
| 12 | 章节扉页 | generate_chapter_opener() | 同架构 | ✅ |
| 13 | 题记（epigraph） | > "quote" — source 解析 | 同逻辑 | ✅ |
| 14 | 正文排版（字号/行距/边距） | generate_css() | 同架构 | ✅ |
| 15 | 动态行距计算 | body_size ≤10/11/>11 三段 | 同逻辑 | ✅ |
| 16 | 首行缩进 | first_line_indent 参数化 | 同 | ✅ |
| 17 | 代码高亮 | Pygments codehilite | 同 | ✅ |
| 18 | 代码块CSS | border + background + padding | 同 + white-space:pre/word-break | ✅ 更完善 |
| 19 | 表格（三线表+自动编号） | table_caption + numbering | 同 | ✅ |
| 20 | 图（figure+自动编号） | fig_counter + 图X-Y | 同 | ✅ |
| 21 | 侧边栏/callout | blockquote → aside.sidebar | 同 | ✅ |
| 22 | 交叉引用链接 | 参见/参阅/参考/见 → a.cross-ref | 同 | ✅ 较晚加入 |
| 23 | 首字下沉（drop cap） | CSS first-letter | 同CSS（未激活） | ✅ 有代码 |
| 24 | 水印 | watermark div overlay | 同 | ✅ |
| 25 | PDF（Playwright） | generate_pdf() | 同 | ✅ |
| 26 | HTML（screen-friendly） | generate_html_output() | 同 | ✅ |
| 27 | **ePub 2.0** | generate_epub() | 同架构 | ✅ **新增** |
| 28 | **MOBI/AZW3（Calibre）** | generate_mobi() | 同 | ✅ **新增** |
| 29 | **mermaid 流程图** | ❌ 无 | ✅ 新增mermaid.js CDN | ✅ **超越** |
| 30 | **雾霁蓝品牌配色** | ❌ 无 | ✅ mist-blue preset | ✅ **超越** |
| 31 | **自动二维码尾页** | ❌ 无 | ✅ 内嵌base64 QR | ✅ **超越** |

## 差距清单（未实现且需关注）

| 缺失能力 | 来源 | 优先级 | 原因 |
|----------|------|--------|------|
| GitHub Actions CI 自动构建 | lovstudio | 🟡 中 | 需先创建Sloth-Press-Den仓库 |
| 封面风格变体（solid/image/texture/academic） | BookSmith | 🟢 低 | 当前gradient够用 |
| TOC 页码后处理注入 | BookSmith | 🟢 低 | target-counter CSS应已工作 |

## 关键教训（翻车提炼）

### 架构层面
1. ❌ 不要只写工具不执行 → press-draft --research 写了但没为ai-agent-handbook跑，等于没用
2. ❌ 不要跳过Phase 2和Phase 4 → 最容易被跳过的恰恰最不能跳
3. ❌ 不要以为"研究了"就说学会了 → 要逐条对照能力清单验证

### CJK排版层面
4. ❌ text-align: justify 对中文 → 字间距拉伸，必须用 text-align: left
5. ❌ min-height: 70vh/100vh 在Paged.js中 → 分页冲突导致内容重叠
6. ❌ nl2br扩展 → 多余 <br> 标签破坏排版
7. ❌ sane_lists扩展 → Python-Markdown中行为不稳定
8. ✅ 代码块内 `#` → 用 in_code_block 状态跟踪过滤
9. ✅ 极短的README.md（~48字符） → 以 heading 为判断依据，不以长度为准

### 流程层面
10. ❌ 不要闭门造车 → 造轮子之前必须先学透现有技能
11. ✅ 研究阶段不能自欺欺人 → lovstudio的Phase 2需要实际搜索、整理、写入
12. ✅ 一次会话只写一章 → 上下文窗口是硬约束
