---
name: sloth-press-den
description: 树懒老K写书工坊 v3.3 — 从规划到出版的完整写书流水线。整合 lovstudio 5阶段写作流程 + BookSmith 专业排版架构 + Chrome原生打印引擎 + 自动审校。支持5套专业主题预设（含雾霁蓝）。
version: 3.4.0
author: 树懒老K（拙一）
license: MIT
trigger: 用户说"写书"、"写电子书"、"出书"、"开始写书"、"排版"、"出版"、"出PDF"、"转PDF"、"出书稿"、"整本书"、"畅销书"、"写一本商业书"、"出畅销书"、"技术实操书"、"技术书"、"技术实操手册"、"技术手册"
metadata:
  hermes:
    tags: [writing, publishing, typesetting, pdf, book, cjk, chinese]
    related_skills: [lovstudio-write-professional-book, sloth-deck, html-ppt]
---

# Sloth-Press-Den v3.4 — 树懒老K写书工坊

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

### 前置检查：书稿状态评估（Phase 0）

**每次被问"书写完了吗" / "书到什么程度了" / "写书进度"时，必做这个三步检查，而不是只看一个地方就下结论。**

书稿可能处于以下四种状态之一，检测方法：

| 状态 | 检测方法 | 特征 |
|------|---------|------|
| **0️⃣ 无稿** | 无 Obsidian 无 sloth-books | 只有书名概念，没写过任何字 |
| **1️⃣ Obsidian 写稿** | `ls 01-写作/书稿/<书名>/` | 有 md 文件，但 `sloth-books/` 下无同名项目目录 |
| **2️⃣ 已初始化未构建** | `ls ~/Desktop/sloth-books/<书名>/` + `ls ~/Desktop/sloth-books/<书名>/output/` | 有项目目录但 output 下无 PDF |
| **3️⃣ 已构建** | `ls ~/Desktop/sloth-books/<书名>/output/*.pdf` | 有 PDF 文件 |

**错误模式（已验证）：** 只看 Obsidian 有文件就说"写完了"→ 漏掉构建管线缺失 → 用户追问 PDF 在哪才发现没有。

**正确的回答结构：**
```
初稿写完了（写好的部分：✅ 绪论+第1~9章+附录A/C）
还没完成的部分：❌ 未接入构建管线 / ❌ 未生成PDF / ❌ 未审校 / ❌ 未补参考文献
```

### 状态1→状态2 的接入流程（"事后接入"）

当书稿已在 Obsidian 写完但 sloth-books 下无项目目录时，按以下步骤接入构建管线：

```bash
# 1. 用 --init 在 sloth-books/ 下创建项目
python scripts/press-draft.py \
    --init ~/Desktop/sloth-books/<书名> \
    --title "书名" \
    --author "树懒老K" \
    --subtitle "副标题" \
    --chapters 10

# 2. 创建 appendix 目录（如有附录）
mkdir -p ~/Desktop/sloth-books/<书名>/src/appendix-{a,b,c}

# 3. 从 Obsidian 复制章节文件到构建目录
cp /Users/wangguobao/Documents/Sloth-Old-K/Sloth-Old-K/01-写作/书稿/<书名>/第*.md \
   ~/Desktop/sloth-books/<书名>/src/

# 4. 整理命名：Obsidian 端是"第X章-标题.md"，构建端需要 chapter-XX/section-01.md
# 5. 合并为 merged-manuscript.md
python scripts/merge-book.py ~/Desktop/sloth-books/<书名>

# 6. 构建 PDF
python scripts/press-typeset.py \
    --input ~/Desktop/sloth-books/<书名>/merged-manuscript.md \
    --preset mist-blue \
    --output ~/Desktop/sloth-books/<书名>/output/<书名>.pdf \
    --title "书名" \
    --author "树懒老K"
```

## 完整工作流（5 Phase + 归档）

| 阶段 | 引擎 | 输入 → 输出 |
|------|------|------------|
| **Phase 0: 状态评估** | 见上"前置检查" | 确定书稿当前状态和下一步动作 |
| **Phase 1: 规划** | press-draft --init | 书名/作者 → OUTLINE.md + 目录骨架 + 术语表 |

