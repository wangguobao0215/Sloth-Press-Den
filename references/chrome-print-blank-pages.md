# Chrome 130+ PDF 空白页 + 封面全幅 问题排查

> 最后更新：2026-05-18 | 三轮完整测试迭代后确认的最终方案

## 问题一：PDF 中出现空白页（p3 空白）

### 症状
封面、版权页正常显示，但第3页是空白（只有页眉和页码）。

### 根因
Chrome 130+ 的 CSS `@page` 命名页机制存在一个行为：当两个连续页使用 **不同的** `@page` 命名页规则（name pages）时，Chrome 会插入一张空白过渡页。

### 测试矩阵（部分）

| @page 配置 | 封面 | 空白页 | 备注 |
|---|---|---|---|
| `@page cover { margin:0; @top-center:none; }` | 有 | 有 | 单独命名页 → 空白 |
| `@page cover { @top-center:content:"BOOK"; }` | 无 | 无 | 有实际内容的命名页可用 |
| `@page cover { }` (空) | 有 | 有 | 即使空的命名页也触发 |
| `@page cover { margin:22mm; }` | 无 | 无 | 同名页→默认页过渡没问题 |
| 无命名页，负边距 | 无 | 无 | 但封面有白边（Chrome裁剪） |
| **封面+版权+封底共用 `page: cover`** | **无** | **无** | **最终工作方案** |

### 最终修复方案

```css
/* solo命名页 → Chrome插空白页 */
/* 封面+版权+封底同名页 → 无空白页 */
@page cover { margin: 0; @top-center { content: none; } @bottom-center { content: none; } }
```

三个关键约束：
1. 封面、版权页、封底 **都必须用 `page: cover`**（同名）→ Chrome 在相同命名页之间不插空白
2. 版权页必须加 `padding`（`page: cover` 的 margin 为 0，内容会到边缘）
3. `page.pdf()` 的 margin 参数必须设 `0mm`（否则叠加到 CSS @page 之上）

## 问题二：封面不是全幅（有白边）

### 症状
封面四角是白色，背景渐变只覆盖到内容区域，页眉和页码显示在顶部/底部。

### 根因
有两个叠加的原因：
1. **Playwright `page.pdf()` 的 `margin` 参数叠加了额外的白边** — 即使 CSS `@page` 已设置了 margins，Playwright 参数会再加一层，这层白边无法被 CSS 覆盖
2. **CSS 负边距技巧在 PDF 中无效** — `margin: -22mm; padding: 22mm` 在屏幕上有效，但在 Chrome PDF 渲染中被裁剪

### 修复

```python
# 错误：额外叠加白色边框
page.pdf(margin={"top": "22mm", "bottom": "22mm", ...})

# 正确：CSS 全权控制
page.pdf(margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"})
```

### 验证结果

三本书全部通过（2026-05-18）：

| 书名 | 页数 | 空白页 | 封面全幅 | 封底全幅 | 封面图 | 封底图 |
|------|------|--------|---------|---------|-------|-------|
| AI领导者之路：从执行到决策 | 115 | 0 | ✅ | ✅ | 1 | 2 |
| 高管的第一本决策书 | 216 | 0 | ✅ | ✅ | 1 | 2 |
| 知识飞轮 | 94 | 0 | ✅ | ✅ | 1 | 2 |

## 关键代码位置

- `press-typeset.py` 的 `generate_css()` 函数中生成 `@page cover` 规则
- `press-typeset.py` 的 `generate_pdf()` 函数中 `page.pdf(margin=...)` 调用
- `press-typeset.py` 的 CSS 中 `.cover-page`, `.copyright-page`, `.back-cover` 的 `page: cover` 声明

## 相关文件

- `references/chrome-print-cjk.md` — CJK 排版相关
- `scripts/press-typeset.py` — 排版引擎
