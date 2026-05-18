---
name: sloth-press-den
description: 树懒老K写书工坊 v3.2 — 从规划到出版的完整写书流水线。整合 lovstudio 5阶段写作流程 + BookSmith 专业排版架构 + Chrome原生打印引擎 + 自动审校。支持5套专业主题预设（含雾霁蓝）。
version: 3.2.0
author: 树懒老K（拙一）
license: MIT
trigger: 用户说"写书"、"写电子书"、"出书"、"开始写书"、"排版"、"出版"、"出PDF"、"转PDF"、"出书稿"、"整本书"
metadata:
  hermes:
    tags: [writing, publishing, typesetting, pdf, book, cjk, chinese]
    related_skills: [lovstudio-write-professional-book, sloth-deck, html-ppt]
---

# Sloth-Press-Den v3.2 — 树懒老K写书工坊

> **匠书·出版排版引擎 + 写作工坊 = 从零到成书的完整流水线**

汲取 **lovstudio-write-professional-book** 的5阶段写作流程 + **Sloth-BookSmith-Den** 的出版级排版引擎精华，重写再造，超越两者。

## Overview

Sloth-Press-Den 是一个面向中文商业书籍的出版级写作与排版工具链。它整合了从内容规划、写作、审校到 PDF/HTML/ePub 输出的完整流程，基于 Chrome 原生 @page 打印引擎渲染，无需 LaTeX 或 Paged.js 等外部依赖。

核心能力：
- **5阶段写作引擎**：规划 → 研究 → 写作 → 审校 → 构建（基于 lovstudio 工作流）
- **出版级排版**：A5 书籍排版、雾霁蓝/经典出版等5套专业预设、CJK 排版最佳实践
- **封面/封底系统**：圆形头像 + 渐变背景 + 公众号二维码
- **多格式输出**：PDF（原生分页）、HTML、ePub、MOBI、AZW3
- **知识附件**：自动生产表编号、图编号、交叉引用、PDF 书签、章首题记

**用户品牌配色**：老K所有书的默认预设为 `mist-blue`（雾霁蓝）。不要用 `publishing-classic` 或其他预设重建已有书的 PDF，除非用户明确要求。重建前必须确认原书使用的 preset。`press-typeset.py` 的 CLI 默认值已设为 `mist-blue`。

## When to Use

- 用户说"写书"、"出书"、"写电子书"、"出版"
- 需要将 Markdown 书稿排版为出版级 PDF
- 已经有完整书稿（单文件 Markdown 或 mdBook 项目）需要输出 PDF/HTML/ePub
- 需要给书加封面、封底、目录、作者头像和公众号二维码
- 从零开始按专业流程写完一本书（规划→研究→写作→审校→构建）

**不要用于**：单页文档排版（用 `sloth-deck` 或 `html-ppt`）、不需要出版级质量的快速输出、非中文书籍。

---

## 前置条件

```bash
pip install markdown pygments pyyaml playwright qrcode Pillow
playwright install chromium
# 可选（用于PDF书签注入）：
pip install PyMuPDF
```

**仓库**：`~/Desktop/sloth-books/`（多书 monorepo 模式）

**用户字体偏好**：首选中文字体为**苹方（PingFang SC）**，正文和标题均使用无衬线体。QR码使用 `~/Desktop/Sloth-BookSmith-Den/assets/qrcode.jpg` 现有文件，不自动生成新的。

---

## 核心架构

```
┌──────────────────────────────────────────────────────────────┐
│                  Sloth-Press-Den v3.0                       │
├────────────┬──────────────────┬──────────────┬──────────────┤
│  写作引擎   │    排版引擎      │   审校引擎    │  编排器      │
│ press-draft │ press-typeset   │ press-review │ press-pipeline│
├────────────┼──────────────────┼──────────────┼──────────────┤
│ lovstudio   │ BookSmith精华    │ 术语/引用/   │ 一键全流程    │
│ 5阶段流程    │ + Chrome原生@page │ 排版规范检查  │              │
└────────────┴──────────────────┴──────────────┴──────────────┘
```