**Phase 1 要点**：
- 用 `clarify` 工具向用户确认书名、副标题、目标读者、章节数、书籍类型（商业畅销书/技术实操手册/行业白皮书）——不要假设你知道，即使之前讨论过
- **用户说"不限篇幅"时**：不要主动给章节上限。按内容需要定章节数。如果OUTLINE结构合理，10-13章都属于正常范围
- **副标题原则**：副标题应补充主标题未覆盖的信息维度（如领域、方法、交付物），不应是主标题的重复或同义转述。例如主标题是"本体驱动"，副标题"制造业主数据语义化实战"补充了"制造业"+"主数据"+"实战"三个新维度。检查：去掉副标题后，书名是否丢失了关键交付信息？如果是，副标题合格
- **当用户说"参考XX出版社XX作者写的书"时**：在 Phase 1 增加一个额外的步骤——搜索参考书，找到它的目录、核心框架和定位。目的是理解参考书的架构和方法论，作为自己书的对照和差异化参考。用以下方式获取参考书信息：(1)百度搜索书名+作者+目录，(2)Jina Reader读百科/豆瓣/当当页面。不用穷举全书内容，获取目录和核心框架即可
- 如果用户说"从零开始"或"忽略现有材料"，必须用 `--init` 新建目录，绝不能迁移旧内容冒充"重新写"
- **初始化后检查 SUMMARY.md**：`press-draft --init`（v3.2+）已自动生成正确的 SUMMARY.md，路径指向 `section-01.md`。检查确认即可，无需手动修改
- **Phase 1 结束时必须完成**：确认书籍类型 → 填写 OUTLINE.md（章节标题+核心概念+案例）→ 检查 SUMMARY.md → 进入 Phase 2
| **Phase 2: 研究** | 并行搜索（delegate_task） | 章号 → refs.md + references/*.md（学术论文+工业实践+开源工具） |

**Phase 2 要点**：
- 不要只用一条线搜索。用 `delegate_task` 并行跑3条线：
  - **线A: 学术论文** → arXiv + Semantic Scholar。注意：arXiv对"manufacturing+ontology"类搜索噪声极大（基因本体论混淆），优先用 `scripts/search_arxiv.py` 加精确查询词，或直接curl Semantic Scholar API
  - **线B: 工业实践** → Web搜索（企业案例、厂商白皮书、行业报告）。中英文混合搜。重点抓有具体企业名称和项目描述的案例
  - **线C: 开源工具** → GitHub API搜索。重点找社区活跃高、文档完整的项目
- 每条线独立采用delegate_task跑，汇总后存入 `references/` 目录
- **研究素材按用途分类存储**：
  - `references/core-papers.md` — 学术论文摘要+引用
  - `references/industry-cases.md` — 工业实践案例汇总
  - `references/open-source-tools.md` — 开源项目清单
- **arXiv搜索陷阱**：当搜索"manufacturing ontology"时，Gene Ontology项目会淹没结果。解决：①用排除词 `+ANDNOT+all:gene` ②优先走Semantic Scholar（排序更精准）③限cs.AI/cs.DB/cs.SE等工科分类
- **工业实践搜索**推荐用中英文混合关键词：英文"manufacturing ontology ERP semantic interoperability" + 中文"制造业主数据 本体 语义集成 ERP"
- 此阶段不要求穷举，但至少每条线收集6-10个有效结果。够了就进入Phase 3，后续写某章时可再搜
| **Phase 3: 写作** | 逐章写作（一次会话一章或整本一次性，前提是OUTLINE已批准） | OUTLINE.md + BOOK_SUMMARY.md → 章节Markdown |
| **→ Phase 3 校准步骤** | 先出绪论+开头章节看调性，用户确认后再铺全量。触发条件：仅当用户没有明确表达"继续"/"好的"/"开写"等就绪信号时，才问"要不要先出第一章看调性"。如果用户已确认OUTLINE且说了"好的继续"，直接写，不要问 | 避免全书写完大改 → 减少翻车；也避免已经ready时过度提问制造摩擦 |
| **Phase 4: 审校** | press-review --book-dir | 全书 → 术语/引用/排版检查报告 |
| **Phase 5: 构建** | press-pipeline.sh + press-typeset | merged-manuscript.md → PDF/HTML/ePub/MOBI/AZW3 |
| **Phase 5+: 书稿归档** | 见"书稿归档到知识库" | sloth-books/src/ → Obsidian 书稿/ 目录 |

### Phase 5+：书稿归档到知识库

PDF构建完成后，如果用户要求将书稿存档到 Obsidian 知识库，按以下规则执行：

**铁律：**
- **只放 manuscripts**（各章节 .md 文本内容），**不放 build 产物**（PDF、output/、assets/、scripts/）。PDF 已经在 sloth-books/output/ 里，知识库只做源文件备份和链接索引
- **不重复**：先检查知识库 书稿/ 目录下是否已有同名目录
- **结构统一**：

  知识库/书稿/<书名>/
  ├── 全书概览.md        ← sloth-books 的 OUTLINE.md + BOOK_SUMMARY.md 合并精简
  ├── 第1章 <标题>.md     ← 去除 YAML frontmatter 的章节正文
  ├── 第2章 <标题>.md
  └── 延伸阅读索引.md     ← references/ 素材浓缩为 [[]] 链接格式

**归档后做的事**：把 references/ 下的 core-papers.md、industry-cases.md、open-source-tools.md 浓缩为"延伸阅读索引.md"，用 Obsidian `[[]]` 链接格式。

**什么不放**：cover-templates/、scripts/、output/、README.md、.gitkeep、assets/

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
| **封面系统** | 渐变背景 + 品牌Logo（透明PNG，居中） + 标题/副标题/作者 + 底部三QR码（个人网站/微信/公众号）。支持三种风格：gradient（渐变默认）、solid（纯色）、academic（学术细线） |
| **版权页** | 自动生成标准版权页 |
| **目录** | 自动生成可点击目录，H2 子章节自动收录 |
| **章节扉页** | 独立扉页 + 中文章号 + 题记支持（`> "引文" —— 出处`） |
| **正文排版** | 首行缩进、行距按字号动态计算、CJK 左对齐（避免字间拉伸） |
| **代码高亮** | Pygments 语法高亮，fenced code 块，monospace 对齐 |
| **表格** | 三线表风格 + 自动编号（表X-Y）+ 斑马纹 |
| **图片** | 自动居中 + 图注编号（图X-Y）；自动约束 `max-height: 150mm` + `object-fit: contain`，防止高 SVG 跨页截断 |
| **侧边栏/callout** | blockquote 内 `**标题:** 内容` 自动转为 styled aside |
| **交叉引用** | `参见/参阅/参考/见 第X章` 自动转为可点击链接 |
| **水印** | CLI 参数注入全页水印 |
| **二维码** | 封面+封底三码横排：个人网站QR + 个人微信QR + 公众号QR，每码带文字标签。自动检测章节尾 `配套资源` 侧边栏，注入公众号二维码（`process_body_html()` 中的侧边栏QR逻辑） |
| **PDF 书签** | 章节级 PDF outline + 子章节书签（需 PyMuPDF） |
| **多格式输出** | PDF（Chrome原生分页）+ HTML + ePub + MOBI + AZW3（需 Calibre） |
| **mermaid 图表** | 支持 ` ```mermaid ` 代码块渲染流程图/架构图（mermaid.js CDN 加载，PDF 渲染等待 10s） |

### 页面架构（三区模型）

PDF 页面分为三个区域，由不同的 CSS `@page` 规则控制：

| 区域 | 页面 | 命名页 | 边距 | 页眉/页码 | 说明 |
|------|------|--------|------|----------|------|
| **Zone 1** | 封面、版权页、封底 | `page: cover`（**相同**命名页） | `margin: 0` | 无 | 封面全幅；版权页需额外加 `padding`；三者同名避免 Chrome 插空白过渡页 |
| **Zone 2** | 目录、正文、附录 | 默认 `@page` | `22mm` | 有 | 标准书眉排版 |

**铁律：** Zone 1 的三个页面必须**全部**使用 `page: cover`（同一个命名页名）。如果封面单独用 `page: cover` 而版权页不用，Chrome 会在它们之间插入空白过渡页。如果封底用别的命名页，同理。

**Playwright 配置：** `page.pdf()` 的 `margin` 参数必须全设 `0mm`，否则叠加到 CSS `@page` 之上产生无法覆盖的白色边框。

详细排查过程见 `references/chrome-print-blank-pages.md`。

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

## 商业畅销书内容策略（Phase 1 进阶）

当用户写的是**商业畅销书**（付费出版、书店/电商销售、面向高管/决策者群体）而非引流电子书或行业研究报告时，Phase 1 规划阶段必须额外完成以下策略工作。

**核心差异对照：**

| 维度 | 引流电子书 | 行业研究报告 | 商业畅销书 |
|------|-----------|------------|-----------|
| 目的 | 让读者想找你聊 | 建立专业权威 | 让读者想买、想看、想传播 |
| 定价 | 免费 | 免费/收费 | 收费出版 |
| 读者 | 潜在客户 | 同行业者 | 决策层+执行层 |
| 传播引擎 | 案例有用性 | 数据权威性 | **叙事张力+可带走的谈资** |

### 1. 多角色视角采集法

在确定书名、副标题和章结构前，必须依次模拟以下角色视角审视书的概念：

| 角色 | 核心关切 | 一句话判断标准 |
|------|---------|--------------|
| **内容专家** | 框架完整吗？认知有推进吗？ | 跟市面已有的书比，差在哪？好在哪？ |
| **骨灰级读者** | 书名让我想拿起来吗？第一章让我想买吗？ | 我每年花几千买书，这本值得吗？ |
| **企业老板** | 30秒内觉得事关身家吗？有我能带走的话吗？ | 前三页让我觉得不看就落后了吗？ |
| **企业高管** | 有我能直接用的方案/模板/话术吗？ | 读完我能搞定老板和团队吗？ |

**方法**：逐角色提问→收集冲突点（比如老板在意ROI、高管在意中层角色、读者在意叙事）→在结构上设计同时满足多角色的章节形态。

**核心产出**：书名（要有矛盾张力）+ 副标题（点明核心命题）+ 陪练企业（贯穿全书的案例）+ 叙事主线（全书张力线）

### 2. 书名定调原则

畅销书书名不是「描述性的」，是「制造好奇的」。衡量标准：

- 读者在书店/电商看到书名，会不会想**拿起来翻**？
- 翻完之后有没有一个**让人想搞明白的矛盾**？
- 书名如果只能被行业内的专家看懂 = 不够好

三种书名类型由强到弱：
```
强：书名有矛盾张力，让人想翻开 → 《Token账本》
中：书名定义新概念，有品牌化潜力 → 《Agent型组织》
弱：书名描述内容，和信息稿标题一样 → 《企业AI转型变革文化建设》
```

### 3. 双受众章节结构设计

畅销书通常服务两种读者（决策者+执行者），不能在阅读体验上舍弃任何一方。

**标准化结构（每章）：**

```
【300字决策者摘要】 → 给高管5分钟掌握要点
    ↓
【正文（6-8小节）】 → 以中层/执行者为主要视角展开
    ↓
【本章小结（5条核心观点）】 → 两方都能带走
    ↓
【📚 延伸阅读（外2内1）】 → 2个外部经典 + 1个作者专题
    ↓
【落地工具】 → 清单/模板/路线图，可带走
```

**硬约束**：全书的极限是10章。超过10章大概率在注水。

### 4. 叙事张力设计

畅销书区别于教科书的核心：**有一根贯穿全书的叙事线**，制造「想知道答案」的阅读动力。

**经典设计模式**：
- 第一章抛出问题/矛盾/悬念（如「一个2000人的企业，全员AI Agent一年烧XXX万——你愿意花吗？」）
- 中间各章每章给一部分答案，同时铺新问题
- 最后一章关上悬念，首尾呼应

这个「悬疑→拆解→收束」的结构让读者有翻页的冲动，而不是把书当字典翻。

### 5. 品牌软性植入三层法

商业畅销书的品牌植入不能是硬广，必须是读者觉得「增值」的赠品式植入。

| 层次 | 位置 | 形式 | 密度控制 |
|------|------|------|---------|
| **第一层：正文见证演示** | 章节正文 | 「在某项目中使用了一套名为XX的工具」自然带出 | 每章≤1处 |
| **第二层：章末延伸阅读** | 每章末尾 | 外2内1结构（2个外部经典+1个作者专题） | 1/3比例 |
| **第三层：附录资源索引** | 书末附录 | 配套资源获取方式，通过公众号回复关键词 | 全书收官 |

**关键原则**：读者不是在「被引流」，而是在「兑现买书时已经付了费的价值」。

### 6. 参考文献分层体系

畅销书的参考文献要同时服务于「不想被打断的读者」和「较真的研究者」：

| 层次 | 位置 | 内容 | 给谁用 |
|------|------|------|--------|
| **第一层：章末延伸阅读** | 每章末尾，3-4条 | 精选商业经典，一句话推荐 | 只想跟着书读的读者 |
| **第二层：正文脚注** | 数据/观点结尾处上标 | 来源出处，简短 | 想验证数据的读者 |
| **第三层：书末参考文献索引** | 全书末，按章分类 | 完整文献（报告/论文/书籍/文章） | 想深挖的研究者/咨询人士 |

**参考文献选材原则**：
- 研报为主，论文为辅（7:3比例）
- 中文文献至少占30%
- 近三年时效性为主
- 每章8-15条，全书80-150条

### 7. 封面封底设计策略（v3.4）

**核心变更（v3.4）**：封面+封底均放置三QR码横排，Logo替换旧版圆形头像。

| 位置 | 设计元素 | 说明 |
|------|---------|------|
| **封面** | 品牌Logo（透明PNG）+ 书名 + 副标题 + 作者 + 底部三QR码 | QR码横排于底部，从左到右：个人网站 / 个人微信 / 公众号 |
| **封底** | 品牌Logo + 作者信息 + 三QR码横排 + 标语 | QR码从左到右：个人网站 / 个人微信 / 公众号，每码带文字标签 |

**QR码图片规格**：所有QR码为PNG。封面Logo（logo-transparent.png）建议200px，封底Logo（logo-transparent-large.png）建议250px。原sloth-avatar-round.png和qrcode.jpg不再使用。

### 8. 陪练企业案例设计

畅销书需要一个贯穿全书的主案例（「陪练企业」）——读者通过跟进这个案例的全程来理解方法论。

**设计要点**：
- 可以是真实案例（脱敏后使用）或基于多个案例的合成
- 在第一章引入，之后每章跟进它的进展
- 合成案例必须标注「基于多个真实案例改编」
- 案例中必须有「中间差点放弃了」的真实情节

**案例质量检测标准**：读者读完会说「对对对，我们公司也是这样」——如果做不到，案例就是编的。

### 9. 写作工作流选项

sloth-press-den 支持两种写作工作流，根据用户的知识管理习惯选择：

| 选项 | 流程 | 适合场景 |
|------|------|---------|
| **方案A：直写模式** | sloth-books/src/ 中直接写 → press-typeset → PDF | 专注快速出书，不需与其他知识库关联 |
| **方案B：双目录模式** | 在 Obsidian/其他笔记系统写 → 同步脚本 → sloth-books/ → build | 用户有自己的知识资产体系，书稿需要可搜索、可关联 |

#### 方案B 实现方式

```
写稿 → Obsidian/01-写作/书名/章节/第X章.md
  ↓ 同步脚本
  ↓
sloth-books/书名/src/chapter-XX/section-01.md
  ↓ build-pdf.sh
  ↓
sloth-books/书名/output/书名.pdf
```

**同步脚本设计要点：**
- 用 `ls | grep "^第${num}章"` 匹配 Obsidian 端的中文文件命名
- 复写前备份已有 `section-01.md` 为 `.bak`
- 支持单章同步（`sync.sh 3`）和全量同步（`sync.sh`）
- 同步完成后提示构建命令

参考模板：`templates/sync-to-build.sh`（根据用户实际的 Obsidian vault 路径调整）

#### 附录管理

`press-draft --init` 默认只创建 10 个 `chapter-XX` 目录。如果书有附录（A-F），需手动创建 `src/appendix-a/` 至 `src/appendix-f/` 目录，并在 `SUMMARY.md` 中添加附录链接。附录同样遵循标准书稿结构规范。

### 10. Phase 1 商业畅销书检查清单

在完成标准 `press-draft --init` 之后，额外检查：

- [ ] 已执行多角色视角采集（至少覆盖骨灰读者+老板+高管三个角色）
- [ ] 书名有矛盾张力，能在3秒内让读者想拿起来
- [ ] 副标题点明了核心命题，补充了书名的信息缺口
- [ ] 第一章以具体冲突场景（不是概念介绍）开头
- [ ] 设计了贯穿全书的叙事主线/悬念线
- [ ] 陪练企业已确定，每章都有它的进展
- [ ] 有专门的一章讲失败案例
- [ ] 每章有「可带走的东西」（清单/模板/话术）
- [ ] 品牌植入设计了三层体系（见证演示/延伸阅读/附录）
- [ ] 参考文献按三层分层体系设计
- [ ] 封面=网站QR码，封底=公众号QR码
- [ ] 全书极限10章，不注水

详细示例见 `references/commercial-bestseller-outline-example.md`（包含完整10章大纲+书名策略+品牌植入方案）。

---

## 技术实操手册内容策略（Phase 1 进阶）

当用户写的是**技术实操手册**（方法论+案例+可复用的框架，面向技术人群/架构师/实施顾问）而非商业畅销书或白皮书时，Phase 1 规划阶段的策略与畅销书不同。

**核心差异对照（扩展版）：**

| 维度 | 引流电子书 | 行业研究报告 | 商业畅销书 | **技术实操手册** |
|------|-----------|------------|-----------|----------------|
| 目的 | 让读者想找你聊 | 建立专业权威 | 让读者想买、想看、想传播 | **让读者能上手落地** |
| 读者 | 潜在客户 | 同行业者 | 决策层+执行层 | **实施顾问/架构师/技术型CIO** |
| 核心交付 | 案例有用性 | 数据权威性 | 叙事张力+谈资 | **可复用的方法论框架+参考模型** |
| 案例策略 | 一两个亮眼故事 | 行业标杆 | 贯穿全书的陪练企业 | **每章独立聚焦案例，脱敏/合成** |
| 章节上限 | 5-8章 | 10-15章 | 10章 | **12章（含绪论+展望）** |
| 品牌植入 | 附录引流 | 致谢页 | 三层植入法 | **章末延伸阅读+配套资源索引** |

### 1. 副标题设计原则

与技术书相比，畅销书的副标题可以天马行空；技术书的副标题要**精确描述交付物**。

**好 vs 不好的例子：**

```
❌ 《本体驱动：制造业的语义革命》
    → 表述是对的，但读者不知道这本书能给他什么

✅ 《本体驱动：制造业主数据语义化实战》
    → 三个关键词"制造业"+"主数据"+"实战"各自补全了书名的信息缺口
```

**检查标准（两个测试）**：
1. **信息缺口测试** — 目标读者（如ERP实施顾问）看到副标题后，能否3秒内判断"这跟我的工作有关"？如果不能，信息浓度不够
2. **同义转述测试** — 去掉副标题后，书名是否丢失了关键交付信息？如果副标题只是把书名换了个说法重新讲一遍（"本体驱动"→"用本体论驱动"），说明它在同义转述而不是补充新信息。不合格的副标题特征：核心名词与书名高度重叠、动词相同或同义

### 2. 章节结构设计原则

技术实操手册的标准结构是**四篇制**：问题→方法论→实践→展望。每篇的章节数和功能如下：

| 篇 | 章节数 | 功能 |
|------|--------|------|
| **上篇：问题与框架** | 3章 | 建立"为什么需要这个方法论"的认知基础 |
| **中篇：方法论** | 4章 | 核心交付——可复用的建模/实施方法论 |
| **下篇：实践** | 3章 | 落地验证——路线图+案例+组织和团队 |
| **终篇：展望** | 1-2章 | 趋势判断+开放问题 |

**每章标准模板（技术书版）：**

```markdown
## 章节标题
> 章首题记（可选）

### [核心场景/问题导入]
一个具体场景切入，让读者先看到"这是我能用到的"

### [方法论/框架主体]
核心内容。包括：
- 步骤化方法（第x步，第y步）
- 可操作性强的模型/框架
- 关键转折点/决策点

### [案例/示例]
每章一个独立聚焦的案例，不追求"陪练企业"式贯穿全书

### 本章小结
- 3-5条核心观点，读者可直接带走
- 📚 延伸阅读（可选）
```

### 3. 案例策略：实事求是

**铁律**（从本次会话翻车预判中提炼）：

- 不确定能拿到的案例，**不要承诺**。用"估计能找到"/"大概率能找到"这类措辞时，先想清楚如果找不到怎么办
- **优先用真实案例**（企业名称脱敏）→ **其次用合成案例**（基于多个真实场景改编，标注"基于多个行业实践改编"）→ **不要编造**
- **合成案例也要有真实内核**：要么是作者实操过的，要么是基于多个公开案例综合的。纯凭想象写出来的案例，业内人士一眼就能看出来
- 每个案例附一个**检测标准**：读者读完会不会说"对对对，我们也是这样"。如果不会，案例就是编的
- 第1章的导入案例可以来自公开报道/论文（标注来源），后续方法论章节的案例尽量是作者可溯源的真实经历

### 4. 研究优先级

技术书的参考文献与研究优先级与畅销书不同：

| 优先级 | 来源 | 原因 |
|--------|------|------|
| **P0** | 学术论文（arXiv/Semantic Scholar） | 本体论/语义建模需要理论根基，论文提供可引用的方法论框架 |
| **P1** | 开源项目（GitHub） | 技术读者关注：有没有开源实现？有没有参考代码？ |
| **P2** | 厂商白皮书/技术文档 | SAP、西门子、OPC UA等厂商的公开文档提供工业实践参考 |
| **P3** | 行业报告（公开摘要） | Gartner/IDC等提供趋势数据，但付费墙后的完整报告无需强求 |

### 5. 技术书的"调性校准"

技术实操手册比畅销书更依赖**Phase 3 校准步骤**——因为技术内容一旦写错，读者信任就碎了。

**校准方法**：
- 先写第1章（导入场景+全书框架）+ 第4章（方法论核心章节）作为样板
- 用户确认：①技术判断有无错误 ②调性是否偏了（太学术？太销售？） ③案例是否让人信服
- 确认后再铺后面所有章节

### 6. Phase 1 技术实操手册检查清单

- [ ] 副标题补充了书名未覆盖的信息维度（领域+方法+交付），不是同义转述
- [ ] 全书结构为上中下终四篇制
- [ ] 第1章以具体业务冲突场景（不是概念介绍）开头
- [ ] 每章有独立案例，不依赖"陪练企业"模式
- [ ] 案例策略明确：真实（脱敏）/合成（标注来源），不是编造
- [ ] 不确定的案例已经计划了备选方案（合成/通用场景）
- [ ] 参考文献优先级：论文>开源>厂商文档>行业报告
- [ ] 计划了调性校准步骤（先出第1章+方法论核心章节给用户看）
- [ ] 全书12章为上限（含绪论+展望），不注水

详细示例见 `references/technical-book-outline-example.md`（包含完整12章大纲+案例策略+研究计划，基于《本体驱动：制造业主数据语义化实战》的实战生成）。

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

### 标准化章节模板

每章统一使用以下结构（适用于商业畅销书，已在多本书稿中验证）：

- `# 标题` — 章标题（每章以 `# ` 开头）
- `## 标题` — 子章节（自动生成目录二级条目）
- `> "内容" —— 来源` — 章首题记
- `---` 前 YAML frontmatter — 元数据（title, author, date）
- `![alt](path)` — 自动编号 + 图注
- Markdown 表格 — 自动编号 + 三线表样式
- `[^1]` 脚注 — 自动渲染

### 学术方法论（提升权威性）

当需要提升文章/书稿的学术严谨性时，按以下优先级执行：

| 优先级 | 行动 | 应用场景 |
|--------|------|---------|
| **P0** | 统一引用格式（作者/来源/日期/链接，区分原文vs判断） | 所有文章和书稿 |
| **P1** | 推理透明化：关键判断处加入"这说明…"、"这意味着…"让读者看到推理链 | 文章和书稿正文 |
| **P2** | 每章末尾加「争议与讨论」一节，主动引述并回应反方观点 | 书稿每章 |
| **P3** | 用 arxiv 搜相关论文作学术佐证 | 需要理论根基时 |

**争议与讨论节标准模板：**
```markdown
## 争议与讨论

本章的核心主张——「……」——在学术界和工业界都有不同声音。

**争议一：标题**
[反方观点概述，引用论文或报告出处]

我的回应：[给出反驳或条件性认同，附学术佐证]

**争议二：标题**
同上模式。

**有待进一步观察的方向：**
- 方向1：暂未定论但值得持续追踪的问题
- 方向2：同上
```

**引用规范：**
- 首次引用时标注：`（Source: Author, "Title", Date, URL）`
- 仅在第一次出现时标注，不重复标注
- 区分"原文观点" vs "树懒老K的判断/回应/验证"
- 全文中所有代表作者本人的发声，统一标注为"**树懒老K：**"，不用"我的判断""我的回应""我的看法"
- 论文引用格式：`Author 等，Year，arXiv:XXXX.XXXXX`

**已验证的高相关论文（可直接引用）：**
- Edwards 等，2026，arXiv:2604.09633 — Agentic AI in Engineering and Manufacturing（30+企业访谈，制造业AI瓶颈研究）
- Srinivasan，2026，arXiv:2604.20158 — Stateless Decision Memory for Enterprise AI Agents（企业Agent部署设计约束）

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
✅ 单次会话可写完整本书（12-13章已验证可行）— 前提是 OUTLINE.md 经用户批准、全书叙事一致、且写完后立即更新 BOOK_SUMMARY.md
- ❌ 不要一次性写多章且不更新 BOOK_SUMMARY.md → 上下文断裂  
*但整书一揽子写作是可行的：12-13章（最长达89,000字+）已验证 —前提是 OUTLINE.md 经用户批准、全书叙事框架一致、写完后立即更新 BOOK_SUMMARY.md*
- ❌ 不要跳过 Phase 4 审校 → 术语混乱、引用缺失、排版错漏
- ❌ 不要写了工具（press-draft --research）但不去实际执行 → 研究阶段不是可选项，是必须步骤
- ❌ 书稿入库时检查路径 → 先确认目标实际路径，不要放错层级再迁移
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
- ❌ **CRITICAL: 不要在 `page.pdf()` 中设置非零 margins** → Playwright 的 `margin` 参数会叠加到 CSS `@page` 边距之上，产生无法覆盖的白色边框。封面全幅失效的根因之一。必须设为 `0mm`，由 CSS 全权控制所有边距。代码中此处为 `generate_pdf()` 函数的 `page.pdf(margin={...})` 调用
- ❌ 不要试图用负边距 + overflow 技巧实现封面全幅 → Chrome PDF 渲染引擎会在 `@page` 边距边界处裁剪内容，不受 CSS overflow 或负边距影响。负边距 `margin: -22mm` + `padding: 22mm` 在屏幕上可能有效，在 PDF 输出中不起作用。已验证过的时间黑洞，不要重复踩坑
- ❌ **CRITICAL: 不要单独给封面用 `@page cover` 命名页** → Chrome 130+ 在不同命名页之间插入空白过渡页。但 **封面、版权页、封底共用同一个命名页时不会产生空白页**。这是唯一安全的命名页使用方式
- ❌ 不要在 CSS f-string 中漏掉双花括号 → `{ margin: 0; }` 会被 Python 解释为变量引用，必须写成 `{{ margin: 0; }}`

  **封面全幅 + 零空白页的最优方案（经三轮完整测试迭代验证）：**
  ```css
  /* 封面/版权/封底共用同一个命名页 → 无空白过渡页 */
  @page cover { margin: 0; @top-center { content: none; } @bottom-center { content: none; } }
  
  .cover-page  { page: cover; min-height: 100vh; ... }
  .copyright-page { page: cover; padding: 22mm; min-height: 100vh; ... } /* 加padding恢复边距 */
  .back-cover  { page: cover; break-before: page; min-height: 100vh; ... }
  ```
  三个关键约束：
  1. **封面、版权页、封底三者都必须用 `page: cover`**（同名）→ 无空白过渡页
  2. **版权页必须显式加 `padding`**（因为 `page: cover` 的 margin 为 0，内容会跑到边缘）
  3. **Playwright 的 `page.pdf()` 必须设 `margin={"top":"0mm",...}`**（CSS 全权控制边距）
  其他内容页用默认 `@page`（保持预设的 22mm 边距，有页眉和页码）

- ❌ 不要只在 CSS @page 设边距而 Playwright margin=0 → Playwright margins 和 CSS @page margins 是叠加关系，不是覆盖关系。设了非零 Playwright margin = 封面永远有白边
- ❌ 不要依赖 CSS 继承链给元素定字号 → 每个元素必须显式声明 `font-size` 和 `line-height`，否则部分元素会退化为浏览器默认字号
- ❌ 不要在 markdown 转换中使用 `nl2br` 扩展 → 多余的 `<br>` 标签破坏排版
- ❌ 不要用 `sane_lists` 扩展（Python-Markdown 中行为不稳定）
- ❌ 不要把 QR 码作为 inline base64 嵌入 HTML → Chrome print 可能不渲染 inline data URI 图片。改为生成真实 PNG 文件，用相对路径引用
- ❌ 不要让 QR 码单独占一整页 → 二维码区域应该紧凑，和文字并排（左图右文），用一个带边框的分隔线 footer 放在最后一页底部，不要 `break-before: page` 或 `min-height`
- ❌ 不要在 html/body 上设 `background-color` → 配合 `print_background=True` 时每页都有底色块。只在特定页面元素（如封面）设背景色
- ❌ 不要在章节扉页数字上设 `letter-spacing: 0.3em` → 使"第五章"显示为"第 五 章"。控制在 0.08em 以内
- ❌ 不要在扉页显示任何章节编号 → 用户明确要求章节扉页不显示"第一章""第1章"等字样。所有章节（包括前言和正文章节）仅在目录中编号。`generate_chapter_opener` 不应输出任何章节号，只显示标题。`opener-number` CSS 类已废弃
- ❌ 不要让 @top-center 页眉文字离底部太远 → `padding-bottom` 用 0.5mm（不是 2mm），加 `vertical-align: bottom` 让文字靠底部对齐
-  ❌ 不要用 Paged.js 的 `string-set` 做 running headers → Chrome 原生 @page 只支持静态 `content` 和 `counter(page)`，不支持 `string()` 运行元素。running header 直接用书名静态文本

### press-typeset.py 配置铁律（每次新建/修改时必读）

以下三条同时满足才能输出**封面全幅 + 零空白页**的PDF。缺少任何一条都会出问题。

1. **@page 命名页铁律**：封面、版权页、封底**全部使用同一个命名页** `page: cover`。封面单独用 = 产生空白过渡页。版权页不用 = 封面到版权页之间有空白页。封底用不同命名页 = 同样产生空白页。检查 `press-typeset.py` 中 CSS 确保 `.cover-page`、`.copyright-page`、`.back-cover` 三者都声明 `page: cover;`。
2. **Playwright margin 铁律**：`page.pdf()` 的 `margin` 参数**必须全设 `0mm`**。任何非零值会叠加在 CSS `@page` 边距之上，产生不可覆盖的白色边框。检查代码中 `generate_pdf()` 函数的 `page.pdf(margin={...})` 调用。
3. **图片加载铁律**：必须用 `page.goto('file:///...')` 加载 HTML，不能用 `page.set_content()`。后者从 `about:blank` 运行，Chrome 安全策略会拦截 `file://` 图片请求，导致封面头像和封底二维码显示为空白占位符。

