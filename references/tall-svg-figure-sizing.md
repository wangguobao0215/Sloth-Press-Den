# 高 SVG 图片跨页截断修复实录

## 问题

Mermaid 生成的 L1 对比图（Before/After 流程图）在 PDF 中跨页截断，底部内容不可见。

## 根因

- L1 对比图 SVGs 尺寸：宽 ~520-567px，高 ~1900-2514px（高宽比 3.4~4.8）
- A5 可打印区域（@page margin 22mm/20mm/16mm）：宽 ~112mm（≈423px），高 ~166mm（≈627px）
- SVG 高度是页面高度的 3-4 倍，即使 `page-break-inside: avoid` 也无法阻止截断
- Chrome PDF 渲染对溢出图片的处理是「在页边界截断」，不会自动分页到下一页继续显示

## 修复方案

### 方案 A（已实施 — press-typeset.py 默认行为）

在 `figure img` CSS 中添加 `max-height` + `object-fit: contain`：

```css
.chapter-body figure img {
    max-width: 85%;
    max-height: 150mm;      /* ← 关键：约束高度不超一页 */
    width: auto;
    height: auto;
    object-fit: contain;    /* ← 等比缩放 */
}
```

效果：图片按比例缩至一页内完整显示，文字同步缩小但可读。

### 方案 B（当方案 A 缩放后图太小）

调大 `max-height` 值，但不要超过 160mm（会骑跨页边距）：

```css
max-height: 158mm;
```

### 方案 C（当缩放到一页内文字完全看不清）

将 Before/After 拆分为两个独立的图，每半张图的高度减半，自然不超一页。

### 方案 D（源头治理）

重新生成 Mermaid 图表：
- 减少节点数量（每列 ≤5 个）
- 使用更紧凑的 layout（`graph TD` 改为 `graph LR` 横向布局）
- 缩小 `fontSize` 设置（8-10px 替代 16px）

## 相关函数

- `generate_css()` 中 `figure img` 规则
- 代码位置：`press-typeset.py` 的 CSS 生成部分

## 验证

PDF 中检查：
- 第 2 章的 L1 对比图（计划流程）应完整在一页内（原跨 3 页）
- 第 4 章的 L1 对比图（P2P 流程，ratio 4.84 最高）应完整在一页内
- 每张对比图下方有 `图 X-Y` 编号