### 完整工作流（5 Phase）

| 阶段 | 引擎 | 输入 → 输出 |
|------|------|------------|
| **Phase 1: 规划** | press-draft --init | 书名/作者 → OUTLINE.md + 目录骨架 + 术语表 |

**Phase 1 要点**：
- 用 `clarify` 工具向用户确认书名、副标题、目标读者、章节数——不要假设你知道，即使之前讨论过
- 如果用户说"从零开始"或"忽略现有材料"，必须用 `--init` 新建目录，绝不能迁移旧内容冒充"重新写"
| **Phase 2: 研究** | press-draft --research | 章号 → refs.md（参考文献框架） |
| **Phase 3: 写作** | 逐章写作（一次会话一章或整本一次性，前提是OUTLINE已批准） | OUTLINE.md + BOOK_SUMMARY.md → 章节Markdown |
| **Phase 4: 审校** | press-review --book-dir | 全书 → 术语/引用/排版检查报告 |
| **Phase 5: 构建** | press-pipeline.sh + press-typeset | merged-manuscript.md → PDF/HTML/ePub/MOBI/AZW3 |

---

## 排版引擎能力

## 主题预设（5套）

| 预设 | 风格 | 适合 | 纸张 |
|------|------|------|------|
| `mist-blue` | **雾霁蓝 · 品牌色系** | 商业书籍、品牌内容 | A5 |
| `publishing-classic` | 经典出版 · 暖纸深红 | 文学、社科、商业 | A5 |
| `tech-modern` | 科技现代 · 品牌蓝 | 技术书籍、开发者手册 | A4 |
| `consulting-navy` | 咨询深蓝 · 海军蓝 | 商业报告、白皮书 | A4 |
| `dark-ebook` | 深色电子书 · 护眼 | 夜间阅读、电子墨水 | A5 |

### 排版特性

| 特性 | 说明 |
|------|------|
| **渲染引擎** | Chrome 原生 @page 打印引擎，不依赖第三方 JS 库，避免 polyfill 兼容性 bug |
| **页面设置** | @top-center 书名字眉 + @bottom-center 页码（Chrome原生支持） |
| **字体系统** | macOS/Windows/Linux 三平台自动检测 + CJK 专业回退链 |
| **封面系统** | 渐变背景 + 角标装饰 + 边框 + 标题/副标题/作者。支持三种风格：gradient（渐变默认）、solid（纯色）、academic（学术细线） |
| **版权页** | 自动生成标准版权页 |
| **目录** | 自动生成可点击目录，H2 子章节自动收录 |
| **章节扉页** | 独立扉页 + 中文章号 + 题记支持（`> "引文" —— 出处`） |
| **正文排版** | 首行缩进、行距按字号动态计算、CJK 左对齐（避免字间拉伸） |
| **代码高亮** | Pygments 语法高亮，fenced code 块，monospace 对齐 |
| **表格** | 三线表风格 + 自动编号（表X-Y）+ 斑马纹 |
| **图片** | 自动居中 + 图注编号（图X-Y） |
| **侧边栏/callout** | blockquote 内 `**标题:** 内容` 自动转为 styled aside |
| **交叉引用** | `参见/参阅/参考/见 第X章` 自动转为可点击链接 |
| **水印** | CLI 参数注入全页水印 |
| **二维码** | 自动生成最后一页公众号二维码（真实PNG文件，解决Chrome print不渲染inline data URI的问题） |
| **PDF 书签** | 章节级 PDF outline + 子章节书签（需 PyMuPDF） |
| **多格式输出** | PDF（Chrome原生分页）+ HTML + ePub + MOBI + AZW3（需 Calibre） |
| **mermaid 图表** | 支持 ` ```mermaid ` 代码块渲染流程图/架构图（mermaid.js CDN 加载，PDF 渲染等待 10s） |

### 字号体系

| 元素 | 经典出版 | 科技现代 | 咨询深蓝 | 深色电子书 | 雾霁蓝 |
|------|---------|---------|---------|-----------|--------|
| 封面标题 | 42pt | 40pt | 38pt | 40pt | 36pt |
| 章标题 | 28pt | 26pt | 24pt | 26pt | 24pt |
| 正文 | 11pt | 10.5pt | 10.5pt | 11pt | 11pt |
| 代码 | 9pt | 9pt | 8.5pt | 9pt | 9pt |

---

### 雾霁蓝配色详情

```yaml
deep:     #3A4E66    (深蓝灰 — 标题/表头)
mid:      #48607C    (中蓝灰 — 次要元素)
accent:   #5B9BC8    (雾霁蓝 — 强调/链接/边框)
gold:     #C8B99B    (暖金 — 封面点缀/装饰)
light:    #B4CDE1    (浅蓝 — 边框/分界线)
page_bg:  #F7F9FC    (极浅蓝白 — 页面底色)
```

---

## 使用方式

### 一键成书（全流程）

```bash
cd ~/.hermes/skills/writing/sloth-press-den
bash scripts/press-pipeline.sh ~/Desktop/sloth-books/my-book
```

### 分步使用

```bash
# Phase 5: 排版输出
python scripts/press-typeset.py \
    --input ~/Desktop/sloth-books/my-book/merged-manuscript.md \
    --preset tech-modern \
    --output ~/Desktop/sloth-books/my-book/output/book.pdf