- ✅ Paged.js 适合需要 running headers、named page strings 的场景，但对 CJK 书籍排版稳定性不足，Chrome 原生打印更可靠
- ✅ Chrome 原生 @page 支持：`size`、`margin`、named pages、`@bottom-center { counter(page) }`、`page-break-before/after/inside`、`target-counter()`、`@media print`
- ✅ 代码块内 `# ` 开头的内容要用 `in_code_block` 状态跟踪过滤，否则被误解析为章节标题
- ✅ 章节 README.md 可能极短（~48字符），但含 `# 第X章` 标记，合并时以 heading 为判断依据不以长度为准
- ❌ **CRITICAL: 不要遗漏 SVG/图片资产复制 → 构建出的 PDF 图片空白或缺失**。`press-typeset.py` 将 HTML 写入 `output/_temp_book.html`，但 Markdown 中的 `![alt](assets/ch*.svg)` 图片路径是相对于书稿目录的。浏览器加载 HTML 时解析为 `output/assets/*.svg`——该目录不存在。**标准修复**：构建前将 `assets/*.svg` 复制到 `output/assets/`。在 `build-pdf.sh` 中必须包含：
  ```bash
  mkdir -p output/assets
  cp assets/ch0*.svg output/assets/ 2>/dev/null
  cp assets/*.png output/assets/ 2>/dev/null
  ```
  同样的原理也适用于封面头像、QR码等——`_ensure_asset()` 函数已处理这些，但书稿正文中 `![]()` 引用的图片需要手动复制。**事后诊断法**：如果 PDF 图片缺失，直接检查 `output/assets/` 目录是否存在且包含所有被引用的图片文件。
