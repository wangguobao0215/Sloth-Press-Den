# lovstudio-write-professional-book — 解密工作流（2026-05-17）

来源：`uvx lovstudio-skill-helper decrypt write-professional-book` + `decrypt write-professional-book references/workflow.md`

## 定位

加密付费 skill，lovstudio 出品。核心能力不是"写"，而是跨会话写长文档的上下文管理。

## 5阶段工作流

### Phase 1: Book Planning
- 用 AskUserQuestion 收集：书名/副标题/目标读者/章节数
- gh repo create（默认 private）
- 生成 OUTLINE.md（每章标题+摘要+依赖+字数预估）
- 生成 book.toml + 空目录骨架
- 生成 references/core-papers.md（WebSearch 搜索）
- 生成 BOOK_SUMMARY.md（每行 placeholder）
- 生成构建脚本（build-html.sh / build-pdf.sh / sync-summary.sh）
- 生成 README.md（带封面图、目录、进度表）
- 初始 commit

### Phase 2: Research & References
- 读 OUTLINE.md 确定当前章主题
- WebSearch 搜 arxiv / 官方文档 / 博客
- context7 MCP 拉取官方文档
- 整理到 src/chapter-xx/refs.md
- 更新 bibliography.md → commit

### Phase 3: Chapter Writing（核心循环）
上下文加载（MANDATORY）：OUTLINE + BOOK_SUMMARY + refs + glossary
不要加载其他章节全文。
流程：小节大纲确认 → 逐节写（1000-2000字/节）→ 更新 BOOK_SUMMARY.md（≤500字）→ 更新 glossary → commit

### Phase 4: Review & Polish
- BOOK_SUMMARY.md 检查一致性
- glossary vs 正文 — 术语统一
- [^n] 引用完整性
- 章节间衔接

### Phase 5: Build & Publish
```bash
bash scripts/build-html.sh   # mdBook
bash scripts/build-pdf.sh    # Pandoc
```

## 核心创新

1. BOOK_SUMMARY.md 作为上下文桥 — 每章≤500字，跨会话续写关键
2. One chapter per session — 设计选择，非技术限制
3. refs.md 先行 — 先研究再写，质量更高

## 关键教训

- 加密 skill 背后有完整方法论，别只看表面
- 写作的难点不是"写"，是"跨会话保持一致性"