# 输出HTML
python scripts/press-typeset.py \
    --input ~/Desktop/sloth-books/my-book/merged-manuscript.md \
    --preset mist-blue \
    --format html \
    --output ~/Desktop/sloth-books/my-book/output/book.html

# 指定参数
python scripts/press-typeset.py \
    --input manuscript.md \
    --preset consulting-navy \
    --output report.pdf \
    --title "商业报告" \
    --author "树懒老K" \
    --subtitle "2026年度战略分析" \
    --cover-style academic \
    --watermark "内部资料"

# 审校
python scripts/press-review.py --book-dir ~/Desktop/sloth-books/my-book
```

### 新建一本书

```bash
python scripts/press-draft.py \
    --init ~/Desktop/sloth-books/my-new-book \
    --title "我的新书" \
    --author "树懒老K" \
    --subtitle "从入门到精通" \
    --chapters 12
```

---

## 场景：从 mdBook 项目排版

如果你的书稿是多文件的 mdBook 项目（如 `ai-agent-handbook`），先用 `merge-book.py` 合并：

```bash
python scripts/merge-book.py ~/Desktop/sloth-books/ai-agent-handbook
# 输出：merged-manuscript.md
```

合并后自动提取书名和作者（从 book.toml），生成 YAML frontmatter，然后：

```bash
python scripts/press-typeset.py \
    --input ~/Desktop/sloth-books/ai-agent-handbook/merged-manuscript.md \
    --preset mist-blue \
    --output ~/Desktop/sloth-books/ai-agent-handbook/output/book.pdf
```

注意：确保每个章节的 README.md 以 `# 第X章` 开头，否则会被当做占位符跳过。

## 场景：已有书稿排版

如果你已经有了一本完整的 Markdown 书稿（单文件），直接使用排版引擎：

```bash
python scripts/press-typeset.py \
    --input manuscript.md \
    --preset mist-blue \
    --output book.pdf \
    --title "书名" \
    --author "作者"
```

书稿需遵循以下结构：

```markdown
---
title: 书名
author: 作者
date: 2026-05-17
---

# 第一章 标题

> "题记引用" —— 出处

正文内容...

## 子章节

更多内容...

## 本章小结

1. 核心观点1
2. 核心观点2

### 📚 延伸阅读

- **专题名称** — 推荐理由

---

# 第二章 标题

...
```

---

## 书稿结构规范

- `# 标题` — 章标题（每章以 `# ` 开头）
- `## 标题` — 子章节（自动生成目录二级条目）
- `> "内容" —— 来源` — 章首题记
- `---` 前 YAML frontmatter — 元数据（title, author, date）
- `![alt](path)` — 自动编号 + 图注
- Markdown 表格 — 自动编号 + 三线表样式
- `[^1]` 脚注 — 自动渲染

---

## 审校检查项