- ❌ **Markdown 图片+图注被合并到同一个 `<p>` 中，导致图片处理正则失效** → Python-Markdown 的默认行为是：连续两行的 `![alt](src)` 和 `*caption*` 会被解析为同一个段落。输出的 HTML 为 `<p><img src="..."/><em>caption</em></p>`，而不是两个独立的 `<p>`。`press-typeset.py` 中 `replace_img_figure()` 的旧正则 `r'<p>\\s*<img[^>]+/?>\\s*</p>'` 因此永远匹配不上，图片不会被包裹进 `<figure>`，也不会应用 `max-height` 约束。**标准修复**：使用 `r'<p>\\s*(<img[^>]+/>)\\s*(?:<em>([^<]*)</em>)?\\s*</p>'`，捕获 `<em>` 内容作为 `<figcaption>`，已在 `press-typeset.py` 中修复。**如果图注不是用斜体 `*` 而是用其他方式标记，也可能被合并进 `<p>` — 检查 HTML 输出确认 `<img>` 和周围内容的 DOM 结构。**
- ✅ pdf 渲染时加 `prefer_css_page_size=True`，等待时间 >5s 让 Chrome 打印引擎处理完毕
- ✅ 一定要用 `page.goto('file:///...')` 而不是 `page.set_content()` 加载 HTML → `set_content()` 从 `about:blank` 运行，Chrome 安全策略会屏蔽 `file://` 图片加载，导致封面头像和封底二维码显示为空白占位符
- ✅ 输出目录需要在 build_book 时就确定，因为 QR 码 PNG 文件需要在 HTML 生成前就写入
- ✅ 封面用品牌Logo（logo-transparent.png）居中，底部三QR码横排（website_qr/wechat_qr/gongzhonghao_qr）。默认从 skill assets 复制
- ✅ 封底用 `generate_back_cover_html` 生成，包含品牌Logo+名称+三QR码横排，和封面使用相同渐变背景

### 内容创作踩坑

- ❌ **副标题设计** → 副标题不应是书名的同义转述或部分重复。好的副标题补充主线未覆盖的信息维度（交付物/领域/方法）。例如书名含"本体"和"AI"时，副标题应补充"对谁/什么场景/解决什么问题"。检查方法：去掉副标题后书名是否丢失关键信息？如果是，副标题合格
- ❌ **书稿入库时检查路径** → 将书籍迁移到Obsidian知识库时，先确认目标目录的实际路径（如`01-写作/书稿/`），不要假设是根级目录。写错层级再迁移浪费时间和算力
- ❌ **不要在初稿中给关键数字写死**
- ✅ **先出开头校准调性**：写整本书前，先写绪论+第1章给用户看调性。用户点头再铺后面。这比全书写完再大改省10倍返工量。用户偏好是"一次做对"。
- ✅ **书内引流统一指向一个入口**：不要分散到多个二维码/链接。统一指向个人网站（非GitHub、非多个端点）。读者只需要记住一个地址。
- ✅ **流程图三级交付体系**：技术/流程类书籍用三级图体系——L1概览对比图（≤8节点Before/After对比）、L2泳道流程图（Mermaid swimlane展示岗位/系统分工）、L3节点详细设计表（结构化表格，含输入/输出/AI介入/异常处理）。每章配L1×2 + L2×1 + L3×1（按需）
- ❌ 不要在初稿中给关键数字（如Token成本XXX万）直接写死 → 用户可能想最后统一校准。用 `XXX万` 或 `YYY元` 等显式占位符代替，并在写作结束时问用户是否需要统一替换。**用户偏好模式：** 写完后说"最后你自己统一校准"——意味着信任你对数字的感知，但需要最终确认。
- ❌ **不要对案例可用性做过度承诺** → 当用户问"你确定能找到么？"，不要用"估计能找到"/"大概率能找到"这类模糊措辞。直接说清楚：①能找到什么（公开论文/厂商白皮书/开源项目）②什么找不到（内部实施细节/机密数据）③替代方案是什么（合成案例）。用户要的是诚实评估，不是轻率承诺。
- ✅ 每写一章立即更新 BOOK_SUMMARY.md（500字以内压缩摘要）和 glossary.md（新术语）→ 跨章节上下文保持一致
- ✅ 每章写完后立即同步到 sloth-books/ 构建目录 → 避免会话结束时才集中同步导致的文件遗漏
- ✅ 使用 todo 工具跟踪多章节进度 → 在长时间写书会话中，用 `todo` 工具管理已写/待写章节比纯记忆可靠