| 检查项 | 说明 |
|--------|------|
| 术语一致性 | glossary.md 中的术语是否在正文中出现 |
| 引用完整性 | 所有 [^n] 是否有对应 refs.md 条目 |
| 跨章引用 | 参见第X章是否存在 |
| 中英文空格 | 中英混排是否规范 |
| 中文引号 | 是否使用正确的中文引号 |
| 省略号 | 是否使用正确的省略号 |

---

## Common Pitfalls / 翻车记录

### 写作流程踩坑
- ❌ 不要跳过 BOOK_SUMMARY.md 更新 → 上下文断裂、章节脱节
- ✅ 单次会话可写完整本书（12章已验证可行）— 前提是 OUTLINE.md 经用户批准、全书叙事一致，且写完后立即更新 BOOK_SUMMARY.md
- ❌ 不要一次性写多章且不更新 BOOK_SUMMARY.md → 上下文断裂
- ❌ 不要跳过 Phase 2 研究 → 没有参考文献支撑的内容缺乏深度
- ❌ 不要跳过 Phase 2 研究 → 没有参考文献支撑的内容缺乏深度
- ❌ 不要跳过 Phase 4 审校 → 术语混乱、引用缺失、排版错漏
- ❌ 不要写了工具（press-draft --research）但不去实际执行 → 研究阶段不是可选项，是必须步骤
- ✅ 一章一次会话，写完立即更新 BOOK_SUMMARY.md
- ✅ 每章先写 refs.md（研究笔记），再写正文
- ✅ 输出前跑一遍审校

### 目录与排版语义
- ❌ 不要在TOC中把前言和正式章节混在一起 → 用户看到"前言"作为第一个条目、然后"第1章"作为第二个条目时，会产生"第2章"的错觉。`generate_toc_html` 必须用 `toc-preface` CSS 类分隔前言类条目，放在列表最前面但独立成组
- ❌ 不要在扉页显示章节编号 → 用户认为同时看到TOC里的"第1章"和扉页上的"第一章"造成困惑。`generate_chapter_opener` 不应输出任何章号文字
- ✅ 要写书之前先规划好结构（封面风格、字体、配色、页码位置）并记入 `references/book-structure-decisions.md`，避免每章写一半再改