### 流程踩坑
- ✅ 注：v3.2+ 的 press-draft.py 已自动生成 SUMMARY.md，且路径指向 `section-01.md`（不是 `README.md` 占位符）。初始化后检查一下即可，不需要手动创建
- ✅ merge-book.py 处理缺失的 foreword.md/前言文件 gracefully：跳过并给出 ⚠️ 警告，不会中断合并。纯技术/研究类书籍没有前言时，这个警告可以放心忽略
- ❌ 写新书时不要迁移旧内容当"重新写" → 用户要的是从0开始完整走一遍流程，不是把旧文件搬过来
- ❌ 重建已有书的 PDF 时，不要擅自换预设/配色 → 必须先用原书的 build 脚本或 output 目录确认原始使用的 `--preset`，或 ask 用户确认
- ❌ **回答"写完了吗"时，必须检查双目录** → 只看 Obsidian `01-写作/书稿/` 的文件就下结论，会漏掉构建管线状态。必须再查 `~/Desktop/sloth-books/` 确认是否有同名项目目录和 output/PDF。两者独立，少查一个就翻车
- ❌ **delegate_task 写作超时的恢复** → 当并行写作超过600s超时时，不要重发整批任务。先检查每个章节文件的实际状态（`ls chapter-*/section-01.md`），只补写缺失的章节。重写全量 = 浪费Token和时间。如果只有2-3章缺失，直接自己写，不要再派agent
- ❌ **PDF构建时注意Python环境** → Hermes venv的python3可能缺少playwright/chromium。构建PDF前先检查：`which python3 && python3 -c "import playwright"`。如果失败，用 `/usr/bin/python3` 替代——系统Python通常预装了playwright和chromium。同理，检查qrcode模块是否存在
- ❌ **子agent 写章节时只输出 `## X.1` 格式** → 解析器需要 `# 第X章 标题` 作为章节边界。写完后必须在每个 section-01.md 开头插入 `# 第X章 标题`
- ❌ **不要在子agent任务中使用老旧的 `search_files` 工具调用** → execute_code 内的 read_file 工具返回格式可能变化，优先在终端中运行 Python 脚本
- ❌ **press-typeset.py 的 Python 环境问题** → Hermes venv 的 python3 (3.11.15) 可能缺少 playwright/qrcode。如果遇到 `ModuleNotFoundError: No module named 'playwright'`，先尝试 `/usr/bin/python3`（系统Python），再尝试 `pip3 install playwright qrcode -i https://pypi.tuna.tsinghua.edu.cn/simple`。如果 Chromium 不存在（`Executable doesn't exist at ...`），需运行 `playwright install chromium`（下载约20分钟）
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
- [ ] `press-draft --init` 是否自动生成了 src/SUMMARY.md？章节链接是否指向 `section-01.md`（非 `README.md` 占位符）？—— v3.2+ 已自动做对，但检查一下保险
- [ ] 输入书稿是完整 Markdown，包含 YAML frontmatter（title, author）
- [ ] 书稿以 `# 第X章` 或 `# 前言` 等有效章节标题开头
- [ ] **press-typeset.py 三铁律检查**：
  - [ ] `.cover-page`、`.copyright-page`、`.back-cover` 三者都声明 `page: cover;`
  - [ ] `page.pdf()` 的 `margin` 参数全设为 `"0mm"`
  - [ ] 使用 `page.goto('file:///...')` 而非 `page.set_content()`