### 排版引擎踩坑
- ❌ 不要对 CJK 文字使用 `text-align: justify` → 浏览器强行拉伸中文字间距，产生"字与字之间间隔太大"的效果。CJK 文本应使用 `text-align: left`
- ❌ 不要在章节扉页使用 `min-height: 70vh` 或 `min-height: 100vh` → Chrome打印分页时导致内容重叠。用 `padding` 代替
- ❌ 不要依赖 Paged.js 处理 CSS @page → Paged.js v0.4.3 对 @page margins 的支持不可靠，经常不应用边距导致页眉和正文在页面顶部重叠。正确做法：直接用 Chrome 原生打印引擎，去掉 Paged.js
- ❌ 不要只在 CSS @page 设边距而 Playwright margin=0 → Playwright margins + CSS @page margins 同时设置，形成双保险
- ❌ 不要依赖 CSS 继承链给元素定字号 → 每个元素必须显式声明 `font-size` 和 `line-height`，否则部分元素会退化为浏览器默认字号
- ❌ 不要在 markdown 转换中使用 `nl2br` 扩展 → 多余的 `<br>` 标签破坏排版
- ❌ 不要用 `sane_lists` 扩展（Python-Markdown 中行为不稳定）
- ❌ 不要在 CSS f-string 中漏掉双花括号 → `{ margin: 0; }` 会被 Python 解释为变量引用，必须写成 `{{ margin: 0; }}`
- ❌ 不要把 QR 码作为 inline base64 嵌入 HTML → Chrome print 可能不渲染 inline data URI 图片。改为生成真实 PNG 文件，用相对路径引用
- ❌ 不要让 QR 码单独占一整页 → 二维码区域应该紧凑，和文字并排（左图右文），用一个带边框的分隔线 footer 放在最后一页底部，不要 `break-before: page` 或 `min-height`
- ❌ 不要在 html/body 上设 `background-color` → 配合 `print_background=True` 时每页都有底色块。只在特定页面元素（如封面）设背景色
- ❌ 不要在章节扉页数字上设 `letter-spacing: 0.3em` → 使"第五章"显示为"第 五 章"。控制在 0.08em 以内
- ❌ 不要在扉页显示任何章节编号 → 用户明确要求章节扉页不显示"第一章""第1章"等字样。所有章节（包括前言和正文章节）仅在目录中编号。`generate_chapter_opener` 不应输出任何章节号，只显示标题。`opener-number` CSS 类已废弃
- ❌ 不要让 @top-center 页眉文字离底部太远 → `padding-bottom` 用 0.5mm（不是 2mm），加 `vertical-align: bottom` 让文字靠底部对齐
- ❌ 不要用 Paged.js 的 `string-set` 做 running headers → Chrome 原生 @page 只支持静态 `content` 和 `counter(page)`，不支持 `string()` 运行元素。running header 直接用书名静态文本
- ❌ 不要使用 `@page xxx` 命名页规则 + `content: none` → Chrome 130+ 在命名页过渡时插入空白中间页。修复：**不使用任何 `@page xxx` 命名页规则**，只用默认 `@page`
- ❌ 不要在 `.cover-page` 上同时用 `min-height: 100vh` + `break-after: page` → `min-height: 100vh` 已填满整页，再加 `break-after: page` 会让 Chrome 生成一张空白过渡页。修复：去掉 cover 的 `break-after: page`，保留 `min-height: 100vh` 自然换页
- ❌ 不要用 `@page xxx` 命名页规则 + `content: none` → Chrome 130+ 在命名页过渡时插入空白中间页。修复：**不使用任何 `@page xxx` 命名页规则**，只用默认 `@page`，接受封面和扉页显示书眉和页码。不要用 `page: xxx` CSS 属性，也不要定义任何 `@page xxx` CSS 规则
- ✅ **封面全幅方案**：不用命名页，用负边距 + padding 实现全幅溢出效果：
  ```css
  .cover-page {
      margin: -22mm;
      padding: 22mm; 
      min-height: calc(100vh + 44mm);
  }
  ```
  背景延伸至纸张边缘，内容保持在原内容区域内。封底同理，但 `min-height: 100vh`（不加 44mm，避免 overflow）。
- ✅ **版权页**不要 `break-after: page`，用 `min-height: 100vh` 自然占满一页
- ✅ **封底**要用 `break-before: page` 确保独占一页，但 `min-height` 用 `100vh`（不加额外 margin 补偿）
- ✅ Paged.js 适合需要 running headers、named page strings 的场景，但对 CJK 书籍排版稳定性不足，Chrome 原生打印更可靠
- ✅ Chrome 原生 @page 支持：`size`、`margin`、named pages、`@bottom-center { counter(page) }`、`page-break-before/after/inside`、`target-counter()`、`@media print`
- ✅ 代码块内 `# ` 开头的内容要用 `in_code_block` 状态跟踪过滤，否则被误解析为章节标题
- ✅ 章节 README.md 可能极短（~48字符），但含 `# 第X章` 标记，合并时以 heading 为判断依据不以长度为准
- ✅ pdf 渲染时加 `prefer_css_page_size=True`，等待时间 >5s 让 Chrome 打印引擎处理完毕
- ✅ 一定要用 `page.goto('file:///...')` 而不是 `page.set_content()` 加载 HTML → `set_content()` 从 `about:blank` 运行，Chrome 安全策略会屏蔽 `file://` 图片加载，导致封面头像和封底二维码显示为空白占位符
- ✅ 输出目录需要在 build_book 时就确定，因为 QR 码 PNG 文件需要在 HTML 生成前就写入
- ✅ 封面用圆形头像（sloth-avatar-round.png）居中替代"树懒老K·拙一"文字。默认从 BookSmith-Den assets 复制
- ✅ 封底用 `generate_back_cover_html` 生成，包含圆形头像+名称+二维码+公众号信息，和封面使用相同渐变背景