- [ ] 执行 `press-typeset.py --input manuscript.md --preset mist-blue --output output.pdf` 成功
- [ ] 输出的 PDF 封面全幅（四角无白边——原理见"页面架构三区模型"）
- [ ] 封面有品牌Logo（透明PNG）+ 底部三QR码（个人网站/微信/公众号） ✅
- [ ] 封底有三QR码横排（个人网站/微信/公众号） ✅
- [ ] 全书扫描：逐页检查无空白页（封面→版权→目录→正文→封底，页与页之间连续）
- [ ] 目录页（目 录）在版权页之后、第1章之前，且不是空白页
- [ ] PDF 书签（章节 outline）正确生成（需 PyMuPDF）
- [ ] 预设选择确认：**必须用 mist-blue（雾霁蓝）**，除非用户明确要求其他
- [ ] 书稿中 `![]()` 引用的图片（SVG/PNG）已复制到 `output/assets/`（构建脚本中应包含 `cp assets/*.svg output/assets/`） ✅
- [ ] 高 SVG 对比图未跨页截断——检查 PDF 中 L1 图表区域，确认完整显示在一个页面内（`figure img { max-height: 150mm; object-fit: contain; }` 应已生效）
- [ ] 章节配套资源段落有二维码——检查 PDF 中每章末尾，`📌 配套资源` 侧边栏应包含可扫描的 QR 码
- [ ] 不要用 `publishing-classic` 或其他预设重建已有书的 PDF