### 流程踩坑
- ❌ press-draft --init 不创建 SUMMARY.md → merge-book.py 依赖 SUMMARY.md 读取章节列表。初始化后必须手动创建一个 src/SUMMARY.md（或修复 press-draft 自动生成）
- ❌ 写新书时不要迁移旧内容当"重新写" → 用户要的是从0开始完整走一遍流程，不是把旧文件搬过来
- ❌ 重建已有书的 PDF 时，不要擅自换预设/配色 → 必须先用原书的 build 脚本或 output 目录确认原始使用的 `--preset`，或 ask 用户确认
- ❌ 不要用 delegate_task 批量写多章时不验证输出格式 → 子agent 可能输出带行号的内容，导致渲染出错。必须批量写完后检查并清理行号前缀
- ❌ 子agent 写章节时只输出 `## X.1` 格式 → 解析器需要 `# 第X章 标题` 作为章节边界。写完后必须在每个 section-01.md 开头插入 `# 第X章 标题`
- ❌ 不要在子agent任务中使用老旧的 `search_files` 工具调用 → execute_code 内的 read_file 工具返回格式可能变化，优先在终端中运行 Python 脚本
- ✅ 5 Phase 流程已通过真实项目验证从0到PDF的全链路（executive-agent-book）
- ✅ 流程验证要点：Phase 1 初始化→写OUTLINE→Phase 2 搜索参考文献→Phase 3 出大纲确认后写→Phase 4 审校→Phase 5 构建输出

### 内容架构踩坑
- ❌ 不要造轮子而不研究已有技能 → 写书应先解密 lovstudio 看 5 阶段流程，再克隆 BookSmith-Den 学排版架构。两套精华必须学透再动手
- ❌ 不要以为写了"工具"就等于实现了能力 → press-draft --research 写出来了但没实际执行研究，等于没有
- ❌ 不要用 `#` 做粗体或注释 → 在 markdown 转 HTML 后可能被解析为标题。用 `**bold**` 替代
- ✅ lovstudio 的 5 阶段流程中，Phase 2（研究）和 Phase 4（审校）最容易被跳过，恰恰最不能跳

---

## Verification Checklist

- [ ] 前置依赖已安装：`pip install markdown pygments pyyaml playwright qrcode Pillow` + `playwright install chromium`
- [ ] 输入书稿是完整 Markdown，包含 YAML frontmatter（title, author）
- [ ] 书稿以 `# 第X章` 或 `# 前言` 等有效章节标题开头
- [ ] 执行 `press-typeset.py --input manuscript.md --preset mist-blue --output output.pdf` 成功
- [ ] 输出的 PDF 封面有头像、封底有二维码、全书无空白页
- [ ] PDF 书签（章节 outline）正确生成（需 PyMuPDF）
- [ ] 预设选择确认：**必须用 mist-blue（雾霁蓝）**，除非用户明确要求其他
- [ ] 不要用 `publishing-classic` 或其他预设重建已有书的 PDF

---

## 参考

- 已有案例：`ai-agent-handbook`（55,000字，10章46小节，已完成初稿+PDF）
- 已有案例：`knowledge-flywheel-book`（终稿+PDF）
- 封面模版：`cover-templates/`
- BookSmith-Den：`~/Desktop/Sloth-BookSmith-Den/`
- Lovstudio workflow 来源：`uvx lovstudio-skill-helper decrypt write-professional-book`
- 能力审计：`references/capability-audit.md`（完整 lovstudio + BookSmith 差异分析）
- 并行写书参考：`references/parallel-writing.md`（使用 delegate_task 批量写多章）
- CJK 排版要点：`references/cjk-typography.md`（中文 PDF 排版的 CSS 坑与修复）
- Chrome 原生打印方案：`references/chrome-print-cjk.md`（去掉 Paged.js 后的实测要点，含10项关键修复）
- Chrome 空白页根因排查：`references/chrome-print-blank-pages.md`（`@page` 命名规则 + `content: none` 导致 Chrome 插入空白过渡页的完整测试矩阵与修复方案）