---

## 参考

- 已有案例：`ai-agent-handbook`（55,000字，10章46小节，已完成初稿+PDF）
- 已有案例：`knowledge-flywheel-book`（终稿+PDF）
- 已有案例：`ai-leader-path`（89,000字，12章+前言+附录，2026-05-18 单次会话从规划到雾霁蓝 PDF 全流程，115页，0空白页，封面全幅）
- 封面封底设计资产规范：`references/cover-asset-conventions.md`（v3.4三QR码+Logo规格）
- 封面模版：`cover-templates/`
- BookSmith-Den：`~/Desktop/Sloth-BookSmith-Den/`
- Lovstudio workflow 来源：`uvx lovstudio-skill-helper decrypt write-professional-book`
- 能力审计：`references/capability-audit.md`（完整 lovstudio + BookSmith 差异分析）
- 并行写书参考：`references/parallel-writing.md`（使用 delegate_task 批量写多章）
- CJK 排版要点：`references/cjk-typography.md`（中文 PDF 排版的 CSS 坑与修复）
- Chrome 原生打印方案：`references/chrome-print-cjk.md`（去掉 Paged.js 后的实测要点，含10项关键修复）
  - Chrome 空白页根因排查：`references/chrome-print-blank-pages.md`（`@page` 命名规则 + `content: none` 导致 Chrome 插入空白过渡页的完整测试矩阵与修复方案）
  - 行业研究+实战指南书结构：`references/industry-research-book-structure.md`（面向特定行业的 AI/数字化转型实战书籍的五部分标准结构，含前后对比表、场景案例、实操要点等标配模式）
  - 已验证案例：`medicine-wholesale-ai`（13章/42K字符/一次会话从0到PDF，仓储路径：`~/Desktop/sloth-books/medicine-wholesale-ai/`）
  - 已验证案例：`token-ledger`（《Token账本》，10章/52K中文字/一次会话完成初稿，商业化畅销书全流程验证。仓储路径：`~/Desktop/sloth-books/token-ledger/`）
  - 流程重构类书籍章节模板（案例B验证）：`references/industry-research-book-structure.md`（"流程重构类书籍的章节模板"一节，含四色标注系统、四类嵌入方式、L1/L2/L3图表三级交付体系、章节尾部引流模板、每章独立可读设计）
  - 章节畅销书化改造：`references/chapter-retrofit-workflow.md`（当已有技术/实操风格的书稿需要升级为畅销书格式时使用——为每章补决策者摘要、延伸阅读、落地工具）
  - 参考文献实战指南：`references/research-refs-workflow.md`（Phase 2 refs.md 如何填写真实来源）
  - 书籍配图管线：`references/book-illustration-workflow.md`（手绘风格插图生成 + 封面QR码集成 + 批量渲染）
  - 网站书封生成：`references/website-book-covers.md`（用Playwright从HTML模板批量生成书封PNG，嵌入SPA关于页面的「我的著作」板块）+ `scripts/gen-website-covers.py`（可复用的生成脚本）
